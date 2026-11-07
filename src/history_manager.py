import json
import os
from pathlib import Path
from datetime import datetime   # ← en haut

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def _history_file(username):
    return DATA_DIR / f"history_{username}.json"

def get_history(username):
    path = _history_file(username)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_analysis(username, record):
    history = get_history(username)
    history.insert(0, record)  # plus récent en premier
    with open(_history_file(username), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def clear_history(username):
    path = _history_file(username)
    if path.exists():
        path.unlink()


def count_today(username):
    today = datetime.now().strftime("%d/%m/%Y")
    return sum(1 for h in get_history(username) if h.get("date", "").startswith(today))


def rewrite_history(username, records):
    path = Path("data") / f"history_{username}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def delete_analysis(username, video_id, date):
    """Supprime UNE analyse (identifiée par video_id + date). Renvoie True si elle existait."""
    h = get_history(username)
    rest = [x for x in h if not (x.get("video_id") == video_id and x.get("date") == date)]
    if len(rest) == len(h):
        return False
    rewrite_history(username, rest)
    return True


def trim_history(username, keep=10):
    h = get_history(username)
    if len(h) > keep:
        rewrite_history(username, h[-keep:])



# ═══════════════════════════════════════════════════════════════
# WRAPPER : Délégation vers PostgreSQL si DATABASE_URL est défini
# ═══════════════════════════════════════════════════════════════
def _use_database():
    """Détecte si on doit utiliser PostgreSQL."""
    try:
        import streamlit as st
        return bool(st.secrets.get("DATABASE_URL"))
    except Exception:
        return bool(os.environ.get("DATABASE_URL"))


if _use_database():
    # Délègue à la version PostgreSQL
    # pylint: disable=redefined-outer-name
    import src.history_manager_db as _db

    get_history = _db.get_history
    save_analysis = _db.save_analysis  # type: ignore[assignment]
    clear_history = _db.clear_history  # type: ignore[assignment]
    count_today = _db.count_today
    trim_history = _db.trim_history

    if hasattr(_db, "delete_analysis"):
        delete_analysis = _db.delete_analysis  # type: ignore[assignment]
    else:
        def delete_analysis(username, video_id, date):  # type: ignore[no-redef]
            """Repli PostgreSQL : reconstruit l'historique sans l'analyse supprimée (restaure en cas d'échec)."""
            full = list(_db.get_history(username) or [])
            rest = [x for x in full if not (x.get("video_id") == video_id and x.get("date") == date)]
            if len(rest) == len(full):
                return False
            _db.clear_history(username)
            try:
                for x in reversed(rest):          # le plus ancien d'abord → l'ordre est conservé
                    _db.save_analysis(username, x)
            except Exception:
                _db.clear_history(username)
                for x in reversed(full):
                    _db.save_analysis(username, x)
                return False
            return True