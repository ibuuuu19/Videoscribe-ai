"""
Module de résumé IA — DistilBART + BART-large.

Supporte la traduction à la volée (optionnelle) pour éviter de tout
traduire avant le résumé.

Usage:
    summarizer = VideoSummarizer(model_key="rapide")
    notes = summarizer.summarize_video(chunks, src_lang="fr", translate_first=True)
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

try:
    from src.translator import translate_texts
except ImportError:
    def translate_texts(texts, src, dest):   # ✅ Même signature exacte
        """Fallback : pas de traduction."""
        return texts
    
MODELS = {
    "rapide":  "sshleifer/distilbart-cnn-12-6",   # ⚡ ~3-5x plus rapide
    "qualite": "facebook/bart-large-cnn",          # 🎓 meilleure qualité, lent CPU
}


class VideoSummarizer:
    def __init__(self, model_name="sshleifer/distilbart-cnn-12-6", model_key="rapide"):
        self.model_key = model_key
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖥️  Device: {self.device}")

        # Utilise TOUS les cœurs du CPU
        if self.device == "cpu":
            n = os.cpu_count() or 4
            torch.set_num_threads(n)
            print(f"🧵 Threads CPU: {n}")

        print("📥 Chargement du tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        print("🧠 Chargement du modèle...")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def summarize_chunk(self, text_chunk, max_length=150, min_length=40):
        """API unitaire conservée."""
        return self.summarize_video([text_chunk], max_length=max_length)[0]

    def summarize_video(
        self,
        chunks,
        progress_callback=None,
        batch_size=6,
        num_beams=2,
        max_length=100,
        src_lang=None,
        translate_to_en=False,
    ):
        """
        Résume une liste de chunks.

        Args:
            chunks: liste de chunks (str)
            progress_callback: fn(current, total) pour la progression
            batch_size: nombre de chunks par batch
            num_beams: 1 (turbo) ou 2+ (qualité)
            max_length: longueur max du résumé
            src_lang: langue source (si traduction à la volée)
            translate_to_en: si True, traduit chaque batch avant le résumé
        """
        # Import différé pour éviter les dépendances circulaires
               # Import différé (évite les dépendances circulaires)
        # On l'importe TOUJOURS si translate_to_en, même si src_lang n'est pas encore vérifié
        
        notes = []

        with torch.no_grad():
            for i in range(0, len(chunks), batch_size):
                batch = list(chunks[i:i + batch_size])

                # ⚡ Traduction à la volée (au lieu de tout traduire avant)
                if translate_to_en and src_lang and src_lang != "en":
                    batch = translate_texts(batch, src=str(src_lang), dest="en")

                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    truncation=True,
                    max_length=1024,
                    padding=True,
                ).to(self.device)

                ids = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    min_length=20,
                    num_beams=num_beams,
                    length_penalty=1.2,
                    no_repeat_ngram_size=3,
                    early_stopping=True,
                )

                for row in ids:
                    notes.append(self.tokenizer.decode(row, skip_special_tokens=True))

                if progress_callback:
                    progress_callback(min(i + batch_size, len(chunks)), len(chunks))

        return notes