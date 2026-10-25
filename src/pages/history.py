"""
Page « Historique » — refonte façon application mobile (cartes arrondies, pastilles de filtre, état vide soigné).

Remplace la fonction `render_historique()` de app.py. Dans app.py :

    from src.pages.history import render_historique as render_historique_v2
    ...
    if page == "historique" and not is_guest: render_historique_v2(user, tier); st.stop()
"""

import html as _html
from datetime import datetime, timedelta

import streamlit as st

from src.ui.i18n import T
from src.ui.layout import render_footer
from src.ui.mobile import theme_tokens
from src.history_manager import get_history, clear_history
from src.ui.storage import load_favs, toggle_fav

_CSS = """
html body .stApp .vh-w { white-space:normal; }
html body .stApp .vh-w * { box-sizing:border-box; }
html body .stApp .vh-title { font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(1.6rem,5.5vw,2.3rem); letter-spacing:-.03em; line-height:1.1; color:@ink@ !important; margin:.2rem 0 0; }
html body .stApp .vh-sub { color:@soft@ !important; font-size:.92rem; margin:.3rem 0 0; }

/* En-tête : titre à gauche, bouton à droite — sur toutes les largeurs */
html body .stApp div[data-testid="stVerticalBlock"].st-key-vh_head [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:minmax(0,1fr) auto !important; gap:12px !important; align-items:center !important; flex-direction:row !important; }
html body .stApp div[data-testid="stVerticalBlock"].st-key-vh_head [data-testid="stColumn"] { width:auto !important; min-width:0 !important; flex:none !important; }
html body .stApp .st-key-vh_new button { height:48px !important; padding:0 18px !important; border-radius:16px !important; font-weight:800 !important; white-space:nowrap !important;
  background:linear-gradient(135deg,@acc@,@acc_dark@) !important; border:none !important; box-shadow:0 12px 26px rgba(30,100,200,.32) !important; }
html body .stApp .st-key-vh_new button p { color:#fff !important; font-weight:800 !important; }

/* Cartes chiffres */
html body .stApp .vh-kpis { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:clamp(.5rem,2vw,1rem); margin:1.1rem 0 1.2rem; }
html body .stApp .vh-kpi { background:@surface@; border:1px solid @line@; border-radius:22px; padding:clamp(.8rem,3vw,1.2rem); box-shadow:@shadow@; min-height:104px; }
html body .stApp .vh-kpi small { display:block; color:@soft@ !important; font-size:clamp(.72rem,2.6vw,.9rem); line-height:1.25; min-height:2.5em; }
html body .stApp .vh-kpi b { display:block; margin-top:.3rem; font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(1.7rem,7vw,2.4rem); color:@ink@ !important; letter-spacing:-.03em; }

/* Pastilles de filtre */
.stApp .st-key-vh_pills { margin:0 0 1rem; }
.stApp .st-key-vh_pills [role="radiogroup"] { gap:.5rem; flex-wrap:wrap; }
.stApp .st-key-vh_pills [data-testid="stRadioOption"], .stApp .st-key-vh_pills label[data-baseweb="radio"] { padding:.55rem 1.25rem; margin:0; border-radius:999px; background:@surface@; border:1px solid @line@; cursor:pointer; transition:all .2s ease; }
.stApp .st-key-vh_pills [data-testid="stRadioOption"] > div > div:first-child, .stApp .st-key-vh_pills label[data-baseweb="radio"] > div:first-child { display:none !important; }
.stApp .st-key-vh_pills [data-testid="stRadioOption"] p, .stApp .st-key-vh_pills label[data-baseweb="radio"] p { font-weight:700 !important; font-size:.95rem !important; margin:0 !important; color:@soft@ !important; }
.stApp .st-key-vh_pills [data-testid="stRadioOption"][data-selected="true"], .stApp .st-key-vh_pills label[data-baseweb="radio"]:has(input:checked) { background:linear-gradient(135deg,@acc@,@acc_dark@); border-color:transparent; box-shadow:0 10px 22px rgba(30,100,200,.28); }
.stApp .st-key-vh_pills [data-testid="stRadioOption"][data-selected="true"] p, .stApp .st-key-vh_pills label[data-baseweb="radio"]:has(input:checked) p { color:#fff !important; }

/* Cartes d'analyse */
html body .stApp .vh-card { display:flex; align-items:center; gap:14px; background:@surface@; border:1px solid @line@; border-radius:22px; padding:12px; box-shadow:@shadow@; transition:transform .35s cubic-bezier(.16,1,.3,1), box-shadow .3s ease; }
html body .stApp .vh-card:hover { transform:translateY(-3px); }
html body .stApp .vh-thumb { position:relative; flex:none; width:92px; height:64px; border-radius:14px; overflow:hidden; background:linear-gradient(135deg,@acc_dark@,@acc@); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; }
html body .stApp .vh-thumb img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
html body .stApp .vh-meta { min-width:0; flex:1; }
html body .stApp .vh-meta b { display:block; color:@ink@ !important; font-size:.98rem; line-height:1.3; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
html body .stApp .vh-meta small { display:block; margin-top:.3rem; color:@soft@ !important; font-size:.78rem; }
html body .stApp .vh-star { flex:none; font-size:1.1rem; }
html body div[data-testid="stVerticalBlock"][class*="st-key-hc_"] { margin:.35rem 0 1rem; }
html body div[data-testid="stVerticalBlock"][class*="st-key-hc_"] [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:minmax(0,1fr) 56px !important; gap:8px !important; flex-direction:row !important; }
html body div[data-testid="stVerticalBlock"][class*="st-key-hc_"] [data-testid="stColumn"] { width:auto !important; min-width:0 !important; flex:none !important; }
html body .stApp [class*="st-key-hc_"] button { border-radius:14px !important; min-height:44px !important; }
html body .stApp [class*="st-key-hc_"] button[data-testid="stBaseButton-secondary"] { background:@surface@ !important; border:1px solid @line@ !important; }
html body .stApp [class*="st-key-hc_"] button[data-testid="stBaseButton-secondary"] p { color:@ink@ !important; }

/* État vide */
html body .stApp .vh-empty { text-align:center; background:@surface@; border:1px solid @line@; border-radius:28px; padding:clamp(1.6rem,6vw,3rem) 1.2rem 1.4rem; box-shadow:@shadow@; margin-top:.4rem; }
html body .stApp .vh-empty .ic { width:84px; height:84px; margin:0 auto 1.1rem; border-radius:50%; background:@surface2@; display:flex; align-items:center; justify-content:center; color:@acc@; }
html body .stApp .vh-empty h3 { font-family:'Sora',sans-serif; font-weight:800; font-size:1.35rem; color:@ink@ !important; margin:0 0 .4rem; padding:0; }
html body .stApp .vh-empty p { color:@soft@ !important; font-size:1rem; line-height:1.6; margin:0 auto .4rem; max-width:340px; }
.stApp .st-key-vh_empty_cta { margin-top:.2rem; }
.stApp .st-key-vh_empty_cta button { height:56px !important; border-radius:18px !important; font-weight:800 !important; background:linear-gradient(135deg,@acc@,@acc_dark@) !important; border:none !important; box-shadow:0 14px 28px rgba(30,100,200,.32) !important; }
.stApp .st-key-vh_empty_cta button p { color:#fff !important; font-weight:800 !important; font-size:1.05rem !important; }
"""

_EMPTY_ICON = ('<svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
               '<rect x="3" y="9" width="18" height="12" rx="2.5"/><path d="M3 9l2.2-5 4.2 1.2M9.4 5.2L13.6 6.4M13.6 6.4L17.8 7.6M7 9l-1-4M12 9l-1-3M17 9l-1-3"/></svg>')


def _md(html: str) -> None:
    st.markdown("\n".join(l.strip() for l in html.strip().splitlines() if l.strip()), unsafe_allow_html=True)


def _parse(h) -> datetime:
    try:
        return datetime.strptime(h["date"], "%d/%m/%Y %H:%M")
    except Exception:
        return datetime.min


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def render_historique(user: str, tier: int) -> None:
    t = theme_tokens()
    css = _CSS
    for k, v in t.items():
        css = css.replace(f"@{k}@", v)
    style_tag = f"<style>{css}</style>"

    hist = get_history(user) or []
    favs = set(load_favs(user) or [])
    week_ago = datetime.now() - timedelta(days=7)
    n_week = sum(1 for h in hist if _parse(h) >= week_ago)

    # ── En-tête ──
    with _keyed("vh_head"):
        c1, c2 = st.columns([3, 2])
        with c1:
            _md(f'{style_tag}<div class="vh-w"><div class="vh-title">{_html.escape(T("hist_title"))}</div>'
                f'<div class="vh-sub">{_html.escape(T("hist_sub"))}</div></div>')
        with c2:
            with _keyed("vh_new"):
                if st.button(f"＋ {T('m_analyse')}", key="hist_new", type="primary"):
                    st.session_state.result = None; st.session_state.page = "analyse"; st.rerun()

    # ── Chiffres ──
    _md(f'''<div class="vh-w"><div class="vh-kpis">
      <div class="vh-kpi"><small>{_html.escape(T("total"))}</small><b>{len(hist)}</b></div>
      <div class="vh-kpi"><small>{_html.escape(T("this_week"))}</small><b>{n_week}</b></div>
      <div class="vh-kpi"><small>{_html.escape(T("favs"))}</small><b>{len(favs)}</b></div>
    </div></div>''')

    # ── Filtres ──
    opt_all, opt_fav, opt_week = "Tout", T("favs"), T("this_week")
    with _keyed("vh_pills"):
        flt = st.radio("Filtre", [opt_all, opt_fav, opt_week], horizontal=True,
                       label_visibility="collapsed", key="hist_filter")

    q = ""
    if tier >= 2:
        q = st.text_input(T("search_ph"), placeholder=T("search_ph"), label_visibility="collapsed", key="hist_search").strip().lower()
    elif hist:
        _md(f'<div class="vh-w"><div class="vh-sub" style="margin:0 0 .8rem">🔒 {_html.escape(T("search_ph"))} — Premium</div></div>')
    if tier == 0 and len(hist) > 10:
        _md(f'<div class="vh-w"><div class="vh-sub" style="margin:0 0 .8rem">{_html.escape(T("plan_free"))} : 10 / {len(hist)}</div></div>')

    shown = []
    for h in hist:
        if flt == opt_fav and h.get("video_id") not in favs: continue
        if flt == opt_week and _parse(h) < week_ago: continue
        if q and q not in str(h).lower(): continue
        shown.append(h)

    # ── État vide ──
    if not shown:
        if hist:
            title, text = "Aucun résultat", "Aucune analyse ne correspond à ce filtre."
        else:
            title, text = "Aucune analyse pour l'instant", "Lancez votre première analyse, elle apparaîtra ici."
        _md(f'<div class="vh-w"><div class="vh-empty"><div class="ic">{_EMPTY_ICON}</div><h3>{title}</h3><p>{text}</p></div></div>')
        with _keyed("vh_empty_cta"):
            if st.button("Analyser ma première vidéo" if not hist else "Voir tout", key="hist_empty_cta", type="primary", use_container_width=True):
                if hist:
                    st.session_state.hist_filter = opt_all; st.rerun()
                st.session_state.result = None; st.session_state.page = "analyse"; st.rerun()
        render_footer(compact=True)
        return

    # ── Liste ──
    for i, h in enumerate(shown):
        vid = h.get("video_id", "")
        is_fav = vid in favs
        title = _html.escape(h.get("title") or f"Résumé — {vid}")
        meta = (f'{h.get("date","")} • {str(h.get("lang","")).upper()} • '
                f'{h.get("total_words",0):,} {T("words")} • {h.get("processing_time",0)} s')
        thumb = (f'<img src="https://i.ytimg.com/vi/{_html.escape(vid)}/mqdefault.jpg" alt="" loading="lazy">') if vid else ""
        _md(f'''<div class="vh-w"><div class="vh-card">
          <div class="vh-thumb">▶{thumb}</div>
          <div class="vh-meta"><b>{title}</b><small>{_html.escape(meta)}</small></div>
          <div class="vh-star">{"⭐" if is_fav else ""}</div>
        </div></div>''')
        with _keyed(f"hc_{i}"):
            b1, b2 = st.columns([4, 1])
            with b1:
                if st.button(T("open_analyse"), key=f"open_{vid}_{h.get('date','')}_{i}", use_container_width=True):
                    st.session_state.result = h; st.session_state.page = "analyse"; st.rerun()
            with b2:
                if st.button("⭐" if is_fav else "☆", key=f"fav_{vid}_{h.get('date','')}_{i}", use_container_width=True, help=T("add_fav")):
                    toggle_fav(user, vid); st.rerun()

    st.markdown("---")
    if st.button(T("clear_hist"), use_container_width=True, key="hist_clear"):
        clear_history(user); st.rerun()
    render_footer(compact=True)