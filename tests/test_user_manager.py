"""
Tests unitaires pour src/user_manager.py

⚠️ IMPORTANT : Ces tests écrivent et lisent des fichiers.
Pour ne PAS polluer le vrai fichier `data/users.json`, on utilise
la fixture `tmp_path` de pytest qui fournit un dossier temporaire
unique par test, supprimé automatiquement après.

Chaque test :
1. Redirige `USERS_FILE` vers un fichier temporaire
2. Effectue ses opérations
3. Est automatiquement nettoyé par pytest
"""

import json
import pytest
from datetime import datetime, timedelta

from src import user_manager


# ═══════════════════════════════════════════════════════════════
# FIXTURE : Rediriger USERS_FILE vers un fichier temporaire
# ═══════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def isolate_users_file(tmp_path, monkeypatch):
    """
    Redirige src.user_manager.USERS_FILE vers un fichier temporaire
    unique pour chaque test. Le fichier est supprimé après le test.
    """
    temp_file = tmp_path / "test_users.json"
    monkeypatch.setattr(user_manager, "USERS_FILE", temp_file)
    # On vide aussi le cache potentiel
    yield temp_file
    # Rien à nettoyer : pytest supprime tmp_path automatiquement


# ═══════════════════════════════════════════════════════════════
# TESTS pour register_user()
# ═══════════════════════════════════════════════════════════════

class TestRegisterUser:
    """Tests pour la fonction register_user()."""

    def test_register_valid_user(self):
        """Créer un utilisateur valide → succès."""
        ok, msg = user_manager.register_user("alice", "password123", "alice@test.com")
        assert ok is True
        assert "succès" in msg.lower() or "créé" in msg.lower()

    def test_register_saves_to_file(self, isolate_users_file):
        """L'utilisateur est bien écrit dans le fichier JSON."""
        user_manager.register_user("bob", "secret123", "bob@test.com")

        assert isolate_users_file.exists()
        with open(isolate_users_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "bob" in data
        assert data["bob"]["email"] == "bob@test.com"
        assert data["bob"]["role"] == "client"
        assert data["bob"]["active"] is True

    def test_password_is_hashed(self, isolate_users_file):
        """Le mot de passe NE doit PAS être stocké en clair."""
        user_manager.register_user("charlie", "topsecret", "charlie@test.com")

        with open(isolate_users_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        user_data = data["charlie"]
        assert "password" not in user_data            # Pas de mot de passe en clair
        assert "password_hash" in user_data           # Hash présent
        assert "salt" in user_data                    # Salt présent
        assert user_data["password_hash"] != "topsecret"

    def test_username_is_lowercased(self, isolate_users_file):
        """Le username est converti en minuscules."""
        user_manager.register_user("ALICE", "password123")

        with open(isolate_users_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "alice" in data
        assert "ALICE" not in data

    def test_username_is_stripped(self, isolate_users_file):
        """Les espaces autour du username sont supprimés."""
        user_manager.register_user("  bob  ", "password123")

        with open(isolate_users_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "bob" in data

    def test_reject_short_username(self):
        """Username < 3 caractères → échec."""
        ok, msg = user_manager.register_user("ab", "password123")
        assert ok is False
        assert "invalide" in msg.lower() or "3" in msg

    def test_reject_empty_username(self):
        """Username vide → échec."""
        ok, msg = user_manager.register_user("", "password123")
        assert ok is False

    def test_reject_short_password(self):
        """Mot de passe < 6 caractères → échec."""
        ok, msg = user_manager.register_user("bob", "12345")
        assert ok is False
        assert "6" in msg or "minimum" in msg.lower()

    def test_reject_duplicate_username(self):
        """Username déjà pris → échec."""
        user_manager.register_user("bob", "password123")
        ok, msg = user_manager.register_user("bob", "otherpass")

        assert ok is False
        assert "existe" in msg.lower() or "déjà" in msg.lower()


# ═══════════════════════════════════════════════════════════════
# TESTS pour authenticate()
# ═══════════════════════════════════════════════════════════════

class TestAuthenticate:
    """Tests pour la fonction authenticate()."""

    def test_authenticate_valid_credentials(self):
        """Username + password corrects → succès."""
        user_manager.register_user("alice", "password123", role="client")
        ok, role = user_manager.authenticate("alice", "password123")

        assert ok is True
        assert role == "client"

    def test_authenticate_wrong_password(self):
        """Mauvais mot de passe → échec."""
        user_manager.register_user("alice", "password123")
        ok, role = user_manager.authenticate("alice", "wrongpassword")

        assert ok is False
        assert role is None

    def test_authenticate_nonexistent_user(self):
        """Utilisateur inexistant → échec."""
        ok, role = user_manager.authenticate("nobody", "password123")
        assert ok is False
        assert role is None

    def test_authenticate_case_insensitive_username(self):
        """Username insensible à la casse."""
        user_manager.register_user("alice", "password123")
        ok, role = user_manager.authenticate("ALICE", "password123")
        assert ok is True

    def test_authenticate_suspended_account(self):
        """Compte suspendu → échec avec statut 'suspended'."""
        user_manager.register_user("alice", "password123")
        user_manager.set_active("alice", False)

        ok, status = user_manager.authenticate("alice", "password123")
        assert ok is False
        assert status == "suspended"


# ═══════════════════════════════════════════════════════════════
# TESTS pour delete_user()
# ═══════════════════════════════════════════════════════════════

class TestDeleteUser:
    """Tests pour la fonction delete_user()."""

    def test_delete_existing_user(self):
        """Suppression d'un utilisateur existant → succès."""
        user_manager.register_user("alice", "password123")
        ok = user_manager.delete_user("alice")

        assert ok is True
        assert "alice" not in user_manager.list_users()

    def test_delete_nonexistent_user(self):
        """Supprimer un utilisateur inexistant → échec."""
        ok = user_manager.delete_user("nobody")
        assert ok is False

    def test_cannot_delete_admin(self, isolate_users_file):
        """On ne peut PAS supprimer un admin."""
        # Créer un admin manuellement
        users = {
            "admin": {
                "email": "admin@test.com",
                "salt": "somesalt",
                "password_hash": "somehash",
                "role": "admin",
                "active": True,
            }
        }
        with open(isolate_users_file, "w") as f:
            json.dump(users, f)

        ok = user_manager.delete_user("admin")
        assert ok is False
        assert "admin" in user_manager.list_users()


# ═══════════════════════════════════════════════════════════════
# TESTS pour set_active()
# ═══════════════════════════════════════════════════════════════

class TestSetActive:
    """Tests pour la fonction set_active()."""

    def test_suspend_user(self):
        """Suspendre un utilisateur → active devient False."""
        user_manager.register_user("alice", "password123")
        ok = user_manager.set_active("alice", False)

        assert ok is True
        assert user_manager.list_users()["alice"]["active"] is False

    def test_reactivate_user(self):
        """Réactiver un utilisateur → active redevient True."""
        user_manager.register_user("alice", "password123")
        user_manager.set_active("alice", False)
        ok = user_manager.set_active("alice", True)

        assert ok is True
        assert user_manager.list_users()["alice"]["active"] is True

    def test_set_active_nonexistent(self):
        """Utilisateur inexistant → échec."""
        ok = user_manager.set_active("nobody", False)
        assert ok is False

    def test_cannot_suspend_admin(self, isolate_users_file):
        """On ne peut PAS suspendre un admin."""
        users = {
            "admin": {
                "role": "admin",
                "active": True,
                "salt": "s",
                "password_hash": "h",
            }
        }
        with open(isolate_users_file, "w") as f:
            json.dump(users, f)

        ok = user_manager.set_active("admin", False)
        assert ok is False


# ═══════════════════════════════════════════════════════════════
# TESTS pour reset_password()
# ═══════════════════════════════════════════════════════════════

class TestResetPassword:
    """Tests pour la fonction reset_password()."""

    def test_reset_valid_password(self):
        """Reset avec mot de passe valide → succès."""
        user_manager.register_user("alice", "oldpass123")
        ok = user_manager.reset_password("alice", "newpass456")

        assert ok is True
        # Vérifier que l'ancien mot de passe ne marche plus
        assert user_manager.authenticate("alice", "oldpass123")[0] is False
        # Et que le nouveau marche
        assert user_manager.authenticate("alice", "newpass456")[0] is True

    def test_reset_short_password(self):
        """Mot de passe < 6 caractères → échec."""
        user_manager.register_user("alice", "oldpass123")
        ok = user_manager.reset_password("alice", "abc")
        assert ok is False

    def test_reset_nonexistent_user(self):
        """Utilisateur inexistant → échec."""
        ok = user_manager.reset_password("nobody", "newpass456")
        assert ok is False

    def test_reset_generates_new_salt(self, isolate_users_file):
        """Le reset génère un nouveau salt (sécurité)."""
        user_manager.register_user("alice", "oldpass123")
        with open(isolate_users_file, "r") as f:
            old_salt = json.load(f)["alice"]["salt"]

        user_manager.reset_password("alice", "newpass456")
        with open(isolate_users_file, "r") as f:
            new_salt = json.load(f)["alice"]["salt"]

        assert old_salt != new_salt


# ═══════════════════════════════════════════════════════════════
# TESTS pour set_plan() et get_plan()
# ═══════════════════════════════════════════════════════════════

class TestPlans:
    """Tests pour set_plan(), get_plan() et get_tier()."""

    def test_default_plan_is_free(self):
        """Nouvel utilisateur → plan 'free' par défaut."""
        user_manager.register_user("alice", "password123")
        assert user_manager.get_plan("alice") == "free"
        assert user_manager.get_tier("alice") == 0

    def test_set_premium_plan(self):
        """Activer premium → get_plan renvoie 'premium'."""
        user_manager.register_user("alice", "password123")
        user_manager.set_plan("alice", "premium", days=30)

        assert user_manager.get_plan("alice") == "premium"
        assert user_manager.get_tier("alice") == 2

    def test_set_premium_plus_plan(self):
        """Activer premium_plus → tier 3."""
        user_manager.register_user("alice", "password123")
        user_manager.set_plan("alice", "premium_plus", days=30)

        assert user_manager.get_plan("alice") == "premium_plus"
        assert user_manager.get_tier("alice") == 3

    def test_set_basique_plan(self):
        """Activer basique → tier 1."""
        user_manager.register_user("alice", "password123")
        user_manager.set_plan("alice", "basique", days=30)

        assert user_manager.get_plan("alice") == "basique"
        assert user_manager.get_tier("alice") == 1

    def test_expired_plan_returns_free(self, isolate_users_file):
        """Un plan expiré → revient automatiquement à 'free'."""
        user_manager.register_user("alice", "password123")
        # Forcer un plan expiré (dans le passé)
        users = user_manager.list_users()
        users["alice"]["plan"] = "premium"
        users["alice"]["premium_expires"] = (
            datetime.now() - timedelta(days=1)
        ).isoformat()
        with open(isolate_users_file, "w") as f:
            json.dump(users, f)

        assert user_manager.get_plan("alice") == "free"
        assert user_manager.get_tier("alice") == 0

    def test_set_free_removes_expiration(self):
        """Repasser en 'free' → premium_expires devient None."""
        user_manager.register_user("alice", "password123")
        user_manager.set_plan("alice", "premium", days=30)
        user_manager.set_plan("alice", "free")

        users = user_manager.list_users()
        assert users["alice"]["plan"] == "free"
        assert users["alice"]["premium_expires"] is None

    def test_set_plan_nonexistent_user(self):
        """Utilisateur inexistant → échec."""
        ok = user_manager.set_plan("nobody", "premium")
        assert ok is False

    def test_get_plan_nonexistent_user(self):
        """Utilisateur inexistant → 'free'."""
        assert user_manager.get_plan("nobody") == "free"
        assert user_manager.get_tier("nobody") == 0