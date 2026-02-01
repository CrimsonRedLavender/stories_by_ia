from src.utils.ollama_client import ollama_chat

# Modèle utilisé pour la classification d'intention.
MODEL_NAME = "mistral"


def classify_intent(user_input: str) -> str:
    """
    Détermine si l'action du joueur appartient à l'univers du jeu
    ou si elle en sort complètement.

    Le modèle suit un format ReAct très simple :
    - il réfléchit (Thought)
    - il applique une action "classify"
    - il donne une réponse finale : IN_GAME ou OUT_OF_GAME

    Paramètres :
        user_input (str) : texte saisi par le joueur.

    Retour :
        str : "IN_GAME" ou "OUT_OF_GAME"
    """

    # Prompt envoyé au modèle. Il décrit clairement les deux catégories
    # et impose un format ReAct pour encourager une réponse structurée.
    prompt = f"""
    Tu es un agent ReAct chargé de classifier l'intention du joueur.

    IN_GAME = action dans l'univers du jeu
    OUT_OF_GAME = question hors jeu, recette, info réelle, etc.

    Format ReAct :
    Thought:
    Action: classify
    Observation:
    Final Answer: IN_GAME ou OUT_OF_GAME

    Message du joueur :
    "{user_input}"
    """

    # Appel au modèle via Ollama.
    raw = ollama_chat(
        MODEL_NAME,
        [
            {"role": "system", "content": "Tu es un agent ReAct expert."},
            {"role": "user", "content": prompt}
        ]
    )

    # On récupère la dernière ligne de la réponse,
    # qui contient normalement "IN_GAME" ou "OUT_OF_GAME".
    last_line = raw.strip().split("\n")[-1].upper()

    # Si la ligne contient OUT_OF_GAME, on renvoie cette catégorie.
    if "OUT_OF_GAME" in last_line:
        return "OUT_OF_GAME"

    # Sinon, par défaut, on considère que l'action est dans le jeu.
    return "IN_GAME"
