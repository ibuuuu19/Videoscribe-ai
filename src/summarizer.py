import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODELS = {
    "rapide":  "sshleifer/distilbart-cnn-12-6",  # ⚡ ~3-5x plus rapide, qualité proche
    "qualite": "facebook/bart-large-cnn",        # 🎓 meilleure qualité, lent sur CPU
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

    def summarize_video(self, chunks, progress_callback=None,
                        batch_size=6, num_beams=2, max_length=100):  # ← batch=6, max=100
        notes = []
        with torch.no_grad():
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                inputs = self.tokenizer(
                    batch, return_tensors="pt", truncation=True,
                    max_length=1024, padding=True,
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