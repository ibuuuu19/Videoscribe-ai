"""
Helpers du Studio — Fonctions utilitaires pour la page Analyse.

Contient :
- _first_sentence : Extraire la première phrase d'un texte
- _studio_score : Calculer un score de qualité (0-100)
- _render_lock : Afficher un message "réservé aux Premium"
- _studio_md : Exporter le résumé en Markdown
- export_presentation : Générer une présentation HTML (slides)

Extrait de app.py pour alléger le fichier principal (~250 lignes).

Usage:
    from src.pages.studio_utils import _first_sentence, _studio_score
"""

import re
import html as _html

import streamlit as st

from src.ui.i18n import I18N
from src.ui.components import ic
from src.ui.utils import better_extract_action_points, _short


# ═══════════════════════════════════════════════════════════════
# HELPERS DE TEXTE
# ═══════════════════════════════════════════════════════════════

def _first_sentence(text, max_len=190):
    """Extrait la première phrase d'un texte (ou tronque proprement)."""
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if not text:
        return "—"
    parts = re.split(r"(?<=[.!?])\s+", text)
    s = parts[0] if parts else text
    if len(s) > max_len:
        s = s[:max_len].rsplit(" ", 1)[0] + "…"
    return s


def _studio_score(data):
    """Calcule un score de qualité du résumé (0-100)."""
    notes = data.get("notes", [])
    kws = data.get("keywords", [])
    qs = data.get("questions", [])
    words = data.get("total_words", 0)
    score = 50
    if len(notes) >= 3: score += 15
    if len(kws) >= 5: score += 12
    if len(qs) >= 3: score += 10
    if words >= 1000: score += 8
    if data.get("processing_time", 0) and data.get("processing_time", 0) < 90: score += 5
    return min(score, 100)


def _render_lock(title, subtitle="Réservé aux abonnés Premium."):
    """Affiche un message 'réservé aux Premium'."""
    st.markdown(f"""<div class="vs-lock-card">
    <span>{ic("lock", 18)}</span>
    <div><b>{title}</b><br><small>{subtitle}</small></div>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

def _studio_md(data):
    """Génère le rapport Studio complet en Markdown."""
    kws = ", ".join([k for k, _ in data.get("keywords", [])[:10]]) or "—"
    txt = f"# {data.get('title', 'Résumé VideoScribe AI')}\n\n"
    txt += f"- Vidéo : https://youtu.be/{data.get('video_id')}\n- Date : {data.get('date')}\n"
    txt += f"- Langue : {data.get('lang', '').upper()}\n- Mots : {data.get('total_words', 0):,}\n- Mots-clés : {kws}\n\n"
    txt += "## Synthèse rapide\n"
    for note in data.get("notes", [])[:4]:
        txt += f"- {_first_sentence(note, 220)}\n"
    txt += "\n## Notes structurées\n"
    for i, note in enumerate(data.get("notes", []), 1):
        txt += f"\n### Section {i}\n{note}\n"
    if data.get("questions"):
        txt += "\n## Questions à explorer\n"
        for q in data["questions"]:
            txt += f"- {q}\n"
    return txt


def export_presentation(data):
    """Génère une présentation HTML (slides) à partir des notes."""
    li = st.session_state.get("cfg_lang", "fr")
    def _tt(k):
        return I18N.get(li, {}).get(k) or I18N["fr"].get(k) or k
    title = _html.escape(data.get("title", "Résumé VideoScribe AI"))
    date = data.get("date", "")
    lang = (data.get("lang") or "unknown").upper()
    words = data.get("total_words", 0)
    notes = data.get("notes", [])
    keywords = data.get("keywords", [])
    questions = data.get("questions", [])
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
    n = len(slides)
    body = "".join(slides)
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