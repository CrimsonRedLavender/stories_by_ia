import json
from src.utils.ollama_client import ollama_chat

MODEL_NAME = "mistral"


def generate_codex(theme: str = "fantasy"):
    """
    Génère un codex narratif complet en interrogeant un modèle Ollama.

    Le codex sert de base à l'univers du jeu : il définit le ton, les lieux,
    les personnages et les objectifs principaux. Le modèle doit renvoyer
    un JSON strict contenant exactement les champs attendus.

    Paramètres :
        theme (str) : thème narratif choisi (ex : fantasy, cyberpunk, enquête).

    Retour :
        dict : un codex structuré contenant les éléments essentiels de l'univers.
    """

    # Prompt envoyé au modèle. Il impose un format JSON strict et interdit
    # tout texte parasite pour éviter les erreurs de parsing.
    prompt = f"""
Tu es un générateur de Codex narratif pour un jeu d'aventure interactif.
Réponds UNIQUEMENT en JSON strict, sans texte avant ou après.

RAPPELS IMPORTANTS :
- Pas de texte hors JSON.
- Pas de markdown.
- Pas de commentaires.
- Pas de champs manquants.
- Toutes les valeurs doivent être des valeurs JSON valides.
- La langue doit être le français.
- Tu dois remplir le JSON avec du contenu original cohérent avec le thème.

Le Codex doit contenir exactement les champs suivants :
{{
  "pitch": "Résumé immersif du monde.",
  "univers": "Description du monde.",
  "personnages": ["nom1", "nom2"],
  "lieux": ["lieu1", "lieu2"],
  "milestones": ["objectif1", "objectif2", "objectif3", "objectif4"]
}}

Le thème est : "{theme}".
"""

    # Appel au modèle via Ollama.
    raw = ollama_chat(
        MODEL_NAME,
        [
            {"role": "system", "content": "Tu es un assistant expert en narration interactive. Réponds uniquement en JSON strict."},
            {"role": "user", "content": prompt}
        ]
    )

    # Nettoyage minimal de la réponse brute.
    cleaned = raw.strip()

    # Certains modèles renvoient un bloc markdown ```json ... ```
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json", "").strip()

    # Parfois, le modèle ajoute une phrase avant le JSON.
    # On cherche la première accolade ouvrante.
    if not cleaned.startswith("{"):
        idx = cleaned.find("{")
        if idx != -1:
            cleaned = cleaned[idx:]

    # Tentative de parsing JSON.
    try:
        codex = json.loads(cleaned)
    except Exception:
        print("Erreur JSON dans generate_codex. Réponse brute :", raw)
        codex = {
            "pitch": "Erreur de génération.",
            "univers": "",
            "personnages": [],
            "lieux": [],
            "milestones": []
        }

    # Vérification minimale : si un champ manque, on le remplit avec une valeur par défaut.
    for key, default in {
        "pitch": "",
        "univers": "",
        "personnages": [],
        "lieux": [],
        "milestones": []
    }.items():
        if key not in codex:
            codex[key] = default

    # On ajoute le thème pour que le reste du moteur puisse s'y référer.
    codex["theme"] = theme.lower()

    return codex
