"""
Habillage « premium » de la page Administration — sans modifier admin.py.

· CSS : cartes KPI (st.metric) avec liseré d'accent, onglets en pastilles segmentées, bandeaux d'alerte sobres,
  titres de section avec repère, tableaux et graphiques en cartes arrondies, boutons / champs / expanders cohérents.
· Graphiques : pendant le rendu de la page, st.bar_chart / line_chart / area_chart reçoivent la couleur d'accent
  et une hauteur homogène (si la page ne les précise pas) ; en cas d'incompatibilité, l'appel d'origine est refait.

Usage (app.py) :  from src.ui.admin_skin import render_with_skin
                  _R("admin", lambda: render_with_skin(render_admin))
"""
import functools

import streamlit as st

from src.ui.mobile import theme_tokens

_P = 'html body .stApp'


def _css() -> str:
    t = theme_tokens()
    dark = st.session_state.get("theme", "light") != "light"
    acc, accd = t["acc"], t["acc_dark"]
    card = "linear-gradient(160deg,rgba(255,255,255,.075),rgba(255,255,255,.03))" if dark else "linear-gradient(160deg,#FFFFFF,#F5F9FF)"
    flat = "rgba(255,255,255,.04)" if dark else "#FFFFFF"
    seg = "rgba(255,255,255,.05)" if dark else "#EDF2FA"
    hov = "0 18px 40px rgba(0,0,0,.45)" if dark else "0 18px 40px rgba(30,70,140,.14)"
    return f"""<style>
/* ── Cartes KPI ── */
{_P} [data-testid="stMetric"] {{ position:relative; overflow:hidden; background:{card}; border:1px solid {t["line"]}; border-radius:22px;
  padding:1.15rem 1.25rem 1.1rem !important; box-shadow:{t["shadow"]}; transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease; }}
{_P} [data-testid="stMetric"]::before {{ content:""; position:absolute; left:0; right:0; top:0; height:3px; background:linear-gradient(90deg,{acc},{accd},transparent 85%); }}
{_P} [data-testid="stMetric"]::after {{ content:""; position:absolute; right:-38px; top:-38px; width:120px; height:120px; border-radius:50%;
  background:radial-gradient(circle,color-mix(in srgb,{acc} 22%,transparent),transparent 70%); pointer-events:none; }}
{_P} [data-testid="stMetric"]:hover {{ transform:translateY(-3px); box-shadow:{hov}; border-color:color-mix(in srgb,{acc} 45%,{t["line"]}); }}
{_P} [data-testid="stMetricLabel"], {_P} [data-testid="stMetricLabel"] p {{ font-size:.7rem !important; font-weight:800 !important; letter-spacing:.12em !important;
  text-transform:uppercase !important; color:{t["soft"]} !important; }}
{_P} [data-testid="stMetricValue"], {_P} [data-testid="stMetricValue"] div {{ font-family:'Sora',sans-serif !important; font-weight:800 !important; font-size:2.05rem !important;
  letter-spacing:-.03em !important; color:{t["ink"]} !important; font-variant-numeric:tabular-nums; line-height:1.15 !important; }}
{_P} [data-testid="stMetricDelta"] {{ font-weight:700 !important; }}
/* ── Onglets en segments ── */
{_P} [role="tablist"] {{ gap:.3rem !important; background:{seg} !important; padding:.32rem !important; border-radius:16px !important; border:1px solid {t["line"]} !important; width:fit-content; max-width:100%; overflow-x:auto; box-shadow:none !important; }}
{_P} [data-baseweb="tab-highlight"], {_P} [data-baseweb="tab-border"], {_P} .react-aria-SelectionIndicator, {_P} [role="tablist"] + [role="presentation"] {{ display:none !important; }}
{_P} [role="tablist"]::after, {_P} [role="tablist"]::before {{ display:none !important; }}
{_P} [data-testid="stTab"], {_P} button[data-baseweb="tab"] {{ height:42px; padding:0 1.05rem !important; border-radius:12px !important; background:transparent !important; border:0 !important; box-shadow:none !important; transition:background .18s ease, color .18s ease; }}
{_P} [data-testid="stTab"] p, {_P} button[data-baseweb="tab"] p {{ font-weight:700 !important; font-size:.88rem !important; color:{t["soft"]} !important; }}
{_P} [data-testid="stTab"]:hover p {{ color:{t["ink"]} !important; }}
{_P} [data-testid="stTab"][aria-selected="true"], {_P} button[data-baseweb="tab"][aria-selected="true"] {{ background:linear-gradient(135deg,{acc},{accd}) !important; box-shadow:0 8px 20px color-mix(in srgb,{acc} 38%,transparent) !important; }}
{_P} [data-testid="stTab"][aria-selected="true"] p, {_P} button[data-baseweb="tab"][aria-selected="true"] p {{ color:#fff !important; }}
{_P} [data-testid="stTabs"] [role="tabpanel"] {{ padding-top:1.25rem; }}
/* ── Bandeaux d'alerte ── */
{_P} [data-testid="stAlert"] {{ background:transparent !important; }}
{_P} [data-testid="stAlertContainer"] {{ border-radius:18px !important; border:1px solid {t["line"]} !important; box-shadow:{t["shadow"]}; padding:.9rem 1.1rem !important; }}
{_P} [data-testid="stAlertContainer"] > div, {_P} [data-testid="stAlertContainer"] [data-testid="stMarkdownContainer"] {{ background:transparent !important; }}
{_P} [data-testid="stAlertContainer"] p {{ font-weight:600 !important; font-size:.9rem !important; }}
{_P} [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{ background:color-mix(in srgb,#F59E0B 13%,transparent) !important; border-left:4px solid #F59E0B !important; }}
{_P} [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {{ background:color-mix(in srgb,{acc} 12%,transparent) !important; border-left:4px solid {acc} !important; }}
{_P} [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {{ background:color-mix(in srgb,#10B981 12%,transparent) !important; border-left:4px solid #10B981 !important; }}
{_P} [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{ background:color-mix(in srgb,#EF4444 12%,transparent) !important; border-left:4px solid #EF4444 !important; }}
/* ── Titres de section ── */
{_P} [data-testid="stMainBlockContainer"] h2, {_P} [data-testid="stMainBlockContainer"] h3 {{ font-family:'Sora',sans-serif !important; letter-spacing:-.025em !important; font-weight:800 !important;
  display:flex; align-items:center; gap:.65rem; margin-top:1.6rem !important; color:{t["ink"]} !important; }}
{_P} [data-testid="stMainBlockContainer"] h2::before, {_P} [data-testid="stMainBlockContainer"] h3::before {{ content:""; width:5px; height:1.05em; border-radius:3px; background:linear-gradient(180deg,{acc},{accd}); flex:none; }}
/* ── Tableaux & graphiques en cartes ── */
{_P} [data-testid="stDataFrame"], {_P} [data-testid="stTable"] {{ border:1px solid {t["line"]}; border-radius:18px; overflow:hidden; box-shadow:{t["shadow"]}; background:{flat}; }}
{_P} [data-testid="stVegaLiteChart"], {_P} [data-testid="stArrowVegaLiteChart"] {{ background:{card}; border:1px solid {t["line"]}; border-radius:22px; padding:0; overflow:hidden; box-shadow:{t["shadow"]}; }}
{_P} [data-testid="stVegaLiteChart"] canvas, {_P} [data-testid="stArrowVegaLiteChart"] canvas {{ border-radius:12px; }}
/* ── Conteneurs bordés / expanders ── */
{_P} [data-testid="stExpander"] {{ border:1px solid {t["line"]} !important; border-radius:18px !important; background:{flat}; overflow:hidden; box-shadow:{t["shadow"]}; }}
{_P} [data-testid="stExpander"] summary {{ font-weight:700; }}
{_P} [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{ border-radius:20px; }}
/* ── Champs & boutons ── */
{_P} [data-testid="stMainBlockContainer"] [data-baseweb="input"], {_P} [data-testid="stMainBlockContainer"] [data-baseweb="select"] > div, {_P} [data-testid="stMainBlockContainer"] textarea {{
  border-radius:14px !important; }}
{_P} [data-testid="stMainBlockContainer"] .stButton > button {{ border-radius:14px !important; font-weight:700 !important; min-height:2.7rem; transition:transform .15s ease, box-shadow .2s ease; }}
{_P} [data-testid="stMainBlockContainer"] .stButton > button:hover {{ transform:translateY(-1px); }}
{_P} [data-testid="stMainBlockContainer"] .stButton > button[kind="primary"] {{ background:linear-gradient(135deg,{acc},{accd}) !important; border:0 !important; color:#fff !important; box-shadow:0 10px 24px color-mix(in srgb,{acc} 35%,transparent); }}
{_P} hr {{ border-color:{t["line"]} !important; }}
</style>"""


def _lighten(hex_color: str, amt: float) -> str:
    try:
        h = hex_color.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return "#%02X%02X%02X" % tuple(int(c + (255 - c) * amt) for c in (r, g, b))
    except Exception:
        return hex_color


_CHARTS = ("bar_chart", "line_chart", "area_chart")


def _wrap(orig, color):
    @functools.wraps(orig)
    def inner(*a, **k):
        if "color" not in k:
            try:
                return orig(*a, **{"color": color, "height": k.pop("height", 300), **k})
            except Exception:
                pass
        return orig(*a, **k)
    return inner


def render_with_skin(fn, *args, **kwargs):
    """Injecte le style puis exécute la page d'administration avec les graphiques aux couleurs de la marque."""
    st.markdown(_css(), unsafe_allow_html=True)
    color = theme_tokens()["acc"]
    if st.session_state.get("theme", "light") != "light":
        color = _lighten(color, .38)
    saved = {n: getattr(st, n) for n in _CHARTS}
    try:
        for n in _CHARTS:
            setattr(st, n, _wrap(saved[n], color))
        return fn(*args, **kwargs)
    finally:
        for n, f in saved.items():
            setattr(st, n, f)