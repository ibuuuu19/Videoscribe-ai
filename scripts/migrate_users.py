"""Migre les utilisateurs JSON → PostgreSQL."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.db import db_cursor

# Lire users.json
users_file = Path("data/users.json")
if not users_file.exists():
    print("❌ data/users.json introuvable")
    exit(1)

old_users = json.loads(users_file.read_text(encoding="utf-8"))
print(f"📋 {len(old_users)} utilisateurs trouvés dans JSON")

# Vérifier combien sont déjà en DB
with db_cursor() as cur:
    cur.execute("SELECT username FROM users")
    existing = {row[0] for row in cur.fetchall()}
print(f"📋 {len(existing)} utilisateurs déjà en PostgreSQL")

# Migrer ceux qui manquent
migrated = 0
for username, data in old_users.items():
    if username in existing:
        print(f"   ⏭️  {username} (déjà en DB)")
        continue

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (username, email, salt, password_hash, role, active, plan, premium_expires, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                username,
                data.get("email", ""),
                data.get("salt", ""),
                data.get("password_hash", ""),
                data.get("role", "client"),
                data.get("active", True),
                data.get("plan", "free"),
                data.get("premium_expires"),
                data.get("created_at"),
            ),
        )
    print(f"   ✅ {username} migré")
    migrated += 1

print(f"\n🎉 {migrated} utilisateurs migrés !")

# Vérification finale
with db_cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM users")
    row = cur.fetchone()
    total = row[0] if row else 0