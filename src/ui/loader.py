"""Écran de chargement premium affiché pendant les latences (connexion, changement de page, déconnexion…).

Sans lui, l'ancienne page reste affichée (parfois à moitié grisée) pendant que le serveur travaille, ce qui donne
l'impression que l'application est figée. Ici, un voile plein écran avec un anneau animé aux couleurs du thème
apparaît dès qu'une navigation dépasse ~0,5 s, et disparaît quand la nouvelle page est prête.

Fonctionnement : un petit script injecté dans la page parente écoute les clics sur les boutons de navigation / de
connexion (barre latérale, barres mobiles, formulaires, menu avatar). Si le serveur est toujours « en cours
d'exécution » 0,45 s plus tard, le voile s'affiche ; il se retire dès que l'exécution est terminée.
Les analyses vidéo (bouton « Analyser ») gardent leur propre barre de progression : elles ne sont pas concernées.

Utilisation (une fois par exécution, juste après apply_tighten()) :
    from src.ui.loader import render_loader
    render_loader()
"""
import json
import streamlit as st
import streamlit.components.v1 as _components

_LBL = {
    "fr": ("Chargement", "Un instant, on prépare votre espace"),
    "en": ("Loading", "One moment, preparing your workspace"),
    "es": ("Cargando", "Un momento, preparamos tu espacio"),
    "de": ("Wird geladen", "Einen Moment, Ihr Bereich wird vorbereitet"),
}

# Boutons déclenchant une « navigation » (pas les boutons d'analyse)
_SEL = ", ".join([
    '[data-testid="stSidebar"] button',
    '.st-key-mnav button', '.st-key-mtop button', '.st-key-vsnav button',
    '[data-testid="stPopoverBody"] button',
    '[data-testid="stFormSubmitButton"] button',
    'button[data-testid="stBaseButton-primaryFormSubmit"]',
    'button[data-testid="stBaseButton-secondaryFormSubmit"]',
])

_JS = r"""
(function(){
  var P = window.parent, d = P.document;
  var cfg = %CFG%;
  P.__vsLdCfg = cfg;
  function css(){
    var c = P.__vsLdCfg, s = d.getElementById('vs-ld-css');
    if(!s){ s = d.createElement('style'); s.id = 'vs-ld-css'; d.head.appendChild(s); }
    s.textContent = [
    '#vs-ld{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;flex-direction:column;opacity:0;visibility:hidden;pointer-events:none;',
    'transition:opacity .35s ease,visibility 0s linear .35s;background:'+c.bg+';backdrop-filter:blur(18px) saturate(140%);-webkit-backdrop-filter:blur(18px) saturate(140%);font-family:Sora,Manrope,system-ui,sans-serif;}',
    '#vs-ld.on{opacity:1;visibility:visible;pointer-events:all;transition:opacity .3s ease;}',
    '#vs-ld .g{position:absolute;width:520px;height:520px;max-width:90vw;border-radius:50%;background:radial-gradient(circle,'+c.acc+'33,transparent 65%);animation:vsLdGlow 3.2s ease-in-out infinite;}',
    '#vs-ld .r{position:relative;width:112px;height:112px;display:flex;align-items:center;justify-content:center;}',
    '#vs-ld .r i{position:absolute;inset:0;border-radius:50%;background:conic-gradient(from 0deg,transparent 0 55%,'+c.acc+' 100%);',
    '-webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 4px),#000 calc(100% - 3px));mask:radial-gradient(farthest-side,transparent calc(100% - 4px),#000 calc(100% - 3px));animation:vsLdSpin 1.15s linear infinite;}',
    '#vs-ld .r i + i{inset:11px;background:conic-gradient(from 180deg,transparent 0 60%,'+c.acc2+' 100%);animation-duration:1.7s;animation-direction:reverse;opacity:.85;}',
    '#vs-ld .m{position:relative;width:58px;height:58px;border-radius:19px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,'+c.acc2+','+c.acc+');',
    'box-shadow:0 14px 38px '+c.acc+'66,inset 0 1px 0 rgba(255,255,255,.4);animation:vsLdPulse 1.8s ease-in-out infinite;}',
    '#vs-ld .t{position:relative;margin-top:30px;font-weight:800;font-size:1.25rem;letter-spacing:-.02em;color:'+c.ink+';}',
    '#vs-ld .t b{background:linear-gradient(92deg,#60A5FA,#34D399 55%,#FBBF24);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}',
    '#vs-ld .s{position:relative;margin-top:10px;font-size:.86rem;font-weight:600;color:'+c.soft+';text-align:center;padding:0 24px;}',
    '#vs-ld .s span{display:inline-block;min-width:1.2em;text-align:left;}',
    '#vs-ld .s span::after{content:"";animation:vsLdDots 1.4s steps(4,end) infinite;}',
    '#vs-ld .bar{position:absolute;left:0;right:0;top:0;height:3px;overflow:hidden;background:'+c.acc+'1f;}',
    '#vs-ld .bar i{position:absolute;top:0;bottom:0;width:38%;border-radius:3px;background:linear-gradient(90deg,transparent,'+c.acc+','+c.acc2+',transparent);animation:vsLdBar 1.3s cubic-bezier(.5,0,.2,1) infinite;}',
    '@keyframes vsLdSpin{to{transform:rotate(360deg)}}',
    '@keyframes vsLdPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}',
    '@keyframes vsLdGlow{0%,100%{opacity:.55;transform:scale(.94)}50%{opacity:1;transform:scale(1.06)}}',
    '@keyframes vsLdBar{0%{left:-40%}100%{left:102%}}',
    '@keyframes vsLdDots{0%{content:""}25%{content:"."}50%{content:".."}75%,100%{content:"..."}}',
    '@media (prefers-reduced-motion:reduce){#vs-ld .r i,#vs-ld .g,#vs-ld .m,#vs-ld .bar i{animation-duration:4s}}'
    ].join('');
  }
  function build(){
    var c = P.__vsLdCfg, el = d.getElementById('vs-ld');
    if(!el){
      el = d.createElement('div'); el.id = 'vs-ld'; el.setAttribute('role','status'); el.setAttribute('aria-live','polite');
      el.innerHTML = '<div class="bar"><i></i></div><div class="g"></div><div class="r"><i></i><i></i>'
        + '<div class="m"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        + '<rect x="3" y="4" width="18" height="16" rx="3.5"/><path d="M10.5 9.2v5.6l4.6-2.8z" fill="#fff"/></svg></div></div>'
        + '<div class="t">VideoScribe <b>AI</b></div><div class="s"><em style="font-style:normal"></em><span></span></div>';
      d.body.appendChild(el);
    }
    el.querySelector('.s em').textContent = c.sub;
    el.setAttribute('aria-label', c.label);
  }
  css(); build();
  if(P.__vsLdInit) return;           // écouteurs posés une seule fois
  P.__vsLdInit = true;
  var SEL = %SEL%;
  var on = false, shownAt = 0, armedUntil = 0, runStart = 0, loop = null, poll = null;
  function el(){ return d.getElementById('vs-ld'); }
  function running(){ return !!d.querySelector('[data-testid="stStatusWidget"]'); }
  function show(){ if(on) return; on = true; shownAt = Date.now(); build(); el().classList.add('on'); var idle = 0;
    poll = setInterval(function(){ idle = running() ? 0 : idle + 1; var age = Date.now() - shownAt;
      if((idle >= 3 && age > 500) || age > 90000) hide(); }, 150); }
  function hide(){ on = false; runStart = 0; clearInterval(poll); poll = null; var e = el(); if(e) e.classList.remove('on'); }
  function tick(){ var now = Date.now();
    if(now > armedUntil && !on){ clearInterval(loop); loop = null; runStart = 0; return; }
    if(running()){ if(!runStart) runStart = now; if(!on && now - runStart > 450) show(); } else { runStart = 0; } }
  function arm(){ armedUntil = Date.now() + 4000; if(!loop) loop = setInterval(tick, 100); }
  d.addEventListener('click', function(e){ var t = e.target; var b = t && t.closest ? t.closest(SEL) : null;
    if(b && !b.disabled) arm(); }, true);
  d.addEventListener('keydown', function(e){ if(e.key === 'Enter' && e.target && e.target.closest && e.target.closest('[data-testid="stForm"]')) arm(); }, true);
  P.addEventListener('pageshow', hide);
})();
"""


def render_loader() -> None:
    """Injecte l'écran de chargement (une fois par exécution)."""
    dark = st.session_state.get("theme", "light") == "dark"
    acc = st.session_state.get("cfg_accent", "#2E6DB4") if st.session_state.get("user") is not None else "#2E6DB4"
    try:
        from src.ui.css import shade
        acc2 = shade(acc, -0.25) if False else _lighten(acc)
    except Exception:
        acc2 = acc
    lbl, sub = _LBL.get(st.session_state.get("cfg_lang", "fr"), _LBL["fr"])
    cfg = {"acc": acc, "acc2": acc2, "label": lbl, "sub": sub,
           "bg": "rgba(5,8,15,.90)" if dark else "rgba(243,247,253,.92)",
           "ink": "#F8FAFC" if dark else "#0F1A2E", "soft": "#AAB8D0" if dark else "#5B6B88"}
    js = _JS.replace("%CFG%", json.dumps(cfg)).replace("%SEL%", json.dumps(_SEL))
    _components.html(f"<script>{js}</script>", height=0)


def _lighten(hex_color: str, t: float = .38) -> str:
    try:
        h = hex_color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return "#" + "".join(f"{round(c + (255 - c) * t):02X}" for c in (r, g, b))
    except Exception:
        return hex_color