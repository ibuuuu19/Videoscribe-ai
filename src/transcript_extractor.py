import re
import json
import os
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def extract_video_id(url):
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

def get_transcript(video_id, languages=None, use_cache=True):
    """Récupère les sous-titres avec cache local."""
    if languages is None:
        languages = ['fr', 'en', 'es', 'de', 'it', 'pt']
    
    # Chercher dans le cache d'abord
    if use_cache:
        for lang in languages + ['auto']:
            cache_file = _cache_path(video_id, lang)
            if cache_file.exists():
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"💾 Transcript chargé depuis le cache ({data['lang']})")
                        return data['text'], data['lang']
                except Exception:
                    pass
    
    api = YouTubeTranscriptApi()
    
    try:
        # Essayer les langues préférées
        for lang in languages:
            try:
                transcript = api.fetch(video_id, languages=[lang])
                text = " ".join([t.text for t in transcript])
                
                if use_cache:
                    with open(_cache_path(video_id, lang), 'w', encoding='utf-8') as f:
                        json.dump({'text': text, 'lang': lang}, f, ensure_ascii=False)
                
                return text, lang
            except NoTranscriptFound:
                continue
        
        # Fallback : première langue disponible
        transcript_list = api.list_transcripts(video_id)
        for transcript in transcript_list:
            fetched = transcript.fetch()
            text = " ".join([t.text for t in fetched])
            lang = transcript.language_code
            
            if use_cache:
                with open(_cache_path(video_id, lang), 'w', encoding='utf-8') as f:
                    json.dump({'text': text, 'lang': lang}, f, ensure_ascii=False)
            
            print(f"ℹ️  Sous-titres trouvés en: {transcript.language}")
            return text, lang
    
    except TranscriptsDisabled:
        return "Error: Sous-titres désactivés.", None
    except Exception as e:
        return f"Error: {str(e)}", None