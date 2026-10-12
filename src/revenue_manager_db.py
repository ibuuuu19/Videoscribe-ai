"""
Module de gestion des revenus — Version PostgreSQL.

Mêmes fonctions que revenue_manager.py mais utilise PostgreSQL (Supabase).

Le champ `user` du JSON devient `user_id` (FK) en PostgreSQL, mais 
get_revenues() retourne le username pour compatibilité.

Usage:
    from src.revenue_manager_db import record_revenue, get_revenues
"""

from src.core.db import db_cursor


def _get_user_id(username):
    """Retourne l'ID de l'utilisateur (ou None)."""
    with db_cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        return row[0] if row else None


def record_revenue(user, plan, amount, days=30, source="manuel"):
    """
    Enregistre un paiement.
    
    Args:
        user: Nom de l'utilisateur
        plan: "basique" | "premium" | "premium_plus"
        amount: Montant en USD
        days: Durée en jours
        source: "manuel" | "cinetpay" | "wave" | "om"
    """
    user_id = _get_user_id(user)
    if not user_id:
        return False

    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO revenues (user_id, plan, amount, days, method)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, plan, amount, days, source),
        )
    return True


def get_revenues():
    """
    Retourne tous les paiements (plus récents en premier).
    
    Format de retour (compatibilité JSON) :
        [
            {
                "user": "ibuuuu_19",
                "plan": "premium",
                "amount": 4.99,
                "days": 30,
                "source": "manuel",
                "date": "11/10/2026",
            },
            ...
        ]
    """
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT u.username, r.plan, r.amount, r.days, r.method, r.date
            FROM revenues r
            JOIN users u ON u.id = r.user_id
            ORDER BY r.date DESC
            """
        )
        rows = cur.fetchall()

    return [
        {
            "user": row[0] or "unknown",
            "plan": row[1] or "free",
            "amount": float(row[2]) if row[2] else 0.0,
            "days": row[3] or 30,
            "source": row[4] or "manuel",
            "date": row[5].strftime("%d/%m/%Y") if row[5] else "",
        }
        for row in rows
    ]