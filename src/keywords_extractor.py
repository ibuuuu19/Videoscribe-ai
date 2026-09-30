from keybert import KeyBERT

_kb = None


def _get_kb():
    global _kb
    if _kb is None:
        try:
            _kb = KeyBERT(model="paraphrase-multilingual-MiniLM-L12-v2")
        except Exception:
            _kb = KeyBERT()
    return _kb


# Stopwords français en LISTE (pas en set — KeyBERT refuse les sets)
STOPWORDS_FR = [
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "l", "et", "ou", "mais",
    "donc", "or", "ni", "car", "à", "au", "aux", "ce", "cet", "cette", "ces", "en",
    "dans", "par", "pour", "sur", "avec", "sans", "sous", "que", "qui", "quoi",
    "dont", "où", "est", "sont", "être", "avoir", "a", "ont", "été", "était",
    "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "me", "te",
    "se", "ne", "pas", "plus", "moins", "très", "bien", "aussi", "trop", "assez",
    "peu", "beaucoup", "tout", "tous", "toute", "toutes", "autre", "autres",
    "même", "mêmes", "chaque", "plusieurs", "mon", "ton", "son", "ma", "ta", "sa",
    "mes", "tes", "ses", "notre", "votre", "leur", "nos", "vos", "leurs", "y",
    "c", "qu", "n", "s", "t", "m", "j", "ai", "as", "avons", "avez", "fait",
    "faire", "comme", "ainsi", "alors", "quand", "comment", "pourquoi", "si",
    "ici", "là", "ceci", "cela", "ça", "lui", "eux", "après", "avant",
    "pendant", "depuis", "vers", "chez", "entre", "contre", "selon", "malgré",
    "afin", "ensuite", "puis", "encore", "toujours", "jamais", "déjà", "vraiment",
    "peut", "peuvent", "doit", "doivent", "faut", "sera", "seront", "serait",
    "été", "avons", "avez", "ont", "suis", "es", "sommes", "êtes",
]


def extract_keywords(text, top_n=10, lang="fr"):
    """Extrait les mots-clés avec KeyBERT."""
    if not text or len(text) < 30:
        return []
    
    kb = _get_kb()
    
    # Utilise la liste (pas un set !)
    stop_list = STOPWORDS_FR if lang == "fr" else "english"
    
    try:
        kws = kb.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            stop_words=stop_list,
            top_n=top_n * 2,
            use_maxsum=True
        )
    except Exception as e:
        print(f"⚠️ KeyBERT: {e} → fallback")
        try:
            kws = kb.extract_keywords(text, top_n=top_n * 2)
        except Exception:
            return []
    
    # Filtrage léger post-extraction
    filtered = []
    for kw, score in kws:
        kwl = kw.lower().strip()
        
        # Longueur raisonnable (3-40 chars)
        if len(kwl) < 3 or len(kwl) > 40:
            continue
        
        # Pas de chiffres purs
        if kwl.isdigit():
            continue
        
        # Évite les doublons par substring
        is_dup = any(kwl in f[0].lower() or f[0].lower() in kwl for f in filtered)
        if is_dup:
            continue
        
        filtered.append((kw, round(float(score), 3)))
        
        if len(filtered) >= top_n:
            break
        
        # Polish final : rejette les n-grams commençant par un verbe
        VERB_STARTERS = {"lancé", "créer", "utiliser", "permet", "propose", "offre",
                        "donne", "montre", "explique", "dit", "parle", "fait"}
        filtered = [(kw, s) for kw, s in filtered
                    if not any(kw.lower().startswith(v) for v in VERB_STARTERS)]
    return filtered
