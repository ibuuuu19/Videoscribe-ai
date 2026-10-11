"""
Module de traduction — Helsinki-NLP + GoogleTranslator + cache.

Priorité :
1. Cache local (instantané)
2. Helsinki-NLP opus-mt (rapide, qualité moyenne)
3. GoogleTranslator (fallback, qualité élevée)
"""

import re
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.cache import (
    get_translation_batch, set_translation_batch,
)

MAX_CHARS = 4000

_pipes = {}
LOCAL_PAIRS = {
    ("en", "fr"), ("fr", "en"),
    ("es", "fr"), ("fr", "es"),
    ("de", "fr"), ("fr", "de"),
    ("es", "en"), ("en", "es"),
    ("de", "en"), ("en", "de"),
}


def _get_pipe(src, dest):
    if (src, dest) not in _pipes:
        from transformers import pipeline
        print(f"🌍 Chargement Helsinki-NLP/opus-mt-{src}-{dest}...")
        _pipes[(src, dest)] = pipeline("translation", model=f"Helsinki-NLP/opus-mt-{src}-{dest}")
    return _pipes[(src, dest)]


def _clean_spacing(text):
    return re.sub(r'\.([A-ZÀ-ÿ0-9])', r'. \1', text)


def _local(batch, src, dest):
    pipe = _get_pipe(src, dest)
    return [r["translation_text"] for r in pipe(batch, max_length=512)]




def _google_one(args):
    """Traduit un seul texte via GoogleTranslator."""
    t, src, dest = args
    try:
        translated = GoogleTranslator(source=src, target=dest).translate(t)
        return translated if translated else t
    except Exception as e:
        print(f"⚠️ Traduction échouée : {e}")
        return t


def _google(batch, src, dest, delay=0.35):
    """
    Traduit séquentiellement avec un délai entre chaque requête
    pour respecter la limite Google de 5 req/s.
    """
    import time
    print(f"ℹ️ GoogleTranslator séquentiel (délai {delay}s entre requêtes)")
    results = []
    for i, t in enumerate(batch):
        if i > 0:
            time.sleep(delay)  # Respecte la limite 5 req/s
        results.append(_google_one((t, src, dest)))
    return results

def _is_model_cached(src, dest):
    """Vérifie si le modèle Helsinki-NLP est déjà téléchargé (cache HuggingFace)."""
    from pathlib import Path
    # Le nom du dossier est : models--Helsinki-NLP--opus-mt-{src}-{dest}
    model_name = f"models--Helsinki-NLP--opus-mt-{src}-{dest}"
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    return (cache_dir / model_name).exists()


def _do(batch, src, dest):
    """
    Traduit un batch — Helsinki-NLP en priorité, GoogleTranslator en fallback.

    Helsinki-NLP :
    - Évite les limites Google
    - Qualité supérieure
    - Télécharge 300 Mo la 1ère fois (mais instantané ensuite)
    """
    if (src, dest) in LOCAL_PAIRS:
        try:
            return _local(batch, src, dest)
        except Exception as e:
            print(f"⚠️ Helsinki {src}->{dest} échec : {e}")
    else:
        print(f"ℹ️ Paire {src}->{dest} non supportée par Helsinki → GoogleTranslator")
    return _google(batch, src, dest)


def _batch_translate(texts, src, dest):
    """Traduit un batch en respectant MAX_CHARS."""
    results, batch, size = [], [], 0
    for t in texts:
        if size + len(t) > MAX_CHARS and batch:
            results += _do(batch, src, dest)
            batch, size = [], 0
        batch.append(t)
        size += len(t)
    if batch:
        results += _do(batch, src, dest)
    return [_clean_spacing(r) for r in results]


def translate_texts(texts, src, dest):
    """
    Traduit une liste de textes avec cache et parallélisation.

    Étapes :
    1. Récupérer ce qui est déjà en cache
    2. Traduire uniquement les textes manquants (en parallèle)
    3. Sauvegarder les nouvelles traductions en cache
    """
    if src == dest or not texts:
        return texts

    # 1. Récupérer le cache
    results, missing_idx, missing_texts = get_translation_batch(texts, src, dest)

    # 2. Traduire les manquants
    if missing_texts:
        n_missing = len(missing_texts)
        n_total = len(texts)
        print(f"🌍 Traduction de {n_missing}/{n_total} textes ({src} → {dest}) — parallélisation activée...")
        import time
        start = time.time()
        translated = _batch_translate(missing_texts, src, dest)
        elapsed = time.time() - start
        print(f"✅ {n_missing} textes traduits en {elapsed:.1f}s")
        set_translation_batch(missing_texts, translated, src, dest)
        for idx, t in zip(missing_idx, translated):
            results[idx] = t
    else:
        print(f"✅ Traduction en cache : {len(texts)} textes récupérés instantanément")

    # ✅ Cast final : tous les None ont été remplacés
    return [r if r is not None else texts[i] for i, r in enumerate(results)]

def translate_notes(notes, source_lang="en"):
    return translate_texts(notes, source_lang, "fr")