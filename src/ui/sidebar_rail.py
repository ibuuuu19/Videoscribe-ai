"""
Barre latérale repliable en « rail d'icônes » (comme NotebookLM).

Quand l'utilisateur replie le menu, au lieu de le faire disparaître, on garde une colonne étroite
(76 px) avec le logo, les icônes de navigation (info-bulle au survol), l'avatar, et le bouton pour déplier.
CSS pur + un petit script qui copie le libellé de chaque bouton dans son attribut `title`.
S'applique uniquement sur grand écran (≥ 900 px) ; le mobile garde ses barres haut/bas.
"""
import streamlit as st
import streamlit.components.v1 as components

_S = 'html body .stApp section[data-testid="stSidebar"][data-collapsed="true"]'


def inject(accent: str = "#2E6DB4", ink: str = "#0F1A2E") -> None:
    css = f"""<style>
@media (min-width: 900px) {{
{_S} {{ width:76px !important; min-width:76px !important; max-width:76px !important; transform:none !important; margin-left:0 !important; visibility:visible !important; }}
{_S} > div, {_S} [data-testid="stSidebarContent"] {{ width:76px !important; overflow-x:hidden !important; }}
{_S} [data-testid="stSidebarHeader"] {{ padding:.7rem 0 .3rem !important; justify-content:center !important; display:flex !important; }}
{_S} [data-testid="stSidebarHeader"] > *:not([data-testid="stSidebarCollapseButton"]) {{ display:none !important; }}
{_S} [data-testid="stSidebarCollapseButton"] {{ margin:0 auto !important; display:flex !important; justify-content:center; }}
{_S} [data-testid="stSidebarCollapseButton"] svg {{ transform:rotate(180deg); }}
{_S} [data-testid="stSidebarUserContent"] {{ padding:0 !important; }}
{_S} .qbrand {{ justify-content:center !important; padding:.2rem 0 .5rem !important; }}
{_S} .qbrand > span:first-child {{ flex:none !important; margin:0 auto !important; }}
{_S} .qbrand > span:not(:first-child) {{ display:none !important; }}
{_S} .qcap {{ height:1px !important; margin:.5rem .7rem !important; padding:0 !important; font-size:0 !important; background:rgba(120,140,170,.25); overflow:hidden; }}
{_S} .stButton > button {{ width:48px !important; min-width:48px !important; height:48px !important; min-height:48px !important; padding:0 !important; margin:0 auto !important;
   display:flex !important; align-items:center !important; justify-content:center !important; border-radius:15px !important; }}
{_S} .stButton {{ display:flex; justify-content:center; }}
{_S} .stButton > button p {{ font-size:0 !important; margin:0 !important; display:flex !important; align-items:center; justify-content:center; line-height:0 !important; }}
{_S} .stButton > button p .vs-ic {{ font-size:16px !important; margin:0 !important; display:inline-flex !important; }}
{_S} .stButton > button p .vs-ic svg {{ width:22px !important; height:22px !important; }}
{_S} .stButton > button:hover {{ transform:scale(1.06); }}
/* ── icônes premium : tuiles en verre, actif = dégradé + halo ── */
{_S} .stButton > button {{ position:relative; background:linear-gradient(145deg,color-mix(in srgb,currentColor 9%,transparent),color-mix(in srgb,currentColor 3%,transparent)) !important;
   border:1px solid color-mix(in srgb,currentColor 12%,transparent) !important; box-shadow:inset 0 1px 0 rgba(255,255,255,.18),0 4px 12px rgba(15,26,46,.07) !important;
   transition:transform .28s cubic-bezier(.34,1.56,.64,1),background .25s ease,box-shadow .25s ease,border-color .25s ease !important; }}
{_S} .stButton > button:hover {{ transform:translateY(-2px) scale(1.05) !important; border-color:{accent}88 !important;
   background:linear-gradient(145deg,{accent}2e,{accent}0d) !important; box-shadow:inset 0 1px 0 rgba(255,255,255,.25),0 10px 22px {accent}38 !important; }}
{_S} .stButton > button:hover .vs-ic, {_S} .stButton > button:hover svg {{ color:{accent} !important; }}
{_S} .stButton > button[kind="primary"], {_S} .stButton > button[data-testid="stBaseButton-primary"] {{
   background:linear-gradient(145deg,{accent},color-mix(in srgb,{accent} 55%,#0F1A2E)) !important; border-color:transparent !important; color:#fff !important;
   box-shadow:inset 0 1px 0 rgba(255,255,255,.35),0 10px 24px {accent}66,0 0 0 3px {accent}22 !important; }}
{_S} .stButton > button[kind="primary"] .vs-ic, {_S} .stButton > button[kind="primary"] svg,
{_S} .stButton > button[data-testid="stBaseButton-primary"] .vs-ic, {_S} .stButton > button[data-testid="stBaseButton-primary"] svg {{ color:#fff !important; }}
{_S} .stButton > button[kind="primary"]::before, {_S} .stButton > button[data-testid="stBaseButton-primary"]::before {{
   content:""; position:absolute; left:-9px; top:25%; bottom:25%; width:4px; border-radius:0 4px 4px 0; background:{accent}; box-shadow:0 0 12px {accent}; }}
{_S} .stButton {{ margin:.18rem 0 !important; }}
{_S} .user-card {{ padding:.35rem 0 !important; background:transparent !important; border:0 !important; box-shadow:none !important; display:flex; justify-content:center; }}
{_S} .user-card .user-row {{ justify-content:center !important; }}
{_S} .user-card .uname, {_S} .user-card .chev {{ display:none !important; }}
{_S} [data-testid="stPopover"] button {{ width:48px !important; }}
/* bouton natif « déplier » : épinglé en haut du rail */
html body .stApp [data-testid="stExpandSidebarButton"], html body .stApp [data-testid="stSidebarCollapsedControl"] {{ position:fixed !important; left:16px !important; top:12px !important; z-index:1000002 !important; display:flex !important; }}
html body .stApp:has(section[data-testid="stSidebar"][data-collapsed="true"]) header[data-testid="stHeader"] {{ z-index:1000003 !important; }}
html body .stApp [data-testid="stExpandSidebarButton"] {{ width:44px !important; height:44px !important; border-radius:14px !important; left:16px !important; top:10px !important; }}
{_S} [data-testid="stSidebarContent"] {{ padding-top:3.6rem !important; }}
}}
</style>"""
    st.markdown(css, unsafe_allow_html=True)
    components.html("""<script>
(function(){var d=window.parent.document,t=null;
function tag(){try{d.querySelectorAll('[data-testid="stSidebar"] .stButton button').forEach(function(b){
 var p=b.querySelector('p');if(!p)return;var x=(p.textContent||'').trim();if(x&&b.title!==x)b.title=x;});}catch(e){}}
new MutationObserver(function(){clearTimeout(t);t=setTimeout(tag,250);}).observe(d.body,{childList:true,subtree:true});tag();})();
</script>""", height=0)