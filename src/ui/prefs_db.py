"""
Module de préférences utilisateur — Version PostgreSQL.

Mêmes fonctions que prefs.py mais utilise PostgreSQL (Supabase).

Note : Dans PostgreSQL, les préférences sont stockées comme des paires
(user_id, key, value). On utilise "value" comme TEXT (string).

Usage:
    from src.ui.prefs_db import get_prefs, set_pref
"""

from src.core.db import db_cursor


def _get_user_id(username):
    """Retourne l'ID de l'utilisateur (ou None)."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def get_prefs(uname):
    """
    Retourne les préférences d'un utilisateur sous forme de dict.
    
    ⚠️ Note : Toutes les valeurs sont des strings (car stockées en TEXT).
    Il faudra convertir (int, float) à la lecture si nécessaire.
    """
    if not uname:
        return {}

    user_id = _get_user_id(uname)
    if not user_id:
        return {}

    with db_cursor() as cur:
        cur.execute(
            "SELECT key, value FROM prefs WHERE user_id = %s",
            (user_id,),
        )
        rows = cur.fetchall()

    prefs = {}
    for key, value in rows:
        # Conversion intelligente : tente int → float → str
        prefs[key] = _parse_value(value)
    return prefs


def set_pref(uname, key, val):
    """
    Enregistre une préférence (upsert).
    
    Args:
        uname: Nom de l'utilisateur
        key: Clé de la préférence (ex: 'accent', 'font_size')
        val: Valeur (convertie en string pour stockage)
    """
    user_id = _get_user_id(uname)
    if not user_id:
        return False

    # Convertit la valeur en string pour stockage TEXT
    val_str = str(val) if val is not None else ""

    with db_cursor() as cur:
        # Upsert : INSERT ... ON CONFLICT DO UPDATE
        cur.execute(
            """
            INSERT INTO prefs (user_id, key, value)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, key)
            DO UPDATE SET value = EXCLUDED.value
            """,
            (user_id, key, val_str),
        )
    return True


def _parse_value(value):
    """
    Convertit une string en int/float/str (best-effort).
    
    Exemples :
        "16" → 16
        "1.6" → 1.6
        "#2E6DB4" → "#2E6DB4"
        "fr" → "fr"
    """
    if value is None:
        return ""
    
    val = str(value).strip()
    
    # Essaye int
    try:
        return int(val)
    except ValueError:
        pass
    
    # Essaye float
    try:
        return float(val)
    except ValueError:
        pass
    
    # Retourne la string
    return val