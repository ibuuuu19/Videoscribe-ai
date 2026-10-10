"""
Page Premium — Formules tarifaires et gestion des achats.

Contient :
- render_premium() : Affichage des 4 formules + tunnel de paiement

Extrait de app.py pour alléger le fichier principal (~138 lignes).

Usage:
    from src.pages.premium import render_premium
"""

import streamlit as st
import streamlit.components.v1 as _components

from src.ui.i18n import T
from src.ui.components import ic
from src.ui.layout import render_footer, render_navbar, sync_notif_cursor
from src.core.config import PLANS, PAYMENT_WAVE, PAYMENT_OM, CINETPAY_APIKEY, CINETPAY_SITE_ID
from src.user_manager import get_plan, set_plan
from src.ui.storage import get_referral_code
from src.payment import create_payment, check_payment
from src.revenue_manager import record_revenue
from src.notification_manager import notify


# ═══════════════════════════════════════════════════════════════
# ⚠️ La fonction render_premium a été copiée automatiquement
#    depuis app.py par le script extract_premium.py
# ═══════════════════════════════════════════════════════════════

def render_premium():
    # On n'affiche la navbar QUE si l'utilisateur n'est PAS connecté
    if st.session_state.get("user") is None:
        render_navbar()
        
    # ═══ Sécurisation : variables globales non définies en mode public ═══
    _prem_user = st.session_state.get("user")
    
    # ═══ Sécurisation : variables globales non définies en mode public ═══
    _prem_user = st.session_state.get("user")
    _prem_role = st.session_state.get("role", "client")
    _prem_is_guest = _prem_user is None
    
    if _prem_role == "admin":
        cur = "premium_plus"
    elif _prem_is_guest:
        cur = "free"
    else:
        cur = get_plan(_prem_user)
    
    cur_label = T("plan_free") if cur == "free" else PLANS[cur]["name"]
    st.markdown(f"""<div style="text-align:center; margin:2.2rem 0 .4rem;">
<div class="g-kicker" style="justify-content:center; display:flex; align-items:center; gap:8px;">{ic("spark",12)} {T("prem_kicker")}</div>
<h1 style="margin:.5rem 0 .3rem;">{T("prem_title")}</h1>
<p style="opacity:.7; max-width:52ch; margin:0 auto;">{T("prem_subtitle")}</p>
</div>""", unsafe_allow_html=True)
    t1, t2, t3 = st.columns([2,2,2])
    with t2: billing = st.radio("billing", [T("monthly"),T("annual")], horizontal=True, label_visibility="collapsed")
    is_annual = billing == T("annual")
    st.markdown(f'<p style="text-align:center; opacity:.65; margin-top:-8px;">{ic("trending-down",13)} {T("save_annual")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center; opacity:.8;">{T("status")} : <b>{cur_label}</b></p>', unsafe_allow_html=True)
    st.markdown(f"""<div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:.8rem 0 1.6rem;">
<span class="pill-trust">{ic("lock",13)} {T("trust_secure")}</span>
<span class="pill-trust">{ic("x",13)} {T("trust_cancel")}</span>
<span class="pill-trust">{ic("zap",13)} {T("trust_fast")}</span>
</div>""", unsafe_allow_html=True)
    if st.session_state.get("buy_plan"):
        key = st.session_state.buy_plan
        billing_sel = st.session_state.get("buy_billing", T("monthly"))
        _components.html('<script>window.parent.scrollTo({top:0,behavior:"smooth"});</script>', height=0)
        if key == "free":
            st.info(f"{T('free')} ✓")
            if st.button(T("close"), use_container_width=True):
                st.session_state.buy_plan = None; st.rerun()
        else:
            info = PLANS[key]; price = info["annual"] if billing_sel==T("annual") else info["monthly"]; days = 365 if billing_sel==T("annual") else 30
            _prem_display_name = _prem_user if _prem_user else "visiteur"
            st.markdown(f"""
<div class="pay-panel">
<div class="pay-title">{ic("card",20)} {T("subscription")} — {info['name']}</div>
<div class="pay-price">${price:g} <span>/ {days} jours</span></div>
<ol class="pay-steps">
<li>Envoyez <b>${price:g}</b> par <b>Wave</b> (<code>{PAYMENT_WAVE}</code>) ou <b>Orange Money</b> (<code>{PAYMENT_OM}</code>)</li>
<li>Indiquez votre pseudo <b>{_prem_display_name}</b> + la formule <b>{info['name']}</b></li>
<li>Activation sous 24 h ({days} jours)</li>
</ol>
</div>""", unsafe_allow_html=True)
            if _prem_is_guest:
                st.info(T("login_sub"))
            elif CINETPAY_APIKEY and CINETPAY_SITE_ID:
                if st.session_state.get("pay_url"):
                    st.link_button("Ouvrir la page de paiement", st.session_state.pay_url, use_container_width=True)
                    if st.button(T("verify"), use_container_width=True):
                        with st.spinner("..."): status = check_payment(st.session_state.pay_tx, CINETPAY_APIKEY, CINETPAY_SITE_ID)
                        if status == "ACCEPTED":
                            set_plan(_prem_user, key, days); record_revenue(_prem_user, key, price, days, "cinetpay")
                            notify(_prem_user, "card", f"Paiement de **${price:g}** confirmé — formule {info['name']} activée ({days} j).")
                            sync_notif_cursor(_prem_user)
                            st.session_state.pay_url = None; st.session_state.buy_plan = None; st.balloons(); st.rerun()
                        else: st.info(f"Paiement non confirmé ({status}).")
                else:
                    if st.button(f"Générer le paiement de ${price:g}", use_container_width=True):
                        with st.spinner("..."):
                            try:
                                tx, url = create_payment(_prem_user, price, CINETPAY_APIKEY, CINETPAY_SITE_ID)
                                st.session_state.pay_tx, st.session_state.pay_url = tx, url; st.rerun()
                            except Exception as e: st.error(f"{e}")
            bb1, bb2 = st.columns([3,1])
            with bb2:
                if st.button(T("close"), use_container_width=True):
                    st.session_state.buy_plan = None; st.session_state.pay_url = None; st.rerun()
        st.markdown("---")
    plans_ui = [
    {"key":"free","icon":"spark","name":T("plan_free"),"tag":T("tag_free"),"monthly":0,"annual":0,"cta":T("get_free"),"hl":False,"plus":None,
     "accent":"#64748B","accent2":"#94A3B8",
     "features":[T("ff1"),T("ff2"),T("ff3"),T("ff4"),T("ff5")],"new_features":[T("ff6"),T("ff7")]},
    {"key":"basique","icon":"zap","name":T("plan_basic"),"tag":T("tag_basic"),"monthly":1.99,"annual":19,"cta":T("get_bas"),"hl":False,"plus":T("plan_free"),"plus_key":"plus_free",
     "accent":"#2E6DB4","accent2":"#4C9AFF",
     "features":[T("fb1"),T("fb2"),T("fb3"),T("fb4"),T("fb5"),T("fb6")],"new_features":[T("fb7"),T("fb8"),T("fb9")]},
    {"key":"premium","icon":"star","name":T("plan_premium"),"tag":T("tag_premium"),"monthly":4.99,"annual":49,"cta":T("get_prem"),"hl":True,"plus":T("plan_basic"),"plus_key":"plus_basic",
     "accent":"#D4AF37","accent2":"#F0D488",
     "features":[T("fp1"),T("fp2"),T("fp3"),T("fp4"),T("fp5"),T("fp6")],"new_features":[T("fp7"),T("fp8"),T("fp9"),T("fp10"),T("fp11")]},
    {"key":"premium_plus","icon":"crown","name":T("plan_plus"),"tag":T("tag_plus"),"monthly":9.99,"annual":99,"cta":T("get_plus"),"hl":False,"plus":T("plan_premium"),"plus_key":"plus_premium",
     "accent":"#8B5CF6","accent2":"#C4B5FD",
     "features":[T("fx1"),T("fx2"),T("fx3"),T("fx4"),T("fx5"),T("fx6"),T("fx7"),T("fx8")],"new_features":[T("fx9"),T("fx10"),T("fx11"),T("fx12"),T("fx13")]},
    ]
    cols = st.columns(4, gap="medium")
    for col, p in zip(cols, plans_ui):
        with col:
            price = p["annual"] if is_annual else p["monthly"]
            sub = T("billed_annually") if is_annual else T("per_month")
            card_cls = "pcard pcard-hl" if p["hl"] else "pcard"
            ribbon = f'<div class="pc-ribbon">{ic("star",12)} {T("popular")}</div>' if p["hl"] else ""
            price_html = f'<span class="cur">$</span>{price:g}' if price > 0 else "0"
            st.markdown(f"""<div class="{card_cls}">{ribbon}<div class="pc-icon-wrap" style="--pc-accent:{p['accent']};--pc-accent2:{p['accent2']};">{ic(p["icon"], 24)}</div><p class="pc-name">{p["name"]}</p><p class="pc-tag">{p["tag"]}</p><p class="pc-price">{price_html}</p><p class="pc-sub">{sub}</p></div>""", unsafe_allow_html=True)
            if st.button(p["cta"], key=f"cta_{p['key']}", use_container_width=True, type="primary" if p["hl"] else "secondary"): st.session_state.buy_plan = p["key"]; st.session_state.buy_billing = billing; st.rerun()
            st.markdown('<div class="pc-sep"></div>', unsafe_allow_html=True)
            head = (f'<p class="pc-plus">{T(p["plus_key"])}</p>' if p.get("plus_key") else f'<p class="pc-plus">{T("included")}</p>')
            feats = "".join(f'<p class="pfeat" style="--pc-accent:{p["accent"]}">{ic("check", 14)}<span>{f}</span></p>' for f in p["features"])
            new_feats = ""
            if p.get("new_features"):
                new_feats = f'<p class="pfeat-group-label">{ic("spark",11)} {T("new_label")}</p>' + "".join(f'<p class="pfeat is-new" style="--pc-accent:{p["accent"]}">{ic("check", 14)}<span>{f}<span class="new-tag">{T("new_label")}</span></span></p>' for f in p["new_features"])
            st.markdown(head + feats + new_feats, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('trophy', 22)} {T('growth_title')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div class="newfeat">{ic("users", 18)} <span><b>{T("referral_title")}</b> · Tous</span></div>
<div class="newfeat">{ic("folder", 18)} <span><b>{T("fb4")}</b> · Basique+</span></div>
<div class="newfeat">{ic("zap", 18)} <span><b>{T("fx2")}</b> · Premium+</span></div>""", unsafe_allow_html=True)
    st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('gem', 22)} {T('comfort_title')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div class="newfeat">{ic("award", 18)} <span><b>{T("fp4")}</b> · Premium</span></div>
<div class="newfeat">{ic("play", 18)} <span><b>{T("fx3")}</b> · Premium+</span></div>
<div class="newfeat">{ic("volume", 18)} <span><b>{T("fx4")}</b> · Premium+</span></div>
<div class="newfeat">{ic("card", 18)} <span><b>{T("fp5")}</b> · Premium</span></div>
<div class="newfeat">{ic("link", 18)} <span><b>{T("fb5")}</b> · Basique+</span></div>
<div class="newfeat">{ic("image", 18)} <span><b>{T("fx8")}</b> · Premium+</span></div>""", unsafe_allow_html=True)
    st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('trending-up', 22)} {T('prem_kicker')}</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div class="newfeat">{ic("trending-up", 18)} <span><b>{T("fp7")}</b> · Premium</span></div>
<div class="newfeat">{ic("target", 18)} <span><b>{T("fp9")}</b> · Premium</span></div>
<div class="newfeat">{ic("calendar", 18)} <span><b>{T("fx10")}</b> · Premium+</span></div>
<div class="newfeat">{ic("compass", 18)} <span><b>{T("fx12")}</b> · Premium+</span></div>""", unsafe_allow_html=True)
    if not _prem_is_guest:
        st.markdown("---")
        st.markdown(f"<h3 style='display:flex;align-items:center;'>{ic('users', 22)} {T('referral_title')}</h3>", unsafe_allow_html=True)
        code = get_referral_code(_prem_user)
        st.markdown(f"<div class='newfeat'>{ic('key', 18)} <span>{T('referral_share')} <b>{code}</b> {T('referral_each')}</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    render_footer(compact=True)