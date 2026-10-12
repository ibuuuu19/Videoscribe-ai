"""
Module de gestion des messages de contact — Version PostgreSQL.

Mêmes fonctions que contact_manager.py mais utilise PostgreSQL (Supabase).

Note : Le champ `user` du JSON devient `sender` en PostgreSQL
(USER est un mot réservé).

Usage:
    from src.contact_manager_db import save_message, get_messages
"""

from src.core.db import db_cursor


def save_message(username, subject, message, urgency="normale"):
    """
    Sauvegarde un message de contact.
    
    Args:
        username: Nom de l'expéditeur (ou "visiteur_anonyme")
        subject: Sujet du message
        message: Contenu
        urgency: "normale" | "importante" | "urgente"
    """
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO contact_messages (sender, subject, message, urgency, read)
            VALUES (%s, %s, %s, %s, FALSE)
            """,
            (username, subject, message, urgency),
        )
    return True


def get_messages():
    """
    Retourne tous les messages (plus récents en premier).
    
    Format de retour (compatibilité JSON) :
        [
            {
                "id": 1,
                "user": "visiteur_anonyme",     # alias de `sender`
                "subject": "...",
                "message": "...",
                "urgency": "normale",
                "date": "11/10/2026 23:45",
                "read": False,
            },
            ...
        ]
    """
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, sender, subject, message, urgency, read, created_at
            FROM contact_messages
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "user": row[1] or "anonyme",       # alias pour compatibilité
            "subject": row[2] or "",
            "message": row[3] or "",
            "urgency": row[4] or "normale",
            "date": row[6].strftime("%d/%m/%Y %H:%M") if row[6] else "",
            "read": row[5],
        }
        for row in rows
    ]


def mark_read(msg_id):
    """Marque un message comme lu."""
    with db_cursor() as cur:
        cur.execute(
            "UPDATE contact_messages SET read = TRUE WHERE id = %s",
            (msg_id,),
        )
    return True


def delete_message(msg_id):
    """Supprime un message."""
    with db_cursor() as cur:
        cur.execute(
            "DELETE FROM contact_messages WHERE id = %s",
            (msg_id,),
        )
    return True