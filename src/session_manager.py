import json
import secrets
import time
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SESSIONS_FILE = DATA_DIR / "sessions.json"
SESSION_TTL = 7 * 24 * 3600

def _load():
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save(sessions):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)

def create_session(username):
    sessions = _load()
    sessions = {t: s for t, s in sessions.items() if s["expires"] > time.time()}
    token = secrets.token_hex(32)
    sessions[token] = {"user": username, "expires": time.time() + SESSION_TTL}
    _save(sessions)
    return token

def get_session_user(token):
    if not token:
        return None
    sessions = _load()
    s = sessions.get(token)
    if not s:
        return None
    if s["expires"] < time.time():
        del sessions[token]
        _save(sessions)
        return None
    return s["user"]

def delete_session(token):
    if not token:
        return
    sessions = _load()
    if token in sessions:
        del sessions[token]
        _save(sessions)