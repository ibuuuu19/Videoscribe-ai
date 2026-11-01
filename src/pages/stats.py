"""
Page « Statistiques » — tableau de bord premium.

· En-tête avec sélecteur de période (7 j / 30 j / Tout) : tous les chiffres suivent la période choisie
· 4 cartes KPI : tendance vs période précédente + mini-courbe
· Graphique d'activité (analyses / mots / temps) par jour, avec jour courant mis en avant
· Rythme hebdomadaire (heatmap), séries (jours consécutifs), jour le plus actif, débit
· Records et dernières analyses (Premium+), rapport hebdomadaire téléchargeable (Premium+)
· Les fonctions verrouillées selon le plan montrent un aperçu + accès direct aux formules

Appel : render_stats(user, tier, history)   (history = get_history(user), liste de dicts)
"""
from collections import Counter
from datetime import datetime, timedelta, date

import streamlit as st

from src.ui.i18n import T
from src.ui.mobile import theme_tokens

_L = {
    "fr": dict(sub="Votre activité en un coup d'œil", p7="7 jours", p30="30 jours", pall="Tout", vs7="vs 7 j précédents", vs30="vs 30 j précédents",
               n="Analyses", w="Mots", t="Temps", avg="Temps moyen", activity="Activité", rhythm="Rythme hebdomadaire", rhythm_s="Vos jours les plus actifs",
               insights="À retenir", streak="Série en cours", days="jours", best="Jour le plus actif", thr="Débit de traitement", wpm="mots / min",
               records="Records", fastest="Plus rapide", slowest="Plus lente", mean="Moyenne", recent="Dernières analyses", empty_t="Aucune analyse pour l'instant",
               empty_d="Analysez votre première vidéo pour voir apparaître vos statistiques.", go="Analyser une vidéo", lock_rec="Records & détails par vidéo",
               lock_rec_d="Plus rapide, plus lente, temps moyen et historique détaillé.", lock_wk="Rapport hebdomadaire", lock_wk_d="Résumé de la semaine téléchargeable en un clic.",
               unlock="Débloquer avec", per="sur la période", vid="vidéo", vids="vidéos", none="Aucune activité sur cette période", wk_title="Rapport hebdomadaire (7 j)",
               wk_hint="Exportez votre résumé de la semaine (Markdown).", total="au total", today="Aujourd'hui", good="Excellent", up="en hausse"),
    "en": dict(sub="Your activity at a glance", p7="7 days", p30="30 days", pall="All", vs7="vs previous 7 d", vs30="vs previous 30 d",
               n="Analyses", w="Words", t="Time", avg="Average time", activity="Activity", rhythm="Weekly rhythm", rhythm_s="Your most active days",
               insights="Highlights", streak="Current streak", days="days", best="Most active day", thr="Processing speed", wpm="words / min",
               records="Records", fastest="Fastest", slowest="Slowest", mean="Average", recent="Latest analyses", empty_t="No analyses yet",
               empty_d="Analyze your first video to see your statistics appear.", go="Analyze a video", lock_rec="Records & per-video details",
               lock_rec_d="Fastest, slowest, average time and detailed history.", lock_wk="Weekly report", lock_wk_d="Download your weekly summary in one click.",
               unlock="Unlock with", per="over the period", vid="video", vids="videos", none="No activity in this period", wk_title="Weekly report (7 d)",
               wk_hint="Export your weekly summary (Markdown).", total="total", today="Today", good="Great", up="up"),
    "es": dict(sub="Tu actividad de un vistazo", p7="7 días", p30="30 días", pall="Todo", vs7="vs 7 d anteriores", vs30="vs 30 d anteriores",
               n="Análisis", w="Palabras", t="Tiempo", avg="Tiempo medio", activity="Actividad", rhythm="Ritmo semanal", rhythm_s="Tus días más activos",
               insights="Claves", streak="Racha actual", days="días", best="Día más activo", thr="Velocidad de proceso", wpm="palabras / min",
               records="Récords", fastest="Más rápido", slowest="Más lento", mean="Media", recent="Últimos análisis", empty_t="Aún no hay análisis",
               empty_d="Analiza tu primer vídeo para ver tus estadísticas.", go="Analizar un vídeo", lock_rec="Récords y detalle por vídeo",
               lock_rec_d="Más rápido, más lento, tiempo medio e historial detallado.", lock_wk="Informe semanal", lock_wk_d="Descarga tu resumen semanal con un clic.",
               unlock="Desbloquear con", per="en el periodo", vid="vídeo", vids="vídeos", none="Sin actividad en este periodo", wk_title="Informe semanal (7 d)",
               wk_hint="Exporta tu resumen semanal (Markdown).", total="en total", today="Hoy", good="Excelente", up="al alza"),
    "de": dict(sub="Ihre Aktivität auf einen Blick", p7="7 Tage", p30="30 Tage", pall="Alle", vs7="vs. vorherige 7 T", vs30="vs. vorherige 30 T",
               n="Analysen", w="Wörter", t="Zeit", avg="Ø Zeit", activity="Aktivität", rhythm="Wochenrhythmus", rhythm_s="Ihre aktivsten Tage",
               insights="Highlights", streak="Aktuelle Serie", days="Tage", best="Aktivster Tag", thr="Verarbeitungstempo", wpm="Wörter / Min",
               records="Rekorde", fastest="Schnellste", slowest="Langsamste", mean="Durchschnitt", recent="Letzte Analysen", empty_t="Noch keine Analysen",
               empty_d="Analysieren Sie Ihr erstes Video, um Statistiken zu sehen.", go="Video analysieren", lock_rec="Rekorde & Details pro Video",
               lock_rec_d="Schnellste, langsamste, Ø Zeit und detaillierter Verlauf.", lock_wk="Wochenbericht", lock_wk_d="Wochenzusammenfassung mit einem Klick herunterladen.",
               unlock="Freischalten mit", per="im Zeitraum", vid="Video", vids="Videos", none="Keine Aktivität in diesem Zeitraum", wk_title="Wochenbericht (7 T)",
               wk_hint="Exportieren Sie Ihre Wochenzusammenfassung (Markdown).", total="insgesamt", today="Heute", good="Ausgezeichnet", up="steigend"),
}
_DAYS = {"fr": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"], "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
         "es": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"], "de": ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]}
_DAYS_LONG = {"fr": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"], "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
              "es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"], "de": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]}
_PLAN = {2: "Premium", 3: "Premium+"}

_ICON = {
    "film": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M8 4v16M16 4v16M3 9h5M3 15h5M16 9h5M16 15h5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "text": '<path d="M5 6h14M5 12h14M5 18h9"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "fire": '<path d="M12 3c1 3 4 4.5 4 8.5A4 4 0 0112 16a4 4 0 01-4-4c0-1.5.7-2.6 1.6-3.6C10.5 10 11 9 11 8c0-1.3.3-3.2 1-5z"/><path d="M8 19h8"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4M16 3v4M3 10h18"/>',
    "gauge": '<path d="M4 16a8 8 0 1116 0"/><path d="M12 16l4-5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="3"/><path d="M8 11V8a4 4 0 118 0v3"/>',
    "dl": '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
}


def _svg(name: str, size: int = 20, sw: float = 1.9) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" style="flex:none">{_ICON[name]}</svg>')


def _lang() -> str:
    l = st.session_state.get("cfg_lang", "fr")
    return l if l in _L else "fr"


def _pdate(h):
    try:
        return datetime.strptime(h["date"], "%d/%m/%Y %H:%M")
    except Exception:
        return datetime.min


def _fmt_dur(s: float) -> str:
    s = int(round(s or 0))
    if s < 60:
        return f"{s} s"
    if s < 3600:
        return f"{s // 60} min {s % 60:02d} s"
    return f"{s // 3600} h {(s % 3600) // 60:02d} min"


def _fmt_n(n) -> str:
    return f"{int(n):,}".replace(",", " ")


def _spark(vals, color_id: str) -> str:
    vals = list(vals) or [0]
    if len(vals) == 1:
        vals = vals * 2
    if len(vals) > 4:   # lissage (moyenne glissante sur 3 points) : courbe lisible, pas en dents de scie
        vals = [sum(vals[max(0, i - 1): i + 2]) / len(vals[max(0, i - 1): i + 2]) for i in range(len(vals))]
    mx = max(vals) or 1
    w, h = 120, 36
    step = w / (len(vals) - 1)
    pts = [(i * step, h - 4 - (v / mx) * (h - 10)) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"0,{h} " + line + f" {w},{h}"
    return (f'<svg class="sx-spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none"><defs><linearGradient id="g{color_id}" x1="0" x2="0" y1="0" y2="1">'
            f'<stop offset="0" stop-color="currentColor" stop-opacity=".35"/><stop offset="1" stop-color="currentColor" stop-opacity="0"/></linearGradient></defs>'
            f'<polygon points="{area}" fill="url(#g{color_id})"/><polyline points="{line}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _delta(cur, prev, label, lower_is_better=False):
    if prev is None:
        return ""
    if prev <= 0:
        if cur <= 0:
            return '<span class="sx-chip flat">—</span>'
        return '<span class="sx-chip up">↑ new</span>'
    pct = (cur - prev) / prev * 100
    if abs(pct) < 0.5:
        return f'<span class="sx-chip flat">= {label}</span>'
    good = (pct < 0) if lower_is_better else (pct > 0)
    arrow = "↑" if pct > 0 else "↓"
    txt = f"{abs(pct):.0f}%" if abs(pct) <= 300 else ("+300%" if pct > 0 else "−100%")
    return f'<span class="sx-chip {"up" if good else "down"}">{arrow} {txt} <i>{label}</i></span>'


def _css() -> None:
    t = theme_tokens()
    dark = st.session_state.get("theme", "light") != "light"
    acc, accd = t["acc"], t["acc_dark"]
    card = "linear-gradient(160deg,rgba(255,255,255,.075),rgba(255,255,255,.028))" if dark else "linear-gradient(160deg,#FFFFFF,#F4F8FF)"
    flat = "rgba(255,255,255,.045)" if dark else "#F3F7FD"
    hov = "0 20px 44px rgba(0,0,0,.45)" if dark else "0 20px 44px rgba(30,70,140,.16)"
    st.markdown(f"""<style>
.sx-root{{ --acc:{acc}; --accd:{accd}; --ink:{t["ink"]}; --soft:{t["soft"]}; --line:{t["line"]}; --flat:{flat}; }}
html body .stApp .sx-title{{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.7rem; letter-spacing:-.03em; color:{t["ink"]} !important; display:flex; align-items:center; gap:14px; line-height:1.15; }}
html body .stApp .sx-logo{{ width:52px; height:52px; border-radius:17px; display:flex; align-items:center; justify-content:center; color:#fff; flex:none; background:linear-gradient(135deg,{acc},{accd}); box-shadow:0 12px 26px color-mix(in srgb,{acc} 40%,transparent); }}
html body .stApp .sx-sub{{ color:{t["soft"]} !important; font-size:.92rem; margin:.25rem 0 0; }}
html body .stApp .sx-title{{ margin-bottom:.9rem; }}
html body .stApp div[data-testid="stVerticalBlock"].st-key-sx_head{{ background:{card} !important; border:1px solid {t["line"]} !important; border-radius:26px !important; padding:1.3rem 1.4rem !important;
  box-shadow:{t["shadow"]} !important; position:relative; overflow:hidden; }}
html body .stApp div[data-testid="stVerticalBlock"].st-key-sx_head::after{{ content:""; position:absolute; right:-70px; top:-90px; width:300px; height:300px; border-radius:50%; background:radial-gradient(circle,color-mix(in srgb,{acc} 26%,transparent),transparent 70%); pointer-events:none; }}
html body .stApp .st-key-sx_head [data-testid="stHorizontalBlock"]{{ align-items:center; }}
/* KPI */
.sx-kpis{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(215px,1fr)); gap:1rem; margin:1.1rem 0 1.1rem; }}
.sx-kpi{{ position:relative; overflow:hidden; background:{card}; border:1px solid {t["line"]}; border-radius:24px; padding:1.15rem 1.2rem 1rem; box-shadow:{t["shadow"]}; transition:transform .2s ease, box-shadow .2s ease, border-color .2s ease; }}
.sx-kpi:hover{{ transform:translateY(-4px); box-shadow:{hov}; border-color:color-mix(in srgb,{acc} 45%,{t["line"]}); }}
.sx-kpi::before{{ content:""; position:absolute; left:0; right:0; top:0; height:3px; background:linear-gradient(90deg,var(--c,{acc}),transparent 85%); }}
.sx-kh{{ display:flex; align-items:center; justify-content:space-between; gap:10px; }}
.sx-ki{{ width:42px; height:42px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,var(--c,{acc}),color-mix(in srgb,var(--c,{acc}) 60%,#000)); box-shadow:0 8px 18px color-mix(in srgb,var(--c,{acc}) 38%,transparent); }}
.sx-kl{{ font-size:.7rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:{t["soft"]}; }}
.sx-kv{{ font-family:'Sora',sans-serif; font-weight:800; font-size:2.1rem; letter-spacing:-.035em; color:{t["ink"]}; margin:.8rem 0 .25rem; line-height:1.05; font-variant-numeric:tabular-nums; }}
.sx-kv small{{ font-size:.95rem; font-weight:700; color:{t["soft"]}; letter-spacing:0; margin-left:4px; }}
.sx-kf{{ display:flex; align-items:flex-end; justify-content:space-between; gap:10px; min-height:40px; }}
.sx-spark{{ width:118px; height:38px; color:var(--c,{acc}); flex:none; }}
.sx-chip{{ display:inline-flex; align-items:center; gap:5px; padding:.28rem .6rem; border-radius:999px; font-size:.76rem; font-weight:800; white-space:nowrap; }}
.sx-chip i{{ font-style:normal; font-weight:600; opacity:.8; }}
.sx-chip.up{{ background:rgba(16,185,129,.15); color:{"#34D399" if dark else "#047857"}; }}
.sx-chip.down{{ background:rgba(239,68,68,.14); color:{"#F87171" if dark else "#B91C1C"}; }}
.sx-chip.flat{{ background:{flat}; color:{t["soft"]}; }}
/* Cartes génériques */
.sx-card{{ position:relative; background:{card}; border:1px solid {t["line"]}; border-radius:24px; padding:1.2rem 1.3rem 1.25rem; box-shadow:{t["shadow"]}; }}
.sx-ch{{ display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:.9rem; flex-wrap:wrap; }}
.sx-ct{{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.05rem; letter-spacing:-.02em; color:{t["ink"]}; display:flex; align-items:center; gap:10px; }}
.sx-ct::before{{ content:""; width:5px; height:1.05em; border-radius:3px; background:linear-gradient(180deg,{acc},{accd}); }}
.sx-cs{{ font-size:.8rem; color:{t["soft"]}; }}
/* Graphique */
.sx-chart{{ position:relative; height:250px; display:flex; align-items:flex-end; gap:clamp(3px,.6vw,9px); padding:6px 0 26px 38px; }}
.sx-grid{{ position:absolute; left:38px; right:0; top:6px; bottom:26px; pointer-events:none; }}
.sx-grid i{{ position:absolute; left:0; right:0; border-top:1px dashed {t["line"]}; }}
.sx-grid b{{ position:absolute; left:-38px; width:30px; text-align:right; transform:translateY(-50%); font-size:.68rem; font-weight:700; color:{t["soft"]}; }}
.sx-col{{ position:relative; flex:1; height:100%; display:flex; align-items:flex-end; justify-content:center; min-width:0; }}
.sx-bar{{ width:100%; max-width:34px; border-radius:9px 9px 4px 4px; background:linear-gradient(180deg,color-mix(in srgb,{acc} 70%,#fff),{acc} 55%,{accd}); transform-origin:bottom; animation:sxrise .6s cubic-bezier(.2,.8,.2,1) both; position:relative; transition:filter .15s ease, transform .15s ease; }}
.sx-col:hover .sx-bar{{ filter:brightness(1.15) saturate(1.1); transform:scaleY(1.02); }}
.sx-bar.zero{{ height:3px !important; background:{t["line"]}; border-radius:3px; }}
.sx-bar.today{{ background:linear-gradient(180deg,#FDE68A,#F59E0B); box-shadow:0 0 0 3px color-mix(in srgb,#F59E0B 22%,transparent); }}
.sx-tip{{ position:absolute; bottom:calc(100% + 8px); left:50%; transform:translateX(-50%) translateY(4px); background:{"#0B1220" if dark else "#0F1A2E"}; color:#fff; font-size:.72rem; font-weight:700; padding:.35rem .6rem; border-radius:10px; white-space:nowrap; opacity:0; pointer-events:none; transition:all .15s ease; z-index:5; box-shadow:0 8px 20px rgba(0,0,0,.3); }}
.sx-col:hover .sx-tip{{ opacity:1; transform:translateX(-50%) translateY(0); }}
.sx-lbl{{ position:absolute; bottom:-22px; left:50%; transform:translateX(-50%); font-size:.66rem; font-weight:700; color:{t["soft"]}; white-space:nowrap; }}
@keyframes sxrise{{ from{{ transform:scaleY(0); }} to{{ transform:scaleY(1); }} }}
.sx-empty-c{{ height:250px; display:flex; align-items:center; justify-content:center; color:{t["soft"]}; font-size:.9rem; }}
html body .stApp div[data-testid="stVerticalBlock"].st-key-sx_chartcard{{ background:{card} !important; border:1px solid {t["line"]} !important; border-radius:24px !important; padding:1.2rem 1.3rem 1.1rem !important; box-shadow:{t["shadow"]} !important; margin-top:0; }}
html body .stApp [class*="st-key-sx_"] [data-baseweb="button-group"] button[kind="segmented_controlActive"], html body .stApp [class*="st-key-sx_"] button[aria-checked="true"]{{ background:linear-gradient(135deg,{acc},{accd}) !important; color:#fff !important; border-color:transparent !important; }}
html body .stApp [class*="st-key-sx_"] [data-baseweb="button-group"] button[kind="segmented_controlActive"] p{{ color:#fff !important; }}
html body .stApp [class*="st-key-sx_"] [data-baseweb="button-group"] button{{ border-radius:12px !important; font-weight:700 !important; }}
html body .stApp [class*="st-key-sx_"] button[aria-checked="false"]{{ background:{flat} !important; color:{t["ink"]} !important; border:1px solid {t["line"]} !important; }}
html body .stApp [class*="st-key-sx_"] button[aria-checked="false"] p{{ color:{t["ink"]} !important; }}
html body .stApp [class*="st-key-sx_"] button[aria-checked="false"]:hover{{ border-color:{acc} !important; }}
/* rangée 2 */
.sx-row{{ display:grid; grid-template-columns:1.25fr 1fr; gap:1rem; margin-top:1rem; }}
@media (max-width:900px){{ .sx-row{{ grid-template-columns:1fr; }} .sx-kv{{ font-size:1.8rem; }} }}
@media (max-width:600px){{ .sx-kpis{{ grid-template-columns:1fr 1fr; gap:.7rem; }} .sx-kpi{{ padding:.9rem .9rem .8rem; border-radius:20px; }} .sx-kv{{ font-size:1.4rem; margin:.6rem 0 .3rem; }}
  .sx-spark{{ display:none; }} .sx-kf{{ min-height:0; }} .sx-ki{{ width:34px; height:34px; border-radius:11px; }} .sx-chip i{{ display:none; }} .sx-chip{{ font-size:.7rem; padding:.22rem .5rem; }}
  .sx-title{{ font-size:1.4rem; }} .sx-logo{{ width:44px; height:44px; border-radius:14px; }} .sx-chart{{ padding-left:30px; }} .sx-grid{{ left:30px; }} .sx-grid b{{ left:-30px; width:24px; font-size:.6rem; }} }}
.sx-rowc{{ display:flex; flex-direction:column; }}
.sx-heat{{ display:grid; grid-template-columns:repeat(7,1fr); gap:.5rem; flex:1; }}
.sx-hc{{ text-align:center; display:flex; flex-direction:column; }}
.sx-leg{{ display:flex; align-items:center; gap:8px; justify-content:flex-end; margin-top:1rem; font-size:.72rem; font-weight:700; color:{t["soft"]}; }}
.sx-leg i{{ width:70px; height:8px; border-radius:4px; background:linear-gradient(90deg,color-mix(in srgb,{acc} 6%,{flat}),{acc}); }}
.sx-hb{{ flex:1; min-height:74px; border-radius:14px; background:color-mix(in srgb,{acc} calc(var(--i,0) * 88% + 6%),{flat}); display:flex; align-items:center; justify-content:center; font-weight:800; font-size:.95rem;
  color:{t["ink"]}; border:1px solid {t["line"]}; transition:transform .15s ease; }}
.sx-hb:hover{{ transform:translateY(-3px); }}
.sx-hd{{ margin-top:.45rem; font-size:.72rem; font-weight:700; color:{t["soft"]}; }}
.sx-ins{{ display:flex; flex-direction:column; gap:.7rem; }}
.sx-in{{ display:flex; align-items:center; gap:14px; padding:.85rem 1rem; border-radius:18px; background:{flat}; border:1px solid {t["line"]}; }}
.sx-ii{{ width:40px; height:40px; border-radius:13px; display:flex; align-items:center; justify-content:center; flex:none; color:#fff; background:linear-gradient(135deg,var(--c),color-mix(in srgb,var(--c) 60%,#000)); }}
.sx-il{{ font-size:.72rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:{t["soft"]}; }}
.sx-iv{{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.15rem; color:{t["ink"]}; letter-spacing:-.02em; }}
/* records & liste */
.sx-rec{{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:.8rem; }}
.sx-r{{ padding:.95rem 1rem; border-radius:18px; background:{flat}; border:1px solid {t["line"]}; }}
.sx-rv{{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.5rem; color:{t["ink"]}; margin-top:.3rem; letter-spacing:-.03em; }}
.sx-list{{ display:flex; flex-direction:column; gap:.55rem; }}
.sx-li{{ display:grid; grid-template-columns:auto minmax(0,1fr) auto; align-items:center; gap:14px; padding:.75rem .9rem; border-radius:16px; background:{flat}; border:1px solid {t["line"]}; transition:transform .15s ease, border-color .15s ease; }}
.sx-li:hover{{ transform:translateX(3px); border-color:color-mix(in srgb,{acc} 50%,{t["line"]}); }}
.sx-lk{{ width:38px; height:38px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,{acc},{accd}); font-weight:800; font-size:.78rem; }}
.sx-lt{{ font-weight:700; font-size:.9rem; color:{t["ink"]}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.sx-lt a{{ color:inherit !important; text-decoration:none; }}
.sx-lt a:hover{{ color:{acc} !important; }}
.sx-ld{{ font-size:.74rem; color:{t["soft"]}; margin-top:2px; }}
.sx-lb{{ height:5px; border-radius:3px; background:{t["line"]}; overflow:hidden; margin-top:6px; }}
.sx-lb i{{ display:block; height:100%; border-radius:3px; background:linear-gradient(90deg,{acc},{accd}); }}
.sx-lr{{ text-align:right; font-weight:800; font-size:.88rem; color:{t["ink"]}; font-variant-numeric:tabular-nums; }}
.sx-lr small{{ display:block; font-weight:600; font-size:.72rem; color:{t["soft"]}; }}
/* verrouillé / vide */
.sx-lock{{ display:flex; align-items:center; gap:16px; flex-wrap:wrap; }}
.sx-lki{{ width:52px; height:52px; border-radius:17px; display:flex; align-items:center; justify-content:center; color:#3A2A00; background:linear-gradient(135deg,#F5D27A,#D4AF37); flex:none; }}
.sx-lkt{{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.05rem; color:{t["ink"]}; }}
.sx-lkd{{ font-size:.85rem; color:{t["soft"]}; margin-top:2px; }}
.sx-plan{{ font-size:.6rem; font-weight:900; letter-spacing:.08em; text-transform:uppercase; padding:.16rem .5rem; border-radius:999px; background:linear-gradient(135deg,#F5D27A,#D4AF37); color:#3A2A00; margin-left:8px; vertical-align:middle; }}
.sx-blur{{ filter:blur(5px) saturate(.8); opacity:.55; pointer-events:none; user-select:none; }}
.sx-emptyc{{ text-align:center; padding:3rem 1rem; }}
.sx-emptyc .sx-logo{{ margin:0 auto 1rem; }}
/* widgets */
html body .stApp .st-key-sx_period [data-baseweb="button-group"], html body .stApp .st-key-sx_metric [data-baseweb="button-group"]{{ gap:.25rem; }}
html body .stApp .st-key-sx_go button, html body .stApp [class*="st-key-sx_up_"] button{{ border-radius:14px !important; font-weight:800 !important; min-height:2.8rem; }}
html body .stApp .st-key-sx_go button, html body .stApp [class*="st-key-sx_up_"] button[kind="primary"]{{ background:linear-gradient(135deg,{acc},{accd}) !important; color:#fff !important; border:0 !important; box-shadow:0 10px 24px color-mix(in srgb,{acc} 35%,transparent); }}
html body .stApp .st-key-sx_dl button{{ border-radius:14px !important; font-weight:800 !important; min-height:2.9rem; background:linear-gradient(135deg,{acc},{accd}) !important; color:#fff !important; border:0 !important; box-shadow:0 10px 24px color-mix(in srgb,{acc} 35%,transparent); }}
</style>""", unsafe_allow_html=True)


def _to_premium() -> None:
    st.session_state.page = "premium"
    st.session_state.show_privacy = False


def _to_studio() -> None:
    st.session_state.page = "analyse"


def _keyed(key):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _lock_card(L, key, title, desc, need):
    st.markdown(f'<div class="sx-card" style="margin-bottom:.7rem"><div class="sx-lock"><div class="sx-lki">{_svg("lock", 24)}</div><div style="flex:1;min-width:200px"><div class="sx-lkt">{title}<span class="sx-plan">{_PLAN[need]}</span></div>'
                f'<div class="sx-lkd">{desc}</div></div></div></div>', unsafe_allow_html=True)
    st.button(f"{L['unlock']} {_PLAN[need]}", key=f"sx_up_{key}", on_click=_to_premium, use_container_width=True, type="primary")


def _segmented(key, options, labels, default):
    fmt = lambda v: labels[v]
    try:
        v = st.segmented_control("p", options, default=default, format_func=fmt, key=key, label_visibility="collapsed")
    except Exception:
        v = st.radio("p", options, index=options.index(default), format_func=fmt, key=key, horizontal=True, label_visibility="collapsed")
    return v or default


def render_stats(user: str, tier: int, hist: list) -> None:
    L = _L[_lang()]
    _css()
    today = date.today()

    # ── En-tête + période ──
    with _keyed("sx_head"):
        c1, c2 = st.columns([1.6, 1])
        with c1:
            st.markdown(f'<div class="sx-title"><span class="sx-logo">{_svg("chart", 26)}</span><span>{T("stats_title")}<div class="sx-sub">{L["sub"]}</div></span></div>', unsafe_allow_html=True)
        with c2:
            period = _segmented("sx_period", ["7", "30", "all"], {"7": L["p7"], "30": L["p30"], "all": L["pall"]}, "30")

    if not hist:
        st.markdown(f'<div class="sx-card sx-emptyc"><div class="sx-logo">{_svg("chart", 26)}</div><div class="sx-lkt">{L["empty_t"]}</div><div class="sx-lkd" style="margin-bottom:1rem">{L["empty_d"]}</div></div>', unsafe_allow_html=True)
        st.button(L["go"], key="sx_go", on_click=_to_studio, use_container_width=True, type="primary")
        return

    # ── Données de la période ──
    P = None if period == "all" else int(period)
    start = today - timedelta(days=P - 1) if P is not None else None
    entries = [(_pdate(h).date(), h) for h in hist]
    cur = [h for d, h in entries if (start is None or d >= start)]
    prev = None
    if P is not None and start is not None:
        ps, pe = start - timedelta(days=P), start
        prev = [h for d, h in entries if ps <= d < pe]
    vs = L["vs7"] if P == 7 else L["vs30"]

    def agg(lst):
        return (len(lst), sum(x.get("processing_time", 0) or 0 for x in lst), sum(x.get("total_words", 0) or 0 for x in lst))

    n, tt, tw = agg(cur)
    pn, ptt, ptw = agg(prev) if prev is not None else (None, None, None)
    avg_t = tt / n if n else 0
    pavg = None if prev is None else ((ptt / pn) if (pn and ptt is not None) else 0)

    # séries journalières (≤ 30 jours) pour mini-courbes et graphique
    span = P if P else 30
    days = [today - timedelta(days=span - 1 - i) for i in range(span)]
    per_day = {d: dict(n=0, w=0, t=0) for d in days}
    for d, h in entries:
        if d in per_day:
            per_day[d]["n"] += 1
            per_day[d]["w"] += h.get("total_words", 0) or 0
            per_day[d]["t"] += h.get("processing_time", 0) or 0

    def series(k):
        return [per_day[d][k] for d in days]

    kpis = [
        ("film", L["n"], f'{_fmt_n(n)}', "", _delta(n, pn, vs), series("n"), "#3B82F6", "a"),
        ("clock", L["t"], _fmt_dur(tt), "", _delta(tt, ptt, vs, True) if prev is not None else "", series("t"), "#8B5CF6", "b"),
        ("text", L["w"], _fmt_n(tw), "", _delta(tw, ptw, vs), series("w"), "#10B981", "c"),
        ("bolt", L["avg"], _fmt_dur(avg_t), "", _delta(avg_t, pavg, vs, True) if prev is not None else "", [per_day[d]["t"] / per_day[d]["n"] if per_day[d]["n"] else 0 for d in days], "#F59E0B", "d"),
    ]
    html = '<div class="sx-kpis">'
    for ic_, lab, val, unit, chip, ser, col, cid in kpis:
        html += (f'<div class="sx-kpi" style="--c:{col}"><div class="sx-kh"><span class="sx-kl">{lab}</span><span class="sx-ki">{_svg(ic_, 20)}</span></div>'
                 f'<div class="sx-kv">{val}</div><div class="sx-kf">{chip or "<span></span>"}{_spark(ser, cid)}</div></div>')
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # ── Graphique d'activité ──
    with _keyed("sx_chartcard"):
        h1, h2 = st.columns([1.4, 1])
        with h1:
            st.markdown(f'<div class="sx-ch" style="margin:0 0 .9rem"><div class="sx-ct">{L["activity"]}</div></div>', unsafe_allow_html=True)
        with h2:
            metric = _segmented("sx_metric", ["n", "w", "t"], {"n": L["n"], "w": L["w"], "t": L["t"]}, "n")
        vals = series(metric)
        mx = max(vals) or 1
        step = 1 if span <= 14 else (2 if span <= 20 else 5)
        grid = "".join(f'<i style="top:{p}%"></i><b style="top:{p}%">{(_fmt_dur(mx * (100 - p) / 100) if metric == "t" else _fmt_n(mx * (100 - p) / 100))}</b>' for p in (0, 25, 50, 75, 100))
        if not any(vals):
            body = f'<div class="sx-empty-c">{L["none"]}</div>'
        else:
            cols = ""
            for i, (d, v) in enumerate(zip(days, vals)):
                hpct = max(v / mx * 100, 0)
                cls = "sx-bar" + (" zero" if v <= 0 else "") + (" today" if d == today else "")
                lab = d.strftime("%d/%m") if (i % step == 0 or d == today) else ""
                tv = _fmt_dur(v) if metric == "t" else _fmt_n(v)
                cols += (f'<div class="sx-col"><div class="{cls}" style="height:{hpct:.1f}%;animation-delay:{i * 12}ms"></div>'
                         f'<span class="sx-tip">{d.strftime("%d/%m/%Y")} · {tv}</span><span class="sx-lbl">{lab}</span></div>')
            body = f'<div class="sx-chart"><div class="sx-grid">{grid}</div>{cols}</div>'
        st.markdown(f'<div style="margin-top:.6rem">{body}</div>', unsafe_allow_html=True)

    # ── Rythme hebdo + points clés ──
    wd = Counter(d.weekday() for d, _h in entries if (start is None or d >= start))
    wmax = max(wd.values()) if wd else 1
    names = _DAYS[_lang()]
    heat = "".join(f'<div class="sx-hc"><div class="sx-hb" style="--i:{wd.get(i, 0) / wmax:.2f}">{wd.get(i, 0) or ""}</div><div class="sx-hd">{names[i]}</div></div>' for i in range(7))
    active = {d for d, _h in entries}
    streak, dcur = 0, today if today in active else today - timedelta(days=1)
    while dcur in active:
        streak += 1
        dcur -= timedelta(days=1)
    best = _DAYS_LONG[_lang()][max(wd.items(), key=lambda kv: kv[1])[0]].capitalize() if wd else "—"
    thr = (tw / (tt / 60)) if tt > 0 else 0
    ins = [("fire", L["streak"], f'{streak} {L["days"]}', "#F97316"), ("cal", L["best"], best, "#3B82F6"), ("gauge", L["thr"], f'{_fmt_n(thr)} {L["wpm"]}', "#10B981")]
    ins_html = "".join(f'<div class="sx-in" style="--c:{c}"><span class="sx-ii">{_svg(i, 20)}</span><div><div class="sx-il">{lab}</div><div class="sx-iv">{val}</div></div></div>' for i, lab, val, c in ins)
    st.markdown(
        f'<div class="sx-row"><div class="sx-card sx-rowc"><div class="sx-ch"><div class="sx-ct">{L["rhythm"]}</div><div class="sx-cs">{L["rhythm_s"]}</div></div><div class="sx-heat">{heat}</div><div class="sx-leg">0<i></i>{max(wd.values()) if wd else 0}</div></div>'
        f'<div class="sx-card"><div class="sx-ch"><div class="sx-ct">{L["insights"]}</div></div><div class="sx-ins">{ins_html}</div></div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

    # ── Records & dernières analyses ──
    times = [h.get("processing_time", 0) or 0 for h in hist]
    if tier >= 2:
        rec = "".join(f'<div class="sx-r"><div class="sx-il">{lab}</div><div class="sx-rv">{_fmt_dur(v)}</div></div>'
                      for lab, v in ((L["fastest"], min(times)), (L["slowest"], max(times)), (L["mean"], sum(times) / len(times))))
        st.markdown(f'<div class="sx-card"><div class="sx-ch"><div class="sx-ct">{L["records"]}</div><div class="sx-cs">{len(hist)} {L["vids"]} {L["total"]}</div></div><div class="sx-rec">{rec}</div></div>', unsafe_allow_html=True)
    else:
        _lock_card(L, "rec", L["lock_rec"], L["lock_rec_d"], 2)

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    recent = sorted(hist, key=_pdate, reverse=True)[: (8 if tier >= 2 else 3)]
    tmax = max([x.get("processing_time", 0) or 0 for x in recent] + [1])
    rows = ""
    for i, h in enumerate(recent):
        vid = h.get("video_id", "")
        title = h.get("title") or f"youtu.be/{vid}"
        pt = h.get("processing_time", 0) or 0
        rows += (f'<div class="sx-li"><span class="sx-lk">{i + 1:02d}</span><div style="min-width:0"><div class="sx-lt"><a href="https://youtu.be/{vid}" target="_blank" rel="noopener">{title}</a></div>'
                 f'<div class="sx-ld">{h.get("date", "")}</div><div class="sx-lb"><i style="width:{pt / tmax * 100:.0f}%"></i></div></div>'
                 f'<div class="sx-lr">{_fmt_dur(pt)}<small>{_fmt_n(h.get("total_words", 0) or 0)} {L["w"].lower()}</small></div></div>')
    st.markdown(f'<div class="sx-card"><div class="sx-ch"><div class="sx-ct">{L["recent"]}</div></div><div class="sx-list">{rows}</div></div>', unsafe_allow_html=True)

    # ── Rapport hebdomadaire ──
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    wk_start = today - timedelta(days=6)
    wk = [h for d, h in entries if d >= wk_start]
    wn, wt, ww = agg(wk)
    if tier >= 3:
        rep = (f"# {T('weekly')} — {user}\n- {T('m_analyse')} : **{wn}**\n- {T('words')} : **{ww:,}**\n- {T('time')} : **{wt:.0f} s**\n## Vidéos\n"
               + "\n".join(f"- {h['date']} — https://youtu.be/{h['video_id']}" for h in wk))
        st.markdown(f'<div class="sx-card"><div class="sx-ch"><div class="sx-ct">{L["wk_title"]}</div><div class="sx-cs">{L["wk_hint"]}</div></div>'
                    f'<div class="sx-rec"><div class="sx-r"><div class="sx-il">{L["n"]}</div><div class="sx-rv">{_fmt_n(wn)}</div></div>'
                    f'<div class="sx-r"><div class="sx-il">{L["w"]}</div><div class="sx-rv">{_fmt_n(ww)}</div></div>'
                    f'<div class="sx-r"><div class="sx-il">{L["t"]}</div><div class="sx-rv">{_fmt_dur(wt)}</div></div></div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:.8rem"></div>', unsafe_allow_html=True)
        st.download_button(T("dl_report"), rep.encode("utf-8"), file_name=f"rapport_{user}.md", mime="text/markdown", use_container_width=True, key="sx_dl")
    else:
        _lock_card(L, "wk", L["lock_wk"], L["lock_wk_d"], 3)