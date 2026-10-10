"""
Tests unitaires pour src/transcript_extractor.py

On teste principalement la fonction extract_video_id() qui doit :
- Accepter toutes les formes d'URL YouTube valides
- Renvoyer None pour les URL invalides
- Ne jamais crasher, même avec des entrées bizarres
"""

import pytest
from src.transcript_extractor import extract_video_id


class TestExtractVideoId:
    """Tests pour la fonction extract_video_id()."""

    # ═══════════════════════════════════════════
    # CAS NORMAUX — Les URL YouTube valides
    # ═══════════════════════════════════════════

    def test_youtube_watch_url(self):
        """URL YouTube classique."""
        assert extract_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ) == "dQw4w9WgXcQ"

    def test_youtube_short_url(self):
        """URL YouTube raccourcie (youtu.be)."""
        assert extract_video_id(
            "https://youtu.be/dQw4w9WgXcQ"
        ) == "dQw4w9WgXcQ"

    def test_youtube_with_extra_params(self):
        """URL avec paramètres supplémentaires (timestamp, playlist)."""
        assert extract_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=PLxyz"
        ) == "dQw4w9WgXcQ"

    def test_youtube_mobile_url(self):
        """URL YouTube depuis mobile (m.youtube.com)."""
        assert extract_video_id(
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ) == "dQw4w9WgXcQ"

    def test_youtube_embed_url(self):
        """URL d'embed YouTube."""
        assert extract_video_id(
            "https://www.youtube.com/embed/dQw4w9WgXcQ"
        ) == "dQw4w9WgXcQ"

    def test_youtube_without_www(self):
        """URL sans www."""
        assert extract_video_id(
            "https://youtube.com/watch?v=dQw4w9WgXcQ"
        ) == "dQw4w9WgXcQ"

    def test_youtube_with_http(self):
        """URL en HTTP (pas HTTPS)."""
        assert extract_video_id(
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ) == "dQw4w9WgXcQ"

    # ═══════════════════════════════════════════
    # CAS D'ERREUR — Les entrées invalides
    # ═══════════════════════════════════════════

    def test_non_youtube_url(self):
        """URL d'un autre site → doit renvoyer None."""
        assert extract_video_id("https://www.google.com") is None

    def test_empty_string(self):
        """Chaîne vide → doit renvoyer None."""
        assert extract_video_id("") is None

    def test_none_input(self):
        """None en entrée → ne doit pas crasher."""
        assert extract_video_id(None) is None

    def test_random_text(self):
        """Texte aléatoire → doit renvoyer None."""
        assert extract_video_id("ceci n'est pas une url") is None

    def test_youtube_homepage(self):
        """Page d'accueil YouTube (sans vidéo) → doit renvoyer None."""
        assert extract_video_id("https://www.youtube.com") is None

    def test_malformed_url(self):
        """URL mal formée → ne doit pas crasher."""
        assert extract_video_id("https://www.youtube.com/watch?v=") is None

    def test_invalid_video_id_length(self):
        """ID vidéo trop court → ne doit pas crasher."""
        result = extract_video_id("https://www.youtube.com/watch?v=abc")
        # Soit None, soit une chaîne courte — l'important : pas de crash
        assert result is None or isinstance(result, str)