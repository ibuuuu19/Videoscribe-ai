"""
Module de stockage — Version PostgreSQL (favoris + partages).

Ne concerne QUE les favoris et partages. Les autres fonctions
(export_anki, generate_audio, get_avatar_b64, get_referral_code)
restent dans src/ui/storage.py.

Usage:
    from src.ui.storage_db import load_favs, toggle_fav, save_share
"""

import hashlib
import json
import time
from datetime import datetime

from src.core.db import db_cursor


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_user_id(username):
    """Retourne l'ID de l'utilisateur (ou None)."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


# ═══════════════════════════════════════════════════════════════
# FAVORIS
# ═══════════════════════════════════════════════════════════════

def load_favs(uname):
    """Retourne la liste des IDs de vidéos favorites d'un utilisateur."""
    user_id = _get_user_id(uname)
    if not user_id:
        return []

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT video_id FROM favorites
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return [row[0] for row in cur.fetchall()]


def toggle_fav(uname, vid):
    """
    Ajoute/retire une vidéo des favoris.
    Retourne True si ajoutée, False si retirée.
    """
    user_id = _get_user_id(uname)
    if not user_id:
        return False

    with db_cursor() as cur:
        # Vérifie si déjà en favori
        cur.execute(
            "SELECT 1 FROM favorites WHERE user_id = %s AND video_id = %s",
            (user_id, vid),
        )
        exists = cur.fetchone() is not None

        if exists:
            cur.execute(
                "DELETE FROM favorites WHERE user_id = %s AND video_id = %s",
                (user_id, vid),
            )
            return False
        else:
            cur.execute(
                "INSERT INTO favorites (user_id, video_id) VALUES (%s, %s)",
                (user_id, vid),
            )
            return True


# ═══════════════════════════════════════════════════════════════
# PARTAGES PUBLICS
# ═══════════════════════════════════════════════════════════════

def load_shares():
    """
    Charge tous les partages depuis la DB.
    Retourne un dict {sid: {video_id, notes, keywords, date, owner}}.
    """
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT s.id, s.video_id, s.notes, s.keywords, s.date, u.username
            FROM shares s
            JOIN users u ON u.id = s.user_id
            """
        )
        rows = cur.fetchall()

    shares = {}
    for sid, video_id, notes, keywords, date, owner in rows:
        shares[sid] = {
            "video_id": video_id,
            "notes": notes if isinstance(notes, list) else json.loads(notes or "[]"),
            "keywords": keywords if isinstance(keywords, list) else json.loads(keywords or "[]"),
            "date": date.strftime("%d/%m/%Y %H:%M") if date else "",
            "owner": owner,
        }
    return shares


def save_share(data, owner):
    """
    Crée un partage public. Retourne l'ID unique (8 caractères).
    
    Args:
        data: dict avec video_id, notes, keywords, date
        owner: username du propriétaire
    """
    user_id = _get_user_id(owner)
    if not user_id:
        return None

    # Génère un ID unique (8 chars, comme avant)
    sid = hashlib.md5((data["video_id"] + str(time.time())).encode()).hexdigest()[:8]

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO shares (id, user_id, video_id, notes, keywords)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                sid,
                user_id,
                data["video_id"],
                json.dumps(data.get("notes", []), ensure_ascii=False),
                json.dumps(data.get("keywords", []), ensure_ascii=False),
            ),
        )
    return sid