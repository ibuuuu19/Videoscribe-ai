"""
Pages d'authentification — Connexion et inscription.

Contient :
- render_login() : Page de connexion
- render_register_wizard() : Assistant d'inscription en 4 étapes
- render_register_page() : Page wrapper de l'inscription

Extrait de app.py pour alléger le fichier principal (~290 lignes).

Usage:
    from src.pages.auth import render_login, render_register_page
"""

import time
import secrets

import streamlit as st

from src.ui.i18n import T, LANGS
from src.ui.components import ic, logo_html
from src.ui.layout import render_footer, _toggle_theme, notify_admins, notify, sync_notif_cursor
from src.ui.navbar import render_navbar   # barre fixe premium
from src.ui.prefs import _load_appearance
from src.ui.storage import get_referral_code
from src.core.config import COOKIE_NAME
from src.core.cookies import set_cookie
from src.user_manager import register_user, authenticate, list_users
from src.session_manager import create_session
from src.email_manager import send_verification_code


# ═══════════════════════════════════════════════════════════════
# ⚠️ Les fonctions ci-dessous ont été copiées automatiquement
#    depuis app.py par le script extract_auth.py
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# HELPERS DU WIZARD
# ═══════════════════════════════════════════════════════════════

def _step_indicator(current):
    """Indicateur de progression du wizard (4 étapes, avec libellés)."""
    labels = _l()["steps"]
    parts = ['<div class="vsa-steps">']
    for i, lab in enumerate(labels, 1):
        cls = "active" if i == current else ("done" if i < current else "")
        parts.append(f'<div class="vsa-st {cls}"><i>{"✓" if i < current else i}</i><span>{lab}</span></div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_register_wizard():
    step = st.session_state.get("reg_step", 1)
    _step_indicator(step)
    if step == 1:
        u = st.text_input(T("username")+" (3 min)", value=st.session_state.get("reg_u",""))
        e = st.text_input(T("your_email"), value=st.session_state.get("reg_e",""))
        lang_sel = st.selectbox(
            T("language"),
            list(LANGS.keys()),
            format_func=lambda l: LANGS[l],
            key="reg_lang_widget"
        )
        parrain = st.text_input("Code parrain", value="", max_chars=12)
        email = (e or "").strip(); verified = st.session_state.get("reg_email_verified", False)
        if email and not verified:
            st.markdown("---"); _m = st.session_state.get("reg_msg")
            if _m:
                if _m[0]=="ok": st.success(_m[1])
                elif _m[0]=="demo": st.warning(_m[1])
                else: st.error(_m[1])
            if not st.session_state.get("reg_code_sent"):
                if st.button(T("resend"), use_container_width=True):
                    code = f"{secrets.randbelow(1000000):06d}"
                    st.session_state.reg_code = code; st.session_state.reg_code_exp = time.time()+300; st.session_state.reg_code_sent = True
                    ok, err = send_verification_code(email, code)
                    if ok: st.session_state.reg_msg = ("ok", f"Code envoyé à **{email}**")
                    else: st.session_state.reg_msg = ("demo", f"{err} → code démo : **{code}**")
                    st.rerun()
            else:
                cin = st.text_input("Code (6)", max_chars=6); b1,b2,b3 = st.columns(3)
                with b1:
                    if st.button(T("verify"), use_container_width=True):
                        if time.time() > st.session_state.get("reg_code_exp",0): st.session_state.reg_msg=("err","Code expiré.")
                        elif (cin or "").strip()==st.session_state.get("reg_code"): st.session_state.reg_email_verified=True; st.session_state.reg_msg=("ok",f"Email vérifié : {email}")
                        else: st.session_state.reg_msg=("err","Code incorrect.")
                        st.rerun()
                with b2:
                    if st.button(T("resend"), use_container_width=True):
                        code = f"{secrets.randbelow(1000000):06d}"; st.session_state.reg_code=code; st.session_state.reg_code_exp=time.time()+300
                        ok, err = send_verification_code(email, code)
                        st.session_state.reg_msg=("ok" if ok else "demo", f"Nouveau code : {code}")
                        st.rerun()
                with b3:
                    if st.button("Email ↺", use_container_width=True): st.session_state.update(reg_code_sent=False, reg_email_verified=False, reg_msg=None); st.rerun()
        elif email and verified: st.success(f"Email vérifié : {email}")
        if st.button(T("continue"), use_container_width=True, type="primary"):
            if len((u or "").strip())<3: st.error("3 caractères minimum.")
            elif email and not verified: st.error("Vérifiez votre email.")
            else: st.session_state.update(reg_u=(u or "").strip(), reg_e=email, reg_lang=lang_sel, reg_parrain=(parrain or "").strip().upper(), reg_step=2); st.rerun()
    elif step == 2:
        st.markdown("### Sécurité")
        p = st.text_input(T("password")+" (6 min)", type="password"); c = st.text_input(T("pwd_confirm"), type="password")
        b1,b2 = st.columns(2)
        with b1:
            if st.button(T("back"), use_container_width=True): st.session_state.reg_step=1; st.rerun()
        with b2:
            if st.button(T("continue"), use_container_width=True, type="primary"):
                if len(p)<6: st.error("6 caractères minimum.")
                elif p!=c: st.error("La confirmation ne correspond pas.")
                else: st.session_state.update(reg_p=p, reg_step=3); st.rerun()
    elif step == 3:
        st.markdown("### Préférences")
        th = st.selectbox(
            T("appearance"),
            ["light","dark"],
            format_func=lambda t: T("light") if t=="light" else T("dark"),
            key="reg_th_widget"
        )
        tr = st.checkbox(T("chip_tr"), value=st.session_state.get("reg_tr", True))
        b1,b2 = st.columns(2)
        with b1:
            if st.button(T("back"), use_container_width=True): st.session_state.reg_step=2; st.rerun()
        with b2:
            if st.button(T("continue"), use_container_width=True, type="primary"): st.session_state.update(reg_th=th, reg_tr=tr, reg_step=4); st.rerun()
    else:
        st.markdown("### Confirmation")
        em = st.session_state.get("reg_e","")
        st.info(f"**{T('username')}** : {st.session_state.get('reg_u')}  •  **Email** : {(em+' ✓') if (em and st.session_state.get('reg_email_verified')) else (em or '—')}  •  **{T('language')}** : {LANGS.get(st.session_state.get('reg_lang','fr'),'fr')}")
        accept = st.checkbox("RGPD ✓")
        b1,b2 = st.columns(2)
        with b1:
            if st.button(T("back"), use_container_width=True): st.session_state.reg_step=3; st.rerun()
        with b2:
            if st.button(T("register"), use_container_width=True, type="primary"):
                if not accept: st.error("Acceptez la politique RGPD.")
                else:
                    ok, msg = register_user(st.session_state.reg_u, st.session_state.reg_p, st.session_state.get("reg_e",""))
                    if ok:
                        uname = st.session_state.reg_u.lower()
                        chosen = st.session_state.get("reg_lang","fr")
                        notify(uname, "spark", "Bienvenue sur VideoScribe AI !")
                        notify_admins("user", f"Nouveau compte : **{uname}**")
                        pc = st.session_state.get("reg_parrain","")
                        if pc:
                            for ref, ru in list_users().items():
                                if get_referral_code(ref).upper() == pc:
                                    notify(ref, "users", f"Filleul inscrit : **{uname}** → +3 jours gratuits")
                        st.session_state.update(user=uname, role="client", token=create_session(uname), theme=st.session_state.get("reg_th","light"), cfg_translate=st.session_state.get("reg_tr",True),
                        cfg_lang=chosen, cfg_target=chosen if chosen!="fr" else "fr",
                        reg_step=1, reg_code_sent=False, reg_email_verified=False, reg_code=None, reg_msg=None, page="analyse")
                        _load_appearance(uname)
                        sync_notif_cursor(uname)
                        set_cookie(COOKIE_NAME, st.session_state.token)
                        set_cookie("ys_user", uname, max_age=30*24*3600)
                        set_cookie("ys_theme", st.session_state.theme, max_age=365*24*3600); st.balloons(); st.rerun()
                    else: st.error(f"{msg}")

# ⚠️ def render_landing(): extrait dans src/pages/public.py
# ═══════════════════════════════════════════════════════════════
# STYLE « PREMIUM » (connexion + inscription)
# ═══════════════════════════════════════════════════════════════

_TXT = {
    "fr": {
        "steps": ["Compte", "Sécurité", "Préférences", "Confirmation"],
        "h_a": "Bon retour parmi", "h_b": "les esprits efficaces",
        "lead": "Retrouvez tous vos résumés, vos favoris, vos statistiques et vos exports. Reprenez exactement là où vous vous étiez arrêté.",
        "f1": ("Historique complet", "Toutes vos analyses, toujours accessibles"), "f2": ("Favoris & collections", "Organisez vos vidéos clés"),
        "f3": ("Statistiques détaillées", "Temps, mots, chunks, tendances"), "f4": ("Exports illimités", "PDF, Markdown, Obsidian, Notion"),
        "quote": "« Je révise mes cours en 10 min au lieu d'1 h de vidéo. »", "qa": "Khadija D.", "qr": "Étudiante en médecine",
        "ph_user": "Votre pseudo", "remember": "Se souvenir de moi", "suspended": "⛔ Compte suspendu. Contactez le support.",
        "bad": "❌ Identifiants incorrects.", "or": "ou", "secure": "Connexion sécurisée · Conformité RGPD",
        "no_acc": "Pas encore de compte ?", "reg_a": "Rejoignez", "reg_b": "VideoScribe AI", "reg_lead": "Créez votre compte gratuit en 4 étapes — sans carte bancaire.",
        "p1": "3 analyses par jour offertes", "p2": "Résumés, quiz et exports", "p3": "Données jamais revendues",
        "have": "Déjà un compte ?",
    },
    "en": {
        "steps": ["Account", "Security", "Preferences", "Confirm"],
        "h_a": "Welcome back to", "h_b": "efficient minds",
        "lead": "Find all your summaries, favourites, statistics and exports. Pick up exactly where you left off.",
        "f1": ("Full history", "All your analyses, always within reach"), "f2": ("Favourites & collections", "Organise your key videos"),
        "f3": ("Detailed statistics", "Time, words, chunks, trends"), "f4": ("Unlimited exports", "PDF, Markdown, Obsidian, Notion"),
        "quote": "“I revise my classes in 10 min instead of 1 h of video.”", "qa": "Khadija D.", "qr": "Medical student",
        "ph_user": "Your username", "remember": "Remember me", "suspended": "⛔ Account suspended. Please contact support.",
        "bad": "❌ Incorrect credentials.", "or": "or", "secure": "Secure sign-in · GDPR compliant",
        "no_acc": "No account yet?", "reg_a": "Join", "reg_b": "VideoScribe AI", "reg_lead": "Create your free account in 4 steps — no credit card.",
        "p1": "3 free analyses per day", "p2": "Summaries, quizzes and exports", "p3": "Your data is never resold",
        "have": "Already have an account?",
    },
}


def _l() -> dict:
    lg = st.session_state.get("cfg_lang", "fr")
    return _TXT["fr"] if lg == "fr" else _TXT["en"]


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _css() -> None:
    light = st.session_state.get("theme", "light") == "light"
    ink = "#0F1A2E" if light else "#F8FAFC"
    soft = "#4A5A7A" if light else "rgba(203,213,225,.85)"
    card = "#FFFFFF" if light else "rgba(255,255,255,.05)"
    field = "#F3F7FD" if light else "rgba(255,255,255,.07)"
    line = "rgba(15,26,46,.10)" if light else "rgba(255,255,255,.12)"
    shadow = "0 28px 70px rgba(15,26,46,.11)" if light else "0 28px 80px rgba(0,0,0,.55)"
    V = 'html body .stApp div[data-testid="stVerticalBlock"].st-key-vsa_card'
    st.markdown(f"""<style>
html body .stApp .vsa-left{{position:relative;overflow:hidden;isolation:isolate;border-radius:30px;padding:clamp(1.8rem,3.2vw,2.8rem);min-height:640px;color:#F8FAFC;display:flex;flex-direction:column;justify-content:space-between;
  background:radial-gradient(640px 360px at 8% 0%,rgba(59,130,246,.45),transparent 62%),radial-gradient(520px 320px at 95% 100%,rgba(16,185,129,.32),transparent 62%),linear-gradient(160deg,#05080F 0%,#0A1220 50%,#0D1830 100%);
  border:1px solid rgba(255,255,255,.10);box-shadow:0 40px 100px rgba(2,8,18,.38);}}
html body .stApp .vsa-left::before{{content:"";position:absolute;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:44px 44px;
  -webkit-mask-image:radial-gradient(ellipse at 50% 40%,#000 25%,transparent 75%);mask-image:radial-gradient(ellipse at 50% 40%,#000 25%,transparent 75%);}}
html body .stApp .vsa-in{{position:relative;z-index:1;}}
html body .stApp .vsa-brand{{display:flex;align-items:center;gap:12px;font-family:'Sora',sans-serif;font-weight:800;font-size:1.2rem;color:#F8FAFC !important;margin-bottom:2rem;}}
html body .stApp .vsa-brand i{{font-style:normal;background:linear-gradient(92deg,#60A5FA,#34D399);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}}
html body .stApp .vsa-h2{{font-family:'Sora',sans-serif;font-weight:800;letter-spacing:-.04em;line-height:1.08;font-size:clamp(1.8rem,2.7vw,2.5rem);color:#F8FAFC !important;margin:0 0 1rem;}}
html body .stApp .vsa-h2 em{{font-style:normal;background:linear-gradient(92deg,#60A5FA,#34D399 55%,#FBBF24);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}}
html body .stApp .vsa-lead{{color:rgba(226,232,240,.80) !important;font-size:1rem;line-height:1.75;margin:0 0 1.6rem;max-width:520px;}}
html body .stApp .vsa-feats{{display:grid;gap:.65rem;}}
html body .stApp .vsa-feat{{display:flex;align-items:center;gap:12px;padding:.7rem .9rem;border-radius:14px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.10);backdrop-filter:blur(8px);}}
html body .stApp .vsa-feat .ic{{width:34px;height:34px;border-radius:11px;flex:none;display:flex;align-items:center;justify-content:center;color:#fff !important;background:linear-gradient(135deg,#3B82F6,#10B981);box-shadow:0 8px 18px rgba(59,130,246,.30);}}
html body .stApp .vsa-feat .ic svg{{stroke:#fff;}}
html body .stApp .vsa-feat b{{display:block;color:#F8FAFC !important;font-size:.92rem;}}
html body .stApp .vsa-feat small{{color:rgba(148,163,184,.95) !important;font-size:.78rem;}}
html body .stApp .vsa-quote{{margin-top:1.8rem;padding-top:1.3rem;border-top:1px solid rgba(255,255,255,.10);font-style:italic;color:rgba(203,213,225,.88) !important;font-size:.9rem;line-height:1.7;}}
html body .stApp .vsa-qa{{display:flex;align-items:center;gap:10px;margin-top:.8rem;font-style:normal;}}
html body .stApp .vsa-qa i{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:800;font-size:.8rem;color:#fff !important;background:linear-gradient(135deg,#3B82F6,#60A5FA);font-family:'Sora',sans-serif;}}
html body .stApp .vsa-qa b{{color:#F8FAFC !important;font-size:.88rem;display:block;}} html body .stApp .vsa-qa small{{color:rgba(148,163,184,.95) !important;}}
html body .stApp .vsa-pills{{display:flex;flex-wrap:wrap;gap:.5rem;}}
html body .stApp .vsa-pills span{{display:inline-flex;align-items:center;gap:7px;padding:7px 14px;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);color:#F1F5F9 !important;font-size:.82rem;font-weight:700;}}
html body .stApp .vsa-pills svg{{stroke:#34D399;}}
/* carte formulaire */
{V}{{background:{card} !important;border:1px solid {line} !important;border-radius:28px !important;padding:clamp(1.4rem,2.6vw,2.2rem) !important;box-shadow:{shadow} !important;gap:.7rem !important;}}
html body .stApp .vsa-ct{{font-family:'Sora',sans-serif;font-weight:800;letter-spacing:-.03em;font-size:1.65rem;color:{ink} !important;margin:0 0 .25rem;}}
html body .stApp .vsa-cs{{color:{soft} !important;font-size:.93rem;margin:0 0 .6rem;}}
html body .stApp .vsa-logo{{display:flex;justify-content:center;margin-bottom:.4rem;}}
html body .stApp .vsa-center{{text-align:center;}}
{V} label p, {V} [data-testid="stWidgetLabel"] p{{color:{ink} !important;font-weight:700 !important;font-size:.88rem !important;}}
{V} [data-testid="stTextInput"] input, {V} [data-testid="stTextArea"] textarea{{background:{field} !important;color:{ink} !important;border:1px solid {line} !important;border-radius:14px !important;min-height:48px;box-shadow:none !important;}}
{V} [data-testid="stTextInput"] input:focus{{border-color:#3B82F6 !important;box-shadow:0 0 0 3px rgba(59,130,246,.22) !important;}}
{V} [data-baseweb="select"] > div{{background:{field} !important;border:1px solid {line} !important;border-radius:14px !important;}}
{V} .stButton > button, {V} [data-testid="stFormSubmitButton"] button{{min-height:50px !important;border-radius:14px !important;font-weight:800 !important;background:transparent !important;border:1px solid {line} !important;box-shadow:none !important;transform:none !important;filter:none !important;transition:background .2s ease,border-color .2s ease,box-shadow .2s ease !important;}}
{V} .stButton > button p, {V} [data-testid="stFormSubmitButton"] button p{{color:{ink} !important;font-weight:800 !important;}}
{V} .stButton > button:hover, {V} [data-testid="stFormSubmitButton"] button:hover{{background:rgba(46,109,180,.10) !important;border-color:rgba(46,109,180,.45) !important;}}
{V} button[data-testid*="primary"], {V} button[kind="primary"], {V} button[kind="primaryFormSubmit"]{{background:linear-gradient(135deg,#1B3B6F,#2E6DB4) !important;border:none !important;box-shadow:0 14px 30px rgba(46,109,180,.34) !important;}}
{V} button[data-testid*="primary"] p, {V} button[kind="primary"] p, {V} button[kind="primaryFormSubmit"] p{{color:#fff !important;}}
{V} button[data-testid*="primary"]:hover, {V} button[kind="primary"]:hover, {V} button[kind="primaryFormSubmit"]:hover{{background:linear-gradient(135deg,#1B3B6F,#3B82F6) !important;transform:translateY(-1px) !important;box-shadow:0 18px 36px rgba(46,109,180,.42) !important;}}
{V} [data-testid="stForm"]{{border:none !important;padding:0 !important;background:transparent !important;box-shadow:none !important;}}
html body .stApp div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .vsa-left){{max-width:1240px;margin:0 auto;align-items:center;}}
{V} h3{{font-family:'Sora',sans-serif;font-weight:800;letter-spacing:-.02em;color:{ink} !important;font-size:1.3rem;margin:.2rem 0 0;padding:0;}}
html body .stApp .vsa-or{{display:flex;align-items:center;gap:12px;color:{soft} !important;font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;margin:.3rem 0;}}
html body .stApp .vsa-or::before, html body .stApp .vsa-or::after{{content:"";flex:1;height:1px;background:{line};}}
html body .stApp .vsa-sec{{display:flex;align-items:center;justify-content:center;gap:8px;color:{soft} !important;font-size:.8rem;margin-top:.5rem;}}
html body .stApp .vsa-sec svg{{stroke:#10B981;}}
/* indicateur d'étapes */
html body .stApp .vsa-steps{{display:flex;align-items:flex-start;justify-content:space-between;gap:.4rem;max-width:560px;margin:.4rem auto 1.2rem;position:relative;}}
html body .stApp .vsa-st{{flex:1;display:flex;flex-direction:column;align-items:center;gap:.4rem;position:relative;text-align:center;}}
html body .stApp .vsa-st::before{{content:"";position:absolute;top:17px;left:-50%;width:100%;height:2px;background:{line};z-index:0;}}
html body .stApp .vsa-st:first-child::before{{display:none;}}
html body .stApp .vsa-st.done::before, html body .stApp .vsa-st.active::before{{background:linear-gradient(90deg,#3B82F6,#10B981);}}
html body .stApp .vsa-st i{{position:relative;z-index:1;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:800;font-size:.85rem;font-family:'Sora',sans-serif;
  background:{card};border:2px solid {line};color:{soft} !important;}}
html body .stApp .vsa-st.active i{{background:linear-gradient(135deg,#1B3B6F,#2E6DB4);border-color:transparent;color:#fff !important;box-shadow:0 10px 22px rgba(46,109,180,.38);}}
html body .stApp .vsa-st.done i{{background:linear-gradient(135deg,#10B981,#34D399);border-color:transparent;color:#fff !important;}}
html body .stApp .vsa-st span{{font-size:.74rem;font-weight:700;color:{soft} !important;}}
html body .stApp .vsa-st.active span{{color:{ink} !important;}}
@media (max-width:900px){{ html body .stApp .vsa-left{{display:none;}} html body .stApp div[data-testid="stColumn"]:has(.vsa-left){{display:none !important;}} .vsa-st span{{font-size:.66rem;}} }}
</style>""", unsafe_allow_html=True)


def render_login():
    render_navbar()
    _css()
    L = _l()
    _left, _right = st.columns([1.05, 1], gap="large")
    with _left:
        feats = "".join(
            f'<div class="vsa-feat"><span class="ic">{ic(i, 16)}</span><div><b>{t}</b><small>{d}</small></div></div>'
            for i, (t, d) in zip(("book", "star", "chart", "download"), (L["f1"], L["f2"], L["f3"], L["f4"])))
        st.markdown(f"""<div class="vsa-left"><div class="vsa-in">
<div class="vsa-brand">{logo_html(38)}<span>VideoScribe<i> AI</i></span></div>
<h2 class="vsa-h2">{L["h_a"]}<br><em>{L["h_b"]}</em>.</h2>
<div class="vsa-lead">{L["lead"]}</div>
<div class="vsa-feats">{feats}</div>
<div class="vsa-quote">{L["quote"]}<div class="vsa-qa"><i>K</i><div><b>{L["qa"]}</b><small>{L["qr"]}</small></div></div></div>
</div></div>""".replace("\n", ""), unsafe_allow_html=True)
    with _right:
        with _keyed("vsa_card"):
            st.markdown(f'<div class="vsa-ct">{T("login_title")}</div><div class="vsa-cs">{T("login_sub")}</div>', unsafe_allow_html=True)
            with st.form("login_form", border=False):
                username = st.text_input(T("username"), placeholder=L["ph_user"], key="login_user")
                password = st.text_input(T("password"), type="password", placeholder="••••••••", key="login_pass")
                _remember = st.checkbox(L["remember"], value=True, key="login_remember")
                _submit = st.form_submit_button(f"{T('continue')}", use_container_width=True, type="primary")
                if _submit:
                    ok, role_ = authenticate(username, password)
                    if ok:
                        uname = (username or "").strip().lower()
                        st.session_state.update(user=uname, role=role_, token=create_session(uname), page="analyse")
                        _load_appearance(uname)
                        sync_notif_cursor(uname)
                        set_cookie(COOKIE_NAME, st.session_state.token, max_age=(30*24*3600 if _remember else 7*24*3600))
                        set_cookie("ys_user", uname, max_age=30*24*3600)
                        st.rerun()
                    elif role_ == "suspended":
                        st.error(L["suspended"])
                    else:
                        st.error(L["bad"])
            st.markdown(f'<div class="vsa-or">{L["or"]}</div>', unsafe_allow_html=True)
            _a1, _a2 = st.columns(2)
            with _a1:
                if st.button(T("register"), use_container_width=True, key="login_to_register"):
                    st.session_state.page = "register"; st.rerun()
            with _a2:
                if st.button("← " + T("home"), use_container_width=True, key="login_to_home"):
                    st.session_state.page = "accueil"; st.rerun()
            st.markdown(f'<div class="vsa-sec">{ic("lock", 14)} {L["secure"]}</div>', unsafe_allow_html=True)
    render_footer(compact=True)


def render_register_page():
    render_navbar()
    _css()
    L = _l()
    _cl, _cm, _cr = st.columns([1, 1.7, 1])
    with _cm:
        st.markdown(f'<div class="vsa-center"><div class="vsa-logo">{logo_html(56)}</div><div class="vsa-ct" style="font-size:2rem">{T("reg_title")}</div>'
                    f'<div class="vsa-cs">{L["reg_lead"]}</div></div>', unsafe_allow_html=True)
        with _keyed("vsa_card"):
            render_register_wizard()
            st.markdown(f'<div class="vsa-or">{L["have"]}</div>', unsafe_allow_html=True)
            if st.button(T("login"), use_container_width=True, key="reg_to_login"):
                st.session_state.page = "login"; st.rerun()
            st.markdown(f'<div class="vsa-sec">{ic("lock", 14)} {L["secure"]}</div>', unsafe_allow_html=True)
    render_footer(compact=True)