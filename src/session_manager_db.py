"""
Module de gestion des sessions — Version PostgreSQL.

Mêmes fonctions que session_manager.py mais utilise PostgreSQL (Supabase).

Usage:
    from src.session_manager_db import create_session, get_session_user, delete_session
"""

import secrets
from datetime import datetime, timedelta

from src.core.db import db_cursor


SESSION_TTL = 7 * 24 * 3600  # 7 jours en secondes


def _get_user_id(username):
    """Retourne l'ID de l'utilisateur (ou None)."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def create_session(username):
    """
    Crée une nouvelle session pour un utilisateur.
    Retourne le token (32 bytes hex).
    """
    user_id = _get_user_id(username)
    if not user_id:
        return None

    token = secrets.token_hex(32)
    expires_at = datetime.now() + timedelta(seconds=SESSION_TTL)

    with db_cursor() as cur:
        # Nettoyer les sessions expirées (housekeeping)
        cur.execute("DELETE FROM sessions WHERE expires_at < NOW()")
        
        # Créer la nouvelle session
        cur.execute(
            """
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (%s, %s, %s)
            """,
            (token, user_id, expires_at),
        )

    return token


def get_session_user(token):
    """
    Récupère l'utilisateur associé à un token (ou None si inexistant/expiré).
    """
    if not token:
        return None

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT u.username, s.expires_at 
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = %s
            """,
            (token,),
        )
        row = cur.fetchone()
        if not row:
            return None

        username, expires_at = row
        if expires_at < datetime.now():
            # Session expirée → on la supprime
            cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
            return None

        return username


def delete_session(token):
    """Supprime une session (logout)."""
    if not token:
        return

    with db_cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE token = %s", (token,))