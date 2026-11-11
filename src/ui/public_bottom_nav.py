"""
Barre de navigation du BAS pour les pages publiques (visiteurs), sur mobile — même style « verre dépoli » que les pages privées.

    Accueil · À propos · [ + Créer un compte ] · Contact · Connexion

• ≤ 900 px uniquement ; sur ordinateur la barre du haut reste inchangée.
• La barre du haut passe en version compacte (logo + bascule clair/sombre) : les liens et le CTA sont déplacés en bas.
• Mêmes callbacks que le reste de l'appli : `st.session_state.page = …` (aucun rechargement de page).

Intégration : dans `src/ui/navbar.py`, à la FIN de `render_navbar()` :

    from src.ui.public_bottom_nav import render_public_bottom_nav
    render_public_bottom_nav()
"""
from urllib.parse import quote

import streamlit as st

from src.ui.i18n import T

_PATHS = {
    "home":   '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "info":   '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.6v.01"/>',
    "plus":   '<path d="M12 5v14M5 12h14"/>',
    "phone":  '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "login":  '<path d="M14 4h4a2 2 0 012 2v12a2 2 0 01-2 2h-4"/><path d="M10 8l-4 4 4 4M6 12h11"/>',
}
_TARGET = {"pn_home": "accueil", "pn_about": "about", "pn_new": "register", "pn_contact": "contact", "pn_login": "login"}


def _mask(name: str, sw: float = 2) -> str:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" '
           f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{_PATHS[name]}</svg>')
    return f'url("data:image/svg+xml,{quote(svg)}")'


def _go(page: str) -> None:
    st.session_state.page = page
    st.session_state.show_privacy = False


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


_CSS = """
.stApp .st-key-pnav { display:none; }
@media (max-width:900px) {
  /* barre du haut compacte : logo + thème */
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav { padding:.4rem 0 !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav [data-testid="stHorizontalBlock"] { grid-template-columns:minmax(0,1fr) 46px !important; padding:0 .8rem !important; row-gap:0 !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav [data-testid="stColumn"]:nth-child(n+2):nth-child(-n+6) { display:none !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav [data-testid="stColumn"]:nth-child(1) { grid-column:1 !important; grid-row:1 !important; }
  html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav [data-testid="stColumn"]:nth-child(7) { grid-column:2 !important; grid-row:1 !important; justify-self:end; }
  html body .stApp div[data-testid="stMainBlockContainer"], html body .stApp section.main > div.block-container { padding-top:4.6rem !important; padding-bottom:8.5rem !important; }

  /* barre du bas */
  html body .stApp div[data-testid="stVerticalBlock"].st-key-pnav { display:block !important; position:fixed !important; left:12px !important; right:12px !important; width:calc(100vw - 24px) !important; max-width:calc(100vw - 24px) !important;
    box-sizing:border-box !important; bottom:calc(12px + env(safe-area-inset-bottom)) !important; z-index:999985 !important; padding:5px !important; margin:0 !important;
    background:@glass@ !important; border:1px solid @gline@ !important; border-radius:38px !important; backdrop-filter:blur(34px) saturate(210%); -webkit-backdrop-filter:blur(34px) saturate(210%);
    box-shadow:0 14px 40px rgba(8,20,45,.24), 0 2px 8px rgba(8,20,45,.10), inset 0 1px 0 rgba(255,255,255,.45); animation:pnUp .5s cubic-bezier(.22,.9,.3,1) both; }
  @keyframes pnUp { from { transform:translateY(120%); opacity:0; } to { transform:none; opacity:1; } }
  html body .stApp .st-key-pnav [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:repeat(5,minmax(0,1fr)) !important; gap:0 !important; width:100% !important; align-items:center !important; flex-wrap:nowrap !important; flex-direction:row !important; }
  html body .stApp .st-key-pnav [data-testid="stColumn"] { width:auto !important; min-width:0 !important; flex:none !important; }
  html body .stApp .st-key-pnav [data-testid="stElementContainer"] { width:100% !important; }
  html body .stApp .st-key-pnav .stButton > button, html body .stApp .st-key-pnav .stButton > button[data-testid="stBaseButton-primary"], html body .stApp .st-key-pnav .stButton > button[data-testid="stBaseButton-secondary"] {
    width:100% !important; min-height:58px !important; padding:8px 0 6px !important; flex-direction:column !important; justify-content:center !important; gap:4px !important;
    background:transparent !important; border:none !important; box-shadow:none !important; border-radius:32px !important; color:@soft@ !important;
    transition:background .35s ease,color .3s ease,transform .3s cubic-bezier(.34,1.56,.64,1) !important; }
  html body .stApp .st-key-pnav .stButton > button::before { content:""; width:26px; height:26px; background:currentColor; flex:none; -webkit-mask:var(--ic) center/contain no-repeat; mask:var(--ic) center/contain no-repeat;
    transition:transform .35s cubic-bezier(.34,1.56,.64,1); }
  html body .stApp .st-key-pnav .stButton > button p { color:inherit !important; font-size:.66rem !important; font-weight:600 !important; line-height:1.1 !important; margin:0 !important; white-space:nowrap !important; }
  html body .stApp .st-key-pnav .stButton > button .stMarkdownEllipsis { overflow:visible !important; text-overflow:clip !important; }
  html body .stApp .st-key-pnav .stButton > button[data-testid="stBaseButton-primary"] { color:@acc@ !important; background:@cap@ !important; box-shadow:inset 0 1px 0 rgba(255,255,255,.35), 0 2px 10px rgba(8,20,45,.08) !important; }
  html body .stApp .st-key-pnav .stButton > button[data-testid="stBaseButton-primary"] p { font-weight:800 !important; }
  html body .stApp .st-key-pnav .stButton > button[data-testid="stBaseButton-primary"]::before { transform:scale(1.1) translateY(-1px); }
  html body .stApp .st-key-pnav .stButton > button:active { transform:scale(.92) !important; }
  html body .stApp .st-key-pn_home button { --ic:@m_home@; } html body .stApp .st-key-pn_about button { --ic:@m_info@; }
  html body .stApp .st-key-pn_contact button { --ic:@m_phone@; } html body .stApp .st-key-pn_login button { --ic:@m_login@; }
  /* bouton central : pastille dégradée « + » */
  html body .stApp .st-key-pnav .st-key-pn_new { display:flex !important; justify-content:center; }
  html body .stApp .st-key-pnav .st-key-pn_new button, html body .stApp .st-key-pnav .st-key-pn_new button[data-testid="stBaseButton-secondary"], html body .stApp .st-key-pnav .st-key-pn_new button[data-testid="stBaseButton-primary"] {
    width:50px !important; min-height:50px !important; height:50px !important; padding:0 !important; margin:0 auto !important; border-radius:50% !important;
    background:linear-gradient(135deg,@acc@,@acc2@) !important; color:#fff !important; border:none !important; box-shadow:0 10px 22px rgba(30,100,200,.40), inset 0 1px 0 rgba(255,255,255,.35) !important; justify-content:center !important; flex-direction:row !important; align-items:center !important; gap:0 !important; }
  html body .stApp .st-key-pnav .st-key-pn_new button > div { display:none !important; }
  html body .stApp .st-key-pnav .st-key-pn_new button::before { width:26px; height:26px; -webkit-mask:@m_plus@ center/contain no-repeat; mask:@m_plus@ center/contain no-repeat; }
  html body .stApp .st-key-pnav .st-key-pn_new button p { font-size:0 !important; }
}
"""


def render_public_bottom_nav() -> None:
    light = st.session_state.get("theme", "light") == "light"
    tok = {
        "acc": "#2E6DB4" if light else "#5B9BF0", "acc2": "#1B3B6F" if light else "#2E6DB4",
        "soft": "#64748B" if light else "rgba(203,213,225,.80)",
        "glass": "rgba(255,255,255,.66)" if light else "rgba(24,28,36,.62)",
        "gline": "rgba(255,255,255,.75)" if light else "rgba(255,255,255,.12)",
        "cap": "rgba(15,26,46,.09)" if light else "rgba(255,255,255,.15)",
    }
    css = _CSS
    for name in _PATHS:
        css = css.replace(f"@m_{name}@", _mask(name, 2.8 if name == "plus" else 2))
    for k, v in tok.items():
        css = css.replace(f"@{k}@", v)

    page = st.session_state.get("page", "accueil")
    labels = {"pn_home": T("home"), "pn_about": T("about"), "pn_new": T("register"),
              "pn_contact": T("m_contact"), "pn_login": T("login")}
    with _keyed("pnav"):
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        cols = st.columns(5)
        for col, key in zip(cols, ["pn_home", "pn_about", "pn_new", "pn_contact", "pn_login"]):
            with col:
                st.button(labels[key], key=key, use_container_width=True,
                          type="primary" if (_TARGET[key] == page and key != "pn_new") else "secondary",
                          on_click=_go, args=(_TARGET[key],))