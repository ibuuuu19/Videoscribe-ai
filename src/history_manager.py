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