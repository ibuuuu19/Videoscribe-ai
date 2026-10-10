"""
Configuration globale de pytest pour VideoScribe AI.

Ce fichier est automatiquement chargé par pytest AVANT tous les tests.
Il mock les modules externes lourds (torch, transformers, keybert...)
pour que les tests unitaires puissent s'exécuter SANS les installer.

Avantages :
- CI ultra-rapide (~15s au lieu de ~3min)
- Tests exécutables sur n'importe quelle machine vierge
- Pas de téléchargement de modèles IA (400 Mo+)
"""

import sys
from unittest.mock import MagicMock


# ═══════════════════════════════════════════════════════════════
# MOCK DES MODULES EXTERNES LOURDS
# ═══════════════════════════════════════════════════════════════
# On remplace ces modules par des mocks AVANT que le code source
# ne tente de les importer. Ainsi :
#   from keybert import KeyBERT
# trouve le mock au lieu du vrai module (non installé).

_MODULES_TO_MOCK = [
    # IA / NLP (très lourds : 2-3 Go au total)
    "keybert",
    "transformers",
    "torch",
    "accelerate",
    "sentencepiece",

    # Extraction vidéo YouTube
    "youtube_transcript_api",

    # Traduction
    "deep_translator",

    # Cache
    "diskcache",

    # Divers
    "streamlit_cookies_controller",
    "fpdf",
    "yt_dlp",
]

for _module_name in _MODULES_TO_MOCK:
    if _module_name not in sys.modules:
        sys.modules[_module_name] = MagicMock()


# ═══════════════════════════════════════════════════════════════
# FIXTURES PARTAGÉES
# ═══════════════════════════════════════════════════════════════
# Ces fixtures peuvent être utilisées dans n'importe quel fichier
# de test, simplement en les passant en argument.

import pytest


@pytest.fixture
def sample_text():
    """Un texte long d'exemple pour les tests."""
    return "Ceci est un texte de test. Il contient plusieurs phrases. " * 5


@pytest.fixture
def sample_notes():
    """Une liste de notes d'exemple, comme en sortie du summarizer."""
    return [
        "Première note importante à retenir.",
        "Deuxième note qui complète la première.",
        "Troisième note avec une action à faire.",
    ]


@pytest.fixture
def sample_youtube_urls():
    """Différentes formes d'URL YouTube valides."""
    return [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
    ]


@pytest.fixture
def sample_keywords():
    """Une liste de mots-clés avec scores, comme en sortie de KeyBERT."""
    return [
        ("intelligence artificielle", 0.85),
        ("apprentissage automatique", 0.72),
        ("réseau de neurones", 0.68),
    ]