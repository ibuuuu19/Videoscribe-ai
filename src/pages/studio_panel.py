"""
Panneau « Studio Premium » — réglages rapides de sortie, au style des tuiles de NotebookLM.

· En-tête (icône dégradée, titre, pastille de formule, bouton de repli en icône)
· Moteur IA : deux tuiles (Rapide / Qualité) + tuile Mode turbo
· Fonctions Premium+ : tuiles à bascule colorées (verrouillées avec badge selon la formule) + langue de sortie en pastilles
· Quantités : curseurs dans une carte
· Sortie : tuiles à bascule

Tous les réglages restent les mêmes clés de session qu'avant (cfg_model, cfg_turbo, cfg_target, cfg_kw, cfg_qa,
cfg_translate, cfg_kw_n, cfg_q_n, cfg_chunk, studio_tldr, studio_questions, studio_actions, studio_chat).
Les tuiles utilisent des callbacks : un seul rerun par clic.
"""
from urllib.parse import quote

import streamlit as st

from src.ui.i18n import T, LANGS
from src.ui.mobile import theme_tokens

_I = {
    "sparkles": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
    "zap": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "cpu": '<rect x="5" y="5" width="14" height="14" rx="3.5"/><rect x="9" y="9" width="6" height="6" rx="1.2"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    "doc": '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h7M9 17h7"/>',
    "help": '<circle cx="12" cy="12" r="9.5"/><path d="M9.5 9.6a2.6 2.6 0 015.1.6c0 1.8-2.6 2.1-2.6 3.8M12 17.4v.01"/>',
    "tasks": '<path d="M4 6l2 2 3.2-3.6M4 14l2 2 3.2-3.6M13 7h7M13 15h7"/>',
    "chat": '<path d="M21 12a8 8 0 01-11.6 7.1L4 21l1.9-5.1A8 8 0 1121 12z"/>',
    "hash": '<path d="M5 9h14M5 15h14M10 3L8 21M16 3l-2 18"/>',
    "lang": '<path d="M3 5h10M8 3v2M5 5c1 4 4 7 8 8M11 5c-1 4-4 7-8 8"/><path d="M13 21l4.5-10L22 21M14.8 17.5h5.4"/>',
    "slides": '<rect x="3" y="4" width="18" height="13" rx="2.5"/><path d="M8 21h8M12 17v4"/>',
    "panel": '<rect x="3" y="4" width="18" height="16" rx="3.8"/><path d="M15 4v16"/>',
    "panel_open": '<rect x="3" y="4" width="18" height="16" rx="3.8"/><path d="M9 4v16"/>',
    "gauge": '<path d="M4 16a8 8 0 1116 0"/><path d="M12 16l4-5"/>',
}


def _mask(name: str, sw: float = 1.9) -> str:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="{sw}" '
           f'stroke-linecap="round" stroke-linejoin="round">{_I[name]}</svg>')
    return f'url("data:image/svg+xml,{quote(svg)}")'


# clé du bouton → (icône, couleur)
_TILES = {
    "sp_m_fast": ("zap", "#F59E0B"), "sp_m_deep": ("cpu", "#8B5CF6"), "sp_turbo": ("gauge", "#F59E0B"),
    "sp_tldr": ("doc", "#06B6D4"), "sp_adv": ("help", "#EC4899"), "sp_act": ("tasks", "#10B981"), "sp_chat": ("chat", "#3B82F6"),
    "spl_tldr": ("doc", "#06B6D4"), "spl_act": ("tasks", "#10B981"), "spl_slides": ("slides", "#EC4899"), "spl_chat": ("chat", "#3B82F6"),
    "spl_deep": ("cpu", "#8B5CF6"),
    "sp_o_kw": ("hash", "#F97316"), "sp_o_qa": ("help", "#EC4899"), "sp_o_tr": ("lang", "#3B82F6"),
}
_P = 'html body .stApp div[data-testid="stVerticalBlock"]'


def _css(tier: int = 3) -> None:
    t = theme_tokens()
    light = st.session_state.get("theme", "light") == "light"
    tile = "#F4F7FC" if light else "rgba(255,255,255,.055)"
    tile_h = "#EAF1FB" if light else "rgba(255,255,255,.09)"
    panel = "#FFFFFF" if light else "rgba(255,255,255,.035)"
    acc = t["acc"]
    r = []
    for key, (icon, col) in _TILES.items():
        r.append(f'html body .stApp .st-key-{key} button::before{{content:"";position:absolute;left:14px;top:14px;width:24px;height:24px;'
                 f'background:{col};-webkit-mask:{_mask(icon)} center/contain no-repeat;mask:{_mask(icon)} center/contain no-repeat;}}')
    for key, (icon, col) in _TILES.items():
        k2 = "sr_" + key.split("_", 1)[1]
        r.append(f'html body .stApp .st-key-{k2} button::before{{background:{col};-webkit-mask:{_mask(icon)} center/contain no-repeat;mask:{_mask(icon)} center/contain no-repeat;}}')
    r.append(f'html body .stApp .st-key-sr_toggle button::before{{background:{t["soft"]};-webkit-mask:{_mask("panel_open")} center/contain no-repeat;mask:{_mask("panel_open")} center/contain no-repeat;}}')
    r.append(f'html body .stApp .st-key-sr_toggle button:hover::before{{background:{acc};}}')
    lk = (["sr_tldr", "sr_act", "sr_slides", "sr_chat"] if tier < 3 else []) + (["sr_deep"] if tier < 2 else [])
    for k in lk:
        r.append(f'html body .stApp .st-key-{k} button{{opacity:.5;}}html body .stApp .st-key-{k} button::before{{filter:grayscale(.9);}}')
    css = f"""<style>
{chr(10).join(r)}
{_P}.st-key-sp_panel {{ background:{panel} !important; border:1px solid {t["line"]} !important; border-radius:26px !important; padding:1.05rem 1.05rem 1.2rem !important;
  gap:.2rem !important; box-shadow:{t["shadow"]} !important; }}
html body .stApp .sp-head {{ display:flex; align-items:center; gap:13px; padding-bottom:1rem; }}
html body .stApp .sp-logo {{ width:46px; height:46px; border-radius:15px; display:flex; align-items:center; justify-content:center; flex:none; color:#fff;
  background:linear-gradient(135deg,{acc},{t["acc_dark"]}); box-shadow:0 10px 24px color-mix(in srgb,{acc} 40%,transparent); }}
html body .stApp .sp-t {{ font-family:'Sora',sans-serif; font-weight:800; font-size:1.12rem; letter-spacing:-.02em; color:{t["ink"]} !important; display:flex; align-items:center; gap:9px; flex-wrap:wrap; line-height:1.2; }}
html body .stApp .sp-s {{ font-size:.8rem; color:{t["soft"]} !important; margin-top:.15rem; }}
html body .stApp .sp-plan {{ font-size:.62rem; font-weight:800; letter-spacing:.07em; text-transform:uppercase; padding:.18rem .55rem; border-radius:999px;
  background:linear-gradient(135deg,#F5D27A,#D4AF37); color:#3A2A00 !important; }}
html body .stApp .sp-lab {{ display:flex; align-items:center; gap:10px; margin:1.15rem 0 .6rem; font-size:.68rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:{t["soft"]} !important; }}
html body .stApp .sp-lab::after {{ content:""; flex:1; height:1px; background:{t["line"]}; }}
html body .stApp .sp-note {{ display:flex; gap:9px; align-items:flex-start; margin-top:1.15rem; padding:.8rem .9rem; border-radius:16px; background:{tile}; font-size:.78rem; line-height:1.5; color:{t["soft"]} !important; }}
html body .stApp .sp-collapsed {{ display:flex; align-items:center; gap:9px; padding:.75rem .9rem; border-radius:16px; background:{tile}; font-size:.8rem; color:{t["soft"]} !important; border:1px dashed {t["line"]}; }}
/* — grilles de tuiles — */
{_P}[class*="st-key-spg_"] {{ display:grid !important; grid-template-columns:1fr 1fr; gap:.6rem !important; }}
{_P}[class*="st-key-spg_"] > [data-testid="stElementContainer"] {{ width:100% !important; min-width:0; margin:0 !important; }}
{_P}.st-key-spg_one {{ grid-template-columns:1fr; }}
{_P}.st-key-spg_lang {{ grid-template-columns:repeat(4,1fr); gap:.45rem !important; }}
/* — tuile — */
html body .stApp [class*="st-key-sp_"] button, html body .stApp [class*="st-key-spl_"] button {{ position:relative; width:100% !important; min-height:92px !important; border-radius:18px !important;
  padding:46px 10px 12px 14px !important; justify-content:flex-start !important; align-items:flex-end !important; text-align:left !important; background:{tile} !important; color:{t["ink"]} !important;
  border:1.5px solid transparent !important; box-shadow:none !important; font-weight:650 !important; transition:background .18s ease, border-color .18s ease, transform .18s ease !important; }}
html body .stApp [class*="st-key-sp_"] button p, html body .stApp [class*="st-key-spl_"] button p {{ font-size:.82rem !important; font-weight:650 !important; line-height:1.25 !important; text-align:left !important; margin:0 !important; color:inherit !important; }}
html body .stApp [class*="st-key-sp_"] button:hover {{ background:{tile_h} !important; transform:translateY(-1px); }}
html body .stApp [class*="st-key-sp_"] button[kind="primary"] {{ background:color-mix(in srgb,{acc} 13%,{tile}) !important; border-color:{acc} !important; color:{t["ink"]} !important; }}
html body .stApp [class*="st-key-sp_"] button[kind="primary"]::after {{ content:"✓"; position:absolute; right:11px; top:12px; width:20px; height:20px; border-radius:50%;
  display:flex; align-items:center; justify-content:center; background:{acc}; color:#fff; font-size:.7rem; font-weight:900; }}
{_P}.st-key-spg_one [class*="st-key-sp_"] button {{ min-height:62px !important; padding:0 44px 0 52px !important; align-items:center !important; }}
html body .stApp .st-key-spg_one button::before {{ top:50% !important; margin-top:-12px; }}
html body .stApp .st-key-spg_one button[kind="primary"]::after {{ top:50%; margin-top:-10px; }}
/* — verrouillées — */
html body .stApp [class*="st-key-spl_"] button {{ opacity:.78; border:1.5px dashed {t["line"]} !important; }}
html body .stApp [class*="st-key-spl_"] button::before {{ filter:grayscale(.85); opacity:.75; }}
html body .stApp [class*="st-key-spl_"] button::after {{ content:"Premium+"; position:absolute; right:10px; top:9px; font-size:.54rem; font-weight:900; letter-spacing:.06em; text-transform:uppercase;
  padding:.14rem .42rem; border-radius:999px; background:linear-gradient(135deg,#F5D27A,#D4AF37); color:#3A2A00; }}
html body .stApp .st-key-spl_deep button::after {{ content:"Premium"; }}
/* — langues — */
html body .stApp [class*="st-key-sp_lg_"] button {{ min-height:46px !important; padding:0 !important; justify-content:center !important; align-items:center !important; border-radius:14px !important; }}
html body .stApp [class*="st-key-sp_lg_"] button::before {{ display:none; }}
html body .stApp [class*="st-key-sp_lg_"] button p {{ text-align:center !important; font-weight:800 !important; letter-spacing:.04em; }}
html body .stApp [class*="st-key-sp_lg_"] button[kind="primary"]::after {{ display:none; }}
html body .stApp [class*="st-key-sp_lg_"] button[kind="primary"] {{ background:linear-gradient(135deg,{acc},{t["acc_dark"]}) !important; color:#fff !important; }}
/* — bouton de repli (icône) — */
html body .stApp .st-key-studio_panel_toggle button {{ width:42px !important; min-height:42px !important; height:42px !important; padding:0 !important; border-radius:13px !important;
  background:{tile} !important; border:1px solid {t["line"]} !important; box-shadow:none !important; position:relative; }}
html body .stApp .st-key-studio_panel_toggle button p {{ opacity:0; font-size:0 !important; }}
html body .stApp .st-key-studio_panel_toggle button::before {{ content:""; position:absolute; inset:0; margin:auto; width:21px; height:21px; background:{t["soft"]};
  -webkit-mask:{_mask("panel")} center/contain no-repeat; mask:{_mask("panel")} center/contain no-repeat; }}
html body .stApp .st-key-studio_panel_toggle button:hover {{ background:{tile_h} !important; }}
html body .stApp .st-key-studio_panel_toggle button:hover::before {{ background:{acc}; }}
{_P}.st-key-sp_headrow {{ display:grid !important; grid-template-columns:1fr auto; align-items:start; gap:.6rem !important; }}
{_P}.st-key-sp_headrow > [data-testid="stElementContainer"] {{ width:auto !important; margin:0 !important; }}
/* — curseurs — */
{_P}.st-key-sp_qty {{ background:{tile}; border-radius:20px; padding:.35rem 1rem .6rem !important; }}
html body .stApp .st-key-sp_qty label p, html body .stApp .st-key-sp_qty [data-testid="stWidgetLabel"] p {{ color:{t["ink"]} !important; font-weight:650 !important; font-size:.84rem !important; }}
/* — rail repliée (icônes seules) — */
{_P}.st-key-sr_rail {{ background:{panel} !important; border:1px solid {t["line"]} !important; border-radius:22px !important; padding:.55rem .35rem !important; gap:.35rem !important;
  align-items:center; box-shadow:{t["shadow"]} !important; position:sticky; top:4.5rem; }}
{_P}.st-key-sr_rail > [data-testid="stElementContainer"] {{ width:100% !important; margin:0 !important; display:flex; justify-content:center; }}
html body .stApp [class*="st-key-sr_"] button {{ position:relative; width:44px !important; min-width:44px !important; height:44px !important; min-height:44px !important; padding:0 !important; border-radius:14px !important;
  background:transparent !important; border:1.5px solid transparent !important; box-shadow:none !important; transition:background .15s ease, transform .15s ease !important; }}
html body .stApp [class*="st-key-sr_"] button p {{ font-size:0 !important; opacity:0; margin:0 !important; }}
html body .stApp [class*="st-key-sr_"] button:hover {{ background:{tile_h} !important; transform:scale(1.06); }}
html body .stApp [class*="st-key-sr_"] button[kind="primary"] {{ background:color-mix(in srgb,{acc} 14%,transparent) !important; border-color:color-mix(in srgb,{acc} 55%,transparent) !important; }}
html body .stApp [class*="st-key-sr_"] button::before {{ content:""; position:absolute; inset:0; margin:auto; width:22px; height:22px; }}
html body .stApp .st-key-sr_lock button {{ opacity:.55; }}
html body .stApp .st-key-sr_lock button::before {{ filter:grayscale(.9); }}
html body .stApp .sr-sep {{ width:26px; height:1px; background:{t["line"]}; margin:.15rem auto; }}
@media (max-width:420px) {{ {_P}.st-key-spg_lang {{ grid-template-columns:repeat(2,1fr); }} }}
</style>"""
    st.markdown(css, unsafe_allow_html=True)


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _flip(key: str, default: bool = True) -> None:
    st.session_state[key] = not st.session_state.get(key, default)


def _set(key: str, value) -> None:
    st.session_state[key] = value


def _toggle_panel() -> None:
    st.session_state.studio_panel_open = not st.session_state.get("studio_panel_open", True)


def _locked(msg: str) -> None:
    try:
        st.toast(msg)
    except Exception:
        pass


def _tile(key: str, label: str, active: bool, *, on_click, args=(), help=None) -> None:
    st.button(label, key=key, type="primary" if active else "secondary", on_click=on_click, args=args, use_container_width=True, help=help)


def _rail(tier: int, ss) -> None:
    def b(key, label, active=False, fn=_flip, args=()):
        st.button("\u00a0", key=key, help=label, type="primary" if active else "secondary", on_click=fn, args=args)

    def lock(key, label, need):
        st.button("\u00a0", key=key, help=f"{label} — {need}", on_click=_locked, args=(f"{label} : disponible avec {need}.",))

    with _keyed("sr_rail"):
        b("sr_toggle", "Déplier les réglages", fn=_toggle_panel)
        st.markdown('<div class="sr-sep"></div>', unsafe_allow_html=True)
        fast_on = ss.get("cfg_model", "qualite") == "rapide" if tier >= 2 else True
        b("sr_m_fast", "Modèle rapide", fast_on, _set, ("cfg_model", "rapide"))
        if tier >= 2:
            b("sr_m_deep", "Modèle Qualité Premium", not fast_on, _set, ("cfg_model", "qualite"))
        else:
            lock("sr_deep", "Qualité Premium", "Premium")
        b("sr_turbo", T("turbo"), bool(ss.get("cfg_turbo", True)), _flip, ("cfg_turbo",))
        st.markdown('<div class="sr-sep"></div>', unsafe_allow_html=True)
        if tier >= 3:
            b("sr_tldr", "TL;DR enrichi", bool(ss.get("studio_tldr", True)), _flip, ("studio_tldr",))
            b("sr_adv", "Questions avancées", bool(ss.get("studio_questions", True)), _flip, ("studio_questions",))
            b("sr_act", "Actions à faire", bool(ss.get("studio_actions", True)), _flip, ("studio_actions",))
            b("sr_chat", "Mode Studio Chat", bool(ss.get("studio_chat", True)), _flip, ("studio_chat",))
        else:
            lock("sr_tldr", "TL;DR enrichi", "Premium+")
            lock("sr_act", "Actions intelligentes", "Premium+")
            lock("sr_slides", T("fx8"), "Premium+")
            lock("sr_chat", "Chat vidéo IA", "Premium+")
        st.markdown('<div class="sr-sep"></div>', unsafe_allow_html=True)
        b("sr_o_kw", T("extract_kw"), bool(ss.get("cfg_kw", True)), _flip, ("cfg_kw",))
        b("sr_o_qa", T("gen_q"), bool(ss.get("cfg_qa", True)), _flip, ("cfg_qa",))
        b("sr_o_tr", T("chip_tr"), bool(ss.get("cfg_translate", True)), _flip, ("cfg_translate",))


def render_studio_panel(tier: int) -> None:
    _css(tier)
    plan = {0: "Gratuit", 1: "Basique", 2: "Premium", 3: "Premium+"}.get(tier, "Gratuit")
    is_open = st.session_state.get("studio_panel_open", True)

    if not is_open:
        _rail(tier, st.session_state)
        return

    with _keyed("sp_panel"):
        with _keyed("sp_headrow"):
            st.markdown(
                f'<div class="sp-head"><div class="sp-logo">'
                f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{_I["sparkles"]}</svg></div>'
                f'<div><div class="sp-t">Studio Premium <span class="sp-plan">{plan}</span></div><div class="sp-s">Réglages rapides de sortie</div></div></div>',
                unsafe_allow_html=True)
            st.button(" ", key="studio_panel_toggle", help="Afficher / masquer les réglages", on_click=_toggle_panel)

        ss = st.session_state
        # ── Moteur IA ──
        st.markdown('<div class="sp-lab">Moteur IA</div>', unsafe_allow_html=True)
        with _keyed("spg_model"):
            fast_on = ss.get("cfg_model", "qualite") == "rapide" if tier >= 2 else True
            _tile("sp_m_fast", "Rapide", fast_on, on_click=_set, args=("cfg_model", "rapide"))
            if tier >= 2:
                _tile("sp_m_deep", "Qualité Premium", not fast_on, on_click=_set, args=("cfg_model", "qualite"))
            else:
                st.button("Qualité Premium", key="spl_deep", use_container_width=True, on_click=_locked, args=("Modèle Qualité : disponible à partir du plan Premium.",))
        with _keyed("spg_one"):
            _tile("sp_turbo", T("turbo"), bool(ss.get("cfg_turbo", True)), on_click=_flip, args=("cfg_turbo",))

        # ── Fonctions Premium+ ──
        st.markdown('<div class="sp-lab">Fonctions Premium+</div>', unsafe_allow_html=True)
        if tier >= 3:
            with _keyed("spg_lang"):
                cur = ss.get("cfg_target", "fr")
                for code in ("fr", "en", "es", "de"):
                    _tile(f"sp_lg_{code}", code.upper(), cur == code, on_click=_set, args=("cfg_target", code), help=str(LANGS.get(code) or code))
            st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
            with _keyed("spg_feats"):
                _tile("sp_tldr", "TL;DR enrichi", bool(ss.get("studio_tldr", True)), on_click=_flip, args=("studio_tldr",))
                _tile("sp_adv", "Questions avancées", bool(ss.get("studio_questions", True)), on_click=_flip, args=("studio_questions",))
                _tile("sp_act", "Actions à faire", bool(ss.get("studio_actions", True)), on_click=_flip, args=("studio_actions",))
                _tile("sp_chat", "Mode Studio Chat", bool(ss.get("studio_chat", True)), on_click=_flip, args=("studio_chat",))
        else:
            with _keyed("spg_feats_l"):
                for k, lbl in (("spl_tldr", "TL;DR enrichi"), ("spl_act", "Actions intelligentes"), ("spl_slides", T("fx8")), ("spl_chat", "Chat vidéo IA")):
                    st.button(lbl, key=k, use_container_width=True, on_click=_locked, args=(f"{lbl} : disponible avec Premium+.",))

        # ── Quantités ──
        st.markdown('<div class="sp-lab">Quantités</div>', unsafe_allow_html=True)
        with _keyed("sp_qty"):
            st.slider(T("kw_count"), 5, 20, key="cfg_kw_n")
            st.slider(T("q_count"), 3, 10, key="cfg_q_n")
            st.slider(T("chunk_size"), 1200, 4000, step=200, key="cfg_chunk")

        # ── Sortie ──
        st.markdown('<div class="sp-lab">Sortie</div>', unsafe_allow_html=True)
        with _keyed("spg_out"):
            _tile("sp_o_kw", T("extract_kw"), bool(ss.get("cfg_kw", True)), on_click=_flip, args=("cfg_kw",))
            _tile("sp_o_qa", T("gen_q"), bool(ss.get("cfg_qa", True)), on_click=_flip, args=("cfg_qa",))
            _tile("sp_o_tr", T("chip_tr"), bool(ss.get("cfg_translate", True)), on_click=_flip, args=("cfg_translate",))

        st.markdown(f'<div class="sp-note"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="flex:none;margin-top:2px"><circle cx="12" cy="12" r="9.5"/><path d="M12 11v6M12 7.5v.01"/></svg><span>Ces réglages s\'appliquent à votre prochaine analyse. Ils sont mémorisés pour ce compte.</span></div>', unsafe_allow_html=True)