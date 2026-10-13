"""
Supprime le bloc Studio d'app.py et ajoute l'import.
"""

from pathlib import Path

content = Path("app.py").read_text(encoding="utf-8")
lines = content.split("\n")

# Bornes : du commentaire PAGE ANALYSE jusqu'au commentaire PAGE PARTAGE PUBLIC
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
    print(f"❌ Bornes non trouvées : start={start_idx}, end={end_idx}")
    exit(1)

removed = end_idx - start_idx
# Remplacer par un commentaire
lines[start_idx:end_idx] = [
    "# ═══════════════ PAGE ANALYSE — STUDIO PREMIUM ═══════════════",
    "# ⚠️ Le Studio a été extrait dans src/pages/studio.py",
    "# La fonction render_studio_page() est appelée dans le routage ci-dessus.",
    "",
]

Path("app.py").write_text("\n".join(lines), encoding="utf-8")
print(f"✅ {removed} lignes supprimées d'app.py")
print(f"✅ app.py : {len(lines)} lignes")