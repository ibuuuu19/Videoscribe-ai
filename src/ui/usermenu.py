"""Menu de l'avatar (popover de la barre latérale) : en-tête profil, icônes, déconnexion en rouge."""
import html as _h
import streamlit as st

_I = {
 "user": "<circle cx='12' cy='8' r='4'/><path d='M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7'/>",
 "gear": "<circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z'/>",
 "bell": "<path d='M6 8a6 6 0 1 1 12 0c0 7 3 8 3 8H3s3-1 3-8'/><path d='M10.3 21a1.9 1.9 0 0 0 3.4 0'/>",
 "moon": "<path d='M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z'/>",
 "sun": "<circle cx='12' cy='12' r='4'/><path d='M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4'/>",
 "phone": "<path d='M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z'/>",
 "tool": "<path d='M14.7 6.3a4 4 0 00-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 005.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z'/>",
 "out": "<path d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/><path d='M16 17l5-5-5-5M21 12H9'/>",
}


def _uri(name: str) -> str:
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' "
           f"stroke-linecap='round' stroke-linejoin='round'>{_I[name]}</svg>")
    return "url(\"data:image/svg+xml;utf8," + svg.replace("#", "%23").replace('"', "'") + "\")"


_COL = {"um_profil": "#3B82F6", "um_config": "#8B5CF6", "um_notifs": "#F59E0B", "um_theme": "#F59E0B", "um_logout": "#EF4444",
        "mt_profil": "#3B82F6", "mt_config": "#8B5CF6", "mt_notifs": "#F59E0B", "mt_contact": "#10B981", "mt_admin": "#EC4899", "mt_theme": "#F59E0B", "mt_logout": "#EF4444"}


# ── Badges de forfait : icônes premium à la place du texte (Gratuit · Basique · Premium · Premium+) ──
_PLAN = {
 0: ("Gratuit",   "<path d='M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z'/>",                       "linear-gradient(135deg,#94A3B8,#64748B)", "#64748B"),
 1: ("Basique",   "<path d='M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z'/><path d='M9 12l2 2 4-4'/>",                           "linear-gradient(135deg,#38BDF8,#2563EB)", "#2563EB"),
 2: ("Premium",   "<path d='M3 8l4 4 5-7 5 7 4-4-2 11H5L3 8z'/>",                                                                    "linear-gradient(135deg,#F5C542,#D4891C)", "#D4AF37"),
 3: ("Premium+",  "<path d='M6 3h12l4 6-10 12L2 9l4-6z'/><path d='M2 9h20M9 3l3 6 3-6M12 21V9'/>",                                  "linear-gradient(135deg,#A855F7,#EC4899 55%,#F59E0B)", "#A855F7"),
}


def plan_badge(tier: int, size: int = 26) -> str:
    """Pastille ronde en dégradé + icône blanche ; le nom du forfait en infobulle."""
    name, path, grad, glow = _PLAN.get(int(tier), _PLAN[0])
    svg = (f"<svg width='{int(size*.58)}' height='{int(size*.58)}' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2.1' "
           f"stroke-linecap='round' stroke-linejoin='round'>{path}</svg>")
    return (f"<span class='vs-plan vs-plan-{int(tier)}' title='{name}' aria-label='{name}' style='--pg:{grad};--pc:{glow};width:{size}px;height:{size}px'>{svg}</span>")


def plan_name(tier: int) -> str:
    return _PLAN.get(int(tier), _PLAN[0])[0]


_BADGE_CSS = (
    "@keyframes vsPlanShine{0%{transform:translateX(-140%) rotate(25deg)}60%,100%{transform:translateX(160%) rotate(25deg)}}"
    ".vs-plan{position:relative;flex:none;display:inline-flex;align-items:center;justify-content:center;border-radius:50%;background:var(--pg);overflow:hidden;"
    "box-shadow:inset 0 1px 0 rgba(255,255,255,.45),0 4px 12px color-mix(in srgb,var(--pc) 55%,transparent),0 0 0 2px color-mix(in srgb,var(--pc) 28%,transparent);}"
    ".vs-plan::after{content:'';position:absolute;top:-30%;bottom:-30%;width:40%;left:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.65),transparent);"
    "animation:vsPlanShine 3.4s ease-in-out infinite;pointer-events:none;}"
    ".vs-plan-0::after{display:none;}"
    ".vs-plan svg{position:relative;z-index:1;filter:drop-shadow(0 1px 1px rgba(0,0,0,.25));}"
)


def trigger_css(dark: bool) -> str:
    """Carte utilisateur (bas de la barre latérale) : indépendante de data-theme, hover + rotation du chevron."""
    ink, soft = ("#F8FAFC", "#AAB8D0") if dark else ("#0F1A2E", "#5B6B88")
    bg = ("linear-gradient(135deg,#131F36,#0F1828)" if dark else "linear-gradient(135deg,#FFFFFF,#F4F8FF)")
    line = "rgba(255,255,255,.10)" if dark else "rgba(15,26,46,.10)"
    sh = "0 8px 24px rgba(0,0,0,.35)" if dark else "0 6px 20px rgba(15,26,46,.08)"
    C = 'html body .stApp section[data-testid="stSidebar"] .user-card'
    H = 'html body .stApp section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.user-card-trigger):has(+ [data-testid="stElementContainer"] [data-testid="stPopover"]'
    r = [
     f"{C}{{background:{bg} !important;border:1px solid {line} !important;box-shadow:{sh} !important;border-radius:16px !important;padding:.62rem .8rem !important;"
     f"transition:transform .25s cubic-bezier(.16,1,.3,1),border-color .25s ease,box-shadow .25s ease !important;}}",
     f"{C} .uname{{color:{ink} !important;font-weight:750 !important;}}",
     f"{C} .tier-chip{{background:linear-gradient(135deg,#D4AF37,#F0D488) !important;color:#0B1F3A !important;border:0 !important;border-radius:999px !important;padding:2px 9px !important;}}",
     f"{C} .chev{{opacity:1 !important;transition:transform .3s cubic-bezier(.16,1,.3,1);}}",
     f"{C} .chev svg{{stroke:{soft} !important;}}",
     f"{C} .avatar{{position:relative;box-shadow:0 0 0 2px {'#0F1828' if dark else '#fff'},0 0 0 4px rgba(46,109,180,.55);overflow:visible !important;}}",
     f"{C} .avatar img{{border-radius:50%;}}",
     f"{C} .avatar::after{{content:'';position:absolute;right:-3px;bottom:-3px;width:11px;height:11px;border-radius:50%;background:#22C55E;"
     f"border:2px solid {'#0F1828' if dark else '#fff'};}}",
     f"{H}:hover) .user-card{{transform:translateY(-2px);border-color:rgba(46,109,180,.55) !important;box-shadow:0 14px 34px rgba(46,109,180,.22) !important;}}",
     f"{H}:hover) .user-card .chev{{transform:translateY(-2px);}}",
     f"{H} button[aria-expanded='true']) .user-card{{border-color:#2E6DB4 !important;box-shadow:0 0 0 3px rgba(46,109,180,.22) !important;}}",
     f"{H} button[aria-expanded='true']) .user-card .chev{{transform:rotate(180deg);}}",
     f'html body .stApp section[data-testid="stSidebar"][data-collapsed="true"] .user-card{{background:none !important;border:0 !important;box-shadow:none !important;padding:0 !important;transform:none !important;}}',
     f'html body .stApp section[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stElementContainer"]:has(.user-card-trigger) {{background:none !important;border:0 !important;box-shadow:none !important;}}',
     f'html body .stApp section[data-testid="stSidebar"][data-collapsed="true"] .user-card .avatar{{width:44px !important;height:44px !important;}}',
     'html body .stApp section[data-testid="stSidebar"][data-collapsed="true"] [data-testid="stPopover"] button{opacity:0 !important;background:none !important;border:0 !important;box-shadow:none !important;}',
    ]
    return "<style>" + _BADGE_CSS + "".join(r) + "</style>"


def css(dark: bool, items=None) -> str:
    ink, soft = ("#F8FAFC", "#AAB8D0") if dark else ("#0F1A2E", "#5B6B88")
    bg = "#0F1828" if dark else "#FFFFFF"
    line = "rgba(255,255,255,.10)" if dark else "rgba(15,26,46,.10)"
    P = 'html body [data-testid="stPopoverBody"]'
    rules = [
     "@keyframes vsumIn{from{opacity:0;transform:translateY(8px) scale(.98)}to{opacity:1;transform:none}}"
     "@keyframes vsumItem{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}"
     "@keyframes vsumPulse{0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,.55)}50%{box-shadow:0 0 0 5px rgba(34,197,94,0)}}",
     f"{P}{{background:{bg} !important;border:1px solid {line} !important;border-radius:22px !important;padding:.6rem !important;"
     f"min-width:284px !important;box-shadow:0 30px 80px rgba(0,0,0,{.6 if dark else .2}),0 0 0 1px rgba(46,109,180,.08) !important;"
     f"animation:vsumIn .28s cubic-bezier(.16,1,.3,1) both;}}",
     f"{P} [data-testid='stVerticalBlock']{{gap:.18rem !important;}}",
     f"{P} hr{{margin:.4rem .5rem !important;border-color:{line} !important;}}",
     f"{P} .vsum-head{{position:relative;display:flex;align-items:center;gap:.8rem;padding:.85rem .8rem .9rem;margin-bottom:.3rem;border-radius:16px;overflow:hidden;"
     f"background:radial-gradient(220px 90px at 0% 0%,rgba(46,109,180,.30),transparent 70%),linear-gradient(135deg,rgba(46,109,180,.14),rgba(16,185,129,.08));"
     f"border:1px solid {line};}}",
     f"{P} .vsum-av{{position:relative;flex:none;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;"
     f"background:linear-gradient(135deg,#1B3B6F,#2E6DB4);color:#fff;font-weight:800;font-size:1rem;box-shadow:0 0 0 2px {bg},0 0 0 4px rgba(46,109,180,.6);}}",
     f"{P} .vsum-av img{{width:100%;height:100%;object-fit:cover;border-radius:50%;}}",
     f"{P} .vsum-av::after{{content:'';position:absolute;right:-2px;bottom:-2px;width:12px;height:12px;border-radius:50%;background:#22C55E;border:2px solid {bg};animation:vsumPulse 2.4s ease infinite;}}",
     f"{P} .vsum-id{{display:flex;flex-direction:column;min-width:0;}}",
     f"{P} .vsum-id b{{color:{ink} !important;font-size:1rem;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}",
     f"{P} .vsum-id>span:not(.vsum-plan){{margin-top:4px;align-self:flex-start;font-size:.62rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;"
     f"padding:2px 9px;border-radius:999px;background:linear-gradient(135deg,#D4AF37,#F0D488);color:#0B1F3A !important;}}",
     f"{P} .vsum-plan{{display:inline-flex;align-items:center;gap:7px;margin-top:5px;}}",
     f"{P} .vsum-plan em{{font-style:normal;font-size:.74rem;font-weight:750;color:{soft} !important;letter-spacing:.02em;}}",
     f"{P} .stButton>button{{position:relative;width:100% !important;min-height:46px !important;height:46px !important;justify-content:flex-start !important;"
     f"gap:.8rem !important;padding:0 .9rem !important;border-radius:14px !important;background:transparent !important;border:0 !important;"
     f"box-shadow:none !important;color:{ink} !important;font-weight:650 !important;font-size:.93rem !important;transform:none !important;overflow:hidden;"
     f"transition:background .22s ease,color .22s ease,padding .22s cubic-bezier(.16,1,.3,1) !important;}}",
     f"{P} .stButton>button>div{{justify-content:flex-start !important;width:auto !important;}}",
     f"{P} .stButton>button p{{color:inherit !important;margin:0 !important;text-align:left !important;font-size:.93rem !important;}}",
     f"{P} .stButton>button .vs-ic, {P} .stButton>button svg{{display:none !important;}}",
     f"{P} .stButton>button::before{{content:'';flex:none;width:20px;height:20px;background:{soft};-webkit-mask:var(--i) center/contain no-repeat;mask:var(--i) center/contain no-repeat;"
     f"transition:background .22s ease,transform .3s cubic-bezier(.34,1.56,.64,1);}}",
     f"{P} .stButton>button::after{{content:'';position:absolute;left:0;top:22%;bottom:22%;width:3px;border-radius:0 3px 3px 0;background:var(--c,#2E6DB4);"
     f"transform:scaleY(0);transition:transform .25s cubic-bezier(.16,1,.3,1);}}",
     f"{P} .stButton>button:hover{{background:linear-gradient(90deg,color-mix(in srgb,var(--c,#2E6DB4) 16%,transparent),transparent) !important;padding-left:1.15rem !important;}}",
     f"{P} .stButton>button:hover::before{{background:var(--c,#2E6DB4);transform:scale(1.18) rotate(-6deg);}}",
     f"{P} .stButton>button:hover::after{{transform:scaleY(1);}}",
     f"{P} .stButton>button:active{{background:color-mix(in srgb,var(--c,#2E6DB4) 24%,transparent) !important;}}",
    ]
    items = items or (("um_profil", "user"), ("um_config", "gear"), ("um_notifs", "bell"),
                      ("um_theme", "sun" if dark else "moon"), ("um_logout", "out"))
    for i, (key, ic_) in enumerate(items):
        rules.append(f"{P} .st-key-{key}{{animation:vsumItem .38s cubic-bezier(.16,1,.3,1) both;animation-delay:{.05 + i * .045:.3f}s;}}")
        rules.append(f"{P} .st-key-{key} .stButton>button{{--i:{_uri(ic_)};--c:{_COL[key]};}}")
    for lk in [k for k, _ in items if k.endswith("logout")]:
        rules.append(f"{P} .st-key-{lk} .stButton>button{{color:#EF4444 !important;}}"
                     f"{P} .st-key-{lk} .stButton>button::before{{background:#EF4444;}}"
                     f"{P} .st-key-{lk} .stButton>button:hover{{background:linear-gradient(90deg,rgba(239,68,68,.18),transparent) !important;}}")
    return "<style>" + _BADGE_CSS + "".join(rules) + "</style>"


def header(user: str, chip: str, av: str, tier: int | None = None) -> str:
    face = f'<img src="{av}" alt="">' if av else _h.escape(user[:2].upper())
    if tier is not None:
        tag = (f'<span class="vsum-plan">{plan_badge(tier, 22)}<em>{_h.escape(plan_name(tier))}</em></span>')
    else:
        tag = f'<span>{_h.escape(chip)}</span>'
    return (f'<div class="vsum-head"><span class="vsum-av">{face}</span>'
            f'<span class="vsum-id"><b>{_h.escape(user)}</b>{tag}</span></div>')