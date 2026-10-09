"""
Pages publiques — Accessibles sans connexion.

Contient :
- render_home() : Page d'accueil marketing
- render_about() : Page À propos
- render_privacy(show_back=True) : Politique de confidentialité
- render_contact() : Page Contact
- render_landing() : Landing page alternative

Extrait de app.py pour alléger le fichier principal (~810 lignes).

Usage:
    from src.pages.public import render_home, render_about
"""

import time
import streamlit as st
import streamlit.components.v1 as _components
from pathlib import Path

from src.ui.i18n import T, LANGS
from src.ui.components import ic, logo_html, STARS
from src.ui.layout import hero, render_navbar, render_footer, notify_admins
from src.core.config import CONTACT_EMAIL, PAYMENT_WAVE, MAP_EMBED, MAP_LINK, DEMO_VIDEO_URL
from src.user_manager import list_users
from src.contact_manager import save_message
from src.email_manager import send_contact_message, send_contact_ack


# ⚠️ Les fonctions ci-dessous seront copiées automatiquement par extract_public.py
# render_home(), render_about(), render_privacy(), render_contact(), render_landing()

def render_home():
    st.markdown("""
    <style>
    .vs-home-hero {
        position: relative; overflow: hidden; border-radius: 34px;
        padding: clamp(2.5rem, 6vw, 5rem) clamp(1.5rem, 5vw, 4rem) clamp(2rem, 5vw, 3.5rem);
        margin: .4rem 0 2rem; isolation: isolate;
        background:
            radial-gradient(900px 500px at 15% 0%, rgba(59,130,246,.35), transparent 60%),
            radial-gradient(800px 480px at 85% 5%, rgba(16,185,129,.28), transparent 60%),
            radial-gradient(700px 400px at 50% 100%, rgba(212,175,55,.18), transparent 65%),
            linear-gradient(160deg, #05080F 0%, #0A1220 45%, #0D1524 100%);
        border: 1px solid rgba(255,255,255,.10);
        box-shadow: 0 40px 100px rgba(2,8,18,.45), inset 0 1px 0 rgba(255,255,255,.06);
    }
    .vs-home-hero::before {
        content:""; position:absolute; inset:0; z-index:0;
        background-image:
            linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
        background-size: 44px 44px;
        mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
        -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
        pointer-events:none;
    }
    .vs-home-hero::after {
        content:""; position:absolute; top:0; left:15%; right:15%; height:1px; z-index:1;
        background: linear-gradient(90deg, transparent, rgba(96,165,250,.6), rgba(52,211,153,.6), transparent);
    }
    .vs-hero-inner { position:relative; z-index:2; max-width: 1100px; margin: 0 auto; text-align:center; }
    .vs-hero-eyebrow {
        display:inline-flex; align-items:center; gap:9px; padding:7px 16px 7px 12px; border-radius:999px;
        background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.14);
        color:rgba(241,245,249,.85) !important; font-size:.76rem; font-weight:800;
        letter-spacing:.14em; text-transform:uppercase; margin-bottom:1.4rem;
    }
    .vs-hero-eyebrow .dot {
        width:6px; height:6px; border-radius:50%; background:#34D399;
        box-shadow:0 0 0 0 rgba(52,211,153,.6); animation: vsPulse 2.2s ease-out infinite;
    }
    @keyframes vsPulse {
        0%{box-shadow:0 0 0 0 rgba(52,211,153,.55);}
        70%{box-shadow:0 0 0 9px rgba(52,211,153,0);}
        100%{box-shadow:0 0 0 0 rgba(52,211,153,0);}
    }
    .vs-hero-h1 {
        font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.045em; line-height:1.03;
        font-size: clamp(2.2rem, 5.4vw, 4.5rem); color:#F8FAFC !important; margin:0 0 1.3rem;
    }
    .vs-hero-h1 .grad {
        background: linear-gradient(92deg,#60A5FA 0%,#34D399 45%,#FBBF24 100%);
        -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    }
    .vs-hero-sub {
        color: rgba(226,232,240,.78) !important; max-width: 680px; margin: 0 auto 2rem;
        font-size: clamp(1rem, 1.35vw, 1.18rem); line-height: 1.75;
    }
    .vs-hero-trust {
        display:flex; flex-wrap:wrap; justify-content:center; gap: 1.6rem;
        padding-top: 1.8rem; border-top: 1px solid rgba(255,255,255,.08);
    }
    .vs-hero-trust-item {
        display:flex; align-items:center; gap:8px; color: rgba(148,163,184,.95) !important;
        font-size:.82rem; font-weight:600;
    }
    .vs-hero-trust-item b { color:#F8FAFC !important; font-weight:800; }
    .vs-hero-mockup {
        position:relative; margin: 2.4rem auto 0; max-width: 640px;
        background: rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.10);
        border-radius:22px; padding:1rem 1rem .4rem; backdrop-filter: blur(20px);
        box-shadow: 0 30px 80px rgba(0,0,0,.5);
        animation: vsFloat 6s ease-in-out infinite;
    }
    @keyframes vsFloat {
        0%,100%{transform:translateY(0);} 50%{transform:translateY(-10px);}
    }
    .vs-mockup-head {
        display:flex; align-items:center; gap:8px; padding: .3rem .4rem .7rem;
        border-bottom:1px solid rgba(255,255,255,.08); margin-bottom:.7rem;
    }
    .vs-mockup-dots { display:flex; gap:5px; }
    .vs-mockup-dots span { width:10px; height:10px; border-radius:50%; }
    .vs-mockup-dots span:nth-child(1){background:#EF4444;}
    .vs-mockup-dots span:nth-child(2){background:#F59E0B;}
    .vs-mockup-dots span:nth-child(3){background:#22C55E;}
    .vs-mockup-url {
        flex:1; text-align:center; color:rgba(148,163,184,.9) !important;
        font-size:.74rem; font-family:monospace;
    }
    .vs-mockup-row {
        display:flex; align-items:center; gap:10px; padding:.7rem .8rem;
        background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.07);
        border-radius:12px; margin-bottom:.5rem; text-align:left;
    }
    .vs-mockup-row .chip {
        width:32px; height:32px; border-radius:9px; flex-shrink:0;
        display:flex; align-items:center; justify-content:center; color:#fff !important;
    }
    .vs-mockup-row .chip.b { background: linear-gradient(135deg,#3B82F6,#60A5FA); }
    .vs-mockup-row .chip.g { background: linear-gradient(135deg,#10B981,#34D399); }
    .vs-mockup-row .chip.y { background: linear-gradient(135deg,#D4AF37,#F0D488); }
    .vs-mockup-row .txt { flex:1; }
    .vs-mockup-row .txt b { color:#F8FAFC !important; font-size:.84rem; display:block; }
    .vs-mockup-row .txt small { color:rgba(148,163,184,.9) !important; font-size:.72rem; }
    .vs-mockup-row .ok { color:#34D399 !important; font-weight:800; font-size:.75rem; }
    .vs-steps { position:relative; padding-left: 1.5rem; margin-top: 1.2rem; }
    .vs-steps::before {
        content:""; position:absolute; left: 19px; top: 14px; bottom: 14px; width:2px;
        background: linear-gradient(180deg, #3B82F6, #10B981, #D4AF37);
        border-radius:2px; opacity:.5;
    }
    .vs-step-item { position:relative; padding: 0 0 1.4rem 3.6rem; }
    .vs-step-item:last-child { padding-bottom: 0; }
    .vs-step-num {
        position:absolute; left:0; top:0; width:42px; height:42px; border-radius:13px;
        display:flex; align-items:center; justify-content:center;
        font-family:'Sora',sans-serif; font-weight:800; font-size:.9rem;
        background: linear-gradient(135deg,#0F172A,#1E293B);
        border:1px solid rgba(96,165,250,.35); color:#60A5FA !important;
        box-shadow: 0 10px 24px rgba(59,130,246,.18);
    }
    .vs-step-item h4 {
        font-family:'Sora',sans-serif; font-weight:800; color:#F8FAFC !important;
        margin: .35rem 0 .3rem; font-size:1.05rem;
    }
    .vs-step-item p { color: rgba(203,213,225,.8) !important; font-size:.9rem; line-height:1.6; }
    .vs-final-cta {
        position:relative; overflow:hidden; border-radius:30px; padding: 3.2rem 2.4rem;
        margin: 2.6rem 0 1rem; text-align:center; isolation:isolate;
        background:
            radial-gradient(700px 300px at 20% 0%, rgba(59,130,246,.35), transparent 60%),
            radial-gradient(600px 300px at 80% 100%, rgba(16,185,129,.30), transparent 60%),
            linear-gradient(135deg, #05080F, #0D1524);
        border:1px solid rgba(255,255,255,.12);
        box-shadow: 0 30px 80px rgba(2,8,18,.5);
    }
    .vs-final-cta h3 {
        font-family:'Sora',sans-serif; font-weight:800; color:#F8FAFC !important;
        font-size: clamp(1.7rem, 3.2vw, 2.6rem); margin-bottom: .8rem; letter-spacing:-.03em;
    }
    .vs-final-cta p {
        color: rgba(203,213,225,.85) !important; max-width: 620px; margin: 0 auto 1.8rem;
        font-size: 1.02rem; line-height: 1.7;
    }
    .vs-final-badges { display:flex; flex-wrap:wrap; gap:.6rem; justify-content:center; margin-bottom:2rem; }
    .vs-final-badges span {
        padding: 7px 15px; border-radius:999px; background: rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.15); color: rgba(241,245,249,.9) !important;
        font-size:.82rem; font-weight:700;
    }
    .vs-faq-item {
        border:1px solid rgba(255,255,255,.09); border-radius:16px; margin-bottom:.6rem;
        background: rgba(255,255,255,.025); overflow:hidden;
    }
    .vs-faq-q {
        display:flex; align-items:center; gap:12px; padding:1rem 1.2rem; cursor:pointer;
        font-weight:700; color:#F8FAFC !important; font-size:.94rem;
    }
    .vs-faq-q::after {
        content:"+"; margin-left:auto; font-size:1.3rem; color:#60A5FA !important;
        transition: transform .3s ease; font-weight:400;
    }
    details[open] .vs-faq-q::after { transform: rotate(45deg); }
    .vs-faq-a {
        padding: 0 1.2rem 1.1rem 3.1rem;
        color: rgba(203,213,225,.82) !important; font-size:.88rem; line-height:1.7;
    }
    @media (max-width: 900px) {
        .vs-hero-trust { gap: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vs-home-hero">
        <div class="vs-hero-inner">
            <div class="vs-hero-eyebrow">
                <span class="dot"></span>
                {ic("spark", 13)} VideoScribe AI — Nouvelle génération
            </div>
            <h1 class="vs-hero-h1">
                Transformez chaque vidéo YouTube<br>
                en <span class="grad">notes exploitables</span>
            </h1>
            <p class="vs-hero-sub">
                Collez un lien, obtenez en ~60 secondes un résumé structuré, des mots-clés,
                des questions, des flashcards, un quiz et des exports professionnels — en 4 langues.
            </p>
            <div class="vs-hero-trust">
                <span class="vs-hero-trust-item">{ic("check", 14)} <b>Sans carte bancaire</b></span>
                <span class="vs-hero-trust-item">{ic("check", 14)} <b>3 analyses/jour</b> offertes</span>
                <span class="vs-hero-trust-item">{ic("check", 14)} <b>RGPD</b> — données jamais revendues</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _c1, _c2, _c3 = st.columns([1, 1.15, 1])
    with _c2:
        _b1, _b2 = st.columns(2)
        with _b1:
            if st.button(f"{T('register')} →", type="primary", use_container_width=True, key="home_cta_register"):
                st.session_state.page = "register"; st.rerun()
        with _b2:
            if st.button("Voir la démo", use_container_width=True, key="home_cta_demo"):
                st.session_state.scroll_demo = True; st.rerun()

    st.markdown(f"""
    <div class="vs-hero-mockup">
        <div class="vs-mockup-head">
            <div class="vs-mockup-dots"><span></span><span></span><span></span></div>
            <div class="vs-mockup-url">videoscribe.ai/studio</div>
        </div>
        <div class="vs-mockup-row">
            <div class="chip b">{ic("link", 15)}</div>
            <div class="txt"><b>youtube.com/watch?v=dQw4…</b><small>Vidéo détectée — 12 min</small></div>
            <span class="ok">OK</span>
        </div>
        <div class="vs-mockup-row">
            <div class="chip g">{ic("cpu", 15)}</div>
            <div class="txt"><b>Résumé IA en cours…</b><small>Modèle BART-large — 7 sections</small></div>
            <span class="ok">59 s</span>
        </div>
        <div class="vs-mockup-row">
            <div class="chip y">{ic("download", 15)}</div>
            <div class="txt"><b>Export prêt</b><small>PDF · Markdown · Anki · Obsidian</small></div>
            <span class="ok">✓</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-stats" style="border:none; margin-top:1rem;">
        <div class="g-stat"><b>+1 000</b><span>vidéos résumées</span></div>
        <div class="g-stat"><b>~60 s</b><span>par analyse</span></div>
        <div class="g-stat"><b>4,9/5</b><span>satisfaction</span></div>
        <div class="g-stat"><b>0</b><span>donnée revendue</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">Comment ça marche</div>
    <div class="g-h2">4 étapes. Zéro friction.</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _s1, _s2 = st.columns([1.2, 1], gap="large")
    with _s1:
        st.markdown(f"""
        <div class="vs-steps">
            <div class="vs-step-item">
                <div class="vs-step-num">01</div>
                <h4>Collez l'URL YouTube</h4>
                <p>N'importe quelle vidéo publique, dans n'importe quelle langue. Détection automatique.</p>
            </div>
            <div class="vs-step-item">
                <div class="vs-step-num">02</div>
                <h4>L'IA analyse et résume</h4>
                <p>Extraction des sous-titres, découpage intelligent, résumé section par section en ~60 s.</p>
            </div>
            <div class="vs-step-item">
                <div class="vs-step-num">03</div>
                <h4>Enrichissez vos notes</h4>
                <p>Mots-clés, questions, flashcards Anki, quiz interactif, points d'action.</p>
            </div>
            <div class="vs-step-item">
                <div class="vs-step-num">04</div>
                <h4>Exportez partout</h4>
                <p>PDF, Markdown, Obsidian, Notion, Anki, présentation HTML — en un clic.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with _s2:
        st.markdown(f"""
        <div class="vs-hero-mockup" style="margin-top:.5rem;">
            <div class="vs-mockup-head">
                <div class="vs-mockup-dots"><span></span><span></span><span></span></div>
                <div class="vs-mockup-url">videoscribe.ai/result</div>
            </div>
            <div class="vs-mockup-row">
                <div class="chip b">{ic("file", 15)}</div>
                <div class="txt"><b>Synthèse</b><small>5 points clés extraits</small></div>
            </div>
            <div class="vs-mockup-row">
                <div class="chip g">{ic("hash", 15)}</div>
                <div class="txt"><b>Mots-clés</b><small>#IA #productivité #résumé</small></div>
            </div>
            <div class="vs-mockup-row">
                <div class="chip y">{ic("award", 15)}</div>
                <div class="txt"><b>Quiz généré</b><small>4 questions · score /100</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">Fonctionnalités</div>
    <div class="g-h2">Tout ce qu'il faut pour apprendre plus vite</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _features = [
        ("cpu", "#3B82F6", "#60A5FA", "IA de pointe", "DistilBART & BART-large : résumés fidèles, sans invention.", None),
        ("msg", "#10B981", "#34D399", "Chat vidéo IA", "Posez une question, obtenez une réponse ancrée dans le contenu.", "Plus"),
        ("award", "#D4AF37", "#F0D488", "Quiz & flashcards", "QCM interactif avec score, export Anki pour révision espacée.", "Premium"),
        ("download", "#8B5CF6", "#C4B5FD", "Exports pro", "PDF, Markdown, Obsidian, Notion, présentation HTML.", None),
        ("image", "#F97316", "#FB923C", "Slides automatiques", "Transformez la vidéo en présentation prête à projeter.", "Plus"),
        ("globe", "#06B6D4", "#22D3EE", "4 langues", "FR, EN, ES, DE. L'interface ET les résumés.", None),
        ("users", "#EC4899", "#F472B6", "Parrainage", "Invitez, gagnez +3 jours gratuits par filleul actif.", None),
        ("folder", "#F59E0B", "#FBBF24", "Collections", "Favoris, historique de recherche, organisation.", "Basique"),
        ("trending-up", "#EF4444", "#F87171", "Viral Score", "Analysez le potentiel viral d'une vidéo sur 100.", "Premium"),
    ]
    _feat_html = ""
    for _icn, _c1c, _c2c, _title, _desc, _tag in _features:
        _tag_html = f'<span class="vs-feat-tag">{_tag}</span>' if _tag else ""
        _feat_html += (
            f'<div class="vs-feat">'
            f'{_tag_html}'
            f'<div class="vs-feat-ico" style="background:linear-gradient(135deg,{_c1c},{_c2c});">{ic(_icn, 20)}</div>'
            f'<div class="vs-feat-title">{_title}</div>'
            f'<div class="vs-feat-desc">{_desc}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="vs-feat-grid">{_feat_html}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    st.markdown('<div id="vs-demo"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="g-kicker">Démo interactive</div>
    <div class="g-h2">VideoScribe AI en action</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _teaser = Path("teaser.html")
    if _teaser.exists():
        _components.html(_teaser.read_text(encoding="utf-8"), height=560)
    elif DEMO_VIDEO_URL:
        st.video(DEMO_VIDEO_URL)

    if st.session_state.pop("scroll_demo", False):
        _components.html('<script>var el=window.parent.document.getElementById("vs-demo"); if(el){el.scrollIntoView({behavior:"smooth"});}</script>', height=0)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">Ils nous font confiance</div>
    <div class="g-h2">Ce qu'ils en disent</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _testis = [
        ("K", "linear-gradient(135deg,#3B82F6,#60A5FA)", "Khadija D.", "Étudiante en médecine",
         "Je révise mes cours en 10 min au lieu d'1 h de vidéo. Les flashcards Anki sont un game-changer."),
        ("S", "linear-gradient(135deg,#10B981,#34D399)", "Sokhna B.", "Veille stratégique",
         "Le rapport hebdo et les points d'action sont devenus mon outil de veille principal."),
        ("A", "linear-gradient(135deg,#D4AF37,#F0D488)", "Ababacar D.", "Créateur de contenu",
         "Paiement Wave en 2 min, Premium activé dans la foulée. Le support est ultra réactif."),
    ]
    _testi_html = ""
    for _init, _grad, _name, _role, _quote in _testis:
        _testi_html += (
            f'<div class="vs-testi">'
            f'<div class="vs-testi-stars">{STARS}</div>'
            f'<div class="vs-testi-quote">« {_quote} »</div>'
            f'<div class="vs-testi-author">'
            f'<div class="vs-testi-avatar" style="background:{_grad};">{_init}</div>'
            f'<div><b>{_name}</b><small>{_role}</small></div>'
            f'</div>'
            f'</div>'
        )
    st.markdown(f'<div class="vs-testi-grid">{_testi_html}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">FAQ</div>
    <div class="g-h2">Questions fréquentes</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _faqs = [
        ("Est-ce vraiment gratuit ?",
         "Oui. Le plan Gratuit offre 3 analyses par jour, à vie, sans carte bancaire. Les plans payants débloquent les analyses illimitées, les exports PDF, le quiz, le chat vidéo, etc."),
        ("Mes données sont-elles en sécurité ?",
         "Absolument. Mots de passe hashés, emails vérifiés, HTTPS, hébergement sécurisé. Nous ne revendons jamais vos données. Conformité RGPD totale."),
        ("Quelles vidéos sont supportées ?",
         "Toute vidéo YouTube publique disposant de sous-titres (manuels ou automatiques). Les vidéos privées ou réservées aux membres ne sont pas accessibles."),
        ("Puis-je exporter vers Notion ou Obsidian ?",
         "Oui, à partir du plan Premium+. Les exports Markdown, Obsidian, Notion et Anki sont disponibles en un clic."),
        ("Comment fonctionne le parrainage ?",
         "Partagez votre code unique. Chaque filleul qui s'inscrit vous rapporte +3 jours gratuits, cumulables."),
        ("Puis-je annuler à tout moment ?",
         "Oui. Aucun engagement. Vous gardez l'accès jusqu'à la fin de la période payée."),
    ]
    for _q, _a in _faqs:
        st.markdown(f"""
        <details class="vs-faq-item">
            <summary class="vs-faq-q">{ic("bulb", 16)} {_q}</summary>
            <div class="vs-faq-a">{_a}</div>
        </details>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vs-final-cta">
        <h3>Prêt à gagner des heures ?</h3>
        <p>Rejoignez plus de 1 000 utilisateurs qui transforment déjà leurs vidéos YouTube en notes exploitables.</p>
        <div class="vs-final-badges">
            <span>✓ 3 analyses/jour offertes</span>
            <span>✓ Sans carte bancaire</span>
            <span>✓ Export immédiat</span>
            <span>✓ Annulation à tout moment</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _cc1, _cc2, _cc3 = st.columns([1, 1.2, 1])
    with _cc2:
        _cc_b1, _cc_b2 = st.columns(2)
        with _cc_b1:
            if st.button(f"{T('register')} →", type="primary", use_container_width=True, key="final_cta_register"):
                st.session_state.page = "register"; st.rerun()
        with _cc_b2:
            if st.button("Découvrir Premium", use_container_width=True, key="final_cta_premium"):
                st.session_state.page = "premium"; st.rerun()

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    render_footer(compact=True)


def render_about():
    render_navbar()
    # ═══ Détection du thème ═══
    _is_light = st.session_state.get("theme", "light") == "light"
    _about_nav = "#0F1A2E" if _is_light else "#F8FAFC"
    _about_soft = "#4A5A7A" if _is_light else "rgba(148,163,184,.9)"
    _about_hero_bg = (
        "radial-gradient(700px 380px at 50% -10%, rgba(59,130,246,.10), transparent 65%), "
        "linear-gradient(160deg, #F8FAFC 0%, #EFF4FB 100%)"
    ) if _is_light else (
        "radial-gradient(700px 380px at 50% -10%, rgba(59,130,246,.32), transparent 65%), "
        "linear-gradient(160deg, #05080F 0%, #0D1524 100%)"
    )
    _about_border = "rgba(15,26,46,.10)" if _is_light else "rgba(255,255,255,.10)"
    _about_shadow = "0 20px 60px rgba(15,26,46,.08)" if _is_light else "0 40px 100px rgba(2,8,18,.45)"
    _about_card_bg = "#FFFFFF" if _is_light else "rgba(255,255,255,.04)"
    _about_card_border = "rgba(15,26,46,.10)" if _is_light else "rgba(255,255,255,.09)"
    _about_grid_line = "rgba(15,26,46,.03)" if _is_light else "rgba(255,255,255,.02)"

    st.markdown(f"""
    <style>
    .vs-about-hero {{
        position:relative; overflow:hidden; border-radius:34px;
        padding: clamp(2.5rem, 6vw, 4.5rem) clamp(1.5rem, 5vw, 4rem);
        margin:.4rem 0 2.5rem; isolation:isolate; text-align:center;
        background: {_about_hero_bg};
        border:1px solid {_about_border};
        box-shadow: {_about_shadow};
    }}
    .vs-about-hero::before {{
        content:""; position:absolute; inset:0; z-index:0;
        background-image:
            linear-gradient({_about_grid_line} 1px, transparent 1px),
            linear-gradient(90deg, {_about_grid_line} 1px, transparent 1px);
        background-size: 50px 50px;
        mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
        -webkit-mask-image: radial-gradient(ellipse at center, black 20%, transparent 70%);
    }}
    .vs-about-kicker {{
        display:inline-flex; align-items:center; gap:8px; padding:7px 16px; border-radius:999px;
        background:{_about_card_bg}; border:1px solid {_about_border};
        color:{_about_soft} !important; font-size:.74rem; font-weight:800;
        letter-spacing:.14em; text-transform:uppercase; margin-bottom:1.3rem; position:relative; z-index:1;
    }}
    .vs-about-h1 {{
        font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.045em;
        line-height:1.05; font-size: clamp(2rem, 4.5vw, 3.6rem);
        color:{_about_nav} !important; margin:0 0 1.2rem; position:relative; z-index:1;
    }}
    .vs-about-h1 .grad {{
        background: linear-gradient(92deg,#60A5FA,#34D399 50%,#FBBF24);
        -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    }}
    .vs-about-lead {{
        color: {_about_soft} !important; max-width: 720px; margin: 0 auto;
        font-size: clamp(1rem, 1.3vw, 1.15rem); line-height: 1.75; position:relative; z-index:1;
    }}
    .vs-about-stats {{
        display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-top:2rem;
        position:relative; z-index:1; max-width: 820px; margin-left:auto; margin-right:auto;
    }}
    .vs-about-stat {{
        background: {_about_card_bg}; border:1px solid {_about_card_border};
        border-radius:16px; padding:1.1rem .8rem; text-align:center;
    }}
    .vs-about-stat b {{
        display:block; font-family:'Sora',sans-serif; font-weight:800;
        font-size:1.7rem; color:{_about_nav} !important; letter-spacing:-.03em;
    }}
    .vs-about-stat span {{
        display:block; color:{_about_soft} !important; font-size:.74rem;
        font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-top:.3rem;
    }}
    .vs-history {{ position:relative; padding-left: 2rem; margin-top: 1.4rem; }}
    .vs-history::before {{
        content:""; position:absolute; left:11px; top: 12px; bottom: 12px; width:2px;
        background: linear-gradient(180deg, #3B82F6, #10B981, #D4AF37, #EF4444);
        border-radius:2px; opacity:.6;
    }}
    .vs-hist-item {{ position:relative; padding: 0 0 1.6rem 2.4rem; }}
    .vs-hist-item:last-child {{ padding-bottom: 0; }}
    .vs-hist-dot {{
        position:absolute; left:0; top:4px; width:24px; height:24px; border-radius:50%;
        background: linear-gradient(135deg,#0F172A,#1E293B);
        border:2px solid #3B82F6; display:flex; align-items:center; justify-content:center;
        box-shadow: 0 0 0 4px rgba(59,130,246,.12);
    }}
    .vs-hist-dot::after {{
        content:""; width:8px; height:8px; border-radius:50%;
        background: linear-gradient(135deg,#60A5FA,#34D399);
    }}
    .vs-hist-year {{
        font-family:'Sora',sans-serif; font-weight:800; color:#2E6DB4 !important;
        font-size:.82rem; letter-spacing:.08em; text-transform:uppercase;
    }}
    .vs-hist-item h4 {{
        font-family:'Sora',sans-serif; font-weight:800; color:{_about_nav} !important;
        font-size:1.02rem; margin:.3rem 0 .35rem;
    }}
    .vs-hist-item p {{ color: {_about_soft} !important; font-size:.88rem; line-height:1.6; }}

    /* Cartes valeurs + équipe — texte adapté au thème */
    .vs-value h4,
    .vs-team h4 {{ color: {_about_nav} !important; }}
    .vs-value p,
    .vs-team p {{ color: {_about_soft} !important; }}
    .vs-team .role {{ color: #2E6DB4 !important; }}
    .vs-value {{ background: {_about_card_bg} !important; border:1px solid {_about_card_border} !important; }}
    .vs-team {{ background: {_about_card_bg} !important; border:1px solid {_about_card_border} !important; }}

    @media (max-width: 900px) {{
        .vs-about-stats {{ grid-template-columns: repeat(2,1fr); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vs-about-hero">
        <div class="vs-about-kicker">{ic("info", 13)} À propos de VideoScribe AI</div>
        <h1 class="vs-about-h1">
            Bâtir l'avenir du <span class="grad">résumé intelligent</span>
        </h1>
        <p class="vs-about-lead">
            Fondée par des passionnés d'IA, VideoScribe AI accompagne étudiants, professionnels
            et créateurs en proposant des résumés de vidéos innovants, sur mesure et performants.
        </p>
        <div class="vs-about-stats">
            <div class="vs-about-stat"><b>+1 000</b><span>Vidéos analysées</span></div>
            <div class="vs-about-stat"><b>4</b><span>Langues supportées</span></div>
            <div class="vs-about-stat"><b>~60 s</b><span>Par analyse</span></div>
            <div class="vs-about-stat"><b>2026</b><span>Année de création</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">Notre raison d'être</div>
    <div class="g-h2">Vision & Mission</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _v1, _v2 = st.columns(2, gap="large")
    with _v1:
        st.markdown(f"""
        <div class="vs-value">
            <div class="vs-value-ico">{ic("eye", 18)}</div>
            <h4>{T("vision")}</h4>
            <p>Devenir le partenaire technologique de référence pour apprendre plus vite,
            reconnu pour notre expertise et notre impact positif sur la gestion de la connaissance.</p>
        </div>
        """, unsafe_allow_html=True)
    with _v2:
        st.markdown(f"""
        <div class="vs-value">
            <div class="vs-value-ico">{ic("target", 18)}</div>
            <h4>{T("mission")}</h4>
            <p>Accompagner les utilisateurs dans leur transformation numérique en concevant
            des solutions IA innovantes, adaptées à leurs besoins spécifiques.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">Notre parcours</div>
    <div class="g-h2">Une histoire construite pas à pas</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vs-history">
        <div class="vs-hist-item">
            <div class="vs-hist-dot"></div>
            <div class="vs-hist-year">2024 — L'idée</div>
            <h4>Un constat simple</h4>
            <p>Des heures de vidéos YouTube pour quelques minutes d'information utile.
            L'idée de VideoScribe AI germe dans l'esprit de ses fondateurs.</p>
        </div>
        <div class="vs-hist-item">
            <div class="vs-hist-dot"></div>
            <div class="vs-hist-year">2025 — Le prototype</div>
            <h4>Premières versions</h4>
            <p>Développement du pipeline d'extraction de sous-titres et des premiers modèles
            de résumé IA. Tests intensifs avec des étudiants et des créateurs.</p>
        </div>
        <div class="vs-hist-item">
            <div class="vs-hist-dot"></div>
            <div class="vs-hist-year">2026 — Le lancement</div>
            <h4>VideoScribe AI v1</h4>
            <p>Sortie publique avec 4 langues, exports multi-formats, quiz interactif,
            flashcards Anki et suite viralité pour créateurs de contenu.</p>
        </div>
        <div class="vs-hist-item">
            <div class="vs-hist-dot"></div>
            <div class="vs-hist-year">Aujourd'hui</div>
            <h4>Une communauté grandissante</h4>
            <p>Plus de 1 000 vidéos analysées, des retours utilisateurs constants,
            et de nouvelles fonctionnalités chaque mois.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">{T("values")}</div>
    <div class="g-h2">Les principes qui guident nos actions</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _vals = [
        ("tool", "Excellence", "Nous visons l'excellence dans tout ce que nous entreprenons, du code à l'expérience utilisateur."),
        ("spark", "Innovation", "L'innovation est au cœur de notre ADN. Chaque mois, de nouvelles fonctionnalités."),
        ("shield", "Intégrité", "Honnêteté, transparence et éthique dans chaque interaction, chaque ligne de code."),
        ("users", "Collaboration", "La puissance de la collaboration étroite avec nos utilisateurs et nos partenaires."),
        ("target", "Impact", "Un impact positif et durable sur l'écosystème de la connaissance."),
        ("book", "Apprentissage", "Une culture d'apprentissage perpétuel, en interne comme pour nos utilisateurs."),
    ]
    _vals_html = ""
    for _icn, _t, _d in _vals:
        _vals_html += (
            f'<div class="vs-value">'
            f'<div class="vs-value-ico">{ic(_icn, 18)}</div>'
            f'<h4>{_t}</h4>'
            f'<p>{_d}</p>'
            f'</div>'
        )
    st.markdown(f'<div class="vs-value-grid">{_vals_html}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="g-kicker">L'équipe</div>
    <div class="g-h2">Les visages derrière VideoScribe AI</div>
    <div class="g-rule"></div>
    """, unsafe_allow_html=True)

    _team = [
        ("M", "linear-gradient(135deg,#3B82F6,#60A5FA)", "Mbaye T.", "Fondateur & Lead Dev", "Architecture technique, pipeline IA, vision produit."),
        ("A", "linear-gradient(135deg,#10B981,#34D399)", "Aminata S.", "UX & Design", "Expérience utilisateur, design system, accessibilité."),
        ("S", "linear-gradient(135deg,#D4AF37,#F0D488)", "Souleymane D.", "IA & Recherche", "Fine-tuning des modèles, qualité des résumés, benchmarks."),
    ]
    _team_html = ""
    for _init, _grad, _name, _role, _desc in _team:
        _team_html += (
            f'<div class="vs-team">'
            f'<div class="vs-team-avatar" style="background:{_grad};">{_init}</div>'
            f'<h4>{_name}</h4>'
            f'<div class="role">{_role}</div>'
            f'<p>{_desc}</p>'
            f'</div>'
        )
    st.markdown(f'<div class="vs-team-grid">{_team_html}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="vs-final-cta" style="margin-top:0;">
        <h3>Envie de tester par vous-même ?</h3>
        <p>Rejoignez VideoScribe AI gratuitement et transformez votre première vidéo en quelques secondes.</p>
        <div class="vs-final-badges">
            <span>✓ Sans carte bancaire</span>
            <span>✓ 3 analyses/jour</span>
            <span>✓ Prêt en 30 secondes</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _ab1, _ab2, _ab3 = st.columns([1, 1.2, 1])
    with _ab2:
        _ab_b1, _ab_b2 = st.columns(2)
        with _ab_b1:
            if st.button(f"{T('register')} →", type="primary", use_container_width=True, key="about_cta_register"):
                st.session_state.page = "register"; st.rerun()
        with _ab_b2:
            if st.button(T("home"), use_container_width=True, key="about_cta_home"):
                st.session_state.page = "accueil"; st.rerun()

    render_footer(compact=False)


def render_privacy(show_back=True):
    hero("lock", T("priv_title"), T("priv_sub"), [f'{ic("shield", 13)} RGPD', f'{ic("check", 13)} CNIL', f'{ic("mail", 13)} Contact'])
    st.markdown(f"""### 1. Responsable — **Mbtech-services** — `{CONTACT_EMAIL}`
### 2. Données — nom, email, photo, historique, cookies.
### 3. Vidéos — sous-titres publics uniquement, rien ne reste.
### 4. Sécurité — mots de passe hashés, emails vérifiés, HTTPS.
### 5. Paiements — CinetPay, aucune donnée bancaire stockée.
### 6. Droits RGPD — consulter, exporter, supprimer.
### 7. Cookies — `ys_token` (7 j), `ys_theme` (1 an).
### 8. Contact — {CONTACT_EMAIL} • {PAYMENT_WAVE}""")
    if show_back and st.button(T("home"), use_container_width=True): st.session_state.page="accueil"; st.rerun()


def render_contact():
    render_navbar()
    _contact_user = st.session_state.get("user")
    _contact_is_guest = _contact_user is None
    _contact_sender = _contact_user or "visiteur_anonyme"
    _contact_tier = 0
    try:
        _contact_tier = tier
    except NameError:
        try:
            if _contact_user:
                _contact_tier = get_tier(_contact_user)
            elif st.session_state.get("role") == "admin":
                _contact_tier = 3
        except Exception:
            _contact_tier = 0

    # ═══════════ DÉTECTION DU THÈME ═══════════
    _is_light = st.session_state.get("theme", "light") == "light"
    if _is_light:
        _c_nav = "#0F1A2E"; _c_soft = "#4A5A7A"
        _c_surface = "#FFFFFF"; _c_border = "rgba(15,26,46,.12)"
        _c_card_bg = "#FFFFFF"
        _c_card_border = "rgba(15,26,46,.10)"
        _c_hero_bg = ("radial-gradient(700px 380px at 50% -10%, rgba(59,130,246,.10), transparent 65%), "
                      "radial-gradient(500px 280px at 20% 100%, rgba(16,185,129,.08), transparent 65%), "
                      "linear-gradient(160deg, #F8FAFC 0%, #EFF4FB 100%)")
        _c_hero_title = "#0F1A2E"
        _c_accent = "#2E6DB4"; _c_ok = "#10B981"
        _c_faq_bg = "#FFFFFF"; _c_faq_hover = "#F1F5FB"
        _c_faq_q = "#0F1A2E"; _c_faq_a = "#4A5A7A"
    else:
        _c_nav = "#F8FAFC"; _c_soft = "rgba(148,163,184,.9)"
        _c_surface = "rgba(255,255,255,.045)"; _c_border = "rgba(255,255,255,.12)"
        _c_card_bg = "rgba(255,255,255,.04)"
        _c_card_border = "rgba(255,255,255,.10)"
        _c_hero_bg = ("radial-gradient(700px 380px at 50% -10%, rgba(59,130,246,.28), transparent 65%), "
                      "radial-gradient(500px 280px at 20% 100%, rgba(16,185,129,.18), transparent 65%), "
                      "linear-gradient(160deg, #05080F 0%, #0D1524 100%)")
        _c_hero_title = "#F8FAFC"
        _c_accent = "#60A5FA"; _c_ok = "#34D399"
        _c_faq_bg = "rgba(255,255,255,.035)"; _c_faq_hover = "rgba(255,255,255,.06)"
        _c_faq_q = "#F8FAFC"; _c_faq_a = "rgba(203,213,225,.85)"

    # ═══════════ CSS CONTACT ═══════════
    st.markdown(f"""
    <style>
    .vs-contact-hero {{
        position:relative; overflow:hidden; border-radius:34px;
        padding: clamp(2.5rem, 6vw, 4.5rem) clamp(1.5rem, 5vw, 4rem);
        margin:.4rem 0 2.5rem; text-align:center;
        background: {_c_hero_bg};
        border:1px solid {_c_border};
        box-shadow: 0 20px 60px rgba(15,26,46,.08);
    }}
    .vs-contact-kicker {{
        display:inline-flex; align-items:center; gap:8px; padding:7px 16px; border-radius:999px;
        background:{_c_surface}; border:1px solid {_c_border};
        color:{_c_soft} !important; font-size:.74rem; font-weight:800;
        letter-spacing:.14em; text-transform:uppercase; margin-bottom:1.3rem;
    }}
    .vs-contact-h1 {{
        font-family:'Sora',sans-serif; font-weight:800; letter-spacing:-.045em;
        line-height:1.05; font-size: clamp(2rem, 4.5vw, 3.4rem);
        color:{_c_hero_title} !important; margin:0 0 1.2rem;
    }}
    .vs-contact-h1 .grad {{
        background: linear-gradient(92deg,{_c_accent},{_c_ok} 50%,#D4AF37);
        -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
    }}
    .vs-contact-lead {{
        color: {_c_soft} !important; max-width: 680px; margin: 0 auto;
        font-size: clamp(1rem, 1.3vw, 1.15rem); line-height: 1.75;
    }}
    .vs-contact-badges {{ display:flex; flex-wrap:wrap; gap:.6rem; justify-content:center; margin-top:1.8rem; }}
    .vs-contact-badge {{
        display:inline-flex; align-items:center; gap:7px; padding:7px 14px; border-radius:999px;
        background:{_c_surface}; border:1px solid {_c_border};
        color:{_c_nav} !important; font-size:.8rem; font-weight:700;
    }}

    /* Cartes canaux */
    .vs-channels-grid {{
        display:grid; grid-template-columns:repeat(4, minmax(0,1fr));
        gap:.9rem; margin: 1.5rem 0 2.5rem;
    }}
    .vs-channel {{
        position:relative; border-radius:20px;
        padding:1.4rem 1.2rem; text-align:left;
        background: {_c_card_bg};
        border:1px solid {_c_card_border};
        transition: transform .35s cubic-bezier(.16,1,.3,1), border-color .3s ease, box-shadow .35s ease;
    }}
    .vs-channel:hover {{
        transform: translateY(-5px);
        border-color: {_c_accent}66;
        box-shadow: 0 20px 50px {_c_accent}22;
    }}
    .vs-channel-ico {{
        width:44px; height:44px; border-radius:12px;
        display:flex; align-items:center; justify-content:center;
        margin-bottom:.9rem; color:#fff !important;
        box-shadow: 0 10px 22px rgba(46,109,180,.22);
    }}
    .vs-channel-label {{
        font-size:.68rem; font-weight:800; letter-spacing:.09em; text-transform:uppercase;
        color:{_c_soft} !important; margin-bottom:.3rem;
    }}
    .vs-channel-title {{
        font-family:'Sora',sans-serif; font-weight:800;
        color:{_c_nav} !important; font-size:.98rem; margin-bottom:.4rem;
    }}
    .vs-channel-value {{
        color:{_c_soft} !important; font-size:.86rem; line-height:1.55; word-break:break-word;
    }}
    .vs-channel-value a {{ color:{_c_accent} !important; text-decoration:none; font-weight:600; }}
    .vs-channel-value a:hover {{ text-decoration:underline; }}

    /* Section titles */
    .vs-section-title {{
        display:flex; align-items:center; gap:10px;
        font-family:'Sora',sans-serif; font-weight:800; color:{_c_nav} !important;
        font-size:1.35rem; margin: 2rem 0 1rem;
    }}
    .vs-section-title .bar {{
        width:5px; height:26px; border-radius:3px;
        background: linear-gradient(180deg, {_c_accent}, {_c_ok});
    }}

    /* Map */
    .vs-map-wrap {{
        border-radius:22px; overflow:hidden;
        border:1px solid {_c_border};
        box-shadow: 0 20px 50px rgba(2,8,18,.10);
        margin-bottom:1rem;
    }}
    .vs-map-wrap iframe {{ border-radius:22px !important; border:none !important; display:block; }}
    .vs-map-link {{
        display:inline-flex; align-items:center; gap:6px;
        color:{_c_accent} !important; font-weight:700; font-size:.88rem;
        text-decoration:none; margin-top:.5rem;
    }}
    .vs-map-link:hover {{ text-decoration:underline; }}

    /* FAQ — CORRIGÉ pour light/dark */
    /* FAQ — light/dark */
details.vs-faq-item {{
    border:1px solid {_c_border};
    border-radius:16px; margin-bottom:.6rem;
    background: {_c_faq_bg};
    overflow:hidden;
    transition: border-color .3s ease, background .3s ease;
}}
details.vs-faq-item:hover {{ border-color: {_c_accent}66; background: {_c_faq_hover}; }}
summary.vs-faq-q {{
    display:flex; align-items:center; gap:12px;
    padding:1rem 1.2rem; cursor:pointer;
    font-weight:700; color:{_c_faq_q} !important; font-size:.94rem;
    list-style:none;
}}
summary.vs-faq-q::-webkit-details-marker {{ display:none; }}
summary.vs-faq-q::after {{
    content:"+"; margin-left:auto; font-size:1.3rem; color:{_c_accent} !important;
    transition: transform .3s ease; font-weight:400;
}}
details.vs-faq-item[open] summary.vs-faq-q::after {{ transform: rotate(45deg); }}
.vs-faq-a {{
    padding: 0 1.2rem 1.1rem 3.1rem;
    color:{_c_faq_a} !important; font-size:.88rem; line-height:1.7;
}}
    details[open] .vs-faq-q::after {{ transform: rotate(45deg); }}
    .vs-faq-a {{
        padding: 0 1.2rem 1.1rem 3.1rem;
        color:{_c_faq_a} !important; font-size:.88rem; line-height:1.7;
    }}

    /* Formulaire */
    .vs-form-wrap {{
        border-radius:24px; padding:1.8rem 1.6rem;
        background: {_c_card_bg};
        border:1px solid {_c_card_border};
        box-shadow: 0 20px 50px rgba(2,8,18,.08);
    }}
    .vs-form-title {{
        font-family:'Sora',sans-serif; font-weight:800;
        color:{_c_nav} !important; font-size:1.2rem; margin-bottom:.4rem;
        display:flex; align-items:center; gap:10px;
    }}
    .vs-form-sub {{ color:{_c_soft} !important; font-size:.86rem; margin-bottom:1.3rem; }}

    @media (max-width: 900px) {{ .vs-channels-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 560px) {{ .vs-channels-grid {{ grid-template-columns: 1fr; }} }}
    </style>
    """, unsafe_allow_html=True)

    # ═══════════ HERO ═══════════
    st.markdown(f"""
    <div class="vs-contact-hero">
        <div class="vs-contact-kicker">{ic("phone", 13)} Contact & Support</div>
        <h1 class="vs-contact-h1">
            Une question, un projet ?<br>
            <span class="grad">Parlons-en.</span>
        </h1>
        <p class="vs-contact-lead">
            Notre équipe vous répond en moins de 24 h (2 h pour les Premium+).
            Par email, WhatsApp ou via le formulaire ci-dessous.
        </p>
        <div class="vs-contact-badges">
            <span class="vs-contact-badge">{ic("zap", 13)} Réponse &lt; 24 h</span>
            <span class="vs-contact-badge">{ic("shield", 13)} Support RGPD</span>
            <span class="vs-contact-badge">{ic("globe", 13)} Support FR / EN</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════ CANAUX ═══════════
    _delay = "< 2 h" if _contact_tier >= 3 else "< 24 h"
    st.markdown(f"""
    <div class="vs-channels-grid">
        <div class="vs-channel">
            <div class="vs-channel-ico" style="background:linear-gradient(135deg,#3B82F6,#60A5FA);">{ic("mail", 20)}</div>
            <div class="vs-channel-label">Email</div>
            <div class="vs-channel-title">Support & Commercial</div>
            <div class="vs-channel-value"><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div>
        </div>
        <div class="vs-channel">
            <div class="vs-channel-ico" style="background:linear-gradient(135deg,#10B981,#34D399);">{ic("msg", 20)}</div>
            <div class="vs-channel-label">WhatsApp</div>
            <div class="vs-channel-title">Support instantané</div>
            <div class="vs-channel-value">{PAYMENT_WAVE}</div>
        </div>
        <div class="vs-channel">
            <div class="vs-channel-ico" style="background:linear-gradient(135deg,#D4AF37,#F0D488);">{ic("card", 20)}</div>
            <div class="vs-channel-label">Paiement</div>
            <div class="vs-channel-title">Wave / Orange Money</div>
            <div class="vs-channel-value">{PAYMENT_WAVE}</div>
        </div>
        <div class="vs-channel">
            <div class="vs-channel-ico" style="background:linear-gradient(135deg,#8B5CF6,#C4B5FD);">{ic("clock", 20)}</div>
            <div class="vs-channel-label">Horaires</div>
            <div class="vs-channel-title">Lun — Sam</div>
            <div class="vs-channel-value">9 h – 20 h (GMT)<br>Réponse : <b style="color:{_c_ok} !important;">{_delay}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ═══════════ LOCALISATION ═══════════
    st.markdown(f"""<div class="vs-section-title"><div class="bar"></div>{ic("map", 20)} Notre localisation</div>""", unsafe_allow_html=True)

    _map_left, _map_right = st.columns([1.6, 1], gap="large")
    with _map_left:
        st.markdown('<div class="vs-map-wrap">', unsafe_allow_html=True)
        _components.iframe(MAP_EMBED, height=340)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<a class="vs-map-link" target="_blank" href="{MAP_LINK}">{ic("link", 13)} Ouvrir dans Google Maps ↗</a>', unsafe_allow_html=True)

    with _map_right:
        st.markdown(f"""
        <div class="vs-channel" style="margin-bottom:.8rem;">
            <div class="vs-channel-ico" style="background:linear-gradient(135deg,#3B82F6,#60A5FA);">{ic("map", 20)}</div>
            <div class="vs-channel-label">Adresse</div>
            <div class="vs-channel-title">Mbtech-services</div>
            <div class="vs-channel-value">Cambérène, Dakar — Sénégal<br>Lun – Sam : 9 h – 20 h (GMT)</div>
        </div>
        <div class="vs-channel">
            <div class="vs-channel-ico" style="background:linear-gradient(135deg,#10B981,#34D399);">{ic("phone", 20)}</div>
            <div class="vs-channel-label">Téléphone</div>
            <div class="vs-channel-title">Appel & WhatsApp</div>
            <div class="vs-channel-value">{PAYMENT_WAVE}</div>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════ FAQ ═══════════
    st.markdown(f"""<div class="vs-section-title" style="margin-top:2.5rem;"><div class="bar"></div>{ic("bulb", 20)} FAQ express</div>""", unsafe_allow_html=True)

    _faqs = [
        ("J'ai oublié mon mot de passe, que faire ?",
         "Utilisez le formulaire ci-dessous ou écrivez-nous sur WhatsApp. Nous réinitialisons votre mot de passe sous 24 h (2 h pour Premium+)."),
        ("Mon paiement n'a pas activé mon compte, pourquoi ?",
         "Envoyez-nous votre pseudo + une capture d'écran Wave/Orange Money. L'activation manuelle est faite sous 24 h maximum."),
        ("Que faire si une vidéo n'a pas de sous-titres ?",
         "Certaines vidéos (privées, réservées aux membres, ou sans sous-titres publics) ne peuvent pas être analysées. Essayez avec une autre vidéo ou contactez-nous."),
        ("Puis-je obtenir une facture pour mon entreprise ?",
         "Oui, sur demande. Envoyez-nous un email avec vos informations de facturation (raison sociale, numéro TVA, adresse)."),
        ("Comment annuler mon abonnement ?",
         "Aucun engagement. Envoyez-nous simplement un message via le formulaire ou WhatsApp, et l'annulation sera effective immédiatement."),
    ]
    for _q, _a in _faqs:
        st.markdown(f"""
        <details class="vs-faq-item">
            <summary class="vs-faq-q">{ic("bulb", 15)} {_q}</summary>
            <div class="vs-faq-a">{_a}</div>
        </details>
        """, unsafe_allow_html=True)

    # ═══════════ FORMULAIRE ═══════════
    st.markdown(f"""<div class="vs-section-title" style="margin-top:2.5rem;"><div class="bar"></div>{ic("send", 20)} Envoyer un message</div>""", unsafe_allow_html=True)

    st.markdown('<div class="vs-form-wrap">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="vs-form-title">{ic("msg", 20)} Support client</div>
    <div class="vs-form-sub">Remplissez le formulaire ci-dessous, nous vous répondrons dans les meilleurs délais.</div>
    """, unsafe_allow_html=True)

    _acc_email = ""
    if not _contact_is_guest:
        try:
            _acc_email = (list_users().get(_contact_user, {}) or {}).get("email", "") or ""
        except Exception:
            _acc_email = ""

    with st.form("contact_form", border=False):
        _c1, _c2 = st.columns(2)
        with _c1:
            subject = st.text_input(T("subject"), placeholder="Ex. Problème de paiement, Question sur Premium...")
        with _c2:
            email_c = st.text_input(T("your_email"), value=_acc_email, placeholder="votre@email.com")
        _c3, _c4 = st.columns([1, 1])
        with _c3:
            urgency = st.selectbox(T("priority"), ["normale", "importante", "urgente"])
        with _c4:
            st.markdown("<div style='height:.6rem;'></div>", unsafe_allow_html=True)
            st.caption("Urgence : pour les problèmes bloquants, choisissez « urgente ».")
        message = st.text_area(T("message"), height=170, placeholder="Décrivez votre demande en détail...")
        _sub_col1, _sub_col2, _sub_col3 = st.columns([1, 1.5, 1])
        with _sub_col2:
            _submitted = st.form_submit_button(f"📤 {T('send')}", use_container_width=True, type="primary")
        if _submitted:
            if subject.strip() and message.strip():
                try: save_message(_contact_sender, subject.strip(), message.strip(), urgency)
                except Exception: pass
                try: notify_admins("msg", f"Nouveau message de **{_contact_sender}** : « {subject.strip()} » (priorité {urgency})")
                except Exception: pass
                ok_admin, err_a = False, "fonction non disponible"
                ok_client, err_c = False, "fonction non disponible"
                try: ok_admin, err_a = send_contact_message(CONTACT_EMAIL, _contact_sender, email_c.strip(), subject.strip(), message.strip(), urgency)
                except Exception as e: err_a = str(e)
                try: ok_client, err_c = send_contact_ack(email_c.strip(), _contact_sender, subject.strip())
                except Exception as e: err_c = str(e)
                st.balloons()
                if ok_admin and ok_client: st.success("✅ Message envoyé ! Un accusé de réception vous a été envoyé par email.")
                elif ok_admin: st.success("✅ Message envoyé à l'équipe support.")
                else: st.warning(f"⚠️ Message enregistré mais l'envoi email a échoué : {err_a}")
            else:
                st.error("❌ Le sujet et le message sont obligatoires.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    render_footer(compact=True)


def render_landing():
    render_navbar()
    l, r = st.columns([1, 1], gap="large", vertical_alignment="center")
    with l:
        st.markdown(f"""<div class="g-kicker">Résumé IA de vidéos YouTube</div>
<div class="g-h1">Transformez vos vidéos en <em>notes structurées</em></div>
<p class="g-lead">VideoScribe AI condense des heures de YouTube en résumés clairs, mots-clés, questions et exports professionnels — en ~60 secondes.</p>
<div class="g-rule"></div>""", unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            if st.button(T("register"), type="primary", use_container_width=True, key="landing_register"):
                st.session_state.page = "register"; st.rerun()
        with b:
            if st.button("Voir la démo", use_container_width=True, key="landing_demo"):
                st.session_state.scroll_demo = True; st.rerun()
    with r:
        st.markdown(f"""<div class="g-card">
<div class="g-ico">{ic("file", 22)}</div>
<h4>Résumé — Vidéo IA</h4>
<p>1. L'IA extrait les sous-titres et résume chaque section…</p>
<p>2. Traduction automatique dans votre langue…</p>
<div style="margin-top:1rem; display:flex; flex-wrap:wrap;">
<span class="g-chip">IA</span>
<span class="g-chip">FR / EN / ES</span>
<span class="g-chip">PDF</span>
</div>
</div>""", unsafe_allow_html=True)
    if st.session_state.pop("scroll_demo", False):
        _components.html('<script>var el=window.parent.document.getElementById("vs-demo"); if(el){el.scrollIntoView({behavior:"smooth"});}</script>', height=0)
    st.markdown(f"""<div class="g-stats">
<div class="g-stat"><b>+1 000</b><span>vidéos résumées</span></div>
<div class="g-stat"><b>~60 s</b><span>par analyse</span></div>
<div class="g-stat"><b>4,9/5</b><span>satisfaction</span></div>
<div class="g-stat"><b>0</b><span>donnée revendue</span></div>
</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="g-kicker">Comment ça marche</div><div class="g-h2">Un processus en 4 étapes</div><div class="g-rule"></div>""", unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)
    for col,(n,t,d) in zip([s1,s2,s3,s4],[("01","Collez l'URL","YouTube, peu importe la langue."),
    ("02","L'IA résume","Sous-titres extraits et résumés en ~60 s."),
    ("03","Enrichissez","Mots-clés, questions, flashcards."),
    ("04","Exportez","PDF, Markdown, Obsidian, Notion, Anki.")]):
        col.markdown(f'<div class="g-step"><div class="n">{n}</div><h4>{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""<div class="g-kicker">Fonctionnalités</div><div class="g-h2">Une suite complète</div><div class="g-rule"></div>""", unsafe_allow_html=True)
    feats = [("cpu","IA de pointe","DistilBART & BART-large : résumés fidèles."),
    ("msg","Interroger la vidéo","Une question → une réponse ancrée (Premium+)."),
    ("award","Quiz & flashcards","Révisez avec QCM et cartes Anki."),
    ("download","Exports pro","PDF, Markdown, Obsidian & Notion."),
    ("folder","Collections","Favoris & historique de recherche."),
    ("users","Parrainage","Gagnez des jours gratuits en invitant.")]
    for row in [feats[0:3], feats[3:6]]:
        ca,cb,cc = st.columns(3)
        for col,(icn,t,d) in zip([ca,cb,cc], row):
            col.markdown(f'<div class="g-card"><div class="g-ico">{ic(icn,20)}</div><h4>{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""<div class="g-kicker">Ils nous font confiance</div><div class="g-h2">Ce qu'ils en disent</div><div class="g-rule"></div>""", unsafe_allow_html=True)
    t1,t2,t3 = st.columns(3)
    t1.markdown(f'<div class="g-card"><div>{STARS}</div><p style="margin-top:.8rem;">« Je révise mes cours en 10 min au lieu d\'1 h de vidéo. »</p><p style="margin-top:.8rem;font-weight:700;">Khadija D.</p></div>', unsafe_allow_html=True)
    t2.markdown(f'<div class="g-card"><div>{STARS}</div><p style="margin-top:.8rem;">« Le rapport hebdo et les points d\'action, mon outil de veille. »</p><p style="margin-top:.8rem;font-weight:700;">Sokhna B.</p></div>', unsafe_allow_html=True)
    t3.markdown(f'<div class="g-card"><div>{STARS}</div><p style="margin-top:.8rem;">« Paiement Wave en 2 min, Premium activé dans la foulée. »</p><p style="margin-top:.8rem;font-weight:700;">Ababacar D.</p></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div id="vs-demo"></div>', unsafe_allow_html=True)
    _teaser = Path("teaser.html")
    if _teaser.exists():
        _components.html(_teaser.read_text(encoding="utf-8"), height=560)
    st.markdown(f"""
<div class="g-cta">
<div class="g-cta-grid">
<h3>Prêt à gagner du temps ?</h3>
<p>Essayez gratuitement pendant un mois, sans carte bancaire. Résumés, mots-clés, quiz et exports en ~60 secondes.</p>
<div class="g-cta-badges">
<span>✓ 3 analyses/jour offertes</span>
<span>✓ Sans carte bancaire</span>
<span>✓ Export immédiat</span>
</div>
</div>
</div>""", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1.2,1])
    with c2:
        if st.button(T("register")+" →", type="primary", use_container_width=True, key="landing_cta_register"): st.session_state.page="register"; st.rerun()
    render_footer(compact=False)