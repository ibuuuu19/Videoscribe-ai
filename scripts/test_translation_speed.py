"""Test de vitesse de traduction (avec cache et parallélisation)."""

import sys
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from src.translator import translate_texts
from src.core.cache import clear_translation_cache, get_cache_stats


# Textes de test (simuler 8 chunks)
texts = [
    "Artificial intelligence is transforming the world.",
    "Machine learning models are becoming more powerful.",
    "Deep learning has revolutionized computer vision.",
    "Natural language processing enables chatbots.",
    "Reinforcement learning is used in robotics.",
    "Neural networks are inspired by the human brain.",
    "Data science combines statistics and programming.",
    "Cloud computing provides scalable infrastructure.",
]

print("=" * 60)
print("Test 1 : Sans cache (parallélisation active)")
print("=" * 60)
clear_translation_cache()
start = time.time()
result = translate_texts(texts, "en", "fr")
elapsed = time.time() - start
print(f"⏱️  Durée : {elapsed:.2f}s")

print("\n" + "=" * 60)
print("Test 2 : Avec cache (doit être instantané)")
print("=" * 60)
start = time.time()
result2 = translate_texts(texts, "en", "fr")
elapsed2 = time.time() - start
print(f"⏱️  Durée : {elapsed2:.2f}s")

print("\n" + "=" * 60)
if elapsed2 > 0.01:
    print(f"📊 Gain : {elapsed:.2f}s → {elapsed2:.2f}s  ({elapsed/elapsed2:.1f}× plus rapide)")
else:
    print(f"📊 Gain : {elapsed:.2f}s → {elapsed2:.3f}s  (instantané !)")
print(f"📦 Cache : {get_cache_stats()}")
print("=" * 60)