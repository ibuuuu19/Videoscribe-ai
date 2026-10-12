"""Test rapide du gestionnaire de revenus PostgreSQL."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.revenue_manager import record_revenue, get_revenues
from src.core.db import db_cursor

# Nettoyage
with db_cursor() as cur:
    cur.execute("DELETE FROM revenues")
print("Revenus vides")

# Test get vide
revs = get_revenues()
print(f"get_revenues vide : {len(revs)} revenus")

# Test create (plusieurs paiements)
record_revenue("ibuuuu_19", "premium", 4.99, 30, "manuel")
record_revenue("ibuuuu_19", "premium_plus", 9.99, 365, "cinetpay")
record_revenue("test_user", "basique", 1.99, 30, "wave")
print("3 revenus enregistres")

# Test get
revs = get_revenues()
print(f"get_revenues : {len(revs)} revenus")
for r in revs:
    print(f"  - [{r['source']}] {r['user']} : {r['plan']} ${r['amount']} ({r['days']}j) le {r['date']}")

# Nettoyage final
with db_cursor() as cur:
    cur.execute("DELETE FROM revenues")
print("Nettoyage final")