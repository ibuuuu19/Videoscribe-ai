# 🎬 VideoScribe AI

> Transformez n'importe quelle vidéo YouTube en notes structurées, mots-clés, quiz et exports professionnels — en ~60 secondes.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://videoscribe-ia.streamlit.app/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Tests](https://github.com/ibuuuu19/Videoscribe-ai/actions/workflows/tests.yml/badge.svg)

## ✨ Fonctionnalités

- 🧠 **Résumé IA** — DistilBART & BART-large, ~60 s par vidéo
- 🌍 **Multilingue** — Interface et résumés en FR / EN / ES / DE
- 🔑 **Mots-clés** — Extraction intelligente et filtrage du bruit
- ❓ **Questions & Quiz** — Générateur automatique + mode interactif
- 🎴 **Flashcards Anki** — Export pour révision espacée
- 📤 **Exports** — PDF, Markdown, Obsidian, Notion, présentation HTML
- 💬 **Chat vidéo IA** — Interrogez la vidéo (Premium+)
- 👥 **Multi-utilisateurs** — Gratuit / Basique / Premium / Premium+
- 🌗 **Thème clair & sombre**

## 🚀 Démarrage rapide

### Prérequis
- Python 3.11
- pip

### Installation

```bash
git clone https://github.com/ibuuuu19/Videoscribe-ai.git
cd Videoscribe-ai

python -m venv venv
source venv/bin/activate    # Linux/Mac
# ou : venv\Scripts\activate  # Windows

pip install -r requirements.txt