import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
REV_FILE = DATA_DIR / "revenues.json"


def _load():
    if REV_FILE.exists():
        try:
            return json.load(open(REV_FILE, encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(rows):
    with open(REV_FILE, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def record_revenue(user, plan, amount, days=30, source="manuel"):
    rows = _load()
    rows.append({"user": user, "plan": plan, "amount": amount,
                 "days": days, "source": source,
                 "date": datetime.now().strftime("%d/%m/%Y")})
    _save(rows)


def get_revenues():
    return _load()

# ═══════════════════════════════════════════════════════════════
# WRAPPER : Délégation vers PostgreSQL si DATABASE_URL est défini
# ═══════════════════════════════════════════════════════════════
def _use_database():
    """Détecte si on doit utiliser PostgreSQL."""
    import os
    try:
        import streamlit as st
        return bool(st.secrets.get("DATABASE_URL"))
    except Exception:
        return bool(os.environ.get("DATABASE_URL"))


if _use_database():
    # Délègue à la version PostgreSQL
    # pylint: disable=redefined-outer-name
    import src.revenue_manager_db as _db
    
    record_revenue = _db.record_revenue  # type: ignore[assignment]
    get_revenues = _db.get_revenues