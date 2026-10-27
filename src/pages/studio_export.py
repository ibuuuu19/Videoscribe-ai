"""
Onglet « Exporter les notes » du Studio — centre d'export.

Cartes par format (Markdown, PDF, Anki, Obsidian, Notion, rapport Studio), présentation, partage public,
formats verrouillés selon le plan (avec accès direct aux formules) et zone de maintenance.
Les fonctions d'export sont celles d'origine : seul le rendu change.
"""
from datetime import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as _components

from src.ui.components import ic
from src.ui.i18n import T
from src.ui.mobile import theme_tokens
from src.ui.storage import save_share, export_anki
from src.pages.studio_utils import _studio_md
from src.pages.studio_slides import export_presentation
from src.export_utils import export_to_markdown, export_to_pdf, export_to_obsidian, export_to_notion

_P = 'html body .stApp div[data-testid="stVerticalBlock"]'
_PLAN = {0: "Gratuit", 1: "Basique", 2: "Premium", 3: "Premium+"}

_CSS = """
<style>
@P@[class*="st-key-vxc_"] { position:relative; background:@surface@ !important; border:1px solid @line@ !important; border-radius:20px !important;
  padding:1.05rem 1.1rem 1.1rem !important; gap:.8rem !important; box-shadow:@shadow@ !important; transition:transform .18s ease, border-color .18s ease, box-shadow .18s ease; overflow:hidden; }
@P@[class*="st-key-vxc_"]::before { content:""; position:absolute; left:0; right:0; top:0; height:3px; background:linear-gradient(90deg,@acc@,@acc2@); opacity:.9; }
@P@[class*="st-key-vxc_"]:hover { transform:translateY(-2px); border-color:@acc@ !important; }
@P@[class*="st-key-vxc_l_"] { opacity:.96; }
@P@[class*="st-key-vxc_l_"]::before { background:linear-gradient(90deg,#94A3B8,#CBD5E1); }
@P@[class*="st-key-vxc_l_"]:hover { transform:none; border-color:@line@ !important; }
@P@[class*="st-key-vxc_"] .stDownloadButton > button,
@P@[class*="st-key-vxc_"] .stButton > button { width:100% !important; min-height:44px !important; border-radius:13px !important; font-weight:700 !important; font-size:.88rem !important; letter-spacing:.01em; }
@P@[class*="st-key-vxc_"] .stDownloadButton > button { background:linear-gradient(135deg,@acc@,@acc2@) !important; color:#fff !important; border:0 !important; box-shadow:0 8px 20px rgba(30,70,140,.22) !important; }
@P@[class*="st-key-vxc_"] .stDownloadButton > button:hover { filter:brightness(1.07); transform:translateY(-1px); }
@P@[class*="st-key-vxc_"] .stButton > button { background:transparent !important; color:@ink@ !important; border:1.5px solid @line@ !important; box-shadow:none !important; }
@P@[class*="st-key-vxc_"] .stButton > button:hover { border-color:@acc@ !important; color:@acc@ !important; }
@P@[class*="st-key-vxc_"] .stButton > button[kind="primary"] { background:linear-gradient(135deg,@acc@,@acc2@) !important; color:#fff !important; border:0 !important; }
@P@[class*="st-key-vxc_l_"] .stButton > button { background:@surface2@ !important; color:@soft@ !important; border:1px dashed @line@ !important; }
@P@.st-key-vx_maint .stButton > button { min-height:40px !important; border-radius:12px !important; background:transparent !important; color:@soft@ !important; border:1px solid @line@ !important; box-shadow:none !important; font-weight:600 !important; font-size:.83rem !important; }
@P@.st-key-vx_maint .stButton > button:hover { color:@ink@ !important; border-color:@acc@ !important; }
@P@.st-key-vx_maint .stButton > button:hover p { color:@ink@ !important; }
html body .stApp .vx-hero { position:relative; overflow:hidden; border-radius:24px; padding:1.5rem 1.6rem; margin:.2rem 0 1.2rem; color:#fff;
  background:radial-gradient(520px 260px at 88% -10%, rgba(255,255,255,.20), transparent 60%), linear-gradient(135deg,@acc2@,@acc@ 62%, #10B981 140%); box-shadow:0 22px 50px rgba(30,70,140,.28); }
html body .stApp .vx-hero::after { content:""; position:absolute; inset:0; background-image:linear-gradient(rgba(255,255,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.06) 1px,transparent 1px); background-size:34px 34px; mask-image:radial-gradient(ellipse at 100% 0%,#000 0%,transparent 70%); -webkit-mask-image:radial-gradient(ellipse at 100% 0%,#000 0%,transparent 70%); pointer-events:none; }
html body .stApp .vx-hero > * { position:relative; z-index:1; }
html body .stApp .vx-hero .row { display:flex; align-items:center; gap:14px; }
html body .stApp .vx-hero .ico { width:50px; height:50px; border-radius:16px; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.30); flex:none; }
html body .stApp .vx-hero .t { font-family:'Sora',sans-serif; font-weight:800; font-size:1.45rem; letter-spacing:-.025em; line-height:1.15; color:#fff !important; }
html body .stApp .vx-hero .s { margin-top:.25rem; font-size:.92rem; color:rgba(255,255,255,.86) !important; line-height:1.55; }
html body .stApp .vx-hero .chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:1rem; }
html body .stApp .vx-chip { display:inline-flex; align-items:center; gap:6px; padding:.32rem .75rem; border-radius:999px; font-size:.74rem; font-weight:700; background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.28); color:#fff !important; backdrop-filter:blur(6px); }
html body .stApp .vx-sec { display:flex; align-items:center; gap:12px; margin:1.5rem 0 .75rem; }
html body .stApp .vx-sec b { font-size:.72rem; letter-spacing:.16em; text-transform:uppercase; color:@soft@ !important; font-weight:800; white-space:nowrap; }
html body .stApp .vx-sec i { flex:1; height:1px; background:@line@; }
html body .stApp .vx-sec small { font-size:.74rem; color:@soft@ !important; white-space:nowrap; }
/* padding-bottom:1rem compense le margin-bottom:-1rem que Streamlit applique à tout bloc markdown */
html body .stApp .vx-head { display:flex; align-items:flex-start; gap:12px; padding-bottom:1rem; }
html body .stApp .vx-ico { width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center; flex:none; color:#fff; background:linear-gradient(135deg,@acc@,@acc2@); box-shadow:0 8px 18px rgba(30,70,140,.25); }
html body .stApp .vx-lock .vx-ico { background:linear-gradient(135deg,#94A3B8,#64748B); box-shadow:none; }
html body .stApp .vx-ttl { font-weight:800; font-size:1rem; color:@ink@ !important; line-height:1.25; display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
html body .stApp .vx-desc { min-height:2.5em; margin-top:.25rem; font-size:.82rem; color:@soft@ !important; line-height:1.55; }
html body .stApp .vx-fmt { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.66rem; font-weight:800; letter-spacing:.04em; padding:.15rem .5rem; border-radius:7px; background:@surface2@; border:1px solid @line@; color:@soft@ !important; }
html body .stApp .vx-need { display:inline-flex; align-items:center; gap:5px; font-size:.66rem; font-weight:800; padding:.15rem .55rem; border-radius:999px; background:rgba(245,158,11,.14); color:#D97706 !important; border:1px solid rgba(245,158,11,.35); }
html body .stApp .vx-note { font-size:.78rem; color:@soft@ !important; margin:.2rem 0 .7rem; }
html body .stApp .vx-share-link { font-family:ui-monospace,Menlo,monospace; font-size:.78rem; padding:.55rem .7rem; border-radius:12px; background:@surface2@; border:1px dashed @line@; color:@ink@ !important; word-break:break-all; }
@media (max-width:768px) {
  html body .stApp .vx-hero { padding:1.15rem 1.1rem; border-radius:20px; }
  html body .stApp .vx-hero .t { font-size:1.2rem; }
  html body .stApp .vx-hero .ico { width:42px; height:42px; border-radius:14px; }
  @P@[class*="st-key-vxc_"] { padding:.95rem .95rem 1rem !important; border-radius:18px !important; }
}
</style>
"""


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _inject_css() -> None:
    t = theme_tokens()
    css = _CSS.replace("@P@", _P)
    for k, v in {"acc": t["acc"], "acc2": t["acc_dark"], "ink": t["ink"], "soft": t["soft"], "surface": t["surface"],
                 "surface2": t["surface2"], "line": t["line"], "shadow": t["shadow"]}.items():
        css = css.replace(f"@{k}@", v)
    st.markdown(css, unsafe_allow_html=True)


def _md(html: str) -> None:
    # une seule ligne, sans indentation ni ligne vide : évite que Markdown ne le prenne pour un bloc de code
    st.markdown(" ".join(line.strip() for line in html.strip().splitlines() if line.strip()), unsafe_allow_html=True)


def _card_head(icon: str, title: str, desc: str, fmt: str = "", need: str = "") -> None:
    badge = f'<span class="vx-need">{ic("lock", 11)} {need}</span>' if need else (f'<span class="vx-fmt">{fmt}</span>' if fmt else "")
    cls = "vx-head vx-lock" if need else "vx-head"
    _md(f'<div class="{cls}"><div class="vx-ico">{ic(icon, 20)}</div><div><div class="vx-ttl">{title} {badge}</div><div class="vx-desc">{desc}</div></div></div>')


def _section(title: str, hint: str = "") -> None:
    _md(f'<div class="vx-sec"><b>{title}</b><i></i>{f"<small>{hint}</small>" if hint else ""}</div>')


def _to_premium() -> None:
    st.session_state.page = "premium"
    st.session_state.show_privacy = False


def _reanalyse(vid: str) -> None:
    st.session_state[f"refresh_{vid}"] = True
    st.session_state.result = None


def _del_cache(vid: str) -> None:
    for p in Path("cache").glob(f"notes_{vid}_*.json"):
        try:
            p.unlink()
        except Exception:
            pass
    st.session_state.result = None
    try:
        st.toast("Cache supprimé.")
    except Exception:
        pass


def _close_batch() -> None:
    st.session_state.results_batch = []
    st.session_state.result = None


def _file_bytes(build, vid: str, kind: str) -> bytes:
    """Génère le fichier UNE seule fois par analyse (le PDF était régénéré à chaque exécution du script)."""
    store = st.session_state.setdefault("_vx_bytes", {})
    key = (vid, kind)
    if key not in store:
        with open(build(), "rb") as f:
            store[key] = f.read()
    return store[key]


def _locked(key: str, icon: str, title: str, desc: str, need_tier: int) -> None:
    with _keyed(f"vxc_l_{key}"):
        _card_head(icon, title, desc, need=_PLAN[need_tier])
        st.button(f"Débloquer avec {_PLAN[need_tier]}", key=f"vx_up_{key}", on_click=_to_premium, use_container_width=True)


def render_export_tab(data: dict, user: str, tier: int) -> None:
    _inject_css()
    vid = data["video_id"]
    fn_key = f"_vx_fn_{vid}"
    if fn_key not in st.session_state:
        st.session_state[fn_key] = f"summary_{vid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    filename = st.session_state[fn_key]

    needs = [0, 1, 2, 3, 3, 0, 3, 1]   # md, pdf, anki, obsidian, notion, rapport, présentation, partage
    ok = sum(1 for n in needs if tier >= n)
    _md(f'''<div class="vx-hero"><div class="row"><div class="ico">{ic("download", 24)}</div><div>
      <div class="t">Centre d'export</div>
      <div class="s">Emportez vos notes dans le format de votre flux de travail : documents, flashcards, outils de prise de notes, présentation ou lien de partage.</div></div></div>
      <div class="chips"><span class="vx-chip">{ic("film", 13)} {vid}</span><span class="vx-chip">{ic("check", 13)} {ok} / {len(needs)} formats disponibles</span><span class="vx-chip">{ic("award", 13)} Formule {_PLAN.get(tier, "Gratuit")}</span></div></div>''')

    # ── Documents ──
    _section("Documents", "Lecture & archivage")
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with _keyed("vxc_md"):
            _card_head("file", "Markdown", "Notes structurées, compatibles avec tous les éditeurs.", ".MD")
            st.download_button(T("dl_md"), _file_bytes(lambda: export_to_markdown(data, filename), vid, "md"),
                               file_name=f"{filename}.md", mime="text/markdown", use_container_width=True, key="vx_dl_md")
    with c2:
        if tier >= 1:
            with _keyed("vxc_pdf"):
                _card_head("book", "PDF", "Document prêt à imprimer ou à partager.", ".PDF")
                st.download_button(T("dl_pdf"), _file_bytes(lambda: export_to_pdf(data, filename), vid, "pdf"),
                                   file_name=f"{filename}.pdf", mime="application/pdf", use_container_width=True, key="vx_dl_pdf")
        else:
            _locked("pdf", "book", "PDF", "Document prêt à imprimer ou à partager.", 1)
    with c3:
        if tier >= 2:
            with _keyed("vxc_anki"):
                _card_head("star", "Anki", "Flashcards à réviser avec la répétition espacée.", ".TXT")
                st.download_button(T("dl_anki"), _file_bytes(lambda: export_anki(data, filename), vid, "anki"),
                                   file_name=f"{filename}.anki.txt", mime="text/plain", use_container_width=True, key="vx_dl_anki")
        else:
            _locked("anki", "star", "Anki", "Flashcards à réviser avec la répétition espacée.", 2)

    # ── Intégrations ──
    _section("Intégrations", "Vos outils de notes")
    i1, i2, i3 = st.columns(3, gap="medium")
    with i1:
        if tier >= 3:
            with _keyed("vxc_obs"):
                _card_head("hash", "Obsidian", "Liens internes et métadonnées prêts pour votre coffre.", ".MD")
                st.download_button("Obsidian", _file_bytes(lambda: export_to_obsidian(data, filename), vid, "obs"),
                                   file_name=f"{filename}_obsidian.md", mime="text/markdown", use_container_width=True, key="vx_dl_obs")
        else:
            _locked("obs", "hash", "Obsidian", "Liens internes et métadonnées prêts pour votre coffre.", 3)
    with i2:
        if tier >= 3:
            with _keyed("vxc_notion"):
                _card_head("folder", "Notion", "Import direct dans une page ou une base Notion.", ".MD")
                st.download_button("Notion", _file_bytes(lambda: export_to_notion(data, filename), vid, "notion"),
                                   file_name=f"{filename}_notion.md", mime="text/markdown", use_container_width=True, key="vx_dl_notion")
        else:
            _locked("notion", "folder", "Notion", "Import direct dans une page ou une base Notion.", 3)
    with i3:
        with _keyed("vxc_rep"):
            _card_head("chart", "Rapport Studio complet", "Synthèse, score, mots-clés, questions et actions.", ".MD")
            st.download_button("Exporter le rapport Studio complet", _studio_md(data).encode("utf-8"),
                               file_name=f"{filename}_studio.md", mime="text/markdown", use_container_width=True, key="vx_dl_rep")

    # ── Présentation & partage ──
    _section("Présentation & partage", "Diffusez vos résultats")
    p1, p2 = st.columns(2, gap="medium")
    with p1:
        if tier >= 3:
            pres_key = f"pres_html_{vid}"
            with _keyed("vxc_pres"):
                _card_head("film", T("fx8"), "Diaporama 16:9 animé (sommaire, chiffres, sections, questions) — export PDF intégré.", "HTML")
                if st.button("🎬 Générer la présentation", key="studio_gen_pres", use_container_width=True,
                             type="primary" if not st.session_state.get(pres_key) else "secondary"):
                    with st.spinner("Génération des slides…"):
                        st.session_state[pres_key] = export_presentation(data, accent=theme_tokens()["acc"], theme=st.session_state.get("theme", "light"))
                if st.session_state.get(pres_key):
                    st.download_button(f"💾 {T('dl_presentation')}", st.session_state[pres_key].encode("utf-8"),
                                       file_name=f"presentation_{vid}.html", mime="text/html", use_container_width=True, key="vx_dl_pres")
        else:
            _locked("pres", "film", T("fx8"), "Diaporama 16:9 animé (sommaire, chiffres, sections, questions) — export PDF intégré.", 3)
    with p2:
        if tier >= 1:
            with _keyed("vxc_share"):
                _card_head("link", "Lien de partage public", "Un lien consultable sans compte, pour envoyer vos notes.", "URL")
                if st.button(T("share"), key="studio_share", use_container_width=True):
                    sid = save_share(data, user)
                    st.session_state.share_link = f"?page=share&id={sid}"
                if st.session_state.get("share_link"):
                    st.code(st.session_state.share_link, language=None)
        else:
            _locked("share", "link", "Lien de partage public", "Un lien consultable sans compte, pour envoyer vos notes.", 1)

    if tier >= 3 and st.session_state.get(f"pres_html_{vid}"):
        _section("Aperçu de la présentation")
        _components.html(st.session_state[f"pres_html_{vid}"], height=660)

    # ── Maintenance ──
    _section("Maintenance", "Actions sur cette analyse")
    with _keyed("vx_maint"):
        has_batch = bool(st.session_state.get("results_batch"))
        cols = st.columns(3 if has_batch else 2, gap="small")
        with cols[0]:
            st.button(T("reanalyse"), key="studio_reanalyse", use_container_width=True, on_click=_reanalyse, args=(vid,))
        with cols[1]:
            st.button(T("del_cache"), key="studio_del_cache", use_container_width=True, on_click=_del_cache, args=(vid,))
        if has_batch:
            with cols[2]:
                st.button(T("close_batch"), key="studio_close_batch", use_container_width=True, on_click=_close_batch)