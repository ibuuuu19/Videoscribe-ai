"""
Module de préférences utilisateur — Persistance et chargement.

Contient :
- Gestion du fichier data/prefs.json
- Sauvegarde/chargement de l'apparence (accent, font size, line height)
- Gestion de la langue

Extrait de app.py pour alléger le fichier principal (~80 lignes).

Usage:
    from src.ui.prefs import get_prefs, set_pref, _load_appearance
"""

import json
from pathlib import Path

import streamlit as st


# ═══════════════════════════════════════════════════════════════
# GESTION DU FICHIER DE PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════════

def _prefs_file():
    """Retourne le chemin du fichier de préférences."""
    return Path("data") / "prefs.json"


def _load_prefs():
    """Charge toutes les préférences depuis le fichier JSON."""
    p = _prefs_file()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def get_prefs(uname):
    """Retourne les préférences d'un utilisateur (ou {} si non connecté)."""
    return _load_prefs().get(uname, {}) if uname else {}


def set_pref(uname, key, val):
    """Enregistre une préférence pour un utilisateur."""
    allp = _load_prefs()
    allp.setdefault(uname, {})[key] = val
    p = _prefs_file()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(allp, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
# APPARENCE (accent, font size, line height)
# ═══════════════════════════════════════════════════════════════

def _save_appearance():
    """Sauvegarde les préférences d'apparence de l'utilisateur connecté."""
    u = st.session_state.get("user")
    if u:
        set_pref(u, "accent", st.session_state.get("cfg_accent", "#2E6DB4"))
        set_pref(u, "font_size", st.session_state.get("cfg_font_size", 16))
        set_pref(u, "line_height", st.session_state.get("cfg_line_height", 1.6))


def _load_appearance(uname):
    """Charge les préférences d'apparence d'un utilisateur."""
    pr = get_prefs(uname)
    st.session_state.cfg_lang = pr.get("lang", st.session_state.get("cfg_lang", "fr"))
    st.session_state.cfg_accent = pr.get("accent", "#2E6DB4")
    st.session_state.cfg_font_size = pr.get("font_size", 16)
    st.session_state.cfg_line_height = pr.get("line_height", 1.6)


# ═══════════════════════════════════════════════════════════════
# LANGUE
# ═══════════════════════════════════════════════════════════════

def set_language(lang):
    """Change la langue de l'interface et la sauvegarde."""
    st.session_state.cfg_lang = lang
    st.session_state.cfg_target = lang if lang != "fr" else "fr"
    u = st.session_state.get("user")
    if u:
        set_pref(u, "lang", lang)
    st.rerun()