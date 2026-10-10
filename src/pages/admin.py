"""
Page Admin — Gestion des comptes clients et supervision.

Contient :
- render_admin() : Terminal administrateur (vue d'ensemble, clients,
  création, messages)

Extrait de app.py pour alléger le fichier principal (~91 lignes).

Usage:
    from src.pages.admin import render_admin
"""

import pandas as pd
import streamlit as st

from src.ui.i18n import T
from src.ui.components import ic
from src.ui.layout import hero, render_footer
from src.core.config import PLANS, PAYMENT_WAVE, CONTACT_EMAIL
from src.user_manager import (
    list_users, get_plan, register_user,
    delete_user, set_active, reset_password, set_plan,
    ADMIN_USER, ADMIN_PASS,
)
from src.history_manager import get_history, clear_history
from src.revenue_manager import record_revenue, get_revenues
from src.contact_manager import get_messages, mark_read, delete_message
from src.notification_manager import notify


# ═══════════════════════════════════════════════════════════════
# ⚠️ La fonction render_admin a été copiée automatiquement
#    depuis app.py par le script extract_admin.py
# ═══════════════════════════════════════════════════════════════

def render_admin():
    hero("tool", T("admin_title"), T("admin_sub"), [f'{ic("users", 13)} Clients', f'{ic("chart", 13)} Stats', f'{ic("card", 13)} {T("billing")}', f'{ic("msg", 13)} {T("tab_msgs")}'])
    
    # ═══ Sécurisation : lecture des secrets (marche en local ET cloud) ═══
    try:
        _sec_admin_user = st.secrets.get("ADMIN_USER", "admin")
        _sec_admin_pass = st.secrets.get("ADMIN_PASS", "admin123")
    except Exception:
        _sec_admin_user = "admin"
        _sec_admin_pass = "admin123"
    
    if ADMIN_USER == _sec_admin_user and ADMIN_PASS == _sec_admin_pass:
        st.warning("Mot de passe admin par défaut — personnalisez-le.")
    
    users = list_users(); rows = []
    for uname, u in users.items():
        hist = get_history(uname); pl = get_plan(uname)
        rows.append({"Utilisateur": uname, "Rôle": u.get("role","client"), "Plan": PLANS[pl]["name"] if pl != "free" else "Gratuit",
        "Email": u.get("email") or "—", "Créé le": u.get("created_at","")[:10], "Analyses": len(hist),
        "Temps (s)": round(sum(h.get("processing_time",0) for h in hist),1), "Statut": "Actif" if u.get("active", True) else "Suspendu"})
    df_users = pd.DataFrame(rows); clients = {u: d for u, d in users.items() if d.get("role") != "admin"}
    revenue = sum(PLANS[get_plan(u)]["monthly"] for u in users if get_plan(u) != "free")
    tab_stats, tab_clients, tab_create, tab_msgs = st.tabs([T("tab_overview"),T("tab_clients"),T("tab_create"),T("tab_msgs")])
    with tab_stats:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric(T("accounts"), len(users)); c2.metric(T("total_analyses"), int(df_users["Analyses"].sum())); c3.metric(T("cum_time"), f"{df_users['Temps (s)'].sum():.0f} s")
        c4.metric(T("paying"), sum(1 for u in users if get_plan(u) != "free")); c5.metric(T("rev_month"), f"${revenue:,.2f}")
        st.subheader(T("analyses_by_account")); st.bar_chart(pd.DataFrame({"Analyses": [len(get_history(u)) for u in users]}, index=list(users.keys())))
        st.subheader(T("revenues")); revs = get_revenues(); gA, gB = st.columns(2)
        with gA:
            total_collected = sum(r["amount"] for r in revs); st.metric(T("total_collected"), f"${total_collected:,.2f}")
            if revs: daily = pd.DataFrame(revs).groupby("date")["amount"].sum(); st.bar_chart(daily); st.caption("—")
            else: st.caption("—")
        with gB:
            st.metric("MRR", f"${revenue:,.2f}")
            counts = {p["name"]: sum(1 for u in users if get_plan(u)==k) for k,p in PLANS.items()}
            st.bar_chart(pd.DataFrame({"Abonnés": list(counts.values())}, index=list(counts.keys()))); st.caption("—")
        if revs: st.subheader(T("last_transactions")); st.dataframe(pd.DataFrame(revs[::-1]), use_container_width=True, hide_index=True)
    with tab_clients:
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        st.download_button("CSV", df_users.to_csv(index=False).encode("utf-8"), file_name="clients.csv", mime="text/csv")
        st.markdown("---"); st.subheader(T("tab_clients"))
        if clients:
            target = st.selectbox("Client", list(clients.keys())); is_active = clients[target].get("active", True)
            a1,a2,a3,a4 = st.columns(4)
            with a1:
                if st.button("Suspendre/Activer", use_container_width=True): set_active(target, not is_active); st.rerun()
            with a2:
                if st.button("Réinit. mdp", use_container_width=True): st.session_state[f"reset_{target}"] = True
            with a3:
                plan_opts = ["free","basique","premium","premium_plus"]
                new_plan = st.selectbox("Plan (30 j)", plan_opts, index=plan_opts.index(get_plan(target)), format_func=lambda p: PLANS[p]["name"] if p != "free" else "Gratuit", key=f"plan_{target}")
                if st.button("Appliquer", use_container_width=True):
                    set_plan(target, new_plan, 30)
                    if new_plan != "free": record_revenue(target, new_plan, PLANS[new_plan]["monthly"], 30, "manuel")
                    st.rerun()
            with a4:
                if st.button("Supprimer", use_container_width=True):
                    if delete_user(target): clear_history(target); st.rerun()
            if st.session_state.get(f"reset_{target}"):
                with st.form(f"reset_form_{target}"):
                    new_pass = st.text_input(T("pwd_new"), type="password")
                    if st.form_submit_button(T("pwd_confirm")):
                        if reset_password(target, new_pass): st.session_state.pop(f"reset_{target}", None); st.success("✓"); st.rerun()
                        else: st.error("6 min.")
            st.subheader(f"Historique : {target}"); hist = get_history(target)
            if hist: st.dataframe(pd.DataFrame([{"Date":h["date"],"Vidéo":h["video_id"],"Langue":h["lang"],"Chunks":h["num_chunks"],"Mots":h["total_words"],"Temps (s)":h["processing_time"]} for h in hist]), use_container_width=True, hide_index=True)
            else: st.caption("—")
        else: st.info("—")
    with tab_create:
        with st.form("create_client"):
            new_u = st.text_input(T("username")); new_e = st.text_input("Email"); new_p = st.text_input(T("password"), type="password")
            if st.form_submit_button(T("register"), use_container_width=True):
                ok, msg = register_user(new_u, new_p, new_e, role="client")
                if ok: notify(new_u.strip().lower(), "spark", "Bienvenue !"); st.success(f"{msg}")
                else: st.error(f"{msg}")
    with tab_msgs:
        msgs = get_messages(); st.metric("Non lus", sum(1 for m in msgs if not m["read"]))
        if msgs:
            for m in msgs:
                with st.expander(f"[{m['urgency'].upper()}] {m['user']} — {m['subject']}"):
                    st.write(m["message"]); b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Lu", key=f"read_{m['id']}"): mark_read(m['id']); st.rerun()
                    with b2:
                        if st.button("Suppr", key=f"del_{m['id']}"): delete_message(m['id']); st.rerun()
        else: st.caption("—")
    render_footer(compact=True)
    

# ⚠️ render_register_wizard, render_login, render_register_page extraits dans src/pages/auth.py