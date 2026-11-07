"""
Page Notifications — design premium (en-tête, compteurs, filtres, fil groupé par jour).
Dans app.py, remplacer render_notifs() par :

    def render_notifs():
        from src.pages.notifs import render_notifs as _rn
        _rn(user)
"""
import html as _h
import re
from datetime import datetime, timedelta

import streamlit as st

from src.ui.i18n import T

_L = {
    "fr": dict(all="Toutes", unread="Non lues", read="Lues", today="Aujourd'hui", yest="Hier", older="Plus ancien", new="Nouveau",
               empty_t="Tout est à jour", empty_s="Vous n'avez aucune notification pour le moment.", empty_u="Aucune notification non lue.",
               total="Total", ago_now="À l'instant", ago_m="il y a {n} min", ago_h="il y a {n} h", live="Temps réel"),
    "en": dict(all="All", unread="Unread", read="Read", today="Today", yest="Yesterday", older="Earlier", new="New",
               empty_t="You're all caught up", empty_s="You have no notifications right now.", empty_u="No unread notifications.",
               total="Total", ago_now="Just now", ago_m="{n} min ago", ago_h="{n} h ago", live="Live"),
    "es": dict(all="Todas", unread="No leídas", read="Leídas", today="Hoy", yest="Ayer", older="Anteriores", new="Nuevo",
               empty_t="Todo al día", empty_s="No tienes notificaciones por ahora.", empty_u="No hay notificaciones sin leer.",
               total="Total", ago_now="Ahora mismo", ago_m="hace {n} min", ago_h="hace {n} h", live="En vivo"),
    "de": dict(all="Alle", unread="Ungelesen", read="Gelesen", today="Heute", yest="Gestern", older="Älter", new="Neu",
               empty_t="Alles erledigt", empty_s="Du hast momentan keine Benachrichtigungen.", empty_u="Keine ungelesenen Benachrichtigungen.",
               total="Gesamt", ago_now="Gerade eben", ago_m="vor {n} Min.", ago_h="vor {n} Std.", live="Live"),
}

_P: dict[str, str] = {
    "bell": "<path d='M6 9a6 6 0 0 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9z'/><path d='M10 20a2 2 0 0 0 4 0'/>",
    "key": "<circle cx='8' cy='15' r='4'/><path d='M11 12l9-9M16 7l3 3'/>",
    "trash": "<path d='M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13'/>",
    "user": "<circle cx='12' cy='8' r='4'/><path d='M4 21c0-4 4-6 8-6s8 2 8 6'/>",
    "mail": "<rect x='3' y='5' width='18' height='14' rx='3'/><path d='M3 8l9 6 9-6'/>",
    "star": "<path d='M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z'/>",
    "card": "<rect x='3' y='5' width='18' height='14' rx='3'/><path d='M3 10h18'/>",
    "check": "<path d='M5 12l5 5 9-10'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    "film": "<rect x='3' y='4' width='18' height='16' rx='3'/><path d='M10 9v6l5-3z'/>",
    "inbox": "<path d='M3 13l3-8h12l3 8v6H3z'/><path d='M3 13h5l1 3h6l1-3h5'/>",
    "warn": "<path d='M12 3l10 18H2z'/><path d='M12 10v5M12 18v.01'/>",
}
_ALIAS: dict[str, str] = {"crown": "star", "money": "card", "wallet": "card", "msg": "mail", "message": "mail", "send": "mail",
          "users": "user", "play": "film", "video": "film", "lock": "key", "alert": "warn", "tool": "key"}


def _svg(name: str, size: int = 20) -> str:
    key = _ALIAS.get(name, name)
    p = _P[key] if key in _P else _P["bell"]
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' "
            f"stroke-linecap='round' stroke-linejoin='round'>{p}</svg>")


def _fmt(text):
    t = _h.escape(str(text))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def _parse(d):
    for f in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(str(d), f)
        except Exception:
            pass
    return None


def _css(acc, acc2, dark):
    ink = "#F8FAFC" if dark else "#0F1A2E"
    soft = "#AAB8D0" if dark else "#5B6B88"
    surf = "rgba(255,255,255,.045)" if dark else "#FFFFFF"
    surf2 = "rgba(255,255,255,.07)" if dark else "#F3F6FB"
    line = "rgba(255,255,255,.10)" if dark else "rgba(15,26,46,.10)"
    shadow = "0 18px 50px rgba(0,0,0,.35)" if dark else "0 18px 50px rgba(15,26,46,.08)"
    css = f"""
html body .stApp .nf-hero {{ position:relative; overflow:hidden; display:flex; align-items:center; gap:1.2rem; padding:1.5rem 1.6rem; border-radius:28px; margin:0 0 1rem; color:#fff;
  background:radial-gradient(120% 160% at 0% 0%,color-mix(in srgb,{acc} 80%,#fff) 0,transparent 55%),linear-gradient(135deg,{acc2},{acc}); box-shadow:0 20px 50px color-mix(in srgb,{acc} 30%,transparent); animation:nfIn .5s ease both; }}
html body .stApp .nf-hero::after {{ content:""; position:absolute; inset:0; background:repeating-linear-gradient(115deg,rgba(255,255,255,.06) 0 1px,transparent 1px 28px); pointer-events:none; }}
html body .stApp .nf-bell {{ position:relative; flex:none; width:64px; height:64px; border-radius:20px; display:flex; align-items:center; justify-content:center; color:#fff; background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.35); backdrop-filter:blur(8px); }}
html body .stApp .nf-bell svg {{ width:30px; height:30px; transform-origin:50% 0; animation:nfRing 3.2s ease-in-out infinite; }}
html body .stApp .nf-bell .n {{ position:absolute; top:-7px; right:-7px; min-width:24px; height:24px; padding:0 6px; border-radius:99px; display:flex; align-items:center; justify-content:center; font:800 .78rem Sora,sans-serif; color:#3B2A00; background:linear-gradient(135deg,#F7D774,#D4AF37); border:2px solid {acc2}; box-sizing:border-box; }}
html body .stApp .nf-hero h1 {{ margin:0; padding:0; font:800 clamp(1.5rem,4vw,2.1rem)/1.15 Sora,sans-serif; letter-spacing:-.03em; color:#fff !important; }}
html body .stApp .nf-hero p {{ margin:.3rem 0 0; font-size:.95rem; font-weight:600; color:rgba(255,255,255,.88) !important; }}
html body .stApp .nf-live {{ margin-left:auto; flex:none; display:inline-flex; align-items:center; gap:7px; padding:6px 13px; border-radius:99px; font-size:.74rem; font-weight:800; background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.3); color:#fff !important; position:relative; z-index:1; }}
html body .stApp .nf-live i {{ width:8px; height:8px; border-radius:50%; background:#4ADE80; box-shadow:0 0 0 0 rgba(74,222,128,.7); animation:nfPulse 2s infinite; }}
html body .stApp .nf-stats {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.8rem; margin-bottom:1rem; }}
html body .stApp .nf-stat {{ display:flex; align-items:center; gap:.8rem; padding:.9rem 1rem; border-radius:20px; background:{surf}; border:1px solid {line}; box-shadow:{shadow}; transition:transform .25s ease; animation:nfIn .5s ease both; }}
html body .stApp .nf-stat:hover {{ transform:translateY(-3px); }}
html body .stApp .nf-stat .i {{ flex:none; width:42px; height:42px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,{acc},{acc2}); }}
html body .stApp .nf-stat small {{ display:block; color:{soft} !important; font-size:.72rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; }}
html body .stApp .nf-stat b {{ display:block; color:{ink} !important; font:800 1.4rem Sora,sans-serif; line-height:1.1; }}
html body .stApp .st-key-nf_bar [data-testid="stHorizontalBlock"] {{ align-items:center; gap:.8rem; }}
html body .stApp .st-key-nf_filter [role="radiogroup"] {{ display:inline-flex !important; flex-wrap:nowrap; gap:3px !important; padding:4px; border-radius:999px; background:{surf2}; border:1px solid {line}; }}
html body .stApp .st-key-nf_filter [data-testid="stRadioOption"] {{ margin:0 !important; padding:.5rem 1.05rem !important; border-radius:999px; cursor:pointer; transition:background .25s ease, box-shadow .25s ease; }}
html body .stApp .st-key-nf_filter [data-testid="stRadioOption"] > div > div:first-child {{ display:none !important; }}
html body .stApp .st-key-nf_filter [data-testid="stRadioOption"] p {{ font-size:.82rem !important; font-weight:700 !important; margin:0 !important; color:{soft} !important; white-space:nowrap; }}
html body .stApp .st-key-nf_filter [data-testid="stRadioOption"]:has(input:checked) {{ background:linear-gradient(135deg,{acc},{acc2}); box-shadow:0 6px 16px color-mix(in srgb,{acc} 35%,transparent); }}
html body .stApp .st-key-nf_filter [data-testid="stRadioOption"]:has(input:checked) p {{ color:#fff !important; font-weight:800 !important; }}
html body .stApp .st-key-nf_markall button {{ min-height:44px; border-radius:999px !important; font-weight:800 !important; color:{acc} !important; background:color-mix(in srgb,{acc} 12%,transparent) !important; border:1.5px solid color-mix(in srgb,{acc} 45%,transparent) !important; box-shadow:none !important; transition:all .2s ease; }}
html body .stApp .st-key-nf_markall button:hover {{ color:#fff !important; background:linear-gradient(135deg,{acc},{acc2}) !important; border-color:transparent !important; transform:translateY(-1px); }}
html body .stApp .st-key-nf_markall button:disabled, html body .stApp .st-key-nf_markall button:disabled:hover {{ opacity:.45 !important; transform:none !important; color:{soft} !important; background:{surf2} !important; border-color:{line} !important; cursor:default; }}
html body .stApp .st-key-nf_markall button p {{ color:inherit !important; }}
html body .stApp .nf-day {{ display:flex; align-items:center; gap:.8rem; margin:1.4rem 0 .7rem; color:{soft} !important; font-size:.76rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }}
html body .stApp .nf-day::after {{ content:""; flex:1; height:1px; background:{line}; }}
html body .stApp .nf-item {{ position:relative; display:flex; align-items:flex-start; gap:1rem; padding:1rem 1.1rem; margin-bottom:.7rem; border-radius:22px; background:{surf}; border:1px solid {line}; box-shadow:{shadow}; transition:transform .25s ease, border-color .25s ease; animation:nfIn .45s ease both; }}
html body .stApp .nf-item:hover {{ transform:translateX(4px); border-color:color-mix(in srgb,{acc} 50%,{line}); }}
html body .stApp .nf-item.un {{ background:linear-gradient(100deg,color-mix(in srgb,{acc} {"14" if dark else "8"}%,transparent),{surf} 55%); border-color:color-mix(in srgb,{acc} 38%,{line}); }}
html body .stApp .nf-item.un::before {{ content:""; position:absolute; left:0; top:16px; bottom:16px; width:4px; border-radius:0 4px 4px 0; background:linear-gradient(180deg,{acc},#D4AF37); }}
html body .stApp .nf-ic {{ flex:none; width:46px; height:46px; border-radius:15px; display:flex; align-items:center; justify-content:center; color:{acc}; background:color-mix(in srgb,{acc} 14%,transparent); border:1px solid color-mix(in srgb,{acc} 28%,transparent); }}
html body .stApp .nf-item.un .nf-ic {{ color:#fff; background:linear-gradient(135deg,{acc},{acc2}); border-color:transparent; box-shadow:0 8px 18px color-mix(in srgb,{acc} 35%,transparent); }}
html body .stApp .nf-body {{ min-width:0; flex:1; }}
html body .stApp .nf-txt {{ color:{ink} !important; font-size:.96rem; font-weight:600; line-height:1.45; word-break:break-word; }}
html body .stApp .nf-txt b {{ font-weight:800; color:{ink} !important; }}
html body .stApp .nf-meta {{ display:flex; align-items:center; flex-wrap:wrap; gap:.4rem .8rem; margin-top:.35rem; color:{soft} !important; font-size:.78rem; font-weight:600; }}
html body .stApp .nf-meta span {{ display:inline-flex; align-items:center; gap:5px; color:{soft} !important; }}
html body .stApp .nf-new {{ flex:none; align-self:center; padding:3px 10px; border-radius:99px; font-size:.64rem; font-weight:800; letter-spacing:.06em; text-transform:uppercase; color:#3B2A00 !important; background:linear-gradient(135deg,#F7D774,#D4AF37); }}
html body .stApp .nf-empty {{ text-align:center; padding:3rem 1.2rem; border-radius:28px; background:{surf}; border:1px dashed {line}; box-shadow:{shadow}; }}
html body .stApp .nf-empty .i {{ width:76px; height:76px; margin:0 auto 1rem; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,{acc},{acc2}); box-shadow:0 16px 36px color-mix(in srgb,{acc} 40%,transparent); }}
html body .stApp .nf-empty h3 {{ margin:0; font:800 1.25rem Sora,sans-serif; color:{ink} !important; }}
html body .stApp .nf-empty p {{ margin:.4rem 0 0; color:{soft} !important; font-size:.92rem; }}
@keyframes nfIn {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:none; }} }}
@keyframes nfRing {{ 0%,55%,100% {{ transform:rotate(0); }} 60% {{ transform:rotate(14deg); }} 70% {{ transform:rotate(-12deg); }} 80% {{ transform:rotate(8deg); }} 90% {{ transform:rotate(-4deg); }} }}
@keyframes nfPulse {{ 70% {{ box-shadow:0 0 0 8px rgba(74,222,128,0); }} 100% {{ box-shadow:0 0 0 0 rgba(74,222,128,0); }} }}
@media (max-width:640px) {{ html body .stApp .nf-hero {{ padding:1.1rem; gap:.9rem; border-radius:22px; }} html body .stApp .nf-bell {{ width:52px; height:52px; border-radius:16px; }} html body .stApp .nf-live {{ display:none; }}
  html body .stApp .nf-stat {{ flex-direction:column; align-items:flex-start; gap:.5rem; padding:.75rem; }} html body .stApp .nf-stat b {{ font-size:1.15rem; }}
  html body .stApp .nf-item {{ padding:.85rem; gap:.75rem; }} html body .stApp .nf-ic {{ width:40px; height:40px; border-radius:13px; }} html body .stApp .nf-new {{ display:none; }} }}
@media (prefers-reduced-motion:reduce) {{ html body .stApp .nf-hero, html body .stApp .nf-stat, html body .stApp .nf-item, html body .stApp .nf-bell svg, html body .stApp .nf-live i {{ animation:none; }} }}
"""
    st.markdown("<style>" + css.replace("\n", " ") + "</style>", unsafe_allow_html=True)


def render_notifs(user):
    from src.ui.css import shade
    from src.ui.fast import get_notifications, unread_count, mark_all_read
    from src.ui.layout import render_footer

    L = _L.get(st.session_state.get("cfg_lang", "fr"), _L["fr"])
    dark = st.session_state.get("theme", "light") == "dark"
    acc = st.session_state.get("cfg_accent", "#2E6DB4")
    acc2 = shade(acc, 0.55)
    _css(acc, acc2, dark)

    notifs = get_notifications(user) or []
    n_un = unread_count(user)
    n_tot = len(notifs)

    badge = f'<span class="n">{n_un if n_un < 100 else "99+"}</span>' if n_un else ""
    st.markdown((f'<div class="nf-hero"><div class="nf-bell">{_svg("bell", 30)}{badge}</div>'
                 f'<div style="position:relative;z-index:1"><h1>{_h.escape(T("notifs_title"))}</h1><p>{_h.escape(T("notifs_sub"))}</p></div>'
                 f'<span class="nf-live"><i></i>{L["live"]}</span></div>'), unsafe_allow_html=True)

    stats = [("inbox", L["total"], n_tot), ("bell", L["unread"], n_un), ("check", L["read"], n_tot - n_un)]
    st.markdown('<div class="nf-stats">' + "".join(
        f'<div class="nf-stat" style="animation-delay:{i*70}ms"><span class="i">{_svg(n, 20)}</span><div><small>{_h.escape(l)}</small><b>{v}</b></div></div>'
        for i, (n, l, v) in enumerate(stats)) + '</div>', unsafe_allow_html=True)

    with st.container(key="nf_bar"):
        c1, c2 = st.columns([3, 2])
        with c1:
            flt = st.radio("filter", ["all", "unread"], horizontal=True, key="nf_filter", label_visibility="collapsed",
                           format_func=lambda k: f'{L["all"]} · {n_tot}' if k == "all" else f'{L["unread"]} · {n_un}')
        with c2:
            with st.container(key="nf_markall"):
                if st.button(T("mark_all"), use_container_width=True, disabled=not n_un, key="nf_mark"):
                    mark_all_read(user)
                    st.rerun()

    shown = [n for n in notifs if flt == "all" or not n.get("read")]
    if not shown:
        st.markdown(f'<div class="nf-empty"><div class="i">{_svg("check", 34)}</div><h3>{L["empty_t"]}</h3>'
                    f'<p>{L["empty_s"] if not notifs else L["empty_u"]}</p></div>', unsafe_allow_html=True)
        render_footer(compact=True)
        return

    now = datetime.now()
    today = now.date()
    groups, order = {}, []
    for n in shown:
        dt = _parse(n.get("date"))
        if dt is None: g = L["older"]
        elif dt.date() == today: g = L["today"]
        elif dt.date() == today - timedelta(days=1): g = L["yest"]
        else: g = L["older"]
        if g not in groups: groups[g] = []; order.append(g)
        groups[g].append((n, dt))

    idx = 0
    for g in order:
        st.markdown(f'<div class="nf-day">{_h.escape(g)}</div>', unsafe_allow_html=True)
        for n, dt in groups[g]:
            un = not n.get("read")
            if dt is None: when = _h.escape(str(n.get("date", "")))
            else:
                diff = now - dt
                if diff < timedelta(minutes=1): when = L["ago_now"]
                elif diff < timedelta(hours=1): when = L["ago_m"].format(n=int(diff.total_seconds() // 60))
                elif diff < timedelta(hours=12) and dt.date() == today: when = L["ago_h"].format(n=int(diff.total_seconds() // 3600))
                else: when = dt.strftime("%d/%m/%Y")
            full = _h.escape(str(n.get("date", "")))
            st.markdown((f'<div class="nf-item {"un" if un else ""}" style="animation-delay:{min(idx, 8)*50}ms">'
                         f'<span class="nf-ic">{_svg(str(n.get("icon", "bell")), 22)}</span>'
                         f'<div class="nf-body"><div class="nf-txt">{_fmt(n.get("text", ""))}</div>'
                         f'<div class="nf-meta"><span title="{full}">{_svg("clock", 13)}{when}</span></div></div>'
                         + (f'<span class="nf-new">{L["new"]}</span>' if un else "") + '</div>').replace("\n", ""), unsafe_allow_html=True)
            idx += 1
    render_footer(compact=True)