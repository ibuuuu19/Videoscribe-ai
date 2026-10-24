"""
Pages publiques — Accessibles sans connexion (refonte « Premium »).

Contient :
- render_home()    : page d'accueil marketing
- render_about()   : page À propos
- render_privacy() : politique de confidentialité
- render_contact() : page Contact & support
- render_landing() : landing page courte (variante de l'accueil)

Principes de la refonte :
- Design system autonome, préfixé `vsp-` (aucun conflit avec les classes `vs-*` / `g-*`
  historiques, qui restent utilisées ailleurs dans l'application).
- Thèmes clair / sombre pilotés par `st.session_state.theme` (variables CSS).
- 100 % responsive : grilles auto-adaptatives, typographie fluide, hero en 1 colonne sur mobile.
- Animations CSS uniquement (aucun JavaScript, donc aucun conflit avec React / Streamlit) ;
  elles sont coupées automatiquement avec « Réduire les animations » ou prefers-reduced-motion.
- Mêmes signatures de fonctions, mêmes clés de boutons et même logique métier qu'avant.

Usage:
    from src.pages.public import render_home, render_about
"""

import html as _html
import re
import streamlit as st
import streamlit.components.v1 as _components
from pathlib import Path

from src.ui.i18n import T
from src.ui.components import ic, logo_html, STARS
from src.ui.layout import render_navbar, render_footer, notify_admins
from src.core.config import CONTACT_EMAIL, PAYMENT_WAVE, MAP_EMBED, MAP_LINK, DEMO_VIDEO_URL
from src.user_manager import list_users, get_tier
from src.contact_manager import save_message
from src.email_manager import send_contact_message, send_contact_ack


# ═══════════════════════════════════════════════════════════════
# OUTILS
# ═══════════════════════════════════════════════════════════════

def _h(html: str) -> str:
    """Retire l'indentation et les lignes vides (sinon Markdown traite le HTML comme du code)."""
    return "\n".join(l.strip() for l in html.strip().splitlines() if l.strip())


def _md(html: str) -> None:
    st.markdown(_h(html), unsafe_allow_html=True)


def _spacer(rem: float = 2.5) -> None:
    st.markdown(f"<div style='height:{rem}rem;'></div>", unsafe_allow_html=True)


def _esc(v) -> str:
    return _html.escape(str(v), quote=True)


def _keyed_container(key: str):
    """Conteneur avec classe CSS `st-key-<key>` (Streamlit récent) ; repli sans clé sinon."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


# Palette des pastilles d'icônes (dégradés)
_GRAD = {
    "blue":   ("#3B82F6", "#60A5FA"),
    "green":  ("#10B981", "#34D399"),
    "gold":   ("#D4AF37", "#F0D488"),
    "violet": ("#8B5CF6", "#C4B5FD"),
    "orange": ("#F97316", "#FB923C"),
    "cyan":   ("#06B6D4", "#22D3EE"),
    "pink":   ("#EC4899", "#F472B6"),
    "amber":  ("#F59E0B", "#FBBF24"),
    "red":    ("#EF4444", "#F87171"),
}


def _ico(icon_name: str, tone: str = "blue", size: int = 20, box: str = "") -> str:
    a, b = _GRAD.get(tone, _GRAD["blue"])
    return (f'<span class="vsp-ico {box}" style="background:linear-gradient(135deg,{a},{b});">'
            f'{ic(icon_name, size)}</span>')


# ═══════════════════════════════════════════════════════════════
# DESIGN SYSTEM (CSS)
# ═══════════════════════════════════════════════════════════════

_THEMES = {
    "light": dict(
        ink="#0F1A2E", soft="#4A5A7A", surface="#FFFFFF", surface2="#F3F6FC",
        line="rgba(15,26,46,.10)", shadow="0 12px 40px rgba(15,26,46,.07)",
        shadowh="0 28px 64px rgba(46,109,180,.20)", chip="rgba(46,109,180,.09)",
        accent="#2E6DB4", ok="#0E9F6E", bandbg="linear-gradient(160deg,#F8FAFC,#EEF3FB)",
    ),
    "dark": dict(
        ink="#F8FAFC", soft="rgba(203,213,225,.86)", surface="rgba(255,255,255,.045)",
        surface2="rgba(255,255,255,.075)", line="rgba(255,255,255,.11)",
        shadow="0 20px 60px rgba(0,0,0,.45)", shadowh="0 28px 70px rgba(59,130,246,.26)",
        chip="rgba(255,255,255,.08)", accent="#60A5FA", ok="#34D399",
        bandbg="linear-gradient(160deg,rgba(255,255,255,.04),rgba(255,255,255,.015))",
    ),
}

# `$$` = préfixe de spécificité élevée (bat les règles globales de l'application)
_CSS = """
html { scroll-behavior: smooth; }
html body .stApp {
  --vsp-ink:@ink@; --vsp-soft:@soft@; --vsp-surface:@surface@; --vsp-surface2:@surface2@;
  --vsp-line:@line@; --vsp-shadow:@shadow@; --vsp-shadowh:@shadowh@; --vsp-chip:@chip@;
  --vsp-accent:@accent@; --vsp-ok:@ok@; --vsp-gold:#C89B3C; --vsp-ease:cubic-bezier(.16,1,.3,1);
}
$$ { max-width: 1240px; margin-left: auto; margin-right: auto; }
$$ *, $$ *::before, $$ *::after { box-sizing: border-box; }
$$ { white-space: normal; }
$$ .vsp-hero, $$ .vsp-phero { white-space: normal; }
$$ .vsp-ico { display:inline-flex; align-items:center; justify-content:center; width:44px; height:44px; border-radius:13px; color:#fff !important; flex:none; box-shadow:0 10px 24px rgba(46,109,180,.24); }
$$ .vsp-ico svg { stroke:#fff; }
$$ .vsp-ico.sm { width:36px; height:36px; border-radius:11px; }

/* ───── Titres de section ───── */
$$ .vsp-sh { text-align:center; max-width:780px; margin:0 auto 2.2rem; }
$$ .vsp-k { display:inline-flex; align-items:center; gap:8px; font-size:.72rem; font-weight:800; letter-spacing:.2em; text-transform:uppercase; color:var(--vsp-gold) !important; }
$$ .vsp-k::before { content:""; width:22px; height:2px; background:var(--vsp-gold); border-radius:2px; }
$$ .vsp-h2 { font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(1.55rem,3.2vw,2.35rem); line-height:1.14; letter-spacing:-.03em; color:var(--vsp-ink) !important; margin:.7rem 0 .7rem; }
$$ .vsp-h2 em { font-style:normal; background:linear-gradient(92deg,#3B82F6,#10B981 55%,#D4AF37); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
$$ .vsp-lead { color:var(--vsp-soft) !important; font-size:clamp(.98rem,1.3vw,1.1rem); line-height:1.75; margin:0 auto; max-width:660px; }

/* ───── Hero (toujours sombre) ───── */
$$ .vsp-hero { position:relative; overflow:hidden; isolation:isolate; border-radius:32px;
  padding:clamp(2.2rem,5.5vw,4.6rem) clamp(1.1rem,4.5vw,4rem) clamp(4.2rem,7vw,5.8rem); margin:.4rem 0 0;
  background:
    radial-gradient(900px 520px at 10% -8%, rgba(59,130,246,.45), transparent 62%),
    radial-gradient(800px 480px at 92% 0%, rgba(16,185,129,.30), transparent 62%),
    radial-gradient(700px 420px at 50% 112%, rgba(212,175,55,.22), transparent 66%),
    linear-gradient(160deg,#05080F 0%,#0A1220 48%,#0D1830 100%);
  border:1px solid rgba(255,255,255,.10); box-shadow:0 40px 100px rgba(2,8,18,.45), inset 0 1px 0 rgba(255,255,255,.07); }
$$ .vsp-hero::before { content:""; position:absolute; inset:0; z-index:0; pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);
  background-size:46px 46px; -webkit-mask-image:radial-gradient(ellipse at 50% 40%,#000 25%,transparent 75%); mask-image:radial-gradient(ellipse at 50% 40%,#000 25%,transparent 75%); }
$$ .vsp-hero::after { content:""; position:absolute; top:0; left:12%; right:12%; height:1px; z-index:1; background:linear-gradient(90deg,transparent,rgba(96,165,250,.7),rgba(52,211,153,.7),transparent); }
$$ .vsp-orb { position:absolute; border-radius:50%; filter:blur(70px); opacity:.55; z-index:0; pointer-events:none; animation:vsp-drift 16s ease-in-out infinite alternate; }
$$ .vsp-orb.a { width:340px; height:340px; left:-90px; top:-60px; background:#3B82F6; }
$$ .vsp-orb.b { width:300px; height:300px; right:-70px; top:30%; background:#10B981; animation-delay:-6s; opacity:.4; }
$$ .vsp-orb.c { width:260px; height:260px; left:38%; bottom:-120px; background:#D4AF37; animation-delay:-10s; opacity:.3; }
$$ .vsp-hero-grid { position:relative; z-index:2; display:grid; grid-template-columns:minmax(0,1.08fr) minmax(0,.92fr); gap:clamp(1.5rem,4vw,3.2rem); align-items:center; }
$$ .vsp-hero-txt { text-align:left; }
$$ .vsp-eyebrow { display:inline-flex; align-items:center; gap:9px; padding:7px 16px 7px 12px; border-radius:999px; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.15); color:rgba(241,245,249,.9) !important; font-size:.74rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; margin-bottom:1.3rem; backdrop-filter:blur(10px); max-width:100%; }
$$ .vsp-dot { width:7px; height:7px; border-radius:50%; background:#34D399; animation:vsp-pulse 2.2s ease-out infinite; }
$$ .vsp-h1 { font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.045em; line-height:1.04; font-size:clamp(2.1rem,4.6vw,3.8rem); color:#F8FAFC !important; margin:0 0 1.2rem; }
$$ .vsp-h1 .vsp-grad, $$ .vsp-grad { background:linear-gradient(92deg,#60A5FA 0%,#34D399 48%,#FBBF24 100%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
$$ .vsp-rot { display:grid; width:100%; height:1.15em; overflow:visible; }
$$ .vsp-h1, $$ .vsp-phero .h1 { display:block; padding:0 !important; }
$$ .vsp-h1 > br { display:none; }
$$ .vsp-hero-txt, $$ .vsp-stage, $$ .vsp-h1 { min-width:0; max-width:100%; overflow-wrap:anywhere; }
$$ .vsp-rot > span { grid-area:1/1; opacity:0; background:linear-gradient(92deg,#60A5FA 0%,#34D399 48%,#FBBF24 100%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; animation:vsp-rot 12s infinite both; padding-bottom:.08em; white-space:normal; }
$$ .vsp-rot > span:first-child { opacity:1; }
$$ .vsp-rot > span:nth-child(2) { animation-delay:3s; }
$$ .vsp-rot > span:nth-child(3) { animation-delay:6s; }
$$ .vsp-rot > span:nth-child(4) { animation-delay:9s; }
$$ .vsp-sub { color:rgba(226,232,240,.80) !important; max-width:560px; font-size:clamp(1rem,1.35vw,1.17rem); line-height:1.75; margin:0 0 1.7rem; }
$$ .vsp-trust { display:flex; flex-wrap:wrap; gap:.55rem 1.4rem; padding-top:1.4rem; border-top:1px solid rgba(255,255,255,.09); }
$$ .vsp-trust span { display:inline-flex; align-items:center; gap:8px; color:rgba(148,163,184,.98) !important; font-size:.84rem; font-weight:600; }
$$ .vsp-trust span b { color:#F8FAFC !important; font-weight:800; }
$$ .vsp-trust svg { color:#34D399; stroke:#34D399; }

/* Fenêtre « produit » animée */
$$ .vsp-stage { position:relative; min-width:0; }
$$ .vsp-win { position:relative; background:rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.12); border-radius:22px; padding:1rem 1rem .5rem; backdrop-filter:blur(22px); box-shadow:0 34px 80px rgba(0,0,0,.55); animation:vsp-float 7s ease-in-out infinite; text-align:left; }
$$ .vsp-win-head { display:flex; align-items:center; gap:10px; padding:.2rem .3rem .8rem; border-bottom:1px solid rgba(255,255,255,.09); margin-bottom:.8rem; }
$$ .vsp-dots { display:flex; gap:5px; } $$ .vsp-dots i { width:10px; height:10px; border-radius:50%; display:block; }
$$ .vsp-dots i:nth-child(1){background:#EF4444;} $$ .vsp-dots i:nth-child(2){background:#F59E0B;} $$ .vsp-dots i:nth-child(3){background:#22C55E;}
$$ .vsp-url { flex:1; text-align:center; color:rgba(148,163,184,.95) !important; font-size:.74rem; font-family:ui-monospace,Menlo,Consolas,monospace; background:rgba(255,255,255,.05); border-radius:8px; padding:3px 8px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
$$ .vsp-row { display:flex; align-items:center; gap:11px; padding:.72rem .8rem; background:rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.08); border-radius:13px; margin-bottom:.55rem; animation:vsp-in .7s var(--vsp-ease) both; }
$$ .vsp-row:nth-of-type(2){animation-delay:.25s;} $$ .vsp-row:nth-of-type(3){animation-delay:.5s;} $$ .vsp-row:nth-of-type(4){animation-delay:.75s;}
$$ .vsp-row .t { flex:1; min-width:0; }
$$ .vsp-row .t b { display:block; color:#F8FAFC !important; font-size:.85rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
$$ .vsp-row .t small { color:rgba(148,163,184,.95) !important; font-size:.72rem; }
$$ .vsp-row .ok { color:#34D399 !important; font-weight:800; font-size:.76rem; white-space:nowrap; }
$$ .vsp-bar { height:5px; border-radius:6px; background:rgba(255,255,255,.10); overflow:hidden; margin-top:6px; }
$$ .vsp-bar i { display:block; height:100%; width:100%; border-radius:6px; background:linear-gradient(90deg,#3B82F6,#34D399); animation:vsp-fill 6s ease-in-out infinite; }
$$ .vsp-fchip { position:absolute; display:inline-flex; align-items:center; gap:7px; padding:8px 14px; border-radius:999px; background:rgba(15,23,42,.82); border:1px solid rgba(255,255,255,.16); color:#F8FAFC !important; font-size:.78rem; font-weight:700; box-shadow:0 14px 34px rgba(0,0,0,.45); backdrop-filter:blur(12px); animation:vsp-float 6s ease-in-out infinite; z-index:3; white-space:nowrap; }
$$ .vsp-fchip.a { left:-18px; top:-16px; animation-delay:-2s; } $$ .vsp-fchip.b { right:-14px; bottom:-14px; animation-delay:-4s; }
$$ .vsp-fchip svg { color:#34D399; stroke:#34D399; }

/* ───── Zone CTA sous le hero ───── */
.stApp [class*="st-key-vsp_cta"] { position:relative; z-index:6; margin-top:-2.4rem !important; }
.stApp [class*="st-key-vsp_cta"] [data-testid="stHorizontalBlock"] { background:rgba(15,23,42,.72); border:1px solid rgba(255,255,255,.14); border-radius:20px; padding:.6rem; backdrop-filter:blur(18px); box-shadow:0 24px 60px rgba(2,8,18,.45); }

/* ───── Marquee ───── */
$$ .vsp-marq { overflow:hidden; margin:2.2rem 0 0; -webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent); mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent); }
$$ .vsp-marq-lab { text-align:center; font-size:.72rem; font-weight:800; letter-spacing:.18em; text-transform:uppercase; color:var(--vsp-soft) !important; opacity:.8; margin-bottom:.9rem; }
$$ .vsp-track { display:flex; gap:.7rem; width:max-content; animation:vsp-marq 34s linear infinite; }
$$ .vsp-marq:hover .vsp-track { animation-play-state:paused; }
$$ .vsp-pill { display:inline-flex; align-items:center; gap:8px; padding:9px 18px; border-radius:999px; background:var(--vsp-surface); border:1px solid var(--vsp-line); color:var(--vsp-ink) !important; font-weight:700; font-size:.88rem; white-space:nowrap; }
$$ .vsp-pill svg { color:var(--vsp-accent); stroke:var(--vsp-accent); }

/* ───── Statistiques ───── */
$$ .vsp-stats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; margin:2.4rem 0 0; }
$$ .vsp-stat { text-align:center; padding:1.4rem 1rem; border-radius:20px; background:var(--vsp-surface); border:1px solid var(--vsp-line); box-shadow:var(--vsp-shadow); transition:transform .4s var(--vsp-ease), box-shadow .4s ease; }
$$ .vsp-stat:hover { transform:translateY(-4px); box-shadow:var(--vsp-shadowh); }
$$ .vsp-stat b { display:block; font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(1.6rem,3vw,2.2rem); letter-spacing:-.03em; color:var(--vsp-ink) !important; }
$$ .vsp-stat span { display:block; margin-top:.25rem; font-size:.74rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:var(--vsp-soft) !important; }

/* ───── Étapes ───── */
$$ .vsp-steps { position:relative; display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1.1rem; }
$$ .vsp-steps::before { content:""; position:absolute; left:8%; right:8%; top:28px; height:2px; background:linear-gradient(90deg,#3B82F6,#10B981,#D4AF37); opacity:.45; border-radius:2px; }
$$ .vsp-step { position:relative; text-align:center; padding:0 .4rem; }
$$ .vsp-num { position:relative; z-index:1; width:56px; height:56px; margin:0 auto 1rem; border-radius:18px; display:flex; align-items:center; justify-content:center; font-family:'Sora',sans-serif; font-weight:800; font-size:1.05rem; color:#60A5FA !important; background:linear-gradient(135deg,#0F172A,#1E293B); border:1px solid rgba(96,165,250,.40); box-shadow:0 14px 30px rgba(59,130,246,.22); }
$$ .vsp-step h4 { font-family:'Sora',sans-serif; font-weight:800; font-size:1.02rem; color:var(--vsp-ink) !important; margin:0 0 .35rem; }
$$ .vsp-step p { color:var(--vsp-soft) !important; font-size:.9rem; line-height:1.6; margin:0; }

/* ───── Bento fonctionnalités ───── */
$$ .vsp-bento { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }
$$ .vsp-card { position:relative; overflow:hidden; border-radius:22px; padding:1.35rem 1.3rem; background:var(--vsp-surface); border:1px solid var(--vsp-line); box-shadow:var(--vsp-shadow); transition:transform .45s var(--vsp-ease), box-shadow .4s ease, border-color .3s ease; text-align:left; }
$$ .vsp-card::after { content:""; position:absolute; inset:0; pointer-events:none; opacity:0; transition:opacity .4s ease; background:radial-gradient(420px 200px at 100% 0%, rgba(59,130,246,.14), transparent 60%); }
$$ .vsp-card:hover { transform:translateY(-6px); box-shadow:var(--vsp-shadowh); border-color:rgba(59,130,246,.38); }
$$ .vsp-card:hover::after { opacity:1; }
$$ .vsp-card.w2 { grid-column:span 2; }
$$ .vsp-card h4 { font-family:'Sora',sans-serif; font-weight:800; font-size:1.05rem; letter-spacing:-.02em; color:var(--vsp-ink) !important; margin:.9rem 0 .35rem; }
$$ .vsp-card p { color:var(--vsp-soft) !important; font-size:.9rem; line-height:1.62; margin:0; }
$$ .vsp-tag { position:absolute; top:14px; right:14px; font-size:.6rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; padding:3px 9px; border-radius:999px; background:rgba(16,185,129,.14); color:#0E9F6E !important; border:1px solid rgba(16,185,129,.35); z-index:2; }
$$ .vsp-mini { margin-top:1rem; display:grid; gap:.45rem; }
$$ .vsp-sk { height:9px; border-radius:6px; background:linear-gradient(90deg,var(--vsp-line),var(--vsp-chip),var(--vsp-line)); background-size:200% 100%; animation:vsp-shimmer 3.2s linear infinite; }
$$ .vsp-sk.hl { background:linear-gradient(90deg,#3B82F6,#34D399); opacity:.85; animation:none; width:62%; }
$$ .vsp-bub { max-width:88%; padding:.5rem .8rem; border-radius:14px; font-size:.8rem; line-height:1.45; }
$$ .vsp-bub.q { background:var(--vsp-chip); color:var(--vsp-ink) !important; justify-self:end; border-bottom-right-radius:4px; }
$$ .vsp-bub.a { background:linear-gradient(135deg,#1B3B6F,#2E6DB4); color:#fff !important; border-bottom-left-radius:4px; }
$$ .vsp-opt { display:flex; align-items:center; gap:8px; padding:.45rem .7rem; border-radius:10px; border:1px solid var(--vsp-line); font-size:.8rem; font-weight:600; color:var(--vsp-ink) !important; }
$$ .vsp-opt.ok { border-color:rgba(16,185,129,.55); background:rgba(16,185,129,.10); }
$$ .vsp-chips { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:1rem; }
$$ .vsp-chip { display:inline-flex; align-items:center; gap:6px; padding:5px 12px; border-radius:999px; background:var(--vsp-chip); border:1px solid var(--vsp-line); color:var(--vsp-ink) !important; font-size:.8rem; font-weight:700; }

/* ───── Démo interactive ───── */
$$ .vsp-demo { border-radius:26px; padding:1.2rem; background:var(--vsp-surface); border:1px solid var(--vsp-line); box-shadow:var(--vsp-shadow); }
$$ .vsp-demo-body { display:grid; gap:.6rem; min-height:230px; align-content:start; }
$$ .vsp-note { display:flex; gap:12px; padding:.8rem 1rem; border-radius:14px; background:var(--vsp-surface2); border:1px solid var(--vsp-line); animation:vsp-in .5s var(--vsp-ease) both; }
$$ .vsp-note i { flex:none; width:30px; height:30px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-style:normal; font-weight:800; font-size:.8rem; color:#fff !important; background:linear-gradient(135deg,#1B3B6F,#2E6DB4); font-family:'Sora',sans-serif; }
$$ .vsp-note span { color:var(--vsp-ink) !important; font-size:.92rem; line-height:1.55; }
$$ .vsp-xgrid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.6rem; }
$$ .vsp-xi { display:flex; align-items:center; gap:10px; padding:.85rem 1rem; border-radius:14px; background:var(--vsp-surface2); border:1px solid var(--vsp-line); color:var(--vsp-ink) !important; font-weight:700; font-size:.88rem; animation:vsp-in .5s var(--vsp-ease) both; }
.stApp [class*="st-key-vsp_demo_tabs"] { margin-bottom:.4rem; }
.stApp [class*="st-key-vsp_demo_tabs"] [role="radiogroup"] { gap:.45rem; flex-wrap:wrap; justify-content:center; }
.stApp [class*="st-key-vsp_demo_tabs"] [data-testid="stRadioOption"], .stApp [class*="st-key-vsp_demo_tabs"] label[data-baseweb="radio"] { padding:.45rem 1.1rem; border-radius:999px; border:1px solid var(--vsp-line); background:var(--vsp-surface); cursor:pointer; margin:0; transition:all .2s ease; }
.stApp [class*="st-key-vsp_demo_tabs"] [data-testid="stRadioOption"] > div > div:first-child, .stApp [class*="st-key-vsp_demo_tabs"] label[data-baseweb="radio"] > div:first-child { display:none !important; }
.stApp [class*="st-key-vsp_demo_tabs"] [data-testid="stRadioOption"][data-selected="true"] { background:linear-gradient(135deg,#1B3B6F,#2E6DB4); border-color:#3B82F6; }
.stApp [class*="st-key-vsp_demo_tabs"] label[data-baseweb="radio"]:has(input:checked) { background:linear-gradient(135deg,#1B3B6F,#2E6DB4); border-color:#3B82F6; }
.stApp [class*="st-key-vsp_demo_tabs"] [data-testid="stRadioOption"] p, .stApp [class*="st-key-vsp_demo_tabs"] label[data-baseweb="radio"] p { font-weight:700; font-size:.9rem; margin:0; color:var(--vsp-ink) !important; }
.stApp [class*="st-key-vsp_demo_tabs"] [data-testid="stRadioOption"][data-selected="true"] p, .stApp [class*="st-key-vsp_demo_tabs"] label[data-baseweb="radio"]:has(input:checked) p { color:#fff !important; }

/* ───── Cas d'usage & offres ───── */
$$ .vsp-grid3 { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }
$$ .vsp-list { list-style:none; padding:0; margin:.9rem 0 0; display:grid; gap:.5rem; }
$$ .vsp-list li { display:flex; align-items:flex-start; gap:9px; color:var(--vsp-soft) !important; font-size:.9rem; line-height:1.5; }
$$ .vsp-list li svg { margin-top:3px; color:var(--vsp-ok); stroke:var(--vsp-ok); }
$$ .vsp-plans { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; align-items:stretch; }
$$ .vsp-plan { position:relative; display:flex; flex-direction:column; border-radius:24px; padding:1.6rem 1.3rem 1.4rem; background:var(--vsp-surface); border:1px solid var(--vsp-line); box-shadow:var(--vsp-shadow); transition:transform .45s var(--vsp-ease), box-shadow .4s ease; text-align:left; }
$$ .vsp-plan:hover { transform:translateY(-6px); box-shadow:var(--vsp-shadowh); }
$$ .vsp-plan.hl { border:1.5px solid rgba(212,175,55,.65); background:linear-gradient(180deg,rgba(212,175,55,.10),var(--vsp-surface) 55%); box-shadow:0 26px 64px rgba(212,175,55,.18); }
$$ .vsp-ribbon { position:absolute; top:-13px; left:50%; transform:translateX(-50%); white-space:nowrap; background:linear-gradient(135deg,#D4AF37,#F0D488); color:#0B1F3A !important; font-family:'Sora',sans-serif; font-weight:800; font-size:.68rem; letter-spacing:.08em; padding:5px 14px; border-radius:999px; box-shadow:0 10px 22px rgba(212,175,55,.4); }
$$ .vsp-plan h4 { font-family:'Sora',sans-serif; font-weight:800; font-size:1.2rem; color:var(--vsp-ink) !important; margin:0 0 .2rem; }
$$ .vsp-plan .tg { color:var(--vsp-soft) !important; font-size:.84rem; min-height:2.4em; margin:0 0 .8rem; }
$$ .vsp-plan .pl { font-weight:800; font-size:.8rem; color:var(--vsp-ink) !important; padding-top:.8rem; border-top:1px solid var(--vsp-line); margin-top:auto; }
$$ .vsp-plan .vsp-list { margin:.7rem 0 .8rem; }

/* ───── Témoignages ───── */
$$ .vsp-quote { color:var(--vsp-ink) !important; font-size:.95rem; line-height:1.7; margin:.8rem 0 1rem; font-style:italic; }
$$ .vsp-who { display:flex; align-items:center; gap:11px; padding-top:.9rem; border-top:1px solid var(--vsp-line); }
$$ .vsp-av { width:38px; height:38px; border-radius:50%; flex:none; display:flex; align-items:center; justify-content:center; color:#fff !important; font-weight:800; font-size:.82rem; font-family:'Sora',sans-serif; }
$$ .vsp-who b { display:block; color:var(--vsp-ink) !important; font-size:.88rem; }
$$ .vsp-who small { color:var(--vsp-soft) !important; font-size:.76rem; }

/* ───── FAQ ───── */
$$ .vsp-faq { max-width:860px; margin:0 auto; }
$$ details.vsp-q { border:1px solid var(--vsp-line); border-radius:16px; margin-bottom:.65rem; background:var(--vsp-surface); overflow:hidden; transition:border-color .3s ease, box-shadow .3s ease; }
$$ details.vsp-q:hover { border-color:rgba(59,130,246,.40); }
$$ details.vsp-q[open] { box-shadow:var(--vsp-shadow); border-color:rgba(59,130,246,.45); }
$$ details.vsp-q summary { display:flex; align-items:center; gap:12px; padding:1rem 1.2rem; cursor:pointer; list-style:none; font-weight:700; font-size:.96rem; color:var(--vsp-ink) !important; }
$$ details.vsp-q summary::-webkit-details-marker { display:none; }
$$ details.vsp-q summary::after { content:"+"; margin-left:auto; font-size:1.4rem; font-weight:400; color:var(--vsp-accent) !important; transition:transform .3s ease; }
$$ details.vsp-q[open] summary::after { transform:rotate(45deg); }
$$ details.vsp-q summary svg { color:var(--vsp-accent); stroke:var(--vsp-accent); }
$$ .vsp-a { padding:0 1.3rem 1.15rem 3.2rem; color:var(--vsp-soft) !important; font-size:.92rem; line-height:1.72; animation:vsp-in .4s var(--vsp-ease) both; }

/* ───── CTA final ───── */
$$ .vsp-cta { position:relative; overflow:hidden; isolation:isolate; border-radius:30px; padding:clamp(2.2rem,5vw,3.6rem) clamp(1.2rem,4vw,2.6rem); text-align:center;
  background:radial-gradient(700px 300px at 15% 0%,rgba(59,130,246,.40),transparent 60%),radial-gradient(600px 300px at 85% 100%,rgba(16,185,129,.32),transparent 60%),linear-gradient(135deg,#05080F,#0D1830);
  border:1px solid rgba(255,255,255,.12); box-shadow:0 30px 80px rgba(2,8,18,.5); }
$$ .vsp-cta h3 { font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(1.6rem,3.4vw,2.6rem); letter-spacing:-.03em; color:#F8FAFC !important; margin:0 0 .7rem; }
$$ .vsp-cta p { color:rgba(203,213,225,.88) !important; max-width:620px; margin:0 auto 1.4rem; font-size:1.02rem; line-height:1.7; }
$$ .vsp-badges { display:flex; flex-wrap:wrap; gap:.55rem; justify-content:center; }
$$ .vsp-badges span { display:inline-flex; align-items:center; gap:7px; padding:7px 15px; border-radius:999px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16); color:rgba(241,245,249,.95) !important; font-size:.82rem; font-weight:700; }
$$ .vsp-badges svg { color:#34D399; stroke:#34D399; }

/* ───── Pages secondaires ───── */
$$ .vsp-phero { position:relative; overflow:hidden; isolation:isolate; text-align:center; border-radius:32px; padding:clamp(2.4rem,6vw,4.4rem) clamp(1.2rem,5vw,4rem); margin:.4rem 0 2rem;
  background:radial-gradient(800px 420px at 50% -15%,rgba(59,130,246,.42),transparent 65%),radial-gradient(520px 300px at 15% 110%,rgba(16,185,129,.24),transparent 65%),radial-gradient(520px 300px at 88% 110%,rgba(212,175,55,.18),transparent 65%),linear-gradient(160deg,#05080F 0%,#0D1524 100%);
  border:1px solid rgba(255,255,255,.10); box-shadow:0 36px 90px rgba(2,8,18,.42); }
$$ .vsp-phero::before { content:""; position:absolute; inset:0; z-index:0; pointer-events:none; background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px); background-size:46px 46px; -webkit-mask-image:radial-gradient(ellipse at center,#000 20%,transparent 72%); mask-image:radial-gradient(ellipse at center,#000 20%,transparent 72%); }
$$ .vsp-phero > * { position:relative; z-index:1; }
$$ .vsp-phero .h1 { font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.045em; line-height:1.06; font-size:clamp(2rem,4.8vw,3.6rem); color:#F8FAFC !important; margin:0 0 1.1rem; }
$$ .vsp-phero p.l { color:rgba(203,213,225,.88) !important; max-width:700px; margin:0 auto; font-size:clamp(1rem,1.3vw,1.15rem); line-height:1.75; }
$$ .vsp-hstats { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; max-width:820px; margin:2rem auto 0; }
$$ .vsp-hstats div { padding:1rem .6rem; border-radius:16px; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); }
$$ .vsp-hstats b { display:block; font-family:'Sora',sans-serif; font-weight:800; font-size:1.55rem; color:#F8FAFC !important; letter-spacing:-.03em; }
$$ .vsp-hstats span { display:block; margin-top:.2rem; font-size:.7rem; font-weight:800; letter-spacing:.09em; text-transform:uppercase; color:rgba(148,163,184,.98) !important; }
$$ .vsp-duo { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; }
$$ .vsp-vm { padding:1.8rem 1.6rem; }
$$ .vsp-vm h4 { font-size:1.3rem; }
$$ .vsp-time { position:relative; max-width:820px; margin:0 auto; padding-left:2.2rem; }
$$ .vsp-time::before { content:""; position:absolute; left:10px; top:8px; bottom:8px; width:2px; border-radius:2px; background:linear-gradient(180deg,#3B82F6,#10B981,#D4AF37,#EF4444); opacity:.55; }
$$ .vsp-ti { position:relative; padding:0 0 1.5rem 1.6rem; }
$$ .vsp-ti:last-child { padding-bottom:0; }
$$ .vsp-ti::before { content:""; position:absolute; left:-2.2rem; top:5px; width:22px; height:22px; border-radius:50%; background:var(--vsp-surface); border:2px solid #3B82F6; box-shadow:0 0 0 5px rgba(59,130,246,.14); }
$$ .vsp-ti::after { content:""; position:absolute; left:calc(-2.2rem + 7px); top:12px; width:8px; height:8px; border-radius:50%; background:linear-gradient(135deg,#60A5FA,#34D399); }
$$ .vsp-ti .y { font-family:'Sora',sans-serif; font-weight:800; font-size:.8rem; letter-spacing:.08em; text-transform:uppercase; color:var(--vsp-accent) !important; }
$$ .vsp-ti h4 { font-family:'Sora',sans-serif; font-weight:800; color:var(--vsp-ink) !important; font-size:1.05rem; margin:.25rem 0 .3rem; }
$$ .vsp-ti p { color:var(--vsp-soft) !important; font-size:.9rem; line-height:1.65; margin:0; }
$$ .vsp-team { text-align:center; }
$$ .vsp-team .vsp-avl { width:68px; height:68px; margin:0 auto .9rem; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff !important; font-weight:800; font-size:1.2rem; font-family:'Sora',sans-serif; box-shadow:0 14px 30px rgba(46,109,180,.26); }
$$ .vsp-team .role { color:var(--vsp-accent) !important; font-size:.8rem; font-weight:700; margin:.15rem 0 .5rem; }
$$ .vsp-team h4 { margin:.1rem 0 0; }

/* Contact */
$$ .vsp-ch { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; }
$$ .vsp-ch .lab { font-size:.68rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; color:var(--vsp-soft) !important; margin-top:.9rem; }
$$ .vsp-ch h4 { margin:.2rem 0 .35rem; }
$$ .vsp-ch .val { color:var(--vsp-soft) !important; font-size:.88rem; line-height:1.55; word-break:break-word; }
$$ .vsp-ch a.go { display:inline-flex; align-items:center; gap:6px; margin-top:.8rem; padding:6px 13px; border-radius:999px; background:var(--vsp-chip); border:1px solid var(--vsp-line); color:var(--vsp-accent) !important; font-weight:800; font-size:.8rem; text-decoration:none; transition:all .25s ease; }
$$ .vsp-ch a.go:hover { background:var(--vsp-accent); color:#fff !important; border-color:transparent; }
$$ .vsp-resp { display:inline-flex; align-items:center; gap:8px; padding:5px 12px; border-radius:999px; background:rgba(16,185,129,.12); border:1px solid rgba(16,185,129,.35); color:var(--vsp-ok) !important; font-size:.78rem; font-weight:800; margin-top:.5rem; }
$$ .vsp-resp i { width:7px; height:7px; border-radius:50%; background:var(--vsp-ok); animation:vsp-pulse 2.2s ease-out infinite; }
$$ .vsp-ft { font-family:'Sora',sans-serif; font-weight:800; font-size:1.25rem; color:var(--vsp-ink) !important; display:flex; align-items:center; gap:10px; margin:.2rem 0 .3rem; }
$$ .vsp-fs { color:var(--vsp-soft) !important; font-size:.9rem; margin:0 0 .6rem; }
$$ .vsp-maplink { display:inline-flex; align-items:center; gap:6px; color:var(--vsp-accent) !important; font-weight:700; font-size:.88rem; text-decoration:none; margin-top:.5rem; }
$$ .vsp-maplink:hover { text-decoration:underline; }

/* Confidentialité */
$$ .vsp-priv { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1rem; }
$$ .vsp-priv .vsp-card { display:flex; gap:1rem; align-items:flex-start; }
$$ .vsp-priv .n { font-family:'Sora',sans-serif; font-weight:800; font-size:.72rem; letter-spacing:.14em; color:var(--vsp-gold) !important; }
$$ .vsp-priv h4 { margin:.15rem 0 .3rem; }
$$ .vsp-priv code { background:var(--vsp-chip); color:var(--vsp-ink) !important; padding:1px 7px; border-radius:6px; font-size:.82rem; }
$$ .vsp-rights { display:flex; flex-wrap:wrap; gap:.6rem; justify-content:center; margin-top:1.4rem; }
$$ .vsp-rights span { display:inline-flex; align-items:center; gap:8px; padding:9px 18px; border-radius:999px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.16); color:#F8FAFC !important; font-weight:700; font-size:.88rem; }
$$ .vsp-rights svg { color:#34D399; stroke:#34D399; }

/* ───── Animations ───── */
@keyframes vsp-drift { from { transform:translate3d(0,0,0) scale(1); } to { transform:translate3d(40px,30px,0) scale(1.12); } }
@keyframes vsp-float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-10px); } }
@keyframes vsp-pulse { 0% { box-shadow:0 0 0 0 rgba(52,211,153,.55); } 70% { box-shadow:0 0 0 9px rgba(52,211,153,0); } 100% { box-shadow:0 0 0 0 rgba(52,211,153,0); } }
@keyframes vsp-in { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:none; } }
@keyframes vsp-fill { 0% { width:0; } 55%,100% { width:100%; } }
@keyframes vsp-shimmer { to { background-position:-200% 0; } }
@keyframes vsp-marq { to { transform:translateX(-50%); } }
@keyframes vsp-rot { 0% { opacity:0; transform:translateY(45%); } 4%,22% { opacity:1; transform:none; } 27%,100% { opacity:0; transform:translateY(-45%); } }
@keyframes vsp-rv { from { opacity:0; transform:translateY(34px) scale(.985); } to { opacity:1; transform:none; } }
@supports (animation-timeline: view()) {
  $$ .rv { animation:vsp-rv linear both; animation-timeline:view(); animation-range:entry 0% cover 22%; }
}
@media (prefers-reduced-motion: reduce) {
  $$ *, $$ *::before, $$ *::after { animation:none !important; transition:none !important; }
  $$ .vsp-rot > span:not(:first-child) { opacity:0; }
}

/* ───── Responsive ───── */
@media (max-width: 1100px) {
  $$ .vsp-plans { grid-template-columns:repeat(2,minmax(0,1fr)); }
  $$ .vsp-ch { grid-template-columns:repeat(2,minmax(0,1fr)); }
}
@media (max-width: 980px) {
  $$ .vsp-hero-grid { grid-template-columns:minmax(0,1fr); text-align:center; }
  $$ .vsp-hero-txt { text-align:center; }
  $$ .vsp-eyebrow { white-space:normal; text-align:center; letter-spacing:.08em; }
  $$ .vsp-sub { margin-left:auto; margin-right:auto; }
  $$ .vsp-trust { justify-content:center; }
  $$ .vsp-fchip.a { left:6px; } $$ .vsp-fchip.b { right:6px; }
  $$ .vsp-bento, $$ .vsp-grid3 { grid-template-columns:repeat(2,minmax(0,1fr)); }
  $$ .vsp-steps { grid-template-columns:repeat(2,minmax(0,1fr)); row-gap:1.8rem; }
  $$ .vsp-steps::before { display:none; }
}
@media (max-width: 768px) {
  $$ .vsp-stats, $$ .vsp-hstats { grid-template-columns:repeat(2,minmax(0,1fr)); }
  $$ .vsp-xgrid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  $$ .vsp-duo, $$ .vsp-priv { grid-template-columns:1fr; }
  $$ .vsp-hero, $$ .vsp-phero { border-radius:22px; }
  .stApp [class*="st-key-vsp_cta"] { margin-top:-1.6rem !important; }
}
@media (max-width: 600px) {
  $$ .vsp-bento, $$ .vsp-grid3, $$ .vsp-plans, $$ .vsp-ch, $$ .vsp-steps { grid-template-columns:1fr; }
  $$ .vsp-card.w2 { grid-column:auto; }
  $$ .vsp-xgrid { grid-template-columns:1fr; }
  $$ .vsp-fchip { display:none; }
  $$ .vsp-a { padding-left:1.3rem; }
  $$ .vsp-time { padding-left:1.8rem; }
}
"""


def _inject_css() -> None:
    t = _THEMES["light" if st.session_state.get("theme", "light") == "light" else "dark"]
    css = _CSS.replace("$$", "html body .stApp .vsp-w")
    for k, v in t.items():
        css = css.replace(f"@{k}@", v)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _wrap(inner: str, extra: str = "") -> None:
    """Rend un bloc de section dans le conteneur stylé `.vsp-w`."""
    _md(f'<div class="vsp-w {extra}">{inner}</div>')


def _head(kicker: str, title: str, lead: str = "") -> None:
    lead_html = f'<p class="vsp-lead">{lead}</p>' if lead else ""
    _wrap(f'<div class="vsp-sh rv"><div class="vsp-k">{kicker}</div>'
          f'<div class="vsp-h2" role="heading" aria-level="2">{title}</div>{lead_html}</div>')


# ═══════════════════════════════════════════════════════════════
# SECTIONS RÉUTILISABLES
# ═══════════════════════════════════════════════════════════════

def _hero_home(prefix: str, compact: bool = False) -> None:
    """Hero d'accueil + boutons d'action. `prefix` garantit des clés de boutons uniques."""
    sub = ("Collez un lien, obtenez en ~60 secondes un résumé structuré, des mots-clés, des questions, "
           "des flashcards, un quiz et des exports professionnels — en 4 langues.")
    _wrap(f"""
    <section class="vsp-hero">
      <span class="vsp-orb a"></span><span class="vsp-orb b"></span><span class="vsp-orb c"></span>
      <div class="vsp-hero-grid">
        <div class="vsp-hero-txt">
          <div class="vsp-eyebrow"><span class="vsp-dot"></span>{ic("spark", 13)} VideoScribe AI — Nouvelle génération</div>
          <div class="vsp-h1" role="heading" aria-level="1">Transformez chaque vidéo YouTube en
            <span class="vsp-rot"><span>résumés clairs</span><span>fiches de cours</span><span>notes utiles</span><span>quiz malins</span></span>
          </div>
          <p class="vsp-sub">{sub}</p>
          <div class="vsp-trust">
            <span>{ic("check", 14)} <b>Sans carte bancaire</b></span>
            <span>{ic("check", 14)} <b>3 analyses/jour</b> offertes</span>
            <span>{ic("check", 14)} <b>RGPD</b> — données jamais revendues</span>
          </div>
        </div>
        <div class="vsp-stage">
          <span class="vsp-fchip a">{ic("check", 13)} Résumé prêt en 59 s</span>
          <div class="vsp-win">
            <div class="vsp-win-head"><div class="vsp-dots"><i></i><i></i><i></i></div><div class="vsp-url">videoscribe.ai/studio</div></div>
            <div class="vsp-row">{_ico("link", "blue", 15, "sm")}<div class="t"><b>youtube.com/watch?v=dQw4…</b><small>Vidéo détectée — 12 min</small></div><span class="ok">OK</span></div>
            <div class="vsp-row">{_ico("cpu", "green", 15, "sm")}<div class="t"><b>Résumé IA en cours…</b><small>Modèle BART-large — 7 sections</small><div class="vsp-bar"><i></i></div></div><span class="ok">59 s</span></div>
            <div class="vsp-row">{_ico("download", "gold", 15, "sm")}<div class="t"><b>Export prêt</b><small>PDF · Markdown · Anki · Obsidian</small></div><span class="ok">✓</span></div>
          </div>
          <span class="vsp-fchip b">{ic("award", 13)} Quiz généré : 4 questions</span>
        </div>
      </div>
    </section>""")

    with _keyed_container("vsp_cta_" + prefix):
        _c1, _c2, _c3 = st.columns([1, 1.7, 1])
        with _c2:
            _b1, _b2 = st.columns(2)
            with _b1:
                if st.button(f"{T('register')} →", type="primary", use_container_width=True, key=f"{prefix}_register"):
                    st.session_state.page = "register"; st.rerun()
            with _b2:
                if st.button("Voir la démo", use_container_width=True, key=f"{prefix}_demo"):
                    st.session_state.scroll_demo = True; st.rerun()


def _marquee() -> None:
    items = [("file", "PDF"), ("hash", "Markdown"), ("book", "Notion"), ("file", "Obsidian"),
             ("award", "Anki"), ("download", "Présentation HTML"), ("globe", "FR · EN · ES · DE"),
             ("msg", "Chat vidéo IA"), ("chart", "Viral Score")]
    one = "".join(f'<span class="vsp-pill">{ic(i, 15)} {n}</span>' for i, n in items)
    _wrap(f'<div class="vsp-marq rv"><div class="vsp-marq-lab">Exportez et travaillez où vous voulez</div>'
          f'<div class="vsp-track">{one}{one}</div></div>')


def _stats() -> None:
    data = [("+1 000", "vidéos résumées"), ("~60 s", "par analyse"), ("4,9/5", "satisfaction"), ("0", "donnée revendue")]
    cells = "".join(f'<div class="vsp-stat rv"><b>{b}</b><span>{s}</span></div>' for b, s in data)
    _wrap(f'<div class="vsp-stats">{cells}</div>')


def _steps() -> None:
    _head("Comment ça marche", "4 étapes. <em>Zéro friction.</em>",
          "De l'URL à des notes prêtes à réviser, sans rien installer.")
    data = [("01", "Collez l'URL YouTube", "N'importe quelle vidéo publique, dans n'importe quelle langue. Détection automatique."),
            ("02", "L'IA analyse et résume", "Extraction des sous-titres, découpage intelligent, résumé section par section en ~60 s."),
            ("03", "Enrichissez vos notes", "Mots-clés, questions, flashcards Anki, quiz interactif, points d'action."),
            ("04", "Exportez partout", "PDF, Markdown, Obsidian, Notion, Anki, présentation HTML — en un clic.")]
    cells = "".join(f'<div class="vsp-step rv"><div class="vsp-num">{n}</div><h4>{t}</h4><p>{d}</p></div>' for n, t, d in data)
    _wrap(f'<div class="vsp-steps">{cells}</div>')


def _features() -> None:
    _head("Fonctionnalités", "Tout ce qu'il faut pour <em>apprendre plus vite</em>",
          "Une suite complète, pensée pour les étudiants, les créateurs et les professionnels.")
    sk = '<div class="vsp-mini"><div class="vsp-sk"></div><div class="vsp-sk hl"></div><div class="vsp-sk"></div><div class="vsp-sk" style="width:78%"></div></div>'
    chat = ('<div class="vsp-mini"><div class="vsp-bub q">Quels sont les points clés ?</div>'
            '<div class="vsp-bub a">3 idées : le contexte, la méthode et le résultat (02:14).</div></div>')
    quiz = ('<div class="vsp-mini"><div class="vsp-opt">A. Première réponse</div>'
            f'<div class="vsp-opt ok">{ic("check", 13)} B. Bonne réponse</div><div class="vsp-opt">C. Troisième réponse</div></div>')
    exports = ('<div class="vsp-chips">' + "".join(f'<span class="vsp-chip">{ic(i, 13)} {n}</span>' for i, n in
               [("file", "PDF"), ("hash", "Markdown"), ("file", "Obsidian"), ("book", "Notion"), ("award", "Anki"), ("film", "Slides")]) + '</div>')
    langs = '<div class="vsp-chips">' + "".join(f'<span class="vsp-chip">{l}</span>' for l in ["FR", "EN", "ES", "DE"]) + '</div>'

    def card(icon_name, tone, title, desc, extra="", w2=False, tag=None):
        tg = f'<span class="vsp-tag">{tag}</span>' if tag else ""
        return (f'<div class="vsp-card rv{" w2" if w2 else ""}">{tg}{_ico(icon_name, tone)}'
                f'<h4>{title}</h4><p>{desc}</p>{extra}</div>')

    cards = [
        card("cpu", "blue", "IA de pointe", "DistilBART & BART-large : des résumés fidèles au contenu, sans invention.", sk, w2=True),
        card("msg", "green", "Chat vidéo IA", "Posez une question, obtenez une réponse ancrée dans la vidéo.", chat, tag="Plus"),
        card("award", "gold", "Quiz & flashcards", "QCM interactif avec score, export Anki pour la révision espacée.", quiz, tag="Premium"),
        card("download", "violet", "Exports pro", "PDF, Markdown, Obsidian, Notion et présentation HTML : vos notes, partout.", exports, w2=True),
        card("globe", "cyan", "4 langues", "L'interface ET les résumés : français, anglais, espagnol, allemand.", langs),
        card("film", "orange", "Slides automatiques", "Transformez la vidéo en présentation prête à projeter.", tag="Plus"),
        card("chart", "red", "Viral Score", "Analysez le potentiel viral d'une vidéo sur 100.", tag="Premium"),
        card("file", "amber", "Collections", "Favoris, historique de recherche et organisation de vos notes.", tag="Basique"),
        card("user", "pink", "Parrainage", "Invitez vos amis et gagnez +3 jours gratuits par filleul actif.", w2=True),
    ]
    _wrap(f'<div class="vsp-bento">{"".join(cards)}</div>')


_DEMO_TABS = ["Résumé", "Mots-clés", "Quiz", "Exports"]


def _demo_body(tab: str) -> str:
    if tab == "Résumé":
        notes = ["Introduction : le sujet, ses enjeux et ce que la vidéo va démontrer.",
                 "Méthode : les étapes clés expliquées dans l'ordre, sans digression.",
                 "Résultats : ce qu'il faut retenir et comment l'appliquer dès aujourd'hui."]
        return "".join(f'<div class="vsp-note" style="animation-delay:{i * .12}s"><i>{i + 1}</i><span>{n}</span></div>'
                       for i, n in enumerate(notes))
    if tab == "Mots-clés":
        kws = ["#IA", "#productivité", "#résumé", "#apprentissage", "#méthode", "#révision", "#notes"]
        return ('<div class="vsp-chips" style="margin-top:.2rem">'
                + "".join(f'<span class="vsp-chip" style="font-size:.95rem;padding:8px 16px">{k}</span>' for k in kws) + '</div>')
    if tab == "Quiz":
        return ('<div class="vsp-note"><i>?</i><span><b>Quel est le principal enseignement de la vidéo ?</b></span></div>'
                '<div class="vsp-opt">A. Une première réponse plausible</div>'
                f'<div class="vsp-opt ok">{ic("check", 14)} B. La bonne réponse, validée par le résumé</div>'
                '<div class="vsp-opt">C. Une troisième réponse</div>')
    items = [("file", "PDF"), ("hash", "Markdown"), ("file", "Obsidian"), ("book", "Notion"), ("award", "Anki"), ("film", "Présentation")]
    return ('<div class="vsp-xgrid">' + "".join(
        f'<div class="vsp-xi" style="animation-delay:{i * .08}s">{ic(n, 18)} {l}</div>' for i, (n, l) in enumerate(items)) + '</div>')


def _demo_tabs_block() -> None:
    with _keyed_container("vsp_demo_tabs"):
        tab = st.radio("Aperçu", _DEMO_TABS, horizontal=True, label_visibility="collapsed", key="vsp_demo_tab")
    _wrap(f'<div class="vsp-demo"><div class="vsp-win-head" style="border-color:var(--vsp-line)">'
          f'<div class="vsp-dots"><i></i><i></i><i></i></div>'
          f'<div class="vsp-url" style="background:var(--vsp-chip);color:var(--vsp-soft) !important">videoscribe.ai/result</div></div>'
          f'<div class="vsp-demo-body">{_demo_body(tab)}</div></div>')


# Fragment : seul l'aperçu se rafraîchit quand on change d'onglet (l'iframe du teaser ne redémarre pas)
_demo_tabs = st.fragment(_demo_tabs_block) if hasattr(st, "fragment") else _demo_tabs_block


def _demo_section() -> None:
    _md('<div id="vs-demo"></div>')
    _head("Démo interactive", "VideoScribe AI <em>en action</em>",
          "Parcourez les résultats générés, puis lancez le teaser en dessous.")
    _demo_tabs()
    _spacer(1.2)
    _teaser = Path("teaser.html")
    if _teaser.exists():
        _components.html(_teaser.read_text(encoding="utf-8"), height=560)
    elif DEMO_VIDEO_URL:
        st.video(DEMO_VIDEO_URL)
    if st.session_state.pop("scroll_demo", False):
        _components.html('<script>var el=window.parent.document.getElementById("vs-demo"); if(el){el.scrollIntoView({behavior:"smooth"});}</script>', height=0)


def _usecases() -> None:
    _head("Pour qui ?", "Un outil, <em>trois façons</em> de gagner du temps")
    data = [
        ("book", "blue", "Étudiants", ["Révisez en 10 min au lieu d'1 h de vidéo", "Flashcards Anki et quiz interactif", "Notes structurées, prêtes à exporter"]),
        ("spark", "gold", "Créateurs de contenu", ["10 titres et hooks par idée", "Viral Score et analyse des points faibles", "Recyclage LinkedIn / X / Instagram"]),
        ("tool", "green", "Professionnels", ["Veille et points d'action automatiques", "Rapport hebdomadaire d'activité", "Exports Notion et Obsidian"]),
    ]
    cells = ""
    for icn, tone, title, pts in data:
        li = "".join(f"<li>{ic('check', 15)}<span>{p}</span></li>" for p in pts)
        cells += f'<div class="vsp-card rv">{_ico(icn, tone)}<h4>{title}</h4><ul class="vsp-list">{li}</ul></div>'
    _wrap(f'<div class="vsp-grid3">{cells}</div>')


def _plans() -> None:
    _head("Offres", T("prem_title"), T("save_annual"))
    plans = [
        ("free", T("plan_free"), T("tag_free"), None, ["ff1", "ff2", "ff3", "ff4"], False, "green"),
        ("basic", T("plan_basic"), T("tag_basic"), T("plus_free"), ["fb1", "fb2", "fb3", "fb5"], False, "blue"),
        ("premium", T("plan_premium"), T("tag_premium"), T("plus_basic"), ["fp1", "fp3", "fp4", "fp5"], True, "gold"),
        ("plus", T("plan_plus"), T("tag_plus"), T("plus_premium"), ["fx2", "fx4", "fx5", "fx8"], False, "violet"),
    ]
    cells = ""
    for _, name, tag, plus, feats, hl, tone in plans:
        ribbon = f'<span class="vsp-ribbon">★ {T("popular")}</span>' if hl else ""
        pl = f'<div class="pl">{plus}</div>' if plus else ""
        li = "".join(f"<li>{ic('check', 15)}<span>{T(k)}</span></li>" for k in feats)
        cells += (f'<div class="vsp-plan rv{" hl" if hl else ""}">{ribbon}{_ico("award" if hl else "star", tone, 20)}'
                  f'<h4 style="margin-top:.9rem">{name}</h4><p class="tg">{tag}</p><ul class="vsp-list">{li}</ul>{pl}</div>')
    _wrap(f'<div class="vsp-plans">{cells}</div>')
    _spacer(1)
    _c1, _c2, _c3 = st.columns([1, 1.2, 1])
    with _c2:
        if st.button(f"{T('m_premium')} →", use_container_width=True, key="home_plans_cta"):
            st.session_state.page = "premium"; st.rerun()


def _testimonials() -> None:
    _head("Ils nous font confiance", "Ce qu'<em>ils en disent</em>")
    data = [("K", "linear-gradient(135deg,#3B82F6,#60A5FA)", "Khadija D.", "Étudiante en médecine",
             "Je révise mes cours en 10 min au lieu d'1 h de vidéo. Les flashcards Anki sont un game-changer."),
            ("S", "linear-gradient(135deg,#10B981,#34D399)", "Sokhna B.", "Veille stratégique",
             "Le rapport hebdo et les points d'action sont devenus mon outil de veille principal."),
            ("A", "linear-gradient(135deg,#D4AF37,#F0D488)", "Ababacar D.", "Créateur de contenu",
             "Paiement Wave en 2 min, Premium activé dans la foulée. Le support est ultra réactif.")]
    cells = "".join(
        f'<div class="vsp-card rv"><div>{STARS}</div><p class="vsp-quote">« {q} »</p>'
        f'<div class="vsp-who"><div class="vsp-av" style="background:{g};">{i}</div><div><b>{n}</b><small>{r}</small></div></div></div>'
        for i, g, n, r, q in data)
    _wrap(f'<div class="vsp-grid3">{cells}</div>')


def _faq_items(faqs, icon_name="bulb") -> str:
    return "".join(
        f'<details class="vsp-q"><summary>{ic(icon_name, 16)} {q}</summary><div class="vsp-a">{a}</div></details>'
        for q, a in faqs)


def _faq_home() -> None:
    _head("FAQ", "Questions <em>fréquentes</em>")
    faqs = [
        ("Est-ce vraiment gratuit ?", "Oui. Le plan Gratuit offre 3 analyses par jour, à vie, sans carte bancaire. Les plans payants débloquent les analyses illimitées, les exports PDF, le quiz, le chat vidéo, etc."),
        ("Mes données sont-elles en sécurité ?", "Absolument. Mots de passe hashés, emails vérifiés, HTTPS, hébergement sécurisé. Nous ne revendons jamais vos données. Conformité RGPD totale."),
        ("Quelles vidéos sont supportées ?", "Toute vidéo YouTube publique disposant de sous-titres (manuels ou automatiques). Les vidéos privées ou réservées aux membres ne sont pas accessibles."),
        ("Puis-je exporter vers Notion ou Obsidian ?", "Oui, à partir du plan Premium+. Les exports Markdown, Obsidian, Notion et Anki sont disponibles en un clic."),
        ("Comment fonctionne le parrainage ?", "Partagez votre code unique. Chaque filleul qui s'inscrit vous rapporte +3 jours gratuits, cumulables."),
        ("Puis-je annuler à tout moment ?", "Oui. Aucun engagement. Vous gardez l'accès jusqu'à la fin de la période payée."),
    ]
    _wrap(f'<div class="vsp-faq rv">{_faq_items(faqs)}</div>')


def _final_cta(register_key: str, second_label: str, second_key: str, second_page: str,
               title="Prêt à gagner des heures ?",
               text="Rejoignez plus de 1 000 utilisateurs qui transforment déjà leurs vidéos YouTube en notes exploitables.",
               badges=("3 analyses/jour offertes", "Sans carte bancaire", "Export immédiat", "Annulation à tout moment")) -> None:
    b = "".join(f"<span>{ic('check', 14)} {x}</span>" for x in badges)
    _wrap(f'<div class="vsp-cta rv"><h3>{title}</h3><p>{text}</p><div class="vsp-badges">{b}</div></div>')
    _spacer(.6)
    _c1, _c2, _c3 = st.columns([1, 1.4, 1])
    with _c2:
        _b1, _b2 = st.columns(2)
        with _b1:
            if st.button(f"{T('register')} →", type="primary", use_container_width=True, key=register_key):
                st.session_state.page = "register"; st.rerun()
        with _b2:
            if st.button(second_label, use_container_width=True, key=second_key):
                st.session_state.page = second_page; st.rerun()


def _page_hero(icon_name: str, kicker: str, title: str, lead: str, extra: str = "") -> None:
    _wrap(f'<section class="vsp-phero"><div class="vsp-eyebrow">{ic(icon_name, 13)} {kicker}</div>'
          f'<div class="h1" role="heading" aria-level="1">{title}</div><p class="l">{lead}</p>{extra}</section>')


# ═══════════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════════

def render_home():
    if st.session_state.get("user") is None:
        render_navbar()
    _inject_css()
    _hero_home("home")
    _marquee()
    _stats()
    _spacer(3)
    _steps()
    _spacer(3)
    _features()
    _spacer(3)
    _demo_section()
    _spacer(3)
    _usecases()
    _spacer(3)
    _plans()
    _spacer(3)
    _testimonials()
    _spacer(3)
    _faq_home()
    _spacer(3)
    _final_cta("final_cta_register", "Découvrir Premium", "final_cta_premium", "premium")
    _spacer(2)
    render_footer(compact=True)


def render_landing():
    if st.session_state.get("user") is None:
        render_navbar()
    _inject_css()
    _hero_home("landing")
    _stats()
    _spacer(3)
    _steps()
    _spacer(3)
    _features()
    _spacer(3)
    _testimonials()
    _spacer(3)
    _demo_section()
    _spacer(3)
    _final_cta("landing_cta_register", "Découvrir Premium", "landing_cta_premium", "premium",
               title="Prêt à gagner du temps ?",
               text="Essayez gratuitement pendant un mois, sans carte bancaire. Résumés, mots-clés, quiz et exports en ~60 secondes.",
               badges=("3 analyses/jour offertes", "Sans carte bancaire", "Export immédiat"))
    render_footer(compact=False)


def render_about():
    if st.session_state.get("user") is None:
        render_navbar()
    _inject_css()
    stats = [("+1 000", "Vidéos analysées"), ("4", "Langues supportées"), ("~60 s", "Par analyse"), ("2026", "Année de création")]
    sx = '<div class="vsp-hstats">' + "".join(f"<div><b>{b}</b><span>{s}</span></div>" for b, s in stats) + "</div>"
    _page_hero("info", "À propos de VideoScribe AI",
               'Bâtir l\'avenir du <span class="vsp-grad">résumé intelligent</span>',
               "Fondée par des passionnés d'IA, VideoScribe AI accompagne étudiants, professionnels et créateurs "
               "en proposant des résumés de vidéos innovants, sur mesure et performants.", sx)

    _head("Notre raison d'être", "Vision & <em>Mission</em>")
    _wrap(f'''<div class="vsp-duo">
      <div class="vsp-card vsp-vm rv">{_ico("eye", "blue")}<h4>{T("vision")}</h4>
        <p>Devenir le partenaire technologique de référence pour apprendre plus vite, reconnu pour notre expertise et notre impact positif sur la gestion de la connaissance.</p></div>
      <div class="vsp-card vsp-vm rv">{_ico("target", "green")}<h4>{T("mission")}</h4>
        <p>Accompagner les utilisateurs dans leur transformation numérique en concevant des solutions IA innovantes, adaptées à leurs besoins spécifiques.</p></div>
    </div>''')
    _spacer(3)

    _head("Notre parcours", "Une histoire construite <em>pas à pas</em>")
    hist = [("2024 — L'idée", "Un constat simple", "Des heures de vidéos YouTube pour quelques minutes d'information utile. L'idée de VideoScribe AI germe dans l'esprit de ses fondateurs."),
            ("2025 — Le prototype", "Premières versions", "Développement du pipeline d'extraction de sous-titres et des premiers modèles de résumé IA. Tests intensifs avec des étudiants et des créateurs."),
            ("2026 — Le lancement", "VideoScribe AI v1", "Sortie publique avec 4 langues, exports multi-formats, quiz interactif, flashcards Anki et suite viralité pour créateurs de contenu."),
            ("Aujourd'hui", "Une communauté grandissante", "Plus de 1 000 vidéos analysées, des retours utilisateurs constants, et de nouvelles fonctionnalités chaque mois.")]
    items = "".join(f'<div class="vsp-ti rv"><div class="y">{y}</div><h4>{t}</h4><p>{d}</p></div>' for y, t, d in hist)
    _wrap(f'<div class="vsp-time">{items}</div>')
    _spacer(3)

    _head(T("values"), "Les principes qui <em>guident nos actions</em>")
    vals = [("tool", "blue", "Excellence", "Nous visons l'excellence dans tout ce que nous entreprenons, du code à l'expérience utilisateur."),
            ("spark", "gold", "Innovation", "L'innovation est au cœur de notre ADN. Chaque mois, de nouvelles fonctionnalités."),
            ("shield", "green", "Intégrité", "Honnêteté, transparence et éthique dans chaque interaction, chaque ligne de code."),
            ("user", "pink", "Collaboration", "La puissance de la collaboration étroite avec nos utilisateurs et nos partenaires."),
            ("target", "red", "Impact", "Un impact positif et durable sur l'écosystème de la connaissance."),
            ("book", "violet", "Apprentissage", "Une culture d'apprentissage perpétuel, en interne comme pour nos utilisateurs.")]
    cells = "".join(f'<div class="vsp-card rv">{_ico(i, t)}<h4>{n}</h4><p>{d}</p></div>' for i, t, n, d in vals)
    _wrap(f'<div class="vsp-grid3">{cells}</div>')
    _spacer(3)

    _head("L'équipe", "Les visages derrière <em>VideoScribe AI</em>")
    team = [("M", "linear-gradient(135deg,#3B82F6,#60A5FA)", "Mbaye T.", "Fondateur & Lead Dev", "Architecture technique, pipeline IA, vision produit."),
            ("A", "linear-gradient(135deg,#10B981,#34D399)", "Aminata S.", "UX & Design", "Expérience utilisateur, design system, accessibilité."),
            ("S", "linear-gradient(135deg,#D4AF37,#F0D488)", "Souleymane D.", "IA & Recherche", "Fine-tuning des modèles, qualité des résumés, benchmarks.")]
    cells = "".join(
        f'<div class="vsp-card vsp-team rv"><div class="vsp-avl" style="background:{g};">{i}</div><h4>{n}</h4><div class="role">{r}</div><p>{d}</p></div>'
        for i, g, n, r, d in team)
    _wrap(f'<div class="vsp-grid3">{cells}</div>')
    _spacer(3)

    _final_cta("about_cta_register", T("home"), "about_cta_home", "accueil",
               title="Envie de tester par vous-même ?",
               text="Rejoignez VideoScribe AI gratuitement et transformez votre première vidéo en quelques secondes.",
               badges=("Sans carte bancaire", "3 analyses/jour", "Prêt en 30 secondes"))
    render_footer(compact=False)


def render_privacy(show_back=True):
    if st.session_state.get("user") is None:
        render_navbar()
    _inject_css()
    rights = "".join(f"<span>{ic('check', 14)} {x}</span>" for x in ("Consulter", "Exporter", "Supprimer"))
    _page_hero("lock", "RGPD · CNIL", T("priv_title"), T("priv_sub"),
               f'<div class="vsp-rights">{rights}</div>')
    mail = _esc(CONTACT_EMAIL); wave = _esc(PAYMENT_WAVE)
    secs = [
        ("user", "blue", "Responsable", f"<b>Mbtech-services</b> — <code>{mail}</code>"),
        ("file", "violet", "Données", "Nom, email, photo, historique, cookies."),
        ("film", "red", "Vidéos", "Sous-titres publics uniquement, rien ne reste."),
        ("lock", "green", "Sécurité", "Mots de passe hashés, emails vérifiés, HTTPS."),
        ("card", "gold", "Paiements", "CinetPay, aucune donnée bancaire stockée."),
        ("shield", "cyan", "Droits RGPD", "Consulter, exporter, supprimer."),
        ("info", "orange", "Cookies", "<code>ys_token</code> (7 j), <code>ys_theme</code> (1 an)."),
        ("mail", "pink", "Contact", f"{mail} • {wave}"),
    ]
    cells = "".join(
        f'<div class="vsp-card rv">{_ico(i, t)}<div><div class="n">{n + 1:02d}</div><h4>{title}</h4><p>{txt}</p></div></div>'
        for n, (i, t, title, txt) in enumerate(secs))
    _wrap(f'<div class="vsp-priv">{cells}</div>')
    _spacer(1.5)
    if show_back and st.button(T("home"), use_container_width=True, key="privacy_back_home"):
        st.session_state.page = "accueil"; st.session_state.show_privacy = False; st.rerun()
    render_footer(compact=True)


def render_contact():
    # La navbar n'est affichée QUE si l'utilisateur n'est PAS connecté
    if st.session_state.get("user") is None:
        render_navbar()
    _inject_css()

    _contact_user = st.session_state.get("user")
    _contact_is_guest = _contact_user is None
    _contact_sender = _contact_user or "visiteur_anonyme"

    _contact_tier = 0
    try:
        if _contact_user:
            _contact_tier = 3 if st.session_state.get("role") == "admin" else get_tier(_contact_user)
    except Exception:
        _contact_tier = 0

    _delay = "< 2 h" if _contact_tier >= 3 else "< 24 h"
    badges = (f'<div class="vsp-badges" style="margin-top:1.6rem">'
              f'<span>{ic("zap", 13)} Réponse {_delay}</span><span>{ic("shield", 13)} Support RGPD</span>'
              f'<span>{ic("globe", 13)} Support FR / EN</span></div>')
    _page_hero("phone", "Contact & Support", 'Une question, un projet ?<br><span class="vsp-grad">Parlons-en.</span>',
               "Notre équipe vous répond en moins de 24 h (2 h pour les Premium+). Par email, WhatsApp ou via le formulaire ci-dessous.",
               badges)

    # ── Canaux ──
    wa_digits = re.sub(r"\D", "", str(PAYMENT_WAVE))
    mail = _esc(CONTACT_EMAIL); wave = _esc(PAYMENT_WAVE)
    wa_link = f'<a class="go" target="_blank" rel="noopener" href="https://wa.me/{wa_digits}">{ic("msg", 13)} Ouvrir WhatsApp</a>' if wa_digits else ""
    _wrap(f'''<div class="vsp-ch">
      <div class="vsp-card rv">{_ico("mail", "blue")}<div class="lab">Email</div><h4>Support & Commercial</h4>
        <div class="val">{mail}</div><a class="go" href="mailto:{mail}">{ic("send", 13)} Écrire</a></div>
      <div class="vsp-card rv">{_ico("msg", "green")}<div class="lab">WhatsApp</div><h4>Support instantané</h4>
        <div class="val">{wave}</div>{wa_link}</div>
      <div class="vsp-card rv">{_ico("card", "gold")}<div class="lab">Paiement</div><h4>Wave / Orange Money</h4>
        <div class="val">{wave}</div></div>
      <div class="vsp-card rv">{_ico("clock", "violet")}<div class="lab">Horaires</div><h4>Lun — Sam</h4>
        <div class="val">9 h – 20 h (GMT)</div><div class="vsp-resp"><i></i>Réponse {_delay}</div></div>
    </div>''')
    _spacer(2.5)

    # ── Localisation ──
    _head("Nous trouver", "Notre <em>localisation</em>")
    _map_left, _map_right = st.columns([1.6, 1], gap="large")
    with _map_left:
        _components.iframe(MAP_EMBED, height=340)
        _md(f'<div class="vsp-w"><a class="vsp-maplink" target="_blank" rel="noopener" href="{_esc(MAP_LINK)}">{ic("link", 13)} Ouvrir dans Google Maps ↗</a></div>')
    with _map_right:
        _wrap(f'''<div class="vsp-card" style="margin-bottom:.9rem">{_ico("map", "blue")}<div class="lab" style="font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--vsp-soft)!important;margin-top:.9rem">Adresse</div>
          <h4>Mbtech-services</h4><p>Cambérène, Dakar — Sénégal<br>Lun – Sam : 9 h – 20 h (GMT)</p></div>
        <div class="vsp-card">{_ico("phone", "green")}<div class="lab" style="font-size:.68rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--vsp-soft)!important;margin-top:.9rem">Téléphone</div>
          <h4>Appel & WhatsApp</h4><p>{wave}</p></div>''')
    _spacer(2.5)

    # ── FAQ ──
    _head("FAQ express", "Les réponses <em>en un clic</em>")
    faqs = [
        ("J'ai oublié mon mot de passe, que faire ?", "Utilisez le formulaire ci-dessous ou écrivez-nous sur WhatsApp. Nous réinitialisons votre mot de passe sous 24 h (2 h pour Premium+)."),
        ("Mon paiement n'a pas activé mon compte, pourquoi ?", "Envoyez-nous votre pseudo + une capture d'écran Wave/Orange Money. L'activation manuelle est faite sous 24 h maximum."),
        ("Que faire si une vidéo n'a pas de sous-titres ?", "Certaines vidéos (privées, réservées aux membres, ou sans sous-titres publics) ne peuvent pas être analysées. Essayez avec une autre vidéo ou contactez-nous."),
        ("Puis-je obtenir une facture pour mon entreprise ?", "Oui, sur demande. Envoyez-nous un email avec vos informations de facturation (raison sociale, numéro TVA, adresse)."),
        ("Comment annuler mon abonnement ?", "Aucun engagement. Envoyez-nous simplement un message via le formulaire ou WhatsApp, et l'annulation sera effective immédiatement."),
    ]
    _wrap(f'<div class="vsp-faq rv">{_faq_items(faqs)}</div>')
    _spacer(2.5)

    # ── Formulaire ──
    _head("Écrivez-nous", "Envoyer un <em>message</em>")
    _wrap(f'<div class="vsp-ft">{_ico("msg", "blue", 18, "sm")} Support client</div>'
          f'<p class="vsp-fs">Remplissez le formulaire ci-dessous, nous vous répondrons dans les meilleurs délais.</p>')

    _acc_email = ""
    if not _contact_is_guest:
        try:
            _acc_email = (list_users().get(_contact_user, {}) or {}).get("email", "") or ""
        except Exception:
            _acc_email = ""

    with st.form("contact_form"):
        _c1, _c2 = st.columns(2)
        with _c1:
            subject = st.text_input(T("subject"), placeholder="Ex. Problème de paiement, Question sur Premium...")
        with _c2:
            email_c = st.text_input(T("your_email"), value=_acc_email, placeholder="votre@email.com")
        _c3, _c4 = st.columns([1, 1])
        with _c3:
            urgency = st.selectbox(T("priority"), ["normale", "importante", "urgente"])
        with _c4:
            st.markdown("<div style='height:.6rem;'></div>", unsafe_allow_html=True)
            st.caption("Urgence : pour les problèmes bloquants, choisissez « urgente ».")
        message = st.text_area(T("message"), height=170, placeholder="Décrivez votre demande en détail...")
        _sub_col1, _sub_col2, _sub_col3 = st.columns([1, 1.5, 1])
        with _sub_col2:
            _submitted = st.form_submit_button(f"📤 {T('send')}", use_container_width=True, type="primary")
        if _submitted:
            _email_ok = (not email_c.strip()) or re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_c.strip())
            if not (subject.strip() and message.strip()):
                st.error("❌ Le sujet et le message sont obligatoires.")
            elif not _email_ok:
                st.error("❌ L'adresse email semble invalide. Vérifiez-la pour recevoir notre réponse.")
            else:
                try: save_message(_contact_sender, subject.strip(), message.strip(), urgency)
                except Exception: pass
                try: notify_admins("msg", f"Nouveau message de **{_contact_sender}** : « {subject.strip()} » (priorité {urgency})")
                except Exception: pass
                ok_admin, err_a = False, "fonction non disponible"
                ok_client, err_c = False, "fonction non disponible"
                try: ok_admin, err_a = send_contact_message(CONTACT_EMAIL, _contact_sender, email_c.strip(), subject.strip(), message.strip(), urgency)
                except Exception as e: err_a = str(e)
                try: ok_client, err_c = send_contact_ack(email_c.strip(), _contact_sender, subject.strip())
                except Exception as e: err_c = str(e)
                st.balloons()
                if ok_admin and ok_client: st.success("✅ Message envoyé ! Un accusé de réception vous a été envoyé par email.")
                elif ok_admin: st.success("✅ Message envoyé à l'équipe support.")
                else: st.warning(f"⚠️ Message enregistré mais l'envoi email a échoué : {err_a}")

    _spacer(2)
    render_footer(compact=True)