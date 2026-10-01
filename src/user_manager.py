import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"

import os
def _get_secret(key, default=""):
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

ADMIN_USER = _get_secret("ADMIN_USER", "admin")
ADMIN_PASS = _get_secret("ADMIN_PASS", "passer1234")
# Niveaux d'abonnement (0 = gratuit → 3 = premium+)
PLAN_TIERS = {"free": 0, "basique": 1, "premium": 2, "premium_plus": 3}


def _load_users():
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def ensure_admin():
    """Crée le compte admin spécifique s'il n'existe pas."""
    users = _load_users()
    if ADMIN_USER not in users:
        salt = secrets.token_hex(16)
        users[ADMIN_USER] = {
            "email": "contact@admin.com",
            "salt": salt,
            "password_hash": _hash_password(ADMIN_PASS, salt),
            "role": "admin",
            "active": True,
            "created_at": datetime.now().isoformat(),
        }
        _save_users(users)


def register_user(username, password, email="", role="client"):
    users = _load_users()
    uname = username.strip().lower()

    if not uname or len(uname) < 3:
        return False, "Nom d'utilisateur invalide (3 caractères min)."
    if uname in users:
        return False, "Ce nom d'utilisateur existe déjà."
    if len(password) < 6:
        return False, "Mot de passe : 6 caractères minimum."

    salt = secrets.token_hex(16)
    users[uname] = {
        "email": email,
        "salt": salt,
        "password_hash": _hash_password(password, salt),
        "role": role,
        "active": True,
        "created_at": datetime.now().isoformat(),
    }
    _save_users(users)
    return True, "Compte créé avec succès !"


def authenticate(username, password):
    """Retourne (succès, rôle_ou_statut)."""
    users = _load_users()
    user = users.get(username.strip().lower())
    if not user:
        return False, None
    if not user.get("active", True):
        return False, "suspended"
    if _hash_password(password, user["salt"]) == user["password_hash"]:
        return True, user.get("role", "client")
    return False, None


def list_users():
    return _load_users()


def delete_user(username):
    users = _load_users()
    if username in users and users[username].get("role") != "admin":
        del users[username]
        _save_users(users)
        return True
    return False


def set_active(username, active):
    users = _load_users()
    if username in users and users[username].get("role") != "admin":
        users[username]["active"] = active
        _save_users(users)
        return True
    return False


def reset_password(username, new_password):
    users = _load_users()
    if username in users and len(new_password) >= 6:
        salt = secrets.token_hex(16)
        users[username]["salt"] = salt
        users[username]["password_hash"] = _hash_password(new_password, salt)
        _save_users(users)
        return True
    return False


def set_plan(username, plan="premium", days=30):
    """Active une formule (basique / premium / premium_plus) ou repasse en gratuit."""
    users = _load_users()
    if username not in users:
        return False
    users[username]["plan"] = plan
    users[username]["premium_expires"] = (
        (datetime.now() + timedelta(days=days)).isoformat()
        if plan != "free" else None
    )
    _save_users(users)
    return True


def set_premium(username, active=True, days=30):
    """Compatibilité ancien code : active/coupe la formule premium."""
    return set_plan(username, "premium" if active else "free", days)


def get_plan(username):
    """Retourne la formule active : free / basique / premium / premium_plus."""
    u = _load_users().get(username, {})
    plan = u.get("plan", "free")
    if plan != "free":
        exp = u.get("premium_expires")
        try:
            if exp and datetime.fromisoformat(exp) > datetime.now():
                return plan
        except Exception:
            pass
    return "free"


def get_tier(username):
    """Retourne le niveau numérique 0-3 de la formule active."""
    return PLAN_TIERS.get(get_plan(username), 0)