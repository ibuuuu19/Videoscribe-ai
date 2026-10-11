"""
Module de gestion de l'historique — Version PostgreSQL.

Mêmes fonctions que history_manager.py mais utilise PostgreSQL (Supabase).

Le champ `date` est stocké comme TIMESTAMP dans PostgreSQL mais retourné
comme string "DD/MM/YYYY HH:MM" pour compatibilité avec le code existant.

Usage:
    from src.history_manager_db import get_history, save_analysis
"""

import json
from datetime import datetime
from src.core.db import db_cursor


# ═══ Helpers ═══
def _row_to_record(row):
    """Convertit une ligne SQL en dict (compatibilité JSON)."""
    (
        video_id, title, lang, notes, keywords, questions,
        total_words, num_chunks, processing_time, date,
    ) = row

    return {
        "video_id": video_id,
        "title": title or f"Résumé - {video_id}",
        "lang": lang or "unknown",
        "notes": notes if isinstance(notes, list) else json.loads(notes or "[]"),
        "keywords": keywords if isinstance(keywords, list) else json.loads(keywords or "[]"),
        "questions": questions if isinstance(questions, list) else json.loads(questions or "[]"),
        "total_words": total_words or 0,
        "num_chunks": num_chunks or 0,
        "processing_time": processing_time or 0,
        "date": date.strftime("%d/%m/%Y %H:%M") if date else "",
    }


def _get_user_id(username):
    """Retourne l'ID de l'utilisateur (ou None)."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


# ═══ CRUD ═══
def get_history(username):
    """Retourne l'historique d'un utilisateur (plus récent en premier)."""
    user_id = _get_user_id(username)
    if not user_id:
        return []

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT video_id, title, lang, notes, keywords, questions,
                   total_words, num_chunks, processing_time, date
            FROM history
            WHERE user_id = %s
            ORDER BY date DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

    return [_row_to_record(row) for row in rows]


def save_analysis(username, record):
    """Sauvegarde une analyse dans l'historique."""
    user_id = _get_user_id(username)
    if not user_id:
        return False

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO history 
                (user_id, video_id, title, lang, notes, keywords, questions,
                 total_words, num_chunks, processing_time, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                record.get("video_id", ""),
                record.get("title", ""),
                record.get("lang", "unknown"),
                json.dumps(record.get("notes", []), ensure_ascii=False),
                json.dumps(record.get("keywords", []), ensure_ascii=False),
                json.dumps(record.get("questions", []), ensure_ascii=False),
                record.get("total_words", 0),
                record.get("num_chunks", 0),
                record.get("processing_time", 0),
                datetime.now(),
            ),
        )
    return True


def clear_history(username):
    """Supprime tout l'historique d'un utilisateur."""
    user_id = _get_user_id(username)
    if not user_id:
        return False

    with db_cursor() as cur:
        cur.execute("DELETE FROM history WHERE user_id = %s", (user_id,))
    return True


def count_today(username):
    """Compte les analyses effectuées aujourd'hui."""
    user_id = _get_user_id(username)
    if not user_id:
        return 0

    with db_cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM history
            WHERE user_id = %s 
              AND DATE(date) = CURRENT_DATE
            """,
            (user_id,),
        )
        row = cur.fetchone()
        return row[0] if row else 0


def trim_history(username, keep=10):
    """Garde seulement les N analyses les plus récentes."""
    if keep >= 999999:
        return  # Pas de trim (plans premium)

    user_id = _get_user_id(username)
    if not user_id:
        return

    with db_cursor() as cur:
        # Supprime tout sauf les N plus récentes
        cur.execute(
            """
            DELETE FROM history
            WHERE user_id = %s
              AND id NOT IN (
                SELECT id FROM history
                WHERE user_id = %s
                ORDER BY date DESC
                LIMIT %s
              )
            """,
            (user_id, user_id, keep),
        )