"""
Configuration globale de VideoScribe AI.

Contient toutes les constantes de l'application :
- Informations de contact et paiement
- Configuration des plans tarifaires
- Constantes de l'interface (couleurs, map, etc.)
- Chemins de fichiers

Extrait de app.py pour être importable depuis n'importe quel module.

Usage:
    from src.core.config import PLANS, CONTACT_EMAIL, TIER_CHIP
"""

from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# INFORMATIONS DE CONTACT & PAIEMENT
# ═══════════════════════════════════════════════════════════════

CONTACT_EMAIL = "mbtech19.sn@gmail.com"
PAYMENT_WAVE = "77 629 50 40"
PAYMENT_OM = "77 629 50 40"      # Orange Money (même numéro que Wave)
CINETPAY_APIKEY = ""              # À remplir en production
CINETPAY_SITE_ID = ""             # À remplir en production

FREE_DAILY_LIMIT = 3              # Limite du plan gratuit (analyses/jour)


# ═══════════════════════════════════════════════════════════════
# MAP & DÉMO
# ═══════════════════════════════════════════════════════════════

MAP_EMBED = "https://www.google.com/maps?q=Camb%C3%A9r%C3%A8ne,+Dakar,+S%C3%A9n%C3%A9gal&output=embed"
MAP_LINK = "https://www.google.com/maps?q=Camb%C3%A9r%C3%A8ne,+Dakar,+S%C3%A9n%C3%A9gal"
DEMO_VIDEO_URL = ""


# ═══════════════════════════════════════════════════════════════
# PLANS TARIFAIRES
# ═══════════════════════════════════════════════════════════════

PLANS = {
    "basique": {
        "tier": 1,
        "chip": "BASIQUE",
        "name": "Basique",
        "monthly": 1.99,
        "annual": 19,
    },
    "premium": {
        "tier": 2,
        "chip": "PREMIUM",
        "name": "Premium",
        "monthly": 4.99,
        "annual": 49,
    },
    "premium_plus": {
        "tier": 3,
        "chip": "PLUS",
        "name": "Premium+",
        "monthly": 9.99,
        "annual": 99,
    },
}

# Chip affiché selon le tier (0=free → 3=premium+)
TIER_CHIP = {0: "FREE", 1: "BASIQUE", 2: "PREMIUM", 3: "PLUS"}

# Nombre d'analyses à conserver dans l'historique selon le tier
HIST_KEEP = {0: 10, 1: 100, 2: 999999, 3: 999999}


# ═══════════════════════════════════════════════════════════════
# CHEMINS DE FICHIERS
# ═══════════════════════════════════════════════════════════════

AVATAR_DIR = Path("data") / "avatars"


# ═══════════════════════════════════════════════════════════════
# COOKIES
# ═══════════════════════════════════════════════════════════════

COOKIE_NAME = "ys_token"