"""
Module de connexion à la base de données PostgreSQL (Supabase).

Fournit :
- get_database_url() : récupère l'URL depuis les secrets
- get_connection() : connexion isolée (utilisée seulement en secours)
- db_cursor() : curseur pris dans un POOL de connexions réutilisées (commit auto)
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
    "cooldown_sec": 8,       # court : le pool se reconnecte seul, on évite de « déconnecter » les gens trop longtemps
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


def _ipv4_conninfo(url):
    """
    Force l'IPv4 SANS modifier socket.getaddrinfo (qui est global et non sûr entre threads) :
    on résout l'hôte une fois et on passe `hostaddr` à libpq ; `host` reste utilisé pour le TLS.
    """
    import socket
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    try:
        d = conninfo_to_dict(url)
        host, port = d.get("host"), int(d.get("port") or 5432)
        if host and not d.get("hostaddr"):
            ip = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)[0][4][0]
            return make_conninfo(url, hostaddr=ip)
    except Exception as e:
        print(f"[db] résolution IPv4 ignorée ({type(e).__name__}) → URL telle quelle")
    return url


@st.cache_resource(show_spinner=False)
def _get_pool():
    """
    Pool de connexions créé UNE fois par processus serveur et partagé par toutes les sessions.
    Avant : psycopg.connect() (DNS + TCP + TLS + auth) à CHAQUE requête → 0,3 à 1 s chacune, et jusqu'à
    2 × 10 s de timeout quand Supabase refusait la connexion = les pages grisées de 12-20 s.
    """
    from psycopg_pool import ConnectionPool
    pool = ConnectionPool(
        _ipv4_conninfo(get_database_url()),
        min_size=1,
        max_size=5,                         # petit : le plan gratuit Supabase limite les connexions
        timeout=6,                          # attente max d'une connexion libre / nouvelle
        max_idle=240,                       # ferme les connexions restées inactives 4 min
        max_lifetime=1500,                  # renouvelle toutes les 25 min
        kwargs={"connect_timeout": 8, "prepare_threshold": None},   # prepare_threshold=None : compatible pooler Supabase
        check=ConnectionPool.check_connection,   # écarte les connexions mortes AVANT usage
        name="videoscribe",
        open=False,
    )
    pool.open(wait=False)
    return pool


def get_connection():
    """Connexion isolée (secours / scripts hors pool). Préférez db_cursor()."""
    import psycopg as _pg
    return _pg.connect(_ipv4_conninfo(get_database_url()), connect_timeout=10, prepare_threshold=None)


_NETWORK_ERRORS = (psycopg.OperationalError, ConnectionError, TimeoutError, OSError)


@contextmanager
def db_cursor():
    # ── DB en cooldown → mode dégradé ──
    if not is_db_available():
        elapsed = time.time() - _DB_STATE["last_failure_ts"]
        print(f"[db] Cooldown ({elapsed:.0f}s/{_DB_STATE['cooldown_sec']}s) → NullCursor")
        yield _NullCursor()
        return

    # ── 1. Prendre une connexion dans le pool (réutilisée, vérifiée) ──
    pool = conn = None
    try:
        pool = _get_pool()
        conn = pool.getconn(timeout=6)
    except Exception as e:
        _mark_db_failure(e)
        print(f"[db] Pool indisponible ({type(e).__name__}: {e}) → cooldown, mode dégradé")
        yield _NullCursor()
        return

    # ── 2. Utiliser le curseur ; une seule fois `yield` ici, les erreurs de l'appelant se propagent ──
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
        _mark_db_success()
    except BaseException as e:
        try:
            conn.rollback()
        except Exception:
            pass
        if isinstance(e, _NETWORK_ERRORS):
            _mark_db_failure(e)
            print(f"[db] Échec DB en cours de requête ({type(e).__name__}) → cooldown")
        raise
    finally:
        try:
            pool.putconn(conn)
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