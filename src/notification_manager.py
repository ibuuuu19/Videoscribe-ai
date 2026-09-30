import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
NOTIFS_FILE = DATA_DIR / "notifications.json"


def _load():
    if NOTIFS_FILE.exists():
        try:
            return json.load(open(NOTIFS_FILE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(d):
    with open(NOTIFS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def notify(username, icon, text):
    d = _load()
    d.setdefault(username, []).append({
        "id": int(datetime.now().timestamp() * 1000),
        "icon": icon, "text": text,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "read": False,
    })
    _save(d)


def get_notifications(username):
    return sorted(_load().get(username, []), key=lambda n: n["id"], reverse=True)


def unread_count(username):
    return sum(1 for n in _load().get(username, []) if not n["read"])


def mark_all_read(username):
    d = _load()
    for n in d.get(username, []):
        n["read"] = True
    _save(d)
