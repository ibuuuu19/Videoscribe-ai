"""
Résumé via LLM (Groq — LLaMA 3.3 70B).
BEAUCOUP plus rapide et cohérent que BART/DistilBART.
"""

import os

try:
    from groq import Groq
except ImportError:
    Groq = None


# Modèles Groq disponibles
GROQ_MODELS = {
    "rapide":  "openai/gpt-oss-20b",           # ⚡ rapide et efficace
    "qualite": "openai/gpt-oss-120b",          # 🎓 haute qualité (remplace le 70B)
}


def _get_groq_key():
    """Récupère la clé Groq depuis les secrets Streamlit ou os.environ."""
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")


class LLMSummarizer:
    """Résumeur via Groq API (LLaMA 3.3 70B)."""

    def __init__(self, model_key="qualite"):
        if Groq is None:
            raise ImportError("groq non installé. Lance: pip install groq")

        api_key = _get_groq_key()
        if not api_key:
            raise ValueError("GROQ_API_KEY non configurée")

        self.client = Groq(api_key=api_key)
        self.model_key = model_key
        self.model = GROQ_MODELS.get(model_key, GROQ_MODELS["qualite"])
        print(f"🤖 Modèle LLM: {self.model}")

    def summarize_video(self, chunks, progress_callback=None, **kwargs):
        """Résume une liste de chunks via Groq avec fallback strict."""
        notes = []
        total = len(chunks)

        for i, chunk in enumerate(chunks):
            if not chunk:
                continue

            chunk_clean = chunk.strip()

            # ✅ Seuil bas (30 chars) pour ne pas ignorer les textes courts
            if len(chunk_clean) < 30:
                print(f"[llm] ⏭️  Chunk {i+1}/{total} ignoré (trop court : {len(chunk_clean)} chars)")
                if progress_callback:
                    try:
                        progress_callback(i + 1, total)
                    except Exception:
                        pass
                continue

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Tu es un assistant expert en synthèse de vidéos. "
                                "Tu reformules en français correct, fluide et naturel. "
                                "Tu ne recopies JAMAIS mot pour mot. "
                                "Tu supprimes les hésitations ('euh', 'bah'), les répétitions et les fautes. "
                                "RÈGLE ABSOLUE N°1 : Tu ne dois JAMAIS inventer d'informations. "
                                "RÈGLE ABSOLUE N°2 : Tu ne dois parler QUE du contenu fourni dans le texte. "
                                "RÈGLE ABSOLUE N°3 : Si le texte ne contient pas d'information claire, tu réponds EXACTEMENT : '(rien à résumer)'. "
                                "Tu ne dois JAMAIS demander de contenu supplémentaire. "
                                "Tu ne dois JAMAIS répondre par une question. "
                                "Tu réponds UNIQUEMENT avec le résumé (pas d'introduction, pas de conclusion)."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Voici un passage d'une transcription vidéo. "
                                f"Résume-le en 2-3 phrases en français correct "
                                f"(sans répétitions, sans hésitations) :\n\n{chunk_clean}"
                            ),
                        },
                    ],
                    temperature=0.0,  # ✅ Déterministe, pas d'invention
                    max_tokens=800,
                )

                note = response.choices[0].message.content.strip()  #type: ignore

                # ✅ Fallback si le LLM ne renvoie rien d'exploitable
                if not note or len(note) < 10 or note.lower() in (
                    "(rien à résumer)", "[rien à résumer]", "rien à résumer",
                    "je ne peux pas résumer", "je ne peux pas", "désolé"
                ):
                    print(f"[llm] ⚠️  Chunk {i+1}/{total} → réponse vide, fallback sur le texte original")
                    fallback = chunk_clean[:250].rsplit(' ', 1)[0] + "..."
                    notes.append(f"_{fallback}_")
                else:
                    notes.append(note)

            except Exception as e:
                print(f"[llm] ❌ Erreur chunk {i+1}: {e}")
                fallback = chunk_clean[:250].rsplit(' ', 1)[0] + "..."
                notes.append(f"_{fallback}_")

            if progress_callback:
                try:
                    progress_callback(i + 1, total)
                except Exception:
                    pass

        return notes