"""
Module de connexion à la base de données PostgreSQL (Supabase).

Fournit :
- get_database_url() : récupère l'URL depuis les secrets
- get_connection() : retourne une nouvelle connexion
- db_cursor() : context manager pour les curseurs (commit auto)
- init_db() : crée les tables depuis schema.sql

Usage:
    from src.core.db import db_cursor, init_db
    init_db()
    with db_cursor() as cur:
        cur.execute("SELECT * FROM users")
"""

import streamlit as st
import psycopg
from contextlib import contextmanager
from pathlib import Path


def get_database_url():
    """Récupère l'URL de connexion depuis les secrets Streamlit ou secrets.toml."""
    try:
        url = st.secrets.get("DATABASE_URL")
        if url:
            return url
    except Exception:
        pass
    
    # Fallback : lecture directe du fichier (hors contexte Streamlit)
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
    """Retourne une nouvelle connexion PostgreSQL."""
    return psycopg.connect(get_database_url(), connect_timeout=10)


@contextmanager
def db_cursor():
    """
    Context manager pour les opérations DB.
    
    - Commit automatique si succès
    - Rollback automatique en cas d'erreur
    - Ferme la connexion à la fin
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """
    Crée les tables si elles n'existent pas (idempotent).
    
    Lit `schema.sql` situé dans le même dossier.
    """
    schema_path = Path(__file__).parent / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql introuvable : {schema_path}")
    
    schema_sql = schema_path.read_text(encoding="utf-8")
    
    with db_cursor() as cur:
        cur.execute(schema_sql)  # type: ignore
    
    print("✅ Base de données initialisée (tables créées si absentes)")


def health_check():
    """Vérifie que la connexion DB est opérationnelle."""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        return True
    except Exception as e:
        print(f"❌ Health check DB échoué : {e}")
        return False