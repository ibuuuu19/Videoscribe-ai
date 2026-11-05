"""
Page Profil — design premium (carte d'identité, tuiles de stats, sécurité, zone sensible).
Remplace render_profil() de app.py :

    def render_profil():
        from src.pages.profil import render_profil as _rp
        _rp(user, role, tier)
"""
import html as _h
from datetime import datetime

import streamlit as st

from src.ui.i18n import T

_P = {  # icônes (tracés Lucide-like)
    "shield": "<path d='M12 3l8 3v6c0 4.5-3.2 8.2-8 9-4.8-.8-8-4.5-8-9V6z'/><path d='M9 12l2 2 4-4'/>",
    "plan": "<path d='M3 8l4 3 5-7 5 7 4-3-2 11H5z'/>",
    "cal": "<rect x='3' y='5' width='18' height='16' rx='3'/><path d='M3 10h18M8 3v4M16 3v4'/>",
    "film": "<rect x='3' y='4' width='18' height='16' rx='3'/><path d='M10 9v6l5-3z'/>",
    "key": "<circle cx='8' cy='15' r='4'/><path d='M11 12l9-9M16 7l3 3'/>",
    "warn": "<path d='M12 3l10 18H2z'/><path d='M12 10v5M12 18v.01'/>",
    "check": "<path d='M5 12l5 5 9-10'/>",
}


def _svg(name, size=20):
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' "
            f"stroke-linecap='round' stroke-linejoin='round'>{_P[name]}</svg>")


def _mix(a, b, t):
    try:
        a, b = a.lstrip("#"), b.lstrip("#")
        return "#" + "".join(f"{round(int(a[i:i+2],16)*(1-t)+int(b[i:i+2],16)*t):02X}" for i in (0, 2, 4))
    except Exception:
        return a


def _css(acc, acc2, dark):
    ink = "#F8FAFC" if dark else "#0F1A2E"
    soft = "#AAB8D0" if dark else "#5B6B88"
    surf = "rgba(255,255,255,.045)" if dark else "#FFFFFF"
    surf2 = "rgba(255,255,255,.07)" if dark else "#F3F6FB"
    line = "rgba(255,255,255,.10)" if dark else "rgba(15,26,46,.10)"
    shadow = "0 18px 50px rgba(0,0,0,.35)" if dark else "0 18px 50px rgba(15,26,46,.08)"
    css = f"""
html body .stApp .pf-hero {{ position:relative; overflow:hidden; border-radius:28px; margin:0 0 1.1rem; border:1px solid {line}; background:{surf}; box-shadow:{shadow}; animation:pfIn .5s ease both; }}
html body .stApp .pf-cover {{ height:150px; background:radial-gradient(120% 140% at 15% 0%,color-mix(in srgb,{acc} 85%,#fff) 0,transparent 55%),radial-gradient(90% 120% at 100% 100%,{acc2} 0,transparent 60%),linear-gradient(135deg,{acc2},{acc}); position:relative; }}
html body .stApp .pf-cover::after {{ content:""; position:absolute; inset:0; background:repeating-linear-gradient(115deg,rgba(255,255,255,.07) 0 1px,transparent 1px 26px); mask-image:linear-gradient(180deg,#000,transparent); -webkit-mask-image:linear-gradient(180deg,#000,transparent); }}
html body .stApp .pf-id {{ display:flex; flex-direction:column; align-items:center; text-align:center; padding:0 1.2rem 1.6rem; margin-top:-62px; position:relative; }}
html body .stApp .pf-av {{ position:relative; width:124px; height:124px; border-radius:50%; padding:4px; background:conic-gradient(from 210deg,{acc},{acc2},#D4AF37,{acc}); box-shadow:0 16px 40px color-mix(in srgb,{acc} 45%,transparent); }}
html body .stApp .pf-av > img, html body .stApp .pf-av > .pf-ini {{ width:100%; height:100%; border-radius:50%; object-fit:cover; display:flex; align-items:center; justify-content:center; border:4px solid {"#0A1220" if dark else "#fff"}; box-sizing:border-box; background:linear-gradient(135deg,{acc2},{acc}); color:#fff; font:800 2rem Sora,sans-serif; }}
html body .stApp .pf-av .pf-on {{ position:absolute; right:10px; bottom:10px; width:16px; height:16px; border-radius:50%; background:#22C55E; border:3px solid {"#0A1220" if dark else "#fff"}; }}
html body .stApp .pf-av .pf-pb {{ position:absolute; left:-4px; bottom:-2px; }}
html body .stApp .pf-av .pf-pb .vs-plan {{ display:inline-flex; align-items:center; justify-content:center; border-radius:50%; background:var(--pg,linear-gradient(135deg,{acc},{acc2})); border:3px solid {"#0A1220" if dark else "#fff"}; box-sizing:content-box; box-shadow:0 8px 20px color-mix(in srgb,var(--pc,{acc}) 50%,transparent); }}
html body .stApp .pf-name {{ margin:.9rem 0 0; font:800 clamp(1.5rem,4vw,2.1rem)/1.15 Sora,sans-serif; letter-spacing:-.03em; color:{ink} !important; }}
html body .stApp .pf-sub {{ margin:.25rem 0 0; color:{soft} !important; font-size:.92rem; font-weight:600; }}
html body .stApp .pf-chips {{ display:flex; flex-wrap:wrap; justify-content:center; gap:.5rem; margin-top:1rem; }}
html body .stApp .pf-chip {{ display:inline-flex; align-items:center; gap:6px; padding:6px 14px; border-radius:999px; font-size:.78rem; font-weight:800; color:{ink} !important; background:{surf2}; border:1px solid {line}; }}
html body .stApp .pf-chip.acc {{ color:#fff !important; border-color:transparent; background:linear-gradient(135deg,{acc},{acc2}); box-shadow:0 8px 20px color-mix(in srgb,{acc} 35%,transparent); }}
html body .stApp .pf-chip.gold {{ color:#3B2A00 !important; border-color:transparent; background:linear-gradient(135deg,#F7D774,#D4AF37); }}
html body .stApp .pf-stats {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.9rem; margin-bottom:1.4rem; }}
html body .stApp .pf-stat {{ display:flex; align-items:center; gap:.9rem; padding:1rem 1.05rem; border-radius:22px; background:{surf}; border:1px solid {line}; box-shadow:{shadow}; transition:transform .25s ease, border-color .25s ease; animation:pfIn .5s ease both; }}
html body .stApp .pf-stat:hover {{ transform:translateY(-3px); border-color:color-mix(in srgb,{acc} 55%,{line}); }}
html body .stApp .pf-stat .i {{ flex:none; width:46px; height:46px; border-radius:15px; display:flex; align-items:center; justify-content:center; color:#fff; background:linear-gradient(135deg,{acc},{acc2}); box-shadow:0 8px 18px color-mix(in srgb,{acc} 35%,transparent); }}
html body .stApp .pf-stat small {{ display:block; color:{soft} !important; font-size:.74rem; font-weight:700; letter-spacing:.05em; text-transform:uppercase; }}
html body .stApp .pf-stat b {{ display:block; margin-top:2px; color:{ink} !important; font:800 1.35rem Sora,sans-serif; letter-spacing:-.02em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
html body .stApp .pf-sec {{ display:flex; align-items:center; gap:.8rem; margin:0 0 .9rem; }}
html body .stApp .pf-sec .i {{ flex:none; width:42px; height:42px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:{acc}; background:color-mix(in srgb,{acc} 14%,transparent); border:1px solid color-mix(in srgb,{acc} 28%,transparent); }}
html body .stApp .pf-sec h3 {{ margin:0; padding:0; font:800 1.2rem Sora,sans-serif; letter-spacing:-.02em; color:{ink} !important; }}
html body .stApp .pf-sec p {{ margin:2px 0 0; color:{soft} !important; font-size:.85rem; }}
html body .stApp .st-key-pf_pwd, html body .stApp .st-key-pf_del {{ padding:1.3rem 1.3rem .6rem; border-radius:26px; background:{surf}; border:1px solid {line}; box-shadow:{shadow}; margin-bottom:1.3rem; animation:pfIn .5s ease both; }}
html body .stApp .st-key-pf_del {{ background:linear-gradient(135deg,rgba(239,68,68,{".10" if dark else ".06"}),{surf}); border-color:rgba(239,68,68,.35); }}
html body .stApp .st-key-pf_del .pf-sec .i {{ color:#EF4444; background:rgba(239,68,68,.14); border-color:rgba(239,68,68,.35); }}
html body .stApp .st-key-pf_pwd [data-testid="stForm"], html body .stApp .st-key-pf_del [data-testid="stForm"] {{ border:0 !important; padding:0 !important; background:transparent !important; box-shadow:none !important; }}
html body .stApp .st-key-pf_pwd [data-baseweb="input"], html body .stApp .st-key-pf_pwd [data-baseweb="base-input"] {{ border-radius:14px !important; }}
html body .stApp .st-key-pf_pwd [data-testid="stFormSubmitButton"] button {{ min-height:50px; border-radius:999px !important; border:0 !important; color:#fff !important; font-weight:800 !important;
   background:linear-gradient(135deg,{acc},{acc2}) !important; box-shadow:0 12px 26px color-mix(in srgb,{acc} 35%,transparent) !important; transition:transform .2s ease, box-shadow .25s ease; }}
html body .stApp .st-key-pf_pwd [data-testid="stFormSubmitButton"] button:hover {{ transform:translateY(-2px); }}
html body .stApp .st-key-pf_del [data-testid="stFormSubmitButton"] button {{ min-height:50px; border-radius:999px !important; font-weight:800 !important; color:#EF4444 !important; background:transparent !important; border:1.5px solid rgba(239,68,68,.55) !important; transition:all .2s ease; }}
html body .stApp .st-key-pf_del [data-testid="stFormSubmitButton"] button:hover {{ background:#EF4444 !important; color:#fff !important; box-shadow:0 12px 26px rgba(239,68,68,.35) !important; }}
@keyframes pfIn {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
@media (max-width:900px) {{ html body .stApp .pf-stats {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
@media (max-width:520px) {{ html body .stApp .pf-cover {{ height:110px; }} html body .stApp .pf-id {{ margin-top:-52px; }} html body .stApp .pf-av {{ width:104px; height:104px; }}
  html body .stApp .pf-stat {{ padding:.8rem; gap:.65rem; }} html body .stApp .pf-stat .i {{ width:38px; height:38px; border-radius:12px; }} html body .stApp .pf-stat b {{ font-size:1.1rem; }}
  html body .stApp .st-key-pf_pwd, html body .stApp .st-key-pf_del {{ padding:1rem 1rem .4rem; border-radius:22px; }} }}
@media (prefers-reduced-motion:reduce) {{ html body .stApp .pf-hero, html body .stApp .pf-stat, html body .stApp .st-key-pf_pwd, html body .stApp .st-key-pf_del {{ animation:none; }} }}
"""
    st.markdown("<style>" + css.replace("\n", " ") + "</style>", unsafe_allow_html=True)


def render_profil(user, role, tier):
    from src.core.config import PLANS, COOKIE_NAME
    from src.ui.css import shade
    from src.ui.fast import get_plan, list_users, get_avatar_b64
    from src.ui.layout import notify_admins, render_footer
    from src.ui.usermenu import plan_badge, _BADGE_CSS
    from src.history_manager import get_history, clear_history
    from src.user_manager import authenticate, reset_password, delete_user
    from src.session_manager import delete_session
    from src.core.cookies import delete_cookie

    dark = st.session_state.get("theme", "light") == "dark"
    acc = st.session_state.get("cfg_accent", "#2E6DB4")
    acc2 = shade(acc, 0.55)
    _css(acc, acc2, dark)
    st.markdown("<style>" + _BADGE_CSS + "</style>", unsafe_allow_html=True)

    info = list_users().get(user, {})
    cur = "premium_plus" if role == "admin" else get_plan(user)
    plan_name = PLANS[cur]["name"] if cur != "free" else T("plan_free")
    e = lambda x: _h.escape(str(x))

    av = get_avatar_b64(user)
    face = f'<img src="{av}" alt="">' if av else f'<div class="pf-ini">{e(user[:2].upper())}</div>'
    chips = [f'<span class="pf-chip acc">{e("Admin" if role == "admin" else "Client")}</span>',
             f'<span class="pf-chip gold">{e(plan_name)}</span>' if cur != "free" else f'<span class="pf-chip">{e(plan_name)}</span>']
    if tier >= 3:
        chips.append(f'<span class="pf-chip">{_svg("check", 14)} {e(T("certified"))}</span>')
    st.markdown((f'<div class="pf-hero"><div class="pf-cover"></div><div class="pf-id">'
                 f'<div class="pf-av">{face}<span class="pf-on"></span><span class="pf-pb">{plan_badge(tier, 34)}</span></div>'
                 f'<h1 class="pf-name">@{e(user)}</h1><div class="pf-sub">{e(T("profile"))}</div>'
                 f'<div class="pf-chips">{"".join(chips)}</div></div></div>').replace("\n", ""), unsafe_allow_html=True)

    exp = info.get("premium_expires")
    try:
        exp_s = datetime.fromisoformat(exp).strftime("%d/%m/%Y") if exp and cur != "free" else "—"
    except Exception:
        exp_s = "—"
    stats = [("shield", T("role"), role), ("plan", T("plan"), plan_name), ("cal", T("expires"), exp_s),
             ("film", T("m_analyse"), len(get_history(user)))]
    tiles = "".join(f'<div class="pf-stat" style="animation-delay:{i*70}ms"><span class="i">{_svg(n, 22)}</span><div><small>{e(l)}</small><b>{e(v)}</b></div></div>'
                    for i, (n, l, v) in enumerate(stats))
    st.markdown(f'<div class="pf-stats">{tiles}</div>', unsafe_allow_html=True)

    with st.container(key="pf_pwd"):
        st.markdown(f'<div class="pf-sec"><span class="i">{_svg("key", 20)}</span><div><h3>{e(T("change_pwd"))}</h3></div></div>', unsafe_allow_html=True)
        with st.form("pwd_form", border=False):
            cur_p = st.text_input(T("pwd_current"), type="password")
            c1, c2 = st.columns(2)
            new = c1.text_input(T("pwd_new"), type="password")
            conf = c2.text_input(T("pwd_confirm"), type="password")
            if st.form_submit_button(T("pwd_update"), use_container_width=True):
                ok, _ = authenticate(user, cur_p)
                if not ok: st.error("Mot de passe actuel incorrect.")
                elif new != conf: st.error("La confirmation ne correspond pas.")
                elif reset_password(user, new):
                    notify_admins("key", f"**{user}** a changé son mot de passe."); st.success("Mot de passe mis à jour.")
                else: st.error("Nouveau mot de passe trop court.")

    with st.container(key="pf_del"):
        st.markdown(f'<div class="pf-sec"><span class="i">{_svg("warn", 20)}</span><div><h3>{e(T("del_title"))}</h3><p>{e(T("del_caption"))}</p></div></div>', unsafe_allow_html=True)
        with st.form("delete_form", border=False):
            confirm_del = st.checkbox(T("del_check"))
            if st.form_submit_button(T("del_btn"), use_container_width=True):
                if confirm_del:
                    uname = user
                    notify_admins("trash", f"Compte **{uname}** supprimé (RGPD).")
                    delete_user(uname); clear_history(uname)
                    from src.core.avatar_store import delete_avatar; delete_avatar(uname)
                    delete_session(st.session_state.get("token")); delete_cookie(COOKIE_NAME); delete_cookie("ys_user")
                    st.session_state.update(user=None, role=None, result=None, token=None, page="accueil", show_privacy=False)
                    st.rerun()
                else:
                    st.error("Cochez la case de confirmation.")
    render_footer(compact=True)