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

def _navbar_css():
    """Barre responsive. Mobile : grille CSS (marque + thème / 4 liens / CTA pleine largeur).
    La grille ignore les flex-basis/min-width imposés par Streamlit sur les colonnes."""
    st.markdown("""<style>
html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stHorizontalBlock"] { align-items:center; }
html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) .stButton > button { transition:transform .2s ease, box-shadow .25s ease, background .2s ease; }
html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) .stButton > button:hover { transform:translateY(-1px); }
@media (max-width: 900px) {
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) { padding:.55rem .65rem .7rem !important; overflow:visible !important; white-space:normal !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stHorizontalBlock"] {
    display:grid !important; grid-template-columns:repeat(4,minmax(0,1fr)) !important; gap:.3rem !important;
    width:100% !important; max-width:100% !important; min-width:0 !important; flex-wrap:nowrap !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"] {
    width:auto !important; min-width:0 !important; max-width:100% !important; flex:none !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(1) { grid-column:1 / 4; grid-row:1; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(7) { grid-column:4; grid-row:1; justify-self:end; width:46px !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(2) { grid-column:1; grid-row:2; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(3) { grid-column:2; grid-row:2; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(4) { grid-column:3; grid-row:2; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(5) { grid-column:4; grid-row:2; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(6) { grid-column:1 / -1; grid-row:3; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) .stButton > button { width:100% !important; min-height:38px !important; padding:.3rem .1rem !important; font-size:.7rem !important; white-space:nowrap !important; overflow:visible !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) .stButton > button p { text-overflow:clip !important; overflow:visible !important; white-space:nowrap !important; font-size:.72rem !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(6) .stButton > button p { font-size:.95rem !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) .stButton > button .stMarkdownEllipsis { overflow:visible !important; text-overflow:clip !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(6) .stButton > button { min-height:44px !important; font-size:.92rem !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav:has(.lnav) [data-testid="stColumn"]:nth-child(7) .stButton > button { min-width:0 !important; padding:.3rem !important; font-size:1.05rem !important; }
}
</style>""", unsafe_allow_html=True)


def render_navbar():
    """Affiche la barre de navigation publique (visiteurs)."""
    try:
        _box = st.container(key="vsnav")
    except TypeError:
        _box = st.container()
    _navbar_css()
    with _box:
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
    """Footer unifié (premium, responsive, clair/sombre)."""
    L = st.session_state.get("theme", "light") == "light"
    ink = "#0F1A2E" if L else "#F8FAFC"
    soft = "#4A5A7A" if L else "rgba(203,213,225,.85)"
    bg = "linear-gradient(160deg,#FFFFFF,#EEF3FB)" if L else "linear-gradient(160deg,#0A1220,#0D1830)"
    line = "rgba(15,26,46,.10)" if L else "rgba(255,255,255,.10)"
    hov = "#2E6DB4" if L else "#FFFFFF"
    chip = "rgba(46,109,180,.10)" if L else "rgba(255,255,255,.07)"
    wa = "".join(ch for ch in str(PAYMENT_WAVE) if ch.isdigit())
    css = f"""<style>
html body .stApp .vsf {{ position:relative; overflow:hidden; margin-top:3rem; border-radius:26px; background:{bg}; border:1px solid {line};
  box-shadow:0 24px 60px rgba(4,16,31,{".08" if L else ".35"}); padding:2.4rem clamp(1.1rem,3vw,2.2rem) 1.3rem; text-align:left; white-space:normal; }}
html body .stApp .vsf::before {{ content:""; position:absolute; top:0; left:10%; right:10%; height:2px; background:linear-gradient(90deg,transparent,#3B82F6,#10B981,#D4AF37,transparent); }}
html body .stApp .vsf-grid {{ display:grid; grid-template-columns:1.5fr 1fr 1fr 1.2fr; gap:2rem; }}
html body .stApp .vsf-logo {{ display:flex; align-items:center; gap:10px; font-family:'Sora',sans-serif; font-weight:800; font-size:1.2rem; color:{ink} !important; margin-bottom:.8rem; }}
html body .stApp .vsf-logo i {{ font-style:normal; background:linear-gradient(92deg,#2E6DB4,#10B981); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
html body .stApp .vsf p {{ color:{soft} !important; font-size:.9rem; line-height:1.65; margin:0; }}
html body .stApp .vsf h5 {{ font-family:'Sora',sans-serif; font-weight:800; font-size:.8rem; letter-spacing:.12em; text-transform:uppercase; color:{ink} !important; margin:0 0 .9rem; padding:0; }}
html body .stApp .vsf ul {{ list-style:none; padding:0; margin:0; display:grid; gap:.55rem; }}
html body .stApp .vsf li {{ color:{soft} !important; font-size:.9rem; display:flex; align-items:center; gap:8px; }}
html body .stApp .vsf li svg {{ color:#2E6DB4; stroke:currentColor; }}
html body .stApp .vsf a.l {{ color:{soft} !important; text-decoration:none; transition:color .2s ease, transform .2s ease; display:inline-block; }}
html body .stApp .vsf a.l:hover {{ color:{hov} !important; transform:translateX(3px); }}
html body .stApp .vsf-soc {{ display:flex; gap:10px; margin-top:1.1rem; }}
html body .stApp .vsf-soc a {{ width:40px; height:40px; border-radius:12px; display:inline-flex; align-items:center; justify-content:center; background:{chip}; border:1px solid {line}; color:{soft} !important; transition:all .3s cubic-bezier(.16,1,.3,1); }}
html body .stApp .vsf-soc a:hover {{ transform:translateY(-3px); color:#fff !important; background:linear-gradient(135deg,#1B3B6F,#2E6DB4); border-color:transparent; }}
html body .stApp .vsf-cta {{ display:inline-flex; align-items:center; gap:8px; margin-top:1rem; padding:10px 18px; border-radius:999px; background:linear-gradient(135deg,#1B3B6F,#2E6DB4); color:#fff !important; font-weight:700; font-size:.88rem; text-decoration:none; box-shadow:0 10px 24px rgba(46,109,180,.3); transition:transform .25s ease; }}
html body .stApp .vsf-cta:hover {{ transform:translateY(-2px); }}
html body .stApp .vsf-cta svg {{ stroke:#fff; }}
html body .stApp .vsf-copy {{ margin-top:1.8rem; padding-top:1rem; border-top:1px solid {line}; display:flex; flex-wrap:wrap; gap:.6rem 1.5rem; justify-content:space-between; align-items:center; color:{soft} !important; font-size:.82rem; }}
html body .stApp .vsf-copy b {{ color:{ink} !important; }}
html body .stApp .vsf-copy span {{ color:{soft} !important; }}
html body .stApp .vsf-links {{ display:flex; flex-wrap:wrap; justify-content:center; gap:.5rem 1.4rem; margin-top:1.1rem; padding-top:1rem; border-top:1px solid {line}; }}
html body .stApp .vsf-c {{ text-align:center; }}
@media (max-width:900px) {{ html body .stApp .vsf-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); gap:1.6rem; }} }}
@media (max-width:560px) {{ html body .stApp .vsf-grid {{ grid-template-columns:1fr; }} html body .stApp .vsf {{ border-radius:20px; }}
  html body .stApp .vsf-copy {{ justify-content:center; text-align:center; }} }}
</style>"""
    links = [("accueil", T("home")), ("about", T("about")), ("contact", T("m_contact")),
             ("premium", T("m_premium")), ("login", T("login")), ("register", T("register"))]
    if compact:
        lk = "".join(f'<a class="l" href="?page={p}">{n}</a>' for p, n in links)
        html = (f'<div class="vsf vsf-c"><div class="vsf-logo" style="justify-content:center">{logo_html(26)} <span>VideoScribe <i>AI</i></span></div>'
                f'<p>© 2026 <b style="color:{ink}">VideoScribe AI</b> — Mbtech-services<br>'
                f'<span style="opacity:.8;font-size:.82rem">{CONTACT_EMAIL} • {PAYMENT_WAVE} • Cambérène, Dakar — Sénégal</span></p>'
                f'<div class="vsf-links">{lk}</div></div>')
        st.markdown(css + html, unsafe_allow_html=True)
        return
    lk = "".join(f'<li><a class="l" href="?page={p}">{n}</a></li>' for p, n in links)
    wa_btn = f'<a href="https://wa.me/{wa}" target="_blank" rel="noopener" title="WhatsApp">{ic("msg",16)}</a>' if wa else ""
    html = f"""<div class="vsf"><div class="vsf-grid">
<div><div class="vsf-logo">{logo_html(30)} <span>VideoScribe <i>AI</i></span></div>
<p>Application de résumé IA de vidéos YouTube, spécialisée dans la création de notes structurées personnalisées.</p>
<div class="vsf-soc"><a href="mailto:{CONTACT_EMAIL}" title="Email">{ic("mail",16)}</a>{wa_btn}<a href="https://github.com/ibuuuu19" target="_blank" rel="noopener" title="GitHub">{ic("code",16)}</a></div></div>
<div><h5>Fonctionnalités</h5><ul><li>Résumés IA</li><li>Traduction automatique</li><li>Mots-clés &amp; flashcards</li><li>Quiz interactif</li><li>Exports pro</li></ul></div>
<div><h5>{T("ft_links")}</h5><ul>{lk}</ul></div>
<div><h5>Contact</h5><ul><li>{ic("mail",14)} {CONTACT_EMAIL}</li><li>{ic("phone",14)} {PAYMENT_WAVE}</li><li>{ic("map",14)} Cambérène, Dakar — Sénégal</li></ul>
<a class="vsf-cta" href="mailto:{CONTACT_EMAIL}">{ic("send",15)} Nous écrire</a></div>
</div><div class="vsf-copy"><span>© 2026 <b>VideoScribe AI</b> — Mbtech-services. Tous droits réservés.</span><span>Fait avec ♥ à Dakar</span></div></div>"""
    st.markdown((css + html).replace("\n<", "<"), unsafe_allow_html=True)