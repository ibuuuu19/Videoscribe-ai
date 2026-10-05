"""
Tests unitaires pour src/keywords_extractor.py

⚠️ Ces tests MOCKENT KeyBERT (le modèle IA) pour :
- Éviter de télécharger 400 Mo de modèle
- Avoir des tests rapides (< 1s au lieu de 30s)
- Avoir des résultats prévisibles

On ne teste PAS la qualité de KeyBERT (c'est HuggingFace), mais :
- Le filtrage post-extraction (longueur, chiffres, doublons)
- Le comportement sur texte vide
- La gestion des erreurs
"""

import pytest
from src import keywords_extractor


# ═══════════════════════════════════════════════════════════════
# FIXTURE : Faux KeyBERT qui renvoie toujours les mêmes résultats
# ═══════════════════════════════════════════════════════════════

class FakeKeyBERT:
    """Faux KeyBERT pour les tests — pas d'appel au vrai modèle."""

    def __init__(self, return_value=None, should_raise=False, model=None):
        self.return_value = return_value or []
        self.should_raise = should_raise

    def extract_keywords(self, text, **kwargs):
        if self.should_raise:
            raise RuntimeError("Fake KeyBERT error")
        return self.return_value


@pytest.fixture(autouse=True)
def reset_kb_cache():
    """Vide le cache global _kb avant chaque test pour l'isoler."""
    keywords_extractor._kb = None
    yield
    keywords_extractor._kb = None


# ═══════════════════════════════════════════════════════════════
# TESTS pour extract_keywords()
# ═══════════════════════════════════════════════════════════════

class TestExtractKeywords:
    """Tests pour la fonction extract_keywords()."""

    def test_empty_text_returns_empty_list(self):
        """Texte vide → liste vide."""
        result = keywords_extractor.extract_keywords("")
        assert result == []

    def test_short_text_returns_empty_list(self):
        """Texte trop court (< 30 chars) → liste vide."""
        result = keywords_extractor.extract_keywords("court")
        assert result == []

    def test_none_text_returns_empty_list(self):
        """None en entrée → liste vide, pas de crash."""
        result = keywords_extractor.extract_keywords(None)
        assert result == []

    def test_returns_keywords_with_scores(self, monkeypatch):
        """Avec un faux KeyBERT, on obtient bien les mots-clés filtrés."""
        fake = FakeKeyBERT(return_value=[
            ("intelligence artificielle", 0.75),
            ("apprentissage automatique", 0.65),
            ("python", 0.60),
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "L'intelligence artificielle et l'apprentissage automatique avec Python sont fascinants."
        result = keywords_extractor.extract_keywords(text, top_n=10)

        assert len(result) == 3
        assert result[0] == ("intelligence artificielle", 0.75)
        assert result[1] == ("apprentissage automatique", 0.65)
        assert result[2] == ("python", 0.60)

    def test_filters_short_keywords(self, monkeypatch):
        """Les mots-clés < 3 caractères sont filtrés."""
        fake = FakeKeyBERT(return_value=[
            ("ok", 0.9),                # trop court → filtré
            ("ab", 0.85),               # trop court → filtré
            ("python", 0.8),            # gardé
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        result = keywords_extractor.extract_keywords(text, top_n=10)

        assert len(result) == 1
        assert result[0][0] == "python"

    def test_filters_long_keywords(self, monkeypatch):
        """Les mots-clés > 40 caractères sont filtrés."""
        fake = FakeKeyBERT(return_value=[
            ("a" * 50, 0.9),            # trop long → filtré
            ("python", 0.8),            # gardé
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        result = keywords_extractor.extract_keywords(text, top_n=10)

        assert len(result) == 1
        assert result[0][0] == "python"

    def test_filters_pure_numbers(self, monkeypatch):
        """Les nombres purs sont filtrés."""
        fake = FakeKeyBERT(return_value=[
            ("12345", 0.9),             # nombre pur → filtré
            ("python", 0.8),            # gardé
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        result = keywords_extractor.extract_keywords(text, top_n=10)

        assert len(result) == 1
        assert result[0][0] == "python"

    def test_filters_substring_duplicates(self, monkeypatch):
        """Un mot-clé qui est un substring d'un autre est filtré."""
        fake = FakeKeyBERT(return_value=[
            ("intelligence artificielle", 0.9),   # gardé
            ("intelligence", 0.85),                # substring du précédent → filtré
            ("python", 0.7),                       # gardé
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        result = keywords_extractor.extract_keywords(text, top_n=10)

        keywords_only = [kw for kw, _ in result]
        assert "intelligence artificielle" in keywords_only
        assert "python" in keywords_only
        # "intelligence" seul ne doit PAS être présent
        assert "intelligence" not in keywords_only

    def test_respects_top_n(self, monkeypatch):
        """Ne renvoie jamais plus que top_n mots-clés."""
        fake = FakeKeyBERT(return_value=[
            (f"keyword{i}", 0.9 - i * 0.01) for i in range(50)
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        result = keywords_extractor.extract_keywords(text, top_n=5)

        assert len(result) <= 5

    def test_handles_keybert_exception(self, monkeypatch):
        """Si KeyBERT plante, on ne doit pas crasher."""
        fake = FakeKeyBERT(should_raise=True)
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        # Le code a un fallback : on ne doit pas crash
        result = keywords_extractor.extract_keywords(text, top_n=5)
        assert isinstance(result, list)

    def test_scores_are_rounded(self, monkeypatch):
        """Les scores sont arrondis à 3 décimales."""
        fake = FakeKeyBERT(return_value=[
            ("python", 0.123456789),
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Un texte suffisamment long pour dépasser les trente caractères."
        result = keywords_extractor.extract_keywords(text, top_n=10)

        assert result[0][1] == 0.123  # arrondi à 3 décimales

    def test_with_english_lang(self, monkeypatch):
        """Avec lang='en', le stopwords change (mais on ne teste pas KeyBERT)."""
        fake = FakeKeyBERT(return_value=[
            ("machine learning", 0.8),
        ])
        monkeypatch.setattr(keywords_extractor, "_get_kb", lambda: fake)

        text = "Machine learning is a fascinating field of computer science."
        result = keywords_extractor.extract_keywords(text, top_n=10, lang="en")

        assert len(result) == 1