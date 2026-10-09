import streamlit as st
import time
import shutil
import json
import re
import os
import random
import secrets
import base64
import hashlib
import html as _html
import pandas as pd
from collections import Counter
import streamlit.components.v1 as _components
from datetime import datetime, timedelta
from pathlib import Path
from streamlit_cookies_controller import CookieController
from src.transcript_extractor import extract_video_id, get_transcript
from src.text_processor import chunk_text, remove_repetitions, polish_translation, extract_action_points
from src.summarizer import VideoSummarizer, MODELS
from src.translator import translate_notes, translate_texts
from src.keywords_extractor import extract_keywords as _origKeywords
from src.qa_generator import generate_questions as _origQuestions
from src.export_utils import (export_to_markdown, export_to_pdf, export_to_obsidian, export_to_notion)
from src.user_manager import (register_user, authenticate, ensure_admin, list_users,
delete_user, set_active, reset_password, set_plan, get_plan, get_tier, ADMIN_USER, ADMIN_PASS)
from src.history_manager import save_analysis, get_history, clear_history, count_today, trim_history
from src.session_manager import create_session, get_session_user, delete_session
from src.payment import create_payment, check_payment
from src.contact_manager import save_message, get_messages, mark_read, delete_message
from src.notification_manager import notify, get_notifications, unread_count, mark_all_read
from src.revenue_manager import record_revenue, get_revenues
from src.email_manager import (send_verification_code, send_contact_message, send_contact_ack)
from src.theme import apply_theme

# ═══════════════ i18n (4 langues) ═══════════════
# ⚠️ Extrait dans src/ui/i18n.py pour alléger app.py
from src.ui.i18n import LANGS, I18N, T
from pathlib import Path
# ═══════════════ ICÔNES SVG ═══════════════
# ⚠️ Extrait dans src/ui/components.py
from src.ui.components import ic, STARS, logo_html, LOGO_FILE, _ICONS, _STAR, get_logo_b64
# ═══════════════ CSS — BASE + APP ═══════════════
# ⚠️ Extrait dans src/ui/css.py
from src.ui.css import BASE_CSS, APP_CSS, custom_css, shade
st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(APP_CSS, unsafe_allow_html=True)
# ═══════════════ CORRECTIONS QUALITÉ ═══════════════
# ⚠️ Extrait dans src/ui/utils.py
from src.ui.utils import (
    _tokenize, clean_summary, better_extract_keywords,
    better_generate_questions, answer_question, _short,
    build_quiz, better_extract_action_points,
    _BAD_KW, _STOP, _FILLER_RE,
)
# ═══════════════ PRÉFÉRENCES D'APPARENCE ═══════════════
# ⚠️ Extrait dans src/ui/prefs.py
from src.ui.prefs import (
    _prefs_file, _load_prefs, get_prefs, set_pref,
    _save_appearance, _load_appearance, set_language,
)
# ═══════════════ STORAGE (favoris, partages, exports) ═══════════════
# ⚠️ Extrait dans src/ui/storage.py
from src.ui.storage import (
    get_referral_code, load_favs, toggle_fav,
    load_shares, save_share, export_anki, generate_audio,
)
# ═══════════════ CONFIG ═══════════════
# ⚠️ Extrait dans src/core/config.py
from src.core.config import (
    FREE_DAILY_LIMIT, COOKIE_NAME, PAYMENT_WAVE, PAYMENT_OM, CONTACT_EMAIL,
    CINETPAY_APIKEY, CINETPAY_SITE_ID, DEMO_VIDEO_URL,
    MAP_EMBED, MAP_LINK, AVATAR_DIR, PLANS, TIER_CHIP, HIST_KEEP,
)
# ═══════════════ PAGES AUTH ═══════════════
from src.pages.auth import (
    render_login, render_register_wizard, render_register_page,
)



# ═══════════════ LAYOUT ═══════════════
from src.ui.layout import (
    get_accent, hero, render_footer, render_navbar,
    notify_admins, sync_notif_cursor, notif_feedback, _toggle_theme,
)

# ═══════════════ PAGES PUBLIQUES ═══════════════
from src.pages.public import (
    render_home, render_about, render_privacy,
    render_contact, render_landing,
)




# ═══ Créer les dossiers nécessaires (cloud) ═══
for folder in ["data", "cache", "exports", "output", "data/avatars"]:
    Path(folder).mkdir(parents=True, exist_ok=True)
    


# ═══════════════ TEASER ═══════════════
TEASER_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VideoScribe AI — Teaser</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',system-ui,sans-serif; }
html,body { height:100%; background:#04101f; overflow:hidden; }
.stage { position:relative; width:100%; height:100%;
background:radial-gradient(1200px 600px at 50% -10%, #1B3B6F, #0B1F3A 60%, #04101f); overflow:hidden; }
.bars { position:absolute; top:12px; left:5%; right:5%; display:flex; gap:6px; z-index:50; }
.bars i { flex:1; height:4px; background:rgba(255,255,255,.25); border-radius:4px; overflow:hidden; }
.bars i b { display:block; height:100%; width:0; background:#fff; }
.brand { position:absolute; top:26px; left:5%; display:flex; gap:10px; align-items:center; z-index:50;
color:#fff; font-weight:700; font-size:clamp(14px,2.2vmin,22px); }
.brand .logo { width:clamp(30px,4.5vmin,46px); height:clamp(30px,4.5vmin,46px); border-radius:50%;
background:linear-gradient(135deg,#2E6DB4,#F5C542); display:flex; align-items:center; justify-content:center;
font-size:clamp(16px,2.4vmin,26px); }
.slide { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; align-items:center;
text-align:center; padding:0 6%; opacity:0; transform:scale(1.04); transition:opacity .5s, transform .5s; }
.slide.on { opacity:1; transform:scale(1); }
.tag { background:#F5C542; color:#0B1F3A; font-weight:800; padding:.4em .9em; border-radius:.4em;
font-size:clamp(16px,3vmin,30px); margin-bottom:.6em; }
h1 { color:#fff; font-size:clamp(30px, 7.5vmin, 92px); line-height:1.1; font-weight:800; max-width:20em; }
h1 em { font-style:normal; color:#F5C542; }
.sub { color:rgba(255,255,255,.85); font-size:clamp(15px, 3vmin, 30px); margin-top:.7em; max-width:30em; }
.phone { margin-top:clamp(16px,4vmin,40px); width:min(430px, 70%); background:#fff; border-radius:26px;
padding:clamp(12px,2vmin,20px); box-shadow:0 20px 60px rgba(0,0,0,.55); }
.phone .p-head { display:flex; align-items:center; gap:8px; font-weight:700; color:#0B1F3A;
font-size:clamp(12px,1.8vmin,17px); margin-bottom:10px; }
.phone .p-head .dot { width:clamp(22px,3vmin,32px); height:clamp(22px,3vmin,32px); border-radius:50%;
background:linear-gradient(135deg,#2E6DB4,#F5C542); }
.card { background:#F1F5FB; border-left:4px solid #2E6DB4; border-radius:10px; padding:9px 10px; margin:8px 0;
color:#22314e; font-size:clamp(11px,1.7vmin,15px); line-height:1.4; text-align:left; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; justify-content:center; }
.chips span { background:#E3ECF9; color:#1B3B6F; font-weight:700; font-size:clamp(10px,1.5vmin,13px);
padding:4px 9px; border-radius:20px; }
.end .big-logo { width:clamp(70px,12vmin,120px); height:clamp(70px,12vmin,120px); border-radius:26px;
background:linear-gradient(135deg,#2E6DB4,#F5C542); display:flex; align-items:center; justify-content:center;
font-size:clamp(36px,6vmin,60px); margin-bottom:20px; }
</style>
</head>
<body>
<div class="stage">
<div class="bars" id="bars"></div>
<div class="brand"><span class="logo">&#9999;</span> VideoScribe AI</div>
<div class="slide"><span class="tag">NOUVEAU</span><h1>VideoScribe <em>AI</em></h1></div>
<div class="slide"><h1>Transformez vos vidéos YouTube en <em>notes structurées</em></h1>
<div class="phone">
<div class="p-head"><span class="dot"></span> Résumé — Vidéo IA</div>
<div class="card">1. L'IA extrait les sous-titres et résume chaque section…</div>
<div class="card">2. Traduction automatique dans votre langue…</div>
<div class="chips"><span>IA</span><span>FR / EN / ES</span><span>PDF</span></div>
</div>
</div>
<div class="slide"><h1>Des résumés en <em>~60 secondes</em></h1><div class="sub">Fini les heures de visionnage.</div></div>
<div class="slide"><h1>Mots-clés, questions & flashcards <em>automatiques</em></h1>
<div class="phone">
<div class="p-head"><span class="dot"></span> Révision</div>
<div class="chips"><span>#IA</span><span>#vidéo</span><span>#résumé</span><span>#flashcard</span></div>
<div class="card">Q : Quels sont les points principaux à retenir ?</div>
</div>
</div>
<div class="slide"><h1>Interrogez la vidéo avec l'<em>IA</em></h1><div class="sub">Une question → une réponse ancrée sur le résumé.</div></div>
<div class="slide"><h1>Export <em>PDF, Notion, Obsidian, Anki</em></h1><div class="sub">Vos notes, partout, en un clic.</div></div>
<div class="slide"><h1>Essayez VideoScribe AI <em>gratuitement</em> pendant un mois.</h1></div>
<div class="slide end"><div class="big-logo">&#9999;</div><h1>VideoScribe AI</h1><div class="sub">Mbtech-services</div></div>
</div>
<script>
var slides = document.querySelectorAll('.slide');
var bars = document.getElementById('bars');
var DUR = 3800;
slides.forEach(function(){ var i=document.createElement('i'); i.innerHTML='<b></b>'; bars.appendChild(i); });
var segs = bars.querySelectorAll('b');
var idx = 0;
function show(n){
slides.forEach(function(s,k){ s.classList.toggle('on', k===n); });
segs.forEach(function(b,k){ b.style.transition='none'; b.style.width = (k<n? '100%':'0'); });
var cur = segs[n];
requestAnimationFrame(function(){ cur.style.transition='width '+DUR+'ms linear'; cur.style.width='100%'; });
}
show(0);
setInterval(function(){ idx = (idx+1) % slides.length; show(idx); }, DUR);
</script>
</body>
</html>"""
Path("teaser.html").write_text(TEASER_HTML, encoding="utf-8")



@st.cache_resource
def get_summarizer(model_key): return VideoSummarizer(MODELS[model_key], model_key=model_key)

def get_avatar_b64(uname):
    for ext in ("png","jpg","jpeg","webp"):
        p = AVATAR_DIR / f"{uname}.{ext}"
        if p.exists():
            mime = "image/jpeg" if ext == "jpg" else f"image/{ext}"
            return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return None

st.set_page_config(page_title="VideoScribe AI", layout="wide",
page_icon=str(LOGO_FILE) if LOGO_FILE.exists() else "🖊️")
ensure_admin()

# ⚠️ cookie_mgr, set_cookie, delete_cookie, read_cookie extraits dans src/core/cookies.py
from src.core.cookies import cookie_mgr, set_cookie, delete_cookie, read_cookie


# ═══ Détection du thème par défaut (cookie ou light) ═══
_theme_default = "light"
try:
    _t = st.context.cookies.get("ys_theme")
    if _t in ("dark","light"): _theme_default = _t
except Exception: pass

for key, default in {"user": None, "role": None, "theme": _theme_default, "result": None, "results_batch": [],
"token": None, "page": "accueil", "cfg_section": "general", "last_query_page": None,
"show_privacy": False, "buy_plan": None, "last_notif_id": 0, "cfg_lang": "fr",
"nl_hide": False, "nl_src_idx": 0,
"reg_step": 1, "reg_code_sent": False, "reg_email_verified": False,
"reg_msg": None, "last_qa": None, "quiz_score": None, "batch_urls": "", "share_link": None,
"cfg_translate": True, "cfg_kw": True, "cfg_qa": True,
"cfg_model": "rapide", "cfg_turbo": True,
"cfg_kw_n": 7, "cfg_q_n": 5, "cfg_chunk": 2800, "cfg_target": "fr",
"cfg_font": "Manrope", "cfg_reduce_motion": False,
"cfg_accent": "#2E6DB4", "cfg_font_size": 16, "cfg_line_height": 1.6,
"cfg_voice_lang": "fr", "cfg_voice_style": "Normal", "cfg_voice_speed": "Normal",
"cfg_notif_complete": True, "cfg_notif_weekly": True,
"prof_fullname": "", "prof_callname": "", "prof_job": "", "prof_instructions": ""}.items():
    if key not in st.session_state: st.session_state[key] = default

apply_theme(st.session_state.theme)


# ═══════════════ CSS DYNAMIQUE — Thème sombre FORCÉ ═══════════════
_theme_now = st.session_state.get("theme", "light")
if _theme_now == "dark":
    st.markdown("""
    <style>
    /* ═══ FOND NOIR PROFOND — Mode sombre ═══ */
    html, body, .stApp,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stMain"],
    section.main,
    section.main > div.block-container,
    div[data-testid="stMainBlockContainer"] {
        background-color: #05080F !important;
        color: #F8FAFC !important;
    }
    /* Sidebar */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background-color: #0A1019 !important;
    }
    /* Header */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }
    /* Navbar glassmorphism dark */
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) {
        background: rgba(10,16,25,.85) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border-bottom: 1px solid rgba(255,255,255,.08) !important;
        box-shadow: 0 4px 24px rgba(0,0,0,.4) !important;
    }
    /* Textes */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #F8FAFC !important;
    }
    .g-lead, .vs-about-lead, .g-step p, .g-kicker {
        color: rgba(203,213,225,.85) !important;
    }
    /* Navbar name */
    .lnav-brand-name { color: #F8FAFC !important; }
    /* Navbar links */
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) p,
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) span {
        color: rgba(203,213,225,.9) !important;
    }
    /* Formulaires */
    [data-testid="stForm"] {
        background: rgba(255,255,255,.03) !important;
        border-color: rgba(255,255,255,.10) !important;
    }
    /* Inputs */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] > div > div {
        background: #0F1A2E !important;
        color: #F8FAFC !important;
        border-color: rgba(255,255,255,.15) !important;
    }
    /* Wizard */
    .wizard-card, .wizard-card * { color: #F8FAFC !important; }
    .wstep {
        background: rgba(255,255,255,.08) !important;
        color: rgba(203,213,225,.9) !important;
        border-color: rgba(255,255,255,.2) !important;
    }
    .wline { background: rgba(255,255,255,.15) !important; }
    /* Cartes claires → sombres */
    .vs-feat, .vs-testi, .vs-value, .vs-team, .vs-insight, .vs-section-card {
        background: rgba(255,255,255,.04) !important;
        border-color: rgba(255,255,255,.10) !important;
    }
    .vs-feat-title, .vs-value h4, .vs-team h4, .vs-insight b, .vs-section-text, .vs-testi-quote {
        color: #F8FAFC !important;
    }
    .vs-feat-desc, .vs-value p, .vs-team p, .vs-insight span, .vs-testi-author small {
        color: rgba(203,213,225,.85) !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════ CSS DYNAMIQUE (thème + accent) ═══════════════
_nav = "#0F1A2E" if st.session_state.theme == "light" else "#F5F7FB"
_soft = "#4A5A7A" if st.session_state.theme == "light" else "#B9C6E2"
_menu_bg = "#ffffff" if st.session_state.theme == "light" else "#20242e"
_input_bg = "#ffffff" if st.session_state.theme == "light" else "#262b36"
_surface = "#ffffff" if st.session_state.theme == "light" else "#0E1626"
_hair = "rgba(15,26,46,.10)" if st.session_state.theme == "light" else "rgba(255,255,255,.10)"
_gold = "#C89B3C"
_chip_bg = "#ffffff" if st.session_state.theme == "light" else "#1E2126"
_font = st.session_state.cfg_font
if _font == "Sora": _fam = "'Sora', sans-serif"
elif _font == "Système": _fam = "system-ui, -apple-system, 'Segoe UI', sans-serif"
elif _font == "Adapté aux dyslexiques": _fam = "Verdana, 'Atkinson Hyperlegible', sans-serif"
else: _fam = "'Manrope', sans-serif"
_motion_css = ("*,*::before,*::after{animation:none!important;transition:none!important;}" if st.session_state.cfg_reduce_motion else "")

st.markdown(f"""
<style>
html body .stApp {{ font-family: {_fam} !important; }}
{_motion_css}
html body .stApp section[data-testid="stSidebar"] button, html body .stApp section[data-testid="stSidebar"] button div,
html body .stApp section[data-testid="stSidebar"] button p, html body .stApp section[data-testid="stSidebar"] button span {{ color: {_nav} !important; }}
html body .stApp section[data-testid="stSidebar"] .vs-ic {{ color: {_nav} !important; }}
html body .stApp .lnav-brand {{ color: {_nav} !important; }}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) {{ position: sticky; top: 2.7rem; z-index: 999;
background: {_menu_bg}E6; backdrop-filter: blur(14px); box-shadow: 0 8px 28px rgba(0,0,0,.10);
border-radius: 0 0 18px 18px; padding: .55rem .6rem; margin: 0 0 .8rem 0; }}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) {{
background: transparent !important; box-shadow: none !important; border: none !important;
border-radius: 999px !important; font-weight: 700 !important; }}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) p,
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) span {{ color: {_nav} !important; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button {{
background: transparent !important; box-shadow: none !important; border: none !important;
justify-content: flex-start !important; text-align: left !important; border-radius: 999px !important;
padding: .85rem 1.3rem !important; font-size: 1.08rem !important; font-weight: 700 !important; min-height: 0 !important; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button p,
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button span {{ color: {_nav} !important; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) [data-testid="stBaseButton-primary"] {{ background: rgba(46,109,180,.16) !important; border: 1px solid rgba(46,109,180,.55) !important; }}
html body .stApp .g-kicker {{ color: {_gold} !important; }}
html body .stApp .g-h1, html body .stApp .g-h2 {{ color: {_nav} !important; }}
html body .stApp .g-lead {{ color: {_soft} !important; }}
html body .stApp .g-card {{ background: {_surface}; border: 1px solid {_hair}; }}
html body .stApp .g-card h4 {{ color: {_nav} !important; }}
html body .stApp .g-card p {{ color: {_soft} !important; }}
html body .stApp .g-ico {{ background: {_nav}; color: {_gold} !important; }}
html body .stApp .g-stat b {{ color: {_nav} !important; }}
html body .stApp .g-stat span {{ color: {_soft} !important; }}
html body .stApp .g-step h4 {{ color: {_nav} !important; }}
html body .stApp .g-step p {{ color: {_soft} !important; }}
html body .stApp .g-cta h3 {{ color: #fff !important; }}
html body .stApp .g-cta p {{ color: rgba(255,255,255,.85) !important; }}
html body .stApp div.footer-dark, html body .stApp div.footer-dark p, html body .stApp div.footer-dark li {{ color: #cbd5e1 !important; }}
html body .stApp div.footer-dark h5, html body .stApp div.footer-dark .fd-logo {{ color: #fff !important; }}
html body .stApp .pay-panel, html body .stApp .pay-panel div, html body .stApp .pay-panel li,
html body .stApp .pay-panel b, html body .stApp .pay-panel code {{ color: {_nav} !important; }}
html body .stApp .pc-name, html body .stApp .pc-price {{ color: {_nav} !important; }}
html body .stApp .pc-tag, html body .stApp .pc-sub {{ color: {_soft} !important; }}
html body .stApp .pc-plus {{ color: {_nav} !important; }}
html body .stApp .pfeat {{ color: {_nav} !important; }}
html body .stApp .pc-badge {{ color: {_nav} !important; }}
html body .stApp .claude-hello .big {{ color: {_nav} !important; }}
html body .stApp .claude-sub {{ color: {_soft} !important; }}
html body .stApp .claude-chip {{ color: {_nav} !important; }}
html body .stApp .qbrand {{ color: {_nav} !important; }}
html body .stApp .qcap {{ color: {_nav} !important; }}
html body .stApp .uname {{ color: {_nav} !important; }}
html body .stApp .tier-chip {{ color: {_nav} !important; }}
html body .stApp [data-testid="stTextInput"] input, html body .stApp [data-testid="stTextArea"] textarea,
html body .stApp [data-testid="stNumberInput"] input {{ background: {_input_bg} !important; color: {_nav} !important; border: 1.5px solid rgba(128,128,128,.35) !important; }}
html body .stApp label {{ color: {_nav} !important; }}
html body .stApp [data-testid="stMarkdown"] p {{ color: {_nav} !important; }}
html body .stApp .kpi-value {{ color: {_nav} !important; }}
html body .stApp .kpi-label {{ color: {_soft} !important; }}
html body .stApp .res-head, html body .stApp .note-card, html body .stApp .q-item, html body .stApp .newfeat,
html body .stApp .notif-card, html body .stApp .hist-card {{ color: {_nav} !important; }}
html body .stApp .pipe-lbl, html body .stApp .pipe-title {{ color: {_nav} !important; }}
html body .stApp h2.nl-title, html body .stApp .nl-hero .nl-title {{ color: #E8EAED !important; }}
html body .stApp .nl-hero .nl-x {{ color: #9AA0A6 !important; }}
html body .stApp div[data-testid="stVerticalBlock"]:has(.nl-zone) [data-testid="stTextInput"] input {{ background: {_input_bg} !important; color: {_nav} !important; }}
html body .stApp div[data-testid="stVerticalBlock"]:has(.nl-zone) .stButton > button {{ background: {_chip_bg} !important; color: {_nav} !important; }}
html body .stApp div[data-testid="stColumn"]:has(.nl-gowrap) .stButton > button {{ background: {_chip_bg} !important; color: {_nav} !important; }}
@media (max-width: 768px) {{
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) {{
display: flex; flex-direction: row; flex-wrap: wrap; gap: .4rem; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) > div[data-testid="stElementContainer"] {{
flex: 1 1 46%; margin: 0 !important; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) > div[data-testid="stElementContainer"]:has(.setnav) {{ display: none; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .qcap {{ flex-basis: 100%; margin: .5rem 0 .1rem; }}
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button {{
padding: .55rem .5rem !important; font-size: .85rem !important; justify-content: center !important; text-align: center !important; }}
}}

</style>
""", unsafe_allow_html=True)

st.markdown(custom_css(), unsafe_allow_html=True)

if st.session_state.user is None:
    st.markdown('<style>section[data-testid="stSidebar"]{display:none !important;}</style>', unsafe_allow_html=True)


# ⚠️ def render_home(): extrait dans src/pages/public.py
# ⚠️ def render_about(): extrait dans src/pages/public.py
# ⚠️ def render_privacy(show_back=True): extrait dans src/pages/public.py
# ⚠️ def render_contact(): extrait dans src/pages/public.py
def render_notifs():
    _acc, _acc_dark = get_accent()
    hero("bell", T("notifs_title"), T("notifs_sub"))
    notifs = get_notifications(user)
    n_unread = unread_count(user)
    s1, s2, s3 = st.columns(3)
    s1.metric("Total", len(notifs)); s2.metric("Non lues", n_unread); s3.metric("Lues", len(notifs)-n_unread)
    if st.button(T("mark_all"), use_container_width=True): mark_all_read(user); st.rerun()
    if not notifs:
        st.markdown(f"<div class='notif-card'><span class='notif-ico'>{ic('bell', 18)}</span><div><b>{T('no_notif')}</b><br><small>—</small></div></div>", unsafe_allow_html=True)
        render_footer(compact=True)
        return
    for n in notifs:
        style = "" if n["read"] else "border-left:4px solid #D4AF37;"
        st.markdown(f"<div class='notif-card' style='{style}'><span class='notif-ico'>{ic('bell', 18)}</span><div><b>{n['text']}</b><br><small>{ic('clock', 12)} {n['date']}</small></div></div>", unsafe_allow_html=True)
    render_footer(compact=True)
def render_premium():
    # On n'affiche la navbar QUE si l'utilisateur n'est PAS connecté
    if st.session_state.get("user") is None:
        render_navbar()
        
    # ═══ Sécurisation : variables globales non définies en mode public ═══
    _prem_user = st.session_state.get("user")
    
    # ═══ Sécurisation : variables globales non définies en mode public ═══
    _prem_user = st.session_state.get("user")
    _prem_role = st.session_state.get("role", "client")
    _prem_is_guest = _prem_user is None
    
    if _prem_role == "admin":
        cur = "premium_plus"
    elif _prem_is_guest:
        cur = "free"
    else:
        cur = get_plan(_prem_user)
    
    cur_label = T("plan_free") if cur == "free" else PLANS[cur]["name"]
    st.markdown(f"""<div style="text-align:center; margin:2.2rem 0 .4rem;">
<div class="g-kicker" style="justify-content:center; display:flex; align-items:center; gap:8px;">{ic("spark",12)} {T("prem_kicker")}</div>
<h1 style="margin:.5rem 0 .3rem;">{T("prem_title")}</h1>
<p style="opacity:.7; max-width:52ch; margin:0 auto;">{T("prem_subtitle")}</p>
</div>""", unsafe_allow_html=True)
    t1, t2, t3 = st.columns([2,2,2])
    with t2: billing = st.radio("billing", [T("monthly"),T("annual")], horizontal=True, label_visibility="collapsed")
    is_annual = billing == T("annual")
    st.markdown(f'<p style="text-align:center; opacity:.65; margin-top:-8px;">{ic("trending-down",13)} {T("save_annual")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; opacity:.8;">{T("status")} : <b>{cur_label}</b></p>', unsafe_allow_html=True)
    st.markdown(f"""<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:.8rem 0 1.6rem;">
<span class="pill-trust">{ic("lock",13)} {T("trust_secure")}</span>
<span class="pill-trust">{ic("x",13)} {T("trust_cancel")}</span>
<span class="pill-trust">{ic("zap",13)} {T("trust_fast")}</span>
</div>""", unsafe_allow_html=True)
    if st.session_state.get("buy_plan"):
        key = st.session_state.buy_plan
        billing_sel = st.session_state.get("buy_billing", T("monthly"))
        _components.html('<script>window.parent.scrollTo({top:0,behavior:"smooth"});</script>', height=0)
        if key == "free":
            st.info(f"{T('free')} ✓")
            if st.button(T("close"), use_container_width=True):
                st.session_state.buy_plan = None; st.rerun()
        else:
            info = PLANS[key]; price = info["annual"] if billing_sel==T("annual") else info["monthly"]; days = 365 if billing_sel==T("annual") else 30
            _prem_display_name = _prem_user if _prem_user else "visiteur"
            st.markdown(f"""
<div class="pay-panel">
<div class="pay-title">{ic("card",20)} {T("subscription")} — {info['name']}</div>
<div class="pay-price">${price:g} <span>/ {days} jours</span></div>
<ol class="pay-steps">
<li>Envoyez <b>${price:g}</b> par <b>Wave</b> (<code>{PAYMENT_WAVE}</code>) ou <b>Orange Money</b> (<code>{PAYMENT_OM}</code>)</li>
<li>Indiquez votre pseudo <b>{_prem_display_name}</b> + la formule <b>{info['name']}</b></li>
<li>Activation sous 24 h ({days} jours)</li>
</ol>
</div>""", unsafe_allow_html=True)
            if _prem_is_guest:
                st.info(T("login_sub"))
            elif CINETPAY_APIKEY and CINETPAY_SITE_ID:
                if st.session_state.get("pay_url"):
                    st.link_button("Ouvrir la page de paiement", st.session_state.pay_url, use_container_width=True)
                    if st.button(T("verify"), use_container_width=True):
                        with st.spinner("..."): status = check_payment(st.session_state.pay_tx, CINETPAY_APIKEY, CINETPAY_SITE_ID)
                        if status == "ACCEPTED":
                            set_plan(_prem_user, key, days); record_revenue(_prem_user, key, price, days, "cinetpay")
                            notify(_prem_user, "card", f"Paiement de **${price:g}** confirmé — formule {info['name']} activée ({days} j).")
                            sync_notif_cursor(_prem_user)
                            st.session_state.pay_url = None; st.session_state.buy_plan = None; st.balloons(); st.rerun()
                        else: st.info(f"Paiement non confirmé ({status}).")
                else:
                    if st.button(f"Générer le paiement de ${price:g}", use_container_width=True):
                        with st.spinner("..."):
                            try:
                                tx, url = create_payment(_prem_user, price, CINETPAY_APIKEY, CINETPAY_SITE_ID)
                                st.session_state.pay_tx, st.session_state.pay_url = tx, url; st.rerun()
                            except Exception as e: st.error(f"{e}")
            bb1, bb2 = st.columns([3,1])
            with bb2:
                if st.button(T("close"), use_container_width=True):
                    st.session_state.buy_plan = None; st.session_state.pay_url = None; st.rerun()
        st.markdown("---")
    plans_ui = [
    {"key":"free","icon":"spark","name":T("plan_free"),"tag":T("tag_free"),"monthly":0,"annual":0,"cta":T("get_free"),"hl":False,"plus":None,
     "accent":"#64748B","accent2":"#94A3B8",
     "features":[T("ff1"),T("ff2"),T("ff3"),T("ff4"),T("ff5")],"new_features":[T("ff6"),T("ff7")]},
    {"key":"basique","icon":"zap","name":T("plan_basic"),"tag":T("tag_basic"),"monthly":1.99,"annual":19,"cta":T("get_bas"),"hl":False,"plus":T("plan_free"),"plus_key":"plus_free",
     "accent":"#2E6DB4","accent2":"#4C9AFF",
     "features":[T("fb1"),T("fb2"),T("fb3"),T("fb4"),T("fb5"),T("fb6")],"new_features":[T("fb7"),T("fb8"),T("fb9")]},
    {"key":"premium","icon":"star","name":T("plan_premium"),"tag":T("tag_premium"),"monthly":4.99,"annual":49,"cta":T("get_prem"),"hl":True,"plus":T("plan_basic"),"plus_key":"plus_basic",
     "accent":"#D4AF37","accent2":"#F0D488",
     "features":[T("fp1"),T("fp2"),T("fp3"),T("fp4"),T("fp5"),T("fp6")],"new_features":[T("fp7"),T("fp8"),T("fp9"),T("fp10"),T("fp11")]},
    {"key":"premium_plus","icon":"crown","name":T("plan_plus"),"tag":T("tag_plus"),"monthly":9.99,"annual":99,"cta":T("get_plus"),"hl":False,"plus":T("plan_premium"),"plus_key":"plus_premium",
     "accent":"#8B5CF6","accent2":"#C4B5FD",
     "features":[T("fx1"),T("fx2"),T("fx3"),T("fx4"),T("fx5"),T("fx6"),T("fx7"),T("fx8")],"new_features":[T("fx9"),T("fx10"),T("fx11"),T("fx12"),T("fx13")]},
    ]
    cols = st.columns(4, gap="medium")
    for col, p in zip(cols, plans_ui):
        with col:
            price = p["annual"] if is_annual else p["monthly"]
            sub = T("billed_annually") if is_annual else T("per_month")
            card_cls = "pcard pcard-hl" if p["hl"] else "pcard"
            ribbon = f'<div class="pc-ribbon">{ic("star",12)} {T("popular")}</div>' if p["hl"] else ""
            price_html = f'<span class="cur">$</span>{price:g}' if price > 0 else "0"
            st.markdown(f"""<div class="{card_cls}">{ribbon}<div class="pc-icon-wrap" style="--pc-accent:{p['accent']};--pc-accent2:{p['accent2']};">{ic(p["icon"], 24)}</div><p class="pc-name">{p["name"]}</p><p class="pc-tag">{p["tag"]}</p><p class="pc-price">{price_html}</p><p class="pc-sub">{sub}</p></div>""", unsafe_allow_html=True)
            if st.button(p["cta"], key=f"cta_{p['key']}", use_container_width=True, type="primary" if p["hl"] else "secondary"): st.session_state.buy_plan = p["key"]; st.session_state.buy_billing = billing; st.rerun()
            st.markdown('<div class="pc-sep"></div>', unsafe_allow_html=True)
            head = (f'<p class="pc-plus">{T(p["plus_key"])}</p>' if p.get("plus_key") else f'<p class="pc-plus">{T("included")}</p>')
            feats = "".join(f'<p class="pfeat" style="--pc-accent:{p["accent"]}">{ic("check", 14)}<span>{f}</span></p>' for f in p["features"])
            new_feats = ""
            if p.get("new_features"):
                new_feats = f'<p class="pfeat-group-label">{ic("spark",11)} {T("new_label")}</p>' + "".join(f'<p class="pfeat is-new" style="--pc-accent:{p["accent"]}">{ic("check", 14)}<span>{f}<span class="new-tag">{T("new_label")}</span></span></p>' for f in p["new_features"])
            st.markdown(head + feats + new_feats, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('trophy', 22)} {T('growth_title')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div class="newfeat">{ic("users", 18)} <span><b>{T("referral_title")}</b> · Tous</span></div>
<div class="newfeat">{ic("folder", 18)} <span><b>{T("fb4")}</b> · Basique+</span></div>
<div class="newfeat">{ic("zap", 18)} <span><b>{T("fx2")}</b> · Premium+</span></div>""", unsafe_allow_html=True)
    st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('gem', 22)} {T('comfort_title')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div class="newfeat">{ic("award", 18)} <span><b>{T("fp4")}</b> · Premium</span></div>
<div class="newfeat">{ic("play", 18)} <span><b>{T("fx3")}</b> · Premium+</span></div>
<div class="newfeat">{ic("volume", 18)} <span><b>{T("fx4")}</b> · Premium+</span></div>
<div class="newfeat">{ic("card", 18)} <span><b>{T("fp5")}</b> · Premium</span></div>
<div class="newfeat">{ic("link", 18)} <span><b>{T("fb5")}</b> · Basique+</span></div>
<div class="newfeat">{ic("image", 18)} <span><b>{T("fx8")}</b> · Premium+</span></div>""", unsafe_allow_html=True)
    st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('trending-up', 22)} {T('prem_kicker')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div class="newfeat">{ic("trending-up", 18)} <span><b>{T("fp7")}</b> · Premium</span></div>
<div class="newfeat">{ic("target", 18)} <span><b>{T("fp9")}</b> · Premium</span></div>
<div class="newfeat">{ic("calendar", 18)} <span><b>{T("fx10")}</b> · Premium+</span></div>
<div class="newfeat">{ic("compass", 18)} <span><b>{T("fx12")}</b> · Premium+</span></div>""", unsafe_allow_html=True)
    if not _prem_is_guest:
        st.markdown("---")
        st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('users', 22)} {T('referral_title')}</h3>", unsafe_allow_html=True)
        code = get_referral_code(_prem_user)
        st.markdown(f"<div class='newfeat'>{ic('key', 18)} <span>{T('referral_share')} <b>{code}</b> {T('referral_each')}</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    render_footer(compact=True)

def render_profil():
    _acc, _acc_dark = get_accent()
    info = list_users().get(user, {})
    cur = "premium_plus" if role == "admin" else get_plan(user)
    badges = ["Admin" if role == "admin" else "Client", PLANS[cur]["name"] if cur != "free" else T("plan_free")]
    if tier >= 3: badges.append(T("certified"))
    hero("user", f"@{user}", T("profile"), badges)
    _av = get_avatar_b64(user)
    if _av: st.markdown(f'<img src="{_av}" class="big-avatar">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T("role"), role); c2.metric(T("plan"), PLANS[cur]["name"] if cur != "free" else T("plan_free"))
    exp = info.get("premium_expires")
    c3.metric(T("expires"), datetime.fromisoformat(exp).strftime("%d/%m/%Y") if exp and cur != "free" else "—")
    c4.metric(T("m_analyse"), len(get_history(user)))
    st.markdown("---"); st.subheader(T("change_pwd"))
    with st.form("pwd_form"):
        cur_p = st.text_input(T("pwd_current"), type="password"); new = st.text_input(T("pwd_new"), type="password"); conf = st.text_input(T("pwd_confirm"), type="password")
        if st.form_submit_button(T("pwd_update"), use_container_width=True):
            ok, _ = authenticate(user, cur_p)
            if not ok: st.error("Mot de passe actuel incorrect.")
            elif new != conf: st.error("La confirmation ne correspond pas.")
            elif reset_password(user, new): notify_admins("key", f"**{user}** a changé son mot de passe."); st.success("Mot de passe mis à jour.")
            else: st.error("Nouveau mot de passe trop court.")
    st.markdown("---"); st.subheader(T("del_title"))
    st.caption(T("del_caption"))
    with st.form("delete_form"):
        confirm_del = st.checkbox(T("del_check"))
        if st.form_submit_button(T("del_btn"), use_container_width=True):
            if confirm_del:
                uname = user; notify_admins("trash", f"Compte **{uname}** supprimé (RGPD).")
                delete_user(uname); clear_history(uname)
                for p in AVATAR_DIR.glob(f"{uname}.*"): p.unlink()
                delete_session(st.session_state.get("token")); delete_cookie(COOKIE_NAME); delete_cookie("ys_user")
                st.session_state.update(user=None, role=None, result=None, token=None, page="accueil", show_privacy=False); st.rerun()
            else: st.error("Cochez la case de confirmation.")
    render_footer(compact=True)

def _parse_hdate(h):
    try: return datetime.strptime(h["date"], "%d/%m/%Y %H:%M")
    except Exception: return datetime.min

def _trend_html(cur_val, prev_val, unit=""):
    diff = cur_val - prev_val
    if prev_val <= 0:
        if diff > 0: return f'<div class="kpi-trend up">↑ +{diff:g}{unit} {T("tr_week")}</div>'
        if diff < 0: return f'<div class="kpi-trend down">↓ {abs(diff):g}{unit} {T("tr_week")}</div>'
        return f'<div class="kpi-trend up">✓ {T("tr_stable")}</div>'
    pct = diff / prev_val * 100
    if abs(pct) > 999:
        cls = "up" if diff >= 0 else "down"; arrow = "↑" if diff >= 0 else "↓"
        return f'<div class="kpi-trend {cls}">{arrow} {diff:+g}{unit} {T("tr_week")}</div>'
    cls = "up" if pct >= 0 else "down"; arrow = "↑" if pct >= 0 else "↓"
    return f'<div class="kpi-trend {cls}">{arrow} {abs(pct):.1f}% {T("tr_vs")}</div>'

def render_bar_chart_html(values, labels, height=280):
    vmax = max(values) if values else 0
    if vmax <= 0: vmax = 1
    bars = ""
    for v, l in zip(values, labels):
        h = max(int(v / vmax * (height - 60)), 4)
        bars += f'<div class="bc-col"><div class="bc-bar" style="height:{h}px" title="{l} : {v:g} s"></div><span class="bc-lbl">{l}</span></div>'
    st.markdown(f'<div class="bc-wrap" style="height:{height}px">{bars}</div>', unsafe_allow_html=True)

def render_stats():
    _acc, _acc_dark = get_accent()
    hero("chart", T("stats_title"), T("stats_sub"))
    hist = get_history(user)
    if not hist: st.caption("Aucune analyse."); render_footer(compact=True); return
    tt = sum(h.get("processing_time", 0) for h in hist)
    tw = sum(h.get("total_words", 0) for h in hist)
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_prev = datetime.now() - timedelta(days=14)
    this_week = [h for h in hist if _parse_hdate(h) >= week_ago]
    prev_week = [h for h in hist if week_ago_prev <= _parse_hdate(h) < week_ago]
    n_this, n_prev = len(this_week), len(prev_week)
    tt_this = sum(h.get("processing_time", 0) for h in this_week)
    tt_prev = sum(h.get("processing_time", 0) for h in prev_week)
    tw_this = sum(h.get("total_words", 0) for h in this_week)
    tw_prev = sum(h.get("total_words", 0) for h in prev_week)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("book", 24)}</div><div class="kpi-label">{T("videos")}</div><div class="kpi-value">{len(hist)}</div>{_trend_html(n_this, n_prev)}</div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("clock", 24)}</div><div class="kpi-label">{T("total_time")}</div><div class="kpi-value">{tt:.0f}s</div>{_trend_html(tt_this, tt_prev, "s")}</div>', unsafe_allow_html=True)
    with k3:
        avg_chunks = sum(h.get('num_chunks',0) for h in hist)/len(hist)
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("zap", 24)}</div><div class="kpi-label">{T("avg_chunks")}</div><div class="kpi-value">{avg_chunks:.1f}</div><div class="kpi-trend up">✓ {T("tr_opt")}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("hash", 24)}</div><div class="kpi-label">{T("words_proc")}</div><div class="kpi-value">{tw:,}</div>{_trend_html(tw_this, tw_prev)}</div>', unsafe_allow_html=True)
    times = [h.get("processing_time", 0) for h in hist]
    labels = [f"V{i+1}" for i in range(len(hist))]
    if tier >= 2:
        e1, e2, e3 = st.columns(3)
        e1.metric(T("fastest"), f"{min(times):.0f} s"); e2.metric(T("slowest"), f"{max(times):.0f} s"); e3.metric(T("avg_time"), f"{tt/len(hist):.0f} s")
        render_bar_chart_html(times, labels)
    else:
        render_bar_chart_html(times[::-1], labels[::-1])
        st.markdown(f"<div class='q-item'>{ic('lock', 14)} Rapport détaillé réservé aux Premium et +</div>", unsafe_allow_html=True)
    if tier >= 3:
        st.markdown("---"); st.subheader(f"{T('weekly')} {T('wk_d')}")
        r1, r2, r3 = st.columns(3)
        r1.metric(f"{T('m_analyse')} {T('wk_d')}", n_this); r2.metric(f"{T('words')} {T('wk_d')}", f"{tw_this:,}"); r3.metric(f"{T('time')} {T('wk_d')}", f"{tt_this:.0f} s")
        rep = (f"# {T('weekly')} — {user}\n- {T('m_analyse')} : **{n_this}**\n- {T('words')} : **{tw_this:,}**\n- {T('time')} : **{tt_this:.0f} s**\n## Vidéos\n" + "\n".join(f"- {h['date']} — https://youtu.be/{h['video_id']}" for h in this_week))
        st.download_button(T("dl_report"), rep.encode("utf-8"), file_name=f"rapport_{user}.md", mime="text/markdown", use_container_width=True)
    render_footer(compact=True)

def render_historique():
    _acc, _acc_dark = get_accent()
    hero("book", T("hist_title"), T("hist_sub"))
    hist = get_history(user); favs = load_favs(user)
    week_ago = datetime.now() - timedelta(days=7)
    recent = [h for h in hist if _parse_hdate(h) >= week_ago]
    s1, s2, s3 = st.columns(3)
    s1.metric(T("total"), len(hist)); s2.metric(T("this_week"), len(recent)); s3.metric(T("favs"), len(favs))
    f1, f2 = st.columns([3,1])
    with f1:
        q = ""
        if tier >= 2:
            q = st.text_input(T("search_ph"), placeholder="Rechercher…").lower()
        else:
            st.markdown(f"<div class='q-item'>{ic('lock', 14)} Recherche réservée aux Premium et +</div>", unsafe_allow_html=True)
    with f2:
        only_fav = st.checkbox("⭐ " + T("only_favs"))
    if tier == 0 and len(hist) > 10:
        st.caption(f"{T('plan_free')} : 10 ({len(hist)}).")
    shown = [h for h in hist
             if (not q or q in json.dumps(h, ensure_ascii=False).lower())
             and (not only_fav or h["video_id"] in favs)]
    if not shown:
        st.markdown(f"<div class='hist-card'><span class='hist-ico'>{ic('book', 18)}</span>"
                  f"<div class='hist-left'><div><b>Aucune analyse</b><br>"
                  f"<small>—</small></div></div></div>", unsafe_allow_html=True)
        render_footer(compact=True); return
    for h in shown:
        vid = h["video_id"]; is_fav = vid in favs
        st.markdown(f"""<div class="hist-card">
<span class="hist-ico">{ic("film", 18)}</span>
<div class="hist-left"><div>
<b>{_html.escape(h.get("title", "Résumé - " + vid))}</b><br>
<small>{h["date"]} • {h["lang"].upper()} • {h.get("total_words",0):,} {T("words")} • {h.get("processing_time",0)} s</small>
</div></div>
<div class="hist-fav">{"⭐" if is_fav else ""}</div>
</div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button(T("open_analyse"), key=f"open_{vid}_{h['date']}", use_container_width=True):
                st.session_state.result = h; st.session_state.page = "analyse"; st.rerun()
        with c2:
            if st.button(("⭐" if is_fav else "☆") + " " + T("add_fav"),
                         key=f"fav_{vid}_{h['date']}", use_container_width=True):
                toggle_fav(user, vid); st.rerun()
    st.markdown("---")
    if st.button(T("clear_hist"), use_container_width=True):
        clear_history(user); st.rerun()
    render_footer(compact=True)

def render_config():
    hero("sliders", T("set_title"), T("set_sub"))
    SECTIONS = [(T("set_title"),[("general",T("general"),"sliders"),("compte",T("account"),"user"),("confidentialite",T("privacy"),"shield"),("facturation",T("billing"),"card"),("capacites",T("caps"),"cpu")]),
    ("Desktop",[("bureau",T("general"),"monitor"),("extensions","Extensions","tool"),("developpeur","Dev","code")]),
    (T("personalization"),[("competences","Skills","spark"),("connecteurs","Connect","link"),("plugins","Plugins","tool"),("memoire","Memory","clock")])]
    query = st.text_input(T("set_search"), placeholder="...", label_visibility="collapsed")
    c_nav, c_body = st.columns([1, 3], gap="large")
    with c_nav:
        st.markdown('<div class="setnav"></div>', unsafe_allow_html=True)
        for group_name, grp in SECTIONS:
            st.markdown(f'<div class="qcap">{group_name}</div>', unsafe_allow_html=True)
            for key, label, icon in grp:
                if query and query.lower() not in label.lower(): continue
                if st.button(f"{label}", key=f"set_{key}", use_container_width=True, type="primary" if st.session_state.cfg_section == key else "secondary"): st.session_state.cfg_section = key; st.rerun()
    with c_body:
        st.markdown('<div class="setbody"></div>', unsafe_allow_html=True); sec = st.session_state.cfg_section
        if sec == "general":
            st.subheader(T("general"))
            a1, a2 = st.columns([2,1]); a1.markdown(f"**{T('appearance')}**", unsafe_allow_html=True)
            with a2:
                t1, t2 = st.columns(2)
                with t1:
                    if st.button(T("light"), use_container_width=True, type="primary" if st.session_state.theme=="light" else "secondary"): st.session_state.theme="light"; set_cookie("ys_theme","light",max_age=365*24*3600); st.rerun()
                with t2:
                    if st.button(T("dark"), use_container_width=True, type="primary" if st.session_state.theme=="dark" else "secondary"): st.session_state.theme="dark"; set_cookie("ys_theme","dark",max_age=365*24*3600); st.rerun()
            st.markdown("---")
            st.subheader(T("language"))
            cur_lang = st.session_state.cfg_lang
            cl = st.selectbox(T("language"), list(LANGS.keys()), index=list(LANGS.keys()).index(cur_lang) if cur_lang in LANGS else 0, format_func=lambda l: LANGS[l], key="sel_lang")
            if cl != cur_lang: set_language(cl)
            _ui = LANGS.get(st.session_state.cfg_lang,"fr"); _tgt = LANGS.get(st.session_state.cfg_target,"fr")
            st.info(f"🌐 **{_ui}** — {T('language')} ✓ | {T('chip_tr')} {T('m_analyse')} → **{_tgt}**")
            st.markdown("---"); b1, b2 = st.columns([2,1]); b1.markdown(f"**{T('font')}**", unsafe_allow_html=True)
            with b2: st.selectbox(T("font"), ["Manrope","Sora","Système","Adapté aux dyslexiques"], key="cfg_font", label_visibility="collapsed")
            st.markdown("---"); st.checkbox(f"**{T('motion')}**", key="cfg_reduce_motion")
            st.markdown("---"); st.subheader(T("personalization"))
            _presets = {"Bleu océan":"#2E6DB4","Teal":"#14B8A6","Violet":"#8B5CF6","Orange":"#F97316","Vert":"#22C55E",
            "Rouge":"#EF4444","Indigo":"#6366F1","Or":"#F59E0B","Rose":"#EC4899","Cyan":"#06B6D4"}
            _cur = st.session_state.get("cfg_accent","#2E6DB4")
            _vals = list(_presets.values()); _names = list(_presets.keys())
            _idx = _vals.index(_cur) if _cur in _vals else 0
            p1, p2 = st.columns(2)
            with p1:
                _sel = st.selectbox(T("presets"), _names, index=_idx)
                if _presets[_sel] != _cur:
                    st.session_state.cfg_accent = _presets[_sel]; _save_appearance(); st.rerun()
            with p2:
                _hex = st.color_picker(T("custom_color"), value=_cur)
                if _hex != _cur:
                    st.session_state.cfg_accent = _hex; _save_appearance(); st.rerun()
            s1, s2 = st.columns(2)
            with s1: st.slider(T("text_size"), 14, 20, int(st.session_state.get("cfg_font_size",16)), key="cfg_font_size", on_change=_save_appearance)
            with s2: st.slider(T("line_height"), 1.4, 2.0, float(st.session_state.get("cfg_line_height",1.6)), key="cfg_line_height", on_change=_save_appearance)
            st.markdown(f'<div class="note-card"><div class="note-num">A</div><div class="note-text">{T("preview")} — <b>{st.session_state.cfg_accent}</b> • {int(st.session_state.cfg_font_size)} px • {st.session_state.cfg_line_height}</div></div>', unsafe_allow_html=True)
            st.markdown("---"); st.subheader(T("voice"))
            v1, v2 = st.columns(2)
            with v1: st.selectbox(T("language"), ["fr","en","es","de"], key="cfg_voice_lang", format_func=lambda l: LANGS[l])
            with v2: st.selectbox(T("speed"), ["Lent","Normal","Rapide"], key="cfg_voice_speed")
            st.selectbox(T("style"), ["Normal","Décontracté","Professionnel"], key="cfg_voice_style")
            st.markdown("---"); st.subheader(T("notif_pref"))
            st.checkbox(f"**{T('completion')}**", key="cfg_notif_complete"); st.checkbox(f"**{T('weekly')}**", key="cfg_notif_weekly")
        elif sec == "compte":
            st.subheader(T("profile"))
            _av = get_avatar_b64(user)
            if _av: st.markdown(f'<img src="{_av}" class="big-avatar">', unsafe_allow_html=True)
            else: st.markdown(f'<div class="big-avatar">{user[:2].upper()}</div>', unsafe_allow_html=True)
            up = st.file_uploader("Avatar", type=["png","jpg","jpeg","webp"])
            if up:
                AVATAR_DIR.mkdir(parents=True, exist_ok=True); ext = up.name.rsplit(".",1)[-1].lower()
                for old in AVATAR_DIR.glob(f"{user}.*"): old.unlink()
                (AVATAR_DIR / f"{user}.{ext}").write_bytes(up.read()); st.success("Photo enregistrée"); st.rerun()
            st.text_input(T("fullname"), key="prof_fullname"); st.text_input(T("callname"), key="prof_callname")
            st.selectbox(T("job"), ["Étudiant","Enseignant","Créateur de contenu","Professionnel","Autre"], key="prof_job")
            st.text_area(T("instructions"), key="prof_instructions", placeholder="ex. : garder les explications brèves")
            st.markdown("---")
            if st.button(T("change_pwd"), use_container_width=True): st.session_state.page = "profil"; st.rerun()
        elif sec == "confidentialite":
            st.subheader(T("privacy")); st.write("RGPD ✓")
            if st.button(T("see_policy"), use_container_width=True): st.session_state.show_privacy = True; st.rerun()
        elif sec == "facturation":
            st.subheader(T("billing")); cur = "premium_plus" if role == "admin" else get_plan(user)
            st.write(f"{T('current_plan')} : **{PLANS[cur]['name'] if cur != 'free' else T('plan_free')}**")
            if st.button(T("manage_plan"), use_container_width=True): st.session_state.page = "premium"; st.rerun()
        elif sec == "capacites":
            st.subheader(T("caps"))
            if tier >= 2: st.selectbox(T("model"), ["rapide","qualite"], key="cfg_model", format_func=lambda m: "Rapide" if m=="rapide" else "Qualité")
            else: st.markdown(f"<div class='q-item'>{ic('lock',14)} Modèle Qualité réservé aux Premium et +</div>", unsafe_allow_html=True)
            st.checkbox(T("turbo"), key="cfg_turbo")
            st.slider(T("kw_count"), 5, 20, key="cfg_kw_n"); st.slider(T("q_count"), 3, 10, key="cfg_q_n")
            st.slider(T("chunk_size"), 1200, 4000, step=200, key="cfg_chunk")
            st.checkbox(T("extract_kw"), key="cfg_kw"); st.checkbox(T("gen_q"), key="cfg_qa")
        elif sec == "bureau": st.subheader(T("general")); st.checkbox(T("motion"), key="cfg_reduce_motion")
        elif sec == "extensions": st.subheader("Extensions"); st.write("Obsidian, Notion…")
        elif sec == "developpeur": st.subheader("Dev"); st.write("API & clés (bientôt).")
        elif sec == "competences": st.subheader("Skills"); st.write("—")
        elif sec == "connecteurs": st.subheader("Connect"); st.write("—")
        elif sec == "plugins": st.subheader("Plugins"); st.write("—")
        elif sec == "memoire": st.subheader("Memory"); st.write("—")
    render_footer(compact=True)
def render_admin():
    hero("tool", T("admin_title"), T("admin_sub"), [f'{ic("users", 13)} Clients', f'{ic("chart", 13)} Stats', f'{ic("card", 13)} {T("billing")}', f'{ic("msg", 13)} {T("tab_msgs")}'])
    
    # ═══ Sécurisation : lecture des secrets (marche en local ET cloud) ═══
    try:
        _sec_admin_user = st.secrets.get("ADMIN_USER", "admin")
        _sec_admin_pass = st.secrets.get("ADMIN_PASS", "admin123")
    except Exception:
        _sec_admin_user = "admin"
        _sec_admin_pass = "admin123"
    
    if ADMIN_USER == _sec_admin_user and ADMIN_PASS == _sec_admin_pass:
        st.warning("Mot de passe admin par défaut — personnalisez-le.")
    
    users = list_users(); rows = []
    for uname, u in users.items():
        hist = get_history(uname); pl = get_plan(uname)
        rows.append({"Utilisateur": uname, "Rôle": u.get("role","client"), "Plan": PLANS[pl]["name"] if pl != "free" else "Gratuit",
        "Email": u.get("email") or "—", "Créé le": u.get("created_at","")[:10], "Analyses": len(hist),
        "Temps (s)": round(sum(h.get("processing_time",0) for h in hist),1), "Statut": "Actif" if u.get("active", True) else "Suspendu"})
    df_users = pd.DataFrame(rows); clients = {u: d for u, d in users.items() if d.get("role") != "admin"}
    revenue = sum(PLANS[get_plan(u)]["monthly"] for u in users if get_plan(u) != "free")
    tab_stats, tab_clients, tab_create, tab_msgs = st.tabs([T("tab_overview"),T("tab_clients"),T("tab_create"),T("tab_msgs")])
    with tab_stats:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric(T("accounts"), len(users)); c2.metric(T("total_analyses"), int(df_users["Analyses"].sum())); c3.metric(T("cum_time"), f"{df_users['Temps (s)'].sum():.0f} s")
        c4.metric(T("paying"), sum(1 for u in users if get_plan(u) != "free")); c5.metric(T("rev_month"), f"${revenue:,.2f}")
        st.subheader(T("analyses_by_account")); st.bar_chart(pd.DataFrame({"Analyses": [len(get_history(u)) for u in users]}, index=list(users.keys())))
        st.subheader(T("revenues")); revs = get_revenues(); gA, gB = st.columns(2)
        with gA:
            total_collected = sum(r["amount"] for r in revs); st.metric(T("total_collected"), f"${total_collected:,.2f}")
            if revs: daily = pd.DataFrame(revs).groupby("date")["amount"].sum(); st.bar_chart(daily); st.caption("—")
            else: st.caption("—")
        with gB:
            st.metric("MRR", f"${revenue:,.2f}")
            counts = {p["name"]: sum(1 for u in users if get_plan(u)==k) for k,p in PLANS.items()}
            st.bar_chart(pd.DataFrame({"Abonnés": list(counts.values())}, index=list(counts.keys()))); st.caption("—")
        if revs: st.subheader(T("last_transactions")); st.dataframe(pd.DataFrame(revs[::-1]), use_container_width=True, hide_index=True)
    with tab_clients:
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        st.download_button("CSV", df_users.to_csv(index=False).encode("utf-8"), file_name="clients.csv", mime="text/csv")
        st.markdown("---"); st.subheader(T("tab_clients"))
        if clients:
            target = st.selectbox("Client", list(clients.keys())); is_active = clients[target].get("active", True)
            a1,a2,a3,a4 = st.columns(4)
            with a1:
                if st.button("Suspendre/Activer", use_container_width=True): set_active(target, not is_active); st.rerun()
            with a2:
                if st.button("Réinit. mdp", use_container_width=True): st.session_state[f"reset_{target}"] = True
            with a3:
                plan_opts = ["free","basique","premium","premium_plus"]
                new_plan = st.selectbox("Plan (30 j)", plan_opts, index=plan_opts.index(get_plan(target)), format_func=lambda p: PLANS[p]["name"] if p != "free" else "Gratuit", key=f"plan_{target}")
                if st.button("Appliquer", use_container_width=True):
                    set_plan(target, new_plan, 30)
                    if new_plan != "free": record_revenue(target, new_plan, PLANS[new_plan]["monthly"], 30, "manuel")
                    st.rerun()
            with a4:
                if st.button("Supprimer", use_container_width=True):
                    if delete_user(target): clear_history(target); st.rerun()
            if st.session_state.get(f"reset_{target}"):
                with st.form(f"reset_form_{target}"):
                    new_pass = st.text_input(T("pwd_new"), type="password")
                    if st.form_submit_button(T("pwd_confirm")):
                        if reset_password(target, new_pass): st.session_state.pop(f"reset_{target}", None); st.success("✓"); st.rerun()
                        else: st.error("6 min.")
            st.subheader(f"Historique : {target}"); hist = get_history(target)
            if hist: st.dataframe(pd.DataFrame([{"Date":h["date"],"Vidéo":h["video_id"],"Langue":h["lang"],"Chunks":h["num_chunks"],"Mots":h["total_words"],"Temps (s)":h["processing_time"]} for h in hist]), use_container_width=True, hide_index=True)
            else: st.caption("—")
        else: st.info("—")
    with tab_create:
        with st.form("create_client"):
            new_u = st.text_input(T("username")); new_e = st.text_input("Email"); new_p = st.text_input(T("password"), type="password")
            if st.form_submit_button(T("register"), use_container_width=True):
                ok, msg = register_user(new_u, new_p, new_e, role="client")
                if ok: notify(new_u.strip().lower(), "spark", "Bienvenue !"); st.success(f"{msg}")
                else: st.error(f"{msg}")
    with tab_msgs:
        msgs = get_messages(); st.metric("Non lus", sum(1 for m in msgs if not m["read"]))
        if msgs:
            for m in msgs:
                with st.expander(f"[{m['urgency'].upper()}] {m['user']} — {m['subject']}"):
                    st.write(m["message"]); b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Lu", key=f"read_{m['id']}"): mark_read(m['id']); st.rerun()
                    with b2:
                        if st.button("Suppr", key=f"del_{m['id']}"): delete_message(m['id']); st.rerun()
        else: st.caption("—")
    render_footer(compact=True)
    
def _step_indicator(current):
    parts = ['<div class="wizard-steps">']
    for s in [1,2,3,4]:
        cls = "active" if s == current else ("done" if s < current else "")
        label = "✓" if s < current else str(s)
        parts.append(f'<div class="wstep {cls}">{label}</div>')
        if s < 4: parts.append(f'<div class="wline{" done" if s < current else ""}"></div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

# ⚠️ render_register_wizard, render_login, render_register_page extraits dans src/pages/auth.py
# ═══════════════ ROUTAGE ═══════════════
_VALID_PAGES = {"accueil","analyse","premium","historique","stats","config","contact",
"notifs","about","login","register"}
if st.session_state.user is None:
    _token = read_cookie(COOKIE_NAME); _user = get_session_user(_token) if _token else None
    if not _user:
        _u2 = read_cookie("ys_user")
        if _u2:
            _us = list_users().get(_u2)
            if _us and _us.get("active", True):
                _user = _u2; _token = create_session(_u2); set_cookie(COOKIE_NAME, _token)
    if _user:
        st.session_state.update(user=_user, role=list_users()[_user].get("role","client"), token=_token)
        _load_appearance(_user)
_qp = st.query_params.get("page")
_last_q = st.session_state.get("last_query_page")
if _qp and _qp != _last_q and _qp in _VALID_PAGES:
    st.session_state.page = _qp
if st.session_state.user is None:
    _gpage = st.session_state.page
    try:
        st.query_params["page"] = _gpage
        st.session_state.last_query_page = _gpage
    except Exception: pass
    if _gpage == "login": render_login(); st.stop()
    if _gpage == "register": render_register_page(); st.stop()
    if _gpage == "about": render_about(); st.stop()
    if _gpage == "contact": render_contact(); st.stop()
    if _gpage == "premium": render_premium(); st.stop()
    render_landing(); st.stop()

# ═══════════════ SIDEBAR ═══════════════
user = st.session_state.user; role = st.session_state.get("role", "client"); is_guest = role == "visiteur"
tier = 3 if role == "admin" else (0 if is_guest else get_tier(user))
with st.sidebar:
    st.markdown(f'<div class="qbrand">{logo_html(34)}<span style="margin-left:8px;"><b>VideoScribe</b> AI</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="qcap">{T("menu")}</div>', unsafe_allow_html=True)
    for label, key in [(T("m_analyse"),"analyse"),(T("m_premium"),"premium"),(T("m_history"),"historique"),(T("m_stats"),"stats"), (T("m_contact"),"contact")]:
        if is_guest and key in ("profil","historique","stats","config"): continue
        if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if st.session_state.page == key else "secondary"): st.session_state.page = key; st.session_state.show_privacy = False; st.rerun()
    if not is_guest:
        st.markdown(f'<div class="qcap">{T("activity")}</div>', unsafe_allow_html=True); _n = unread_count(user)
        if st.button(f"{T('m_notifs')} ({_n})" if _n else T("m_notifs"), key="nav_notifs", use_container_width=True, type="primary" if st.session_state.page == "notifs" else "secondary"): st.session_state.page = "notifs"; st.session_state.show_privacy = False; st.rerun()
        if role == "admin":
            if st.button(T("m_admin"), key="nav_admin", use_container_width=True, type="primary" if st.session_state.page == "admin" else "secondary"): st.session_state.page = "admin"; st.session_state.show_privacy = False; st.rerun()
        _av = get_avatar_b64(user); _av_html = f'<img src="{_av}" alt="">' if _av else user[:2].upper(); _th = st.session_state.theme
        with st.container():
            st.markdown(f"""<div class="user-card"><div class="user-row"><span class="avatar">{_av_html}</span><span class="uname">{user} <span class="tier-chip">{TIER_CHIP[tier]}</span></span><span class="chev">{ic("chev", 14)}</span></div></div>""", unsafe_allow_html=True)
            if st.button(T("m_profile"), key="um_profil", use_container_width=True): st.session_state.update(page="profil"); st.rerun()
            if st.button(T("m_settings"), key="um_config", use_container_width=True): st.session_state.update(page="config"); st.rerun()
            if st.button(T("m_notifs"), key="um_notifs", use_container_width=True): st.session_state.update(page="notifs"); st.rerun()
            st.markdown('<div class="um-sep"></div>', unsafe_allow_html=True)
            if st.button(T("theme_to_light") if _th=="dark" else T("theme_to_dark"), key="um_theme", use_container_width=True): _toggle_theme()
            st.markdown('<div class="um-sep"></div>', unsafe_allow_html=True)
            if st.button(T("m_logout"), key="um_logout", use_container_width=True):
                if st.session_state.get("token"):
                    try: delete_session(st.session_state.get("token"))
                    except Exception: pass
                delete_cookie(COOKIE_NAME)
                delete_cookie("ys_user")
                delete_cookie("ys_theme")
                # Force l'anti-reconnexion
                st.session_state._logged_out = True
                st.session_state.user = None
                st.session_state.role = None
                st.session_state.token = None
                st.session_state.page = "contact"
                st.session_state.show_privacy = False
                _components.html("""<script>
                try {
                    document.cookie = "ys_token=; path=/; max-age=0; SameSite=Lax";
                    document.cookie = "ys_user=; path=/; max-age=0; SameSite=Lax";
                    if (window.parent && window.parent !== window) {
                        window.parent.document.cookie = "ys_token=; path=/; max-age=0; SameSite=Lax";
                        window.parent.document.cookie = "ys_user=; path=/; max-age=0; SameSite=Lax";
                    }
                } catch(e) {}
                </script>""", height=0, width=0)
                time.sleep(1)
                st.rerun()
    else:
        _th = st.session_state.theme
        with st.container():
            st.markdown(f"""<div class="user-card"><div class="user-row"><span class="avatar">{ic("user", 16)}</span><span class="uname">{T("guest")} <span class="tier-chip">FREE</span></span><span class="chev">{ic("chev", 14)}</span></div></div>""", unsafe_allow_html=True)
            if st.button(T("login"), key="gm_login", use_container_width=True): st.session_state.page="login"; st.rerun()
            if st.button(T("register"), key="gm_register", use_container_width=True): st.session_state.page="register"; st.rerun()
            st.markdown('<div class="um-sep"></div>', unsafe_allow_html=True)
            if st.button(T("theme_to_light") if _th=="dark" else T("theme_to_dark"), key="gm_theme", use_container_width=True): _toggle_theme()

import json as _json
_js_icons = _json.dumps({
    # ═══ FRANÇAIS ═══
    "Analyse": ic("film",16), "Accueil": ic("home",16), "Profil": ic("user",16), "Premium": ic("star",16), "Historique": ic("book",16),
    "Statistiques": ic("chart",16), "Paramètres": ic("sliders",16), "Contact": ic("phone",16), "À propos": ic("info",16),
    "Notifications": ic("bell",16), "Administration": ic("tool",16), "Passer en mode clair": ic("sun",16),
    "Passer en mode sombre": ic("moon",16), "Mode clair": ic("sun",16), "Mode sombre": ic("moon",16),
    "Se déconnecter": ic("logout",16), "Se connecter": ic("login",16),
    "Général": ic("sliders",16), "Compte": ic("user",16), "Confidentialité": ic("shield",16),
    "Facturation": ic("card",16), "Capacités": ic("cpu",16), "Développeur": ic("code",16),
    "Compétences": ic("spark",16), "Connecteurs": ic("link",16), "Mémoire": ic("clock",16),

    # ═══ ENGLISH ═══
    "Analysis": ic("film",16), "Home": ic("home",16), "Profile": ic("user",16), "History": ic("book",16),
    "Statistics": ic("chart",16), "Settings": ic("sliders",16), "About": ic("info",16), "Admin": ic("tool",16),
    "Log out": ic("logout",16), "Log in": ic("login",16), "Switch to light": ic("sun",16), "Switch to dark": ic("moon",16),
    "General": ic("sliders",16), "Account": ic("user",16), "Privacy": ic("shield",16),
    "Billing": ic("card",16), "Capabilities": ic("cpu",16),

    # ═══ ESPAÑOL ═══
    "Análisis": ic("film",16), "Inicio": ic("home",16), "Historial": ic("book",16), "Estadísticas": ic("chart",16),
    "Ajustes": ic("sliders",16), "Contacto": ic("phone",16), "Administración": ic("tool",16), "Cerrar sesión": ic("logout",16),
    "Cuenta": ic("user",16), "Privacidad": ic("shield",16), "Facturación": ic("card",16), "Capacidades": ic("cpu",16),

    # ═══ DEUTSCH ═══
    "Verlauf": ic("book",16), "Start": ic("home",16), "Statistiken": ic("chart",16), "Kontakt": ic("phone",16),
    "Einstellungen": ic("sliders",16), "Über uns": ic("info",16), "Verwaltung": ic("tool",16), "Abmelden": ic("logout",16),
    "Allgemein": ic("sliders",16), "Konto": ic("user",16), "Datenschutz": ic("shield",16),
    "Abrechnung": ic("card",16), "Funktionen": ic("cpu",16),

    # ═══ HARDCODED (mêmes dans toutes les langues) ═══
    "Extensions": ic("tool",16), "Plugins": ic("tool",16),
    "Dev": ic("code",16), "Skills": ic("spark",16), "Connect": ic("link",16), "Memory": ic("clock",16),
}, ensure_ascii=False)

_components.html(f"""<script>
(function () {{
var d = window.parent.document;
var icons = {_js_icons};
function decorate() {{
d.querySelectorAll('[data-testid="stSidebar"] button, div[data-testid="stVerticalBlock"]:has(.setnav) button').forEach(function (b) {{
var p = b.querySelector('p');
if (!p || p.querySelector('.vs-ic')) return;
var txt = (p.textContent || '').trim();
for (var k in icons) {{ if (txt.indexOf(k) === 0) {{ p.insertAdjacentHTML('afterbegin', '<span class="vs-ic">' + icons[k] + '</span>'); return; }} }}
}});
d.querySelectorAll('[data-testid="stForm"] div, [data-testid="stForm"] span').forEach(function (el) {{
if (el.childElementCount === 0 && el.textContent.trim() === 'Press Enter to submit form') el.style.display = 'none';
}});
}}
decorate();
setInterval(decorate, 500);
}})();
</script>""", height=0, width=0)

if st.session_state.user is not None and "notif_cursor_init" not in st.session_state:
    st.session_state.notif_cursor_init = True
    _latest = get_notifications(st.session_state.user)
    st.session_state.last_notif_id = _latest[0]["id"] if _latest else 0
notif_feedback()
if st.session_state.page == "admin" and role == "admin": render_admin(); st.stop()
if st.session_state.show_privacy: render_privacy(show_back=True); st.stop()
page = st.session_state.page
try:
    st.query_params["page"] = page
    st.session_state.last_query_page = page
except Exception: pass
if page == "accueil": render_home(); st.stop()
if page == "profil" and not is_guest: render_profil(); st.stop()
if page == "premium": render_premium(); st.stop()
if page == "historique" and not is_guest: render_historique(); st.stop()
if page == "stats" and not is_guest: render_stats(); st.stop()
if page == "config" and not is_guest: render_config(); st.stop()
if page == "contact": render_contact(); st.stop()
if page == "notifs" and not is_guest: render_notifs(); st.stop()
if page == "about": render_about(); st.stop()

# ═══════════════ PAGE ANALYSE — STUDIO PREMIUM ═══════════════
_a_theme = st.session_state.get("theme", "light")
_a_nav = "#0F1A2E" if _a_theme == "light" else "#F5F7FB"
_a_soft = "#4A5A7A" if _a_theme == "light" else "#B9C6E2"
_a_surface = "#FFFFFF" if _a_theme == "light" else "#111827"
_a_surface_2 = "#F7F9FC" if _a_theme == "light" else "#0B1220"
_a_card = "rgba(255,255,255,.92)" if _a_theme == "light" else "rgba(17,24,39,.92)"
_a_border = "rgba(15,26,46,.12)" if _a_theme == "light" else "rgba(255,255,255,.12)"
_a_shadow = "0 24px 70px rgba(15,26,46,.14)" if _a_theme == "light" else "0 24px 70px rgba(0,0,0,.42)"
_a_input = "#FFFFFF" if _a_theme == "light" else "#151B2B"
_a_accent = st.session_state.get("cfg_accent", "#2E6DB4")
_a_accent_dark = shade(_a_accent, 0.55)
_a_gold = "#D4AF37"
_a_hair = "rgba(15,26,46,.08)" if _a_theme == "light" else "rgba(255,255,255,.08)"
_a_noise = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E"
"%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E"
"%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")

st.markdown(f"""
<style>
.vs-studio-top {{ position:relative; overflow:hidden; border-radius:34px; padding:3.3rem 2.3rem 2.8rem; margin:.4rem 0 1.5rem;
background: radial-gradient(820px 340px at 6% -12%, rgba(59,130,246,.34), transparent 62%),
radial-gradient(780px 340px at 96% -12%, rgba(16,185,129,.24), transparent 60%),
linear-gradient(178deg, #070B12 0%, #0A1019 46%, #0D1524 100%);
border:1px solid rgba(255,255,255,.09); box-shadow:0 40px 100px rgba(2,8,18,.38), inset 0 1px 0 rgba(255,255,255,.06);
text-align:center; isolation:isolate; }}
.vs-studio-top::before {{ content:""; position:absolute; inset:0; z-index:0;
background:linear-gradient(90deg, transparent, rgba(255,255,255,.055), transparent);
transform:translateX(-100%); animation:vsShine 9s ease-in-out infinite; pointer-events:none; }}
.vs-studio-top::after {{ content:""; position:absolute; inset:0; z-index:0; opacity:.05; mix-blend-mode:overlay;
background-image:url("{_a_noise}"); pointer-events:none; }}
.vs-studio-top-bar {{ position:absolute; top:0; left:14%; right:14%; height:1px; z-index:1;
background:linear-gradient(90deg, transparent, rgba(96,165,250,.55), rgba(52,211,153,.55), transparent); }}
@keyframes vsShine {{ 0%,55% {{transform:translateX(-100%);}} 72%,100% {{transform:translateX(100%);}} }}
.vs-studio-kicker {{ position:relative; z-index:1; display:inline-flex; align-items:center; gap:9px; padding:7px 15px 7px 11px; border-radius:999px;
background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.13); color:rgba(255,255,255,.86) !important;
font-size:.76rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin-bottom:1.15rem; }}
.vs-kicker-dot {{ width:6px; height:6px; border-radius:50%; background:#34D399; box-shadow:0 0 0 0 rgba(52,211,153,.6); animation:vsPulse 2.2s ease-out infinite; }}
@keyframes vsPulse {{ 0%{{box-shadow:0 0 0 0 rgba(52,211,153,.55);}} 70%{{box-shadow:0 0 0 8px rgba(52,211,153,0);}} 100%{{box-shadow:0 0 0 0 rgba(52,211,153,0);}} }}
.vs-studio-title {{ position:relative; z-index:1; color:#F8FAFC !important; font-family:'Sora',sans-serif; font-weight:800;
letter-spacing:-.045em; line-height:1.06; font-size:clamp(1.9rem,4.6vw,4.1rem); margin:0; }}
.vs-studio-grad {{ background:linear-gradient(92deg,#60A5FA 0%,#34D399 50%,#FBBF24 100%);
-webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }}
.vs-studio-sub {{ position:relative; z-index:1; color:rgba(226,232,240,.72) !important; max-width:700px; margin:1.05rem auto 0; font-size:1.02rem; line-height:1.72; }}
.vs-quick-row {{ position:relative; z-index:1; display:flex; flex-wrap:wrap; gap:.55rem; justify-content:center; margin-top:1.5rem; }}
.vs-quick {{ display:inline-flex; align-items:center; gap:7px; padding:.56rem .95rem; border-radius:999px;
background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.11); color:rgba(241,245,249,.86) !important;
font-weight:700; font-size:.82rem; transition:transform .3s cubic-bezier(.16,1,.3,1), background .3s ease, border-color .3s ease; }}
.vs-quick:hover {{ transform:translateY(-2px); background:rgba(255,255,255,.10); border-color:rgba(255,255,255,.22); }}
.vs-link-marker {{ display:none; }}
div[data-testid="stVerticalBlock"]:has(.vs-link-marker) {{ position:relative; background:{_a_card}; border:1px solid {_a_border};
border-radius:30px; padding:1.1rem 1.1rem .9rem; box-shadow:{_a_shadow}; backdrop-filter:blur(18px);
overflow:hidden; }}
div[data-testid="stVerticalBlock"]:has(.vs-link-marker)::before {{ content:""; position:absolute; top:0; left:8%; right:8%; height:1px;
background:linear-gradient(90deg,transparent,{_a_accent}66,transparent); }}
div[data-testid="stVerticalBlock"]:has(.vs-link-marker) [data-testid="stTextInput"] input {{
height:68px !important; min-height:68px !important; border-radius:22px !important; background:{_a_input} !important;
color:{_a_nav} !important; border:1.5px solid rgba(76,111,255,.34) !important;
box-shadow:inset 0 1px 0 rgba(255,255,255,.06), 0 0 0 5px rgba(76,111,255,.075) !important;
padding:0 1.35rem !important; font-size:1.05rem !important; font-weight:650 !important;
transition:border-color .25s ease, box-shadow .25s ease !important; }}
div[data-testid="stVerticalBlock"]:has(.vs-link-marker) [data-testid="stTextInput"] input:focus {{
border-color:{_a_accent} !important; box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 0 0 5px {_a_accent}22 !important; }}
div[data-testid="stVerticalBlock"]:has(.vs-link-marker) [data-testid="stTextInput"] input::placeholder {{ color:{_a_soft} !important; opacity:.68 !important; }}
.vs-toolbar-marker {{ display:none; }}
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) {{ margin-top:.55rem; }}
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="column"]:first-child .stButton > button,
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="stColumn"]:first-child .stButton > button {{
min-height:58px !important; border-radius:20px !important; font-size:1.02rem !important;
background:linear-gradient(135deg,#0F172A,{_a_accent}) !important; color:#FFFFFF !important;
box-shadow:0 18px 40px rgba(46,109,180,.26) !important; letter-spacing:-.01em; }}
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="column"]:first-child .stButton > button:hover,
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="stColumn"]:first-child .stButton > button:hover {{
transform:translateY(-3px) scale(1.008) !important; box-shadow:0 24px 52px rgba(46,109,180,.34) !important; }}
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="column"]:not(:first-child) .stButton > button,
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button {{
min-height:58px !important; border-radius:20px !important; background:{_a_surface_2} !important; color:{_a_nav} !important;
border:1px solid {_a_border} !important; box-shadow:none !important; font-weight:700 !important; }}
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="column"]:not(:first-child) .stButton > button:hover,
div[data-testid="stVerticalBlock"]:has(.vs-toolbar-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button:hover {{
border-color:{_a_accent}55 !important; color:{_a_accent} !important; }}
.vs-chip-row {{ display:flex; flex-wrap:wrap; gap:.5rem; justify-content:flex-start; margin-top:.6rem; }}
.claude-chip {{ display:flex; align-items:center; justify-content:center; gap:8px; border:1px solid {_a_border};
border-radius:999px; padding:.5rem 1rem; font-size:.83rem; font-weight:650; color:{_a_soft} !important;
background:{_a_surface_2}; transition:all .25s ease; }}
.claude-chip:hover {{ border-color:{_a_accent}55; color:{_a_nav} !important; transform:translateY(-1px); }}
.vs-panel-head {{ position:relative; display:flex; align-items:center; gap:11px; margin-bottom:.15rem; }}
[data-testid="stColumn"]:has(.vs-panel-head) [data-testid="stColumn"]:last-child .stButton > button,
[data-testid="stColumn"]:has(.vs-panel-head) [data-testid="column"]:last-child .stButton > button {{
    background:transparent !important; border:1px solid {_a_border} !important; box-shadow:none !important;
    color:{_a_soft} !important; opacity:.75 !important; font-size:1rem !important; font-weight:800 !important;
    min-height:36px !important; height:36px !important; padding:0 !important;
    border-radius:10px !important; transition:opacity .25s ease, background .25s ease, transform .25s ease !important;
}}
[data-testid="stColumn"]:has(.vs-panel-head) [data-testid="stColumn"]:last-child .stButton > button:hover,
[data-testid="stColumn"]:has(.vs-panel-head) [data-testid="column"]:last-child .stButton > button:hover {{
    opacity:1 !important; background:{_a_surface_2} !important; transform:translateY(-1px);
}}
@keyframes vsFadeUp {{ from{{opacity:0; transform:translateY(-6px);}} to{{opacity:1; transform:translateY(0);}} }}
.vs-panel-collapsed-hint {{ display:flex; align-items:center; gap:8px; margin-top:.7rem; padding:.6rem .8rem;
border-radius:14px; background:{_a_surface_2}; border:1px dashed {_a_border}; color:{_a_soft} !important; font-size:.78rem; font-weight:600; }}
.vs-group-label {{ display:flex; align-items:center; gap:8px; margin:1.05rem 0 .55rem; color:{_a_soft} !important;
font-size:.68rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }}
.vs-group-label::after {{ content:""; flex:1; height:1px; background:{_a_border}; }}
.vs-group-label:first-of-type {{ margin-top:.3rem; }}
.vs-studio-panel .stCheckbox label, .vs-studio-panel label, .vs-studio-panel p, .vs-studio-panel span {{ color:{_a_nav} !important; }}
.vs-lock-card {{ display:flex; gap:10px; align-items:flex-start; border:1px dashed rgba(212,175,55,.5);
background:linear-gradient(135deg, rgba(212,175,55,.10), rgba(212,175,55,.03)); border-radius:18px; padding:.85rem .9rem; margin:.6rem 0;
color:{_a_nav} !important; transition:transform .25s ease, box-shadow .25s ease; }}
.vs-lock-card:hover {{ transform:translateY(-1px); box-shadow:0 10px 26px rgba(212,175,55,.14); }}
.vs-lock-card small {{ color:{_a_soft} !important; }}
.vs-mini-feature {{ position:relative; display:flex; align-items:center; gap:10px; padding:.7rem .8rem .7rem .78rem; border-radius:16px;
background:{_a_surface_2}; border:1px solid {_a_border}; margin:.5rem 0; color:{_a_nav} !important; font-weight:700; font-size:.9rem;
overflow:hidden; transition:transform .25s ease, border-color .25s ease; }}
.vs-mini-feature::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:3px; background:linear-gradient(180deg,{_a_gold},#F0D488); }}
.vs-mini-feature:hover {{ transform:translateX(2px); border-color:{_a_gold}55; }}
.vs-mini-feature small {{ display:block; font-weight:500; color:{_a_soft} !important; margin-top:2px; }}
.vs-mini-tag {{ margin-left:auto; flex-shrink:0; font-size:.6rem; font-weight:800; letter-spacing:.05em; text-transform:uppercase;
background:linear-gradient(135deg,{_a_gold},#F0D488); color:#0B1F3A !important; padding:3px 8px; border-radius:999px; }}
.vs-panel-footer-hint {{ display:flex; align-items:flex-start; gap:8px; margin-top:1.1rem; padding-top:.9rem; border-top:1px solid {_a_border};
color:{_a_soft} !important; font-size:.76rem; line-height:1.5; }}
.vs-result-hero {{ border-radius:28px; padding:1.35rem 1.45rem;
background:radial-gradient(500px 200px at 5% -20%, rgba(46,109,180,.20), transparent 62%), linear-gradient(135deg, rgba(46,109,180,.12), rgba(16,185,129,.07));
border:1px solid rgba(46,109,180,.24); margin:1.5rem 0 1rem; color:{_a_nav} !important; box-shadow:0 18px 44px rgba(15,26,46,.08);
transition:box-shadow .3s ease; }}
.vs-result-title {{ display:flex; align-items:center; gap:11px; font-family:'Sora',sans-serif; font-weight:800; font-size:1.15rem; color:{_a_nav} !important; }}
.vs-result-meta {{ color:{_a_soft} !important; margin-top:.35rem; font-size:.88rem; }}
.vs-score {{ display:inline-flex; align-items:center; gap:8px; padding:.5rem .82rem; border-radius:999px;
background:rgba(34,197,94,.10); border:1px solid rgba(34,197,94,.25); color:#16A34A !important; font-weight:800; margin-top:.8rem; }}
.vs-section-card {{ display:flex; gap:14px; padding:1rem 1.1rem; margin:.8rem 0; border-radius:20px;
background:{_a_surface}; border:1px solid {_a_border}; box-shadow:0 8px 26px rgba(15,26,46,.06); color:{_a_nav} !important;
transition:transform .25s ease, box-shadow .25s ease; }}
.vs-section-card:hover {{ transform:translateX(3px); box-shadow:0 14px 32px rgba(15,26,46,.10); }}
.vs-section-num {{ width:38px; height:38px; flex-shrink:0; border-radius:14px; display:flex; align-items:center; justify-content:center;
background:linear-gradient(135deg,{_a_accent},#34D399); color:#FFFFFF !important; font-weight:900; font-family:'Sora',sans-serif; }}
.vs-section-text {{ color:{_a_nav} !important; line-height:1.75; font-size:.96rem; }}
.vs-insight-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.75rem; margin:.8rem 0 1rem; }}
.vs-insight {{ border-radius:18px; padding:.9rem; background:{_a_surface}; border:1px solid {_a_border}; color:{_a_nav} !important;
transition:transform .25s ease; }}
.vs-insight:hover {{ transform:translateY(-3px); }}
.vs-insight b {{ display:block; color:{_a_nav} !important; font-size:.88rem; margin-bottom:.35rem; }}
.vs-insight span {{ color:{_a_soft} !important; font-size:.82rem; line-height:1.5; }}
.vs-action {{ display:flex; align-items:flex-start; gap:10px; border-radius:17px; padding:.82rem .9rem; margin:.5rem 0;
background:rgba(16,185,129,.08); border:1px solid rgba(16,185,129,.24); color:{_a_nav} !important; font-weight:650; }}
.vs-keyword {{ display:inline-flex; align-items:center; gap:6px; padding:7px 12px; border-radius:999px; margin:4px;
background:rgba(46,109,180,.10); border:1px solid rgba(46,109,180,.24); color:{_a_nav} !important; font-weight:750; font-size:.86rem;
transition:transform .2s ease, border-color .2s ease; }}
.vs-keyword:hover {{ transform:translateY(-2px); border-color:{_a_accent}66; }}
@media (max-width:900px) {{ .vs-insight-grid {{grid-template-columns:1fr;}} .vs-studio-panel {{position:relative; top:0;}} .vs-studio-top {{padding:2.2rem 1.2rem; border-radius:24px;}} }}
</style>
""", unsafe_allow_html=True)

def _first_sentence(text, max_len=190):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if not text: return "—"
    parts = re.split(r"(?<=[.!?])\s+", text)
    s = parts[0] if parts else text
    if len(s) > max_len: s = s[:max_len].rsplit(" ", 1)[0] + "…"
    return s

def _studio_score(data):
    notes = data.get("notes", []); kws = data.get("keywords", []); qs = data.get("questions", [])
    words = data.get("total_words", 0)
    score = 50
    if len(notes) >= 3: score += 15
    if len(kws) >= 5: score += 12
    if len(qs) >= 3: score += 10
    if words >= 1000: score += 8
    if data.get("processing_time", 0) and data.get("processing_time", 0) < 90: score += 5
    return min(score, 100)

def _render_lock(title, subtitle="Réservé aux abonnés Premium."):
    st.markdown(f"""<div class="vs-lock-card">
    <span>{ic("lock", 18)}</span>
    <div><b>{title}</b><br><small>{subtitle}</small></div>
    </div>""", unsafe_allow_html=True)

def _studio_md(data):
    kws = ", ".join([k for k, _ in data.get("keywords", [])[:10]]) or "—"
    txt = f"# {data.get('title', 'Résumé VideoScribe AI')}\n\n"
    txt += f"- Vidéo : https://youtu.be/{data.get('video_id')}\n- Date : {data.get('date')}\n"
    txt += f"- Langue : {data.get('lang', '').upper()}\n- Mots : {data.get('total_words', 0):,}\n- Mots-clés : {kws}\n\n"
    txt += "## Synthèse rapide\n"
    for note in data.get("notes", [])[:4]: txt += f"- {_first_sentence(note, 220)}\n"
    txt += "\n## Notes structurées\n"
    for i, note in enumerate(data.get("notes", []), 1): txt += f"\n### Section {i}\n{note}\n"
    if data.get("questions"):
        txt += "\n## Questions à explorer\n"
        for q in data["questions"]: txt += f"- {q}\n"
    return txt

def export_presentation(data):
    li = st.session_state.get("cfg_lang", "fr")
    def _tt(k): return I18N.get(li, {}).get(k) or I18N["fr"].get(k) or k
    title = _html.escape(data.get("title", "Résumé VideoScribe AI"))
    date = data.get("date", ""); lang = (data.get("lang") or "unknown").upper()
    words = data.get("total_words", 0); notes = data.get("notes", [])
    keywords = data.get("keywords", []); questions = data.get("questions", [])
    actions = better_extract_action_points(notes)
    slides = []
    slides.append(f"""<section class="slide is-active"><div class="orb o1"></div><div class="orb o2"></div>
<div class="kicker">✦ VideoScribe AI — Studio</div>
<h1 class="h1">{title}</h1>
<div class="chips"><span class="chip">📅 {date}</span><span class="chip">🌐 {lang}</span><span class="chip">📊 {words:,} {_tt('words')}</span><span class="chip">🧩 {len(notes)} {_tt('sections')}</span></div>
<div class="foot">{_tt('slide_generated')}</div></section>""")
    if notes:
        cards = "".join(f'<div class="card"><div class="card-n">{j+1:02d}</div><p>{_html.escape(_first_sentence(notes[j], 200))}</p></div>' for j in range(min(3, len(notes))))
        slides.append(f"""<section class="slide"><div class="orb o1"></div><div class="orb o2"></div>
<div class="kicker">{_tt('slide_synthesis')}</div><h2 class="h2">{_tt('tldr')}</h2>
<div class="cards">{cards}</div></section>""")
    for i, note in enumerate(notes[:5], 1):
        slides.append(f"""<section class="slide"><div class="orb o1"></div><div class="orb o2"></div>
<div class="kicker">{_tt('slide_notes')} • {i}/{len(notes)}</div><h2 class="h2">§ {i}</h2>
<p class="body">{_html.escape(_short(note, 400))}</p></section>""")
    if keywords:
        pills = "".join(f'<span class="pill">{_html.escape(str(k))}</span>' for k, _ in keywords[:12])
        slides.append(f"""<section class="slide"><div class="orb o1"></div><div class="orb o2"></div>
<div class="kicker">{_tt('slide_keywords')}</div><h2 class="h2">{_tt('res_kw')}</h2>
<div class="pills">{pills}</div></section>""")
    if questions:
        lis = "".join(f"<li>{_html.escape(q)}</li>" for q in questions[:5])
        slides.append(f"""<section class="slide"><div class="orb o1"></div><div class="orb o2"></div>
<div class="kicker">{_tt('slide_questions')}</div><h2 class="h2">{_tt('res_q')}</h2>
<ul class="list">{lis}</ul></section>""")
    if actions:
        lis = "".join(f"<li>{_html.escape(a)}</li>" for a in actions[:5])
        slides.append(f"""<section class="slide"><div class="orb o1"></div><div class="orb o2"></div>
<div class="kicker">{_tt('slide_actions')}</div><h2 class="h2">{_tt('res_actions')}</h2>
<ul class="list check">{lis}</ul></section>""")
    slides.append(f"""<section class="slide"><div class="orb o1"></div><div class="orb o2"></div>
<h1 class="h1 grad">{_tt('slide_end')}</h1>
<div class="foot">{_tt('slide_generated')} — © 2026 Mbtech-services</div></section>""")
    n = len(slides); body = "".join(slides)
    return f"""<!DOCTYPE html>
<html lang="{li}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {_tt('fx8')}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;700;800&family=Sora:wght@700;800&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{height:100%;overflow:hidden;background:#070B12;font-family:'Manrope',system-ui,sans-serif}}
.deck{{position:relative;width:100%;height:100%}}
.slide{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:6vh 7vw;opacity:0;visibility:hidden;transform:translateX(70px) scale(.98);transition:opacity .5s ease,transform .5s cubic-bezier(.22,1,.36,1),visibility 0s .5s}}
.slide.is-active{{opacity:1;visibility:visible;transform:none;transition:opacity .5s ease,transform .5s cubic-bezier(.22,1,.36,1)}}
.orb{{position:absolute;border-radius:50%;filter:blur(95px);opacity:.38;pointer-events:none}}
.o1{{width:430px;height:430px;left:-150px;top:-170px;background:#2563EB}}
.o2{{width:430px;height:430px;right:-150px;bottom:-170px;background:#10B981}}
.kicker{{display:inline-flex;align-items:center;gap:8px;padding:8px 18px;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);color:rgba(248,250,252,.8);font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin-bottom:1.4rem}}
.h1{{font-family:'Sora',sans-serif;font-weight:800;letter-spacing:-.03em;line-height:1.08;color:#F8FAFC;font-size:clamp(1.8rem,4.6vw,3.9rem);max-width:22em}}
.h2{{font-family:'Sora',sans-serif;font-weight:800;letter-spacing:-.02em;color:#F8FAFC;font-size:clamp(1.5rem,3.4vw,2.6rem);margin-bottom:1.6rem}}
.grad{{background:linear-gradient(90deg,#60A5FA 0%,#34D399 60%,#FBBF24 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.chips{{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;margin-top:1.6rem}}
.chip{{padding:.55rem .95rem;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14);color:#E2E8F0;font-weight:700;font-size:.88rem}}
.foot{{position:absolute;bottom:26px;left:0;right:0;text-align:center;color:#64748B;font-size:.85rem;font-weight:600}}
.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;max-width:1050px;width:100%}}
.card{{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);border-radius:20px;padding:1.2rem;text-align:left}}
.card-n{{font-family:'Sora',sans-serif;font-weight:800;font-size:.85rem;background:linear-gradient(90deg,#60A5FA,#34D399);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.6rem}}
.card p{{color:#CBD5E1;font-size:.95rem;line-height:1.6}}
.body{{color:#E2E8F0;font-size:clamp(1rem,1.6vw,1.25rem);line-height:1.8;max-width:56ch;text-align:left;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.10);border-left:4px solid #34D399;border-radius:18px;padding:1.4rem 1.6rem}}
.pills{{display:flex;flex-wrap:wrap;gap:.7rem;justify-content:center;max-width:900px}}
.pill{{padding:.7rem 1.3rem;border-radius:999px;background:linear-gradient(135deg,rgba(59,130,246,.18),rgba(16,185,129,.18));border:1px solid rgba(59,130,246,.35);color:#E2E8F0;font-weight:800;font-size:1rem}}
.list{{list-style:none;max-width:880px;width:100%;text-align:left}}
.list li{{background:rgba(255,255,255,.05);border-left:4px solid #3B82F6;border-radius:14px;padding:1rem 1.3rem;margin:.7rem 0;color:#E2E8F0;font-size:1.05rem;line-height:1.6}}
.list.check li{{border-left-color:#10B981}}
.bar{{position:fixed;top:0;left:0;height:4px;width:0;background:linear-gradient(90deg,#60A5FA,#34D399);z-index:20;transition:width .45s ease}}
.nav{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);display:flex;gap:10px;z-index:20}}
.nav button{{width:52px;height:52px;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.08);backdrop-filter:blur(12px);color:#fff;font-size:1.25rem;cursor:pointer;transition:all .25s ease}}
.nav button:hover{{background:rgba(255,255,255,.18);transform:scale(1.08)}}
.count{{position:fixed;bottom:38px;right:30px;color:#94A3B8;font-weight:800;z-index:20;font-size:.95rem}}
@media(max-width:820px){{.cards{{grid-template-columns:1fr}}.slide{{padding:5vh 6vw}}}}
</style>
</head>
<body>
<div class="bar" id="bar"></div>
<div class="deck">{body}</div>
<div class="nav"><button id="prev" aria-label="Previous">←</button><button id="next" aria-label="Next">→</button></div>
<div class="count" id="count">1 / {n}</div>
<script>
var s=document.querySelectorAll('.slide'),i=0;
function go(n){{i=(n+s.length)%s.length;s.forEach(function(el,k){{el.classList.toggle('is-active',k===i)}});document.getElementById('bar').style.width=((i+1)/s.length*100)+'%';document.getElementById('count').textContent=(i+1)+' / '+s.length;}}
document.getElementById('next').addEventListener('click',function(){{go(i+1)}});
document.getElementById('prev').addEventListener('click',function(){{go(i-1)}});
document.addEventListener('keydown',function(e){{if(e.key==='ArrowRight'||e.key===' '||e.key==='Enter'){{go(i+1)}}else if(e.key==='ArrowLeft'){{go(i-1)}}}});
go(0);
</script>
</body>
</html>"""

# ═══════════════ LAYOUT STUDIO ═══════════════
translate_to_fr = st.session_state.cfg_translate; extract_kw = st.session_state.cfg_kw
generate_qa = st.session_state.cfg_qa; model_choice = st.session_state.cfg_model
turbo = st.session_state.cfg_turbo; num_keywords = st.session_state.cfg_kw_n
num_questions = st.session_state.cfg_q_n; chunk_size = st.session_state.cfg_chunk
if st.query_params.get("nlhide") == "1": st.session_state.nl_hide = True
if "studio_panel_open" not in st.session_state: st.session_state.studio_panel_open = True

left_col, studio_col = st.columns([1.62, .88], gap="large")
with left_col:
    if not st.session_state.get("nl_hide", False):
        st.markdown(f"""
        <div class="vs-studio-top">
            <div class="vs-studio-top-bar"></div>
            <div class="vs-studio-kicker"><span class="vs-kicker-dot"></span>{ic("spark", 13)} VideoScribe Studio</div>
            <h1 class="vs-studio-title">Analysez vos vidéos.<br>Obtenez un <span class="vs-studio-grad">résumé exploitable</span>.</h1>
            <p class="vs-studio-sub">Collez un lien YouTube, lancez l'analyse, puis transformez la vidéo en notes, mots-clés, quiz, flashcards, exports, présentation et réponses IA.</p>
            <div class="vs-quick-row">
                <span class="vs-quick">{ic("zap", 14)} Résumé rapide</span>
                <span class="vs-quick">{ic("hash", 14)} Mots-clés</span>
                <span class="vs-quick">{ic("award", 14)} Quiz</span>
                <span class="vs-quick">{ic("download", 14)} Exports</span>
                <span class="vs-quick">{ic("image", 14)} Slides</span>
                <span class="vs-quick">{ic("msg", 14)} Chat vidéo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button(T("nl_show"), key="nl_show_btn", use_container_width=True):
            st.session_state.nl_hide = False
            try: st.query_params.pop("nlhide", None)
            except Exception: pass
            st.rerun()
    st.markdown('<div class="vs-link-marker"></div>', unsafe_allow_html=True)
    url = st.text_input("URL YouTube", placeholder=T("url_ph"), label_visibility="collapsed", key="studio_url")
    st.markdown('<div class="vs-toolbar-marker"></div>', unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1.55, .75, .75])
    with b1:
        process_btn = st.button(f"🔍 {T('analyse_btn')}", key="studio_analyse_btn", use_container_width=True)
    with b2:
        if st.button("YouTube ⌄", key="studio_source", use_container_width=True): st.toast("Source YouTube sélectionnée")
    with b3:
        _fast = model_choice == "rapide"
        if st.button(f"{'⚡' if _fast else '🧠'} {T('nl_mode_fast') if _fast else T('nl_mode_deep')}", key="studio_mode_btn", use_container_width=True):
            if tier >= 2:
                st.session_state.cfg_model = "qualite" if _fast else "rapide"; st.rerun()
            else: st.toast("Mode qualité réservé aux Premium.")
    if tier >= 3:
        with st.expander(f"⚡ {T('batch')}", expanded=False):
            st.caption(T("batch_hint"))
            batch_txt = st.text_area("URLs", key="batch_urls", height=130, label_visibility="collapsed", placeholder="https://www.youtube.com/watch?v=...\nhttps://youtu.be/...")
            batch_btn = st.button(T("batch_btn"), use_container_width=True)
    else:
        batch_txt = ""; batch_btn = False
    st.markdown("<div style='height:.9rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="vs-chip-row">', unsafe_allow_html=True)
    q1, q2, q3, q4, q5 = st.columns(5)
    for col, icon_name, label in [(q1,"file",T("chip_sum")),(q2,"lang",T("chip_tr")),(q3,"hash",T("chip_kw")),(q4,"bulb",T("chip_q")),(q5,"download",T("chip_exp"))]:
        with col: st.markdown(f'<div class="claude-chip">{ic(icon_name, 15)}{label}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with studio_col:
    _panel_open = st.session_state.studio_panel_open
    st.markdown('<div class="vs-studio-panel">', unsafe_allow_html=True)
    head_l, head_r = st.columns([5.2, 1])
    with head_l:
        st.markdown(f"""<div class="vs-panel-head">
            <div class="vs-panel-icon">{ic("sliders", 20)}</div>
            <div class="vs-panel-head-txt"><div class="vs-panel-title">Studio Premium</div><div class="vs-panel-sub">Réglages rapides de sortie</div></div>
        </div>""", unsafe_allow_html=True)
    with head_r:
        if st.button("⌃" if _panel_open else "⌄", key="studio_panel_toggle", help="Afficher / masquer les réglages", use_container_width=True):
            st.session_state.studio_panel_open = not _panel_open
            st.rerun()
    if _panel_open:
        st.markdown('<div class="vs-panel-body">', unsafe_allow_html=True)
        st.markdown('<div class="vs-group-label">Moteur IA</div>', unsafe_allow_html=True)
        if tier >= 2:
            st.selectbox(T("model"), ["rapide","qualite"], key="cfg_model", format_func=lambda m: "⚡ Rapide" if m=="rapide" else "🧠 Qualité Premium")
        else:
            st.markdown(f"""<div class="vs-lock-card">{ic("lock", 18)}<div><b>Modèle Qualité</b><br><small>Disponible à partir du plan Premium.</small></div></div>""", unsafe_allow_html=True)
        st.checkbox(T("turbo"), key="cfg_turbo")
        if tier >= 3:
            st.markdown('<div class="vs-group-label">Fonctions Premium+</div>', unsafe_allow_html=True)
            st.selectbox("Langue de sortie", ["fr","en","es","de"], key="cfg_target", format_func=lambda l: LANGS.get(l, l))
            st.checkbox("TL;DR enrichi", key="studio_tldr", value=st.session_state.get("studio_tldr", True))
            st.checkbox("Questions avancées", key="studio_questions", value=st.session_state.get("studio_questions", True))
            st.checkbox("Actions à faire", key="studio_actions", value=st.session_state.get("studio_actions", True))
            st.checkbox("Mode Studio Chat", key="studio_chat", value=st.session_state.get("studio_chat", True))
        else:
            st.markdown('<div class="vs-group-label">Fonctions Premium+</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="vs-mini-feature">{ic("star", 17)}<div>TL;DR enrichi<small>Résumé condensé et hiérarchisé</small></div><span class="vs-mini-tag">Premium+</span></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="vs-mini-feature">{ic("target", 17)}<div>Actions intelligentes<small>Points d'action détectés automatiquement</small></div><span class="vs-mini-tag">Premium+</span></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="vs-mini-feature">{ic("image", 17)}<div>{T("fx8")}<small>Slides générées depuis la vidéo</small></div><span class="vs-mini-tag">Premium+</span></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="vs-mini-feature">{ic("msg", 17)}<div>Chat vidéo IA<small>Question → réponse ancrée</small></div><span class="vs-mini-tag">Premium+</span></div>""", unsafe_allow_html=True)
        st.markdown('<div class="vs-group-label">Quantités</div>', unsafe_allow_html=True)
        st.slider(T("kw_count"), 5, 20, key="cfg_kw_n"); st.slider(T("q_count"), 3, 10, key="cfg_q_n")
        st.slider(T("chunk_size"), 1200, 4000, step=200, key="cfg_chunk")
        st.markdown('<div class="vs-group-label">Sortie</div>', unsafe_allow_html=True)
        st.checkbox(T("extract_kw"), key="cfg_kw"); st.checkbox(T("gen_q"), key="cfg_qa"); st.checkbox(T("chip_tr"), key="cfg_translate")
        st.markdown(f"""<div class="vs-panel-footer-hint">{ic("info", 14)}<span>Ces réglages s'appliquent à ta prochaine analyse. Ils sont mémorisés pour ce compte.</span></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="vs-panel-collapsed-hint">{ic("chev", 13)} Réglages repliés — clique sur la flèche pour les rouvrir.</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def _run_one(url_single):
    video_id = extract_video_id(url_single)
    if not video_id: return None
    transcript, lang = get_transcript(video_id)
    if transcript.startswith("Error"): return None
    ch = chunk_text(transcript, chunk_size=chunk_size); work = ch
    if lang != "en": work = translate_texts(ch, src=lang, dest="en")
    beams = 1 if turbo else 3
    cache_notes = Path("cache") / f"notes_{video_id}_{model_choice}_b{beams}.json"
    if cache_notes.exists():
        notes = json.loads(cache_notes.read_text(encoding="utf-8"))
    else:
        summarizer = get_summarizer(model_choice)
        notes = summarizer.summarize_video(work, lambda i,t: None, batch_size=6, num_beams=beams)
        cache_notes.parent.mkdir(parents=True, exist_ok=True)
        cache_notes.write_text(json.dumps(notes, ensure_ascii=False), encoding="utf-8")
    notes = [clean_summary(remove_repetitions(n)) for n in notes]
    if translate_to_fr:
        target = st.session_state.cfg_target if tier >= 3 else "fr"
        notes = [polish_translation(n) for n in translate_texts(notes, src="en", dest=target)]
    kws = better_extract_keywords(transcript, top_n=num_keywords, lang=lang) if extract_kw else []
    qs = better_generate_questions(notes, keywords=kws, n=num_questions, lang=st.session_state.get("cfg_lang","fr")) if generate_qa else []
    return {"video_id": video_id, "url": url_single, "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "lang": lang or "unknown", "num_chunks": len(ch), "total_chars": len(transcript),
    "total_words": len(transcript.split()), "processing_time": 0,
    "title": f"Résumé - {video_id}", "author": "", "notes": notes, "keywords": kws, "questions": qs}

if tier >= 3 and batch_btn and batch_txt.strip():
    urls = [line.strip() for line in batch_txt.splitlines() if line.strip()]
    st.session_state.results_batch = []; st.session_state.result = None
    done = 0; failed = 0
    st.markdown("---")
    st.markdown(f'<div class="pipe-card"><b class="pipe-title">{ic("zap",16)} {T("batch")} ({len(urls)})</b></div>', unsafe_allow_html=True)
    prog = st.progress(0); status = st.empty()
    for i, u_single in enumerate(urls):
        vid = extract_video_id(u_single) or u_single[:50]
        status.markdown(f'<div class="pipe-row">{ic("film",16)}<span class="pipe-lbl">{i+1}/{len(urls)} : <b>{_html.escape(vid)}</b></span><span class="pipe-run">● …</span></div>', unsafe_allow_html=True)
        rec = _run_one(u_single)
        if rec:
            save_analysis(user, rec); st.session_state.results_batch.append(rec); done += 1
            status.markdown(f'<div class="pipe-row">{ic("film",16)}<span class="pipe-lbl">OK — {_html.escape(rec["title"])}</span><span class="pipe-ok">{ic("check",14)} OK</span></div>', unsafe_allow_html=True)
        else:
            failed += 1
            status.markdown(f'<div class="pipe-row">{ic("film",16)}<span class="pipe-lbl">Échec — {_html.escape(vid)}</span><span style="color:#dc2626;font-weight:800;">Erreur</span></div>', unsafe_allow_html=True)
        prog.progress((i+1)/len(urls))
    prog.empty(); status.empty()
    if done:
        st.success(f"Lot terminé : {done} succès / {failed} échecs sur {len(urls)} vidéos.")
        st.session_state.result = st.session_state.results_batch[-1]; st.rerun()
    else: st.error("Aucune vidéo analysée dans le lot.")

if process_btn and url:
    start_time = time.time(); st.markdown("---")
    with st.container():
        st.markdown(f'<div class="pipe-card"><b class="pipe-title">{ic("zap",16)} Pipeline Studio</b></div>', unsafe_allow_html=True)
        ph_detect = st.empty(); ph_sub = st.empty(); ph_chunk = st.empty()
        ph_sum = st.empty(); ph_tr = st.empty(); ph_kw = st.empty()
        txt_ph = st.empty(); prog_ph = st.empty()
    def _step(ph, icon_name, label, state):
        if state == "ok": badge = f'<span class="pipe-ok">{ic("check",14)} OK</span>'
        elif state == "run": badge = '<span class="pipe-run">● Analyse…</span>'
        else: badge = '<span class="pipe-wait">En attente</span>'
        ph.markdown(f'<div class="pipe-row">{ic(icon_name,16)}<span class="pipe-lbl">{label}</span>{badge}</div>', unsafe_allow_html=True)
    _step(ph_detect, "link", "Détection du lien", "run")
    video_id = extract_video_id(url)
    if not video_id: st.error("URL YouTube invalide."); st.stop()
    _step(ph_detect, "link", f"Vidéo détectée : {video_id}", "ok")
    if tier == 0 and not is_guest:
        used = count_today(user)
        if used >= FREE_DAILY_LIMIT: st.error(f"Limite gratuite atteinte ({FREE_DAILY_LIMIT}/jour)."); st.stop()
        st.info(f"{T('plan_free')} : {FREE_DAILY_LIMIT - used} analyse(s) restante(s) aujourd'hui.")
    if tier < 2 and model_choice == "qualite": model_choice = "rapide"
    _step(ph_sub, "film", "Extraction des sous-titres", "run")
    transcript, lang = get_transcript(video_id)
    if transcript.startswith("Error"):
        low = transcript.lower()
        if "members-only" in low or "join this channel" in low: st.error("Vidéo réservée aux membres.")
        elif "private" in low or "unplayable" in low: st.error("Vidéo privée ou supprimée.")
        elif "no transcript" in low or "could not retrieve" in low: st.error("Aucun sous-titre public disponible pour cette vidéo.")
        else: st.error(transcript)
        st.stop()
    _step(ph_sub, "film", f"Sous-titres OK — {len(transcript.split()):,} mots ({lang})", "ok")
    _step(ph_chunk, "folder", "Découpage intelligent", "run")
    chunks = chunk_text(transcript, chunk_size=chunk_size)
    _step(ph_chunk, "folder", f"{len(chunks)} chunks générés", "ok")
    work_chunks = chunks
    if lang != "en":
        _step(ph_tr, "lang", f"Pré-traduction {lang} → EN", "run")
        work_chunks = translate_texts(chunks, src=lang, dest="en")
        _step(ph_tr, "lang", f"Pré-traduction {lang} → EN OK", "ok")
    else: _step(ph_tr, "lang", "Traduction source non nécessaire", "wait")
    _step(ph_sum, "cpu", f"Résumé IA — mode {model_choice}", "run")
    beams = 1 if turbo else 3
    cache_notes = Path("cache") / f"notes_{video_id}_{model_choice}_b{beams}.json"
    force_refresh = st.session_state.get(f"refresh_{video_id}", False)
    if cache_notes.exists() and not force_refresh:
        notes = json.loads(cache_notes.read_text(encoding="utf-8"))
        _step(ph_sum, "cpu", f"{len(notes)} sections récupérées depuis le cache", "ok")
    else:
        if force_refresh: st.session_state[f"refresh_{video_id}"] = False
        def update_progress(i, total):
            txt_ph.markdown(f'<span class="pipe-run">Résumé du chunk {i}/{total}…</span>', unsafe_allow_html=True)
            prog_ph.progress(i / total)
        with st.spinner(f"Résumé en cours avec le modèle {model_choice}…"):
            summarizer = get_summarizer(model_choice)
            notes = summarizer.summarize_video(work_chunks, update_progress, batch_size=6, num_beams=beams)
        txt_ph.empty(); prog_ph.empty()
        cache_notes.parent.mkdir(parents=True, exist_ok=True)
        cache_notes.write_text(json.dumps(notes, ensure_ascii=False), encoding="utf-8")
        _step(ph_sum, "cpu", f"{len(notes)} sections générées", "ok")
    notes = [clean_summary(remove_repetitions(n)) for n in notes]
    if translate_to_fr:
        target = st.session_state.cfg_target if tier >= 3 else "fr"
        _step(ph_tr, "lang", f"Traduction finale → {target.upper()}", "run")
        notes = [polish_translation(n) for n in translate_texts(notes, src="en", dest=target)]
        _step(ph_tr, "lang", f"Traduction finale → {target.upper()} OK", "ok")
    _step(ph_kw, "hash", "Extraction des mots-clés et questions", "run")
    keywords = better_extract_keywords(transcript, top_n=num_keywords, lang=lang) if extract_kw else []
    questions = better_generate_questions(notes, keywords=keywords, n=num_questions, lang=st.session_state.get("cfg_lang","fr")) if generate_qa else []
    _step(ph_kw, "hash", f"{len(keywords)} mots-clés | {len(questions)} questions", "ok")
    elapsed = time.time() - start_time
    record = {"video_id": video_id, "url": url, "date": datetime.now().strftime("%d/%m/%Y %H:%M"), "lang": lang or "unknown",
    "num_chunks": len(chunks), "total_chars": len(transcript), "total_words": len(transcript.split()),
    "processing_time": round(elapsed,1), "title": f"Résumé - {video_id}", "author": "",
    "notes": notes, "keywords": keywords, "questions": questions}
    if is_guest: st.info(T("login_sub"))
    else: save_analysis(user, record); trim_history(user, keep=HIST_KEEP[tier]); st.success(f"Analyse terminée en {elapsed:.1f} s.")
    st.session_state.result = record

if st.session_state.result:
    data = st.session_state.result
    if st.session_state.get("results_batch") and len(st.session_state.results_batch) > 1:
        batch = st.session_state.results_batch
        labels = [f"{i+1}. {r['title'][:60]}" + ("…" if len(r['title'])>60 else "") for i, r in enumerate(batch)]
        current_idx = next((i for i, r in enumerate(batch) if r["video_id"] == data["video_id"]), len(batch)-1)
        chosen = st.selectbox("Résultats du lot", options=range(len(batch)), format_func=lambda i: labels[i], index=current_idx, key="batch_selector")
        if chosen != current_idx:
            st.session_state.result = batch[chosen]; st.rerun()
    score = _studio_score(data)
    st.markdown(f"""
    <div class="vs-result-hero">
        <div class="vs-result-title">{ic("file", 22)} {T("res_title")} — {_html.escape(data["title"])}</div>
        <div class="vs-result-meta">{data["date"]} • {data["lang"].upper()} • {data.get("total_words", 0):,} {T("words")} • {data.get("processing_time", 0)} s</div>
        <div class="vs-score">{ic("check", 15)} Score Studio : {score}/100</div>
    </div>
    """, unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(T("lang_lbl"), data["lang"].upper()); m2.metric(T("sections"), len(data.get("notes", [])))
    m3.metric(T("chunks"), data.get("num_chunks", "-")); m4.metric(T("words"), f"{data.get('total_words', 0):,}")
    m5.metric(T("time"), f"{data.get('processing_time', 0)} s")
    tab_summary, tab_notes, tab_studio, tab_export = st.tabs(["Synthèse", T("res_struct"), "Studio", T("res_export")])
    with tab_summary:
        notes = data.get("notes", []); keywords = data.get("keywords", [])
        st.markdown("### Vue d'ensemble")
        insight_1 = _first_sentence(notes[0]) if len(notes) > 0 else "—"
        insight_2 = _first_sentence(notes[1]) if len(notes) > 1 else "—"
        insight_3 = _first_sentence(notes[2]) if len(notes) > 2 else "—"
        st.markdown(f"""
        <div class="vs-insight-grid">
            <div class="vs-insight"><b>{ic("spark",14)} Idée principale</b><span>{_html.escape(insight_1)}</span></div>
            <div class="vs-insight"><b>{ic("target",14)} Point important</b><span>{_html.escape(insight_2)}</span></div>
            <div class="vs-insight"><b>{ic("bulb",14)} À retenir</b><span>{_html.escape(insight_3)}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if tier >= 2:
            st.markdown(f"### {T('tldr')}")
            for item in notes[:5]:
                st.markdown(f'<div class="vs-action">{ic("check", 15)} <span>{_html.escape(_first_sentence(item, 260))}</span></div>', unsafe_allow_html=True)
        else: _render_lock("TL;DR avancé", "Disponible à partir du plan Premium.")
        if keywords:
            st.markdown(f"### {T('res_kw')}")
            st.markdown(" ".join([f'<span class="vs-keyword">{_html.escape(str(kw))} <small>{score_kw}</small></span>' for kw, score_kw in keywords]), unsafe_allow_html=True)
        if data.get("questions"):
            st.markdown(f"### {T('res_q')}")
            for q in data["questions"]: st.markdown(f'<div class="q-item">{_html.escape(q)}</div>', unsafe_allow_html=True)
    with tab_notes:
        st.markdown(f"### {T('res_struct')}")
        for i, note in enumerate(data.get("notes", []), 1):
            st.markdown(f"""
            <div class="vs-section-card">
                <div class="vs-section-num">{i}</div>
                <div class="vs-section-text">{_html.escape(note)}</div>
            </div>
            """, unsafe_allow_html=True)
    with tab_studio:
        st.markdown("### Studio IA")
        if not is_guest:
            is_fav = data["video_id"] in load_favs(user)
            if st.button(("⭐" if is_fav else "☆") + " " + T("add_fav"), use_container_width=True, key="studio_fav_result"):
                added = toggle_fav(user, data["video_id"])
                st.success("Ajouté aux favoris." if added else "Retiré des favoris."); st.rerun()
        st.markdown("---")
        st.markdown(f"#### {ic('msg', 18)} {T('res_ask')}", unsafe_allow_html=True)
        if tier >= 3:
            q = st.text_input(T("res_ask"), key="video_q", placeholder="Ex. Quel est le message principal de cette vidéo ?")
            if st.button(T("send"), key="studio_send_question", use_container_width=True):
                if q.strip(): ans, refs = answer_question(q, data["notes"]); st.session_state.last_qa = (q, ans, refs)
            if st.session_state.get("last_qa"):
                qq, ans, refs = st.session_state.last_qa
                st.markdown(f"""
                <div class="qa-box">
                    <b>Question :</b> {_html.escape(qq)}<br><br>
                    <b>Réponse :</b> {_html.escape(ans)}
                </div>
                """, unsafe_allow_html=True)
                if refs: st.caption(f"Sections utilisées : {', '.join(map(str, refs))}")
        else: _render_lock("Chat vidéo IA", "Disponible avec Premium+.")
        st.markdown("---")
        st.markdown(f"#### {ic('award', 18)} {T('res_quiz')}", unsafe_allow_html=True)
        if tier >= 2:
            quiz = build_quiz(data, lang=st.session_state.get("cfg_lang", "fr"))
            if quiz:
                with st.form("quiz_form"):
                    answers = {}
                    for i, qq in enumerate(quiz): answers[i] = st.radio(qq["q"], qq["choices"], key=f"qz_{i}")
                    if st.form_submit_button(T("verify"), use_container_width=True):
                        score_q = sum(1 for i, qq in enumerate(quiz) if answers[i] == qq["answer"])
                        st.session_state.quiz_score = (score_q, len(quiz))
                if st.session_state.get("quiz_score"):
                    sc, tot = st.session_state.quiz_score
                    st.progress(sc / tot)
                    if sc == tot: st.balloons(); st.success(f"Parfait : {sc}/{tot}")
                    elif sc >= tot / 2: st.success(f"Bon score : {sc}/{tot}")
                    else: st.info(f"Score : {sc}/{tot}")
            else: st.info("Pas assez de contenu pour générer un quiz.")
        else: _render_lock("Quiz interactif", "Disponible avec Premium.")
        st.markdown("---")
        st.markdown(f"#### {ic('target', 18)} {T('res_actions')}", unsafe_allow_html=True)
        if tier >= 3:
            actions = better_extract_action_points(data["notes"])
            if actions:
                for a in actions: st.markdown(f'<div class="vs-action">{ic("check", 15)} <span>{_html.escape(a)}</span></div>', unsafe_allow_html=True)
            else: st.info("Aucun point d'action clair détecté.")
        else: _render_lock("Points d'action intelligents", "Disponible avec Premium+.")
        st.markdown("---")
        st.markdown(f"#### {ic('volume', 18)} Audio", unsafe_allow_html=True)
        if tier >= 3:
            audio_filename = f"audio_{data['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if st.button(T("gen_audio"), key="studio_audio", use_container_width=True):
                with st.spinner("Génération audio…"): audio_path = generate_audio(" . ".join(data["notes"][:4]), audio_filename)
                if audio_path:
                    with open(audio_path, "rb") as f:
                        st.download_button(T("dl_audio"), f.read(), file_name=f"{audio_filename}.mp3", mime="audio/mpeg", use_container_width=True)
                else: st.warning("Module gTTS requis pour générer l'audio.")
        else: _render_lock("Résumé audio", "Disponible avec Premium+.")
    with tab_export:
        st.markdown(f"### {T('res_export')}")
        filename = f"summary_{data['video_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        e1, e2 = st.columns(2)
        with e1:
            with open(export_to_markdown(data, filename), "rb") as f:
                st.download_button(T("dl_md"), f.read(), file_name=f"{filename}.md", mime="text/markdown", use_container_width=True)
        with e2:
            if tier >= 1:
                with open(export_to_pdf(data, filename), "rb") as f:
                    st.download_button(T("dl_pdf"), f.read(), file_name=f"{filename}.pdf", mime="application/pdf", use_container_width=True)
            else: _render_lock("Export PDF", "Disponible avec Basique et plus.")
        if tier >= 2:
            with open(export_anki(data, filename), "rb") as f:
                st.download_button(T("dl_anki"), f.read(), file_name=f"{filename}.anki.txt", mime="text/plain", use_container_width=True)
        else: _render_lock("Export Anki", "Disponible avec Premium.")
        st.markdown("---")
        st.markdown(f"#### 🎨 {T('fx8')}", unsafe_allow_html=True)
        if tier >= 3:
            pres_key = f"pres_html_{data['video_id']}"
            if st.button("🎬 Générer la présentation", key="studio_gen_pres", use_container_width=True):
                with st.spinner("Génération des slides…"): st.session_state[pres_key] = export_presentation(data)
                st.rerun()
            if st.session_state.get(pres_key):
                _components.html(st.session_state[pres_key], height=430)
                st.download_button(f"💾 {T('dl_presentation')}", st.session_state[pres_key].encode("utf-8"),
                file_name=f"presentation_{data['video_id']}.html", mime="text/html", use_container_width=True)
        else: _render_lock(T("fx8"), "Disponible avec Premium+.")
        st.markdown("---")
        if tier >= 1:
            if st.button(T("share"), key="studio_share", use_container_width=True):
                sid = save_share(data, user); st.session_state.share_link = f"?page=share&id={sid}"
            if st.session_state.get("share_link"): st.code(st.session_state.share_link)
        else: _render_lock("Lien de partage public", "Disponible avec Basique et plus.")
        if tier >= 3:
            st.markdown("---")
            x1, x2 = st.columns(2)
            with x1:
                with open(export_to_obsidian(data, filename), "rb") as f:
                    st.download_button("Obsidian", f.read(), file_name=f"{filename}_obsidian.md", mime="text/markdown", use_container_width=True)
            with x2:
                with open(export_to_notion(data, filename), "rb") as f:
                    st.download_button("Notion", f.read(), file_name=f"{filename}_notion.md", mime="text/markdown", use_container_width=True)
        st.markdown("---")
        st.download_button("Exporter le rapport Studio complet", _studio_md(data).encode("utf-8"),
        file_name=f"{filename}_studio.md", mime="text/markdown", use_container_width=True)
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button(T("reanalyse"), key="studio_reanalyse", use_container_width=True):
                st.session_state[f"refresh_{data['video_id']}"] = True; st.session_state.result = None; st.rerun()
        with col_b:
            if st.button(T("del_cache"), key="studio_del_cache", use_container_width=True):
                for p in Path("cache").glob(f"notes_{data['video_id']}_*.json"): p.unlink()
                st.session_state.result = None; st.success("Cache supprimé."); st.rerun()
        with col_c:
            if st.session_state.get("results_batch"):
                if st.button(T("close_batch"), key="studio_close_batch", use_container_width=True):
                    st.session_state.results_batch = []; st.session_state.result = None; st.rerun()

# ═══════════════ PAGE PARTAGE PUBLIC ═══════════════
if st.session_state.page == "share":
    import streamlit as _st
    _params = _st.query_params; sid = _params.get("id"); shares = load_shares()
    if sid and sid in shares:
        sh = shares[sid]; hero("link", "Résumé partagé", f"{sh['video_id']} — {sh['owner']}")
        for i, note in enumerate(sh["notes"], 1):
            st.markdown(f"""
            <div class="vs-section-card">
                <div class="vs-section-num">{i}</div>
                <div class="vs-section-text">{_html.escape(note)}</div>
            </div>
            """, unsafe_allow_html=True)
    else: st.error("Lien invalide.")