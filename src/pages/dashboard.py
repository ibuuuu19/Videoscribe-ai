"""
Pages dashboard — Historique, statistiques, profil, paramètres.

Contient :
- render_notifs() : Notifications
- render_profil() : Profil utilisateur
- render_stats() : Statistiques détaillées
- render_historique() : Historique des analyses
- render_config() : Paramètres

Helpers :
- _parse_hdate() : Parse une date d'historique
- _trend_html() : Affiche une tendance (↑ ou ↓)
- render_bar_chart_html() : Graphique à barres HTML

Extrait de app.py pour alléger le fichier principal (~272 lignes).

Usage:
    from src.pages.dashboard import render_historique, render_stats
"""

import json
from datetime import datetime, timedelta

import streamlit as st

from src.ui.i18n import T, LANGS
from src.ui.components import ic, logo_html
from src.ui.layout import hero, render_footer, get_accent, notify_admins
from src.ui.prefs import _save_appearance, set_language
from src.ui.storage import load_favs, toggle_fav, get_avatar_b64
from src.core.config import PLANS, TIER_CHIP
from src.core.cookies import set_cookie
from src.user_manager import (
    list_users, get_plan, get_tier, authenticate,
    reset_password, delete_user, set_active, set_plan,
)
from src.history_manager import get_history, clear_history
from src.session_manager import delete_session
from src.notification_manager import get_notifications, unread_count, mark_all_read
from src.revenue_manager import get_revenues, record_revenue
from src.contact_manager import get_messages, mark_read, delete_message
import html as _html                            # ← Pour _html.escape
from src.core.config import AVATAR_DIR          # ← Pour AVATAR_DIR
from src.core.cookies import delete_cookie, COOKIE_NAME   # ← Pour delete_cookie et COOKIE_NAME

# ═══════════════════════════════════════════════════════════════
# ⚠️ Les fonctions ci-dessous ont été copiées automatiquement
#    depuis app.py par le script extract_dashboard.py
# ═══════════════════════════════════════════════════════════════

def render_notifs():
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    tier = 3 if role == "admin" else (0 if not user else get_tier(user))
    _acc, _acc_dark = get_accent()
    hero("bell", T("notifs_title"), T("notifs_sub"))
    notifs = get_notifications(user)
    n_unread = unread_count(user)
    s1, s2, s3 = st.columns(3)
    s1.metric("Total", len(notifs)); s2.metric("Non lues", n_unread); s3.metric("Lues", len(notifs)-n_unread)
    if st.button(T("mark_all"), use_container_width=True): mark_all_read(user); st.rerun()
    if not notifs:
        st.markdown(f"<div class='notif-card'><span class='notif-ico'>{ic('bell', 18)}</span><div><b>{T('no_notif')}</b><br><small>—</small></div></div>", unsafe_allow_html=True)
        render_footer(compact=True)
        return
    for n in notifs:
        style = "" if n["read"] else "border-left:4px solid #D4AF37;"
        st.markdown(f"<div class='notif-card' style='{style}'><span class='notif-ico'>{ic('bell', 18)}</span><div><b>{n['text']}</b><br><small>{ic('clock', 12)} {n['date']}</small></div></div>", unsafe_allow_html=True)
    render_footer(compact=True)
# ⚠️ render_premium extrait dans src/pages/premium.py
def render_profil():
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    tier = 3 if role == "admin" else (0 if not user else get_tier(user))
    _acc, _acc_dark = get_accent()
    info = list_users().get(user, {})
    cur = "premium_plus" if role == "admin" else get_plan(user)
    badges = ["Admin" if role == "admin" else "Client", PLANS[cur]["name"] if cur != "free" else T("plan_free")]
    if tier >= 3: badges.append(T("certified"))
    hero("user", f"@{user}", T("profile"), badges)
    _av = get_avatar_b64(user)
    if _av: st.markdown(f'<img src="{_av}" class="big-avatar">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T("role"), role); c2.metric(T("plan"), PLANS[cur]["name"] if cur != "free" else T("plan_free"))
    exp = info.get("premium_expires")
    c3.metric(T("expires"), datetime.fromisoformat(exp).strftime("%d/%m/%Y") if exp and cur != "free" else "—")
    c4.metric(T("m_analyse"), len(get_history(user)))
    st.markdown("---"); st.subheader(T("change_pwd"))
    with st.form("pwd_form"):
        cur_p = st.text_input(T("pwd_current"), type="password"); new = st.text_input(T("pwd_new"), type="password"); conf = st.text_input(T("pwd_confirm"), type="password")
        if st.form_submit_button(T("pwd_update"), use_container_width=True):
            ok, _ = authenticate(user, cur_p)
            if not ok: st.error("Mot de passe actuel incorrect.")
            elif new != conf: st.error("La confirmation ne correspond pas.")
            elif reset_password(user, new): notify_admins("key", f"**{user}** a changé son mot de passe."); st.success("Mot de passe mis à jour.")
            else: st.error("Nouveau mot de passe trop court.")
    st.markdown("---"); st.subheader(T("del_title"))
    st.caption(T("del_caption"))
    with st.form("delete_form"):
        confirm_del = st.checkbox(T("del_check"))
        if st.form_submit_button(T("del_btn"), use_container_width=True):
            if confirm_del:
                uname = user; notify_admins("trash", f"Compte **{uname}** supprimé (RGPD).")
                delete_user(uname); clear_history(uname)
                for p in AVATAR_DIR.glob(f"{uname}.*"): p.unlink()
                delete_session(st.session_state.get("token")); delete_cookie(COOKIE_NAME); delete_cookie("ys_user")
                st.session_state.update(user=None, role=None, result=None, token=None, page="accueil", show_privacy=False); st.rerun()
            else: st.error("Cochez la case de confirmation.")
    render_footer(compact=True)

def _parse_hdate(h):
    try: return datetime.strptime(h["date"], "%d/%m/%Y %H:%M")
    except Exception: return datetime.min

def _trend_html(cur_val, prev_val, unit=""):
    diff = cur_val - prev_val
    if prev_val <= 0:
        if diff > 0: return f'<div class="kpi-trend up">↑ +{diff:g}{unit} {T("tr_week")}</div>'
        if diff < 0: return f'<div class="kpi-trend down">↓ {abs(diff):g}{unit} {T("tr_week")}</div>'
        return f'<div class="kpi-trend up">✓ {T("tr_stable")}</div>'
    pct = diff / prev_val * 100
    if abs(pct) > 999:
        cls = "up" if diff >= 0 else "down"; arrow = "↑" if diff >= 0 else "↓"
        return f'<div class="kpi-trend {cls}">{arrow} {diff:+g}{unit} {T("tr_week")}</div>'
    cls = "up" if pct >= 0 else "down"; arrow = "↑" if pct >= 0 else "↓"
    return f'<div class="kpi-trend {cls}">{arrow} {abs(pct):.1f}% {T("tr_vs")}</div>'

def render_bar_chart_html(values, labels, height=280):
    vmax = max(values) if values else 0
    if vmax <= 0: vmax = 1
    bars = ""
    for v, l in zip(values, labels):
        h = max(int(v / vmax * (height - 60)), 4)
        bars += f'<div class="bc-col"><div class="bc-bar" style="height:{h}px" title="{l} : {v:g} s"></div><span class="bc-lbl">{l}</span></div>'
    st.markdown(f'<div class="bc-wrap" style="height:{height}px">{bars}</div>', unsafe_allow_html=True)

def render_stats():
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    tier = 3 if role == "admin" else (0 if not user else get_tier(user))
    _acc, _acc_dark = get_accent()
    hero("chart", T("stats_title"), T("stats_sub"))
    hist = get_history(user)
    if not hist: st.caption("Aucune analyse."); render_footer(compact=True); return
    tt = sum(h.get("processing_time", 0) for h in hist)
    tw = sum(h.get("total_words", 0) for h in hist)
    week_ago = datetime.now() - timedelta(days=7)
    week_ago_prev = datetime.now() - timedelta(days=14)
    this_week = [h for h in hist if _parse_hdate(h) >= week_ago]
    prev_week = [h for h in hist if week_ago_prev <= _parse_hdate(h) < week_ago]
    n_this, n_prev = len(this_week), len(prev_week)
    tt_this = sum(h.get("processing_time", 0) for h in this_week)
    tt_prev = sum(h.get("processing_time", 0) for h in prev_week)
    tw_this = sum(h.get("total_words", 0) for h in this_week)
    tw_prev = sum(h.get("total_words", 0) for h in prev_week)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("book", 24)}</div><div class="kpi-label">{T("videos")}</div><div class="kpi-value">{len(hist)}</div>{_trend_html(n_this, n_prev)}</div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("clock", 24)}</div><div class="kpi-label">{T("total_time")}</div><div class="kpi-value">{tt:.0f}s</div>{_trend_html(tt_this, tt_prev, "s")}</div>', unsafe_allow_html=True)
    with k3:
        avg_chunks = sum(h.get('num_chunks',0) for h in hist)/len(hist)
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("zap", 24)}</div><div class="kpi-label">{T("avg_chunks")}</div><div class="kpi-value">{avg_chunks:.1f}</div><div class="kpi-trend up">✓ {T("tr_opt")}</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-icon">{ic("hash", 24)}</div><div class="kpi-label">{T("words_proc")}</div><div class="kpi-value">{tw:,}</div>{_trend_html(tw_this, tw_prev)}</div>', unsafe_allow_html=True)
    times = [h.get("processing_time", 0) for h in hist]
    labels = [f"V{i+1}" for i in range(len(hist))]
    if tier >= 2:
        e1, e2, e3 = st.columns(3)
        e1.metric(T("fastest"), f"{min(times):.0f} s"); e2.metric(T("slowest"), f"{max(times):.0f} s"); e3.metric(T("avg_time"), f"{tt/len(hist):.0f} s")
        render_bar_chart_html(times, labels)
    else:
        render_bar_chart_html(times[::-1], labels[::-1])
        st.markdown(f"<div class='q-item'>{ic('lock', 14)} Rapport détaillé réservé aux Premium et +</div>", unsafe_allow_html=True)
    if tier >= 3:
        st.markdown("---"); st.subheader(f"{T('weekly')} {T('wk_d')}")
        r1, r2, r3 = st.columns(3)
        r1.metric(f"{T('m_analyse')} {T('wk_d')}", n_this); r2.metric(f"{T('words')} {T('wk_d')}", f"{tw_this:,}"); r3.metric(f"{T('time')} {T('wk_d')}", f"{tt_this:.0f} s")
        rep = (f"# {T('weekly')} — {user}\n- {T('m_analyse')} : **{n_this}**\n- {T('words')} : **{tw_this:,}**\n- {T('time')} : **{tt_this:.0f} s**\n## Vidéos\n" + "\n".join(f"- {h['date']} — https://youtu.be/{h['video_id']}" for h in this_week))
        st.download_button(T("dl_report"), rep.encode("utf-8"), file_name=f"rapport_{user}.md", mime="text/markdown", use_container_width=True)
    render_footer(compact=True)

def render_historique():
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    tier = 3 if role == "admin" else (0 if not user else get_tier(user))
    _acc, _acc_dark = get_accent()
    hero("book", T("hist_title"), T("hist_sub"))
    hist = get_history(user); favs = load_favs(user)
    week_ago = datetime.now() - timedelta(days=7)
    recent = [h for h in hist if _parse_hdate(h) >= week_ago]
    s1, s2, s3 = st.columns(3)
    s1.metric(T("total"), len(hist)); s2.metric(T("this_week"), len(recent)); s3.metric(T("favs"), len(favs))
    f1, f2 = st.columns([3,1])
    with f1:
        q = ""
        if tier >= 2:
            q = st.text_input(T("search_ph"), placeholder="Rechercher…").lower()
        else:
            st.markdown(f"<div class='q-item'>{ic('lock', 14)} Recherche réservée aux Premium et +</div>", unsafe_allow_html=True)
    with f2:
        only_fav = st.checkbox("⭐ " + T("only_favs"))
    if tier == 0 and len(hist) > 10:
        st.caption(f"{T('plan_free')} : 10 ({len(hist)}).")
    shown = [h for h in hist
             if (not q or q in json.dumps(h, ensure_ascii=False).lower())
             and (not only_fav or h["video_id"] in favs)]
    if not shown:
        st.markdown(f"<div class='hist-card'><span class='hist-ico'>{ic('book', 18)}</span>"
                  f"<div class='hist-left'><div><b>Aucune analyse</b><br>"
                  f"<small>—</small></div></div></div>", unsafe_allow_html=True)
        render_footer(compact=True); return
    for h in shown:
        vid = h["video_id"]; is_fav = vid in favs
        st.markdown(f"""<div class="hist-card">
<span class="hist-ico">{ic("film", 18)}</span>
<div class="hist-left"><div>
<b>{_html.escape(h.get("title", "Résumé - " + vid))}</b><br>
<small>{h["date"]} • {h["lang"].upper()} • {h.get("total_words",0):,} {T("words")} • {h.get("processing_time",0)} s</small>
</div></div>
<div class="hist-fav">{"⭐" if is_fav else ""}</div>
</div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button(T("open_analyse"), key=f"open_{vid}_{h['date']}", use_container_width=True):
                st.session_state.result = h; st.session_state.page = "analyse"; st.rerun()
        with c2:
            if st.button(("⭐" if is_fav else "☆") + " " + T("add_fav"),
                         key=f"fav_{vid}_{h['date']}", use_container_width=True):
                toggle_fav(user, vid); st.rerun()
    st.markdown("---")
    if st.button(T("clear_hist"), use_container_width=True):
        clear_history(user); st.rerun()
    render_footer(compact=True)

def render_config():
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    tier = 3 if role == "admin" else (0 if not user else get_tier(user))
    hero("sliders", T("set_title"), T("set_sub"))
    SECTIONS = [(T("set_title"),[("general",T("general"),"sliders"),("compte",T("account"),"user"),("confidentialite",T("privacy"),"shield"),("facturation",T("billing"),"card"),("capacites",T("caps"),"cpu")]),
    ("Desktop",[("bureau",T("general"),"monitor"),("extensions","Extensions","tool"),("developpeur","Dev","code")]),
    (T("personalization"),[("competences","Skills","spark"),("connecteurs","Connect","link"),("plugins","Plugins","tool"),("memoire","Memory","clock")])]
    query = st.text_input(T("set_search"), placeholder="...", label_visibility="collapsed")
    c_nav, c_body = st.columns([1, 3], gap="large")
    with c_nav:
        st.markdown('<div class="setnav"></div>', unsafe_allow_html=True)
        for group_name, grp in SECTIONS:
            st.markdown(f'<div class="qcap">{group_name}</div>', unsafe_allow_html=True)
            for key, label, icon in grp:
                if query and query.lower() not in label.lower(): continue
                if st.button(f"{label}", key=f"set_{key}", use_container_width=True, type="primary" if st.session_state.cfg_section == key else "secondary"): st.session_state.cfg_section = key; st.rerun()
    with c_body:
        st.markdown('<div class="setbody"></div>', unsafe_allow_html=True); sec = st.session_state.cfg_section
        if sec == "general":
            st.subheader(T("general"))
            a1, a2 = st.columns([2,1]); a1.markdown(f"**{T('appearance')}**", unsafe_allow_html=True)
            with a2:
                t1, t2 = st.columns(2)
                with t1:
                    if st.button(T("light"), use_container_width=True, type="primary" if st.session_state.theme=="light" else "secondary"): st.session_state.theme="light"; set_cookie("ys_theme","light",max_age=365*24*3600); st.rerun()
                with t2:
                    if st.button(T("dark"), use_container_width=True, type="primary" if st.session_state.theme=="dark" else "secondary"): st.session_state.theme="dark"; set_cookie("ys_theme","dark",max_age=365*24*3600); st.rerun()
            st.markdown("---")
            st.subheader(T("language"))
            cur_lang = st.session_state.cfg_lang
            cl = st.selectbox(T("language"), list(LANGS.keys()), index=list(LANGS.keys()).index(cur_lang) if cur_lang in LANGS else 0, format_func=lambda l: LANGS[l], key="sel_lang")
            if cl != cur_lang: set_language(cl)
            _ui = LANGS.get(st.session_state.cfg_lang,"fr"); _tgt = LANGS.get(st.session_state.cfg_target,"fr")
            st.info(f"🌐 **{_ui}** — {T('language')} ✓ | {T('chip_tr')} {T('m_analyse')} → **{_tgt}**")
            st.markdown("---"); b1, b2 = st.columns([2,1]); b1.markdown(f"**{T('font')}**", unsafe_allow_html=True)
            with b2: st.selectbox(T("font"), ["Manrope","Sora","Système","Adapté aux dyslexiques"], key="cfg_font", label_visibility="collapsed")
            st.markdown("---"); st.checkbox(f"**{T('motion')}**", key="cfg_reduce_motion")
            st.markdown("---"); st.subheader(T("personalization"))
            _presets = {"Bleu océan":"#2E6DB4","Teal":"#14B8A6","Violet":"#8B5CF6","Orange":"#F97316","Vert":"#22C55E",
            "Rouge":"#EF4444","Indigo":"#6366F1","Or":"#F59E0B","Rose":"#EC4899","Cyan":"#06B6D4"}
            _cur = st.session_state.get("cfg_accent","#2E6DB4")
            _vals = list(_presets.values()); _names = list(_presets.keys())
            _idx = _vals.index(_cur) if _cur in _vals else 0
            p1, p2 = st.columns(2)
            with p1:
                _sel = st.selectbox(T("presets"), _names, index=_idx)
                if _presets[_sel] != _cur:
                    st.session_state.cfg_accent = _presets[_sel]; _save_appearance(); st.rerun()
            with p2:
                _hex = st.color_picker(T("custom_color"), value=_cur)
                if _hex != _cur:
                    st.session_state.cfg_accent = _hex; _save_appearance(); st.rerun()
            s1, s2 = st.columns(2)
            with s1: st.slider(T("text_size"), 14, 20, int(st.session_state.get("cfg_font_size",16)), key="cfg_font_size", on_change=_save_appearance)
            with s2: st.slider(T("line_height"), 1.4, 2.0, float(st.session_state.get("cfg_line_height",1.6)), key="cfg_line_height", on_change=_save_appearance)
            st.markdown(f'<div class="note-card"><div class="note-num">A</div><div class="note-text">{T("preview")} — <b>{st.session_state.cfg_accent}</b> • {int(st.session_state.cfg_font_size)} px • {st.session_state.cfg_line_height}</div></div>', unsafe_allow_html=True)
            st.markdown("---"); st.subheader(T("voice"))
            v1, v2 = st.columns(2)
            with v1: st.selectbox(T("language"), ["fr","en","es","de"], key="cfg_voice_lang", format_func=lambda l: LANGS[l])
            with v2: st.selectbox(T("speed"), ["Lent","Normal","Rapide"], key="cfg_voice_speed")
            st.selectbox(T("style"), ["Normal","Décontracté","Professionnel"], key="cfg_voice_style")
            st.markdown("---"); st.subheader(T("notif_pref"))
            st.checkbox(f"**{T('completion')}**", key="cfg_notif_complete"); st.checkbox(f"**{T('weekly')}**", key="cfg_notif_weekly")
        elif sec == "compte":
            st.subheader(T("profile"))
            _av = get_avatar_b64(user)
            if _av: st.markdown(f'<img src="{_av}" class="big-avatar">', unsafe_allow_html=True)
            else: st.markdown(f'<div class="big-avatar">{(user or "??")[:2].upper()}</div>', unsafe_allow_html=True)
            up = st.file_uploader("Avatar", type=["png","jpg","jpeg","webp"])
            if up:
                AVATAR_DIR.mkdir(parents=True, exist_ok=True); ext = up.name.rsplit(".",1)[-1].lower()
                for old in AVATAR_DIR.glob(f"{user}.*"): old.unlink()
                (AVATAR_DIR / f"{user}.{ext}").write_bytes(up.read()); st.success("Photo enregistrée"); st.rerun()
            st.text_input(T("fullname"), key="prof_fullname"); st.text_input(T("callname"), key="prof_callname")
            st.selectbox(T("job"), ["Étudiant","Enseignant","Créateur de contenu","Professionnel","Autre"], key="prof_job")
            st.text_area(T("instructions"), key="prof_instructions", placeholder="ex. : garder les explications brèves")
            st.markdown("---")
            if st.button(T("change_pwd"), use_container_width=True): st.session_state.page = "profil"; st.rerun()
        elif sec == "confidentialite":
            st.subheader(T("privacy")); st.write("RGPD ✓")
            if st.button(T("see_policy"), use_container_width=True): st.session_state.show_privacy = True; st.rerun()
        elif sec == "facturation":
            st.subheader(T("billing")); cur = "premium_plus" if role == "admin" else get_plan(user)
            st.write(f"{T('current_plan')} : **{PLANS[cur]['name'] if cur != 'free' else T('plan_free')}**")
            if st.button(T("manage_plan"), use_container_width=True): st.session_state.page = "premium"; st.rerun()
        elif sec == "capacites":
            st.subheader(T("caps"))
            if tier >= 2: st.selectbox(T("model"), ["rapide","qualite"], key="cfg_model", format_func=lambda m: "Rapide" if m=="rapide" else "Qualité")
            else: st.markdown(f"<div class='q-item'>{ic('lock',14)} Modèle Qualité réservé aux Premium et +</div>", unsafe_allow_html=True)
            st.checkbox(T("turbo"), key="cfg_turbo")
            st.slider(T("kw_count"), 5, 20, key="cfg_kw_n"); st.slider(T("q_count"), 3, 10, key="cfg_q_n")
            st.slider(T("chunk_size"), 1200, 4000, step=200, key="cfg_chunk")
            st.checkbox(T("extract_kw"), key="cfg_kw"); st.checkbox(T("gen_q"), key="cfg_qa")
        elif sec == "bureau": st.subheader(T("general")); st.checkbox(T("motion"), key="cfg_reduce_motion")
        elif sec == "extensions": st.subheader("Extensions"); st.write("Obsidian, Notion…")
        elif sec == "developpeur": st.subheader("Dev"); st.write("API & clés (bientôt).")
        elif sec == "competences": st.subheader("Skills"); st.write("—")
        elif sec == "connecteurs": st.subheader("Connect"); st.write("—")
        elif sec == "plugins": st.subheader("Plugins"); st.write("—")
        elif sec == "memoire": st.subheader("Memory"); st.write("—")
    render_footer(compact=True)