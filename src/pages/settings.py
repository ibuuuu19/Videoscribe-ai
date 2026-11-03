"""
Page « Paramètres » — refonte premium.

· Bureau : navigation latérale en cartes (icônes colorées, sections groupées, recherche) + contenu en cartes.
· Mobile (≤ 768 px) : la navigation devient une LISTE de sections ; toucher une option ouvre SA propre section
  (bouton « Retour » en haut) — comme les réglages iOS / Android.
· Sections : Général (thème, couleur d'accent, langue, typographie), Compte, Notifications, Confidentialité
  (export des données, effacement de l'historique), Facturation (formule + fonctionnalités incluses),
  Capacités (moteur IA, quantités, sortie, voix), Extensions, Connecteurs, Plugins, Développeur, Compétences, Mémoire.

Toutes les clés de session existantes sont conservées (cfg_*, prof_*, sel_lang, theme, cfg_section…).
Nouvelle clé : `cfg_open` (mobile : une section est ouverte).
Les dépendances de app.py arrivent via le dictionnaire `ctx` (voir render_config dans app.py).
"""
import json
from datetime import datetime
from urllib.parse import quote

import streamlit as st

from src.ui.i18n import T, LANGS
from src.ui.mobile import theme_tokens

# ───────────────────────── icônes (tracés 24×24) ─────────────────────────
_I = {
    "sliders": '<path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1"/><circle cx="15" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="18" r="2"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    "bell": '<path d="M6 17V11a6 6 0 1112 0v6l1.5 2h-15z"/><path d="M10 21h4"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.4 8.2-8 9-4.6-.8-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "card": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 10h18M7 15h4"/>',
    "cpu": '<rect x="5" y="5" width="14" height="14" rx="3.5"/><rect x="9" y="9" width="6" height="6" rx="1.2"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
    "tool": '<path d="M14.7 6.3a4 4 0 005 5L21 13l-8 8-3-3 8-8z"/><path d="M13 7L5 15"/><path d="M3 21l3-3"/>',
    "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3A4 4 0 0011 18.7l1-1"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "spark": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "back": '<path d="M15 5l-7 7 7 7"/>',
    "palette": '<path d="M12 3a9 9 0 100 18c1.4 0 2-1 1.6-2.1-.4-1.2.3-2.4 1.6-2.4H17a4 4 0 004-4C21 6.6 17 3 12 3z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="15" cy="7.5" r="1"/>',
    "type": '<path d="M4 7V5h16v2M9 19h6M12 5v14"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/>',
    "download": '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
    "trash": '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v5M14 11v5"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="3"/><path d="M8 11V8a4 4 0 018 0v3"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "film": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M8 4v16M16 4v16M3 9h5M3 15h5M16 9h5M16 15h5"/>',
    "chev": '<path d="M9 5l7 7-7 7"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8 8 0 019.5 4a8 8 0 1010.5 10.5z"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>',
    "brain": '<path d="M9 4a3 3 0 00-3 3 3 3 0 00-2 5 3 3 0 002 5 3 3 0 006 0V4a3 3 0 00-3 0zM15 4a3 3 0 013 3 3 3 0 012 5 3 3 0 01-2 5 3 3 0 01-6 0"/>',
    "note": '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
}


def _svg(name: str, size: int = 18, color: str = "currentColor", sw: float = 1.9) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_I[name]}</svg>')


def _uri(name: str, color: str = "#fff", sw: float = 1.9) -> str:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
           f'stroke-linecap="round" stroke-linejoin="round">{_I[name]}</svg>')
    return f'url("data:image/svg+xml,{quote(svg)}")'


# ───────────────────────── textes propres à cette page ─────────────────────────
_L = {
    "fr": {
        "back": "Paramètres", "grp_account": "Compte & préférences", "grp_studio": "Studio IA", "grp_int": "Intégrations", "grp_adv": "Avancé",
        "notifs": "Notifications", "connect": "Connecteurs", "dev": "Développeur", "skills": "Compétences", "memory": "Mémoire",
        "d_general": "Apparence, couleur d'accent, langue et typographie.",
        "d_compte": "Votre profil, votre identité et votre sécurité.",
        "d_notifications": "Choisissez ce qui mérite de vous interrompre.",
        "d_confidentialite": "Vos données vous appartiennent : exportez-les ou effacez-les.",
        "d_facturation": "Votre formule, ce qu'elle inclut et sa gestion.",
        "d_capacites": "Moteur IA, quantités générées, sortie et voix.",
        "d_extensions": "Envoyez vos notes vers vos outils de travail.",
        "d_connecteurs": "Reliez VideoScribe à vos applications.",
        "d_plugins": "Ajoutez de nouvelles fonctions à votre espace.",
        "d_developpeur": "API et clés d'accès pour intégrer VideoScribe.",
        "d_competences": "Apprenez à l'IA vos formats de notes préférés.",
        "d_memoire": "Ce que l'IA retient de vos préférences.",
        "theme": "Thème", "theme_d": "Choisissez l'ambiance qui vous convient.", "accent": "Couleur d'accent",
        "accent_d": "Boutons, icônes et surbrillances de toute l'application.",
        "lang_d": "Langue de l'interface et langue des analyses traduites.", "typo": "Typographie & lisibilité",
        "typo_d": "Police, taille et interlignes, avec aperçu en direct.", "sample": "VideoScribe transforme une vidéo en notes claires : résumé, mots-clés, questions et points d'action.",
        "identity": "Identité", "identity_d": "Ces informations personnalisent les résumés de l'IA.", "security": "Sécurité",
        "security_d": "Protégez l'accès à votre compte.", "role": "Rôle", "photo": "Photo de profil", "photo_ok": "Photo enregistrée",
        "notifs_d": "Alertes liées à vos analyses.", "rgpd": "Vos droits (RGPD)",
        "rgpd1": "Vos analyses ne sont visibles que de vous.", "rgpd2": "Vous pouvez exporter vos données à tout moment.",
        "rgpd3": "Vous pouvez effacer votre historique en un clic.", "mydata": "Mes données", "mydata_d": "Téléchargez une copie de vos analyses et réglages (JSON).",
        "export": "Exporter mes données", "danger": "Zone sensible", "danger_d": "Action définitive : l'historique effacé ne peut pas être restauré.",
        "confirm_del": "Je confirme vouloir effacer tout mon historique", "del": "Effacer mon historique", "del_ok": "Historique effacé.",
        "plan": "Formule actuelle", "today": "Analyses aujourd'hui", "included": "Inclus dans votre formule", "locked": "Disponible en Premium / Premium+",
        "f_analyse": "Analyse de vidéos", "f_search": "Recherche dans l'historique", "f_quality": "Modèle Qualité", "f_tldr": "TL;DR",
        "f_actions": "Points d'action", "f_slides": "Diaporama", "f_chat": "Chat avec la vidéo", "f_lang": "Langue de sortie",
        "engine": "Moteur IA", "engine_d": "Vitesse ou précision : choisissez le moteur.", "qty": "Quantités", "qty_d": "Combien d'éléments générer par analyse.",
        "out": "Sortie", "out_d": "Éléments ajoutés à chaque résultat.", "voice_d": "Lecture à voix haute des notes.", "locked_q": "Modèle Qualité réservé aux Premium et +",
        "soon": "Bientôt", "soon_t": "Cette section arrive bientôt",
        "ext_t": "Exports disponibles", "ext_d": "Ces outils sont déjà accessibles depuis le bouton « Exporter » d'un résultat.",
        "ext_obs": "Notes au format Obsidian (Markdown + liens).", "ext_not": "Page prête à coller dans Notion.", "ext_pdf": "Document PDF mis en page.", "ext_md": "Fichier Markdown universel.",
        "available": "Disponible",
        "p_connect": ["Google Drive & Notion en un clic", "Synchronisation automatique des notes", "Envoi vers Slack / e-mail"],
        "p_plugins": ["Modèles de résumé personnalisés", "Extensions communautaires", "Automatisations après analyse"],
        "p_dev": ["Clés d'API personnelles", "Webhooks de fin d'analyse", "Quotas et journaux d'usage"],
        "p_skills": ["Formats de notes sur mesure (cours, réunion, podcast)", "Vocabulaire métier", "Consignes réutilisables"],
        "p_memory": ["Préférences retenues d'une analyse à l'autre", "Historique des consignes", "Effacement à tout moment"],
        "active": "Actif", "version": "VideoScribe AI · Mbtech-services",
    },
    "en": {
        "back": "Settings", "grp_account": "Account & preferences", "grp_studio": "AI Studio", "grp_int": "Integrations", "grp_adv": "Advanced",
        "notifs": "Notifications", "connect": "Connectors", "dev": "Developer", "skills": "Skills", "memory": "Memory",
        "d_general": "Appearance, accent colour, language and typography.",
        "d_compte": "Your profile, identity and security.",
        "d_notifications": "Choose what deserves to interrupt you.",
        "d_confidentialite": "Your data is yours: export it or erase it.",
        "d_facturation": "Your plan, what it includes and how to manage it.",
        "d_capacites": "AI engine, generated quantities, output and voice.",
        "d_extensions": "Send your notes to your work tools.",
        "d_connecteurs": "Link VideoScribe to your apps.",
        "d_plugins": "Add new features to your workspace.",
        "d_developpeur": "API and access keys to integrate VideoScribe.",
        "d_competences": "Teach the AI your preferred note formats.",
        "d_memoire": "What the AI remembers about your preferences.",
        "theme": "Theme", "theme_d": "Pick the look that suits you.", "accent": "Accent colour",
        "accent_d": "Buttons, icons and highlights across the whole app.",
        "lang_d": "Interface language and translated-analysis language.", "typo": "Typography & readability",
        "typo_d": "Font, size and line spacing, with a live preview.", "sample": "VideoScribe turns a video into clear notes: summary, keywords, questions and action points.",
        "identity": "Identity", "identity_d": "This information personalises the AI summaries.", "security": "Security",
        "security_d": "Protect access to your account.", "role": "Role", "photo": "Profile photo", "photo_ok": "Photo saved",
        "notifs_d": "Alerts related to your analyses.", "rgpd": "Your rights (GDPR)",
        "rgpd1": "Your analyses are visible only to you.", "rgpd2": "You can export your data at any time.",
        "rgpd3": "You can erase your history in one click.", "mydata": "My data", "mydata_d": "Download a copy of your analyses and settings (JSON).",
        "export": "Export my data", "danger": "Danger zone", "danger_d": "Permanent action: erased history cannot be restored.",
        "confirm_del": "I confirm I want to erase my whole history", "del": "Erase my history", "del_ok": "History erased.",
        "plan": "Current plan", "today": "Analyses today", "included": "Included in your plan", "locked": "Available with Premium / Premium+",
        "f_analyse": "Video analysis", "f_search": "History search", "f_quality": "Quality model", "f_tldr": "TL;DR",
        "f_actions": "Action points", "f_slides": "Slides", "f_chat": "Chat with the video", "f_lang": "Output language",
        "engine": "AI engine", "engine_d": "Speed or accuracy: pick the engine.", "qty": "Quantities", "qty_d": "How many items to generate per analysis.",
        "out": "Output", "out_d": "Items added to each result.", "voice_d": "Read your notes aloud.", "locked_q": "Quality model is reserved for Premium and above",
        "soon": "Soon", "soon_t": "This section is coming soon",
        "ext_t": "Available exports", "ext_d": "These tools are already available from the “Export” button on a result.",
        "ext_obs": "Notes in Obsidian format (Markdown + links).", "ext_not": "Page ready to paste into Notion.", "ext_pdf": "Formatted PDF document.", "ext_md": "Universal Markdown file.",
        "available": "Available",
        "p_connect": ["Google Drive & Notion in one click", "Automatic note syncing", "Send to Slack / email"],
        "p_plugins": ["Custom summary templates", "Community extensions", "Post-analysis automations"],
        "p_dev": ["Personal API keys", "End-of-analysis webhooks", "Quotas and usage logs"],
        "p_skills": ["Custom note formats (class, meeting, podcast)", "Domain vocabulary", "Reusable instructions"],
        "p_memory": ["Preferences remembered across analyses", "Instruction history", "Erase at any time"],
        "active": "Active", "version": "VideoScribe AI · Mbtech-services",
    },
}


def _l() -> dict:
    return _L.get(st.session_state.get("cfg_lang", "fr"), _L["en"] if st.session_state.get("cfg_lang", "fr") in ("es", "de") else _L["fr"])


# clé → (icône, couleur)
_META = {
    "general": ("sliders", "#3B82F6"), "compte": ("user", "#8B5CF6"), "notifications": ("bell", "#F59E0B"),
    "confidentialite": ("shield", "#10B981"), "facturation": ("card", "#EC4899"), "capacites": ("cpu", "#06B6D4"),
    "extensions": ("tool", "#F97316"), "connecteurs": ("link", "#3B82F6"), "plugins": ("spark", "#8B5CF6"),
    "developpeur": ("code", "#64748B"), "competences": ("star", "#F59E0B"), "memoire": ("brain", "#14B8A6"),
}
_PRESETS = [("Bleu océan", "#2E6DB4"), ("Teal", "#14B8A6"), ("Violet", "#8B5CF6"), ("Orange", "#F97316"), ("Vert", "#22C55E"),
            ("Rouge", "#EF4444"), ("Indigo", "#6366F1"), ("Or", "#F59E0B"), ("Rose", "#EC4899"), ("Cyan", "#06B6D4")]
_P = 'html body .stApp div[data-testid="stVerticalBlock"]'


def _groups(L: dict):
    return [
        (L["grp_account"], [("general", T("general")), ("compte", T("account")), ("notifications", L["notifs"]),
                            ("confidentialite", T("privacy")), ("facturation", T("billing"))]),
        (L["grp_studio"], [("capacites", T("caps"))]),
        (L["grp_int"], [("extensions", "Extensions"), ("connecteurs", L["connect"]), ("plugins", "Plugins"), ("developpeur", L["dev"])]),
        (L["grp_adv"], [("competences", L["skills"]), ("memoire", L["memory"])]),
    ]


def _keyed(key: str):
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


# ───────────────────────── callbacks (un seul rerun par clic) ─────────────────────────
def _open(key: str):
    st.session_state.cfg_section = key
    st.session_state.cfg_open = True


def _back():
    st.session_state.cfg_open = False


def _accent(value: str, save):
    st.session_state.cfg_accent = value
    try:
        save()
    except Exception:
        pass


# ───────────────────────── CSS ─────────────────────────
def _css(active: str, cur_accent: str) -> None:
    t = theme_tokens()
    dark = st.session_state.get("theme", "light") != "light"
    acc, accd, ink, soft, line = t["acc"], t["acc_dark"], t["ink"], t["soft"], t["line"]
    card = "rgba(255,255,255,.045)" if dark else "#FFFFFF"
    flat = "rgba(255,255,255,.06)" if dark else "#F3F7FD"
    rows = []
    for key, (icon, col) in _META.items():
        rows.append(
            f'html body .stApp .st-key-stn_{key} button::before{{content:"";position:absolute;left:10px;top:50%;transform:translateY(-50%);'
            f'width:32px;height:32px;border-radius:10px;background:{_uri(icon)} center/17px no-repeat,linear-gradient(135deg,{col},color-mix(in srgb,{col} 68%,#000));'
            f'box-shadow:0 6px 14px color-mix(in srgb,{col} 32%,transparent);}}')
    for i, (_, hexv) in enumerate(_PRESETS):
        ring = f"box-shadow:0 0 0 3px {card},0 0 0 5px {hexv} !important;transform:scale(1.04);" if hexv.lower() == cur_accent.lower() else ""
        rows.append(f'html body .stApp .st-key-stac_{i} button{{background:{hexv} !important;{ring}}}'
                    f'html body .stApp .st-key-stac_{i} button:hover{{transform:scale(1.12);}}')
    chev = _uri("chev", soft, 2.2)
    st.markdown(f"""<style>
{chr(10).join(rows)}
html body .stApp .stg-hero{{position:relative;overflow:hidden;border-radius:26px;padding:1.5rem 1.6rem;margin:0 0 1.2rem;color:#fff;display:flex;align-items:center;gap:16px;
  background:radial-gradient(120% 140% at 100% 0%,color-mix(in srgb,{acc} 55%,#fff 0%),transparent 60%),linear-gradient(135deg,{accd},{acc});
  box-shadow:0 18px 40px color-mix(in srgb,{acc} 32%,transparent);}}
html body .stApp .stg-hero::after{{content:"";position:absolute;right:-60px;top:-70px;width:230px;height:230px;border-radius:50%;background:rgba(255,255,255,.10);}}
html body .stApp .stg-hico{{width:56px;height:56px;border-radius:18px;display:flex;align-items:center;justify-content:center;flex:none;background:rgba(255,255,255,.18);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.28);}}
html body .stApp .stg-ht{{font-family:'Sora',sans-serif;font-weight:800;font-size:1.65rem;letter-spacing:-.03em;color:#fff !important;line-height:1.1;}}
html body .stApp .stg-hs{{color:rgba(255,255,255,.86) !important;font-size:.93rem;margin-top:.25rem;}}
html body .stApp .stg-chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:.7rem;position:relative;z-index:1;}}
html body .stApp .stg-chip{{display:inline-flex;align-items:center;gap:6px;padding:.28rem .7rem;border-radius:999px;font-size:.76rem;font-weight:700;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.28);color:#fff !important;}}
/* ── navigation ── */
html body .stApp div[data-testid="stColumn"]:has(.st-key-st_nav){{align-self:flex-start;position:sticky;top:4.2rem;}}
{_P}.st-key-st_nav{{gap:.3rem !important;}}
html body .stApp .stg-cap{{font-size:.68rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:{soft} !important;margin:1.1rem 0 .35rem .5rem;padding-bottom:.5rem;}}
html body .stApp .st-key-st_nav [data-testid="stTextInput"] input{{border-radius:14px !important;background:{flat} !important;border:1px solid {line} !important;}}
html body .stApp [class*="st-key-stn_"] button{{position:relative;width:100%;min-height:52px;border-radius:16px !important;border:1px solid transparent !important;background:transparent !important;
  box-shadow:none !important;justify-content:flex-start !important;text-align:left !important;padding:.5rem .9rem .5rem 56px !important;transition:background .15s,border-color .15s,transform .15s;}}
html body .stApp [class*="st-key-stn_"] button > div, html body .stApp [class*="st-key-stn_"] button [data-testid="stMarkdownContainer"]{{width:100% !important;justify-content:flex-start !important;text-align:left !important;}}
html body .stApp [class*="st-key-stn_"] button p{{text-align:left !important;font-weight:700 !important;font-size:.98rem !important;color:{ink} !important;margin:0;}}
html body .stApp [class*="st-key-stn_"] button:hover{{background:{flat} !important;}}
html body .stApp [class*="st-key-stn_"] button[data-testid="stBaseButton-primary"]{{background:color-mix(in srgb,{acc} 13%,transparent) !important;border-color:color-mix(in srgb,{acc} 45%,transparent) !important;}}
html body .stApp [class*="st-key-stn_"] button[data-testid="stBaseButton-primary"] p{{color:{acc} !important;}}
html body .stApp [class*="st-key-stn_"] button::after{{content:"";position:absolute;right:14px;top:50%;width:16px;height:16px;transform:translateY(-50%);background:{chev} center/contain no-repeat;opacity:0;}}
/* ── cartes ── */
{_P}[class*="st-key-stc_"]{{background:{card} !important;border:1px solid {line} !important;border-radius:22px !important;padding:1.15rem 1.25rem 1.25rem !important;gap:.55rem !important;
  box-shadow:{t["shadow"]} !important;margin-bottom:1rem;}}
html body .stApp .stg-ch{{display:flex;align-items:center;gap:12px;margin-bottom:1.1rem;}}
html body .stApp .stg-lis{{margin-bottom:1.2rem;}}
html body .stApp .st-key-st_del button:not([disabled]){{background:linear-gradient(135deg,#B91C1C,#EF4444) !important;}}
html body .stApp .stg-ci{{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex:none;color:#fff;
  background:linear-gradient(135deg,var(--c),color-mix(in srgb,var(--c) 66%,#000));box-shadow:0 8px 18px color-mix(in srgb,var(--c) 30%,transparent);}}
html body .stApp .stg-ch b{{display:block;font-family:'Sora',sans-serif;font-size:1.02rem;font-weight:800;letter-spacing:-.01em;color:{ink} !important;line-height:1.2;}}
html body .stApp .stg-ch small{{display:block;color:{soft} !important;font-size:.82rem;margin-top:2px;}}
html body .stApp .stg-sec{{display:flex;align-items:center;gap:14px;margin:0 0 1rem;}}
html body .stApp .stg-sec .stg-ci{{width:46px;height:46px;border-radius:15px;}}
html body .stApp .stg-sec b{{font-family:'Sora',sans-serif;font-size:1.5rem;font-weight:800;letter-spacing:-.03em;color:{ink} !important;display:block;line-height:1.15;}}
html body .stApp .stg-sec small{{color:{soft} !important;font-size:.9rem;}}
/* thème : tuiles */
{_P}.st-key-stc_theme [data-testid="stHorizontalBlock"]{{gap:.8rem !important;}}
html body .stApp [class*="st-key-st_th_"] button{{min-height:116px !important;height:116px !important;border-radius:18px !important;align-items:flex-end !important;justify-content:flex-start !important;padding:.8rem 1rem !important;
  border:2px solid {line} !important;position:relative;overflow:hidden;}}
html body .stApp .st-key-st_th_light button{{background:linear-gradient(160deg,#FFFFFF 0%,#E8F0FB 100%) !important;}}
html body .stApp .st-key-st_th_dark button{{background:linear-gradient(160deg,#16223A 0%,#070C17 100%) !important;}}
html body .stApp [class*="st-key-st_th_"] button > div{{width:100% !important;justify-content:flex-start !important;text-align:left !important;}}
html body .stApp .st-key-st_th_light button p{{color:#0F1A2E !important;font-weight:800 !important;}}
html body .stApp .st-key-st_th_dark button p{{color:#F8FAFC !important;font-weight:800 !important;}}
html body .stApp [class*="st-key-st_th_"] button::before{{content:"";position:absolute;left:14px;top:14px;right:14px;height:26px;border-radius:9px;background:color-mix(in srgb,{acc} 80%,transparent);opacity:.9;}}
html body .stApp [class*="st-key-st_th_"] button::after{{content:"";position:absolute;left:14px;top:48px;width:55%;height:8px;border-radius:5px;background:rgba(128,128,128,.35);}}
html body .stApp [class*="st-key-st_th_"] button[data-testid="stBaseButton-primary"]{{border-color:{acc} !important;box-shadow:0 0 0 4px color-mix(in srgb,{acc} 22%,transparent) !important;}}
/* pastilles de couleur */
{_P}.st-key-stc_acc .st-key-st_sw{{flex-direction:row !important;flex-wrap:wrap;gap:14px !important;padding:.3rem .3rem .5rem;}}
{_P}.st-key-st_sw > div[data-testid="stElementContainer"]{{width:auto !important;flex:none !important;}}
html body .stApp [class*="st-key-stac_"] button{{width:36px !important;min-width:36px !important;height:36px !important;min-height:36px !important;padding:0 !important;border-radius:50% !important;border:none !important;transition:transform .15s,box-shadow .15s;}}
html body .stApp [class*="st-key-stac_"] button p{{font-size:0 !important;}}
/* aperçu typo */
html body .stApp .stg-prev{{border-radius:16px;padding:1rem 1.1rem;background:{flat};border-left:4px solid {acc};color:{ink} !important;}}
html body .stApp .stg-prev small{{display:block;color:{soft} !important;font-size:.72rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.35rem;}}
/* identité */
html body .stApp .stg-id{{display:flex;align-items:center;gap:16px;padding:.3rem 0 1rem;}}
html body .stApp .stg-id .big-avatar{{margin:0 !important;flex:none;}}
html body .stApp .stg-id b{{font-family:'Sora',sans-serif;font-size:1.15rem;color:{ink} !important;display:block;}}
html body .stApp .stg-id small{{color:{soft} !important;}}
/* listes / chips fonctionnalités */
html body .stApp .stg-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.6rem;}}
html body .stApp .stg-feat{{display:flex;align-items:center;gap:10px;padding:.65rem .8rem;border-radius:14px;background:{flat};font-weight:600;font-size:.9rem;color:{ink} !important;}}
html body .stApp .stg-feat i{{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex:none;font-style:normal;}}
html body .stApp .stg-feat.on i{{background:color-mix(in srgb,#10B981 20%,transparent);color:#10B981;}}
html body .stApp .stg-feat.off{{opacity:.55;}}
html body .stApp .stg-feat.off i{{background:rgba(128,128,128,.18);color:{soft};}}
html body .stApp .stg-plan{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:1.1rem 1.2rem;border-radius:18px;color:#fff;
  background:linear-gradient(135deg,{accd},{acc});box-shadow:0 14px 30px color-mix(in srgb,{acc} 30%,transparent);margin-bottom:1.3rem;}}
html body .stApp .stg-plan small{{color:rgba(255,255,255,.82) !important;font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:.7rem;display:block;}}
html body .stApp .stg-plan b{{font-family:'Sora',sans-serif;font-size:1.55rem;color:#fff !important;}}
html body .stApp .stg-stat{{text-align:right;color:#fff !important;}}
html body .stApp .stg-stat b{{font-size:1.9rem;display:block;line-height:1;}}
html body .stApp .stg-li{{display:flex;gap:10px;align-items:flex-start;padding:.35rem 0;color:{ink} !important;font-size:.93rem;}}
html body .stApp .stg-li i{{flex:none;color:#10B981;margin-top:2px;}}
html body .stApp .stg-soon{{text-align:center;padding:1.4rem .5rem .6rem;}}
html body .stApp .stg-soon .stg-ci{{width:64px;height:64px;border-radius:20px;margin:0 auto .8rem;}}
html body .stApp .stg-soon b{{font-family:'Sora',sans-serif;font-size:1.15rem;color:{ink} !important;display:block;}}
html body .stApp .stg-badge{{display:inline-block;margin:.5rem 0;padding:.2rem .7rem;border-radius:999px;font-size:.72rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;
  color:{acc} !important;background:color-mix(in srgb,{acc} 14%,transparent);}}
html body .stApp .stg-ext{{display:flex;align-items:center;gap:12px;padding:.8rem .9rem;border-radius:16px;background:{flat};margin-bottom:.5rem;}}
html body .stApp .stg-ext b{{color:{ink} !important;display:block;font-size:.95rem;}}
html body .stApp .stg-ext small{{color:{soft} !important;}}
html body .stApp .stg-ext .stg-badge{{margin:0 0 0 auto;color:#10B981 !important;background:color-mix(in srgb,#10B981 15%,transparent);}}
html body .stApp .stg-foot{{text-align:center;color:{soft} !important;font-size:.78rem;margin:1rem 0 .4rem;}}
html body .stApp .st-key-st_back{{display:none;}}
/* ── mobile : liste → section ── */
@media (max-width:768px){{
  html body .stApp div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-st_nav){{flex-direction:column !important;gap:0 !important;}}
  html body .stApp div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] .st-key-st_nav) > div[data-testid="stColumn"]{{width:100% !important;min-width:100% !important;flex:1 1 100% !important;position:static;}}
  html body .stApp:has(.stg-open) div[data-testid="stColumn"]:has(.st-key-st_nav){{display:none !important;}}
  html body .stApp:has(.stg-list) div[data-testid="stColumn"]:has(.st-key-st_body){{display:none !important;}}
  html body .stApp:has(.stg-open) .stg-hero{{display:none;}}
  html body .stApp .stg-hero{{padding:1.1rem 1.15rem;border-radius:22px;}}
  html body .stApp .stg-ht{{font-size:1.35rem;}}
  html body .stApp .stg-hico{{width:46px;height:46px;border-radius:15px;}}
  html body .stApp [class*="st-key-stn_"] button{{min-height:64px;background:{card} !important;border:1px solid {line} !important;box-shadow:{t["shadow"]} !important;}}
  html body .stApp [class*="st-key-stn_"] button::before{{left:14px;width:38px;height:38px;border-radius:12px;background-size:19px,auto !important;}}
  html body .stApp [class*="st-key-stn_"] button{{padding-left:68px !important;}}
  html body .stApp [class*="st-key-stn_"] button::after{{opacity:.8;}}
  html body .stApp .st-key-st_back{{display:block;position:sticky;top:3.4rem;z-index:20;margin-bottom:.6rem;}}
  html body .stApp .st-key-st_back button{{border-radius:999px !important;padding:.35rem 1rem .35rem 2.1rem !important;background:{card} !important;border:1px solid {line} !important;
     box-shadow:{t["shadow"]} !important;position:relative;min-height:0;width:auto;}}
  html body .stApp .st-key-st_back button::before{{content:"";position:absolute;left:11px;top:50%;width:16px;height:16px;transform:translateY(-50%);background:{_uri("back", acc, 2.4)} center/contain no-repeat;}}
  html body .stApp .st-key-st_back button p{{color:{acc} !important;font-weight:800 !important;}}
  {_P}[class*="st-key-stc_"]{{padding:1rem 1rem 1.1rem !important;border-radius:20px !important;}}
  html body .stApp .stg-sec b{{font-size:1.3rem;}}
}}
</style>""", unsafe_allow_html=True)


# ───────────────────────── éléments communs ─────────────────────────
def _head(key: str, title: str, desc: str = "") -> None:
    icon, col = _META.get(key, ("sliders", "#3B82F6"))
    st.markdown(f'<div class="stg-ch"><span class="stg-ci" style="--c:{col}">{_svg(icon, 19)}</span><div><b>{title}</b>'
                + (f'<small>{desc}</small>' if desc else '') + '</div></div>', unsafe_allow_html=True)


def _chead(icon: str, col: str, title: str, desc: str = "") -> None:
    st.markdown(f'<div class="stg-ch"><span class="stg-ci" style="--c:{col}">{_svg(icon, 19)}</span><div><b>{title}</b>'
                + (f'<small>{desc}</small>' if desc else '') + '</div></div>', unsafe_allow_html=True)


def _soon(key: str, title: str, items: list, L: dict) -> None:
    icon, col = _META[key]
    with _keyed(f"stc_{key}"):
        st.markdown(f'<div class="stg-soon"><span class="stg-ci" style="--c:{col}">{_svg(icon, 28)}</span><b>{L["soon_t"]}</b>'
                    f'<span class="stg-badge">{L["soon"]}</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="stg-lis">' + "".join(f'<div class="stg-li"><i>{_svg("check", 16)}</i><span>{x}</span></div>' for x in items) + '</div>', unsafe_allow_html=True)


# ───────────────────────── sections ─────────────────────────
def _sec_general(ctx, L):
    ss = st.session_state
    with _keyed("stc_theme"):
        _chead("palette", "#3B82F6", L["theme"], L["theme_d"])
        c1, c2 = st.columns(2)
        with c1:
            if st.button(T("light"), key="st_th_light", use_container_width=True, type="primary" if ss.theme == "light" else "secondary") and ss.theme != "light":
                ss.theme = "light"; ctx["set_cookie"]("ys_theme", "light", max_age=365 * 24 * 3600); st.rerun()
        with c2:
            if st.button(T("dark"), key="st_th_dark", use_container_width=True, type="primary" if ss.theme == "dark" else "secondary") and ss.theme != "dark":
                ss.theme = "dark"; ctx["set_cookie"]("ys_theme", "dark", max_age=365 * 24 * 3600); st.rerun()
    with _keyed("stc_acc"):
        _chead("spark", "#8B5CF6", L["accent"], L["accent_d"])
        with _keyed("st_sw"):
            for i, (name, hexv) in enumerate(_PRESETS):
                st.button(name, key=f"stac_{i}", help=name, on_click=_accent, args=(hexv, ctx["save_appearance"]))
        cur = ss.get("cfg_accent", "#2E6DB4")
        hx = st.color_picker(T("custom_color"), value=cur)
        if hx != cur:
            ss.cfg_accent = hx; ctx["save_appearance"](); st.rerun()
    with _keyed("stc_lang"):
        _chead("globe", "#06B6D4", T("language"), L["lang_d"])
        cur_lang = ss.cfg_lang
        keys = list(LANGS.keys())
        cl = st.selectbox(T("language"), keys, index=keys.index(cur_lang) if cur_lang in LANGS else 0, format_func=lambda l: LANGS[l],
                          key="sel_lang", label_visibility="collapsed")
        if cl != cur_lang:
            ctx["set_language"](cl)
        _ui = LANGS.get(ss.cfg_lang, "fr"); _tgt = LANGS.get(ss.cfg_target, "fr")
        st.info(f"🌐 **{_ui}** — {T('language')} ✓ | {T('chip_tr')} {T('m_analyse')} → **{_tgt}**")
    with _keyed("stc_typo"):
        _chead("type", "#F97316", L["typo"], L["typo_d"])
        st.selectbox(T("font"), ["Manrope", "Sora", "Système", "Adapté aux dyslexiques"], key="cfg_font")
        s1, s2 = st.columns(2)
        with s1:
            st.slider(T("text_size"), 14, 20, int(ss.get("cfg_font_size", 16)), key="cfg_font_size", on_change=ctx["save_appearance"])
        with s2:
            st.slider(T("line_height"), 1.4, 2.0, float(ss.get("cfg_line_height", 1.6)), key="cfg_line_height", on_change=ctx["save_appearance"])
        st.toggle(T("motion"), key="cfg_reduce_motion")
        st.markdown(f'<div class="stg-prev" style="font-size:{int(ss.cfg_font_size)}px;line-height:{ss.cfg_line_height}"><small>{T("preview")} · '
                    f'{ss.cfg_accent} · {int(ss.cfg_font_size)} px · {ss.cfg_line_height}</small>{L["sample"]}</div>', unsafe_allow_html=True)


def _sec_compte(ctx, L):
    ss = st.session_state
    user, role = ctx["user"], ctx["role"]
    with _keyed("stc_profile"):
        _chead("user", "#8B5CF6", L["identity"], L["identity_d"])
        av = ctx["get_avatar_b64"](user)
        face = f'<img src="{av}" class="big-avatar">' if av else f'<div class="big-avatar">{user[:2].upper()}</div>'
        st.markdown(f'<div class="stg-id">{face}<div><b>{user}</b><small>{L["role"]} : {role} · {ctx["plan_name"]}</small></div></div>', unsafe_allow_html=True)
        up = st.file_uploader(L["photo"], type=["png", "jpg", "jpeg", "webp"])
        if up:
            from src.core.avatar_store import save_avatar
            _sig = f"{up.name}:{up.size}"
            if ss.get("_av_sig") != _sig:  # évite de ré-enregistrer (et de boucler) à chaque rerun
                save_avatar(user, up.getvalue(), up.name); ss["_av_sig"] = _sig
                ctx["fast_clear"](); st.success(L["photo_ok"]); st.rerun()
        a, b = st.columns(2)
        with a:
            st.text_input(T("fullname"), key="prof_fullname")
        with b:
            st.text_input(T("callname"), key="prof_callname")
        st.selectbox(T("job"), ["Étudiant", "Enseignant", "Créateur de contenu", "Professionnel", "Autre"], key="prof_job")
        st.text_area(T("instructions"), key="prof_instructions", placeholder="ex. : garder les explications brèves")
    with _keyed("stc_security"):
        _chead("key", "#EC4899", L["security"], L["security_d"])
        if st.button(T("change_pwd"), key="st_pwd", use_container_width=True):
            ss.page = "profil"; st.rerun()


def _sec_notifications(ctx, L):
    with _keyed("stc_notifs"):
        _chead("bell", "#F59E0B", T("notif_pref"), L["notifs_d"])
        st.toggle(T("completion"), key="cfg_notif_complete")
        st.toggle(T("weekly"), key="cfg_notif_weekly")


def _sec_confidentialite(ctx, L):
    ss = st.session_state
    user = ctx["user"]
    with _keyed("stc_rgpd"):
        _chead("shield", "#10B981", L["rgpd"], "RGPD ✓")
        st.markdown('<div class="stg-lis">' + "".join(f'<div class="stg-li"><i>{_svg("check", 16)}</i><span>{L[k]}</span></div>' for k in ("rgpd1", "rgpd2", "rgpd3")) + '</div>', unsafe_allow_html=True)
        if st.button(T("see_policy"), key="st_policy", use_container_width=True):
            ss.show_privacy = True; st.rerun()
    with _keyed("stc_data"):
        _chead("download", "#3B82F6", L["mydata"], L["mydata_d"])
        try:
            hist = ctx["get_history"](user)
        except Exception:
            hist = []
        payload = {"user": user, "exported_at": datetime.now().isoformat(timespec="seconds"), "plan": ctx["plan_name"],
                   "settings": {k: ss.get(k) for k in ("cfg_lang", "cfg_target", "cfg_accent", "cfg_font", "cfg_font_size", "cfg_line_height",
                                                       "cfg_model", "cfg_turbo", "cfg_kw_n", "cfg_q_n", "cfg_chunk")},
                   "history": hist}
        st.download_button(L["export"], data=json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8"),
                           file_name=f"videoscribe_{user}.json", mime="application/json", key="st_export", use_container_width=True)
    with _keyed("stc_danger"):
        _chead("trash", "#EF4444", L["danger"], L["danger_d"])
        ok = st.checkbox(L["confirm_del"], key="st_del_ok")
        if st.button(L["del"], key="st_del", use_container_width=True, disabled=not ok):
            ctx["clear_history"](user); ss.st_del_ok = False; st.toast(L["del_ok"]); st.rerun()


def _sec_facturation(ctx, L):
    tier = ctx["tier"]
    try:
        n = ctx["count_today"](ctx["user"])
    except Exception:
        n = None
    with _keyed("stc_plan"):
        stat = f'<div class="stg-stat"><b>{n}</b><small>{L["today"]}</small></div>' if n is not None else ""
        st.markdown(f'<div class="stg-plan"><div><small>{L["plan"]}</small><b>{ctx["plan_name"]}</b></div>{stat}</div>', unsafe_allow_html=True)
        if st.button(T("manage_plan"), key="st_manage", use_container_width=True, type="primary"):
            st.session_state.page = "premium"; st.rerun()
    feats = [("f_analyse", 0), ("f_search", 2), ("f_quality", 2), ("f_tldr", 3), ("f_actions", 3), ("f_slides", 3), ("f_chat", 3), ("f_lang", 3)]
    with _keyed("stc_feats"):
        _chead("star", "#F59E0B", L["included"], L["locked"])
        st.markdown('<div class="stg-grid">' + "".join(
            f'<div class="stg-feat {"on" if tier >= need else "off"}"><i>{_svg("check" if tier >= need else "lock", 14, sw=2.4)}</i>{L[k]}</div>'
            for k, need in feats) + '</div>', unsafe_allow_html=True)


def _sec_capacites(ctx, L):
    tier = ctx["tier"]
    with _keyed("stc_engine"):
        _chead("cpu", "#06B6D4", L["engine"], L["engine_d"])
        if tier >= 2:
            st.selectbox(T("model"), ["rapide", "qualite"], key="cfg_model", format_func=lambda m: "Rapide" if m == "rapide" else "Qualité")
        else:
            st.markdown(f"<div class='q-item'>{_svg('lock', 14)} {L['locked_q']}</div>", unsafe_allow_html=True)
        st.toggle(T("turbo"), key="cfg_turbo")
    with _keyed("stc_qty"):
        _chead("sliders", "#8B5CF6", L["qty"], L["qty_d"])
        st.slider(T("kw_count"), 5, 20, key="cfg_kw_n")
        st.slider(T("q_count"), 3, 10, key="cfg_q_n")
        st.slider(T("chunk_size"), 1200, 4000, step=200, key="cfg_chunk")
    with _keyed("stc_out"):
        _chead("note", "#F97316", L["out"], L["out_d"])
        st.toggle(T("extract_kw"), key="cfg_kw")
        st.toggle(T("gen_q"), key="cfg_qa")
    with _keyed("stc_voice"):
        _chead("mic", "#EC4899", T("voice"), L["voice_d"])
        a, b = st.columns(2)
        with a:
            st.selectbox(T("language"), ["fr", "en", "es", "de"], key="cfg_voice_lang", format_func=lambda l: LANGS[l])
        with b:
            st.selectbox(T("speed"), ["Lent", "Normal", "Rapide"], key="cfg_voice_speed")
        st.selectbox(T("style"), ["Normal", "Décontracté", "Professionnel"], key="cfg_voice_style")


def _sec_extensions(ctx, L):
    with _keyed("stc_ext"):
        _chead("tool", "#F97316", L["ext_t"], L["ext_d"])
        for icon, col, name, d in (("note", "#8B5CF6", "Obsidian", L["ext_obs"]), ("note", "#111827", "Notion", L["ext_not"]),
                                   ("film", "#EF4444", "PDF", L["ext_pdf"]), ("code", "#3B82F6", "Markdown", L["ext_md"])):
            st.markdown(f'<div class="stg-ext"><span class="stg-ci" style="--c:{col}">{_svg(icon, 18)}</span><div><b>{name}</b><small>{d}</small></div>'
                        f'<span class="stg-badge">{L["available"]}</span></div>', unsafe_allow_html=True)


_SOON = {"connecteurs": "p_connect", "plugins": "p_plugins", "developpeur": "p_dev", "competences": "p_skills", "memoire": "p_memory"}
_RENDER = {"general": _sec_general, "compte": _sec_compte, "notifications": _sec_notifications, "confidentialite": _sec_confidentialite,
           "facturation": _sec_facturation, "capacites": _sec_capacites, "extensions": _sec_extensions}


# ───────────────────────── point d'entrée ─────────────────────────
def render_settings(ctx: dict) -> None:
    ss = st.session_state
    L = _l()
    ss.setdefault("cfg_open", False)
    sec = ss.get("cfg_section", "general")
    if sec == "bureau" or sec not in _META:
        sec = ss.cfg_section = "general"
    _css(sec, ss.get("cfg_accent", "#2E6DB4"))

    t = ctx["plan_name"]
    st.markdown(f'<div class="stg-hero"><span class="stg-hico">{_svg("sliders", 28, "#fff")}</span><div style="position:relative;z-index:1">'
                f'<div class="stg-ht">{T("set_title")}</div><div class="stg-hs">{T("set_sub")}</div>'
                f'<div class="stg-chips"><span class="stg-chip">{_svg("user", 13, "#fff", 2.2)} {ctx["user"]}</span>'
                f'<span class="stg-chip">{_svg("star", 13, "#fff", 2.2)} {t}</span></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stg-{"open" if ss.cfg_open else "list"}" style="display:none"></div>', unsafe_allow_html=True)

    c_nav, c_body = st.columns([1, 2.5], gap="large")
    with c_nav:
        with _keyed("st_nav"):
            q = st.text_input(T("set_search"), placeholder=T("set_search"), label_visibility="collapsed", key="cfg_q").strip().lower()
            shown = 0
            for gname, items in _groups(L):
                vis = [(k, lab) for k, lab in items if not q or q in lab.lower()]
                if not vis:
                    continue
                st.markdown(f'<div class="stg-cap">{gname}</div>', unsafe_allow_html=True)
                for k, lab in vis:
                    shown += 1
                    st.button(lab, key=f"stn_{k}", on_click=_open, args=(k,), use_container_width=True, type="primary" if sec == k else "secondary")
            if not shown:
                st.caption("—")
    with c_body:
        with _keyed("st_body"):
            st.button(L["back"], key="st_back", on_click=_back)
            label = dict(x for _, its in _groups(L) for x in its).get(sec, sec)
            icon, col = _META[sec]
            st.markdown(f'<div class="stg-sec"><span class="stg-ci" style="--c:{col}">{_svg(icon, 22)}</span><div><b>{label}</b>'
                        f'<small>{L.get("d_" + sec, "")}</small></div></div>', unsafe_allow_html=True)
            if sec in _RENDER:
                _RENDER[sec](ctx, L)
            else:
                _soon(sec, label, L[_SOON[sec]], L)
    st.markdown(f'<div class="stg-foot">{L["version"]}</div>', unsafe_allow_html=True)