def generate_questions(notes, keywords=None, n=5):
    questions = []
    if keywords:
        for kw, _ in keywords[:3]:
            questions.append(f"Que dit la vidéo à propos de « {kw} » ?")
    general = [
        "Quels sont les points principaux à retenir de cette vidéo ?",
        "Quelles solutions ou recommandations sont proposées ?",
        "Quels exemples concrets illustrent le propos ?",
        "Quelles sont les conséquences ou implications évoquées ?",
        "Quel est le message central de la vidéo ?",
    ]
    for g in general:
        if len(questions) >= n:
            break
        questions.append(g)
    return questions[:n]
