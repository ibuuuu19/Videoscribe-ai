import re
from difflib import SequenceMatcher
from difflib import SequenceMatcher
from collections import Counter

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

def remove_repetitions(text, threshold=0.75):
    """
    Supprime les phrases identiques ou presque identiques (fuzzy).

    Améliorations v2 :
    - Détecte les doublons même avec 1-2 mots de différence à la fin
    - Détecte les répétitions "courtes" (< 20 chars) qui se répètent 2+ fois
    - Supprime les phrases tronquées ou incomplètes
    - Nettoie les hésitations ("euh", "bah", "là", "[musique]", etc.)
    """
    if not text or not isinstance(text, str):
        return text

    # ── 0. NOUVEAU : nettoie les doublons de MOTS consécutifs ──
    # "été été" → "été", "de faire de faire" → "de faire"
    text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)
    # "de faire de faire" → détecte les groupes de 2 mots
    text = re.sub(r'\b(\w+\s+\w+)(\s+\1\b)+', r'\1', text, flags=re.IGNORECASE)

    # ── 0bis. Nettoie les lettres doublées en fin de mot ──
    # "préparéé" → "préparé", "dégageuveuve" → "dégageuve"
    text = re.sub(r'(\w)\1{2,}', r'\1\1', text)   # 3+ lettres → 2 max
    # Pour les accents : "éé" → "é"
    text = re.sub(r'([éèêëàâîïôûùç])\1+', r'\1', text, flags=re.IGNORECASE)
    
    
    if not text or not isinstance(text, str):
        return text

    # ── 1. Nettoie les artefacts de transcription ──
    text = re.sub(r'\[musique\]|\[music\]|\[applaudissements\]|\[rires\]', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()

    # ── 2. Découpe en phrases (gère ".", "!", "?", "...") ──
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip().rstrip('.!?').strip() for s in raw_sentences if s.strip()]

    if not sentences:
        return text

    # ── 3. Filtre les phrases trop courtes / vides / hésitations ──
    HESITATIONS = {'euh', 'bah', 'ben', 'hein', 'ok', 'okay', 'voilà', 'voila', 'là', 'bon'}
    filtered = []
    for s in sentences:
        words = s.split()
        # Trop court (< 3 mots sauf si phrase complète)
        if len(words) < 3 and len(s) < 15:
            continue
        # Que des hésitations
        if all(w.lower().strip(',.!?') in HESITATIONS for w in words):
            continue
        filtered.append(s)

    # ── 4. Dédoublonnage fuzzy ──
    kept = []
    for s in filtered:
        sl = s.lower().strip()
        dup = False

        for k in kept:
            kl = k.lower().strip()

            # Doublon exact
            if sl == kl:
                dup = True
                break

            # Similarité fuzzy
            ratio = SequenceMatcher(None, sl, kl).ratio()
            if ratio > threshold:
                dup = True
                break

            # Inclusion stricte (l'un contient l'autre, longueur suffisante)
            if len(sl) > 20 and len(kl) > 20:
                if sl in kl or kl in sl:
                    dup = True
                    break

            # ✅ NOUVEAU : préfixe commun long (ex: "J'ai besoin de m'hydrater là" vs "J'ai besoin de m'hydrater là c'eux-nous")
            # Si les 30 premiers caractères sont identiques → doublon
            if len(sl) > 25 and len(kl) > 25 and sl[:30] == kl[:30]:
                dup = True
                break

        if not dup:
            kept.append(s)

    # ── 5. Reconstruit ──
    out = ". ".join(kept)
    if out and not out.endswith(('.', '!', '?')):
        out += "."
    return out

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
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
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


