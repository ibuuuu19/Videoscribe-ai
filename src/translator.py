import re
from deep_translator import GoogleTranslator

MAX_CHARS = 4000

_pipes = {}
LOCAL_PAIRS = {("en", "fr"), ("fr", "en")}

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

def _google(batch, src, dest):
    """Traduction via deep-translator (remplace googletrans)."""
    results = []
    for t in batch:
        try:
            # deep-translator gère les longs textes automatiquement
            translated = GoogleTranslator(source=src, target=dest).translate(t)
            results.append(translated if translated else t)
        except Exception as e:
            print(f"⚠️ Traduction échouée pour un chunk : {e}")
            results.append(t)  # Fallback : garde l'original
    return results

def _do(batch, src, dest):
    # D'abord essayer Helsinki (local, plus rapide pour EN<->FR)
    if (src, dest) in LOCAL_PAIRS:
        try:
            return _local(batch, src, dest)
        except Exception as e:
            print(f"⚠️ Helsinki {src}->{dest} échec : {e}")
    # Sinon Google Translate
    return _google(batch, src, dest)

def _batch_translate(texts, src, dest):
    results, batch, size = [], [], 0
    for t in texts:
        if size + len(t) > MAX_CHARS and batch:
            results += _do(batch, src, dest)
            batch, size = [], 0
        batch.append(t); size += len(t)
    if batch: results += _do(batch, src, dest)
    return [_clean_spacing(r) for r in results]

def translate_texts(texts, src, dest):
    if src == dest or not texts:
        return texts
    return _batch_translate(texts, src, dest)

def translate_notes(notes, source_lang="en"):
    return translate_texts(notes, source_lang, "fr")