import re
from difflib import SequenceMatcher


def chunk_text(text, chunk_size=1200):
    sentences = text.split(". ")
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def remove_repetitions(text, threshold=0.72):
    """Supprime les phrases identiques OU presque identiques (fuzzy)."""
    sentences = [s.strip() for s in text.split(". ") if s.strip()]
    kept = []
    for s in sentences:
        sl = s.lower().strip()
        dup = False
        for k in kept:
            kl = k.lower().strip()
            if sl == kl or sl in kl or kl in sl:
                dup = True
                break
            if SequenceMatcher(None, sl, kl).ratio() > threshold:
                dup = True
                break
        if not dup:
            kept.append(s)
    out = ". ".join(kept)
    return out + "." if out else text


def format_notes(notes_list):
    formatted = "📝 RÉSUMÉ DE LA VIDÉO\n" + "=" * 50 + "\n\n"
    for i, note in enumerate(notes_list, 1):
        formatted += f"{i}. {remove_repetitions(note)}\n\n"
    return formatted


GLOSSAIRE = [
    (r"\bflotteurs?\b", "floats"),
    (r"\btuiles?\b", "tuples"),
    (r"accessoires bouclés", "accolades"),
    (r"fonction de plage", "fonction range"),
    (r"\bAlors que les boucles\b", "Les boucles while"),
    (r"alors que les boucles", "les boucles while"),
    (r"opérateur non\b", "opérateur not"),
    (r"priorité opérateur", "priorité des opérateurs"),
    (r"la méthode de recherche", "la méthode find"),
    (r"la méthode de remplacement", "la méthode replace"),
    (r"variable d'élément", "variable item"),
    (r"l'index de démarrage", "l'index de début"),
    (r"appelée entrée pour", "appelée input pour"),
    (r"\bEn maths\b", "En mathématiques"),
]


def polish_translation(text):
    for pattern, repl in GLOSSAIRE:
        text = re.sub(pattern, repl, text)
    text = re.sub(r"\s+", " ", text).strip()
    text = _dedup_words(text)
    return text


def _dedup_words(text):
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\b(\w[\w'-]*)\s+\1\b", r"\1", text, flags=re.IGNORECASE)
    return text


def extract_action_points(notes, max_n=6):
    cues = ("il faut", "vous devez", "tu dois", "n'oubliez pas", "pensez à",
            "essayez", "utilisez", "vous pouvez", "il est important",
            "assurez-vous", "veillez à", "commencez par",
            "you should", "you must", "make sure")
    actions = []
    for n in notes:
        for s in n.split(". "):
            low = s.lower()
            if any(c in low for c in cues) and len(s) > 20:
                actions.append(s.strip().rstrip(".") + ".")
            if len(actions) >= max_n:
                return actions
    return actions


