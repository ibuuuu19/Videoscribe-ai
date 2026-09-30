from src.transcript_extractor import extract_video_id, get_transcript
from src.text_processor import chunk_text, format_notes
from src.summarizer import VideoSummarizer
from datetime import datetime
import os

def generate_video_notes(video_url, output_dir="output/summaries"):
    """Pipeline complet de résumé de vidéo YouTube."""
    
    print(f"\n🎬 Traitement de la vidéo: {video_url}\n")
    
    # 1. Extraire l'ID vidéo
    video_id = extract_video_id(video_url)
    if not video_id:
        print("❌ URL YouTube invalide.")
        return None
    
    # 2. Récupérer les sous-titres
    print("🎧 Récupération des sous-titres...")
    transcript = get_transcript(video_id)
    
    if transcript.startswith("Error"):
        print(f"❌ {transcript}")
        return None
    
    print(f"✅ Transcript récupéré: {len(transcript)} caractères\n")
    
    # 3. Découper en chunks
    print("🔪 Découpage du texte en chunks...")
    chunks = chunk_text(transcript, chunk_size=1200)
    print(f"✅ {len(chunks)} chunks créés\n")
    
    # 4. Initialiser le modèle (une seule fois)
    if not hasattr(generate_video_notes, "summarizer"):
        generate_video_notes.summarizer = VideoSummarizer()
    
    # 5. Générer les résumés
    print("🧠 Génération des résumés...\n")
    notes = generate_video_notes.summarizer.summarize_video(chunks)
    
    # 6. Formater et sauvegarder
    formatted_notes = format_notes(notes)
    
    print("\n" + "=" * 50)
    print(formatted_notes)
    print("=" * 50)
    
    # Sauvegarder dans un fichier
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"summary_{video_id}_{timestamp}.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Vidéo: {video_url}\n")
        f.write(f"ID: {video_id}\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write(f"Nombre de chunks: {len(chunks)}\n\n")
        f.write(formatted_notes)
    
    print(f"\n💾 Résumé sauvegardé: {output_file}")
    
    return formatted_notes

if __name__ == "__main__":
    print("=" * 50)
    print("🎥 AI YouTube Video Summarizer")
    print("=" * 50)
    
    url = input("\n📎 Colle l'URL YouTube: ").strip()
    
    if url:
        generate_video_notes(url)
    else:
        print("❌ Aucune URL fournie.")