from src.utils.ollama_client import ollama_chat

# Modèle utilisé pour décider si l'histoire doit avancer automatiquement.
MODEL_NAME = "mistral"


def should_auto_continue(scene: dict, state: dict, codex: dict) -> str:
    """
    Détermine si l'histoire doit avancer automatiquement ou attendre
    une action du joueur.

    Le modèle reçoit la scène actuelle, l'état narratif et le codex,
    puis applique quelques règles simples :

    - S'il existe des choix proposés au joueur → WAIT_FOR_PLAYER
    - S'il n'y a aucun choix → AUTO_CONTINUE
    - Si la scène ressemble à une transition narrative (ex : description,
      déplacement, changement de lieu) → AUTO_CONTINUE
    - Si la scène demande explicitement une action → WAIT_FOR_PLAYER

    Paramètres :
        scene (dict) : scène générée par le moteur narratif.
        state (dict) : état narratif actuel.
        codex (dict) : informations de l'univers.

    Retour :
        str : "AUTO_CONTINUE" ou "WAIT_FOR_PLAYER"
    """

    # Prompt envoyé au modèle. Il décrit clairement les règles de décision.
    prompt = f"""
    Tu es un agent de décision pour un jeu narratif. La langue à utiliser est le français.

    Ta tâche : déterminer si l'histoire doit continuer automatiquement
    ou si on doit attendre une action du joueur.

    Règles :
    - S'il y a des choix → WAIT_FOR_PLAYER
    - S'il n'y a aucun choix → AUTO_CONTINUE
    - Si la scène est une transition narrative → AUTO_CONTINUE
    - Si la scène demande explicitement une action → WAIT_FOR_PLAYER

    Données :
    Scène : {scene}
    État : {state}
    Codex : {codex}

    Réponds uniquement par :
    AUTO_CONTINUE
    ou
    WAIT_FOR_PLAYER
    """

    # Appel au modèle via Ollama.
    raw = ollama_chat(
        MODEL_NAME,
        [
            {"role": "system", "content": "Tu es un agent de décision narratif."},
            {"role": "user", "content": prompt}
        ]
    )

    # On nettoie la réponse et on la met en majuscules pour simplifier la détection.
    answer = raw.strip().upper()

    # Si la réponse contient AUTO_CONTINUE, on choisit cette option.
    if "AUTO_CONTINUE" in answer:
        return "AUTO_CONTINUE"

    # Sinon, par défaut, on attend une action du joueur.
    return "WAIT_FOR_PLAYER"
