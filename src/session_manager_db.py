"""
Module de gestion des sessions — Version PostgreSQL (Supabase).

Mêmes fonctions que session_manager.py.

Correctif « déconnexion au rechargement » :
  · l'ancienne version comparait `expires_at` (datetime AWARE renvoyé par psycopg3 si la colonne est
    `timestamptz`) à `datetime.now()` (NAÏF) → TypeError → l'app l'attrapait → session = None → déconnexion
    à CHAQUE rechargement. Désormais l'expiration est calculée et vérifiée côté SQL avec NOW() : plus aucune
    comparaison Python, valable pour `timestamp` comme pour `timestamptz`, et indépendante du fuseau du serveur.
  · une erreur de base temporaire n'est plus confondue avec « session invalide » : elle remonte à l'appelant
    (app.py affiche « reconnexion… » au lieu de déconnecter).
"""

import secrets

from src.core.db import db_cursor

SESSION_TTL = 7 * 24 * 3600  # 7 jours en secondes


def _get_user_id(username):
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def create_session(username):
    """Crée une session et retourne le token (64 car. hex), ou None."""
    user_id = _get_user_id(username)
    if not user_id:
        return None

    token = secrets.token_hex(32)
    with db_cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE expires_at < NOW()")  # ménage
        cur.execute(
            "INSERT INTO sessions (token, user_id, expires_at) "
            "VALUES (%s, %s, NOW() + make_interval(secs => %s))",
            (token, user_id, SESSION_TTL),
        )
    return token


def get_session_user(token):
    """Utilisateur associé au token, ou None si inconnu / expiré."""
    if not token:
        return None

    with db_cursor() as cur:
        cur.execute(
            "SELECT u.username FROM sessions s JOIN users u ON u.id = s.user_id "
            "WHERE s.token = %s AND s.expires_at > NOW()",
            (token,),
        )
        row = cur.fetchone()
        return row[0] if row else None


def delete_session(token):
    """Supprime une session (déconnexion)."""
    if not token:
        return
    with db_cursor() as cur:
        cur.execute("DELETE FROM sessions WHERE token = %s", (token,))