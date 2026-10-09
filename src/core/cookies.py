"""
Module de gestion des cookies — Authentification et thème.

Contient :
- cookie_mgr : instance globale du CookieController
- COOKIE_NAME : nom du cookie d'authentification
- set_cookie : définit un cookie (via lib + JS fallback)
- delete_cookie : supprime un cookie à tous les niveaux
- read_cookie : lit un cookie (via st.context ou cookie_mgr)

Extrait de app.py pour permettre l'utilisation depuis layout.py et autres modules.

Usage:
    from src.core.cookies import set_cookie, read_cookie, COOKIE_NAME
"""

import time

import streamlit as st
import streamlit.components.v1 as _components
from streamlit_cookies_controller import CookieController

from src.core.config import COOKIE_NAME


# ═══════════════════════════════════════════════════════════════
# INSTANCE GLOBALE DU COOKIE CONTROLLER
# ═══════════════════════════════════════════════════════════════

cookie_mgr = CookieController()


# ═══════════════════════════════════════════════════════════════
# DÉFINIR UN COOKIE
# ═══════════════════════════════════════════════════════════════

def set_cookie(name, value, max_age=7*24*3600):
    """
    Définit un cookie à 3 niveaux :
    1. Via la lib streamlit-cookies-controller
    2. Via JS dans le document courant
    3. Via JS dans le parent/top frame (si iframe)

    Args:
        name: Nom du cookie
        value: Valeur du cookie
        max_age: Durée de vie en secondes (défaut : 7 jours)
    """
    # Niveau 1 : via la lib
    try: 
        cookie_mgr.set(name, value, max_age=max_age, path="/", samesite="Lax")  # type: ignore
    except Exception:
        pass

    # Niveau 2+3 : via JS
    js = f"""<script>try {{
var c = '{name}={value}; path=/; max-age={max_age}; SameSite=Lax';
document.cookie = c;
if (window.parent && window.parent !== window) window.parent.document.cookie = c;
if (window.top) window.top.document.cookie = c;
}} catch(e) {{}}</script>"""
    try:
        _components.html(js, height=0, width=0)
    except Exception:
        pass
    time.sleep(0.3)


# ═══════════════════════════════════════════════════════════════
# SUPPRIMER UN COOKIE
# ═══════════════════════════════════════════════════════════════

def delete_cookie(name):
    """
    Supprime un cookie à TOUS les niveaux :
    - Via la lib (si présente)
    - Via JS dans document, parent et top frame
    - Sur tous les chemins et domaines possibles

    Args:
        name: Nom du cookie à supprimer
    """
    # 1. Via la lib
    try:
        if cookie_mgr.get(name):
            cookie_mgr.remove(name)
    except Exception:
        pass

    # 2. Via JS (tous niveaux)
    js = f"""<script>try {{
        var names = ['{name}'];
        var paths = ['/', '/app', window.location.pathname];
        var domains = [null, window.location.hostname, '.' + window.location.hostname];
        names.forEach(function(n) {{
            paths.forEach(function(p) {{
                domains.forEach(function(d) {{
                    var c = n + '=; path=' + p + '; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
                    if (d) c += '; domain=' + d;
                    document.cookie = c;
                    if (window.parent && window.parent !== window) window.parent.document.cookie = c;
                    if (window.top) window.top.document.cookie = c;
                }});
            }});
        }});
    }} catch(e) {{}}</script>"""
    try:
        _components.html(js, height=0, width=0)
    except Exception:
        pass
    time.sleep(0.5)


# ═══════════════════════════════════════════════════════════════
# LIRE UN COOKIE
# ═══════════════════════════════════════════════════════════════

def read_cookie(name):
    """
    Lit un cookie en essayant plusieurs méthodes :
    1. st.context.cookies (méthode moderne)
    2. cookie_mgr (fallback)

    Args:
        name: Nom du cookie à lire

    Returns:
        La valeur du cookie ou None
    """
    try:
        val = st.context.cookies.get(name)
        if val:
            return val
    except Exception:
        pass
    try:
        return cookie_mgr.get(name) or None
    except Exception:
        return None