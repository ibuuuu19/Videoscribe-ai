"""
Extraction de sous-titres YouTube avec 3 moteurs en cascade :
1. API YouTube Data v3 (officielle, jamais rate-limitée)
2. youtube-transcript-api (rapide)
3. yt-dlp (robuste aux blocages)
"""

import re
import json
import os
import unicodedata
import urllib.request
from pathlib import Path

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def extract_video_id(url):
    """Extrait l'ID vidéo depuis une URL YouTube."""
    if not url or not isinstance(url, str):
        return None
    patterns = [
        r"(?:v=|youtu\.be/|embed/|v/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def _cache_path(video_id, lang):
    return CACHE_DIR / f"{video_id}_{lang}.json"


def _load_cache(video_id, languages):
    for lang in languages + ['auto']:
        cache_file = _cache_path(video_id, lang)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"💾 Transcript depuis le cache ({data['lang']})")
                    return data['text'], data['lang']
            except Exception:
                pass
    return None, None


def _save_cache(video_id, lang, text):
    try:
        with open(_cache_path(video_id, lang), 'w', encoding='utf-8') as f:
            json.dump({'text': text, 'lang': lang}, f, ensure_ascii=False)
    except Exception:
        pass


def _get_api_key():
    """Récupère la clé API YouTube."""
    try:
        import streamlit as st
        key = st.secrets.get("YOUTUBE_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("YOUTUBE_API_KEY")


# ═══════════════════════════════════════════════════════════════
# NETTOYAGE DU TRANSCRIPT (anti-encodage cassé)
# ═══════════════════════════════════════════════════════════════

def clean_transcript(text):
    """Nettoie les caractères corrompus et les artefacts d'encodage."""
    if not text:
        return text

    # ✅ Remplace TOUS les '=' par des apostrophes (artefact fréquent)
    # Cela gère l=, d=, s=, n=, qu=, c=, j=, m=, t=, etc.
    text = re.sub(r"(\w)=", r"\1'", text)

    # ✅ Corrige les caractères accentués mal encodés (UTF-8 mal interprété)
    replacements = {
        "Ã©": "é", "Ã ̈": "è", "Ã ": "à", "Ãª": "ê", "Ã®": "î",
        "Ã´": "ô", "Ã»": "û", "Ã§": "ç", "Ã«": "ë", "Ã¯": "ï",
        "Ã¼": "ü", "Ã¿": "ÿ", "Ã¹": "ù", "Ã¢": "â",
        "Ã‰": "É", "Ã€": "À", "ÃŠ": "Ê", "Ã‡": "Ç",
        "â€™": "'", "â€œ": '"', "â€\x9d": '"', "â€“": "–", "â€”": "—",
        "â€¦": "...", "Â«": "«", "Â»": "»", "Â°": "°",
        "\u00a0": " ",  # Espace insécable
        "Ã©": "é", "Ã¨": "è", "Ã ": "à", "Ãª": "ê", "Ã®": "î",
        "Ã´": "ô", "Ã»": "û", "Ã§": "ç", "Ã«": "ë", "Ã¯": "ï",
        "Ã¼": "ü", "Ã¿": "ÿ", "Ã¹": "ù", "Ã¢": "â",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # ✅ Normalisation Unicode (corrige les accents décomposés)
    text = unicodedata.normalize("NFKC", text)

    # ✅ Supprime les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()

    return text
# ═══════════════════════════════════════════════════════════════
# MOTEUR 0 : API YouTube officielle
# ═══════════════════════════════════════════════════════════════

def _parse_sbv(content):
    """Parse le format SBV (YouTube captions download)."""
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if re.match(r'^\d+:\d+:\d+\.\d+,\d+:\d+:\d+\.\d+$', line):
            continue
        if not line or line.isdigit():
            continue 
        lines.append(line)
    text = " ".join(lines)
    return re.sub(r'\s+', ' ', text).strip()


def _try_youtube_api(video_id, languages):
    """Moteur 0 : API YouTube Data v3 (liste seulement)."""
    api_key = _get_api_key()
    if not api_key:
        return None, None, "YOUTUBE_API_KEY non configurée"

    try:
        from googleapiclient.discovery import build
    except ImportError:
        return None, None, "google-api-python-client non installé"

    try:
        youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
        resp = youtube.captions().list(part="snippet", videoId=video_id).execute()
        items = resp.get('items', [])

        if not items:
            return None, None, "Aucun sous-titre via API YouTube"

        available = [i['snippet']['language'] for i in items]
        print(f"[transcript] API YouTube: langues dispo = {available[:5]}...")

        return None, None, f"API v3 ne peut pas télécharger (langues dispo: {available})"
    except Exception as e:
        return None, None, f"{type(e).__name__}: {str(e)[:150]}"


# ═══════════════════════════════════════════════════════════════
# MOTEUR 1 : youtube-transcript-api
# ═══════════════════════════════════════════════════════════════

def _try_transcript_api(video_id, languages):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
    except ImportError:
        return None, None, "youtube-transcript-api non installé"

    try:
        api = YouTubeTranscriptApi()
        for lang in languages:
            try:
                transcript = api.fetch(video_id, languages=[lang])
                text = " ".join([t.text for t in transcript])
                if text and len(text) > 50:
                    return text, lang, None
            except NoTranscriptFound:
                continue
        return None, None, "Aucun sous-titre trouvé"

    except TranscriptsDisabled:
        return None, None, "Sous-titres désactivés"
    except Exception as e:
        err_name = type(e).__name__
        err_msg = str(e).lower()

        if "ipblock" in err_name.lower() or "ipblocked" in err_msg:
            return None, None, "YOUTUBE_BLOCKED"
        if "429" in err_msg or "too many requests" in err_msg:
            return None, None, "YOUTUBE_RATE_LIMIT"
        if "resolve" in err_msg or "nodename" in err_msg:
            return None, None, "NETWORK_DNS"
        if "timeout" in err_msg or "timed out" in err_msg:
            return None, None, "NETWORK_TIMEOUT"
        if "connection" in err_msg or "connectionpool" in err_msg:
            return None, None, "NETWORK_CONNECTION"

        return None, None, f"{err_name}: {str(e)[:150]}"


# ═══════════════════════════════════════════════════════════════
# MOTEUR 2 : yt-dlp
# ═══════════════════════════════════════════════════════════════

def _extract_text_from_json3(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8')
        if content.strip().startswith('#EXTM3U'):
            return None
        data = json.loads(content)
        events = data.get('events', [])
        parts = []
        for e in events:
            if 'segs' in e:
                parts.append("".join(seg.get('utf8', '') for seg in e['segs']))
        text = " ".join(parts)
        return re.sub(r'\s+', ' ', text).strip() or None
    except Exception as e:
        print(f"[transcript] Erreur json3: {e}")
        return None


def _extract_text_from_vtt(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            vtt = r.read().decode('utf-8', errors='ignore')
        if vtt.strip().startswith('#EXTM3U'):
            return None
        lines = []
        for line in vtt.split('\n'):
            line = line.strip()
            if not line or line.startswith('WEBVTT') or '-->' in line or line.isdigit():
                continue
            line = re.sub(r'<[^>]+>', '', line)
            if line:
                lines.append(line)
        text = " ".join(lines)
        return re.sub(r'\s+', ' ', text).strip() or None
    except Exception as e:
        print(f"[transcript] Erreur vtt: {e}")
        return None


def _try_ytdlp(video_id, languages):
    try:
        import yt_dlp
    except ImportError:
        return None, None, "yt-dlp non installé"

    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': languages + ['en'],
        'subtitlesformat': 'json3/vtt/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android_vr', 'web_safari', 'tv'],
                'skip': ['hls', 'dash'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        'socket_timeout': 15,
    }

    for cookie_file in [os.environ.get('YTDLP_COOKIES', ''), 'youtube-cookies.txt']:
        if cookie_file and Path(cookie_file).exists():
            ydl_opts['cookiefile'] = cookie_file
            print(f"[transcript] 🍪 Cookies: {cookie_file}")
            break

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subs = info.get('subtitles', {}) or {}
            auto_subs = info.get('automatic_captions', {}) or {}
            all_subs = {**subs, **auto_subs}

            if not all_subs:
                return None, None, "Aucun sous-titre disponible"

            priority = [l for l in languages if l in all_subs]
            others = [l for l in all_subs if l not in priority]
            ordered = priority + others

            for lang in ordered:
                tracks = all_subs[lang]
                for t in tracks:
                    if t.get('ext') == 'json3':
                        text = _extract_text_from_json3(t['url'])
                        if text and len(text) > 50:
                            return text, lang, None
                for t in tracks:
                    if t.get('ext') == 'vtt':
                        text = _extract_text_from_vtt(t['url'])
                        if text and len(text) > 50:
                            return text, lang, None

        return None, None, "Aucune piste exploitable"

    except Exception as e:
        err_name = type(e).__name__
        err_msg = str(e).lower()

        if "resolve" in err_msg or "nodename" in err_msg or "name or service" in err_msg:
            return None, None, "NETWORK_DNS"
        if "timeout" in err_msg or "timed out" in err_msg:
            return None, None, "NETWORK_TIMEOUT"
        if "connection" in err_msg or "connectionpool" in err_msg:
            return None, None, "NETWORK_CONNECTION"
        if "sign in to confirm" in err_msg or "bot" in err_msg:
            return None, None, "YOUTUBE_BLOCKED"
        if "429" in err_msg or "too many requests" in err_msg:
            return None, None, "YOUTUBE_RATE_LIMIT"

        return None, None, f"{err_name}: {str(e)[:150]}"


# ═══════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════

def get_transcript(video_id, languages=None, use_cache=True):
    """Récupère les sous-titres (3 moteurs en cascade + nettoyage)."""
    if languages is None:
        languages = ['fr', 'en', 'es', 'de', 'it', 'pt']

    # Cache
    if use_cache:
        text, lang = _load_cache(video_id, languages)
        if text:
            return clean_transcript(text), lang

    errors = {}

    # ── Moteur 1 : API YouTube v3 ──
    print("[transcript] Tentative API YouTube officielle...")
    text, lang, err = _try_youtube_api(video_id, languages)
    if text:
        print(f"[transcript] ✅ API YouTube OK ({lang}) — {len(text)} chars")
        text = clean_transcript(text)
        if use_cache:
            _save_cache(video_id, lang, text)
        return text, lang
    errors['api'] = err
    print(f"[transcript] ❌ API YouTube: {err}")

    # ── Moteur 2 : youtube-transcript-api ──
    print("[transcript] Tentative youtube-transcript-api...")
    text, lang, err2 = _try_transcript_api(video_id, languages)
    if text:
        print(f"[transcript] ✅ youtube-transcript-api OK ({lang})")
        text = clean_transcript(text)
        if use_cache:
            _save_cache(video_id, lang, text)
        return text, lang
    errors['transcript_api'] = err2
    print(f"[transcript] ❌ youtube-transcript-api: {err2}")

    # ── Moteur 3 : yt-dlp ──
    print("[transcript] Tentative yt-dlp...")
    text, lang, err3 = _try_ytdlp(video_id, languages)
    if text:
        print(f"[transcript] ✅ yt-dlp OK ({lang})")
        text = clean_transcript(text)
        if use_cache:
            _save_cache(video_id, lang, text)
        return text, lang
    errors['ytdlp'] = err3
    print(f"[transcript] ❌ yt-dlp: {err3}")

    # ── Toutes les erreurs ──
    all_errors = " ".join(str(v) for v in errors.values() if v)

    if "NETWORK_DNS" in all_errors:
        return "Error: Impossible de joindre YouTube. Vérifiez votre connexion internet.", None
    if "NETWORK_TIMEOUT" in all_errors:
        return "Error: YouTube ne répond pas. Réessayez dans quelques minutes.", None
    if "NETWORK_CONNECTION" in all_errors:
        return "Error: Problème de connexion réseau. Vérifiez votre WiFi/VPN.", None
    if "YOUTUBE_RATE_LIMIT" in all_errors:
        return "Error: YouTube a temporairement bloqué les requêtes. Réessayez dans 15-30 min.", None
    if "YOUTUBE_BLOCKED" in all_errors:
        return "Error: YouTube bloque l'accès depuis ce serveur. Utilisez un service tiers ou des cookies.", None
    if "Sous-titres désactivés" in all_errors:
        return "Error: L'auteur a désactivé les sous-titres pour cette vidéo.", None

    return f"Error: Aucun transcript disponible (détails : {all_errors[:200]})", None