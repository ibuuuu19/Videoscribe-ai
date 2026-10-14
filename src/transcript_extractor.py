"""
Extraction de sous-titres YouTube avec 3 moteurs en cascade :
1. API YouTube Data v3 (officielle, jamais rate-limitée) ← NOUVEAU
2. youtube-transcript-api (rapide)
3. yt-dlp (robuste aux blocages)
"""

import re
import json
import os
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
    """
    Moteur 0 : API YouTube Data v3.
    ⚠️ Ne peut PAS télécharger les sous-titres (401 sans OAuth).
    Sert juste à CONFIRMER quels sous-titres existent → accélère le fallback.
    """
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

        # ✅ Récupère la liste des langues dispo (utile pour le fallback)
        available = [i['snippet']['language'] for i in items]
        print(f"[transcript] API YouTube: langues dispo = {available[:5]}...")

        # ✅ API v3 ne peut pas télécharger sans OAuth → on retourne les langues pour le fallback
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
        return None, None, f"{type(e).__name__}: {str(e)[:150]}"


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
        'subtitleslangs': languages,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        from typing import Any, cast
        with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
            info = ydl.extract_info(url, download=False)
            all_subs = {**(info.get('subtitles') or {}), **(info.get('automatic_captions') or {})}
            if not all_subs:
                return None, None, "Aucun sous-titre disponible"

            priority = [l for l in languages if l in all_subs]
            others = [l for l in all_subs if l not in priority]
            for lang in priority + others:
                for t in all_subs[lang]:
                    if t.get('ext') == 'json3':
                        text = _extract_text_from_json3(t['url'])
                        if text and len(text) > 50:
                            return text, lang, None
                for t in all_subs[lang]:
                    if t.get('ext') == 'vtt':
                        text = _extract_text_from_vtt(t['url'])
                        if text and len(text) > 50:
                            return text, lang, None
        return None, None, "Aucune piste exploitable"
    except Exception as e:
        return None, None, f"{type(e).__name__}: {str(e)[:150]}"


# ═══════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════

def get_transcript(video_id, languages=None, use_cache=True):
    """Récupère les sous-titres (3 moteurs en cascade)."""
    if languages is None:
        languages = ['fr', 'en', 'es', 'de', 'it', 'pt']

    if use_cache:
        text, lang = _load_cache(video_id, languages)
        if text:
            return text, lang

    # Moteur 0 : API YouTube officielle
    print("[transcript] Tentative API YouTube officielle...")
    text, lang, err = _try_youtube_api(video_id, languages)
    if text:
        print(f"[transcript] ✅ API YouTube OK ({lang}) — {len(text)} chars")
        if use_cache:
            _save_cache(video_id, lang, text)
        return text, lang
    print(f"[transcript] ❌ API YouTube: {err}")

    # Moteur 1 : youtube-transcript-api
    print("[transcript] Tentative youtube-transcript-api...")
    text, lang, err2 = _try_transcript_api(video_id, languages)
    if text:
        print(f"[transcript] ✅ youtube-transcript-api OK ({lang})")
        if use_cache:
            _save_cache(video_id, lang, text)
        return text, lang
    print(f"[transcript] ❌ youtube-transcript-api: {err2}")

    # Moteur 2 : yt-dlp
    print("[transcript] Tentative yt-dlp...")
    text, lang, err3 = _try_ytdlp(video_id, languages)
    if text:
        print(f"[transcript] ✅ yt-dlp OK ({lang})")
        if use_cache:
            _save_cache(video_id, lang, text)
        return text, lang
    print(f"[transcript] ❌ yt-dlp: {err3}")

    return f"Error: {err} | {err2} | {err3}", None