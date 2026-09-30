"""
VideoScribe AI — Premium theme
==============================
Drop-in replacement for BASE_CSS + the theme block in app.py.

Usage (app.py):
    from src.premium_theme import premium_css
    ...
    apply_theme(st.session_state.theme)
    st.markdown(premium_css(st.session_state.theme, st.session_state.cfg_font,
                            st.session_state.cfg_reduce_motion), unsafe_allow_html=True)
    st.markdown(custom_css(), unsafe_allow_html=True)   # accent utilisateur (inchangé)

Then DELETE the old `BASE_CSS = ...` string, the `st.markdown(BASE_CSS, ...)` call,
and the big `st.markdown(f\"\"\"<style> ... </style>\"\"\")` theme block (lines ~810-901).
All existing class names (.main-header, .kpi-card, .pcard, .g-card, .nl-hero, ...) are kept.
"""

# ─────────────────────────── design tokens ───────────────────────────
_TOKENS_LIGHT = """
:root, .stApp {
  --vs-bg:            #F6F8FC;
  --vs-surface:       #FFFFFF;
  --vs-surface-2:     #F1F4F9;
  --vs-ink:           #0B1728;
  --vs-ink-soft:      #4B5B78;
  --vs-ink-mute:      #8B97AE;
  --vs-hair:          rgba(11,23,40,.08);
  --vs-hair-strong:   rgba(11,23,40,.14);
  --vs-brand:         #1F4E8C;
  --vs-brand-deep:    #0B1F3A;
  --vs-brand-soft:    rgba(31,78,140,.08);
  --vs-brand-ring:    rgba(31,78,140,.22);
  --vs-gold:          #C89B3C;
  --vs-gold-soft:     rgba(200,155,60,.10);
  --vs-ok:            #15803D;
  --vs-ok-soft:       rgba(21,128,61,.10);
  --vs-bad:           #B91C1C;
  --vs-bad-soft:      rgba(185,28,28,.10);
  --vs-input:         #FFFFFF;
  --vs-menu:          rgba(255,255,255,.82);
  --vs-shadow-1:      0 1px 2px rgba(11,23,40,.04), 0 2px 8px rgba(11,23,40,.05);
  --vs-shadow-2:      0 2px 6px rgba(11,23,40,.05), 0 12px 32px rgba(11,23,40,.08);
  --vs-shadow-3:      0 8px 24px rgba(11,23,40,.10), 0 28px 64px rgba(11,23,40,.12);
  --vs-shadow-brand:  0 10px 28px rgba(31,78,140,.28);
}
"""

_TOKENS_DARK = """
:root, .stApp {
  --vs-bg:            #0A0F18;
  --vs-surface:       #111827;
  --vs-surface-2:     #161E2E;
  --vs-ink:           #EEF2F8;
  --vs-ink-soft:      #A9B5CC;
  --vs-ink-mute:      #6E7C96;
  --vs-hair:          rgba(255,255,255,.07);
  --vs-hair-strong:   rgba(255,255,255,.13);
  --vs-brand:         #5B8FDB;
  --vs-brand-deep:    #1B3B6F;
  --vs-brand-soft:    rgba(91,143,219,.12);
  --vs-brand-ring:    rgba(91,143,219,.30);
  --vs-gold:          #E0B65A;
  --vs-gold-soft:     rgba(224,182,90,.12);
  --vs-ok:            #4ADE80;
  --vs-ok-soft:       rgba(74,222,128,.12);
  --vs-bad:           #F87171;
  --vs-bad-soft:      rgba(248,113,113,.12);
  --vs-input:         #0F1624;
  --vs-menu:          rgba(17,24,39,.78);
  --vs-shadow-1:      0 1px 2px rgba(0,0,0,.30), 0 2px 8px rgba(0,0,0,.25);
  --vs-shadow-2:      0 2px 6px rgba(0,0,0,.30), 0 14px 36px rgba(0,0,0,.40);
  --vs-shadow-3:      0 10px 28px rgba(0,0,0,.45), 0 32px 72px rgba(0,0,0,.55);
  --vs-shadow-brand:  0 10px 28px rgba(27,59,111,.55);
}
"""

# ─────────────────────────── base stylesheet ───────────────────────────
_BASE = """
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

/* ═══ 0. Global rhythm ═══ */
:root, .stApp {
  --vs-r-sm: 10px; --vs-r-md: 14px; --vs-r-lg: 18px; --vs-r-xl: 24px;
  --vs-ease: cubic-bezier(.2,.8,.2,1);
  --vs-t-fast: 160ms var(--vs-ease);
  --vs-t-base: 260ms var(--vs-ease);
  --vs-t-slow: 420ms var(--vs-ease);
}
html, body, .stApp { font-family: var(--vs-font, 'Manrope'), system-ui, sans-serif !important; color: var(--vs-ink); }
.stApp { background: var(--vs-bg) !important; }
h1, h2, h3, h4, h5 { font-family: 'Sora', sans-serif !important; letter-spacing: -.022em !important; color: var(--vs-ink) !important; font-weight: 700 !important; }
h1 { margin: 1.2rem 0 .6rem !important; font-size: clamp(1.7rem, 2.6vw, 2.25rem) !important; }
h2 { font-size: clamp(1.35rem, 2vw, 1.7rem) !important; }
h3 { font-size: 1.2rem !important; }
p, li { line-height: 1.65; }
* { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }
*:focus-visible { outline: 2px solid var(--vs-brand) !important; outline-offset: 2px !important; border-radius: 6px; }

/* ═══ 1. Streamlit chrome ═══ */
#MainMenu, footer, [data-testid*="Deploy"], #stDeployButton, header [data-testid="stToolbarActions"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; height: 2.7rem !important; }
#root, #root > div, div[data-testid="stAppViewContainer"], div[data-testid="stAppViewBlockContainer"],
main[data-testid="stMain"], section.main { padding-top: 0 !important; margin-top: 0 !important; }
div[data-testid="stMainBlockContainer"], section.main > div.block-container { padding-top: .5rem !important; max-width: 1180px; }
[data-testid="stSidebarCollapsedControl"] { top: .6rem !important; left: .6rem !important; }
[data-testid="stSidebarCollapsedControl"] button {
  width: 40px !important; height: 40px !important; border-radius: var(--vs-r-sm) !important;
  background: var(--vs-surface) !important; border: 1px solid var(--vs-hair-strong) !important;
  box-shadow: var(--vs-shadow-1) !important; transition: transform var(--vs-t-fast), box-shadow var(--vs-t-fast) !important; }
[data-testid="stSidebarCollapsedControl"] button:hover { transform: translateY(-1px); box-shadow: var(--vs-shadow-2) !important; }
[data-testid="stSidebarCollapsedControl"] button svg { display: none !important; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--vs-hair-strong); border-radius: 99px; border: 2px solid transparent; background-clip: padding-box; }
::-webkit-scrollbar-thumb:hover { background: var(--vs-ink-mute); background-clip: padding-box; }
::selection { background: var(--vs-brand-ring); }

/* ═══ 2. Sidebar ═══ */
[data-testid="stSidebar"] { background: var(--vs-surface) !important; border-right: 1px solid var(--vs-hair) !important; box-shadow: none !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important; box-shadow: none !important; border: 1px solid transparent !important;
  justify-content: flex-start !important; text-align: left !important;
  border-radius: var(--vs-r-sm) !important; padding: .62rem 1rem !important;
  font-size: .95rem !important; font-weight: 600 !important; color: var(--vs-ink-soft) !important;
  transition: background var(--vs-t-fast), color var(--vs-t-fast), transform var(--vs-t-fast) !important; }
[data-testid="stSidebar"] .stButton > button * { color: inherit !important; }
[data-testid="stSidebar"] .stButton > button:hover { background: var(--vs-surface-2) !important; color: var(--vs-ink) !important; transform: none !important; }
[data-testid="stSidebar"] .stButton > button::after { content: none !important; }
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
  background: var(--vs-brand-soft) !important; border: 1px solid var(--vs-brand-ring) !important;
  color: var(--vs-brand) !important; font-weight: 700 !important; }
.qbrand { font-family:'Sora',sans-serif; font-size:1.25rem; font-weight:800; padding:.3rem .6rem 1rem; letter-spacing:-.02em; display:flex; align-items:center; color: var(--vs-ink) !important; }
.qcap { text-transform:uppercase; font-size:.66rem; letter-spacing:.12em; color: var(--vs-ink-mute) !important; margin:1rem .7rem .35rem; font-weight:700; }

/* user card */
.user-card { position:relative; padding:.65rem .8rem; border-radius: var(--vs-r-md); border:1px solid var(--vs-hair);
  background: var(--vs-surface-2); z-index:10; transition: border-color var(--vs-t-fast), background var(--vs-t-fast); cursor:pointer; }
.user-card:hover { border-color: var(--vs-hair-strong); }
.user-row { display:flex; align-items:center; gap:10px; }
.chev { opacity:.45; display:flex; transition: transform var(--vs-t-fast); }
.avatar { width:36px; height:36px; border-radius:50%; background: linear-gradient(135deg, var(--vs-brand-deep), var(--vs-brand));
  color:#fff !important; font-weight:800; display:flex; align-items:center; justify-content:center; font-family:'Sora',sans-serif; font-size:.8rem; flex-shrink:0; overflow:hidden;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.18); }
.avatar img { width:100%; height:100%; border-radius:50%; object-fit:cover; }
.uname { font-weight:700; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; display:flex; align-items:center; gap:8px; font-size:.93rem; color: var(--vs-ink) !important; }
.tier-chip { font-size:.58rem; font-weight:800; padding:2px 7px; border-radius:6px; background: var(--vs-gold-soft); border:1px solid var(--vs-gold); color: var(--vs-gold) !important; letter-spacing:.08em; white-space:nowrap; }
div[data-testid="stVerticalBlock"]:has(.user-card):not(:has(.qbrand)) { margin-top:.2rem; padding:.35rem; border:1px solid var(--vs-hair); border-radius: var(--vs-r-md); background: var(--vs-surface); }
div[data-testid="stVerticalBlock"]:has(.user-card):not(:has(.qbrand)) > div:not(:first-child) { display:none; }
div[data-testid="stVerticalBlock"]:has(.user-card):not(:has(.qbrand)):hover > div:not(:first-child) { display:block; animation: vsFade var(--vs-t-base) both; }
div[data-testid="stVerticalBlock"]:has(.user-card):not(:has(.qbrand)) .user-card { border:none; background:transparent; }
div[data-testid="stVerticalBlock"]:has(.user-card):not(:has(.qbrand)) [data-testid="stButton"] > button {
  background:transparent !important; box-shadow:none !important; border:none !important; border-radius: var(--vs-r-sm) !important;
  padding:.55rem .8rem !important; font-size:.88rem !important; justify-content:flex-start !important; color: var(--vs-ink-soft) !important; }
.um-sep { border-top:1px solid var(--vs-hair); margin:.3rem .4rem; }
.big-avatar { width:84px; height:84px; border-radius:50%; object-fit:cover; display:flex; align-items:center; justify-content:center; font-size:1.6rem;
  background: linear-gradient(135deg, var(--vs-brand-deep), var(--vs-brand)); color:#fff !important; font-weight:800; font-family:'Sora',sans-serif; box-shadow: var(--vs-shadow-2); }

/* ═══ 3. Buttons ═══ */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(180deg, var(--vs-brand) 0%, var(--vs-brand-deep) 140%) !important;
  color:#fff !important; border:1px solid rgba(255,255,255,.06) !important; border-radius: 12px !important;
  font-weight:700 !important; font-size:.93rem !important; padding:.62rem 1.15rem !important; letter-spacing:.005em;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.16), var(--vs-shadow-brand) !important;
  transition: transform var(--vs-t-fast), box-shadow var(--vs-t-fast), filter var(--vs-t-fast) !important; position:relative; overflow:hidden; }
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px) !important; filter: brightness(1.06); box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 14px 32px rgba(31,78,140,.34) !important; }
.stButton > button:active, .stDownloadButton > button:active { transform: translateY(0) scale(.99) !important; filter: brightness(.98); }
.stButton > button p, .stDownloadButton > button p { color:#fff !important; }
[data-testid="stBaseButton-secondary"] { background: var(--vs-surface) !important; color: var(--vs-ink) !important; border:1px solid var(--vs-hair-strong) !important; box-shadow: var(--vs-shadow-1) !important; }
[data-testid="stBaseButton-secondary"] p { color: var(--vs-ink) !important; }

/* ═══ 4. Inputs / forms / tabs / alerts ═══ */
html body .stApp [data-testid="stTextInput"] input, html body .stApp [data-testid="stTextArea"] textarea, html body .stApp [data-testid="stNumberInput"] input,
html body .stApp [data-testid="stSelectbox"] > div > div {
  background: var(--vs-input) !important; color: var(--vs-ink) !important; border:1px solid var(--vs-hair-strong) !important;
  border-radius: 12px !important; box-shadow: var(--vs-shadow-1) !important;
  transition: border-color var(--vs-t-fast), box-shadow var(--vs-t-fast) !important; }
html body .stApp [data-testid="stTextInput"] input:focus, html body .stApp [data-testid="stTextArea"] textarea:focus, html body .stApp [data-testid="stNumberInput"] input:focus {
  border-color: var(--vs-brand) !important; box-shadow: 0 0 0 4px var(--vs-brand-ring), var(--vs-shadow-1) !important; outline:none !important; }
html body .stApp [data-testid="stTextInput"] > div, html body .stApp [data-testid="stTextArea"] > div { border:none !important; background:transparent !important; }
html body .stApp label, html body .stApp [data-testid="stWidgetLabel"] p { color: var(--vs-ink-soft) !important; font-weight:600 !important; font-size:.88rem !important; }
html body .stApp [data-testid="stMarkdown"] p { color: var(--vs-ink); }
[data-testid="stForm"] { background: var(--vs-surface); border:1px solid var(--vs-hair); border-radius: var(--vs-r-xl); padding:1.7rem 1.5rem; box-shadow: var(--vs-shadow-2); }
[data-testid="stExpander"] { border:1px solid var(--vs-hair) !important; border-radius: var(--vs-r-md) !important; background: var(--vs-surface) !important; box-shadow: var(--vs-shadow-1); overflow:hidden; }
[data-testid="stExpander"] summary { font-weight:600; }
[data-testid="stExpander"] summary:hover { color: var(--vs-brand) !important; }
[data-testid="stTabs"] [role="tablist"] { border-bottom:none !important; gap:4px; background: var(--vs-surface-2); padding:4px; border-radius: 12px; display:inline-flex; }
[data-testid="stTabs"] [role="tab"] { font-weight:600; padding:.5rem 1rem; border-radius:9px; color: var(--vs-ink-soft) !important; transition: background var(--vs-t-fast), color var(--vs-t-fast); }
[data-testid="stTabs"] [role="tab"]:hover { color: var(--vs-ink) !important; }
[data-testid="stTabs"] [aria-selected="true"] { background: var(--vs-surface); color: var(--vs-ink) !important; box-shadow: var(--vs-shadow-1); }
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] { display:none !important; }
[data-testid="stMetric"] { background: var(--vs-surface); border:1px solid var(--vs-hair); border-radius: var(--vs-r-lg); padding:1rem 1.2rem; box-shadow: var(--vs-shadow-1); }
[data-testid="stMetricLabel"] p { color: var(--vs-ink-mute) !important; font-size:.8rem !important; text-transform:uppercase; letter-spacing:.06em; font-weight:700 !important; }
[data-testid="stMetricValue"] { font-family:'Sora',sans-serif !important; font-weight:800 !important; }
.stAlert { border-radius: var(--vs-r-md) !important; border:1px solid var(--vs-hair) !important; box-shadow: var(--vs-shadow-1); }
.stProgress > div > div { background: var(--vs-surface-2) !important; border-radius:99px; }
.stProgress > div > div > div { background: linear-gradient(90deg, var(--vs-brand), var(--vs-gold)) !important; border-radius:99px; }
[data-testid="stDataFrame"] { border-radius: var(--vs-r-md); overflow:hidden; border:1px solid var(--vs-hair); box-shadow: var(--vs-shadow-1); }
iframe { border-radius: var(--vs-r-xl) !important; border:1px solid var(--vs-hair-strong) !important; box-shadow: var(--vs-shadow-3) !important; }
hr { border-color: var(--vs-hair) !important; margin: 1.6rem 0 !important; }

/* ═══ 5. Hero & landing ═══ */
.main-header { position:relative; overflow:hidden; color:#fff; text-align:center; padding:3rem 2rem 2.6rem; margin-bottom:2rem;
  border-radius: var(--vs-r-xl); border:1px solid rgba(255,255,255,.10);
  background: radial-gradient(900px 380px at 15% -20%, rgba(91,143,219,.45), transparent 60%),
              radial-gradient(700px 320px at 95% 110%, rgba(200,155,60,.28), transparent 60%),
              linear-gradient(160deg, #0B1F3A 0%, #12305A 60%, #1F4E8C 130%);
  box-shadow: var(--vs-shadow-3), inset 0 1px 0 rgba(255,255,255,.12); }
.main-header::after { content:""; position:absolute; inset:0; pointer-events:none;
  background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.035) 1px, transparent 1px);
  background-size: 36px 36px; mask-image: radial-gradient(ellipse at center, #000 30%, transparent 80%); }
.main-header > * { position:relative; z-index:1; }
.hero-badges { display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-top:1.2rem; }
.hbadge { background: rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.22); backdrop-filter: blur(10px);
  color:#fff; padding:6px 13px; border-radius:99px; font-size:.76rem; font-weight:600; display:inline-flex; align-items:center; letter-spacing:.01em; }
.vs-ic { display:inline-flex; align-items:center; margin-right:9px; vertical-align:-3px; }
.lnav-brand { display:flex; align-items:center; gap:9px; font-family:'Sora',sans-serif; font-weight:800; font-size:1.12rem; color: var(--vs-ink) !important; }
.lnav-brand * { color: var(--vs-ink) !important; }

/* top nav (public) */
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) { position:sticky; top:2.7rem; z-index:999;
  background: var(--vs-menu); backdrop-filter: blur(18px) saturate(1.4); -webkit-backdrop-filter: blur(18px) saturate(1.4);
  border:1px solid var(--vs-hair); border-top:none; box-shadow: var(--vs-shadow-1); border-radius:0 0 var(--vs-r-lg) var(--vs-r-lg); padding:.5rem .7rem; margin:0 0 1rem 0; }
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) {
  background:transparent !important; box-shadow:none !important; border:none !important; border-radius:99px !important; font-weight:600 !important; color: var(--vs-ink-soft) !important; }
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]):hover { background: var(--vs-surface-2) !important; color: var(--vs-ink) !important; transform:none !important; }
div[data-testid="stVerticalBlock"]:has(.lnav):not(:has(.lp-hero)) .stButton > button:not([data-testid="stBaseButton-primary"]) * { color: inherit !important; }

/* settings side-nav */
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button {
  background:transparent !important; box-shadow:none !important; border:1px solid transparent !important; justify-content:flex-start !important; text-align:left !important;
  border-radius: var(--vs-r-sm) !important; padding:.7rem 1.1rem !important; font-size:.98rem !important; font-weight:600 !important; min-height:0 !important; color: var(--vs-ink-soft) !important; }
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button * { color: inherit !important; }
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button:hover { background: var(--vs-surface-2) !important; color: var(--vs-ink) !important; transform:none !important; }
div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) [data-testid="stBaseButton-primary"] { background: var(--vs-brand-soft) !important; border-color: var(--vs-brand-ring) !important; color: var(--vs-brand) !important; }

/* greeting + url zone */
.claude-hello { text-align:center; padding:3.2rem 0 .6rem; }
.claude-hello .big { font-size: clamp(1.8rem, 3.4vw, 2.5rem); font-weight:800; font-family:'Sora',sans-serif; display:flex; align-items:center; justify-content:center; gap:14px; color: var(--vs-ink) !important; letter-spacing:-.03em; }
.claude-sub { margin-top:.6rem; font-size:1.02rem; color: var(--vs-ink-soft) !important; }
.claude-chip { display:flex; align-items:center; justify-content:center; gap:8px; border:1px solid var(--vs-hair-strong); background: var(--vs-surface);
  border-radius:99px; padding:.5rem 1rem; font-size:.85rem; font-weight:600; color: var(--vs-ink) !important; box-shadow: var(--vs-shadow-1); }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stTextInput"] input {
  border-radius:99px !important; padding:1.05rem 1.5rem !important; font-size:1rem !important; border:1px solid var(--vs-hair-strong) !important; box-shadow: var(--vs-shadow-2) !important; }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stTextInput"] input:focus { border-color: var(--vs-brand) !important; box-shadow: 0 0 0 4px var(--vs-brand-ring), var(--vs-shadow-2) !important; }
div[data-testid="stVerticalBlock"]:has(.urlzone) [data-testid="stButton"] > button { border-radius:99px !important; }

/* new-launch hero */
.nl-hero { position:relative; overflow:hidden; border-radius: var(--vs-r-xl); padding:3rem 1.5rem 2.6rem; text-align:center; margin:0 0 1.6rem;
  background: radial-gradient(640px 260px at 10% -10%, rgba(59,130,246,.28), transparent 60%),
              radial-gradient(640px 260px at 90% -10%, rgba(16,185,129,.22), transparent 60%),
              linear-gradient(180deg,#0B0F14,#0D1117); border:1px solid rgba(255,255,255,.08); box-shadow: var(--vs-shadow-3); }
.nl-glow { position:absolute; width:320px; height:320px; border-radius:50%; filter:blur(90px); opacity:.30; pointer-events:none; }
.nl-l { left:-110px; top:-140px; background:#2563EB; } .nl-r { right:-110px; top:-140px; background:#10B981; }
.nl-x { position:absolute; top:14px; right:16px; color:#9AA0A6 !important; cursor:pointer; opacity:.8; display:flex; transition: opacity var(--vs-t-fast); } .nl-x:hover { opacity:1; color:#fff !important; }
.nl-title, html body .stApp .nl-hero .nl-title { color:#E8EAED !important; font-family:'Sora',sans-serif; font-weight:700; font-size:clamp(1.35rem,3vw,2.05rem); line-height:1.4; margin:0; }
.nl-rot { position:relative; display:inline-block; height:1.5em; min-width:250px; vertical-align:bottom; }
.nl-word { position:absolute; left:50%; top:0; transform:translateX(-50%); white-space:nowrap; opacity:0;
  background:linear-gradient(90deg,#60A5FA 15%,#34D399 85%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; animation:nlcycle 12s infinite; }
.nl-word:nth-child(2){animation-delay:3s} .nl-word:nth-child(3){animation-delay:6s} .nl-word:nth-child(4){animation-delay:9s}
@keyframes nlcycle { 0%{opacity:0;transform:translateX(-50%) translateY(10px)} 4%{opacity:1;transform:translateX(-50%) translateY(0)} 25%{opacity:1} 29%{opacity:0;transform:translateX(-50%) translateY(-10px)} 100%{opacity:0} }
div[data-testid="stVerticalBlock"]:has(.nl-zone) [data-testid="stTextInput"] input { border-radius:16px !important; padding:1.1rem 1.4rem !important; font-size:1rem !important;
  background: var(--vs-input) !important; color: var(--vs-ink) !important; border:1px solid var(--vs-brand) !important; box-shadow: 0 0 0 4px var(--vs-brand-ring), var(--vs-shadow-2) !important; }
div[data-testid="stVerticalBlock"]:has(.nl-zone) .stButton > button { background: var(--vs-surface) !important; color: var(--vs-ink) !important; border:1px solid var(--vs-hair-strong) !important; box-shadow: var(--vs-shadow-1) !important;
  border-radius:99px !important; font-weight:600 !important; padding:.5rem 1rem !important; min-height:0 !important; }
div[data-testid="stVerticalBlock"]:has(.nl-zone) .stButton > button p { color: var(--vs-ink) !important; }
div[data-testid="stVerticalBlock"]:has(.nl-zone) .stButton > button:hover { border-color: var(--vs-brand) !important; color: var(--vs-brand) !important; }
div[data-testid="stColumn"]:has(.nl-gowrap) .stButton > button { border-radius:50% !important; width:48px !important; height:48px !important; padding:0 !important; }

/* ═══ 6. Cards (shared surface recipe) ═══ */
.hist-card, .note-card, .notif-card, .pipe-card, .res-head, .kpi-card, .feat-card, .g-card, .qa-box, .q-item, .newfeat, .pay-panel, .bc-wrap,
[data-testid="stColumn"] > div:has(.pcard), [data-testid="stColumn"] [data-testid="stVerticalBlock"]:has(.pcard) {
  background: var(--vs-surface); border:1px solid var(--vs-hair); box-shadow: var(--vs-shadow-1); color: var(--vs-ink);
  transition: transform var(--vs-t-base), box-shadow var(--vs-t-base), border-color var(--vs-t-base); }
.hist-card, .note-card, .notif-card { display:flex; gap:12px; align-items:flex-start; border-radius: var(--vs-r-md); padding:14px 16px; margin:10px 0; border-left:none; }
.hist-card { align-items:center; }
.hist-card:hover, .note-card:hover, .notif-card:hover, .kpi-card:hover, .feat-card:hover, .g-card:hover { border-color: var(--vs-hair-strong); box-shadow: var(--vs-shadow-2); transform: translateY(-2px); }
.hist-left { display:flex; align-items:center; gap:12px; flex:1; }
.hist-ico, .notif-ico, .note-num, .kpi-icon, .g-ico { flex-shrink:0; border-radius: 11px; display:flex; align-items:center; justify-content:center;
  background: var(--vs-brand-soft); color: var(--vs-brand) !important; border:1px solid var(--vs-brand-ring); }
.hist-ico { width:40px; height:40px; } .notif-ico { width:38px; height:38px; }
.note-num { width:32px; height:32px; font-weight:800; font-family:'Sora',sans-serif; font-size:.85rem; }
.note-text { line-height:1.7; font-size:.95rem; color: var(--vs-ink); }
.kpi-card { position:relative; border-radius: var(--vs-r-lg); padding:1.5rem 1.4rem; }
.kpi-icon { width:46px; height:46px; margin-bottom:.9rem; }
.kpi-value { font-family:'Sora',sans-serif; font-size:2.1rem; font-weight:800; margin:.3rem 0; letter-spacing:-.03em; color: var(--vs-ink) !important; }
.kpi-label { font-size:.78rem; text-transform:uppercase; letter-spacing:.07em; font-weight:700; color: var(--vs-ink-mute) !important; margin-bottom:.3rem; }
.kpi-trend { display:inline-flex; align-items:center; gap:4px; font-size:.8rem; font-weight:700; padding:3px 9px; border-radius:99px; }
.kpi-trend.up { background: var(--vs-ok-soft); color: var(--vs-ok); } .kpi-trend.down { background: var(--vs-bad-soft); color: var(--vs-bad); }
.bc-wrap { display:flex; align-items:flex-end; gap:10px; padding:18px 14px 10px; border-radius: var(--vs-r-lg); margin:1rem 0; }
.bc-col { flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; gap:6px; min-width:0; }
.bc-bar { width:70%; max-width:44px; border-radius:6px 6px 3px 3px; background: linear-gradient(180deg, var(--vs-brand), var(--vs-brand-deep)); box-shadow:none; transition: filter var(--vs-t-fast); }
.bc-col:hover .bc-bar { filter: brightness(1.15); }
.bc-lbl { font-size:.7rem; color: var(--vs-ink-mute); }
.pipe-card { border-radius: var(--vs-r-lg); padding:.9rem 1.1rem; margin-bottom:.6rem; }
.pipe-title { display:flex; align-items:center; gap:8px; font-weight:800; color: var(--vs-ink) !important; }
.pipe-row { display:flex; align-items:center; gap:10px; padding:.55rem .2rem; border-bottom:1px solid var(--vs-hair); }
.pipe-row:last-child { border-bottom:none; }
.pipe-lbl { flex:1; font-weight:600; color: var(--vs-ink) !important; }
.pipe-ok { color: var(--vs-ok); font-weight:700; display:flex; align-items:center; gap:4px; }
.pipe-run { color: var(--vs-brand); font-weight:700; } .pipe-wait { color: var(--vs-ink-mute); }
.res-head { display:flex; gap:14px; align-items:center; border-radius: var(--vs-r-lg); padding:1rem 1.2rem; margin-bottom:1rem; border-left:3px solid var(--vs-gold); }
.qa-box { border-radius: var(--vs-r-md); padding:1rem 1.2rem; margin:.6rem 0; background: var(--vs-brand-soft); border-color: var(--vs-brand-ring); }
.q-item { border-radius: var(--vs-r-md); padding:10px 14px; margin:8px 0; font-weight:600; border-left:3px solid var(--vs-gold); }
.newfeat { border-radius: var(--vs-r-md); padding:.7rem 1rem; margin:.4rem 0; display:flex; align-items:center; gap:10px; font-weight:600; }
.keyword-tag { display:inline-block; background: var(--vs-brand-soft); border:1px solid var(--vs-brand-ring); color: var(--vs-brand) !important;
  padding:5px 13px; border-radius:99px; margin:3px; font-size:.85rem; font-weight:700; transition: background var(--vs-t-fast), transform var(--vs-t-fast); }
.keyword-tag:hover { background: var(--vs-brand-ring); transform: translateY(-1px); }

/* payment */
.pay-panel { border-radius: var(--vs-r-xl); padding:1.5rem 1.7rem; margin:1rem 0; box-shadow: var(--vs-shadow-2); border-color: var(--vs-hair-strong); }
.pay-panel, .pay-panel div, .pay-panel li, .pay-panel b, .pay-panel code { color: var(--vs-ink) !important; }
.pay-title { font-family:'Sora',sans-serif; font-weight:800; font-size:1.2rem; display:flex; align-items:center; gap:8px; }
.pay-price { font-family:'Sora',sans-serif; font-size:2.2rem; font-weight:800; margin:.4rem 0; letter-spacing:-.03em; }
.pay-price span { font-size:1rem; color: var(--vs-ink-soft) !important; font-weight:600; }
.pay-steps { margin:.6rem 0 0 1.2rem; line-height:1.9; }

/* pricing */
[data-testid="stColumn"] > div:has(.pcard), [data-testid="stColumn"] [data-testid="stVerticalBlock"]:has(.pcard) { border-radius: var(--vs-r-xl); padding:1.6rem 1.4rem; position:relative; }
[data-testid="stColumn"] [data-testid="stVerticalBlock"]:has(.pcard):hover { border-color: var(--vs-brand-ring); box-shadow: var(--vs-shadow-2); transform: translateY(-3px); }
[data-testid="stColumn"] [data-testid="stVerticalBlock"]:has(.pc-badge) { border-color: var(--vs-brand) !important; box-shadow: 0 0 0 1px var(--vs-brand), var(--vs-shadow-2) !important; }
.pc-icon { margin-bottom:.8rem; color: var(--vs-brand); }
.pc-name, .pc-price { font-family:'Sora',sans-serif; font-weight:800; color: var(--vs-ink) !important; }
.pc-name { font-size:1.35rem; margin:0 0 .2rem; } .pc-price { font-size:2.2rem; margin:.4rem 0 0; letter-spacing:-.03em; }
.pc-tag { color: var(--vs-ink-soft) !important; margin:.2rem 0 1.1rem; font-size:.9rem; min-height:2.6em; }
.pc-sub { font-size:.78rem; color: var(--vs-ink-mute) !important; margin:.3rem 0 1rem; }
.pc-sep { border-top:1px solid var(--vs-hair); margin:1.2rem 0; }
.pc-plus { font-weight:700; margin:0 0 .6rem; font-size:.85rem; text-transform:uppercase; letter-spacing:.06em; color: var(--vs-ink-mute) !important; }
.pfeat { display:flex; align-items:flex-start; gap:9px; margin:.55rem 0; font-size:.9rem; line-height:1.5; color: var(--vs-ink) !important; }
.pfeat svg { margin-right:0; margin-top:3px; flex-shrink:0; color: var(--vs-ok); }
.pc-badge { display:inline-block; padding:4px 11px; border-radius:99px; font-size:.66rem; font-weight:800; letter-spacing:.08em;
  background: linear-gradient(180deg, var(--vs-brand), var(--vs-brand-deep)); color:#fff !important; border:none; position:absolute; top:14px; right:14px; margin:0; box-shadow: var(--vs-shadow-brand); }

/* features / wizard */
.feat-card { border-radius: var(--vs-r-lg); padding:1.6rem 1.2rem; text-align:center; height:100%; }
.feat-icon { display:flex; justify-content:center; margin-bottom:.8rem; }
.feat-title { font-weight:800; font-size:1.02rem; font-family:'Sora',sans-serif; color: var(--vs-ink); }
.feat-text { font-size:.88rem; color: var(--vs-ink-soft); margin-top:.45rem; line-height:1.55; }
.wizard-steps { display:flex; align-items:center; justify-content:center; gap:8px; margin:1.4rem 0 2rem; }
.wstep { width:38px; height:38px; border-radius:50%; display:flex; align-items:center; justify-content:center; background: var(--vs-surface);
  color: var(--vs-ink-mute); font-weight:800; border:1.5px solid var(--vs-hair-strong); font-family:'Sora',sans-serif; font-size:.9rem; transition: all var(--vs-t-base); }
.wstep.active { background: var(--vs-gold); color:#0B1F3A; border-color: var(--vs-gold); box-shadow: 0 0 0 5px var(--vs-gold-soft); }
.wstep.done { background: var(--vs-brand); color:#fff; border-color: var(--vs-brand); }
.wline { flex:0 0 46px; height:2px; background: var(--vs-hair-strong); border-radius:99px; transition: background var(--vs-t-base); }
.wline.done { background: var(--vs-brand); }
.wizard-card { max-width:560px; margin:0 auto; }

/* ═══ 7. About / editorial ═══ */
.g-kicker { letter-spacing:.24em; text-transform:uppercase; font-size:.68rem; font-weight:800; color: var(--vs-gold) !important; }
.g-h1 { font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(2.2rem,4.4vw,3.6rem); line-height:1.06; letter-spacing:-.03em; margin:.9rem 0 1rem; color: var(--vs-ink) !important; }
.g-h1 em { font-style:normal; color: var(--vs-gold); }
.g-h2 { font-family:'Sora',sans-serif; font-weight:700; font-size:clamp(1.5rem,2.6vw,2.1rem); letter-spacing:-.02em; color: var(--vs-ink) !important; }
.g-lead { font-size:1.06rem; line-height:1.75; max-width:56ch; color: var(--vs-ink-soft) !important; }
.g-rule { width:48px; height:2px; background: var(--vs-gold); margin:1.4rem 0; border-radius:99px; }
.g-card { border-radius: var(--vs-r-xl); padding:1.8rem; height:100%; }
.g-card h4 { font-family:'Sora',sans-serif; font-weight:700; font-size:1.05rem; margin-bottom:.5rem; color: var(--vs-ink) !important; }
.g-card p { line-height:1.65; font-size:.95rem; color: var(--vs-ink-soft) !important; }
.g-ico { width:44px; height:44px; margin-bottom:1rem; background: var(--vs-gold-soft); border-color: transparent; color: var(--vs-gold) !important; }
.g-stats { display:flex; border-top:1px solid var(--vs-hair); border-bottom:1px solid var(--vs-hair); margin:2.6rem 0; }
.g-stat { flex:1; text-align:center; padding:1.5rem 1rem; border-left:1px solid var(--vs-hair); }
.g-stat:first-child { border-left:none; }
.g-stat b { display:block; font-family:'Sora',sans-serif; font-weight:800; font-size:1.9rem; letter-spacing:-.03em; color: var(--vs-ink) !important; }
.g-stat span { font-size:.75rem; letter-spacing:.08em; text-transform:uppercase; color: var(--vs-ink-mute) !important; }
.g-step { border-top:2px solid var(--vs-hair); padding-top:1.2rem; }
.g-step .n { font-family:'Sora',sans-serif; font-weight:800; color: var(--vs-gold); font-size:.8rem; letter-spacing:.2em; }
.g-step h4 { font-family:'Sora',sans-serif; font-weight:700; margin:.5rem 0 .4rem; color: var(--vs-ink) !important; }
.g-step p { font-size:.93rem; line-height:1.6; color: var(--vs-ink-soft) !important; }
.g-cta { position:relative; overflow:hidden; border-radius: var(--vs-r-xl); margin:2.8rem 0 1.2rem; padding:3.2rem 2.8rem;
  background: radial-gradient(700px 300px at 90% -10%, rgba(200,155,60,.30), transparent 60%), linear-gradient(135deg,#0B1F3A 0%, #12305A 55%, #1F4E8C 130%);
  border:1px solid rgba(255,255,255,.12); box-shadow: var(--vs-shadow-3); }
.g-cta h3 { color:#fff !important; font-family:'Sora',sans-serif; font-size:2rem; font-weight:800; margin-bottom:.6rem; letter-spacing:-.03em; }
.g-cta p { color:rgba(255,255,255,.85) !important; max-width:60ch; }
.g-cta-badges { display:flex; gap:8px; flex-wrap:wrap; margin-top:1.2rem; }
.g-cta-badges span { background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18); padding:7px 14px; border-radius:99px; font-size:.8rem; font-weight:600; color:#fff !important; }

/* footer */
.footer-dark { background:#0A0F18; color:#B8C2D6; border-radius: var(--vs-r-xl); margin-top:3rem; padding:2.8rem 2.4rem 1.4rem; border:1px solid rgba(255,255,255,.06); }
.footer-dark p, .footer-dark li { color:#B8C2D6 !important; }
.fd-grid { display:grid; grid-template-columns:1.4fr 1fr 1fr 1fr; gap:2rem; }
.fd-logo { display:flex; align-items:center; gap:9px; color:#fff !important; font-size:1.15rem; font-family:'Sora',sans-serif; margin-bottom:.9rem; }
.footer-dark h5 { color:#fff !important; font-size:.8rem; letter-spacing:.1em; text-transform:uppercase; margin-bottom:.9rem; }
.footer-dark ul { list-style:none; padding:0; }
.footer-dark li { padding:.3rem 0; font-size:.9rem; }
.fd-copy { border-top:1px solid rgba(255,255,255,.10); margin-top:2rem; padding-top:1rem; text-align:center; font-size:.82rem; opacity:.65; }
.fd-social { width:38px; height:38px; border-radius:50%; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); display:inline-flex; align-items:center; justify-content:center; color:#B8C2D6 !important; transition: background var(--vs-t-fast), color var(--vs-t-fast); }
.fd-social:hover { background:rgba(255,255,255,.14); color:#fff !important; }
.fd-input { flex:1; background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.12); border-radius:99px; padding:10px 16px; color:#fff; outline:none; font-size:.9rem; }
.fd-send { width:42px; height:42px; border-radius:50%; background: var(--vs-brand); display:inline-flex; align-items:center; justify-content:center; color:#fff !important; flex-shrink:0; }
.fd-link { color:#B8C2D6 !important; text-decoration:none; transition: color var(--vs-t-fast); }
.fd-link:hover { color:#fff !important; }

/* ═══ 8. Motion ═══ */
@keyframes vsFade { from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:none} }
.main-header, [data-testid="stMetric"], .note-card, .notif-card, .pipe-card, .res-head, .hist-card, .kpi-card, .feat-card, .g-card, .pay-panel { animation: vsFade var(--vs-t-slow) both; }
.note-card:nth-child(2), .hist-card:nth-child(2) { animation-delay: 40ms; } .note-card:nth-child(3), .hist-card:nth-child(3) { animation-delay: 80ms; }
.note-card:nth-child(4), .hist-card:nth-child(4) { animation-delay: 120ms; } .note-card:nth-child(5), .hist-card:nth-child(5) { animation-delay: 160ms; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }

/* ═══ 9. Responsive ═══ */
@media (max-width: 768px) {
  .fd-grid { grid-template-columns:1fr; } .g-stats { flex-wrap:wrap; } .g-stat { flex:1 1 45%; }
  .main-header { padding:1.8rem 1.1rem; border-radius: var(--vs-r-lg); } .g-cta { padding:2rem 1.4rem; } .claude-hello .big { font-size:1.7rem; }
  div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) { display:flex; flex-direction:row; flex-wrap:wrap; gap:.4rem; }
  div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) > div[data-testid="stElementContainer"] { flex:1 1 46%; margin:0 !important; }
  div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) > div[data-testid="stElementContainer"]:has(.setnav) { display:none; }
  div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .qcap { flex-basis:100%; margin:.5rem 0 .1rem; }
  div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"]:has(.setnav) .stButton > button { padding:.55rem .5rem !important; font-size:.85rem !important; justify-content:center !important; text-align:center !important; }
}
"""

_FONT_STACKS = {
    "Sora": "'Sora', sans-serif",
    "Système": "system-ui, -apple-system, 'Segoe UI', sans-serif",
    "Adapté aux dyslexiques": "Verdana, 'Atkinson Hyperlegible', sans-serif",
}


def premium_css(theme: str = "light", font: str = "Manrope", reduce_motion: bool = False) -> str:
    """Return the complete <style> block for the given theme / font / motion preferences."""
    tokens = _TOKENS_DARK if theme == "dark" else _TOKENS_LIGHT
    fam = _FONT_STACKS.get(font, "'Manrope', sans-serif")
    motion = ("*,*::before,*::after{animation:none!important;transition:none!important;}"
              if reduce_motion else "")
    return (
        "<style>"
        + tokens
        + _BASE
        + f":root, .stApp {{ --vs-font: {fam}; }}"
        + motion
        + "</style>"
    )