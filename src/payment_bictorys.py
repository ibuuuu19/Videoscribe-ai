import requests
import streamlit as st
import uuid

def create_bictorys_checkout(amount, currency="XOF", country="SN"):
    """
    Crée une session de paiement Bictorys (mode Checkout).
    L'utilisateur sera redirigé vers la page de paiement Bictorys.
    """
    api_key = st.secrets.get("BICTORYS_PUBLIC_KEY")
    if not api_key:
        return {"error": "Clé API Bictorys non configurée."}

    # Mode test : api.test.bictorys.com
    # Mode production : api.bictorys.com
    url = "https://api.test.bictorys.com/pay/v1/charges"

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    # Référence unique pour cette commande
    merchant_ref = str(uuid.uuid4())

    payload = {
        "amount": amount,
        "currency": currency,
        "country": country,
        "merchantReference": merchant_ref,
        # URLs de redirection après paiement (adapte à ton app)
        "successRedirectUrl": "https://videoscr-be-ia.streamlit.app/?page=premium&status=success",
        "errorRedirectUrl": "https://videoscr-be-ia.streamlit.app/?page=premium&status=error",
        "customer": {
            "name": "Client VideoScribe",
            "email": "client@example.com"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Bictorys renvoie généralement une URL de redirection
        if data.get("redirectUrl"):
            return {"checkout_url": data["redirectUrl"]}
        return {"data": data}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}