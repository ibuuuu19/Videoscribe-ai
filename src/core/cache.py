"""
Module de cache pour les traductions et autres données coûteuses.

Gestion d'un cache persistant en JSON, avec hash SHA-256 des clés.
Extrait de app.py pour permettre la réutilisation entre modules.
"""

import json
import hashlib
from pathlib import Path


CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _hash_key(text, src, dest):
    """Génère un hash unique pour une clé de traduction."""
    raw = f"{src}|{dest}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _load_cache(name):
    """Charge un cache JSON."""
    path = CACHE_DIR / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(name, data):
    """Sauvegarde un cache JSON."""
    path = CACHE_DIR / f"{name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
# CACHE DE TRADUCTION
# ═══════════════════════════════════════════════════════════════

def get_translation_cache(text, src, dest):
    """Récupère une traduction du cache (ou None si absente)."""
    cache = _load_cache("translations")
    key = _hash_key(text, src, dest)
    return cache.get(key)


def set_translation_cache(text, src, dest, translation):
    """Sauvegarde une traduction dans le cache."""
    cache = _load_cache("translations")
    key = _hash_key(text, src, dest)
    cache[key] = translation
    _save_cache("translations", cache)


def get_translation_batch(texts, src, dest):
    """..."""
    cache = _load_cache("translations")
    # ✅ Typer explicitement : list[str | None]
    results: list[str | None] = [None] * len(texts)
    missing_indices = []
    missing_texts = []
    for i, text in enumerate(texts):
        key = _hash_key(text, src, dest)
        cached = cache.get(key)
        if cached is not None:
            results[i] = cached
        else:
            missing_indices.append(i)
            missing_texts.append(text)
    return results, missing_indices, missing_texts

def set_translation_batch(texts, translations, src, dest):
    """Sauvegarde plusieurs traductions dans le cache (une seule écriture)."""
    cache = _load_cache("translations")
    for text, translation in zip(texts, translations):
        key = _hash_key(text, src, dest)
        cache[key] = translation
    _save_cache("translations", cache)


def get_cache_stats():
    """Retourne des stats sur le cache de traductions."""
    cache = _load_cache("translations")
    path = CACHE_DIR / "translations.json"
    size_kb = path.stat().st_size / 1024 if path.exists() else 0
    return {"entries": len(cache), "size_kb": round(size_kb, 2)}


def clear_translation_cache():
    """Vide le cache de traductions."""
    path = CACHE_DIR / "translations.json"
    if path.exists():
        path.unlink()