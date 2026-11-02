"""
Barre de navigation publique — FIXE (toujours visible), verre dépoli, premium.

· `position: fixed` : reste en haut pendant tout le défilement (l'ancienne barre « sticky » sortait de l'écran).
· Supprime l'espace vide au-dessus de la page (en-tête Streamlit masqué, marge haute = hauteur exacte de la barre).
· Page active soulignée, bouton « Créer un compte » en dégradé, bascule clair/sombre en pastille ronde.
· Mobile (≤ 900 px) : ligne 1 = marque + CTA + thème ; ligne 2 = les 4 liens.
· Mêmes clés de boutons qu'avant (ln_home, ln_about, ln_contact, ln_login, ln_register, ln_theme) et même logique.

N'utilise PAS le marqueur `.lnav` : les anciennes règles globales `:has(.lnav)` (sticky + habillage de TOUS les boutons
de la page) ne s'appliquent donc plus.
"""
import streamlit as st

from src.ui.i18n import T
from src.ui.components import logo_html
from src.ui.layout import _toggle_theme

_ACTIVE = {"accueil": "ln_home", "about": "ln_about", "contact": "ln_contact", "login": "ln_login"}


def _css() -> None:
    light = st.session_state.get("theme", "light") == "light"
    ink = "#0F1A2E" if light else "#E8EEF8"
    soft = "#4A5A7A" if light else "rgba(203,213,225,.85)"
    bg = "rgba(255,255,255,.80)" if light else "rgba(7,11,20,.78)"
    line = "rgba(15,26,46,.08)" if light else "rgba(255,255,255,.09)"
    hov = "rgba(46,109,180,.09)" if light else "rgba(255,255,255,.08)"
    acc = "#2E6DB4" if light else "#7DB2FF"
    shadow = "0 10px 34px rgba(15,26,46,.07)" if light else "0 12px 36px rgba(0,0,0,.45)"
    act = _ACTIVE.get(st.session_state.get("page", "accueil"))
    act_css = ""
    if act:
        act_css = (f'html body .stApp .st-key-vsnav .st-key-{act} button p{{color:{acc} !important;}}'
                   f'html body .stApp .st-key-vsnav .st-key-{act} button::after{{content:"";position:absolute;left:28%;right:28%;bottom:3px;height:2px;'
                   f'border-radius:2px;background:linear-gradient(90deg,#3B82F6,#10B981);}}')
    V = 'html body .stApp div[data-testid="stVerticalBlock"].st-key-vsnav'
    st.markdown(f"""<style>
header[data-testid="stHeader"]{{display:none !important;}}
/* éléments « invisibles » (blocs <style>, iframes de scripts de hauteur 0) : sortis du flux, sinon chacun ajoute 1 rem d'espace vide */
html body .stApp div[data-testid="stMainBlockContainer"] div[data-testid="stElementContainer"]:has(style):not(:has(.vsp-w)):not(:has(.vsn-brand)),
html body .stApp div[data-testid="stMainBlockContainer"] div[data-testid="stElementContainer"]:has(iframe[height="0"]){{position:absolute !important;width:0 !important;height:0 !important;overflow:hidden !important;margin:0 !important;}}
html body .stApp div[data-testid="stMainBlockContainer"], html body .stApp section.main > div.block-container{{padding-top:5.3rem !important;}}
{V}{{position:fixed !important;top:0;left:0;right:0;width:100% !important;max-width:100% !important;z-index:1000001;margin:0 !important;gap:0 !important;
  padding:.5rem 0 !important;background:{bg} !important;backdrop-filter:blur(22px) saturate(180%);-webkit-backdrop-filter:blur(22px) saturate(180%);
  border-bottom:1px solid {line} !important;box-shadow:{shadow} !important;border-radius:0 !important;}}
{V} > div[data-testid="stElementContainer"]:has(.vsn-mark){{display:none !important;}}
{V} [data-testid="stHorizontalBlock"]{{display:grid !important;grid-template-columns:minmax(190px,1fr) repeat(4,auto) auto 46px;align-items:center;gap:.2rem !important;
  flex-wrap:nowrap !important;width:100% !important;max-width:1240px;margin:0 auto;padding:0 1.5rem;}}
{V} [data-testid="stColumn"]{{width:auto !important;min-width:0 !important;max-width:100% !important;flex:none !important;}}
{V} [data-testid="stColumn"]:nth-child(6){{margin-left:.7rem;}}
html body .stApp .vsn-brand{{display:flex;align-items:center;gap:10px;font-family:'Sora',sans-serif;font-weight:800;font-size:1.2rem;letter-spacing:-.03em;color:{ink} !important;white-space:nowrap;}}
html body .stApp .vsn-brand i{{font-style:normal;background:linear-gradient(92deg,#2E6DB4,#10B981);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}}
html body .stApp .st-key-vsnav [data-testid="stMarkdownContainer"]{{margin:0 !important;}}
html body .stApp .st-key-vsnav .stButton > button{{position:relative;background:transparent !important;border:none !important;box-shadow:none !important;border-radius:999px !important;
  padding:.5rem 1rem !important;min-height:0 !important;height:auto !important;width:auto !important;transform:none !important;filter:none !important;transition:background .2s ease,color .2s ease !important;}}
html body .stApp .st-key-vsnav .stButton > button p{{color:{soft} !important;font-weight:700 !important;font-size:.92rem !important;margin:0;white-space:nowrap;}}
html body .stApp .st-key-vsnav .stButton > button:hover{{background:{hov} !important;}}
html body .stApp .st-key-vsnav .stButton > button:hover p{{color:{ink} !important;}}
{act_css}
html body .stApp .st-key-vsnav .st-key-ln_register button{{background:linear-gradient(135deg,#1B3B6F,#2E6DB4) !important;padding:.58rem 1.35rem !important;box-shadow:0 10px 24px rgba(46,109,180,.30) !important;}}
html body .stApp .st-key-vsnav .st-key-ln_register button p{{color:#fff !important;}}
html body .stApp .st-key-vsnav .st-key-ln_register button:hover{{background:linear-gradient(135deg,#1B3B6F,#3B82F6) !important;transform:translateY(-1px) !important;}}
html body .stApp .st-key-vsnav .st-key-ln_theme button{{width:40px !important;height:40px !important;padding:0 !important;justify-content:center;border:1px solid {line} !important;background:{hov} !important;}}
@media (max-width:900px){{
  html body .stApp div[data-testid="stMainBlockContainer"], html body .stApp section.main > div.block-container{{padding-top:7.2rem !important;}}
  {V}{{padding:.45rem 0 .5rem !important;}}
  {V} [data-testid="stHorizontalBlock"]{{grid-template-columns:repeat(4,minmax(0,1fr));padding:0 .7rem;row-gap:.3rem !important;}}
  {V} [data-testid="stColumn"]:nth-child(1){{grid-column:1 / 3;grid-row:1;}}
  {V} [data-testid="stColumn"]:nth-child(6){{grid-column:3;grid-row:1;margin-left:0;justify-self:end;}}
  {V} [data-testid="stColumn"]:nth-child(7){{grid-column:4;grid-row:1;justify-self:end;}}
  {V} [data-testid="stColumn"]:nth-child(2){{grid-column:1;grid-row:2;}}
  {V} [data-testid="stColumn"]:nth-child(3){{grid-column:2;grid-row:2;}}
  {V} [data-testid="stColumn"]:nth-child(4){{grid-column:3;grid-row:2;}}
  {V} [data-testid="stColumn"]:nth-child(5){{grid-column:4;grid-row:2;}}
  html body .stApp .vsn-brand{{font-size:1.05rem;}}
  html body .stApp .st-key-vsnav .stButton > button{{width:100% !important;padding:.4rem .2rem !important;justify-content:center;}}
  html body .stApp .st-key-vsnav .stButton > button p{{font-size:.78rem !important;}}
  html body .stApp .st-key-vsnav .st-key-ln_register button{{width:auto !important;padding:.5rem .9rem !important;}}
  html body .stApp .st-key-vsnav .st-key-ln_register button p{{font-size:.76rem !important;}}
  html body .stApp .st-key-vsnav .st-key-ln_theme button{{width:38px !important;height:38px !important;}}
}}
</style>""", unsafe_allow_html=True)


def render_navbar() -> None:
    """Barre de navigation publique fixe (visiteurs)."""
    try:
        box = st.container(key="vsnav")
    except TypeError:
        box = st.container()
    _css()
    with box:
        st.markdown('<div class="vsn-mark"></div>', unsafe_allow_html=True)
        b1, b2, b3, b4, b5, b6, b7 = st.columns([2.2, 1, 1, 1, 1.2, 1.6, .6])
        with b1:
            st.markdown(f'<div class="vsn-brand">{logo_html(32)}<span>VideoScribe<i> AI</i></span></div>', unsafe_allow_html=True)
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