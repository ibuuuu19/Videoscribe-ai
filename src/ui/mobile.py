"""
Coque « application mobile » de VideoScribe AI (connectés uniquement).

Sur téléphone (≤ 768 px) l'application prend l'allure d'une vraie app :
  • barre du haut fixe  : menu ☰ · logo · pastille « analyses restantes » · cloche · avatar
  • barre du bas fixe   : Analyse · Historique · [+ Nouvelle analyse] · Stats · Premium
  • le contenu défile entre les deux (marges calculées, zones sûres iPhone respectées)

Sur ordinateur (> 768 px) rien ne change : les deux barres sont masquées et la
barre latérale reste le menu principal.

Intégration dans app.py (une seule ligne, juste après le bloc `with st.sidebar:`) :

    from src.ui.mobile import render_mobile_shell
    ...
    if not is_guest:
        render_mobile_shell(user, role, tier)

Les boutons sont de vrais `st.button` (pas de rechargement de page, la session est conservée).
"""

from urllib.parse import quote

import streamlit as st

from src.ui.components import logo_html
from src.ui.layout import get_accent, _toggle_theme
from src.core.config import FREE_DAILY_LIMIT, COOKIE_NAME
from src.core.cookies import delete_cookie
from src.session_manager import delete_session
from src.notification_manager import unread_count
from src.history_manager import count_today


# ───────────────────────── Icônes (masques SVG) ─────────────────────────
_PATHS = {
    "home":   '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "grid":   '<rect x="3" y="3" width="7" height="7" rx="1.8"/><rect x="14" y="3" width="7" height="7" rx="1.8"/>'
              '<rect x="3" y="14" width="7" height="7" rx="1.8"/><rect x="14" y="14" width="7" height="7" rx="1.8"/>',
    "plus":   '<path d="M12 5v14M5 12h14"/>',
    "chart":  '<path d="M5 20V11M12 20V4M19 20v-6"/>',
    "star":   '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "bell":   '<path d="M6 8a6 6 0 0112 0c0 7 3 8 3 8H3s3-1 3-8"/><path d="M10 21a2 2 0 004 0"/>',
    "menu":   '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close":  '<path d="M6 6l12 12M18 6L6 18"/>',
    "film":   '<rect x="3" y="4" width="18" height="16" rx="2.5"/><path d="M3 9h18M8 4v5M16 4v5M10 13l5 3-5 3z"/>',
    "phone":  '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "tool":   '<path d="M14.7 6.3a4 4 0 00-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 005.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    "gem":    '<path d="M6 3h12l4 6-10 12L2 9z"/><path d="M2 9h20M9 3l3 6 3-6M12 21L9 9M12 21l3-12"/>',
}


def _mask(name: str, sw: float = 2) -> str:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" '
           f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{_PATHS[name]}</svg>')
    return f'url("data:image/svg+xml,{quote(svg)}")'


def theme_tokens() -> dict:
    """Jetons de couleur partagés (barres mobiles + page Historique)."""
    acc, acc_dark = get_accent()
    if st.session_state.get("theme", "light") == "light":
        return dict(acc=acc, acc_dark=acc_dark, ink="#0F1A2E", soft="#64748B", surface="#FFFFFF",
                    surface2="#F1F6FD", bar="rgba(255,255,255,.90)", line="rgba(15,26,46,.09)",
                    shadow="0 10px 30px rgba(30,70,140,.10)", page="#EEF5FE")
    return dict(acc=acc, acc_dark=acc_dark, ink="#F8FAFC", soft="rgba(203,213,225,.80)",
                surface="rgba(255,255,255,.06)", surface2="rgba(255,255,255,.09)", bar="rgba(10,16,25,.90)",
                line="rgba(255,255,255,.11)", shadow="0 14px 34px rgba(0,0,0,.45)", page="#05080F")


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _go(page: str, new_analysis: bool = False):
    st.session_state.page = page
    st.session_state.show_privacy = False
    if new_analysis:
        st.session_state.result = None
    st.rerun()


# Sélecteur de base : plus spécifique que les règles globales de css.py (colonnes empilées, etc.)
_P = 'html body .stApp div[data-testid="stVerticalBlock"]'

_CSS = """
/* Desktop : barres cachées */
.stApp .st-key-mtop, .stApp .st-key-mnav, .stApp .st-key-sb_promo { display:none; }

@media (max-width: 768px) {
  /* ── Cadre général ── */
  html body .stApp { background:@page@ !important; }
  html body .stApp [data-testid="stMainBlockContainer"], html body .stApp section.main > div.block-container {
    padding-top:5rem !important; padding-bottom:8rem !important; }
  html body .stApp header[data-testid="stHeader"] { background:transparent !important; height:0 !important; min-height:0 !important; }
  html body .stApp [data-testid="stToolbarActions"], html body .stApp [data-testid="stMainMenu"],
  html body .stApp [data-testid="stAppDeployButton"], html body .stApp [data-testid="stDecoration"] { display:none !important; }

  /* Blocs <style> seuls : aucun espace dans la page */
  html body .stApp [data-testid="stMainBlockContainer"] [data-testid="stElementContainer"]:has(style:only-child) { display:none !important; }

  /* ── Bouton ☰ (ouvre la barre latérale native) ── */
  html body .stApp [data-testid="stExpandSidebarButton"], html body .stApp [data-testid="stSidebarCollapsedControl"] {
    position:fixed !important; top:11px !important; left:12px !important; z-index:999995 !important;
    width:46px !important; height:46px !important; border-radius:15px !important; padding:0 !important; margin:0 !important;
    background:@surface@ !important; border:1px solid @line@ !important; box-shadow:@shadow@ !important;
    display:flex !important; align-items:center !important; justify-content:center !important; visibility:visible !important; }
  html body .stApp [data-testid="stExpandSidebarButton"] > *, html body .stApp [data-testid="stSidebarCollapsedControl"] > * { display:none !important; }
  html body .stApp [data-testid="stExpandSidebarButton"]::before, html body .stApp [data-testid="stSidebarCollapsedControl"]::before {
    content:""; width:22px; height:22px; background:@ink@; -webkit-mask:@m_menu@ center/contain no-repeat; mask:@m_menu@ center/contain no-repeat; }

  /* ══ BARRE DU HAUT ══ */
  $P.st-key-mtop { display:block !important; position:fixed !important; top:0 !important; left:0 !important; right:0 !important; z-index:999985 !important;
    height:68px; padding:11px 12px 11px 68px !important; margin:0 !important; background:@bar@ !important;
    backdrop-filter:blur(18px) saturate(160%); -webkit-backdrop-filter:blur(18px) saturate(160%); border-bottom:1px solid @line@ !important; }
  $P.st-key-mtop [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:auto minmax(0,1fr) auto auto !important;
    gap:8px !important; align-items:center !important; width:100% !important; flex-wrap:nowrap !important; flex-direction:row !important; }
  $P.st-key-mtop [data-testid="stColumn"] { width:auto !important; min-width:0 !important; flex:none !important; }
  $P.st-key-mtop [data-testid="stColumn"]:nth-child(2) { justify-self:end; }
  $P.st-key-mtop [data-testid="stMarkdownContainer"] p { margin:0 !important; }
  $P.st-key-mtop .stButton > button { min-height:0 !important; box-shadow:none !important; }

  /* Pastille « analyses restantes » */
  .stApp .st-key-mt_credits button { height:42px !important; padding:0 6px 0 12px !important; gap:8px !important; border-radius:999px !important;
    background:@surface@ !important; border:1px solid @line@ !important; box-shadow:@shadow@ !important; width:auto !important; }
  .stApp .st-key-mt_credits button::before { content:""; width:16px; height:16px; border-radius:50%; flex:none;
    background:radial-gradient(circle at 35% 30%,#FDE68A,#F59E0B); box-shadow:0 0 0 2px rgba(245,158,11,.25); }
  .stApp .st-key-mt_credits button::after { content:"+"; width:26px; height:26px; border-radius:50%; flex:none; display:flex; align-items:center; justify-content:center;
    background:linear-gradient(135deg,#FB923C,#EA580C); color:#fff; font-weight:800; font-size:1rem; line-height:1; }
  .stApp .st-key-mt_credits button p { color:@ink@ !important; font-weight:700 !important; font-size:.8rem !important; white-space:nowrap !important; }
  .stApp .st-key-mt_credits button .stMarkdownEllipsis { overflow:visible !important; text-overflow:clip !important; }

  /* Cloche */
  .stApp .st-key-mt_bell button { width:44px !important; height:44px !important; padding:0 !important; border-radius:50% !important;
    background:@surface@ !important; border:1px solid @line@ !important; box-shadow:@shadow@ !important; position:relative; }
  .stApp .st-key-mt_bell button p { font-size:0 !important; line-height:0 !important; }
  .stApp .st-key-mt_bell button::before { content:""; width:22px; height:22px; background:@ink@; -webkit-mask:@m_bell@ center/contain no-repeat; mask:@m_bell@ center/contain no-repeat; }
  @BADGE@

  /* Avatar (popover) */
  .stApp .st-key-mt_user button { height:44px !important; padding:0 4px 0 2px !important; border:none !important; background:transparent !important; box-shadow:none !important; gap:2px !important; }
  .stApp .st-key-mt_user button p { width:42px; height:42px; border-radius:50% !important; display:flex !important; align-items:center; justify-content:center;
    background:linear-gradient(135deg,@acc@,@acc_dark@); color:#fff !important; font-weight:800 !important; font-size:.82rem !important; box-shadow:0 8px 18px rgba(30,100,200,.30); }
  .stApp .st-key-mt_user button [data-testid="stIconMaterial"] { color:@soft@ !important; font-size:1.2rem !important; }

  /* ══ BARRE DU BAS ══ */
  $P.st-key-mnav { display:block !important; position:fixed !important; left:0 !important; right:0 !important; bottom:0 !important; z-index:999985 !important;
    padding:8px 8px calc(8px + env(safe-area-inset-bottom)) !important; margin:0 !important; background:@bar@ !important;
    backdrop-filter:blur(18px) saturate(160%); -webkit-backdrop-filter:blur(18px) saturate(160%);
    border-top:1px solid @line@ !important; box-shadow:0 -12px 34px rgba(30,70,140,.08); border-radius:22px 22px 0 0; }
  $P.st-key-mnav [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:repeat(5,minmax(0,1fr)) !important; gap:2px !important;
    width:100% !important; align-items:end !important; flex-wrap:nowrap !important; flex-direction:row !important; }
  $P.st-key-mnav [data-testid="stColumn"] { width:auto !important; min-width:0 !important; flex:none !important; }
  $P.st-key-mnav [data-testid="stElementContainer"] { width:100% !important; }
  $P.st-key-mnav .stButton > button, $P.st-key-mnav .stButton > button[data-testid="stBaseButton-primary"], $P.st-key-mnav .stButton > button[data-testid="stBaseButton-secondary"] {
    width:100% !important; min-height:56px !important; padding:6px 0 2px !important; flex-direction:column !important; gap:4px !important;
    background:transparent !important; border:none !important; box-shadow:none !important; border-radius:14px !important; color:@soft@ !important; }
  $P.st-key-mnav .stButton > button::before { content:""; width:24px; height:24px; background:currentColor; flex:none;
    -webkit-mask:var(--ic) center/contain no-repeat; mask:var(--ic) center/contain no-repeat; transition:transform .25s cubic-bezier(.16,1,.3,1); }
  $P.st-key-mnav .stButton > button p { color:inherit !important; font-size:.68rem !important; font-weight:700 !important; line-height:1.1 !important; margin:0 !important; white-space:nowrap !important; }
  $P.st-key-mnav .stButton > button .stMarkdownEllipsis { overflow:visible !important; text-overflow:clip !important; }
  $P.st-key-mnav .stButton > button[data-testid="stBaseButton-primary"] { color:@acc@ !important; }
  $P.st-key-mnav .stButton > button[data-testid="stBaseButton-primary"]::before { transform:translateY(-1px) scale(1.1); }
  $P.st-key-mnav .stButton > button:active { transform:scale(.94); }
  .stApp .st-key-mn_analyse button { --ic:@m_home@; } .stApp .st-key-mn_hist button { --ic:@m_grid@; }
  .stApp .st-key-mn_stats button { --ic:@m_chart@; } .stApp .st-key-mn_premium button { --ic:@m_star@; }

  /* Bouton central « + » */
  .stApp .st-key-mn_new { display:flex !important; justify-content:center; }
  $P.st-key-mnav .st-key-mn_new button, $P.st-key-mnav .st-key-mn_new button[data-testid="stBaseButton-secondary"] {
    width:60px !important; min-height:60px !important; height:60px !important; padding:0 !important; margin-top:-34px !important; border-radius:21px !important;
    background:linear-gradient(135deg,@acc@,@acc_dark@) !important; color:#fff !important; border:4px solid @surface_solid@ !important;
    box-shadow:0 16px 30px rgba(30,100,200,.38) !important; justify-content:center !important; }
  $P.st-key-mnav .st-key-mn_new button::before { width:28px; height:28px; -webkit-mask:@m_plus@ center/contain no-repeat; mask:@m_plus@ center/contain no-repeat; }
  $P.st-key-mnav .st-key-mn_new button p { font-size:0 !important; }
  /* ══ TIROIR (menu ☰) : mêmes liens que la barre latérale, style application ══ */
  html body .stApp [data-testid="stSidebar"] { width:min(86vw,330px) !important; min-width:0 !important; background:@surface_solid@ !important;
    border-radius:0 26px 26px 0 !important; border-right:1px solid @line@ !important; box-shadow:0 0 60px rgba(8,20,45,.35) !important; }
  html body .stApp [data-testid="stSidebar"] > div { background:transparent !important; }
  html body .stApp [data-testid="stSidebarContent"] { padding:0 14px 20px !important; }
  html body .stApp [data-testid="stSidebarHeader"] { padding:14px 4px 0 !important; height:auto !important; position:absolute; top:6px; right:8px; z-index:5; }
  html body .stApp [data-testid="stSidebarCollapseButton"] button, html body .stApp [data-testid="stSidebarCollapseButton"] { width:40px !important; height:40px !important; border-radius:50% !important; display:flex !important; align-items:center; justify-content:center; background:transparent !important; }
  html body .stApp [data-testid="stSidebarCollapseButton"] button > *, html body .stApp [data-testid="stSidebarCollapseButton"] > button > * { display:none !important; }
  html body .stApp [data-testid="stSidebarCollapseButton"] button::before { content:""; width:22px; height:22px; background:@soft@; -webkit-mask:@m_close@ center/contain no-repeat; mask:@m_close@ center/contain no-repeat; }
  html body .stApp [data-testid="stSidebar"] .qbrand { display:flex; align-items:center; gap:12px; font-size:1.45rem !important; padding:1.1rem .2rem 1rem !important; margin:0 -4px .6rem !important; border-bottom:1px solid @line@; color:@ink@ !important; }
  html body .stApp [data-testid="stSidebar"] .qbrand span, html body .stApp [data-testid="stSidebar"] .qbrand b { color:@ink@ !important; }
  html body .stApp [data-testid="stSidebar"] .qcap { font-size:.72rem !important; font-weight:800 !important; letter-spacing:.16em !important; text-transform:uppercase; color:@soft@ !important; margin:1.2rem 0 .4rem .6rem !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button { justify-content:flex-start !important; gap:14px !important; min-height:50px !important; padding:0 14px !important;
    background:transparent !important; border:none !important; box-shadow:none !important; border-radius:14px !important; color:@soft@ !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button p { color:inherit !important; font-size:1rem !important; font-weight:600 !important; margin:0 !important; text-align:left !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button > div, html body .stApp [data-testid="stSidebar"] .stButton > button [data-testid="stMarkdownContainer"] { width:auto !important; flex:1 1 auto; justify-content:flex-start !important; text-align:left !important; }
  html body .stApp [data-testid="stSidebar"] [class*="st-key-nav_"] .stButton > button[data-testid="stBaseButton-secondary"] p, html body .stApp [data-testid="stSidebar"] [class*="st-key-nav_"] .stButton > button[data-testid="stBaseButton-secondary"] span { color:@ink@ !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button .vs-ic { display:none !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] { background:@acc_tint@ !important; color:@acc@ !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] p { font-weight:700 !important; color:@acc@ !important; }
  html body .stApp [data-testid="stSidebar"] .stButton > button::before { content:""; width:22px; height:22px; flex:none; background:currentColor; -webkit-mask:var(--ic) center/contain no-repeat; mask:var(--ic) center/contain no-repeat; }
  html body .stApp [data-testid="stSidebar"] [class*="st-key-nav_"] button:hover { background:@surface2@ !important; }
  .stApp [data-testid="stSidebar"] .st-key-nav_analyse button { --ic:@m_film@; }
  .stApp [data-testid="stSidebar"] .st-key-nav_premium button { --ic:@m_star@; }
  .stApp [data-testid="stSidebar"] .st-key-nav_historique button { --ic:@m_grid@; }
  .stApp [data-testid="stSidebar"] .st-key-nav_stats button { --ic:@m_chart@; }
  .stApp [data-testid="stSidebar"] .st-key-nav_contact button { --ic:@m_phone@; }
  .stApp [data-testid="stSidebar"] .st-key-nav_notifs button { --ic:@m_bell@; }
  .stApp [data-testid="stSidebar"] .st-key-nav_admin button { --ic:@m_tool@; }
  /* Carte « Passer à Premium » en bas du tiroir */
  .stApp [data-testid="stSidebar"] .st-key-sb_promo { margin-top:1.4rem; padding:16px; border-radius:22px; background:@acc_tint@; border:1px solid @line@; display:block !important; }
  html body .stApp [data-testid="stSidebar"] .st-key-sb_promo { display:flex !important; flex-direction:column !important; gap:.9rem !important; }
  .stApp [data-testid="stSidebar"] .st-key-sb_promo p { color:@soft@ !important; font-size:.84rem; line-height:1.5; margin:0; }
  .stApp [data-testid="stSidebar"] .st-key-sb_promo .sbp-t { display:flex; align-items:center; gap:10px; font-weight:800; font-size:1rem; color:@ink@ !important; margin-bottom:.5rem; }
  .stApp [data-testid="stSidebar"] .st-key-sb_promo .sbp-t i { width:28px; height:28px; border-radius:9px; background:linear-gradient(135deg,@acc@,@acc_dark@); display:inline-block; -webkit-mask:none; position:relative; }
  .stApp [data-testid="stSidebar"] .st-key-sb_promo .sbp-t i::after { content:""; position:absolute; inset:5px; background:#fff; -webkit-mask:@m_gem@ center/contain no-repeat; mask:@m_gem@ center/contain no-repeat; }
  html body .stApp [data-testid="stSidebar"] .st-key-sb_promo .stButton > button { justify-content:center !important; height:48px !important; margin:0; border-radius:14px !important; background:linear-gradient(135deg,@acc@,@acc_dark@) !important; box-shadow:0 12px 24px rgba(30,100,200,.30) !important; color:#fff !important; }
  html body .stApp [data-testid="stSidebar"] .st-key-sb_promo .stButton > button::before { display:none; }
  html body .stApp [data-testid="stSidebar"] .st-key-sb_promo .stButton > button p, html body .stApp [data-testid="stSidebar"] .st-key-sb_promo .stButton > button > div { color:#fff !important; font-weight:800 !important; text-align:center !important; justify-content:center !important; }
}
"""


def render_mobile_shell(user: str, role: str, tier: int) -> None:
    """Barres haut/bas façon application mobile. À appeler une fois par exécution, pour un utilisateur connecté."""
    t = theme_tokens()
    page = st.session_state.get("page", "analyse")
    active = {"accueil": "analyse", "analyse": "analyse", "historique": "historique",
              "stats": "stats", "premium": "premium"}.get(page, "")

    try:
        n_unread = int(unread_count(user))
    except Exception:
        n_unread = 0
    solid = "#FFFFFF" if st.session_state.get("theme", "light") == "light" else "#0A1019"
    badge = ""
    if n_unread > 0:
        badge = (f'.stApp .st-key-mt_bell button::after {{ content:"{min(n_unread, 9)}{"+" if n_unread > 9 else ""}"; position:absolute; top:-3px; right:-3px; min-width:19px; height:19px; '
                 f'padding:0 5px; border-radius:999px; background:#EF4444; color:#fff; font-size:.66rem; font-weight:800; display:flex; align-items:center; justify-content:center; border:2px solid {solid}; }}')

    css = _CSS.replace("$P", _P).replace("@BADGE@", badge).replace("@surface_solid@", solid)
    for name in ("home", "grid", "chart", "star", "plus", "bell", "menu", "close", "film", "phone", "tool", "gem"):
        css = css.replace(f"@m_{name}@", _mask(name, 2.8 if name == "plus" else 2))
    hx = t["acc"].lstrip("#")
    try:
        r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
        tint = f"rgba({r},{g},{b},{'.12' if st.session_state.get('theme','light') == 'light' else '.20'})"
    except Exception:
        tint = "rgba(46,109,180,.12)"
    t = {**t, "acc_tint": tint, "surface_solid": solid}
    for k, v in t.items():
        css = css.replace(f"@{k}@", v)
    style_tag = f"<style>{css}</style>"   # injecté dans la barre fixe : aucun espace ajouté au flux de la page

    # ── Libellé de la pastille ──
    if tier == 0:
        try:
            left = max(int(FREE_DAILY_LIMIT) - int(count_today(user)), 0)
            credit_label = f"{left} analyse{'s' if left > 1 else ''}"
        except Exception:
            credit_label = "Analyses"
    else:
        credit_label = "Illimité"

    # ══════════ CARTE PREMIUM DU TIROIR (comptes gratuits / Basique) ══════════
    if tier < 2:
        with st.sidebar:
            with _keyed("sb_promo"):
                st.markdown('<div class="sbp-t"><i></i>Passez à Premium</div>'
                            '<p>Analyses illimitées, quiz, chat vidéo, exports PDF, Notion et Obsidian.</p>', unsafe_allow_html=True)
                if st.button("Voir les offres", key="sb_promo_btn", use_container_width=True):
                    _go("premium")

    # ══════════ BARRE DU HAUT ══════════
    with _keyed("mtop"):
        c1, c2, c3, c4 = st.columns([1, 3, 1, 1.4])
        with c1:
            st.markdown(style_tag + f'<div style="display:flex;align-items:center;">{logo_html(36)}</div>', unsafe_allow_html=True)
        with c2:
            if st.button(credit_label, key="mt_credits", help="Voir les offres"):
                _go("premium")
        with c3:
            if st.button("Notifications", key="mt_bell"):
                _go("notifs")
        with c4:
            with _keyed("mt_user"):
                with st.popover(user[:2].upper()):
                    if st.button("Profil", key="mt_profil", use_container_width=True): _go("profil")
                    if st.button("Paramètres", key="mt_config", use_container_width=True): _go("config")
                    if st.button("Notifications" + (f" ({n_unread})" if n_unread else ""), key="mt_notifs", use_container_width=True): _go("notifs")
                    if st.button("Contact", key="mt_contact", use_container_width=True): _go("contact")
                    if role == "admin" and st.button("Administration", key="mt_admin", use_container_width=True): _go("admin")
                    st.divider()
                    dark = st.session_state.get("theme", "light") == "dark"
                    if st.button("Passer en mode clair" if dark else "Passer en mode sombre", key="mt_theme", use_container_width=True):
                        _toggle_theme()
                    if st.button("Se déconnecter", key="mt_logout", use_container_width=True):
                        if st.session_state.get("token"):
                            try: delete_session(st.session_state.get("token"))
                            except Exception: pass
                        delete_cookie(COOKIE_NAME); delete_cookie("ys_user"); delete_cookie("ys_theme")
                        st.session_state._logged_out = True
                        st.rerun()

    # ══════════ BARRE DU BAS ══════════
    with _keyed("mnav"):
        cols = st.columns(5)
        tabs = [("mn_analyse", "Analyse", "analyse"), ("mn_hist", "Historique", "historique"),
                ("mn_new", "Nouvelle analyse", None),
                ("mn_stats", "Stats", "stats"), ("mn_premium", "Premium", "premium")]
        for col, (key, label, target) in zip(cols, tabs):
            with col:
                is_active = target is not None and active == target
                if st.button(label, key=key, use_container_width=True,
                             type="primary" if is_active else "secondary"):
                    if target is None:
                        _go("analyse", new_analysis=True)
                    else:
                        _go(target)