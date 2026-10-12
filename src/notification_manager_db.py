"""
Module de gestion des notifications — Version PostgreSQL.

Mêmes fonctions que notification_manager.py mais utilise PostgreSQL (Supabase).

Usage:
    from src.notification_manager_db import notify, get_notifications
"""

from datetime import datetime
from src.core.db import db_cursor


def _get_user_id(username):
    """Retourne l'ID de l'utilisateur (ou None)."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def notify(username, icon, text):
    """
    Ajoute une notification pour un utilisateur.
    
    Args:
        username: Nom de l'utilisateur
        icon: Nom de l'icône (ex: 'bell', 'msg', 'user')
        text: Texte de la notification
    """
    user_id = _get_user_id(username)
    if not user_id:
        return False

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO notifications (user_id, icon, text, read)
            VALUES (%s, %s, %s, FALSE)
            """,
            (user_id, icon, text),
        )
    return True


def get_notifications(username):
    """
    Retourne toutes les notifications d'un utilisateur (plus récente en premier).
    
    Format de retour (compatibilité JSON) :
        [
            {
                "id": 1234567890,       # timestamp ms (compat JSON)
                "icon": "bell",
                "text": "...",
                "date": "11/10/2026 23:38",
                "read": False,
            },
            ...
        ]
    """
    user_id = _get_user_id(username)
    if not user_id:
        return []

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, icon, text, read, created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    return [
        {
            "id": int(row[4].timestamp() * 1000) if row[4] else 0,  # timestamp ms
            "icon": row[1] or "info",
            "text": row[2] or "",
            "date": row[4].strftime("%d/%m/%Y %H:%M") if row[4] else "",
            "read": row[3],
        }
        for row in rows
    ]


def unread_count(username):
    """Compte les notifications non lues."""
    user_id = _get_user_id(username)
    if not user_id:
        return 0

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM notifications
            WHERE user_id = %s AND read = FALSE
            """,
            (user_id,),
        )
        row = cur.fetchone()
        return row[0] if row else 0


def mark_all_read(username):
    """Marque toutes les notifications comme lues."""
    user_id = _get_user_id(username)
    if not user_id:
        return False

    with db_cursor() as cur:
        cur.execute(
            "UPDATE notifications SET read = TRUE WHERE user_id = %s AND read = FALSE",
            (user_id,),
        )
    return True