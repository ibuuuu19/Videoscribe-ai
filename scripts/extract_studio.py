"""
Script d'extraction du Studio depuis app.py vers src/pages/studio.py.

Enveloppe le bloc dans une fonction render_studio_page() avec les
variables locales (user, role, tier, is_guest) récupérées de session_state.
"""

from pathlib import Path

content = Path("app.py").read_text(encoding="utf-8")
lines = content.split("\n")

# Bornes
start_marker = "# ═══════════════ PAGE ANALYSE — STUDIO PREMIUM ═══════════════"
end_marker = "# ═══════════════ PAGE PARTAGE PUBLIC ═══════════════"

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if line.startswith(start_marker) and start_idx is None:
        start_idx = i
    if start_idx is not None and line.startswith(end_marker):
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print(f"❌ Bornes non trouvées")
    exit(1)

block = "\n".join(lines[start_idx:end_idx]).rstrip()
print(f"✅ Bloc Studio extrait : lignes {start_idx+1} à {end_idx} ({len(block.splitlines())} lignes)")

# Indenter le bloc (ajouter 4 espaces à chaque ligne non vide)
block_indented = "\n".join("    " + line if line.strip() else line for line in block.split("\n"))

# En-tête de la fonction
header = '''def render_studio_page():
    """Affiche la page Studio complète (analyse + résultats)."""
    # ═══ Variables locales ═══
    user = st.session_state.get("user")
    role = st.session_state.get("role", "client")
    is_guest = role == "visiteur"
    tier = 3 if role == "admin" else (0 if is_guest else get_tier(user))

    # ═══ Configuration depuis session_state ═══
    translate_to_fr = st.session_state.cfg_translate
    extract_kw = st.session_state.cfg_kw
    generate_qa = st.session_state.cfg_qa
    model_choice = st.session_state.cfg_model
    turbo = st.session_state.cfg_turbo
    num_keywords = st.session_state.cfg_kw_n
    num_questions = st.session_state.cfg_q_n
    chunk_size = st.session_state.cfg_chunk

    # ═══ État du Studio ═══
    if st.query_params.get("nlhide") == "1":
        st.session_state.nl_hide = True
    if "studio_panel_open" not in st.session_state:
        st.session_state.studio_panel_open = True

    # ═══ Code du Studio (extrait de app.py) ═══
'''

full_func = header + block_indented

# Écrire dans studio.py
studio_path = Path("src/pages/studio.py")
studio_content = studio_path.read_text(encoding="utf-8")

marker = "# ═══ PLACEHOLDER — À REMPLIR PAR extract_studio.py ═══"
if marker in studio_content:
    studio_content = studio_content.replace(marker, full_func)
    studio_path.write_text(studio_content, encoding="utf-8")
    print(f"\n✅ studio.py mis à jour : {len(studio_content.splitlines())} lignes")
else:
    print("❌ Placeholder non trouvé dans studio.py")