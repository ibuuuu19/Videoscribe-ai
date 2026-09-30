import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MESSAGES_FILE = DATA_DIR / "messages.json"


def _load():
    if MESSAGES_FILE.exists():
        try:
            return json.load(open(MESSAGES_FILE, encoding="utf-8"))
        except Exception:
            return []
    return []


def _save(msgs):
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)


def save_message(username, subject, message, urgency="normale"):
    msgs = _load()
    msgs.append({
        "id": (max([m["id"] for m in msgs], default=0) + 1),
        "user": username, "subject": subject, "message": message,
        "urgency": urgency,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "read": False,
    })
    _save(msgs)
    return True


def get_messages():
    return sorted(_load(), key=lambda m: m["id"], reverse=True)


def mark_read(msg_id):
    msgs = _load()
    for m in msgs:
        if m["id"] == msg_id:
            m["read"] = True
    _save(msgs)


def delete_message(msg_id):
    _save([m for m in _load() if m["id"] != msg_id])