"""
Balayage pour ouvrir / fermer le menu latéral (tiroir) sur mobile — avec suivi du doigt, voile qui s'assombrit,
et validation au 1/3 de la largeur ou sur un geste rapide.

    from src.ui.swipe_nav import render_swipe_nav
    render_swipe_nav()          # dans app.py, juste après render_mobile_shell(...)

• Ouvrir  : glisser vers la DROITE depuis la bande gauche de l'écran (28 % de la largeur ; la bande 0-24 px reste libre
            pour le « retour » système d'iOS/Android).
• Fermer  : glisser vers la GAUCHE n'importe où sur le tiroir ou sur le voile.
• Ignoré  : champs, curseurs, zones défilantes horizontalement, onglets Premium (qui ont leur propre balayage), ≥ 769 px.
"""
import streamlit as st
import streamlit.components.v1 as _components

_JS = r"""<script>(function(){try{
var P=window.parent,d=P.document;
if(P.__vsSwipeNav){return;} P.__vsSwipeNav=true;

var st=null, scrim=null;
function sb(){return d.querySelector('section[data-testid="stSidebar"]');}
function isMobile(){return P.innerWidth<=768;}
function isOpen(){var s=sb();return !!s && s.getAttribute('data-collapsed')==='false';}
function sbW(){var s=sb(),w=s?s.getBoundingClientRect().width:0;return w>50?w:Math.min(P.innerWidth*0.86,330);}
function openBtn(){return d.querySelector('[data-testid="stExpandSidebarButton"]')||d.querySelector('[data-testid="stSidebarCollapsedControl"] button')||d.querySelector('.st-key-mt_menu button');}
function closeBtn(){return d.querySelector('[data-testid="stSidebarCollapseButton"] button')||d.querySelector('[data-testid="stSidebarCollapseButton"]');}
function mkScrim(){
  if(scrim&&scrim.isConnected)return scrim;
  scrim=d.createElement('div');scrim.id='vs-sw-scrim';
  scrim.style.cssText='position:fixed;inset:0;z-index:999980;background:rgba(2,6,16,.58);opacity:0;pointer-events:none;transition:none;-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)';
  d.body.appendChild(scrim);return scrim;
}
function fadeScrim(p,anim){var s=mkScrim();s.style.transition=anim?'opacity .28s ease':'none';s.style.opacity=String(Math.max(0,Math.min(1,p)));}
function blocked(t){
  if(!t||!t.closest)return true;
  if(t.closest('input,textarea,select,[role="slider"],[data-testid="stSlider"],[data-baseweb="select"],iframe,.st-key-pm_mob,.st-key-pm_buy'))return true;
  var e=t;while(e&&e!==d.body){var cs=P.getComputedStyle(e);
    if((cs.overflowX==='auto'||cs.overflowX==='scroll')&&e.scrollWidth>e.clientWidth+4&&!e.matches('[data-testid="stSidebar"],[data-testid="stSidebarContent"]'))return true;
    e=e.parentElement;}
  return false;
}
// On ne touche JAMAIS au style inline du tiroir (géré par React/Streamlit) : on pilote une classe + des variables CSS sur <html>.
var root=d.documentElement;
if(!d.getElementById('vs-sw-css')){var cs=d.createElement('style');cs.id='vs-sw-css';
  cs.textContent='html.vs-sw section[data-testid="stSidebar"]{width:var(--vs-w)!important;min-width:var(--vs-w)!important;transform:translateX(var(--vs-x))!important;transition:var(--vs-t,none)!important;will-change:transform}';
  d.head.appendChild(cs);}
function setX(x,anim){root.style.setProperty('--vs-w',sbW()+'px');root.style.setProperty('--vs-x',x+'px');
  root.style.setProperty('--vs-t',anim?'transform .28s cubic-bezier(.22,.9,.3,1)':'none');root.classList.add('vs-sw');}
function clearInline(){root.classList.remove('vs-sw');['--vs-w','--vs-x','--vs-t'].forEach(function(k){root.style.removeProperty(k);});}
P.addEventListener('pagehide',clearInline);

d.addEventListener('touchstart',function(e){
  st=null;if(!isMobile()||e.touches.length!==1)return;var s=sb();if(!s)return;
  var p=e.touches[0],open=isOpen();
  if(!open){ if(p.clientX>P.innerWidth*0.28||blocked(e.target))return; st={mode:'open'}; }
  else { st={mode:'close'}; }
  st.x=p.clientX;st.y=p.clientY;st.t=Date.now();st.lock=false;st.w=sbW();st.dx=0;
},{passive:true});

d.addEventListener('touchmove',function(e){
  if(!st)return;var p=e.touches[0],dx=p.clientX-st.x,dy=p.clientY-st.y;
  if(!st.lock){
    if(Math.abs(dx)<10&&Math.abs(dy)<10)return;
    if(Math.abs(dx)<Math.abs(dy)*1.5||(st.mode==='open'&&dx<0)||(st.mode==='close'&&dx>0)){st=null;return;}
    st.lock=true;
  }
  if(e.cancelable)e.preventDefault();
  st.dx=dx;
  if(st.mode==='open'){var x=Math.min(0,-st.w+Math.max(0,dx));setX(x,false);fadeScrim((st.w+x)/st.w,false);}
  else{var x2=Math.max(-st.w,Math.min(0,dx));setX(x2,false);fadeScrim(1+x2/st.w,false);}
},{passive:false});

d.addEventListener('touchend',function(e){
  if(!st||!st.lock){st=null;return;}
  var dt=Math.max(1,Date.now()-st.t),v=Math.abs(st.dx)/dt,go=Math.abs(st.dx)>st.w*0.33||v>0.55,mode=st.mode;st=null;
  if(mode==='open'){
    if(go){setX(0,true);fadeScrim(1,true);var b=openBtn();if(b)b.click();
      setTimeout(function(){clearInline();fadeScrim(0,true);},340);}
    else{setX(-sbW(),true);fadeScrim(0,true);setTimeout(clearInline,320);}
  }else{
    if(go){setX(-sbW(),true);fadeScrim(0,true);var c=closeBtn();if(c)c.click();setTimeout(clearInline,340);}
    else{setX(0,true);fadeScrim(1,true);setTimeout(function(){clearInline();fadeScrim(0,true);},320);}
  }
},{passive:true});
d.addEventListener('touchcancel',function(){if(st&&st.lock){clearInline();fadeScrim(0,true);}st=null;},{passive:true});
}catch(e){}})();</script>"""


def render_swipe_nav() -> None:
    _components.html(_JS, height=0)