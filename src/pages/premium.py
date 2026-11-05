"""
Page Premium — Formules tarifaires et gestion des achats.
"""

import streamlit as st
import streamlit.components.v1 as _components
import uuid
import requests

from src.ui.i18n import T
from src.ui.components import ic
from src.ui.layout import render_footer, render_navbar, sync_notif_cursor
from src.ui.css import shade
from src.core.config import PLANS, PAYMENT_WAVE, PAYMENT_OM, CINETPAY_APIKEY, CINETPAY_SITE_ID
from src.user_manager import get_plan, set_plan
from src.ui.storage import get_referral_code
from src.payment import create_payment, check_payment
from src.revenue_manager import record_revenue
from src.notification_manager import notify


# ═══════════════════════════════════════════════════════════════
# FONCTION DE PAIEMENT BICTORYS (Checkout)
# ═══════════════════════════════════════════════════════════════

def create_bictorys_checkout(amount, currency="XOF", country="SN", email="client@example.com"):
    """
    Crée une session de paiement Bictorys (mode Checkout).
    Retourne un dict avec 'checkout_url' ou 'error'.
    """
    api_key = st.secrets.get("BICTORYS_PUBLIC_KEY")
    if not api_key:
        return {"error": "Clé API Bictorys non configurée dans les secrets."}

    url = "https://api.test.bictorys.com/pay/v1/charges"  # Mode test

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    merchant_ref = str(uuid.uuid4())

    payload = {
        "amount": int(amount),
        "currency": currency,
        "country": country,
        "merchantReference": merchant_ref,
        "successRedirectUrl": "https://videoscribe-ia.streamlit.app/?page=premium&status=success",
        "errorRedirectUrl": "https://videoscribe-ia.streamlit.app/?page=premium&status=error",
        "customer": {
            "name": "Client VideoScribe",
            "email": email
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data", {}).get("link"):
            return {"checkout_url": data["data"]["link"], "merchant_ref": merchant_ref}
        if data.get("link"):
            return {"checkout_url": data["link"], "merchant_ref": merchant_ref}
        return {"data": data, "merchant_ref": merchant_ref}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
    
def verify_bictorys_payment(charge_id):
    """
    Vérifie le statut d'un paiement Bictorys via l'API.
    Retourne le statut ("success", "pending", "error") ou un dict d'erreur.
    """
    api_key = st.secrets.get("BICTORYS_PUBLIC_KEY")
    if not api_key:
        return {"error": "Clé API Bictorys non configurée."}

    url = f"https://api.test.bictorys.com/pay/v1/charges/{charge_id}"
    headers = {"X-Api-Key": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        status = data.get("status") or data.get("data", {}).get("status")
        return {"status": status, "raw": data}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════
# STYLE : couleur du thème + feuille d'abonnement mobile (façon X)
# ═══════════════════════════════════════════════════════════════

_FEAT_ICONS = ["zap", "file", "hash", "bulb", "download", "lang", "msg", "image",
               "award", "target", "calendar", "compass", "trending-up"]

_PM = {
    "fr": {"title": "Un seul abonnement.<br>Accédez à tout.", "adv": "Avantages de {p}", "mo": "par mois", "yr": "par an",
           "permo": "{x} $/mois", "save": "−{n} %", "renew": "Se renouvelle automatiquement. Annulez à tout moment.",
           "fine": "Prix en dollars US, hors taxes ou frais applicables. Pour éviter des frais supplémentaires, annulez au moins 24 h avant le renouvellement.",
           "current": "Votre formule actuelle", "flex": "Sans engagement", "free_note": "Gratuit, sans carte bancaire.", "new": "Nouveau"},
    "en": {"title": "One subscription.<br>Access everything.", "adv": "{p} benefits", "mo": "per month", "yr": "per year",
           "permo": "${x}/month", "save": "−{n}%", "renew": "Renews automatically. Cancel anytime.",
           "fine": "Prices in US dollars, excluding applicable taxes or fees. To avoid extra charges, cancel at least 24 hours before renewal.",
           "current": "Your current plan", "flex": "No commitment", "free_note": "Free, no credit card needed.", "new": "New"},
    "es": {"title": "Una sola suscripción.<br>Accede a todo.", "adv": "Ventajas de {p}", "mo": "al mes", "yr": "al año",
           "permo": "{x} $/mes", "save": "−{n} %", "renew": "Se renueva automáticamente. Cancela cuando quieras.",
           "fine": "Precios en dólares estadounidenses, sin impuestos ni tasas aplicables. Para evitar cargos adicionales, cancela al menos 24 h antes de la renovación.",
           "current": "Tu plan actual", "flex": "Sin compromiso", "free_note": "Gratis, sin tarjeta bancaria.", "new": "Nuevo"},
    "de": {"title": "Ein Abo.<br>Zugriff auf alles.", "adv": "Vorteile von {p}", "mo": "pro Monat", "yr": "pro Jahr",
           "permo": "{x} $/Monat", "save": "−{n} %", "renew": "Verlängert sich automatisch. Jederzeit kündbar.",
           "fine": "Preise in US-Dollar, zzgl. anfallender Steuern oder Gebühren. Zur Vermeidung zusätzlicher Kosten mindestens 24 Std. vor der Verlängerung kündigen.",
           "current": "Ihr aktueller Tarif", "flex": "Jederzeit kündbar", "free_note": "Kostenlos, ohne Kreditkarte.", "new": "Neu"},
}


def _theme_accent():
    """Couleur choisie par l'utilisateur (get_accent() renvoie le bleu fixe sur les pages « publiques », dont Premium)."""
    if st.session_state.get("user") is not None:
        a = st.session_state.get("cfg_accent", "#2E6DB4")
        return a, shade(a, 0.55)
    return "#2E6DB4", "#1B3B6F"


def _mix(hex_a, hex_b, t):
    """Mélange deux couleurs #RRGGBB (t = part de hex_b)."""
    try:
        a = [int(hex_a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
        b = [int(hex_b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
        return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))
    except Exception:
        return hex_a


def _skin_css(acc, acc_dark):
    """Applique la couleur d'accent choisie à toute la page Premium (bureau + mobile)."""
    dark = st.session_state.get("theme", "light") == "dark"
    ink, soft = ("#F8FAFC", "#AAB8D0") if dark else ("#0F1A2E", "#5B6B88")
    surf = "#11161F" if dark else "#FFFFFF"
    surf2 = "rgba(255,255,255,.07)" if dark else "#EEF2F8"
    line = "rgba(255,255,255,.12)" if dark else "rgba(15,26,46,.12)"
    page = "#05080F" if dark else "#F3F7FD"
    sel = "rgba(255,255,255,.17)" if dark else "#FFFFFF"
    logged = st.session_state.get("user") is not None and st.session_state.get("role") != "visiteur"
    bottom = "calc(92px + env(safe-area-inset-bottom))" if logged else "calc(10px + env(safe-area-inset-bottom))"
    tint = f"color-mix(in srgb, {acc} 16%, transparent)"
    V = 'html body .stApp div[data-testid="stVerticalBlock"]'
    css = f"""
html body .stApp .pcard-hl {{ border-color:{acc} !important; box-shadow:0 20px 56px color-mix(in srgb,{acc} 28%,transparent) !important; }}
html body .stApp [data-testid="stColumn"]:has(.pcard-hl) {{ border-color:{acc} !important; box-shadow:0 22px 60px color-mix(in srgb,{acc} 26%,transparent) !important; }}
{V}.st-key-pm_desk_grid .stButton > button[kind="secondary"], {V}.st-key-pm_desk_grid .stButton > button[data-testid="stBaseButton-secondary"] {{
  background:{tint} !important; color:{acc} !important; border:1px solid color-mix(in srgb,{acc} 40%,transparent) !important; box-shadow:none !important; font-weight:800 !important; }}
{V}.st-key-pm_desk_grid .stButton > button[kind="secondary"]:hover, {V}.st-key-pm_desk_grid .stButton > button[data-testid="stBaseButton-secondary"]:hover {{
  background:{acc} !important; color:#fff !important; }}
html body .stApp .g-kicker {{ color:{acc} !important; }}
html body .stApp .pcard-hl {{ background:linear-gradient(180deg,color-mix(in srgb,{acc} 9%,transparent),transparent 60%) !important; }}
html body .stApp .pcard:hover {{ border-color:color-mix(in srgb,{acc} 55%,transparent) !important; }}
html body .stApp .pc-ribbon {{ background:linear-gradient(135deg,{acc},{acc_dark}) !important; color:#fff !important; }}
html body .stApp .pc-price .cur {{ color:{acc} !important; }}
html body .stApp .new-tag {{ background:{tint} !important; color:{acc} !important; }}
html body .stApp .pill-trust svg, html body .stApp .pfeat svg {{ color:{acc} !important; stroke:{acc} !important; }}
html body .stApp .pay-panel {{ border-color:color-mix(in srgb,{acc} 45%,transparent) !important; }}
html body .stApp .pay-price {{ color:{acc} !important; }}
html body .stApp [data-testid="stMainBlockContainer"] .stButton > button[kind="primary"], html body .stApp [data-testid="stMainBlockContainer"] .stButton > button[data-testid="stBaseButton-primary"] {{
  background:linear-gradient(135deg,{acc},{acc_dark}) !important; border:0 !important; color:#fff !important; }}

/* ── feuille mobile ── */
.stApp .st-key-pm_mob {{ display:none; }}
@media (max-width:768px) {{
  {V}.st-key-pm_desk_top, {V}.st-key-pm_desk_grid {{ display:none !important; }}
  {V}.st-key-pm_mob {{ display:flex !important; flex-direction:column; gap:1rem !important; padding-bottom:400px; }}
  .pm-title {{ text-align:center; font-family:'Sora',sans-serif; font-weight:800; font-size:1.7rem; line-height:1.18; letter-spacing:-.03em; color:{ink} !important; margin:.4rem 0 0; }}
  .pm-cur {{ text-align:center; margin:-.2rem auto 0; display:inline-flex; align-items:center; gap:6px; font-size:.78rem; font-weight:700; color:{acc} !important;
     padding:4px 12px; border-radius:999px; background:{tint}; }}
  .stApp .st-key-pm_plan, .stApp .st-key-pm_plan [data-testid="stRadio"] {{ width:100% !important; }}
  html body .stApp .st-key-pm_plan [role="radiogroup"] > * {{ flex:1 1 0 !important; min-width:0 !important; display:flex !important; }}
  html body .stApp .st-key-pm_plan [data-testid="stRadioOption"] {{ width:100% !important; flex:1 1 auto !important; }}
  .stApp .st-key-pm_plan [role="radiogroup"] {{ width:100% !important; box-sizing:border-box; display:flex !important; flex-wrap:nowrap !important; gap:2px !important; padding:4px; border-radius:999px; background:{surf2}; border:1px solid {line}; }}
  .stApp .st-key-pm_plan [data-testid="stRadioOption"] {{ flex:1 1 0 !important; min-width:0; justify-content:center !important; margin:0 !important; padding:.62rem .1rem !important; border-radius:999px; cursor:pointer;
     transition:background .25s ease, box-shadow .25s ease; }}
  html body .stApp .st-key-pm_plan [data-testid="stRadioOption"] > div > div:first-child {{ display:none !important; }}
  html body .stApp .st-key-pm_plan [data-testid="stRadioOption"] > div {{ display:flex; justify-content:center; width:100%; }}
  .stApp .st-key-pm_plan [data-testid="stRadioOption"] p {{ font-size:.76rem !important; font-weight:700 !important; color:{soft} !important; text-align:center; white-space:nowrap; margin:0 !important; }}
  .stApp .st-key-pm_plan [data-testid="stRadioOption"]:has(input:checked) {{ background:{sel}; box-shadow:0 3px 12px rgba(8,20,45,.16); }}
  .stApp .st-key-pm_plan [data-testid="stRadioOption"]:has(input:checked) p {{ color:{ink} !important; font-weight:800 !important; }}
  .pm-panel {{ border-radius:26px; padding:1.1rem 1.15rem .6rem; background:{surf}; border:1px solid {line}; box-shadow:0 14px 40px rgba(8,20,45,.08); }}
  .pm-adv {{ color:{soft} !important; font-size:.86rem; font-weight:600; padding-bottom:.7rem; margin-bottom:.4rem; border-bottom:1px solid {line}; }}
  .pm-adv b {{ color:{ink} !important; }}
  .pm-f {{ display:flex; align-items:flex-start; gap:.85rem; padding:.62rem 0; color:{ink} !important; font-size:.92rem; font-weight:600; line-height:1.35; }}
  .pm-f svg {{ flex:none; width:20px; height:20px; margin-top:1px; color:{acc}; stroke:{acc}; }}
  .pm-f .pm-new {{ margin-left:6px; font-size:.6rem; font-weight:800; text-transform:uppercase; letter-spacing:.05em; padding:2px 7px; border-radius:999px; background:{tint}; color:{acc} !important; white-space:nowrap; }}
  /* barre d'achat fixe */
  {V}.st-key-pm_buy {{ position:fixed !important; left:0; right:0; bottom:{bottom}; z-index:999980; padding:.9rem 14px .7rem; gap:.65rem !important;
     background:linear-gradient(180deg,transparent 0,{page} 22px); backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); }}
  {V}.st-key-pm_buy [data-testid="stHorizontalBlock"] {{ flex-direction:row !important; flex-wrap:nowrap !important; gap:.6rem !important; margin-bottom:.2rem; }}
  {V}.st-key-pm_buy [data-testid="stColumn"] {{ min-width:0 !important; width:auto !important; flex:1 1 0 !important; }}
  {V}.st-key-pm_pc_m, {V}.st-key-pm_pc_a {{ position:relative; gap:0 !important; }}
  .stApp .st-key-pm_pc_m [data-testid="stElementContainer"]:has(.stButton), .stApp .st-key-pm_pc_a [data-testid="stElementContainer"]:has(.stButton) {{ position:absolute !important; inset:0; z-index:3; margin:0 !important; }}
  .stApp .st-key-pm_pc_m .stButton, .stApp .st-key-pm_pc_a .stButton {{ height:100%; }}
  html body .stApp .st-key-pm_pc_m .stButton button, html body .stApp .st-key-pm_pc_a .stButton button,
  html body .stApp .st-key-pm_pc_m .stButton button:hover, html body .stApp .st-key-pm_pc_a .stButton button:hover,
  html body .stApp .st-key-pm_pc_m .stButton button:focus, html body .stApp .st-key-pm_pc_a .stButton button:focus,
  html body .stApp .st-key-pm_pc_m .stButton button:active, html body .stApp .st-key-pm_pc_a .stButton button:active {{
     width:100% !important; height:100% !important; min-height:0 !important; opacity:0 !important; cursor:pointer; background:transparent !important; background-image:none !important;
     border:0 !important; box-shadow:none !important; outline:0 !important; transform:none !important; filter:none !important; }}
  html body .stApp .st-key-pm_pc_m .stButton button::before, html body .stApp .st-key-pm_pc_a .stButton button::before,
  html body .stApp .st-key-pm_pc_m .stButton button::after, html body .stApp .st-key-pm_pc_a .stButton button::after {{ display:none !important; content:none !important; }}
  html body .stApp .st-key-pm_pc_m [data-testid="stElementContainer"], html body .stApp .st-key-pm_pc_a [data-testid="stElementContainer"] {{ background:transparent !important; }}
  /* balayage : le panneau glisse depuis le côté du geste */
  @keyframes pmSlide {{ from {{ opacity:0; transform:translateX(var(--pm-d,34px)); }} to {{ opacity:1; transform:none; }} }}
  .pm-panel.pm-a0, .pm-panel.pm-a1 {{ animation:pmSlide .38s cubic-bezier(.22,.9,.3,1) both; }}
  .pm-panel.pm-a1 {{ animation-name:pmSlide2; }}
  @keyframes pmSlide2 {{ from {{ opacity:0; transform:translateX(var(--pm-d,34px)); }} to {{ opacity:1; transform:none; }} }}
  .st-key-pm_mob {{ touch-action:pan-y; overflow-x:clip; }}
  .pm-dots {{ display:flex; justify-content:center; gap:6px; margin:.7rem 0 .2rem; }}
  .pm-dots i {{ width:6px; height:6px; border-radius:99px; background:{line}; transition:width .3s ease, background .3s ease; }}
  .pm-dots i.on {{ width:20px; background:linear-gradient(90deg,{acc},{acc_dark}); }}
  @media (prefers-reduced-motion:reduce) {{ .pm-panel.pm-a0, .pm-panel.pm-a1 {{ animation:none; }} }}
  .pm-pc {{ position:relative; box-sizing:border-box; min-height:78px; border-radius:20px; padding:.8rem .95rem; background:{surf2}; border:1.5px solid {line};
     transition:border-color .25s ease, background .25s ease, box-shadow .25s ease; }}
  .pm-pc b {{ display:block; color:{ink} !important; font-size:1.18rem; font-weight:800; letter-spacing:-.02em; }}
  .pm-pc b span {{ font-size:.78rem; font-weight:600; color:{soft} !important; margin-left:3px; }}
  .pm-pc small {{ display:block; margin-top:3px; color:{soft} !important; font-size:.74rem; font-weight:600; line-height:1.3; }}
  .pm-pc.sel {{ border-color:{acc}; background:linear-gradient(135deg,color-mix(in srgb,{acc} 20%,transparent),color-mix(in srgb,{acc} 7%,transparent)); box-shadow:0 0 0 3px color-mix(in srgb,{acc} 20%,transparent); }}
  .pm-pc.sel small:first-of-type {{ color:{acc} !important; }}
  .pm-save {{ position:absolute; top:-9px; right:12px; padding:2px 9px; border-radius:999px; font-size:.66rem; font-weight:800; color:#fff !important; background:linear-gradient(135deg,{acc},{acc_dark}); }}
  {V}.st-key-pm_buy .stButton > button[kind="primary"], {V}.st-key-pm_buy .stButton > button[data-testid="stBaseButton-primary"] {{
     min-height:56px !important; border-radius:999px !important; border:0 !important; font-size:1.02rem !important; font-weight:800 !important;
     background:linear-gradient(135deg,{acc},{acc_dark}) !important; color:#fff !important; box-shadow:0 14px 30px color-mix(in srgb,{acc} 38%,transparent) !important; }}
  {V}.st-key-pm_buy .stButton > button:disabled {{ opacity:.6 !important; }}
  .pm-note {{ font-family:inherit; text-align:center; color:{soft} !important; font-size:.74rem; font-weight:600; margin:0; }}
  .pm-fine {{ text-align:center; color:{soft} !important; font-size:.66rem; line-height:1.45; margin:0; opacity:.85; }}
}}
"""
    st.markdown("<style>" + css.replace("\n", " ") + "</style>", unsafe_allow_html=True)


_SWIPE_JS = """<script>(function(){try{
var P=window.parent,d=P.document;
if(P.__pmSwipe){return;} P.__pmSwipe=true;
var x0=0,y0=0,t0=0,on=false;
function inZone(t){return t&&t.closest&&t.closest('.st-key-pm_mob')&&!t.closest('.st-key-pm_buy');}
d.addEventListener('touchstart',function(e){var t=e.target;if(!inZone(t)){on=false;return;}var p=e.touches[0];x0=p.clientX;y0=p.clientY;t0=Date.now();on=true;},{passive:true});
d.addEventListener('touchend',function(e){if(!on)return;on=false;var p=e.changedTouches[0],dx=p.clientX-x0,dy=p.clientY-y0;
 if(Math.abs(dx)<48||Math.abs(dx)<Math.abs(dy)*1.4||Date.now()-t0>700)return;
 var opts=d.querySelectorAll('.st-key-pm_plan [data-testid="stRadioOption"]');if(!opts.length)return;
 var cur=-1;opts.forEach(function(o,i){if(o.querySelector('input:checked'))cur=i;});
 var nx=cur+(dx<0?1:-1);if(nx<0||nx>=opts.length)return;opts[nx].click();},{passive:true});
}catch(e){}})();</script>"""


def _render_mobile_sheet(plans_ui, cur, is_guest, acc, acc_dark):
    """Feuille d'abonnement mobile : onglets de formule, avantages, cartes mensuel/annuel fixes, gros bouton d'achat."""
    lang = st.session_state.get("cfg_lang", "fr")
    X = _PM.get(lang, _PM["en"])
    by_key = {p["key"]: p for p in plans_ui}
    with st.container(key="pm_mob"):
        st.markdown(f'<div class="pm-title">{X["title"]}</div>', unsafe_allow_html=True)
        key = st.radio("plan", [p["key"] for p in plans_ui], index=2, horizontal=True, key="pm_plan",
                       format_func=lambda k: by_key[k]["name"], label_visibility="collapsed")
        p = by_key[key]
        feats = [(f, False) for f in p["features"]] + [(f, True) for f in p.get("new_features", [])]
        rows = "".join(
            f'<div class="pm-f">{ic(_FEAT_ICONS[i % len(_FEAT_ICONS)], 20)}<span>{_html_esc(f)}'
            f'{(" <span class=pm-new>" + X["new"] + "</span>") if new else ""}</span></div>'
            for i, (f, new) in enumerate(feats))
        keys = [pp["key"] for pp in plans_ui]
        idx = keys.index(key)
        last = st.session_state.get("_pm_last")
        if last is not None and last != idx:
            st.session_state["_pm_n"] = st.session_state.get("_pm_n", 0) + 1
        d = 34 if (last is None or idx >= last) else -34
        st.session_state["_pm_last"] = idx
        anim = f'pm-a{st.session_state.get("_pm_n", 0) % 2}' if (last is not None and last != idx) else ""
        dots = "".join(f'<i class="{"on" if i == idx else ""}"></i>' for i in range(len(keys)))
        st.markdown(f'<div class="pm-panel {anim}" style="--pm-d:{d}px"><div class="pm-adv"><b>{X["adv"].format(p=_html_esc(p["name"]))}</b></div>{rows}</div><div class="pm-dots">{dots}</div>'.replace("\n", ""),
                    unsafe_allow_html=True)
        _components.html(_SWIPE_JS.replace("%N%", str(len(keys))), height=0)

        # ── barre d'achat fixe ──
        with st.container(key="pm_buy"):
            bill = st.session_state.get("pm_bill", "annual")
            if key != "free":
                m, a = p["monthly"], p["annual"]
                pct = max(round((1 - a / (12 * m)) * 100), 0) if m else 0
                c1, c2 = st.columns(2)
                with c1:
                    with st.container(key="pm_pc_m"):
                        st.markdown(f'<div class="pm-pc {"sel" if bill == "monthly" else ""}"><b>${m:g}<span>{X["mo"]}</span></b>'
                                    f'<small>{X["flex"]}</small></div>', unsafe_allow_html=True)
                        st.button(" ", key="pm_pick_m", on_click=lambda: st.session_state.update(pm_bill="monthly"))
                with c2:
                    with st.container(key="pm_pc_a"):
                        st.markdown(f'<div class="pm-pc {"sel" if bill == "annual" else ""}">'
                                    + (f'<span class="pm-save">{X["save"].format(n=pct)}</span>' if pct else "")
                                    + f'<b>${a:g}<span>{X["yr"]}</span></b><small>{X["permo"].format(x=f"{a / 12:.2f}".rstrip("0").rstrip("."))}</small></div>',
                                    unsafe_allow_html=True)
                        st.button(" ", key="pm_pick_a", on_click=lambda: st.session_state.update(pm_bill="annual"))
            is_cur = (cur == key and key != "free")
            label = ("✓ " + X["current"]) if is_cur else p["cta"]
            if st.button(label, key="pm_cta", type="primary", use_container_width=True, disabled=is_cur):
                st.session_state.buy_plan = key
                st.session_state.buy_billing = T("annual") if (bill == "annual" and key != "free") else T("monthly")
                st.rerun()
            if key == "free":
                st.markdown(f'<div class="pm-note">{X["free_note"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="pm-note">{X["renew"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="pm-fine">{X["fine"]}</div>', unsafe_allow_html=True)


def _html_esc(x):
    import html as _h
    return _h.escape(str(x))


# ═══════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════

def render_premium():
    # On n'affiche la navbar QUE si l'utilisateur n'est PAS connecté
    if st.session_state.get("user") is None:
        render_navbar()
        
    _prem_user = st.session_state.get("user")
    _prem_role = st.session_state.get("role", "client")
    _prem_is_guest = _prem_user is None
    
    # ✅ GESTION DU RETOUR DE PAIEMENT (UNE SEULE FOIS, AVEC ACTIVATION AUTO)
    if "payment_processed" not in st.session_state:
        st.session_state.payment_processed = False

    status = st.query_params.get("status")
    if status == "success" and not st.session_state.payment_processed:
        st.session_state.payment_processed = True
        
        # Récupération des infos stockées avant la redirection
        charge_ref = st.session_state.get("pending_charge_ref")
        plan_key = st.session_state.get("pending_plan_key")
        plan_days = st.session_state.get("pending_plan_days", 30)
        
        if charge_ref and plan_key and not _prem_is_guest:
            with st.spinner("Vérification du paiement..."):
                result = verify_bictorys_payment(charge_ref)
                
                if result.get("status") == "success":
                    set_plan(_prem_user, plan_key, plan_days)
                    price_paid = PLANS[plan_key]["annual"] if plan_days == 365 else PLANS[plan_key]["monthly"]
                    record_revenue(_prem_user, plan_key, price_paid, plan_days, "bictorys_auto")
                    notify(_prem_user, "card", f"Paiement de **${price_paid:g}** confirmé — formule {PLANS[plan_key]['name']} activée ({plan_days} j).")
                    sync_notif_cursor(_prem_user)
                    st.success(f"✅ Paiement confirmé ! Votre formule {PLANS[plan_key]['name']} est activée.")
                    st.balloons()
                elif result.get("status") == "pending":
                    st.warning("⏳ Paiement en attente. Utilisez le formulaire ci-dessous si nécessaire.")
                else:
                    st.error(f"❌ Le paiement n'a pas été confirmé (statut : {result.get('status')}).")
        else:
            st.success("✅ Paiement validé ! Si votre compte n'est pas activé, utilisez le formulaire de vérification ci-dessous.")
            st.balloons()
        
        st.query_params.clear()
        for k in ["pending_charge_ref", "pending_plan_key", "pending_plan_days"]:
            st.session_state.pop(k, None)
            
    elif status == "error" and not st.session_state.payment_processed:
        st.session_state.payment_processed = True
        st.error("❌ Le paiement a échoué ou a été annulé. Veuillez réessayer.")
        st.query_params.clear()
    
    if _prem_role == "admin":
        cur = "premium_plus"
    elif _prem_is_guest:
        cur = "free"
    else:
        cur = get_plan(_prem_user)
    
    _A, _AD = _theme_accent(); _A2 = _mix(_A, "#FFFFFF", .35)
    _skin_css(_A, _AD)
    with st.container(key="pm_desk_top"):
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
    
    # ═══════════════════════════════════════════════════════════════
    # TUNNEL DE PAIEMENT
    # ═══════════════════════════════════════════════════════════════
    if st.session_state.get("buy_plan"):
        key = st.session_state.buy_plan
        billing_sel = st.session_state.get("buy_billing", T("monthly"))
        _components.html('<script>window.parent.scrollTo({top:0,behavior:"smooth"});</script>', height=0)
        
        if key == "free":
            st.info(f"{T('free')} ✓")
            if st.button(T("close"), use_container_width=True):
                st.session_state.buy_plan = None; st.rerun()
        else:
            info = PLANS[key]
            price = info["annual"] if billing_sel == T("annual") else info["monthly"]
            days = 365 if billing_sel == T("annual") else 30
            _prem_display_name = _prem_user if _prem_user else "visiteur"
            
            st.markdown(f"""
<div class="pay-panel">
<div class="pay-title">{ic("card",20)} {T("subscription")} — {info['name']}</div>
<div class="pay-price">${price:g} <span>/ {days} jours</span></div>
</div>""", unsafe_allow_html=True)
            
            if _prem_is_guest:
                st.info(T("login_sub"))
            else:
                # ═══ MÉTHODE 1 : BICTORYS (Principal) ═══
                st.markdown(f"<h4 style='display:flex;align-items:center;gap:8px;'>{ic('credit-card',18)} Payer par Mobile Money (Bictorys)</h4>", unsafe_allow_html=True)
                st.caption("Wave, Orange Money, ou Carte Bancaire via Bictorys.")
                
                if st.button(f"Payer ${price:g} avec Bictorys", key="pay_bictorys", use_container_width=True, type="primary"):
                    with st.spinner("Redirection vers Bictorys..."):
                        amount_xof = int(price * 500)
                        email = st.session_state.get("prof_email", "client@example.com")
                        
                        result = create_bictorys_checkout(
                            amount=amount_xof, 
                            currency="XOF", 
                            country="SN",
                            email=email
                        )
                        
                        if "error" in result:
                            st.error(f"Erreur Bictorys : {result['error']}")
                        elif "checkout_url" in result:
                            # ✅ Stockage des infos AVANT redirection
                            st.session_state.pending_charge_ref = result.get("merchant_ref")
                            st.session_state.pending_plan_key = key
                            st.session_state.pending_plan_days = days
                            st.session_state.pay_url = result["checkout_url"]
                            
                            st.markdown(f'<meta http-equiv="refresh" content="0; url={result["checkout_url"]}">', unsafe_allow_html=True)
                        else:
                            st.warning("Réponse inattendue de Bictorys.")
                            st.json(result)
                
                st.markdown("---")
                st.markdown(f"<h4 style='display:flex;align-items:center;gap:8px;'>{ic('phone',18)} Payer manuellement (Fallback)</h4>", unsafe_allow_html=True)
                
                with st.expander("Voir les instructions de paiement manuel"):
                    st.markdown(f"""
Envoyez **${price:g}** par :
- **Wave** : <code>{PAYMENT_WAVE}</code>
- **Orange Money** : <code>{PAYMENT_OM}</code>

Puis indiquez votre pseudo **{_prem_display_name}** + formule **{info['name']}**.

Activation sous 24h ({days} jours).
""", unsafe_allow_html=True)
                    
                st.markdown("---")
                st.markdown(f"<h4 style='display:flex;align-items:center;gap:8px;'>{ic('check-circle',18)} Déjà payé ? Vérifier mon compte</h4>", unsafe_allow_html=True)
                st.caption("Si vous avez payé mais que votre compte n'est pas encore activé, entrez votre référence de transaction Bictorys ci-dessous.")
                
                with st.form("verify_payment_form"):
                    charge_id = st.text_input("Référence de transaction (charge ID)")
                    plan_choice = st.selectbox("Quel plan avez-vous payé ?", ["basique", "premium", "premium_plus"])
                    submitted = st.form_submit_button("Vérifier le paiement", use_container_width=True)
                    
                    if submitted and charge_id:
                        with st.spinner("Vérification en cours..."):
                            result = verify_bictorys_payment(charge_id.strip())
                            
                            if "error" in result:
                                st.error(f"Erreur : {result['error']}")
                            elif result.get("status") == "success":
                                set_plan(_prem_user, plan_choice, days)
                                record_revenue(_prem_user, plan_choice, PLANS[plan_choice]["monthly"], days, "bictorys_manual")
                                notify(_prem_user, "card", f"Paiement confirmé — formule {PLANS[plan_choice]['name']} activée.")
                                st.success("✅ Paiement confirmé ! Votre compte est activé.")
                                st.balloons()
                                st.rerun()
                            elif result.get("status") == "pending":
                                st.warning("⏳ Paiement en attente. Réessayez dans quelques minutes.")
                            else:
                                st.info(f"Statut : {result.get('status')}")
                
                if CINETPAY_APIKEY and CINETPAY_SITE_ID:
                    if st.session_state.get("pay_url") and "bictorys" not in st.session_state.pay_url:
                        st.link_button("Ouvrir la page de paiement CinetPay", st.session_state.pay_url, use_container_width=True)
                        if st.button(T("verify"), use_container_width=True):
                            with st.spinner("..."): status = check_payment(st.session_state.pay_tx, CINETPAY_APIKEY, CINETPAY_SITE_ID)
                            if status == "ACCEPTED":
                                set_plan(_prem_user, key, days); record_revenue(_prem_user, key, price, days, "cinetpay")
                                notify(_prem_user, "card", f"Paiement de **${price:g}** confirmé — formule {info['name']} activée ({days} j).")
                                sync_notif_cursor(_prem_user)
                                st.session_state.pay_url = None; st.session_state.buy_plan = None; st.balloons(); st.rerun()
                            else: st.info(f"Paiement non confirmé ({status}).")
                    else:
                        if st.button(f"Générer le paiement CinetPay de ${price:g}", use_container_width=True):
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
    
    # ═══════════════════════════════════════════════════════════════
    # GRILLE DES PLANS
    # ═══════════════════════════════════════════════════════════════
    plans_ui = [
    {"key":"free","icon":"spark","name":T("plan_free"),"tag":T("tag_free"),"monthly":0,"annual":0,"cta":T("get_free"),"hl":False,"plus":None,
     "accent":_A,"accent2":_A2,
     "features":[T("ff1"),T("ff2"),T("ff3"),T("ff4"),T("ff5")],"new_features":[T("ff6"),T("ff7")]},
    {"key":"basique","icon":"zap","name":T("plan_basic"),"tag":T("tag_basic"),"monthly":1.99,"annual":19,"cta":T("get_bas"),"hl":False,"plus":T("plan_free"),"plus_key":"plus_free",
     "accent":_A,"accent2":_A2,
     "features":[T("fb1"),T("fb2"),T("fb3"),T("fb4"),T("fb5"),T("fb6")],"new_features":[T("fb7"),T("fb8"),T("fb9")]},
    {"key":"premium","icon":"star","name":T("plan_premium"),"tag":T("tag_premium"),"monthly":4.99,"annual":49,"cta":T("get_prem"),"hl":True,"plus":T("plan_basic"),"plus_key":"plus_basic",
     "accent":_A,"accent2":_A2,
     "features":[T("fp1"),T("fp2"),T("fp3"),T("fp4"),T("fp5"),T("fp6")],"new_features":[T("fp7"),T("fp8"),T("fp9"),T("fp10"),T("fp11")]},
    {"key":"premium_plus","icon":"crown","name":T("plan_plus"),"tag":T("tag_plus"),"monthly":9.99,"annual":99,"cta":T("get_plus"),"hl":False,"plus":T("plan_premium"),"plus_key":"plus_premium",
     "accent":_A,"accent2":_A2,
     "features":[T("fx1"),T("fx2"),T("fx3"),T("fx4"),T("fx5"),T("fx6"),T("fx7"),T("fx8")],"new_features":[T("fx9"),T("fx10"),T("fx11"),T("fx12"),T("fx13")]},
    ]
    with st.container(key="pm_desk_grid"):
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

    if not st.session_state.get("buy_plan"):  # pendant le paiement, seul le tunnel s'affiche sur mobile
        _render_mobile_sheet(plans_ui, cur, _prem_is_guest, _A, _AD)
    
    # ═══════════════════════════════════════════════════════════════
    # SECTIONS SUPPLÉMENTAIRES
    # ═══════════════════════════════════════════════════════════════
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