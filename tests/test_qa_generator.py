"""
Tests unitaires pour src/qa_generator.py

On teste la fonction generate_questions() qui :
- Génère des questions à partir des mots-clés
- Complète avec des questions génériques
- Respecte le paramètre n (nombre max de questions)
"""

import pytest
from src.qa_generator import generate_questions


# ═══════════════════════════════════════════════════════════════
# TESTS pour generate_questions()
# ═══════════════════════════════════════════════════════════════

class TestGenerateQuestions:
    """Tests pour la fonction generate_questions()."""

    # ───────────────────────────────────────────────────
    # CAS NORMAUX
    # ───────────────────────────────────────────────────

    def test_returns_list(self):
        """La fonction renvoie toujours une liste."""
        result = generate_questions([])
        assert isinstance(result, list)

    def test_default_returns_five_questions(self):
        """Avec n=5 par défaut, on obtient 5 questions."""
        result = generate_questions([])
        assert len(result) == 5

    def test_respects_n_parameter(self):
        """Avec n=3, on obtient seulement 3 questions."""
        result = generate_questions([], n=3)
        assert len(result) == 3

    def test_n_larger_than_available(self):
        """Si on demande plus que disponible, on renvoie ce qu'on a."""
        result = generate_questions([], n=100)
        # Il y a 5 questions générales disponibles
        assert len(result) == 5

    def test_questions_are_strings(self):
        """Toutes les questions renvoyées sont des chaînes."""
        result = generate_questions([], n=5)
        for q in result:
            assert isinstance(q, str)
            assert len(q) > 0

    # ───────────────────────────────────────────────────
    # AVEC MOTS-CLÉS
    # ───────────────────────────────────────────────────

    def test_with_keywords_generates_keyword_questions(self):
        """Avec des mots-clés, on génère des questions à leur sujet."""
        keywords = [
            ("intelligence artificielle", 0.9),
            ("apprentissage automatique", 0.8),
            ("réseau de neurones", 0.7),
        ]
        result = generate_questions([], keywords=keywords, n=5)

        # Les 3 premières questions doivent mentionner les mots-clés
        assert "intelligence artificielle" in result[0]
        assert "apprentissage automatique" in result[1]
        assert "réseau de neurones" in result[2]

    def test_with_keywords_uses_only_first_three(self):
        """On n'utilise que les 3 premiers mots-clés."""
        keywords = [
            ("mot1", 0.9),
            ("mot2", 0.8),
            ("mot3", 0.7),
            ("mot4", 0.6),      # ignoré
            ("mot5", 0.5),      # ignoré
        ]
        result = generate_questions([], keywords=keywords, n=5)

        # Aucune question ne doit mentionner mot4 ou mot5
        all_text = " ".join(result)
        assert "mot4" not in all_text
        assert "mot5" not in all_text

    def test_with_keywords_and_small_n(self):
        """Avec n=2 et 3 mots-clés, on obtient 2 questions (les 2 premiers mots-clés)."""
        keywords = [
            ("mot1", 0.9),
            ("mot2", 0.8),
            ("mot3", 0.7),
        ]
        result = generate_questions([], keywords=keywords, n=2)

        assert len(result) == 2
        assert "mot1" in result[0]
        assert "mot2" in result[1]

    def test_completes_with_general_when_keywords_insufficient(self):
        """Si peu de mots-clés, on complète avec des questions générales."""
        keywords = [("unique_mot", 0.9)]
        result = generate_questions([], keywords=keywords, n=5)

        assert len(result) == 5
        # La première mentionne le mot-clé
        assert "unique_mot" in result[0]
        # Les autres sont des questions générales
        for q in result[1:]:
            assert "unique_mot" not in q

    # ───────────────────────────────────────────────────
    # CAS LIMITES
    # ───────────────────────────────────────────────────

    def test_empty_keywords_list(self):
        """Liste de mots-clés vide → seulement questions générales."""
        result = generate_questions([], keywords=[], n=5)
        assert len(result) == 5

    def test_none_keywords(self):
        """keywords=None → seulement questions générales."""
        result = generate_questions([], keywords=None, n=5)
        assert len(result) == 5

    def test_n_zero(self):
        """Avec n=0, on ne renvoie aucune question."""
        result = generate_questions([], n=0)
        assert result == []

    def test_n_negative(self):
        """Avec n négatif, on ne renvoie aucune question."""
        result = generate_questions([], n=-3)
        assert result == []

    def test_notes_parameter_is_ignored(self):
        """Le paramètre 'notes' n'est pas utilisé dans la fonction actuelle."""
        result_with_notes = generate_questions(["une note"], n=5)
        result_without_notes = generate_questions([], n=5)
        assert result_with_notes == result_without_notes

    # ───────────────────────────────────────────────────
    # FORMAT DES QUESTIONS
    # ───────────────────────────────────────────────────

    def test_keyword_questions_use_guillemets(self):
        """Les questions sur les mots-clés utilisent des guillemets français «  »."""
        keywords = [("python", 0.9)]
        result = generate_questions([], keywords=keywords, n=1)

        # On doit trouver le mot-clé entre guillemets
        assert "«" in result[0]
        assert "»" in result[0]
        assert "python" in result[0]

    def test_general_questions_end_with_question_mark(self):
        """Toutes les questions générales finissent par '?'."""
        result = generate_questions([], n=5)
        for q in result:
            assert q.endswith("?")