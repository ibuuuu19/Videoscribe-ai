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
from src.ui.layout import render_footer, _toggle_theme
from src.core.config import COOKIE_NAME
from src.core.cookies import set_cookie
from src.user_manager import register_user, authenticate, list_users
from src.session_manager import create_session
from src.email_manager import send_verification_code


# ═══════════════════════════════════════════════════════════════
# ⚠️ Les fonctions ci-dessous ont été copiées automatiquement
#    depuis app.py par le script extract_auth.py
# ═══════════════════════════════════════════════════════════════

def render_register_wizard():
    step = st.session_state.get("reg_step", 1)
    _step_indicator(step); st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    if step == 1:
        st.markdown(f"### {T('reg_title')}"); st.caption(T("reg_sub"))
        u = st.text_input(T("username")+" (3 min)", value=st.session_state.get("reg_u",""))
        e = st.text_input(T("your_email"), value=st.session_state.get("reg_e",""))
        lang_sel = st.selectbox(
            T("language"),
            list(LANGS.keys()),
            format_func=lambda l: LANGS[l],
            key="reg_lang_widget"
        )
        parrain = st.text_input("Code parrain", value="", max_chars=12)
        email = e.strip(); verified = st.session_state.get("reg_email_verified", False)
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
                        elif cin.strip()==st.session_state.get("reg_code"): st.session_state.reg_email_verified=True; st.session_state.reg_msg=("ok",f"Email vérifié : {email}")
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
        if st.button(T("continue"), use_container_width=True):
            if len(u.strip())<3: st.error("3 caractères minimum.")
            elif email and not verified: st.error("Vérifiez votre email.")
            else: st.session_state.update(reg_u=u.strip(), reg_e=email, reg_lang=lang_sel, reg_parrain=parrain.strip().upper(), reg_step=2); st.rerun()
    elif step == 2:
        st.markdown("### Sécurité")
        p = st.text_input(T("password")+" (6 min)", type="password"); c = st.text_input(T("pwd_confirm"), type="password")
        b1,b2 = st.columns(2)
        with b1:
            if st.button(T("back"), use_container_width=True): st.session_state.reg_step=1; st.rerun()
        with b2:
            if st.button(T("continue"), use_container_width=True):
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
            if st.button(T("continue"), use_container_width=True): st.session_state.update(reg_th=th, reg_tr=tr, reg_step=4); st.rerun()
    else:
        st.markdown("### Confirmation")
        em = st.session_state.get("reg_e","")
        st.info(f"**{T('username')}** : {st.session_state.get('reg_u')}  •  **Email** : {(em+' ✓') if (em and st.session_state.get('reg_email_verified')) else (em or '—')}  •  **{T('language')}** : {LANGS.get(st.session_state.get('reg_lang','fr'),'fr')}")
        accept = st.checkbox("RGPD ✓")
        b1,b2 = st.columns(2)
        with b1:
            if st.button(T("back"), use_container_width=True): st.session_state.reg_step=3; st.rerun()
        with b2:
            if st.button(T("register"), use_container_width=True):
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
    st.markdown('</div>', unsafe_allow_html=True)

# ⚠️ def render_landing(): extrait dans src/pages/public.py
def render_login():
    st.markdown("""
    <style>
    .vs-login-left {
        position:relative; overflow:hidden; padding: 3rem 2.6rem; border-radius: 24px;
        background:
            radial-gradient(600px 340px at 10% 0%, rgba(59,130,246,.38), transparent 62%),
            radial-gradient(500px 300px at 90% 100%, rgba(16,185,129,.28), transparent 62%),
            linear-gradient(160deg, #05080F 0%, #0A1220 50%, #0D1524 100%);
        display:flex; flex-direction:column; justify-content:space-between;
        color:#F8FAFC !important;
        border:1px solid rgba(255,255,255,.10);
        box-shadow: 0 40px 100px rgba(2,8,18,.35);
        min-height: 620px;
    }
    .vs-login-left::before {
        content:""; position:absolute; inset:0; z-index:0;
        background-image:
            linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
        background-size: 40px 40px;
        mask-image: radial-gradient(ellipse at center, black 25%, transparent 75%);
        -webkit-mask-image: radial-gradient(ellipse at center, black 25%, transparent 75%);
        pointer-events:none;
    }
    .vs-login-left-inner { position:relative; z-index:1; }
    .vs-login-brand {
        display:flex; align-items:center; gap:12px; margin-bottom: 2.5rem;
        font-family:'Sora',sans-serif; font-weight:800; font-size:1.25rem;
        color:#F8FAFC !important;
    }
    .vs-login-h2 {
        font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.04em;
        line-height:1.08; font-size: clamp(1.7rem, 2.6vw, 2.4rem);
        color:#F8FAFC !important; margin-bottom: 1.1rem;
    }
    .vs-login-h2 .grad {
        background: linear-gradient(92deg,#60A5FA,#34D399 55%,#FBBF24);
        -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    }
    .vs-login-lead {
        color: rgba(226,232,240,.78) !important; font-size: 1rem;
        line-height: 1.75; margin-bottom: 1.8rem;
    }
    .vs-login-feats { display:flex; flex-direction:column; gap:.7rem; }
    .vs-login-feat {
        display:flex; align-items:flex-start; gap:11px; padding:.7rem .85rem;
        background: rgba(255,255,255,.045); border:1px solid rgba(255,255,255,.09);
        border-radius: 13px; color:#E2E8F0 !important; font-size:.9rem;
    }
    .vs-login-feat .ic {
        width:30px; height:30px; border-radius:9px; flex-shrink:0;
        display:flex; align-items:center; justify-content:center;
        background: linear-gradient(135deg, rgba(59,130,246,.28), rgba(16,185,129,.28));
        color:#60A5FA !important;
    }
    .vs-login-feat b { color:#F8FAFC !important; font-weight:700; }
    .vs-login-feat small { color: rgba(148,163,184,.9) !important; display:block; font-size:.76rem; margin-top:2px; }
    .vs-login-quote {
        margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,.08);
        font-style: italic; color: rgba(203,213,225,.85) !important; font-size: .88rem; line-height:1.7;
    }
    .vs-login-quote-author {
        display:flex; align-items:center; gap:9px; margin-top:.7rem; font-style: normal;
    }
    .vs-login-quote-avatar {
        width:32px; height:32px; border-radius:50%;
        background: linear-gradient(135deg,#3B82F6,#60A5FA);
        display:flex; align-items:center; justify-content:center;
        color:#fff !important; font-weight:800; font-size:.78rem; font-family:'Sora',sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    _left, _right = st.columns([1.05, 1], gap="large")
    with _left:
        st.markdown(f"""
        <div class="vs-login-left">
            <div class="vs-login-left-inner">
                <div class="vs-login-brand">{logo_html(38)}<span><b>VideoScribe</b> AI</span></div>
                <h2 class="vs-login-h2">Bon retour parmi<br>les <span class="grad">esprits efficaces</span>.</h2>
                <p class="vs-login-lead">
                    Retrouvez tous vos résumés, vos favoris, vos statistiques et vos exports.
                    Reprenez exactement là où vous vous étiez arrêté.
                </p>
                <div class="vs-login-feats">
                    <div class="vs-login-feat">
                        <span class="ic">{ic("book", 15)}</span>
                        <div><b>Historique complet</b><small>Toutes vos analyses, toujours accessibles</small></div>
                    </div>
                    <div class="vs-login-feat">
                        <span class="ic">{ic("star", 15)}</span>
                        <div><b>Favoris & collections</b><small>Organisez vos vidéos clés</small></div>
                    </div>
                    <div class="vs-login-feat">
                        <span class="ic">{ic("chart", 15)}</span>
                        <div><b>Statistiques détaillées</b><small>Temps, mots, chunks, tendances</small></div>
                    </div>
                    <div class="vs-login-feat">
                        <span class="ic">{ic("download", 15)}</span>
                        <div><b>Exports illimités</b><small>PDF, Markdown, Obsidian, Notion</small></div>
                    </div>
                </div>
                <div class="vs-login-quote">
                    « Je révise mes cours en 10 min au lieu d'1 h de vidéo. »
                    <div class="vs-login-quote-author">
                        <div class="vs-login-quote-avatar">K</div>
                        <div>
                            <b style="color:#F8FAFC !important;">Khadija D.</b><br>
                            <small style="color:rgba(148,163,184,.9) !important;">Étudiante en médecine</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with _right:
        st.markdown(f"""
        <div style="padding: 1rem 0 1.4rem;">
            <h2 style="font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.03em;
                font-size:1.7rem; margin-bottom:.35rem;">{T("login_title")}</h2>
            <p style="opacity:.7; font-size:.92rem;">{T("login_sub")}</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form", border=False):
            username = st.text_input(T("username"), placeholder="Votre pseudo", key="login_user")
            password = st.text_input(T("password"), type="password", placeholder="••••••••", key="login_pass")
            _remember = st.checkbox("Se souvenir de moi", value=True, key="login_remember")
            _submit = st.form_submit_button(f"{T('continue')}", use_container_width=True, type="primary")
            if _submit:
                ok, role_ = authenticate(username, password)
                if ok:
                    uname = username.strip().lower()
                    st.session_state.update(user=uname, role=role_, token=create_session(uname), page="analyse")
                    _load_appearance(uname)
                    sync_notif_cursor(uname)
                    set_cookie(COOKIE_NAME, st.session_state.token, max_age=(30*24*3600 if _remember else 7*24*3600))
                    set_cookie("ys_user", uname, max_age=30*24*3600)
                    st.rerun()
                elif role_ == "suspended":
                    st.error("⛔ Compte suspendu. Contactez le support.")
                else:
                    st.error("❌ Identifiants incorrects.")
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        _a1, _a2 = st.columns(2)
        with _a1:
            if st.button(T("register"), use_container_width=True, key="login_to_register"):
                st.session_state.page = "register"; st.rerun()
        with _a2:
            if st.button("← " + T("home"), use_container_width=True, key="login_to_home"):
                st.session_state.page = "accueil"; st.rerun()
        st.markdown(f"""
        <div style="margin-top:1.2rem; text-align:center; opacity:.7; font-size:.82rem;">
            Pas encore de compte ? <b>Créez-en un</b> — c'est gratuit.
        </div>
        """, unsafe_allow_html=True)
        _theme_label = "🌙 Mode sombre" if st.session_state.theme == "light" else "☀️ Mode clair"
        if st.button(_theme_label, use_container_width=True, key="login_theme_toggle"):
            _toggle_theme()
    render_footer(compact=True)

def render_register_page():
    render_navbar()
    _cl,_cm,_cr = st.columns([1,1.4,1])
    with _cm:
        st.markdown(f"""<div style="text-align:center; margin-top:2.5rem;">{logo_html(64)}
<div class="g-h1" style="font-size:2.2rem;">{T("reg_title")}</div>
<p class="g-lead" style="margin:0 auto;">{T("reg_sub")}</p><div class="g-rule" style="margin:1.4rem auto;"></div></div>""", unsafe_allow_html=True)
        render_register_wizard()
        if st.button(T("login"), use_container_width=True): st.session_state.page="login"; st.rerun()
    render_footer(compact=True)