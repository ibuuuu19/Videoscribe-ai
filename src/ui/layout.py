"""
Module de layout — Composants UI réutilisables.

Contient :
- get_accent() : couleur d'accent selon la page active
- hero() : bannière principale
- render_footer() : footer complet ou compact
- render_navbar() : barre de navigation publique
- notify_admins() : notification aux admins
- sync_notif_cursor() : synchronise le curseur de notifications
- notif_feedback() : affiche les toasts de notification
- _toggle_theme() : bascule light/dark

Extrait de app.py pour être réutilisable dans les pages.

Usage:
    from src.ui.layout import hero, render_footer, render_navbar
"""

import streamlit as st
import streamlit.components.v1 as _components

from src.ui.i18n import T
from src.ui.components import ic, logo_html, STARS
from src.ui.css import shade
from src.core.config import CONTACT_EMAIL, PAYMENT_WAVE
from src.core.cookies import set_cookie
from src.user_manager import list_users
from src.notification_manager import notify, get_notifications


# ═══════════════════════════════════════════════════════════════
# COULEUR D'ACCENT
# ═══════════════════════════════════════════════════════════════

def get_accent():
    """Retourne la couleur d'accent selon la page active."""
    _public_pages = {"accueil", "about", "contact", "premium", "login", "register", "landing", "share"}
    _page = st.session_state.get("page", "accueil")
    if _page in _public_pages or st.session_state.get("user") is None:
        return "#2E6DB4", "#1B3B6F"
    _acc = st.session_state.get("cfg_accent", "#2E6DB4")
    return _acc, shade(_acc, 0.55)


# ═══════════════════════════════════════════════════════════════
# HERO (bannière principale)
# ═══════════════════════════════════════════════════════════════

def hero(icon_name, title, subtitle, badges=None, use_logo=False):
    """Affiche une bannière principale avec icône, titre, sous-titre et badges."""
    b = ""
    if badges:
        b = '<div class="hero-badges">' + "".join(f'<span class="hbadge">{t}</span>' for t in badges) + '</div>'
    icon_html = logo_html(44) if use_logo else ic(icon_name, 34)
    st.markdown(f"""<div class="main-header"><div style="color:#FFFFFF !important; font-family:'Sora',sans-serif; font-size:2.1rem; font-weight:800; letter-spacing:-.02em; margin:0; display:flex; align-items:center; justify-content:center; gap:14px;"><span style="display:inline-flex;">{icon_html}</span>{title}</div><div style="color:rgba(255,255,255,.9) !important; margin:.6rem 0 0; font-size:1rem;">{subtitle}</div>{b}</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

def notify_admins(icon, text):
    """Envoie une notification à tous les admins."""
    for uname, u in list_users().items():
        if u.get("role") == "admin":
            notify(uname, icon, text)


def sync_notif_cursor(uname):
    """Synchronise le curseur de notifications pour un utilisateur."""
    notifs = get_notifications(uname)
    st.session_state.last_notif_id = notifs[0]["id"] if notifs else 0


def notif_feedback():
    """Affiche des toasts pour les nouvelles notifications."""
    if st.session_state.get("role") == "visiteur":
        return
    uname = st.session_state.get("user")
    if not uname:
        return
    notifs = get_notifications(uname)
    last_seen = st.session_state.get("last_notif_id", 0)
    fresh = [n for n in notifs if n["id"] > last_seen]
    if not fresh:
        return
    st.session_state.last_notif_id = fresh[0]["id"]
    for n in fresh[:3]:
        st.toast(n["text"])


# ═══════════════════════════════════════════════════════════════
# THÈME
# ═══════════════════════════════════════════════════════════════

def _toggle_theme():
    """Bascule entre le thème clair et sombre, et sauvegarde dans un cookie."""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    set_cookie("ys_theme", st.session_state.theme, max_age=365*24*3600)
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# NAVBAR PUBLIQUE
# ═══════════════════════════════════════════════════════════════

def render_navbar():
    """Affiche la barre de navigation publique (visiteurs)."""
    with st.container():
        st.markdown('<div class="lnav"></div>', unsafe_allow_html=True)
        b1, b2, b3, b4, b5, b6, b7 = st.columns([2.2, 1, 1, 1, 1.2, 1.6, .6])
        with b1:
            st.markdown(f'''
                <div class="lnav-brand">
                    {logo_html(32)}
                    <div class="lnav-brand-text">
                        <span class="lnav-brand-name">VideoScribe</span>
                        <span class="lnav-brand-ai">AI</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        with b2:
            if st.button(T("home"), key="ln_home", use_container_width=True):
                st.session_state.page = "accueil"; st.rerun()
        with b3:
            if st.button(T("about"), key="ln_about", use_container_width=True):
                st.session_state.page = "about"; st.rerun()
        with b4:
            if st.button(T("m_contact"), key="ln_contact", use_container_width=True):
                st.session_state.page = "contact"; st.rerun()
        with b5:
            if st.button(T("login"), key="ln_login", use_container_width=True):
                st.session_state.page = "login"; st.rerun()
        with b6:
            if st.button(f"{T('register')} →", key="ln_register", type="primary", use_container_width=True):
                st.session_state.page = "register"; st.rerun()
        with b7:
            if st.button("🌙" if st.session_state.theme == "light" else "☀️", key="ln_theme", use_container_width=True):
                _toggle_theme()


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

def render_footer(compact=False):
    """Footer unifié pour toutes les pages."""
    
    _is_light = st.session_state.get("theme", "light") == "light"
    _f_nav = "#0F1A2E" if _is_light else "#F8FAFC"
    _f_soft = "#4A5A7A" if _is_light else "rgba(148,163,184,.9)"
    _f_bg = "linear-gradient(145deg, #F8FAFC, #EFF4FB)" if _is_light else "linear-gradient(145deg, #080E18, #0C1728)"
    _f_border = "rgba(15,26,46,.10)" if _is_light else "rgba(255,255,255,.08)"
    _f_link = "#4A5A7A" if _is_light else "#cbd5e1"
    _f_link_hover = "#2E6DB4" if _is_light else "#FFFFFF"
    _f_head = "#0F1A2E" if _is_light else "#FFFFFF"
    _f_copy = "#4A5A7A" if _is_light else "#94a3b8"
    _f_copy_border = "rgba(15,26,46,.12)" if _is_light else "rgba(255,255,255,.12)"

    if compact:
        st.markdown(f"""
        <style>
        .footer-compact {{
            background: {_f_bg};
            border: 1px solid {_f_border};
            border-radius: 20px;
            margin-top: 3rem;
            padding: 1.8rem 1.5rem;
            text-align: center;
        }}
        .footer-compact .copy {{
            color: {_f_copy};
            font-size: .88rem;
            line-height: 1.7;
        }}
        .footer-compact .copy b {{
            color: {_f_nav};
            font-weight: 700;
        }}
        .footer-compact .links {{
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: .8rem;
            padding-top: .8rem;
            border-top: 1px solid {_f_copy_border};
        }}
        .footer-compact .links a {{
            color: {_f_link} !important;
            text-decoration: none;
            font-size: .82rem;
            font-weight: 600;
            transition: color .25s ease;
        }}
        .footer-compact .links a:hover {{
            color: {_f_link_hover} !important;
            text-decoration: underline;
        }}
        </style>
        <div class="footer-compact">
            <div class="copy">
                © 2026 <b>VideoScribe AI</b> — Mbtech-services<br>
                <span style="opacity:.75; font-size:.82rem;">
                    {CONTACT_EMAIL} • {PAYMENT_WAVE} • Cambérène, Dakar — Sénégal
                </span>
            </div>
            <div class="links">
                <a href="?page=accueil">{T("home")}</a>
                <a href="?page=about">{T("about")}</a>
                <a href="?page=contact">{T("m_contact")}</a>
                <a href="?page=premium">{T("m_premium")}</a>
                <a href="?page=login">{T("login")}</a>
                <a href="?page=register">{T("register")}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
                # Force l'ouverture des liens du footer dans le même onglet
        _components.html("""
        <script>
        (function() {
            try {
                var doc = window.parent.document;
                function fixLinks() {
                    doc.querySelectorAll('a[href^="?page="]').forEach(function(a) {
                        a.setAttribute('target', '_top');
                    });
                }
                fixLinks();
                setInterval(fixLinks, 500);
            } catch(e) {}
        })();
        </script>
        """, height=0, width=0)
        
        return

    st.markdown(f"""
    <style>
    .footer-dark {{
        background: {_f_bg};
        color: {_f_soft};
        border-radius: 24px;
        border: 1px solid {_f_border};
        box-shadow: 0 24px 60px rgba(4,16,31,.15);
        margin-top: 3rem;
        padding: 2.6rem 2.2rem 1.4rem;
    }}
    .fd-grid {{
        display: grid;
        grid-template-columns: 1.4fr 1fr 1fr 1fr;
        gap: 2rem;
    }}
    .fd-logo {{
        display: flex; align-items: center; gap: 9px;
        color: {_f_head}; font-size: 1.15rem;
        font-family: 'Sora', sans-serif;
        margin-bottom: .9rem;
        font-weight: 700;
    }}
    .footer-dark h5 {{
        color: {_f_head};
        font-size: 1rem;
        margin-bottom: .8rem;
        font-family: 'Sora', sans-serif;
        font-weight: 700;
    }}
    .footer-dark ul {{
        list-style: none;
        padding: 0;
        margin: 0;
    }}
    .footer-dark li {{
        padding: .3rem 0;
        font-size: .92rem;
        color: {_f_soft};
    }}
    .footer-dark p {{
        color: {_f_soft};
        font-size: .92rem;
        line-height: 1.6;
    }}
    .fd-copy {{
        border-top: 1px solid {_f_copy_border};
        margin-top: 2rem;
        padding-top: 1rem;
        text-align: center;
        font-size: .85rem;
        color: {_f_copy};
    }}
    .fd-social {{
        width: 40px; height: 40px; border-radius: 12px;
        background: rgba(46,109,180,.10);
        border: 1px solid rgba(46,109,180,.20);
        display: inline-flex; align-items: center; justify-content: center;
        color: {_f_link} !important;
        transition: all .3s cubic-bezier(.16,1,.3,1);
        text-decoration: none;
    }}
    .fd-social:hover {{
        transform: translateY(-3px);
        background: rgba(46,109,180,.20) !important;
        border-color: rgba(76,154,255,.40) !important;
        color: {_f_link_hover} !important;
    }}
    .fd-input {{
        flex: 1;
        background: {"rgba(15,26,46,.04)" if _is_light else "rgba(255,255,255,.06)"};
        border: 1px solid {_f_border};
        border-radius: 999px;
        padding: 10px 16px;
        color: {_f_nav};
        outline: none;
        font-size: .9rem;
    }}
    .fd-input::placeholder {{
        color: {_f_copy};
    }}
    .fd-send {{
        width: 42px; height: 42px; border-radius: 50%;
        background: linear-gradient(135deg, #1B3B6F, #2E6DB4);
        display: inline-flex; align-items: center; justify-content: center;
        color: #fff !important;
        flex-shrink: 0;
        transition: all .3s ease;
        cursor: pointer;
    }}
    .fd-send:hover {{
        transform: scale(1.08);
        box-shadow: 0 8px 24px rgba(46,109,180,.4);
    }}
    .fd-link {{
        color: {_f_link} !important;
        text-decoration: none;
        transition: color .25s ease;
    }}
    .fd-link:hover {{
        color: {_f_link_hover} !important;
        text-decoration: underline;
    }}
    @media (max-width: 900px) {{
        .fd-grid {{ grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
    }}
    @media (max-width: 560px) {{
        .fd-grid {{ grid-template-columns: 1fr; }}
    }}
    </style>
    <div class="footer-dark">
        <div class="fd-grid">
            <div>
                <div class="fd-logo">{logo_html(30)} <b>VideoScribe</b> AI</div>
                <p>Application de résumé IA de vidéos YouTube, spécialisée dans la création de notes structurées personnalisées.</p>
                <div style="display:flex; gap:10px; margin-top:1.1rem;">
                    <a class="fd-social" href="mailto:{CONTACT_EMAIL}" title="Email">{ic("mail",16)}</a>
                    <a class="fd-social" href="https://wa.me/{PAYMENT_WAVE.replace(' ', '')}" target="_blank" title="WhatsApp">{ic("msg",16)}</a>
                    <a class="fd-social" href="https://github.com/ibuuuu19" target="_blank" title="GitHub">{ic("code",16)}</a>
                </div>
            </div>
            <div>
                <h5>Fonctionnalités</h5>
                <ul>
                    <li>Résumés IA</li>
                    <li>Traduction automatique</li>
                    <li>Mots-clés & flashcards</li>
                    <li>Quiz interactif</li>
                    <li>Exports pro</li>
                </ul>
            </div>
            <div>
                <h5>{T("ft_links")}</h5>
                <ul>
                    <li><a class="fd-link" href="?page=accueil"  >{T("home")}</a></li>
                    <li><a class="fd-link" href="?page=about"    >{T("about")}</a></li>
                    <li><a class="fd-link" href="?page=contact"  >{T("m_contact")}</a></li>
                    <li><a class="fd-link" href="?page=premium"  >{T("m_premium")}</a></li>
                    <li><a class="fd-link" href="?page=login"    >{T("login")}</a></li>
                    <li><a class="fd-link" href="?page=register" >{T("register")}</a></li>
                </ul>
            </div>
            <div>
                <h5>Contact & Newsletter</h5>
                <ul>
                    <li>{ic("mail",13)} {CONTACT_EMAIL}</li>
                    <li>{ic("phone",13)} {PAYMENT_WAVE}</li>
                    <li>{ic("map",13)} Cambérène, Dakar — Sénégal</li>
                </ul>
                <div style="display:flex; gap:8px; margin-top:1.1rem;">
                    <input class="fd-input" placeholder="Votre email" />
                    <span class="fd-send">{ic("send",16)}</span>
                </div>
            </div>
        </div>
        <div class="fd-copy">
            © 2026 VideoScribe AI — Mbtech-services. Tous droits réservés.
        </div>
    </div>
    """, unsafe_allow_html=True)    
