"""
Page Studio — Analyse de vidéos YouTube.

Contient le Studio complet (formulaire URL, panneau Premium,
pipeline d'analyse, affichage des résultats).

Extrait de app.py pour alléger le fichier principal (~563 lignes).

Usage:
    from src.pages.studio import render_studio_page
"""

import json
import time
from datetime import datetime
from pathlib import Path
import html as _html

import streamlit as st
import streamlit.components.v1 as _components

from src.ui.i18n import T, LANGS
from src.ui.components import ic
from src.ui.css import shade
from src.ui.layout import get_accent, render_footer
from src.ui.storage import load_favs, toggle_fav, save_share, export_anki, generate_audio
from src.ui.utils import (
    build_quiz, answer_question, better_extract_action_points,
    better_extract_keywords, better_generate_questions, clean_summary,
)
from src.pages.studio_utils import (
    _first_sentence, _studio_score, _render_lock, _studio_md, export_presentation,
)
from src.core.config import HIST_KEEP, FREE_DAILY_LIMIT
from src.user_manager import get_tier
from src.transcript_extractor import extract_video_id, get_transcript
from src.text_processor import chunk_text, remove_repetitions, polish_translation
from src.summarizer import VideoSummarizer, MODELS
from src.translator import translate_texts
from src.history_manager import save_analysis, count_today, trim_history
from src.export_utils import export_to_markdown, export_to_pdf, export_to_obsidian, export_to_notion


@st.cache_resource
def get_summarizer(model_key):
    """Instance du summarizer (caché)."""
    return VideoSummarizer(MODELS[model_key], model_key=model_key)

def _run_one(url_single, chunk_size, turbo, model_choice, translate_to_fr,
             num_keywords, num_questions, extract_kw, generate_qa, tier):
    """Traite une vidéo (utilisé en batch)."""
    video_id = extract_video_id(url_single)
    if not video_id:
        return None
    transcript, lang = get_transcript(video_id)
    if transcript.startswith("Error"):
        return None
    ch = chunk_text(transcript, chunk_size=chunk_size)
    # ⚡ Plus de pré-traduction : le summarizer gère la traduction à la volée
    beams = 1 if turbo else 3
    cache_notes = Path("cache") / f"notes_{video_id}_{model_choice}_b{beams}.json"
    if cache_notes.exists():
        notes = json.loads(cache_notes.read_text(encoding="utf-8"))
    else:
        summarizer = get_summarizer(model_choice)
        # ✅ On passe src_lang et translate_to_en au summarizer
        notes = summarizer.summarize_video(
            ch,
            progress_callback=lambda i, t: None,
            batch_size=6,
            num_beams=beams,
            src_lang=lang,
            translate_to_en=(lang != "en"),
        )
        cache_notes.parent.mkdir(parents=True, exist_ok=True)
        cache_notes.write_text(json.dumps(notes, ensure_ascii=False), encoding="utf-8")
    notes = [clean_summary(remove_repetitions(n)) for n in notes]
    if translate_to_fr:
        target = st.session_state.cfg_target if tier >= 3 else "fr"
        # ✅ Filtrer les None après polish_translation
        translated = translate_texts(notes, src="en", dest=target)
        notes = [polish_translation(n) if n else n for n in translated]
    kws = better_extract_keywords(transcript, top_n=num_keywords, lang=lang) if extract_kw else []
    qs = better_generate_questions(
        notes, keywords=kws, n=num_questions,
        lang=st.session_state.get("cfg_lang", "fr")
    ) if generate_qa else []
    return {
        "video_id": video_id, "url": url_single,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "lang": lang or "unknown", "num_chunks": len(ch),
        "total_chars": len(transcript), "total_words": len(transcript.split()),
        "processing_time": 0, "title": f"Résumé - {video_id}", "author": "",
        "notes": notes, "keywords": kws, "questions": qs,
    }


# ═══════════════════════════════════════════════════════════════
# ⚠️ Le reste du Studio a été copié automatiquement par extract_studio.py
# ═══════════════════════════════════════════════════════════════

def render_studio_page():
    """Affiche la page Studio complète (analyse + résultats)."""
    # ═══ Variables locales ═══
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    is_guest = role == "visiteur"
    tier = 3 if role == "admin" else (0 if is_guest else get_tier(user))

    # ═══ Configuration depuis session_state ═══
    translate_to_fr = st.session_state.cfg_translate
    extract_kw = st.session_state.cfg_kw
    generate_qa = st.session_state.cfg_qa
    model_choice = st.session_state.cfg_model
    turbo = st.session_state.cfg_turbo
    num_keywords = st.session_state.cfg_kw_n
    num_questions = st.session_state.cfg_q_n
    chunk_size = st.session_state.cfg_chunk

    # ═══ État du Studio ═══
    if st.query_params.get("nlhide") == "1":
        st.session_state.nl_hide = True
    if "studio_panel_open" not in st.session_state:
        st.session_state.studio_panel_open = True

    # ═══ Code du Studio (extrait de app.py) ═══
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

    # ⚠️ _first_sentence, _studio_score, _render_lock, _studio_md extraits dans src/pages/studio_utils.py
    # ⚠️ export_presentation extrait dans src/pages/studio_utils.py
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
                st.selectbox("Langue de sortie", ["fr","en","es","de"], key="cfg_target", format_func=lambda l: str(LANGS.get(l) or l))
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

        # ⚡ Traduction à la volée (pas de pré-traduction)
        if lang != "en":
            _step(ph_tr, "lang", f"Traduction {lang} → EN à la volée", "run")
        else:
            _step(ph_tr, "lang", "Traduction source non nécessaire", "wait")
        
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
                notes = summarizer.summarize_video(
                    chunks,
                    progress_callback=update_progress,
                    batch_size=6,
                    num_beams=beams,
                    src_lang=lang,
                    translate_to_en=(lang != "en"),
                )
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