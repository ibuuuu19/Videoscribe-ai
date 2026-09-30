import os
from datetime import datetime
from pathlib import Path
from fpdf import FPDF

OUTPUT_DIR = Path("output")
PDF_DIR = OUTPUT_DIR / "pdf"
MD_DIR = OUTPUT_DIR / "markdown"
PDF_DIR.mkdir(parents=True, exist_ok=True)
MD_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Polices Unicode système ----------
FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
]

def _find_unicode_font():
    for regular, bold in FONT_CANDIDATES:
        if os.path.exists(regular):
            return regular, (bold if os.path.exists(bold) else regular)
    return None, None

# ---------- Nettoyage (fallback si pas de police Unicode) ----------
_REPLACEMENTS = {
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "…": "...", "—": "-", "–": "-", "→": "->",
    "•": "-", "œ": "oe", "Œ": "OE", "€": "EUR",
    "\u00a0": " ", "\u200b": "",
}

def _clean(text):
    for k, v in _REPLACEMENTS.items():
        text = text.replace(k, v)
    return text.encode("latin-1", errors="ignore").decode("latin-1")


class SmartPDF(FPDF):
    def __init__(self):
        super().__init__()
        regular, bold = _find_unicode_font()
        self.unicode = regular is not None
        if self.unicode:
            self.add_font("Smart", "", regular)
            self.add_font("Smart", "B", bold)
        self._family = "Smart" if self.unicode else "Helvetica"

    def put(self, text, size, bold=False, color=(0, 0, 0), max_len=None):
        """Écrit du texte en toute sécurité, avec largeur explicite."""
        text = str(text)
        if not self.unicode:
            text = _clean(text)
        if max_len and len(text) > max_len:
            text = text[:max_len - 3] + "..."

        self.set_font(self._family, "B" if bold else "", size)
        self.set_text_color(*color)
        # Force le retour à la marge gauche + largeur explicite
        self.set_x(self.l_margin)
        self.multi_cell(w=self.epw, h=6, text=text, new_x="LMARGIN", new_y="NEXT")


def export_to_markdown(data, filename):
    path = MD_DIR / f"{filename}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# 📹 {data['title']}\n\n")
        f.write(f"**URL:** {data['url']}\n")
        f.write(f"**Date:** {data['date']}\n")
        f.write(f"**Langue détectée:** {data['lang']}\n\n")
        f.write("---\n\n")
        f.write("## 📝 Résumé\n\n")
        for i, note in enumerate(data["notes"], 1):
            f.write(f"{i}. {note}\n\n")
        if data.get("keywords"):
            f.write("## 🔑 Mots-clés\n\n")
            for kw, score in data["keywords"]:
                f.write(f"- **{kw}** _(score: {score})_\n")
            f.write("\n")
        if data.get("questions"):
            f.write("## ❓ Questions à explorer\n\n")
            for q in data["questions"]:
                f.write(f"- {q}\n")
    print(f"📄 Markdown sauvegardé: {path}")
    return str(path)


def export_to_pdf(data, filename):
    path = PDF_DIR / f"{filename}.pdf"

    pdf = SmartPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ----- Titre -----
    pdf.put(data["title"], 18, bold=True, color=(18, 36, 74), max_len=120)
    pdf.put(f"URL: {data['url']}", 9, color=(100, 100, 100), max_len=150)
    pdf.put(f"Date: {data['date']} | Langue: {data['lang']}", 9, color=(100, 100, 100))
    pdf.ln(4)

    # ----- Résumé -----
    pdf.put("Resume", 14, bold=True, color=(18, 36, 74))
    for i, note in enumerate(data["notes"], 1):
        pdf.put(f"{i}. {note}", 11)
        pdf.ln(1)

    # ----- Mots-clés -----
    if data.get("keywords"):
        pdf.ln(3)
        pdf.put("Mots-cles", 14, bold=True, color=(18, 36, 74))
        for kw, score in data["keywords"]:
            pdf.put(f"- {kw} (score: {score})", 11)

    # ----- Questions -----
    if data.get("questions"):
        pdf.ln(3)
        pdf.put("Questions a explorer", 14, bold=True, color=(18, 36, 74))
        for q in data["questions"]:
            pdf.put(f"- {q}", 11, max_len=200)

    pdf.output(path)
    print(f"📄 PDF sauvegardé: {path}")
    return str(path)


def export_to_obsidian(data, filename):
    kws = data.get("keywords", [])
    front = ["---", f'title: "{data["title"]}"', f"source: {data['url']}",
             f"date: {data['date']}",
             "tags: [youtube, resume" +
             (", " + ", ".join(k.replace(' ', '_') for k, _ in kws[:6]) if kws else "") +
             "]", "---", ""]
    body = [f"# 🎥 {data['title']}", "", f"> Vidéo : {data['url']}", ""]
    for i, n in enumerate(data["notes"], 1):
        body += [f"## Section {i}", "", n, ""]
    if kws:
        body += ["## 🔑 Mots-clés", "", " ".join(f"[[{k}]]" for k, _ in kws), ""]
    path = Path("exports") / f"{filename}_obsidian.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(front + body), encoding="utf-8")
    return str(path)


def export_to_notion(data, filename):
    lines = [f"# {data['title']}", "", f"**Vidéo** : {data['url']}  ",
             f"**Date** : {data['date']}", "", "## 📝 Résumé structuré", ""]
    for i, n in enumerate(data["notes"], 1):
        lines.append(f"{i}. {n}")
    if data.get("keywords"):
        lines += ["", "## 🔑 Mots-clés", ""]
        lines += [f"- {k} ({s})" for k, s in data["keywords"]]
    if data.get("questions"):
        lines += ["", "## ❓ Questions à explorer", ""]
        lines += [f"- {q}" for q in data["questions"]]
    path = Path("exports") / f"{filename}_notion.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)
