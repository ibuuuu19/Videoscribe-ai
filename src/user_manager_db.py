"""
Module de gestion des utilisateurs — Version PostgreSQL.

Mêmes fonctions que user_manager.py mais utilise PostgreSQL (Supabase).

Usage:
    from src.user_manager_db import register_user, authenticate, ...
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta

from src.core.db import db_cursor


# ═══ Configuration ═══
def _get_secret(key, default=""):
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return os.environ.get(key, default)


ADMIN_USER = _get_secret("ADMIN_USER", "admin")
ADMIN_PASS = _get_secret("ADMIN_PASS", "passer1234")

PLAN_TIERS = {"free": 0, "basique": 1, "premium": 2, "premium_plus": 3}


# ═══ Helpers ═══
def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def _row_to_user_dict(row):
    """Convertit une ligne SQL en dict (compatibilité JSON)."""
    if not row:
        return {}
    return {
        "id": row[0],
        "email": row[1] or "",
        "salt": row[2],
        "password_hash": row[3],
        "role": row[4] or "client",
        "active": row[5],
        "plan": row[6] or "free",
        "premium_expires": row[7].isoformat() if row[7] else None,
        "created_at": row[8].isoformat() if row[8] else None,
    }


# ═══ Initialisation ═══
def ensure_admin():
    """Crée le compte admin s'il n'existe pas."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (ADMIN_USER,))
        if cur.fetchone():
            return  # Admin existe déjà
        
        salt = secrets.token_hex(16)
        password_hash = _hash_password(ADMIN_PASS, salt)
        cur.execute(
            """
            INSERT INTO users (username, email, salt, password_hash, role, active, plan)
            VALUES (%s, %s, %s, %s, 'admin', TRUE, 'premium_plus')
            """,
            (ADMIN_USER, "contact@admin.com", salt, password_hash),
        )


# ═══ CRUD ═══
def register_user(username, password, email="", role="client"):
    """Crée un nouvel utilisateur."""
    uname = (username or "").strip().lower()

    # Validations (identiques à la version JSON)
    if not uname or len(uname) < 3:
        return False, "Nom d'utilisateur invalide (3 caractères min)."
    if len(password) < 6:
        return False, "Mot de passe : 6 caractères minimum."

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)

    try:
        with db_cursor() as cur:
            # Vérifier si existe déjà
            cur.execute("SELECT id FROM users WHERE username = %s", (uname,))
            if cur.fetchone():
                return False, "Ce nom d'utilisateur existe déjà."
            
            cur.execute(
                """
                INSERT INTO users (username, email, salt, password_hash, role, active, plan)
                VALUES (%s, %s, %s, %s, %s, TRUE, 'free')
                """,
                (uname, email or "", salt, password_hash, role),
            )
        return True, "Compte créé avec succès !"
    except Exception as e:
        return False, f"Erreur lors de la création : {e}"


def authenticate(username, password):
    """Vérifie les credentials. Retourne (succès, rôle_ou_statut)."""
    uname = (username or "").strip().lower()
    if not uname:
        return False, None

    with db_cursor() as cur:
        cur.execute(
            "SELECT salt, password_hash, role, active FROM users WHERE username = %s",
            (uname,),
        )
        row = cur.fetchone()
        if not row:
            return False, None
        
        salt, password_hash, role, active = row
        if not active:
            return False, "suspended"
        
        if _hash_password(password, salt) == password_hash:
            return True, role or "client"
        return False, None


def list_users():
    """Retourne tous les utilisateurs (format dict comme avant)."""
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT id, email, salt, password_hash, role, active, plan, premium_expires, created_at
            FROM users
            """
        )
        rows = cur.fetchall()
        # Récupérer les usernames
        cur.execute("SELECT id, username FROM users")
        id_to_username = {r[0]: r[1] for r in cur.fetchall()}
    
    return {id_to_username[row[0]]: _row_to_user_dict(row) for row in rows}


def delete_user(username):
    """Supprime un utilisateur (sauf admin)."""
    with db_cursor() as cur:
        cur.execute("SELECT role FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row or row[0] == "admin":
            return False
        
        cur.execute("DELETE FROM users WHERE username = %s", (username,))
        return True


def set_active(username, active):
    """Active ou suspend un utilisateur (sauf admin)."""
    with db_cursor() as cur:
        cur.execute("SELECT role FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row or row[0] == "admin":
            return False
        
        cur.execute(
            "UPDATE users SET active = %s WHERE username = %s",
            (active, username),
        )
        return True


def reset_password(username, new_password):
    """Change le mot de passe d'un utilisateur."""
    if len(new_password) < 6:
        return False
    
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if not cur.fetchone():
            return False
        
        salt = secrets.token_hex(16)
        password_hash = _hash_password(new_password, salt)
        cur.execute(
            "UPDATE users SET salt = %s, password_hash = %s WHERE username = %s",
            (salt, password_hash, username),
        )
        return True


def set_plan(username, plan="premium", days=30):
    """Active une formule."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if not cur.fetchone():
            return False
        
        expires = None
        if plan != "free":
            expires = datetime.now() + timedelta(days=days)
        
        cur.execute(
            "UPDATE users SET plan = %s, premium_expires = %s WHERE username = %s",
            (plan, expires, username),
        )
        return True


def set_premium(username, active=True, days=30):
    """Compatibilité ancien code."""
    return set_plan(username, "premium" if active else "free", days)


def get_plan(username):
    """Retourne la formule active."""
    with db_cursor() as cur:
        cur.execute(
            "SELECT plan, premium_expires FROM users WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return "free"
        
        plan, expires = row
        if plan != "free" and expires and expires > datetime.now():
            return plan
        return "free"


def get_tier(username):
    """Retourne le niveau numérique 0-3."""
    return PLAN_TIERS.get(get_plan(username), 0)