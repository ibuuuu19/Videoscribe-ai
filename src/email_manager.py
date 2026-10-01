import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Lecture des secrets : priorité st.secrets (Streamlit Cloud) → os.getenv (local) ──
def _get_secret(key, default=""):
    """Lit d'abord st.secrets (Streamlit Cloud), puis os.environ (local)."""
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

SMTP_HOST = _get_secret("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(_get_secret("SMTP_PORT", "587"))
SMTP_USER = (_get_secret("SMTP_USER") or _get_secret("EMAIL_USER")
             or _get_secret("GMAIL_USER") or "mbtech19.sn@gmail.com")
SMTP_PASS = (_get_secret("SMTP_PASS") or _get_secret("EMAIL_PASS")
             or _get_secret("GMAIL_APP_PASSWORD") or "")

SENDER_NAME = "VideoScribe AI — Mbtech-services"
BRAND = "VideoScribe AI"

# Couleurs de la marque
NAVY = "#0B1F3A"
BLUE = "#2E6DB4"
GOLD = "#D4AF37"
LIGHT = "#F5F7FB"


def _verification_html(code: str) -> str:
    """Gabarit HTML professionnel pour le code de vérification."""
    return f"""
    <div style="margin:0; padding:0; background:{LIGHT}; font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{LIGHT}; padding:24px 0;">
        <tr><td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e3e8f0;">

            <!-- En-tête brandé -->
            <tr><td style="background:linear-gradient(135deg,{NAVY} 0%,{BLUE} 100%); padding:28px 32px; text-align:center;">
              <div style="font-size:26px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">✍️ {BRAND}</div>
              <div style="color:rgba(255,255,255,.85); font-size:13px; margin-top:6px;">Mbtech-services · Sénégal</div>
            </td></tr>

            <!-- Corps -->
            <tr><td style="padding:32px;">
              <div style="font-size:20px; font-weight:700; color:{NAVY};">🔐 Vérification de votre adresse email</div>
              <p style="color:#4A5A7A; font-size:15px; line-height:1.6; margin:16px 0 24px;">
                Bonjour,<br><br>
                Merci d'avoir choisi <b>{BRAND}</b>. Utilisez le code ci-dessous pour confirmer votre adresse email et finaliser la création de votre compte.
              </p>

              <!-- Encadré du code -->
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr><td align="center" style="background:{LIGHT}; border:2px dashed {BLUE}; border-radius:12px; padding:20px;">
                  <div style="font-size:32px; font-weight:800; letter-spacing:8px; color:{NAVY}; font-family:'Courier New',monospace;">{code}</div>
                  <div style="color:#4A5A7A; font-size:12px; margin-top:8px;">Valable 5 minutes</div>
                </td></tr>
              </table>

              <p style="color:#8a94a6; font-size:13px; line-height:1.6; margin:24px 0 0;">
                ⚠️ Ne partagez jamais ce code. Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email.
              </p>
            </td></tr>

            <!-- Pied de page -->
            <tr><td style="background:{NAVY}; padding:20px 32px; text-align:center;">
              <div style="color:rgba(255,255,255,.9); font-size:13px; font-weight:600;">{BRAND}</div>
              <div style="color:rgba(255,255,255,.6); font-size:12px; margin-top:4px;">
                Transformez vos vidéos YouTube en notes structurées avec l'IA
              </div>
              <div style="color:{GOLD}; font-size:12px; margin-top:10px;">
                © 2026 Mbtech-services · <a href="mailto:{SMTP_USER}" style="color:{GOLD}; text-decoration:none;">{SMTP_USER}</a>
              </div>
            </td></tr>

          </table>
        </td></tr>
      </table>
    </div>
    """


def _verification_text(code: str) -> str:
    """Version texte de secours (clients sans HTML)."""
    return (f"{BRAND} — Code de vérification\n\n"
            f"Bonjour,\n\nVotre code de vérification : {code}\n"
            f"Valable 5 minutes. Ne le partagez pas.\n\n— Mbtech-services")


def send_verification_code(email: str, code: str):
    """Envoie le code de vérification. Retourne (ok, message_erreur)."""
    if not SMTP_PASS:
        return False, "SMTP non configuré (mot de passe d'application absent)"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔐 Votre code de vérification — {BRAND}"
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = email

    msg.attach(MIMEText(_verification_text(code), "plain", "utf-8"))
    msg.attach(MIMEText(_verification_html(code), "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [email], msg.as_string())
        return True, ""
    except Exception as e:
        return False, f"Échec d'envoi : {e}"
    
def _urgency_color(urgency: str) -> str:
    return {"normale": BLUE, "importante": "#F97316", "urgente": "#DC2626"}.get(urgency, BLUE)


def _contact_admin_html(client_name, client_email, subject, message, urgency) -> str:
    col = _urgency_color(urgency)
    return f"""
    <div style="margin:0; padding:0; background:{LIGHT}; font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{LIGHT}; padding:24px 0;">
        <tr><td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e3e8f0;">
            <tr><td style="background:linear-gradient(135deg,{NAVY} 0%,{BLUE} 100%); padding:24px 32px; text-align:center;">
              <div style="font-size:24px; font-weight:800; color:#ffffff;">📩 Nouveau message client</div>
              <div style="color:rgba(255,255,255,.85); font-size:13px; margin-top:6px;">{BRAND} · Support</div>
            </td></tr>
            <tr><td style="padding:28px 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-size:14px; color:#4A5A7A; margin-bottom:20px;">
                <tr><td style="padding:6px 0;"><b style="color:{NAVY};">Client :</b> {client_name}</td></tr>
                <tr><td style="padding:6px 0;"><b style="color:{NAVY};">Email :</b> {client_email or '—'}</td></tr>
                <tr><td style="padding:6px 0;"><b style="color:{NAVY};">Priorité :</b>
                  <span style="background:{col}; color:#ffffff; padding:3px 12px; border-radius:20px; font-size:12px; font-weight:700;">{urgency.upper()}</span></td></tr>
                <tr><td style="padding:6px 0;"><b style="color:{NAVY};">Sujet :</b> {subject}</td></tr>
              </table>
              <div style="background:{LIGHT}; border-left:4px solid {col}; border-radius:8px; padding:16px; color:#33415c; font-size:14px; line-height:1.6; white-space:pre-wrap;">{message}</div>
            </td></tr>
            <tr><td style="background:{NAVY}; padding:16px 32px; text-align:center;">
              <div style="color:rgba(255,255,255,.7); font-size:12px;">© 2026 Mbtech-services · {SMTP_USER}</div>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </div>
    """


def _contact_ack_html(client_name, subject) -> str:
    return f"""
    <div style="margin:0; padding:0; background:{LIGHT}; font-family:Arial,Helvetica,sans-serif;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{LIGHT}; padding:24px 0;">
        <tr><td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px; background:#ffffff; border-radius:16px; overflow:hidden; border:1px solid #e3e8f0;">
            <tr><td style="background:linear-gradient(135deg,{NAVY} 0%,{BLUE} 100%); padding:24px 32px; text-align:center;">
              <div style="font-size:24px; font-weight:800; color:#ffffff;">✍️ {BRAND}</div>
            </td></tr>
            <tr><td style="padding:32px;">
              <div style="font-size:20px; font-weight:700; color:{NAVY};">✅ Message bien reçu !</div>
              <p style="color:#4A5A7A; font-size:15px; line-height:1.6; margin:16px 0;">
                Bonjour {client_name},<br><br>
                Nous avons bien reçu votre message «&nbsp;<b>{subject}</b>&nbsp;».
                Notre équipe vous répondra dans les plus brefs délais (généralement &lt; 24 h).
              </p>
              <p style="color:#8a94a6; font-size:13px;">Merci de votre confiance. — Mbtech-services</p>
            </td></tr>
            <tr><td style="background:{NAVY}; padding:16px 32px; text-align:center;">
              <div style="color:{GOLD}; font-size:12px;">© 2026 Mbtech-services</div>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </div>
    """


def send_contact_message(to_email, client_name, client_email, subject, message, urgency="normale"):
    """Envoie le message du client à l'admin. Retourne (ok, err)."""
    if not SMTP_PASS:
        return False, "SMTP non configuré"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📩 [{urgency.upper()}] {client_name} — {subject}"
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(f"Message de {client_name} ({client_email or '—'})\nPriorité: {urgency}\nSujet: {subject}\n\n{message}", "plain", "utf-8"))
    msg.attach(MIMEText(_contact_admin_html(client_name, client_email, subject, message, urgency), "html", "utf-8"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
            s.ehlo(); s.starttls(); s.ehlo(); s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [to_email], msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)


def send_contact_ack(client_email, client_name, subject):
    """Accusé de réception au client."""
    if not SMTP_PASS or not client_email:
        return False, "SMTP non configuré ou email client absent"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ Nous avons reçu votre message — {BRAND}"
    msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg["To"] = client_email
    msg.attach(MIMEText(f"Bonjour {client_name}, nous avons bien reçu votre message « {subject} ». — Mbtech-services", "plain", "utf-8"))
    msg.attach(MIMEText(_contact_ack_html(client_name, subject), "html", "utf-8"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
            s.ehlo(); s.starttls(); s.ehlo(); s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [client_email], msg.as_string())
        return True, ""
    except Exception as e:
        return False, str(e)    