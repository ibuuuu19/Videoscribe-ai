import json
import secrets
import time
from pathlib import Path
import requests

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PAYMENTS_FILE = DATA_DIR / "payments.json"

CINETPAY_BASE = "https://api.cinetpay.com/v2"


def _load():
    if PAYMENTS_FILE.exists():
        try:
            return json.load(open(PAYMENTS_FILE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save(payments):
    json.dump(payments, open(PAYMENTS_FILE, "w", encoding="utf-8"), indent=2)


def create_payment(username, amount, apikey, site_id, currency="XOF"):
    """Crée une transaction CinetPay → renvoie (transaction_id, payment_url)."""
    tx_id = f"YTSAI-{int(time.time())}-{secrets.token_hex(4)}"
    payload = {
        "apikey": apikey,
        "site_id": site_id,
        "transaction_id": tx_id,
        "transaction_amount": int(amount),
        "transaction_currency": currency,
        "description": "Abonnement Premium 30 jours - YouTube Summarizer AI",
        "customer_name": username,
        "return_url": "http://localhost:8501",
        "cancel_url": "http://localhost:8501",
        "notification_url": "http://localhost:8501",
    }
    r = requests.post(f"{CINETPAY_BASE}/payment", json=payload, timeout=30)
    data = r.json()
    if str(data.get("code")) in ("200", "201"):
        url = data["data"]["payment_url"]
        payments = _load()
        payments[tx_id] = {"user": username, "amount": amount,
                           "status": "PENDING", "created": time.time()}
        _save(payments)
        return tx_id, url
    raise Exception(f"CinetPay : {data.get('message', 'erreur inconnue')}")


def check_payment(tx_id, apikey, site_id):
    """Vérifie le statut (ACCEPTED / PENDING / REFUSED). Pas besoin de webhook."""
    r = requests.post(f"{CINETPAY_BASE}/payment/check",
                      json={"apikey": apikey, "site_id": site_id,
                            "transaction_id": tx_id}, timeout=30)
    data = r.json()
    status = data.get("data", {}).get("status", "PENDING")
    if status == "ACCEPTED":
        payments = _load()
        if tx_id in payments:
            payments[tx_id]["status"] = "ACCEPTED"
            _save(payments)
    return status