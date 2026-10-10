"""
Module d'utilitaires — Fonctions de traitement de texte et de données.

Contient :
- Tokenisation et constantes de filtrage
- Nettoyage des résumés IA
- Extraction de mots-clés et questions
- Génération de quiz et points d'action
- Q&A sur les résumés

Extrait de app.py pour alléger le fichier principal (~170 lignes).
"""

import re
import random
from collections import Counter

import re
import random
from collections import Counter

# ⚠️ Imports optionnels : keybert et autres modules IA ne sont pas toujours installés
# (ex: en CI ou en dev sans avoir téléchargé les modèles de 400 Mo+)
try:
    from src.keywords_extractor import extract_keywords as _origKeywords
except ImportError:
    _origKeywords = None

try:
    from src.qa_generator import generate_questions as _origQuestions
except ImportError:
    _origQuestions = None

# ═══════════════════════════════════════════════════════════════
# CONSTANTES DE FILTRAGE
# ═══════════════════════════════════════════════════════════════

_BAD_KW = {"vidéo","video","outil","outils","directement","donnes","donne","veux","veulent","présenter",
"lancer","veut","voulez","pouvez","pouvez-vous","ici","là","ça","cela","ceci","chose","choses",
"truc","genre","un peu","juste","alors","donc","mais","puis","après","avant","pendant"}

_STOP = {"le","la","les","un","une","des","de","du","et","ou","a","à","est","sont","ce","cette","ces",
"que","qui","quoi","dans","sur","pour","avec","sans","ne","pas","en","au","aux","y","il","elle",
"on","nous","vous","ils","elles","mon","ma","mes","ton","ta","tes","son","sa","ses","comment",
"pourquoi","quel","quelle","quels","quelles","video","vidéo","dit","parle"}

_FILLER_RE = re.compile(r"\b(euh|hein|du coup|en fait|voilà|quoi)\b", re.I)


# ═══════════════════════════════════════════════════════════════
# TOKENISATION
# ═══════════════════════════════════════════════════════════════

def _tokenize(t):
    """Tokenise un texte en mots significatifs (sans stopwords)."""
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿñæœ0-9]+", t.lower())
    return [w for w in words if w not in _STOP and len(w) > 2]


# ═══════════════════════════════════════════════════════════════
# NETTOYAGE DES RÉSUMÉS
# ═══════════════════════════════════════════════════════════════

def clean_summary(note):
    """Nettoie un résumé IA : enlève fillers, doublons, phrases courtes."""
    sentences = re.split(r'(?<=[.!?]) +', note)
    seen_content, unique = [], []
    for s in sentences:
        s_clean = _FILLER_RE.sub("", s.strip())
        s_clean = re.sub(r"\s{2,}", " ", s_clean).strip()
        if not s_clean or len(s_clean) < 25: continue
        if "MTA AI" in s_clean and s_clean.count("MTA AI") > 1: continue
        words = set(_tokenize(s_clean))
        if any(len(words & pw) / max(len(words),1) > 0.55 for pw in seen_content): continue
        seen_content.append(words); unique.append(s_clean)
        if len(unique) >= 4: break
    result = ". ".join(unique)
    result = re.sub(r'\s*\.\.\s*', '. ', result)
    result = re.sub(r'\.\s*\.', '.', result).strip()
    if result and not result.endswith(('.', '!', '?')): result += '.'
    return result


# ═══════════════════════════════════════════════════════════════
# EXTRACTION DE MOTS-CLÉS
# ═══════════════════════════════════════════════════════════════

def better_extract_keywords(text, top_n=10, lang='fr'):
    """Extrait et filtre les mots-clés (wrapper autour de _origKeywords)."""
    if _origKeywords is None:
        raw = []
    else:
        try: raw = _origKeywords(text, top_n=top_n * 3, lang=lang)
        except Exception: raw = []
        
    filtered, seen = [], set()
    for kw, score in (raw or []):
        if not isinstance(kw, str): continue
        kw_lower = kw.lower()
        if len(kw_lower.split()) > 4 or any(b in kw_lower for b in _BAD_KW): continue
        if score < 0.30 or kw_lower in seen: continue
        seen.add(kw_lower); filtered.append((kw, round(float(score), 3)))
    if len(filtered) < 5:
        cnt = Counter(_tokenize(text))
        if cnt:
            top = cnt.most_common(1)[0][1]
            for w, c in cnt.most_common(40):
                if len(filtered) >= top_n: break
                if c >= 3 and len(w) > 3 and w not in seen:
                    seen.add(w); filtered.append((w, round(0.3 + 0.3 * c / top, 3)))
    filtered.sort(key=lambda x: -x[1]); return filtered[:top_n]


# ═══════════════════════════════════════════════════════════════
# GÉNÉRATION DE QUESTIONS
# ═══════════════════════════════════════════════════════════════

def better_generate_questions(notes, keywords=None, n=5, lang='fr'):
    """Génère des questions pertinentes (multi-langues)."""
    templates_map = {
    "fr": ["Quels sont les points principaux développés dans la section {i} ?",
    "Quelle solution ou recommandation est proposée dans la section {i} ?",
    "Quel exemple concret est mentionné dans la section {i} ?",
    "Quels avantages ou limites sont discutés dans la section {i} ?"],
    "en": ["What are the main points developed in section {i}?",
    "What solution or recommendation is proposed in section {i}?",
    "What concrete example is mentioned in section {i}?",
    "What advantages or limitations are discussed in section {i}?"],
    "es": ["¿Cuáles son los puntos principales desarrollados en la sección {i}?",
    "¿Qué solución o recomendación se propone en la sección {i}?",
    "¿Qué ejemplo concreto se menciona en la sección {i}?",
    "¿Qué ventajas o límites se discuten en la sección {i}?"],
    "de": ["Was sind die Hauptpunkte in Abschnitt {i}?",
    "Welche Lösung oder Empfehlung wird in Abschnitt {i} vorgeschlagen?",
    "Welches konkrete Beispiel wird in Abschnitt {i} erwähnt?",
    "Welche Vorteile oder Grenzen werden in Abschnitt {i} diskutiert?"]}
    general_map = {
    "fr": ["Quels sont les points principaux à retenir de cette vidéo ?",
    "Quelles solutions ou recommandations sont proposées ?",
    "Quels exemples concrets sont mentionnés ?",
    "Quels avantages et limites sont discutés ?"],
    "en": ["What are the main takeaways from this video?",
    "What solutions or recommendations are proposed?",
    "What concrete examples are mentioned?",
    "What advantages and limitations are discussed?"],
    "es": ["¿Cuáles son los puntos clave a recordar de este video?",
    "¿Qué soluciones o recomendaciones se proponen?",
    "¿Qué ejemplos concretos se mencionan?",
    "¿Qué ventajas y límites se discuten?"],
    "de": ["Was sind die wichtigsten Punkte aus diesem Video?",
    "Welche Lösungen oder Empfehlungen werden vorgeschlagen?",
    "Welche konkreten Beispiele werden erwähnt?",
    "Welche Vorteile und Grenzen werden diskutiert?"]}
    kw_map = {"fr":"Que dit la vidéo à propos de « {kw} » ?","en":"What does the video say about « {kw} »?",
    "es":"¿Qué dice el video sobre « {kw} »?","de":"Was sagt das Video über « {kw} »?"}
    templates = templates_map.get(lang, templates_map["fr"])
    general = general_map.get(lang, general_map["fr"])
    kw_template = kw_map.get(lang, kw_map["fr"])
    questions = []; seen = set()
    if keywords:
        for kw, _ in keywords[:3]:
            if kw and kw.lower() not in _BAD_KW:
                q = kw_template.format(kw=kw)
                if q not in seen: questions.append(q); seen.add(q)
    for i in range(1, min(5, len(notes)+1)):
        q = templates[(i-1) % len(templates)].format(i=i)
        if q not in seen: questions.append(q); seen.add(q)
    for q in general:
        if len(questions) >= n: break
        if q not in seen: questions.append(q); seen.add(q)
    return questions[:n]


# ═══════════════════════════════════════════════════════════════
# Q&A SUR LES RÉSUMÉS
# ═══════════════════════════════════════════════════════════════

def answer_question(question, notes):
    """Cherche une réponse dans les notes via chevauchement de mots-clés."""
    q = set(_tokenize(question))
    if not q: return "Posez une question plus précise.", []
    scored = []
    for i, note in enumerate(notes, 1):
        overlap = len(q & set(_tokenize(note)))
        if overlap: scored.append((overlap, i, note))
    scored.sort(key=lambda x: -x[0])
    if not scored: return "Je n'ai pas trouvé d'information pertinente. Reformulez.", []
    top = scored[:2]
    return " ".join(n for _,_,n in top), [i for _,i,_ in top]


# ═══════════════════════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════════════════════

def _short(x, n=90):
    """Tronque un texte proprement à la fin d'un mot."""
    x = x.strip()
    if len(x) <= n: return x
    cut = x[:n]
    return cut[:cut.rfind(" ")] + " …"


def build_quiz(data, n=4, lang='fr'):
    """Construit un quiz QCM à partir des notes."""
    QZ = {"fr":"Quelle section correspond au point {i} ?","en":"Which section corresponds to point {i}?","es":"¿Qué sección corresponde al punto {i}?","de":"Welcher Abschnitt entspricht Punkt {i}?"}
    qz = QZ.get(lang, QZ["fr"])
    rng = random.Random(data["video_id"]); notes = data["notes"]; qs = []
    pool = [x for x in notes if len(x) > 40]
    if len(pool) < 3: return []
    for i in range(min(n, len(pool))):
        correct = pool[i]
        wrongs = [x for x in pool if x != correct]
        rng.shuffle(wrongs)
        opts = {_short(correct)}
        for w in wrongs:
            opts.add(_short(w))
            if len(opts) >= 3: break
        if len(opts) < 3: continue
        choices = list(opts); rng.shuffle(choices)
        qs.append({"q": qz.format(i=i+1), "choices": choices, "answer": _short(correct)})
    return qs


# ═══════════════════════════════════════════════════════════════
# POINTS D'ACTION
# ═══════════════════════════════════════════════════════════════

def better_extract_action_points(notes):
    """Extrait les points d'action (verbes d'action + suggestions)."""
    actions = []
    action_words = ["utiliser","connecter","installer","télécharger","configurer",
    "générer","ajouter","créer","tester","essayer","reproduire"]
    for note in notes:
        note_lower = note.lower()
        for word in action_words:
            if word in note_lower:
                sentences = re.split(r'[.!?]', note)
                for sent in sentences:
                    if word in sent.lower() and len(sent.strip()) > 20:
                        action = sent.strip().capitalize()
                        if not action.endswith(('.', '!', '?')): action += '.'
                        if action not in actions: actions.append(action)
                        break
        if len(actions) >= 5: break
    if len(actions) < 3:
        for note in notes[:3]:
            if len(note) > 50:
                action = note.split('.')[0].strip()
                if action and action not in actions: actions.append(action + '.')
    return actions[:5]