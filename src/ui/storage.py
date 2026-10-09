"""
Module de stockage local — Favoris, partages, exports.

Contient :
- Code de parrainage (généré à partir du username + date)
- Gestion des favoris (data/favoris.json)
- Gestion des partages publics (data/shares.json)
- Export Anki (flashcards)
- Génération audio (gTTS, optionnel)

Extrait de app.py pour alléger le fichier principal (~80 lignes).

Usage:
    from src.ui.storage import load_favs, toggle_fav, save_share
"""

import json
import time
import hashlib
from pathlib import Path

from src.user_manager import list_users


# ═══════════════════════════════════════════════════════════════
# CODE DE PARRAINAGE
# ═══════════════════════════════════════════════════════════════

def get_referral_code(uname):
    """Génère un code de parrainage unique à partir du username + date de création."""
    info = list_users().get(uname, {}) or {}
    created = info.get("created_at", "")
    digits = "".join(c for c in created if c.isdigit())[:6]
    name_part = "".join(c for c in uname if c.isalnum())[:6].upper()
    return f"{name_part}{digits}"


# ═══════════════════════════════════════════════════════════════
# FAVORIS
# ═══════════════════════════════════════════════════════════════

def _fav_file():
    """Retourne le chemin du fichier de favoris."""
    return Path("data") / "favoris.json"


def load_favs(uname):
    """Retourne la liste des IDs de vidéos favorites d'un utilisateur."""
    p = _fav_file()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8")).get(uname, [])
        except Exception:
            return []
    return []


def toggle_fav(uname, vid):
    """Ajoute/retire une vidéo des favoris. Retourne True si ajoutée, False si retirée."""
    p = _fav_file()
    allf = {}
    if p.exists():
        try:
            allf = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            allf = {}
    lst = allf.get(uname, [])
    if vid in lst:
        lst.remove(vid)
    else:
        lst.append(vid)
    allf[uname] = lst
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(allf, ensure_ascii=False), encoding="utf-8")
    return vid in lst


# ═══════════════════════════════════════════════════════════════
# PARTAGES PUBLICS
# ═══════════════════════════════════════════════════════════════

def _shares_file():
    """Retourne le chemin du fichier de partages."""
    return Path("data") / "shares.json"


def load_shares():
    """Charge tous les partages depuis le fichier JSON."""
    p = _shares_file()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_share(data, owner):
    """Crée un partage public. Retourne l'ID unique (8 caractères)."""
    shares = load_shares()
    sid = hashlib.md5((data["video_id"] + str(time.time())).encode()).hexdigest()[:8]
    shares[sid] = {
        "video_id": data["video_id"],
        "notes": data["notes"],
        "keywords": data.get("keywords", []),
        "date": data["date"],
        "owner": owner,
    }
    _shares_file().parent.mkdir(parents=True, exist_ok=True)
    _shares_file().write_text(json.dumps(shares, ensure_ascii=False), encoding="utf-8")
    return sid


# ═══════════════════════════════════════════════════════════════
# EXPORT ANKI (flashcards)
# ═══════════════════════════════════════════════════════════════

def export_anki(data, filename):
    """Exporte les mots-clés et questions en format Anki (TSV)."""
    lines = []
    for kw, _ in data.get("keywords", []):
        ans = next((n for n in data["notes"] if kw.split()[0].lower() in n.lower()), "")
        lines.append(f"{kw}\t{ans}")
    for q in data.get("questions", []):
        lines.append(f"{q}\tVoir le résumé VideoScribe AI")
    p = Path("exports") / f"{filename}.anki.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines), encoding="utf-8")
    return str(p)


# ═══════════════════════════════════════════════════════════════
# GÉNÉRATION AUDIO (gTTS)
# ═══════════════════════════════════════════════════════════════

def generate_audio(text, filename):
    """Génère un MP3 à partir du texte. Retourne le chemin ou None si échec."""
    try:
        from gtts import gTTS
        p = Path("exports") / f"{filename}.mp3"
        p.parent.mkdir(parents=True, exist_ok=True)
        gTTS(text=text, lang="fr").save(str(p))
        return str(p)
    except Exception:
        return None