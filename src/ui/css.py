"""
Module CSS — Design system de VideoScribe AI.

Extrait de app.py pour :
- Alléger app.py d'environ 1200 lignes
- Permettre la réutilisation dans d'autres modules
- Séparer les styles du code métier

Contient :
- BASE_CSS : Reset global, typographie, classes génériques
- APP_CSS : Design system complet (cards, navbar, dark mode)
- custom_css() : CSS dynamique basé sur les préférences utilisateur
"""

import streamlit as st


# ═══════════════════════════════════════════════════════════════
# BASE CSS — Reset global + typographie
# ═══════════════════════════════════════════════════════════════

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');
html, body, .stApp { font-family: 'Manrope', sans-serif !important; }
h1, h2, h3, h4 { font-family: 'Sora', sans-serif !important; letter-spacing: -.02em !important; }
#MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 2.7rem !important; }
header [data-testid="stToolbarActions"] { display: none !important; }
[data-testid*="Deploy"], #stDeployButton { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { top: .6rem !important; left: .6rem !important; }
[data-testid="stSidebarCollapsedControl"] button {
width: 42px !important; height: 42px !important; border-radius: 12px !important;
background: rgba(15,26,46,.85) !important; border: 1px solid rgba(128,128,128,.35) !important;
box-shadow: 0 6px 18px rgba(0,0,0,.3) !important; }
[data-testid="stSidebarCollapsedControl"] button svg { display: none !important; }
[data-testid="stCollapseSidebar"] { opacity: .85 !important; }
#root, #root > div, div[data-testid="stAppViewContainer"], div[data-testid="stAppViewBlockContainer"],
main[data-testid="stMain"], section.main { padding-top: 0 !important; margin-top: 0 !important; }
div[data-testid="stMainBlockContainer"], section.main > div.block-container { padding-top: .5rem !important; }
iframe { border-radius: 24px !important; border: 1px solid rgba(46,109,180,.35) !important;
box-shadow: 0 24px 60px rgba(11,31,58,.45) !important; }
.g-kicker { letter-spacing:.24em; text-transform:uppercase; font-size:.7rem; font-weight:800; color:#C89B3C; }
.g-h1 { font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(2.3rem,4.6vw,3.8rem);
line-height:1.06; letter-spacing:-.02em; margin:.9rem 0 1rem; }
.g-h1 em { font-style:normal; color:#C89B3C; }
.g-h2 { font-family:'Sora',sans-serif; font-weight:700; font-size:clamp(1.5rem,2.6vw,2.2rem); }
.g-lead { font-size:1.06rem; line-height:1.75; max-width:56ch; }
.g-rule { width:56px; height:2px; background:#C89B3C; margin:1.4rem 0; }
.g-stats { display:flex; border-top:1px solid rgba(128,128,128,.2); border-bottom:1px solid rgba(128,128,128,.2); margin:2.6rem 0; }
.g-stat { flex:1; text-align:center; padding:1.5rem 1rem; border-left:1px solid rgba(128,128,128,.2); }
.g-stat:first-child { border-left:none; }
.g-stat b { display:block; font-family:'Sora',sans-serif; font-weight:800; font-size:1.9rem; }
.g-stat span { font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; }
.g-step { border-top:2px solid rgba(128,128,128,.2); padding-top:1.2rem; }
.g-step .n { font-family:'Sora',sans-serif; font-weight:800; color:#C89B3C; font-size:.85rem; letter-spacing:.2em; }
.g-step h4 { font-family:'Sora',sans-serif; font-weight:700; margin:.5rem 0 .4rem; }
.g-step p { font-size:.93rem; line-height:1.6; }
.g-ico { width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; margin-bottom:1rem; }
.feat-card { background: linear-gradient(160deg, rgba(46,109,180,.14), rgba(212,175,55,.08)); border: 1px solid rgba(46,109,180,.32);
border-radius: 18px; padding: 1.4rem 1.1rem; text-align: center; transition: all .3s ease; height: 100%; }
.feat-card:hover { transform: translateY(-6px); box-shadow: 0 16px 36px rgba(0,0,0,.22); }
.feat-icon { display:flex; justify-content:center; margin-bottom:.6rem; }
.feat-title { font-weight: 800; font-size: 1.05rem; font-family: 'Sora', sans-serif; }
.feat-text { font-size: .88rem; opacity: .9; margin-top: .45rem; line-height: 1.55; }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stTextInput"] input {
border-radius: 999px !important; padding: 1.05rem 1.5rem !important; font-size: 1.02rem !important;
border: 1.5px solid rgba(128,128,128,.35) !important;
box-shadow: 0 6px 24px rgba(0,0,0,.10) !important; transition: all .25s ease !important; }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stTextInput"] input:focus {
border-color: #2E6DB4 !important; box-shadow: 0 8px 32px rgba(46,109,180,.28) !important; }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stButton"] > button { border-radius: 999px !important; }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stExpander"] {
border: 1px solid rgba(128,128,128,.25) !important; border-radius: 14px !important; }
.claude-hello { text-align:center; padding: 3rem 0 .5rem; }
.claude-hello .big { font-size: 2.4rem; font-weight: 800; font-family:'Sora',sans-serif; display:flex; align-items:center; justify-content:center; gap:14px; }
.claude-sub { margin-top:.6rem; font-size:1rem; }
.claude-chip { display:flex; align-items:center; justify-content:center; gap:8px; border:1px solid rgba(128,128,128,.3);
border-radius:999px; padding:.5rem 1rem; font-size:.85rem; font-weight:600; }
.keyword-tag { display: inline-block; background: linear-gradient(135deg, rgba(46,109,180,.16), rgba(212,175,55,.16));
border: 1px solid rgba(46,109,180,.4); padding: 6px 14px; border-radius: 30px; margin: 3px; font-size: .88rem; font-weight: 700; }
.newfeat { background: rgba(46,109,180,.08); border:1px solid rgba(46,109,180,.3); border-radius:12px; padding:.7rem 1rem; margin:.4rem 0; display:flex; align-items:center; gap:10px; font-weight:600; }
.bc-wrap { display:flex; align-items:flex-end; gap:10px; padding:16px 12px 8px;
background:rgba(128,128,128,.06); border:1px solid rgba(128,128,128,.18); border-radius:16px; margin:1rem 0; }
.bc-col { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; gap:6px; min-width:0; }
.bc-bar { width:70%; max-width:46px; border-radius:8px 8px 4px 4px;
background:linear-gradient(180deg,#4C9AFF,#1B3B6F); box-shadow:0 4px 12px rgba(46,109,180,.35); }
.bc-lbl { font-size:.7rem; opacity:.6; }
section.main [data-testid="stVerticalBlock"] { animation: fadeUp .3s ease both; }
@keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes fadeUp { from{opacity:0; transform:translateY(14px)} to{opacity:1; transform:none} }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg,#1B3B6F,#2E6DB4); border-radius: 10px; }
@media (max-width: 768px) {
.fd-grid { grid-template-columns:1fr; } .g-stats { flex-wrap:wrap; } .g-stat { flex:1 1 45%; }
.main-header { padding:1.6rem 1rem; } .g-cta { padding:2rem 1.4rem; } .claude-hello .big { font-size:1.7rem; }
}
</style>
"""


# ═══════════════════════════════════════════════════════════════
# APP CSS — Design system unifié
# ═══════════════════════════════════════════════════════════════

APP_CSS = """
<style>
:root {
    --vs-primary: #2E6DB4;
    --vs-primary-dark: #16345F;
    --vs-primary-soft: #4C9AFF;
    --vs-gold: #D4AF37;
    --vs-ease: cubic-bezier(.16,1,.3,1);
}
section.main > div.block-container,
div[data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: .7rem !important;
    padding-bottom: 4rem !important;
}
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(128,128,128,.14) !important;
    box-shadow: 8px 0 40px rgba(0,0,0,.06) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] .stButton > button {
    min-height: 46px !important;
    border-radius: 13px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    box-shadow: none !important;
    font-weight: 700 !important;
    justify-content: flex-start !important;
    text-align: left !important;
    transition: transform .25s var(--vs-ease), background .25s ease, border-color .25s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateX(3px) !important;
    background: rgba(46,109,180,.08) !important;
    border-color: rgba(46,109,180,.16) !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(46,109,180,.20), rgba(46,109,180,.07)) !important;
    border-color: rgba(46,109,180,.30) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.10), 0 8px 24px rgba(46,109,180,.09) !important;
}
.stButton > button, .stDownloadButton > button {
    min-height: 44px !important;
    border-radius: 13px !important;
    padding: .68rem 1.2rem !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    background: linear-gradient(135deg, var(--vs-primary-dark), var(--vs-primary)) !important;
    color: #fff !important;
    font-weight: 800 !important;
    box-shadow: 0 8px 24px rgba(46,109,180,.20), inset 0 1px 0 rgba(255,255,255,.10) !important;
    transition: transform .30s var(--vs-ease), box-shadow .30s ease, filter .30s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-3px) !important;
    filter: brightness(1.06);
    box-shadow: 0 16px 34px rgba(46,109,180,.28), inset 0 1px 0 rgba(255,255,255,.12) !important;
}
.stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(-1px) scale(.985) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    border-radius: 14px !important;
    min-height: 46px !important;
    padding: .75rem 1rem !important;
    border: 1px solid rgba(128,128,128,.22) !important;
    box-shadow: 0 5px 20px rgba(15,26,46,.05) !important;
    transition: border-color .25s ease, box-shadow .25s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--vs-primary) !important;
    box-shadow: 0 0 0 4px rgba(46,109,180,.10), 0 12px 30px rgba(46,109,180,.10) !important;
}
.main-header {
    position: relative;
    overflow: hidden;
    border-radius: 30px !important;
    padding: clamp(2rem,5vw,4rem) clamp(1.2rem,4vw,3rem) !important;
    margin: .4rem 0 2.2rem !important;
    background:
        radial-gradient(700px 300px at 8% -20%, rgba(76,154,255,.38), transparent 65%),
        radial-gradient(600px 280px at 92% -15%, rgba(212,175,55,.20), transparent 65%),
        linear-gradient(135deg, #08111F 0%, #102747 48%, #2E6DB4 100%) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    box-shadow: 0 30px 80px rgba(11,31,58,.30), inset 0 1px 0 rgba(255,255,255,.10) !important;
    animation: vsHeroGradient 12s ease infinite;
}
.main-header::before {
    content: ""; position: absolute; width: 320px; height: 320px;
    top: -180px; left: 50%; transform: translateX(-50%);
    border-radius: 50%; background: rgba(255,255,255,.08);
    filter: blur(70px); pointer-events: none;
}
.hbadge {
    display: inline-flex; align-items: center; padding: 7px 14px;
    border-radius: 999px; background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(12px);
    color: #fff !important; font-size: .76rem; font-weight: 700;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
}
.hero-badges { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 1.1rem; }
.vs-ic { display: inline-flex; align-items: center; margin-right: 9px; vertical-align: -3px; }
.lnav-brand { display: flex; align-items: center; gap: 9px; font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.15rem; }
.g-chip {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 12px; border-radius: 999px;
    background: linear-gradient(135deg, rgba(46,109,180,.18), rgba(212,175,55,.14));
    border: 1px solid rgba(46,109,180,.35);
    color: #E2E8F0 !important; font-weight: 700; font-size: .78rem;
    margin: 3px; letter-spacing: .02em;
}
div[data-testid="stColumn"] { height: auto !important; align-self: flex-start !important; }
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] { height: auto !important; }
.vs-feat-grid, .vs-testi-grid, .vs-value-grid, .vs-team-grid {
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .85rem; margin-top: 1rem; align-items: start;
}
.vs-feat {
    position: relative; overflow: hidden; border-radius: 20px;
    padding: 1.15rem 1.15rem !important;
    background: #FFFFFF !important;
    border: 1px solid rgba(15,26,46,.10) !important;
    text-align: left; height: auto !important; min-height: unset !important;
    box-shadow: 0 4px 20px rgba(15,26,46,.06) !important;
    transition: transform .4s var(--vs-ease), border-color .35s ease, box-shadow .35s ease;
}
.vs-feat:hover {
    transform: translateY(-5px);
    border-color: rgba(46,109,180,.35) !important;
    box-shadow: 0 20px 50px rgba(46,109,180,.18) !important;
}
.vs-feat-ico {
    width: 40px; height: 40px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: .75rem; color: #fff !important;
    box-shadow: 0 10px 22px rgba(46,109,180,.22);
}
.vs-feat-title {
    font-family: 'Sora', sans-serif; font-weight: 800;
    color: #0F1A2E !important; font-size: .98rem !important;
    margin-bottom: .3rem !important; letter-spacing: -.02em;
}
.vs-feat-desc { color: #4A5A7A !important; font-size: .84rem !important; line-height: 1.55 !important; }
.vs-feat-tag {
    position: absolute; top: 12px; right: 12px;
    font-size: .58rem; font-weight: 800;
    letter-spacing: .06em; text-transform: uppercase;
    padding: 3px 8px; border-radius: 999px;
    background: rgba(16,185,129,.15); color: #059669 !important;
    border: 1px solid rgba(16,185,129,.35); z-index: 2;
}
.vs-testi {
    position: relative; border-radius: 20px; padding: 1.2rem !important;
    background: #FFFFFF !important;
    border: 1px solid rgba(15,26,46,.10) !important;
    height: auto !important;
    box-shadow: 0 4px 20px rgba(15,26,46,.06) !important;
    transition: transform .35s ease, border-color .3s ease, box-shadow .35s ease;
}
.vs-testi:hover {
    transform: translateY(-4px);
    border-color: rgba(212,175,55,.5) !important;
    box-shadow: 0 20px 50px rgba(212,175,55,.15) !important;
}
.vs-testi-stars { display: flex; gap: 2px; margin-bottom: .75rem; }
.vs-testi-quote { color: #0F1A2E !important; font-size: .9rem; line-height: 1.65; margin-bottom: .9rem; font-style: italic; }
.vs-testi-author { display: flex; align-items: center; gap: 10px; padding-top: .8rem; border-top: 1px solid rgba(15,26,46,.10); }
.vs-testi-avatar {
    width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    color: #fff !important; font-weight: 800; font-size: .78rem; font-family: 'Sora', sans-serif;
}
.vs-testi-author b { color: #0F1A2E !important; font-size: .86rem; display: block; }
.vs-testi-author small { color: #4A5A7A !important; font-size: .72rem; }
.vs-value {
    position: relative; overflow: hidden; border-radius: 20px;
    padding: 1.2rem !important; background: #FFFFFF !important;
    border: 1px solid rgba(15,26,46,.10) !important;
    text-align: left; height: auto !important;
    box-shadow: 0 4px 20px rgba(15,26,46,.06) !important;
    transition: transform .35s ease, border-color .3s ease, box-shadow .35s ease;
}
.vs-value:hover {
    transform: translateY(-5px);
    border-color: rgba(46,109,180,.35) !important;
    box-shadow: 0 20px 50px rgba(46,109,180,.15) !important;
}
.vs-value-ico {
    width: 38px !important; height: 38px !important; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: .7rem !important; color: #fff !important;
    background: linear-gradient(135deg, #1B3B6F, #2E6DB4) !important;
    box-shadow: 0 8px 18px rgba(46,109,180,.20) !important;
}
.vs-value h4 { font-family: 'Sora', sans-serif; font-weight: 800; color: #0F1A2E !important; font-size: 1rem !important; margin-bottom: .35rem !important; }
.vs-value p { color: #4A5A7A !important; font-size: .86rem !important; line-height: 1.6 !important; }
.vs-team {
    text-align: center; border-radius: 20px; padding: 1.3rem 1rem !important;
    background: #FFFFFF !important;
    border: 1px solid rgba(15,26,46,.10) !important;
    height: auto !important;
    box-shadow: 0 4px 20px rgba(15,26,46,.06) !important;
    transition: transform .35s ease, box-shadow .35s ease;
}
.vs-team:hover { transform: translateY(-5px); box-shadow: 0 20px 50px rgba(46,109,180,.12) !important; }
.vs-team-avatar {
    width: 64px; height: 64px; border-radius: 50%; margin: 0 auto .8rem;
    display: flex; align-items: center; justify-content: center;
    color: #fff !important; font-weight: 800; font-size: 1.15rem;
    font-family: 'Sora', sans-serif;
    box-shadow: 0 12px 28px rgba(46,109,180,.22);
}
.vs-team h4 { font-family: 'Sora', sans-serif; font-weight: 800; color: #0F1A2E !important; font-size: 1rem !important; }
.vs-team .role { color: #2E6DB4 !important; font-size: .78rem; font-weight: 700; margin: .25rem 0 .5rem; }
.vs-team p { color: #4A5A7A !important; font-size: .84rem; line-height: 1.55; }
.vs-insight {
    border-radius: 18px; padding: .9rem;
    background: #FFFFFF !important;
    border: 1px solid rgba(15,26,46,.10) !important;
    color: #0F1A2E !important;
    box-shadow: 0 4px 20px rgba(15,26,46,.06) !important;
    transition: transform .25s ease;
}
.vs-insight:hover { transform: translateY(-3px); }
.vs-insight b { display: block; color: #0F1A2E !important; font-size: .88rem; margin-bottom: .35rem; }
.vs-insight span { color: #4A5A7A !important; font-size: .82rem; line-height: 1.5; }
.vs-section-card {
    display: flex; gap: 14px; padding: 1rem 1.1rem; margin: .8rem 0;
    border-radius: 20px; background: #FFFFFF !important;
    border: 1px solid rgba(15,26,46,.10) !important;
    box-shadow: 0 8px 26px rgba(15,26,46,.06) !important;
    color: #0F1A2E !important;
    transition: transform .25s ease, box-shadow .25s ease;
}
.vs-section-card:hover { transform: translateX(3px); box-shadow: 0 14px 32px rgba(15,26,46,.10) !important; }
.vs-section-num {
    width: 38px; height: 38px; flex-shrink: 0; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #2E6DB4, #34D399);
    color: #FFFFFF !important; font-weight: 900; font-family: 'Sora', sans-serif;
}
.vs-section-text { color: #0F1A2E !important; line-height: 1.75; font-size: .96rem; }

/* ═══ Adaptation THÈME SOMBRE pour les cartes claires ═══ */
html[data-theme="dark"] .vs-feat,
html[data-theme="dark"] .vs-testi,
html[data-theme="dark"] .vs-value,
html[data-theme="dark"] .vs-team,
html[data-theme="dark"] .vs-insight,
html[data-theme="dark"] .vs-section-card,
body.dark .vs-feat,
body.dark .vs-testi,
body.dark .vs-value,
body.dark .vs-team,
body.dark .vs-insight,
body.dark .vs-section-card {
    background: rgba(255,255,255,.04) !important;
    border-color: rgba(255,255,255,.10) !important;
}
html[data-theme="dark"] .vs-feat-title,
html[data-theme="dark"] .vs-value h4,
html[data-theme="dark"] .vs-team h4,
html[data-theme="dark"] .vs-insight b,
html[data-theme="dark"] .vs-section-text,
html[data-theme="dark"] .vs-testi-quote,
body.dark .vs-feat-title,
body.dark .vs-value h4,
body.dark .vs-team h4,
body.dark .vs-insight b,
body.dark .vs-section-text,
body.dark .vs-testi-quote {
    color: #F8FAFC !important;
}
html[data-theme="dark"] .vs-feat-desc,
html[data-theme="dark"] .vs-value p,
html[data-theme="dark"] .vs-team p,
html[data-theme="dark"] .vs-insight span,
html[data-theme="dark"] .vs-testi-author small,
body.dark .vs-feat-desc,
body.dark .vs-value p,
body.dark .vs-team p,
body.dark .vs-insight span,
body.dark .vs-testi-author small {
    color: rgba(203,213,225,.85) !important;
}

.g-card {
    width: 100% !important; height: auto !important;
    padding: 1.8rem 1.6rem !important; align-self: flex-start !important;
    display: flex !important; flex-direction: column !important;
    border-radius: 20px; border: 1px solid rgba(128,128,128,.2);
}
.g-card .g-ico { margin-bottom: .9rem; }
.g-card h4 { font-family: 'Sora', sans-serif; font-size: 1.1rem; margin-bottom: .7rem; font-weight: 700; }
.g-card p { margin-bottom: .5rem; line-height: 1.6; font-size: .93rem; }
.kpi-card {
    position: relative; overflow: hidden; border-radius: 20px !important;
    padding: 1.5rem 1.35rem;
    background: linear-gradient(145deg, rgba(46,109,180,.09), rgba(212,175,55,.035));
    border: 1px solid rgba(46,109,180,.16);
    box-shadow: 0 4px 16px rgba(15,26,46,.06);
    transition: transform .35s var(--vs-ease), box-shadow .35s ease;
}
.kpi-card:hover { transform: translateY(-6px); box-shadow: 0 24px 60px rgba(46,109,180,.16); }
.kpi-icon {
    width: 48px; height: 48px; border-radius: 12px;
    background: linear-gradient(135deg, #2E6DB4, #F5C542);
    display: flex; align-items: center; justify-content: center;
    color: #fff !important; margin-bottom: .8rem;
    box-shadow: 0 10px 24px rgba(46,109,180,.18);
}
.kpi-value { font-family: 'Sora', sans-serif !important; font-size: clamp(1.7rem,3vw,2.3rem) !important; font-weight: 800 !important; margin: .4rem 0; }
.kpi-label { font-size: .85rem; opacity: .7; margin-bottom: .3rem; }
.kpi-trend { display: inline-flex; align-items: center; gap: 4px; font-size: .85rem; font-weight: 700; padding: 4px 10px; border-radius: 8px; }
.kpi-trend.up { background: rgba(34,197,94,.12); color: #16a34a; }
.kpi-trend.down { background: rgba(239,68,68,.12); color: #dc2626; }
.hist-card, .note-card, .notif-card {
    background: rgba(128,128,128,.045) !important;
    border: 1px solid rgba(128,128,128,.14) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 18px rgba(15,26,46,.035) !important;
    transition: transform .35s var(--vs-ease), box-shadow .35s ease;
}
.hist-card:hover, .note-card:hover, .notif-card:hover {
    transform: translateX(4px); box-shadow: 0 12px 30px rgba(46,109,180,.09) !important;
}
.hist-card { display: flex; align-items: center; gap: 12px; border-left: 4px solid #2E6DB4; padding: 12px 16px; margin: 10px 0; }
.hist-left { display: flex; align-items: center; gap: 12px; flex: 1; }
.hist-ico {
    flex-shrink: 0; width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, #1B3B6F, #2E6DB4);
    color: #fff !important; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 24px rgba(46,109,180,.18);
}
.note-card {
    display: flex; gap: 14px; align-items: flex-start;
    border-left: 4px solid var(--vs-primary) !important;
    padding: 14px 16px; margin: 10px 0;
}
.note-num {
    flex-shrink: 0; width: 34px; height: 34px; border-radius: 10px;
    background: linear-gradient(135deg, #1B3B6F, #2E6DB4);
    color: #fff !important; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Sora', sans-serif;
    box-shadow: 0 10px 24px rgba(46,109,180,.18);
}
.note-text { line-height: 1.7; font-size: .95rem; }
.notif-card { display: flex; gap: 12px; align-items: flex-start; padding: 14px 16px; margin: 10px 0; }
.notif-ico {
    flex-shrink: 0; width: 38px; height: 38px; border-radius: 12px;
    background: linear-gradient(135deg, #1B3B6F, #2E6DB4);
    color: #fff !important; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 24px rgba(46,109,180,.18);
}
.pipe-card {
    background: linear-gradient(160deg, rgba(46,109,180,.10), rgba(212,175,55,.06));
    border: 1px solid rgba(46,109,180,.3);
    border-radius: 16px; padding: .8rem 1rem; margin-bottom: .6rem;
}
.pipe-title { display: flex; align-items: center; gap: 8px; font-weight: 800; }
.pipe-row { display: flex; align-items: center; gap: 10px; padding: .5rem .2rem; border-bottom: 1px dashed rgba(128,128,128,.25); }
.pipe-row:last-child { border-bottom: none; }
.pipe-lbl { flex: 1; font-weight: 600; }
.pipe-ok { color: #16a34a; font-weight: 700; display: flex; align-items: center; gap: 4px; }
.pipe-run { color: #2E6DB4; font-weight: 700; }
.pipe-wait { opacity: .5; }
.qa-box { background: rgba(46,109,180,.08); border: 1px solid rgba(46,109,180,.3); border-radius: 14px; padding: 1rem 1.2rem; margin: .6rem 0; }
.q-item { background: rgba(212,175,55,.08); border: 1px solid rgba(212,175,55,.3); border-radius: 12px; padding: 10px 14px; margin: 8px 0; font-weight: 600; }
.pay-panel {
    background: linear-gradient(160deg, rgba(46,109,180,.14), rgba(212,175,55,.06));
    border: 1px solid rgba(46,109,180,.45);
    border-radius: 18px; padding: 1.4rem 1.6rem; margin: 1rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,.15);
}
.pay-title { font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.2rem; display: flex; align-items: center; gap: 8px; }
.pay-price { font-family: 'Sora', sans-serif; font-size: 2rem; font-weight: 800; margin: .4rem 0; }
.pay-price span { font-size: 1rem; opacity: .7; font-weight: 600; }
.pay-steps { margin: .6rem 0 0 1.2rem; line-height: 1.9; }
.pill-trust {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; border-radius: 999px;
    background: rgba(128,128,128,.08); border: 1px solid rgba(128,128,128,.18);
    font-size: .8rem; font-weight: 700; opacity: .85;
}
[data-testid="stColumn"] > div:has(.pcard) {
    position: relative; overflow: visible !important;
    border-radius: 26px !important;
    border: 1px solid rgba(128,128,128,.16) !important;
    background: linear-gradient(180deg, rgba(128,128,128,.045), rgba(128,128,128,.01)) !important;
    padding: 1.9rem 1.5rem 1.7rem !important;
    transition: transform .4s var(--vs-ease), box-shadow .4s ease, border-color .4s ease !important;
}
[data-testid="stColumn"] > div:has(.pcard):hover {
    transform: translateY(-8px) !important;
    box-shadow: 0 30px 70px rgba(15,26,46,.16) !important;
    border-color: rgba(46,109,180,.28) !important;
}
[data-testid="stColumn"] > div:has(.pcard-hl) {
    border: 1.5px solid rgba(212,175,55,.55) !important;
    background: linear-gradient(180deg, rgba(212,175,55,.08), rgba(128,128,128,.01)) !important;
    box-shadow: 0 26px 64px rgba(212,175,55,.20) !important;
    transform: translateY(-6px) scale(1.015) !important;
    z-index: 3;
}
[data-testid="stColumn"] > div:has(.pcard-hl):hover { transform: translateY(-13px) scale(1.02) !important; }
.pc-ribbon {
    position: absolute; top: -14px; left: 50%; transform: translateX(-50%);
    white-space: nowrap;
    background: linear-gradient(135deg, #D4AF37, #F0D488);
    color: #0B1F3A !important;
    font-family: 'Sora', sans-serif; font-weight: 800; font-size: .72rem;
    letter-spacing: .07em; padding: 6px 16px; border-radius: 999px;
    box-shadow: 0 10px 22px rgba(212,175,55,.42);
    display: flex; align-items: center; gap: 6px; z-index: 5;
}
.pc-icon-wrap {
    width: 52px; height: 52px; border-radius: 15px;
    display: flex; align-items: center; justify-content: center;
    margin: .2rem auto .9rem; color: #fff !important;
    background: linear-gradient(135deg, var(--pc-accent,#2E6DB4), var(--pc-accent2,#4C9AFF));
    box-shadow: 0 12px 28px rgba(46,109,180,.28);
}
.pcard { text-align: center; }
.pc-name { font-family: 'Sora', sans-serif !important; font-weight: 800 !important; font-size: 1.32rem !important; margin-bottom: .15rem !important; }
.pc-price { font-family: 'Sora', sans-serif !important; font-weight: 800 !important; display: flex !important; align-items: baseline; justify-content: center; gap: 2px; }
.pc-price .cur { font-size: 1.05rem; opacity: .6; font-weight: 800; margin-right: 1px; }
.pc-tag { min-height: 2.6em; }
.pc-sub { font-size: .78rem; opacity: .7; margin: .3rem 0 1rem; }
.pc-sep { border-top: 1px solid rgba(128,128,128,.28); margin: 1.2rem 0; }
.pc-plus { font-weight: 700; margin: 0 0 .6rem; font-size: .9rem; }
.pfeat-group-label {
    text-align: left; font-size: .68rem; font-weight: 800;
    letter-spacing: .09em; text-transform: uppercase;
    opacity: .5; margin: 1.1rem 0 .5rem;
    display: flex; align-items: center; gap: 5px;
}
.pfeat { display: flex; align-items: flex-start; gap: 9px; margin: .55rem 0; font-size: .9rem; line-height: 1.5; text-align: left; }
.pfeat svg { margin-right: 0; margin-top: 3px; flex-shrink: 0; opacity: .8; }
.pfeat.is-new {
    background: rgba(16,185,129,.08);
    border: 1px solid rgba(16,185,129,.22);
    border-radius: 11px; padding: 7px 10px !important; margin: .4rem 0 !important;
}
.pfeat.is-new svg { color: #10B981; }
.new-tag {
    display: inline-block; font-size: .6rem; font-weight: 800;
    letter-spacing: .05em; text-transform: uppercase;
    background: #10B981; color: #fff !important;
    padding: 2px 7px; border-radius: 999px;
    margin-left: 6px; vertical-align: 1px;
}
div[data-testid="stVerticalBlock"]:has(.pcard-hl) .stButton > button {
    background: linear-gradient(135deg, #D4AF37, #F0D488) !important;
    color: #0B1F3A !important; font-weight: 900 !important;
    box-shadow: 0 16px 36px rgba(212,175,55,.35) !important;
}
[data-testid="stForm"] {
    background: rgba(128,128,128,.035) !important;
    border: 1px solid rgba(128,128,128,.16) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    box-shadow: 0 10px 35px rgba(15,26,46,.05);
    backdrop-filter: blur(14px);
}
[data-testid="stTabs"] [role="tablist"] { gap: 7px; padding-bottom: 4px; border-bottom: 1px solid rgba(128,128,128,.16); }
[data-testid="stTabs"] [role="tab"] { border-radius: 11px !important; padding: .62rem 1rem; font-weight: 700; transition: all .25s ease; }
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, var(--vs-primary-dark), var(--vs-primary)) !important;
    color: #fff !important; border-radius: 11px !important;
    box-shadow: 0 8px 20px rgba(46,109,180,.16);
}
[data-testid="stMetric"] {
    background: rgba(128,128,128,.08);
    border: 1px solid rgba(128,128,128,.18);
    border-radius: 16px; padding: 1rem 1.2rem;
    backdrop-filter: blur(8px);
}
.g-cta {
    position: relative; overflow: hidden;
    border-radius: 28px !important; margin: 3rem 0 1.5rem;
    padding: 3.4rem 2.8rem;
    background:
        radial-gradient(500px 220px at 85% 0%, rgba(76,154,255,.28), transparent 65%),
        linear-gradient(135deg, #07111F, #16345F 58%, #2E6DB4);
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 28px 80px rgba(4,16,31,.45);
}
.g-cta h3 { color: #fff !important; font-family: 'Sora', sans-serif; font-size: 2rem; font-weight: 800; margin-bottom: .6rem; }
.g-cta p { color: rgba(255,255,255,.85) !important; max-width: 60ch; }
.g-cta-badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 1.2rem; }
.g-cta-badges span {
    background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.18);
    padding: 7px 14px; border-radius: 999px;
    font-size: .8rem; font-weight: 600; color: #fff !important;
}
.footer-dark {
    background: linear-gradient(145deg, #080E18, #0C1728) !important;
    color: #cbd5e1;
    border-radius: 24px !important;
    border: 1px solid rgba(255,255,255,.08);
    box-shadow: 0 24px 60px rgba(4,16,31,.25);
    margin-top: 3rem; padding: 2.6rem 2.2rem 1.4rem;
}
.fd-grid { display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr; gap: 2rem; }
.fd-logo { display: flex; align-items: center; gap: 9px; color: #fff; font-size: 1.15rem; font-family: 'Sora', sans-serif; margin-bottom: .9rem; }
.footer-dark h5 { color: #fff; font-size: 1rem; margin-bottom: .8rem; font-family: 'Sora', sans-serif; font-weight: 700; }
.footer-dark ul { list-style: none; padding: 0; margin: 0; }
.footer-dark li { padding: .3rem 0; font-size: .92rem; color: #cbd5e1; }
.footer-dark p { color: #cbd5e1; font-size: .92rem; line-height: 1.6; }
.fd-copy { border-top: 1px solid rgba(255,255,255,.12); margin-top: 2rem; padding-top: 1rem; text-align: center; font-size: .85rem; color: #94a3b8; }
.fd-social {
    width: 40px; height: 40px; border-radius: 12px;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.15);
    display: inline-flex; align-items: center; justify-content: center;
    color: #cbd5e1 !important;
    transition: all .3s var(--vs-ease);
}
.fd-social:hover { transform: translateY(-3px); background: rgba(46,109,180,.25) !important; border-color: rgba(76,154,255,.35) !important; color: #fff !important; }
.fd-input { flex: 1; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.15); border-radius: 999px; padding: 10px 16px; color: #fff; outline: none; font-size: .9rem; }
.fd-input::placeholder { color: rgba(203,213,225,.55); }
.fd-send { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, #1B3B6F, #2E6DB4); display: inline-flex; align-items: center; justify-content: center; color: #fff !important; flex-shrink: 0; transition: all .3s ease; }
.fd-send:hover { transform: scale(1.08); box-shadow: 0 8px 24px rgba(46,109,180,.4); }
.fd-link { color: #cbd5e1 !important; text-decoration: none; transition: color .25s ease; }
.fd-link:hover { color: #fff !important; text-decoration: underline; }
.user-card { position: relative; padding: .7rem .9rem; border-radius: 14px; border: 1px solid rgba(128,128,128,.22); background: rgba(128,128,128,.06); z-index: 10; transition: all .25s ease; cursor: pointer; }
.user-row { display: flex; align-items: center; gap: 10px; }
.chev { opacity: .5; display: flex; }
.avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #1B3B6F, #2E6DB4); color: #fff !important; font-weight: 800; display: flex; align-items: center; justify-content: center; font-family: 'Sora', sans-serif; font-size: .82rem; flex-shrink: 0; overflow: hidden; box-shadow: 0 10px 24px rgba(46,109,180,.18); }
.avatar img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
.uname { font-weight: 700; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 8px; font-size: .95rem; }
.tier-chip { font-size: .6rem; font-weight: 800; padding: 2px 8px; border-radius: 6px; background: rgba(46,109,180,.18); border: 1px solid rgba(46,109,180,.4); letter-spacing: .06em; white-space: nowrap; }
.big-avatar { width: 84px; height: 84px; border-radius: 50%; object-fit: cover; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; background: linear-gradient(135deg, #1B3B6F, #2E6DB4); color: #fff !important; font-weight: 800; font-family: 'Sora', sans-serif; }
.qbrand { font-family: 'Sora', sans-serif; font-size: 1.3rem; font-weight: 800; padding: .2rem .6rem 1rem; letter-spacing: -.02em; display: flex; align-items: center; }
.qcap { text-transform: uppercase; font-size: .68rem; letter-spacing: .09em; opacity: .55; margin: .9rem .6rem .3rem; font-weight: 700; }
.wizard-steps { display: flex; align-items: center; justify-content: center; gap: 8px; margin: 1.4rem 0 2rem; }
.wstep { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(128,128,128,.12); color: #8fa3c8; font-weight: 800; border: 2px solid rgba(128,128,128,.3); font-family: 'Sora', sans-serif; }
.wstep.active { background: linear-gradient(135deg, #D4AF37, #F0D488); color: #0B1F3A; border-color: #D4AF37; }
.wstep.done { background: linear-gradient(135deg, #1B3B6F, #2E6DB4); color: #fff; border-color: #2E6DB4; }
.wline { flex: 0 0 46px; height: 2px; background: rgba(128,128,128,.3); }
.wline.done { background: #2E6DB4; }
.wizard-card { max-width: 560px; margin: 0 auto; }
details[class*="vs-faq"] {
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 16px; margin-bottom: .6rem;
    background: rgba(255,255,255,.025);
    overflow: hidden;
    transition: border-color .3s ease, background .3s ease;
}
details[class*="vs-faq"]:hover { border-color: rgba(96,165,250,.28); }
summary[class*="vs-faq-q"] {
    display: flex; align-items: center; gap: 12px;
    padding: 1rem 1.2rem; cursor: pointer;
    font-weight: 700; color: #F8FAFC !important; font-size: .94rem;
    list-style: none;
}
summary[class*="vs-faq-q"]::-webkit-details-marker { display: none; }
summary[class*="vs-faq-q"]::after {
    content: "+"; margin-left: auto; font-size: 1.3rem;
    color: #60A5FA !important;
    transition: transform .3s ease; font-weight: 400;
}
details[open] summary[class*="vs-faq-q"]::after { transform: rotate(45deg); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #1B3B6F, #2E6DB4); border-radius: 10px; }
.stProgress > div > div > div { background: linear-gradient(90deg, #D4AF37, #F0D488) !important; }
.stAlert { border-radius: 14px !important; backdrop-filter: blur(8px); }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid rgba(128,128,128,.2); }
@keyframes vsHeroGradient { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes vsShine { 0% { transform: translateX(-100%); } 45%,100% { transform: translateX(100%); } }
@keyframes vsFadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
.kpi-card, .feat-card, .hist-card, .note-card, .notif-card, .pipe-card { animation: vsFadeUp .5s var(--vs-ease) both; }
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
@media (max-width: 900px) {
    .vs-feat-grid, .vs-testi-grid, .vs-value-grid, .vs-team-grid { grid-template-columns: 1fr; }
    .fd-grid { grid-template-columns: 1fr; gap: 1.5rem; }
    [data-testid="stColumn"] > div:has(.pcard-hl) { transform: none !important; }
}
@media (max-width: 768px) {
    section.main > div.block-container, div[data-testid="stMainBlockContainer"] { padding-left: .75rem !important; padding-right: .75rem !important; }
    .main-header { border-radius: 20px !important; padding: 2rem 1rem !important; }
    .feat-card { min-height: 155px; padding: 1.25rem 1rem !important; }
    .g-cta { padding: 2rem 1.25rem !important; border-radius: 20px !important; }
    .footer-dark { border-radius: 18px !important; }
}
@media (max-width: 480px) {
    .main-header { padding: 1.6rem .85rem !important; }
    .hist-card, .note-card, .notif-card { padding: 11px 12px !important; }
    .stButton > button, .stDownloadButton > button { min-height: 42px !important; padding: .6rem .9rem !important; }
}

/* ═══ Pleine largeur ═══ */
section.main > div.block-container,
div[data-testid="stMainBlockContainer"] {
    max-width: 100% !important; width: 100% !important;
    padding-left: 0.5rem !important; padding-right: 0.5rem !important;
    padding-top: 0.5rem !important; padding-bottom: 4rem !important;
}
div[data-testid="stColumn"] > div { padding-left: 0 !important; padding-right: 0 !important; }
.main-header, .vs-home-hero, .vs-hero-mockup, .g-cta, .footer-dark { max-width: 100% !important; width: 100% !important; }

/* ═══ Navbar mobile responsive ═══ */
@media (max-width: 768px) {
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) {
        padding: .4rem .5rem !important; margin: 0 !important; border-radius: 0 !important;
        overflow-x: auto !important; white-space: nowrap !important; scrollbar-width: none !important;
    }
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero))::-webkit-scrollbar { display: none !important; }
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stHorizontalBlock"] {
        display: flex !important; flex-wrap: nowrap !important; gap: .3rem !important; min-width: max-content !important;
    }
    .lnav-brand { font-size: 1rem !important; gap: 5px !important; }
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button,
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stBaseButton-primary"] {
        min-height: 36px !important; padding: .35rem .7rem !important; font-size: .78rem !important;
        border-radius: 999px !important; white-space: nowrap !important;
    }
    div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stColumn"]:last-child .stButton > button {
        min-width: 36px !important; padding: .35rem !important; font-size: 1rem !important;
    }
}

/* ═══════════════════════════════════════════════════════════
   NAVBAR SAAS MODERNE + DARK MODE — CORRIGÉ
   ═══════════════════════════════════════════════════════════ */

/* Navbar container — LIGHT */
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) {
    position: sticky !important; top: 0 !important; z-index: 9999 !important;
    background: rgba(255,255,255,.72) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border-bottom: 1px solid rgba(15,26,46,.06) !important;
    box-shadow: 0 4px 24px rgba(15,26,46,.04) !important;
    border-radius: 0 !important; padding: .6rem 1.5rem !important; margin: 0 0 1.5rem !important;
}

/* Navbar container — DARK */
html[data-theme="dark"] div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)),
body.dark div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) {
    background: rgba(10,16,25,.85) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border-bottom: 1px solid rgba(255,255,255,.08) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,.4) !important;
}

/* Brand — LIGHT */
.lnav-brand { display: flex !important; align-items: center !important; gap: 10px !important; font-family: 'Sora', sans-serif !important; font-weight: 800 !important; text-decoration: none !important; }
.lnav-brand-text { display: flex !important; align-items: baseline !important; gap: 2px !important; font-size: 1.18rem !important; letter-spacing: -.03em !important; }
.lnav-brand-name { color: #0F1A2E !important; font-weight: 800 !important; }
html[data-theme="dark"] .lnav-brand-name, body.dark .lnav-brand-name { color: #F8FAFC !important; }
.lnav-brand-ai { background: linear-gradient(92deg, #2E6DB4, #10B981); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; font-size: 1.18rem !important; }

/* Liens navbar — LIGHT */
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) {
    background: transparent !important; border: none !important; box-shadow: none !important;
    border-radius: 999px !important; font-weight: 600 !important; font-size: .94rem !important;
    color: #4A5A7A !important; padding: .5rem 1rem !important; min-height: 40px !important;
    transition: all .25s cubic-bezier(.16,1,.3,1) !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) p,
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) span {
    color: #4A5A7A !important; font-weight: 600 !important;
}
html[data-theme="dark"] div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) p,
html[data-theme="dark"] div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) span,
body.dark div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) p,
body.dark div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) span {
    color: rgba(203,213,225,.9) !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]):hover {
    background: rgba(46,109,180,.08) !important; color: #0F1A2E !important; transform: none !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]):hover p,
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]):hover span {
    color: #2E6DB4 !important;
}

/* CTA bouton navbar */
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #1B3B6F 0%, #2E6DB4 100%) !important;
    color: #FFFFFF !important; border: 1px solid rgba(96,165,250,.35) !important;
    box-shadow: 0 8px 24px rgba(46,109,180,.28), inset 0 1px 0 rgba(255,255,255,.15) !important;
    border-radius: 999px !important; font-weight: 800 !important;
    padding: .55rem 1.3rem !important; min-height: 42px !important; font-size: .94rem !important;
    transition: all .3s cubic-bezier(.16,1,.3,1) !important; position: relative !important; overflow: hidden !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stBaseButton-primary"]::before {
    content: "" !important; position: absolute !important;
    top: 0 !important; left: -100% !important; width: 100% !important; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.3), transparent) !important;
    transition: left .6s ease !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stBaseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 32px rgba(46,109,180,.4), inset 0 1px 0 rgba(255,255,255,.2) !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stBaseButton-primary"]:hover::before { left: 100% !important; }

/* Bouton thème */
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stColumn"]:last-child .stButton > button {
    width: 42px !important; min-width: 42px !important; height: 42px !important; min-height: 42px !important;
    padding: 0 !important; border-radius: 50% !important;
    background: rgba(46,109,180,.08) !important; border: 1px solid rgba(46,109,180,.15) !important;
    font-size: 1.1rem !important; transition: all .3s ease !important;
}
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) [data-testid="stColumn"]:last-child .stButton > button:hover {
    background: rgba(46,109,180,.15) !important; transform: rotate(15deg) scale(1.05) !important;
}

/* ═══ FOND SOMBRE PROFOND — Correction du gris moyen ═══ */
html[data-theme="dark"] body,
html[data-theme="dark"] .stApp,
html[data-theme="dark"] div[data-testid="stAppViewContainer"],
html[data-theme="dark"] div[data-testid="stMain"],
html[data-theme="dark"] section.main,
html[data-theme="dark"] section.main > div.block-container,
html[data-theme="dark"] div[data-testid="stMainBlockContainer"],
body.dark, body.dark .stApp,
body.dark div[data-testid="stAppViewContainer"],
body.dark div[data-testid="stMain"],
body.dark section.main,
body.dark section.main > div.block-container,
body.dark div[data-testid="stMainBlockContainer"] {
    background-color: #05080F !important;
    color: #F8FAFC !important;
}
html[data-theme="dark"] section[data-testid="stSidebar"],
html[data-theme="dark"] section[data-testid="stSidebar"] > div,
body.dark section[data-testid="stSidebar"],
body.dark section[data-testid="stSidebar"] > div { background-color: #0A1019 !important; }
html[data-theme="dark"] header[data-testid="stHeader"],
body.dark header[data-testid="stHeader"] { background-color: transparent !important; }

/* Textes — lisibilité en dark */
html[data-theme="dark"] h1, html[data-theme="dark"] h2, html[data-theme="dark"] h3,
html[data-theme="dark"] h4, html[data-theme="dark"] h5, html[data-theme="dark"] h6,
html[data-theme="dark"] p, html[data-theme="dark"] span, html[data-theme="dark"] label,
body.dark h1, body.dark h2, body.dark h3, body.dark h4, body.dark h5, body.dark h6,
body.dark p, body.dark span, body.dark label { color: #F8FAFC !important; }
html[data-theme="dark"] .g-lead, html[data-theme="dark"] .vs-about-lead, html[data-theme="dark"] .g-step p,
body.dark .g-lead, body.dark .vs-about-lead, body.dark .g-step p { color: rgba(203,213,225,.85) !important; }

/* Wizard dark */
html[data-theme="dark"] .wizard-card, html[data-theme="dark"] .wizard-card *,
body.dark .wizard-card, body.dark .wizard-card * { color: #F8FAFC !important; }
html[data-theme="dark"] .wstep, body.dark .wstep {
    background: rgba(255,255,255,.08) !important;
    color: rgba(203,213,225,.9) !important;
    border-color: rgba(255,255,255,.2) !important;
}
html[data-theme="dark"] .wline, body.dark .wline { background: rgba(255,255,255,.15) !important; }
html[data-theme="dark"] [data-testid="stForm"], body.dark [data-testid="stForm"] {
    background: rgba(255,255,255,.03) !important;
    border-color: rgba(255,255,255,.10) !important;
}
html[data-theme="dark"] [data-testid="stTextInput"] input,
html[data-theme="dark"] [data-testid="stTextArea"] textarea,
html[data-theme="dark"] [data-testid="stNumberInput"] input,
html[data-theme="dark"] [data-testid="stSelectbox"] > div > div,
body.dark [data-testid="stTextInput"] input,
body.dark [data-testid="stTextArea"] textarea,
body.dark [data-testid="stNumberInput"] input,
body.dark [data-testid="stSelectbox"] > div > div {
    background: #0F1A2E !important;
    color: #F8FAFC !important;
    border-color: rgba(255,255,255,.15) !important;
}
html[data-theme="dark"] .g-h1, html[data-theme="dark"] .g-h2, html[data-theme="dark"] .g-kicker,
body.dark .g-h1, body.dark .g-h2, body.dark .g-kicker { color: #F8FAFC !important; }
</style>
"""


# ═══════════════════════════════════════════════════════════════
# CSS DYNAMIQUE — Basé sur les préférences utilisateur
# ═══════════════════════════════════════════════════════════════
def shade(hex_color, factor=0.55):
    """Assombrit une couleur hexadécimale d'un facteur donné.

    Args:
        hex_color: Couleur au format "#RRGGBB"
        factor: Facteur d'assombrissement (0.55 = assombrit de ~45%)

    Returns:
        Couleur hexadécimale assombrie
    """
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"

def custom_css():
    acc = st.session_state.get("cfg_accent", "#2E6DB4"); dark = shade(acc, 0.55)
    fs = st.session_state.get("cfg_font_size", 16); lh = st.session_state.get("cfg_line_height", 1.6)
    return f"""<style>
.stButton > button, .stDownloadButton > button {{ background: linear-gradient(135deg, {dark}, {acc}) !important; }}
.kpi-icon, .avatar, .hist-ico, .notif-ico, .note-num {{ background: linear-gradient(135deg, {dark}, {acc}) !important; }}
.bc-bar {{ background: linear-gradient(180deg, {acc}, {dark}) !important; }}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {{ background: {acc}26 !important; border-color: {acc} !important; }}
html body .stApp {{ font-size: {fs}px !important; }}
.note-text, .g-card p, .step-desc, .feat-text {{ line-height: {lh} !important; }}
</style>"""
