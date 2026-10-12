"""Verification directe des revenus dans PostgreSQL."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db import db_cursor

# Nettoyage
with db_cursor() as cur:
    cur.execute("DELETE FROM revenues")
print("Revenus vides")

# Verifier l'utilisateur
with db_cursor() as cur:
    cur.execute("SELECT id FROM users WHERE username = 'ibuuuu_19'")
    row = cur.fetchone()
    if not row:
        print("ERREUR: ibuuuu_19 n'existe pas")
        exit(1)
    user_id = row[0]
    print(f"user_id = {user_id}")

# Inserer 3 revenus DIRECTEMENT en SQL
with db_cursor() as cur:
    cur.execute(
        "INSERT INTO revenues (user_id, plan, amount, days, method) VALUES (%s, %s, %s, %s, %s)",
        (user_id, 'premium', 4.99, 30, 'manuel'),
    )
    cur.execute(
        "INSERT INTO revenues (user_id, plan, amount, days, method) VALUES (%s, %s, %s, %s, %s)",
        (user_id, 'premium_plus', 9.99, 365, 'cinetpay'),
    )
    cur.execute(
        "INSERT INTO revenues (user_id, plan, amount, days, method) VALUES (%s, %s, %s, %s, %s)",
        (user_id, 'basique', 1.99, 30, 'wave'),
    )
print("3 revenus inseres en SQL direct")

# Verification 1 : COUNT en SQL
with db_cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM revenues")
    row = cur.fetchone()
    count = row[0] if row else 0
print(f"COUNT(*) FROM revenues : {count}")

# Verification 2 : lignes brutes
with db_cursor() as cur:
    cur.execute("SELECT id, user_id, plan, amount, method FROM revenues ORDER BY id")
    rows = cur.fetchall()
    print("Lignes brutes :")
    for r in rows:
        print(f"  {r}")

# Verification 3 : via get_revenues()
from src.revenue_manager import get_revenues
revs = get_revenues()
print(f"get_revenues : {len(revs)} revenus")
for r in revs:
    print(f"  - [{r['source']}] {r['user']} : {r['plan']} ${r['amount']}")

# Nettoyage
with db_cursor() as cur:
    cur.execute("DELETE FROM revenues")
print("Nettoyage final")