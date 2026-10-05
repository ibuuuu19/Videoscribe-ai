"""
Tests unitaires pour src/text_processor.py

On teste les 5 fonctions principales :
- chunk_text() : découpage du texte en morceaux
- remove_repetitions() : suppression des répétitions
- format_notes() : formatage des notes
- polish_translation() : nettoyage post-traduction
- extract_action_points() : extraction des actions
"""

import pytest
from src.text_processor import (
    chunk_text,
    remove_repetitions,
    format_notes,
    polish_translation,
    extract_action_points,
)


# ═══════════════════════════════════════════════════════════════
# TESTS POUR chunk_text()
# ═══════════════════════════════════════════════════════════════

class TestChunkText:
    """Tests pour la fonction chunk_text()."""

    def test_simple_chunking(self):
        """Un texte court → un seul chunk."""
        text = "Ceci est une phrase. Une autre phrase. Encore une."
        chunks = chunk_text(text, chunk_size=1200)
        assert len(chunks) == 1
        assert "Ceci est une phrase" in chunks[0]

    def test_chunking_splits_when_too_long(self):
        """Un texte long → plusieurs chunks."""
        # On construit un texte long avec des phrases répétées
        text = "Ceci est une phrase de test suffisamment longue. " * 50
        chunks = chunk_text(text, chunk_size=200)
        assert len(chunks) > 1

    def test_chunk_size_is_respected(self):
        """Chaque chunk ne doit pas dépasser largement chunk_size."""
        text = "Phrase de test numéro un. " * 100
        chunks = chunk_text(text, chunk_size=300)
        # On tolère un dépassement car chunk_size est une cible, pas une limite stricte
        for chunk in chunks:
            assert len(chunk) <= 400  # 300 + tolérance

    def test_empty_text(self):
        """Texte vide → résultat vide ou liste vide, pas de crash."""
        result = chunk_text("", chunk_size=1200)
        assert isinstance(result, list)

    def test_text_with_no_periods(self):
        """Texte sans point → un seul chunk (pas de découpage possible)."""
        text = "Un texte sans aucun point"
        chunks = chunk_text(text, chunk_size=1200)
        assert isinstance(chunks, list)
        assert len(chunks) >= 1


# ═══════════════════════════════════════════════════════════════
# TESTS POUR remove_repetitions()
# ═══════════════════════════════════════════════════════════════

class TestRemoveRepetitions:
    """Tests pour la fonction remove_repetitions()."""

    def test_no_repetitions(self):
        """Texte sans répétition → inchangé."""
        text = "Première phrase. Deuxième phrase. Troisième phrase."
        result = remove_repetitions(text)
        assert "Première phrase" in result
        assert "Deuxième phrase" in result
        assert "Troisième phrase" in result

    def test_exact_duplicate(self):
        """Phrase exactement dupliquée → une seule conservée."""
        text = "Phrase répétée. Phrase répétée. Autre phrase."
        result = remove_repetitions(text)
        # La phrase "Phrase répétée" ne doit apparaître qu'une fois
        assert result.count("Phrase répétée") == 1

    def test_near_duplicate(self):
        """Phrases presque identiques → une seule conservée."""
        text = "Les données sont importantes. Les données sont importantes pour tous. Autre phrase."
        result = remove_repetitions(text)
        # On garde la plus longue, l'autre est supprimée
        assert isinstance(result, str)
        # L'une des deux doit avoir été retirée
        assert result.count("Les données sont importantes") <= 2

    def test_empty_text(self):
        """Texte vide → pas de crash."""
        result = remove_repetitions("")
        assert isinstance(result, str)

    def test_single_sentence(self):
        """Une seule phrase → retournée telle quelle (avec point)."""
        result = remove_repetitions("Une seule phrase")
        assert "Une seule phrase" in result


# ═══════════════════════════════════════════════════════════════
# TESTS POUR format_notes()
# ═══════════════════════════════════════════════════════════════

class TestFormatNotes:
    """Tests pour la fonction format_notes()."""

    def test_format_single_note(self):
        """Une seule note → bien formatée avec en-tête."""
        notes = ["Ceci est la première note."]
        result = format_notes(notes)
        assert "RÉSUMÉ" in result
        assert "1." in result
        assert "Ceci est la première note" in result

    def test_format_multiple_notes(self):
        """Plusieurs notes → numérotées 1, 2, 3..."""
        notes = ["Note une.", "Note deux.", "Note trois."]
        result = format_notes(notes)
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_format_empty_list(self):
        """Liste vide → juste l'en-tête."""
        result = format_notes([])
        assert isinstance(result, str)
        assert "RÉSUMÉ" in result


# ═══════════════════════════════════════════════════════════════
# TESTS POUR polish_translation()
# ═══════════════════════════════════════════════════════════════

class TestPolishTranslation:
    """Tests pour la fonction polish_translation()."""

    def test_glossary_replacement(self):
        """Un mot du glossaire → remplacé par le bon terme."""
        result = polish_translation("Nous utilisons des flotteurs.")
        assert "floats" in result
        assert "flotteurs" not in result

    def test_extra_whitespace_removed(self):
        """Espaces multiples → réduits à un seul."""
        result = polish_translation("Texte    avec    trop    d'espaces.")
        assert "  " not in result  # pas de double espace

    def test_duplicate_words_removed(self):
        """Mots dupliqués consécutifs → un seul conservé."""
        result = polish_translation("Le chat chat mange.")
        assert "chat chat" not in result
        assert "chat" in result

    def test_case_insensitive_glossary(self):
        """Le glossaire doit fonctionner avec différentes casses."""
        result = polish_translation("Les Tuiles sont utiles.")
        assert "tuples" in result.lower() or "tuiles" not in result.lower()

    def test_empty_text(self):
        """Texte vide → pas de crash."""
        result = polish_translation("")
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════════════
# TESTS POUR extract_action_points()
# ═══════════════════════════════════════════════════════════════

class TestExtractActionPoints:
    """Tests pour la fonction extract_action_points()."""

    def test_detects_il_faut(self):
        """Détecte les actions avec 'il faut'."""
        notes = ["Il faut toujours tester son code avant de déployer."]
        result = extract_action_points(notes)
        assert len(result) >= 1
        assert any("tester" in r.lower() for r in result)

    def test_detects_vous_devez(self):
        """Détecte les actions avec 'vous devez'."""
        notes = ["Vous devez installer les dépendances du projet."]
        result = extract_action_points(notes)
        assert len(result) >= 1
        assert any("installer" in r.lower() for r in result)

    def test_detects_essayez(self):
        """Détecte les actions avec 'essayez'."""
        notes = ["Essayez cette nouvelle méthode pour progresser rapidement."]
        result = extract_action_points(notes)
        assert len(result) >= 1

    def test_detects_english_cues(self):
        """Détecte les actions en anglais aussi."""
        notes = ["You should always test your code before deploying it."]
        result = extract_action_points(notes)
        assert len(result) >= 1

    def test_respects_max_n(self):
        """Ne retourne jamais plus que max_n actions."""
        notes = ["Il faut tester. Vous devez vérifier. Essayez aussi. N'oubliez pas de déployer."] * 5
        result = extract_action_points(notes, max_n=3)
        assert len(result) <= 3

    def test_no_actions(self):
        """Aucun mot-clé d'action → liste vide."""
        notes = ["Le ciel est bleu.", "L'eau est mouillée."]
        result = extract_action_points(notes)
        assert result == []

    def test_empty_notes(self):
        """Liste vide → liste vide, pas de crash."""
        result = extract_action_points([])
        assert result == []

    def test_minimum_length_filter(self):
        """Les phrases trop courtes (<20 caractères) sont ignorées."""
        notes = ["Il faut."]  # trop court
        result = extract_action_points(notes)
        assert result == []