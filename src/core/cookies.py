"""
Module de gestion des cookies — Authentification et thème.

Correctifs (déconnexion au rechargement sur Streamlit Cloud) :
  1. L'ancien `cookie_mgr = CookieController()` était créé AU CHARGEMENT DU MODULE : instance partagée par tous les
     utilisateurs, figée sur le premier `{}` reçu → `cookie_mgr.get()` ne renvoyait jamais rien. Désormais le
     contrôleur est créé PAR SESSION (`_ctl()`), et `cookie_mgr` n'est qu'un proxy vers lui (même API).
  2. `cookie_mgr.set(..., samesite="Lax")` utilisait un argument qui n'existe pas (c'est `same_site="lax"`) :
     TypeError avalé par le `except` → l'écriture via la lib n'a JAMAIS eu lieu. Corrigé.
  3. Sur Streamlit Cloud, le navigateur est à plusieurs centaines de ms du serveur : avec `sleep(0.3)` puis
     `st.rerun()`, l'iframe qui écrit le cookie était détruite avant d'avoir chargé → cookie jamais écrit.
     L'attente est maintenant de 1,5 s (connexion) / 1 s (thème), et le script JS est unique à chaque appel.
  4. `read_cookie` lit d'abord les en-têtes HTTP (`st.context.cookies`), puis le contrôleur de session.

Usage : from src.core.cookies import set_cookie, read_cookie, delete_cookie, cookie_mgr, COOKIE_NAME
"""

import json
import time
import uuid
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as _components
from streamlit_cookies_controller import CookieController

from src.core.config import COOKIE_NAME

_CTL_KEY = "vs_cookies"


def _ctl():
    """Contrôleur de cookies propre à la session (rend le composant au 1er passage, puis lit le cache de session)."""
    try:
        return CookieController(key=_CTL_KEY)
    except Exception:
        return None


class _Proxy:
    """Même API que l'ancien `cookie_mgr` global (get / getAll / set / remove / refresh)."""

    def __getattr__(self, name):
        c = _ctl()
        if c is None:
            raise AttributeError(name)
        return getattr(c, name)

    def get(self, name):
        c = _ctl()
        return c.get(name) if c else None


cookie_mgr = _Proxy()


def set_cookie(name, value, max_age=7 * 24 * 3600, wait=None):
    """Écrit un cookie (lib + JS), puis attend que le navigateur ait eu le temps d'exécuter l'écriture."""
    value = str(value)
    # 1) via la lib (arguments corrigés)
    try:
        c = _ctl()
        if c is not None:
            c.set(name, value, path="/", max_age=max_age, expires=datetime.now() + timedelta(seconds=max_age), same_site="lax")
    except Exception:
        pass
    # 2) via JS (iframe, parent, top) — identifiant unique pour que le script soit toujours ré-exécuté
    secure = "; Secure" if _is_https() else ""
    ck = json.dumps(f"{name}={value}; path=/; max-age={int(max_age)}; SameSite=Lax{secure}")
    js = f"""<script>/*{uuid.uuid4().hex}*/try {{
var c = {ck};
document.cookie = c;
try {{ if (window.parent && window.parent !== window) window.parent.document.cookie = c; }} catch(e) {{}}
try {{ if (window.top && window.top !== window.parent) window.top.document.cookie = c; }} catch(e) {{}}
}} catch(e) {{}}</script>"""
    try:
        _components.html(js, height=0, width=0)
    except Exception:
        pass
    time.sleep(wait if wait is not None else (1.5 if name != "ys_theme" else 1.0))


def delete_cookie(name):
    """Supprime un cookie (lib + JS sur tous les chemins/domaines)."""
    try:
        c = _ctl()
        if c is not None and c.get(name):
            c.remove(name, path="/", same_site="lax")
    except Exception:
        pass
    js = f"""<script>/*{uuid.uuid4().hex}*/try {{
var n = {json.dumps(name)};
var paths = ['/', window.location.pathname];
var domains = [null, window.location.hostname, '.' + window.location.hostname];
function kill(doc) {{ paths.forEach(function(p) {{ domains.forEach(function(d) {{
  var c = n + '=; path=' + p + '; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
  if (d) c += '; domain=' + d; doc.cookie = c; }}); }}); }}
kill(document);
try {{ if (window.parent && window.parent !== window) kill(window.parent.document); }} catch(e) {{}}
try {{ if (window.top && window.top !== window.parent) kill(window.top.document); }} catch(e) {{}}
}} catch(e) {{}}</script>"""
    try:
        _components.html(js, height=0, width=0)
    except Exception:
        pass
    time.sleep(1.0)


def read_cookie(name):
    """Lit un cookie : en-têtes HTTP d'abord, puis contrôleur de la session."""
    try:
        val = st.context.cookies.get(name)
        if val:
            return val
    except Exception:
        pass
    try:
        return _ctl().get(name) or None   # type: ignore
    except Exception:
        return None


def _is_https():
    try:
        return str(st.context.headers.get("X-Forwarded-Proto", "")).lower() == "https" or \
               str(st.context.url or "").startswith("https")
    except Exception:
        return False