from src.utils.ollama_client import ollama_chat
from src.rag.query import get_context
import json

MODEL_NAME = "mistral"


def generate_scene(codex, state, user_input=None, memory="", long_memory=""):
    """
    Génère une nouvelle scène narrative en interrogeant le modèle Ollama.

    Cette fonction construit un prompt complet contenant :
    - le codex (univers, personnages, lieux…)
    - l'état narratif actuel
    - l'action du joueur
    - la mémoire courte (résumé des dernières scènes)
    - la mémoire longue (scènes anciennes pertinentes)
    - le contexte RAG (éléments du lore liés à l'action)

    Le modèle doit renvoyer un JSON strict contenant :
    - scene_text : texte narratif
    - choices : choix proposés au joueur
    - consequences : effets sur l'état narratif

    Paramètres :
        codex (dict) : informations de l'univers générées au début de l'histoire.
        state (dict) : état narratif actuel.
        user_input (str | None) : action du joueur.
        memory (str) : résumé des dernières scènes.
        long_memory (str) : contexte plus ancien retrouvé via la mémoire vectorielle.

    Retour :
        dict : scène générée, toujours sous forme de JSON.
    """

    # Affichage console utile pour le debug.
    print("State avant :", state)

    # Contexte RAG : on tente de récupérer des éléments du lore liés à l'action.
    rag_context = None
    if user_input:
        try:
            rag_context = get_context(user_input, codex.get("theme", "fantasy"))
        except Exception:
            # En cas d'erreur, on ignore simplement le RAG.
            rag_context = None

    # Construction du prompt envoyé au modèle.
    # On inclut toutes les informations nécessaires pour générer une scène cohérente.
    prompt = f"""
Tu es un moteur narratif pour un jeu interactif.
Réponds UNIQUEMENT en JSON strict, sans texte avant ou après.

RAPPELS IMPORTANTS :
- Pas de texte hors JSON.
- Pas de commentaires.
- Pas de markdown.
- Pas de variables ou expressions (PAS de (choix == "...")).
- Toutes les valeurs doivent être des valeurs JSON valides : true, false, strings, arrays, objects.
- Les champs doivent contenir directement les valeurs finales.

CONTEXTE :
Codex : {codex}
État actuel : {state}
Action du joueur : {user_input}

Résumé des événements récents :
{memory if memory else "Aucun."}

Mémoire longue pertinente :
{long_memory if long_memory else "Aucune."}

Contexte RAG :
{rag_context}

FORMAT EXACT À RESPECTER :
{{
  "scene_text": "Texte immersif ici.",
  "choices": ["choix 1", "choix 2"],
  "consequences": {{
    "milestone_progress": true,
    "flags": {{"quete_active": false}},
    "inventory_add": []
  }}
}}
"""

    # Appel au modèle via Ollama.
    raw = ollama_chat(
        MODEL_NAME,
        [
            {"role": "system", "content": "Tu es un moteur narratif expert. Réponds uniquement en JSON strict."},
            {"role": "user", "content": prompt}
        ]
    )

    # Nettoyage minimal si le modèle renvoie un bloc markdown.
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        cleaned = cleaned.replace("json", "").strip()

    # Tentative de parsing JSON.
    # Si le modèle renvoie un JSON invalide, on renvoie une scène d'erreur.
    try:
        scene = json.loads(cleaned)
    except Exception:
        print("❌ Erreur JSON dans generate_scene. Réponse brute :", raw)
        scene = {
            "scene_text": "Erreur de génération.",
            "choices": [],
            "consequences": {}
        }

    return scene
