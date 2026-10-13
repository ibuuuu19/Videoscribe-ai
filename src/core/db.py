"""
Module de connexion à la base de données PostgreSQL (Supabase).

Fournit :
- get_database_url() : récupère l'URL depuis les secrets
- get_connection() : retourne une nouvelle connexion (timeout court)
- db_cursor() : context manager pour les curseurs (commit auto)
- init_db() : crée les tables depuis schema.sql
- is_db_available() : vérifie si la DB n'est pas en "circuit ouvert"

Usage:
    from src.core.db import db_cursor, init_db
    init_db()
    with db_cursor() as cur:
        cur.execute("SELECT * FROM users")
"""

import time
import streamlit as st
import psycopg
from contextlib import contextmanager
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# CIRCUIT BREAKER : évite de retenter la DB en boucle si elle est down
# ═══════════════════════════════════════════════════════════════

_DB_STATE = {
    "last_failure_ts": 0.0,
    "cooldown_sec": 20,      # 20s au lieu de 60s → récupération plus rapide
    "last_error": None,
}


def is_db_available():
    """Retourne False si la DB est en cooldown (échec récent)."""
    elapsed = time.time() - _DB_STATE["last_failure_ts"]
    return elapsed > _DB_STATE["cooldown_sec"]


def _mark_db_failure(err):
    """Marque la DB comme 'en panne' pour déclencher le cooldown."""
    _DB_STATE["last_failure_ts"] = time.time()
    _DB_STATE["last_error"] = str(err)


def _mark_db_success():
    """Réinitialise le circuit breaker après un succès."""
    _DB_STATE["last_failure_ts"] = 0.0
    _DB_STATE["last_error"] = None


# ═══════════════════════════════════════════════════════════════
# NULL CURSOR : curseur "no-op" pour le mode dégradé
# ═══════════════════════════════════════════════════════════════

class _NullCursor:
    """
    Faux curseur en mode dégradé :
    - Lectures (SELECT) → retourne None / []  (silencieux)
    - Écritures (INSERT/UPDATE/DELETE) → lève ConnectionError
      pour que l'appelant sache que l'opération n'a PAS été faite.
    """
    description = None
    rowcount = 0

    def execute(self, query, *args, **kwargs):
        q = (query or "").strip().upper()
        if q.startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE")):
            raise ConnectionError("DB indisponible — écriture refusée (mode dégradé)")
        return self

    def executemany(self, query, *args, **kwargs):
        return self.execute(query, *args, **kwargs)

    def fetchone(self):
        return None

    def fetchall(self):
        return []

    def fetchmany(self, size=None):
        return []

    def __iter__(self):
        return iter([])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def close(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

# ═══════════════════════════════════════════════════════════════
# CONNEXION
# ═══════════════════════════════════════════════════════════════

def get_database_url():
    """Récupère l'URL de connexion depuis les secrets Streamlit ou secrets.toml."""
    try:
        url = st.secrets.get("DATABASE_URL")
        if url:
            return url
    except Exception:
        pass

    try:
        import tomli
        secrets_path = Path(".streamlit/secrets.toml")
        if secrets_path.exists():
            with open(secrets_path, "rb") as f:
                url = tomli.load(f).get("DATABASE_URL")
                if url:
                    return url
    except Exception:
        pass

    raise RuntimeError(
        "DATABASE_URL non configurée. "
        "Ajoute-la dans .streamlit/secrets.toml ou dans les secrets Streamlit Cloud."
    )


def get_connection():
    """Connexion avec fallback pooler → direct."""
    import socket
    
    _orig = socket.getaddrinfo
    def _ipv4_only(host, *args, **kwargs):
        return [a for a in _orig(host, *args, **kwargs) if a[0] == socket.AF_INET]
    
    url = get_database_url()
    
    # URLs alternatives à tester (fallback)
    urls_to_try = [url]
    
    # Si c'est le pooler 6543, tester aussi le 5432 et le direct
    if ":6543" in url:
        urls_to_try.append(url.replace(":6543", ":5432"))
    if "pooler.supabase.com" in url:
        # host direct (si encore actif)
        direct = url.replace("aws-0-eu-west-1.pooler.supabase.com", "db.cdgssmyhsyzapaaylsfp.supabase.co")
        urls_to_try.append(direct)
    
    last_err = None
    socket.getaddrinfo = _ipv4_only
    
    for i, try_url in enumerate(urls_to_try):
        try:
            conn = psycopg.connect(
                try_url,
                connect_timeout=15,
                prepare_threshold=None,
            )
            print(f"[db] ✅ Connecté via URL #{i+1}")
            return conn
        except Exception as e:
            last_err = e
            print(f"[db] ❌ URL #{i+1} échouée: {type(e).__name__}")
            continue
    finally:                                # type: ignore
        socket.getaddrinfo = _orig          # type: ignore
    
    raise last_err        # type: ignore


@contextmanager
def db_cursor():
    # ── DB en cooldown → mode dégradé ──
    if not is_db_available():
        elapsed = time.time() - _DB_STATE["last_failure_ts"]
        print(f"[db] Cooldown ({elapsed:.0f}s/{_DB_STATE['cooldown_sec']}s) → NullCursor")
        yield _NullCursor()
        return

    # ── Tentative ──
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            yield cur
        conn.commit()
        _mark_db_success()
    except Exception as e:
        # Rollback best-effort
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass

        # Marque la DB en panne si c'est un timeout / erreur réseau
        if isinstance(e, (
            psycopg.OperationalError,
            psycopg.errors.ConnectionTimeout,
            ConnectionError,
            TimeoutError,
            OSError,
        )):
            _mark_db_failure(e)
            print(f"[db] Échec DB ({type(e).__name__}) → marqué en cooldown, mode dégradé")
            # ✅ On yield un NullCursor au lieu de crash
            yield _NullCursor()
            return

        # Autre type d'erreur (SQL, contrainte, etc.) → on propage
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def init_db():
    """Crée les tables si elles n'existent pas (idempotent)."""
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql introuvable : {schema_path}")

    schema_sql = schema_path.read_text(encoding="utf-8")

    with db_cursor() as cur:
        cur.execute(schema_sql)  # type: ignore

    if is_db_available():
        print("✅ Base de données initialisée (tables créées si absentes)")


def health_check():
    """Vérifie que la connexion DB est opérationnelle."""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        return result is not None
    except Exception as e:
        print(f"❌ Health check DB échoué : {e}")
        return False