def initial_state(codex):
    """
    Crée l'état initial de l'histoire à partir du codex.

    L'état narratif regroupe toutes les informations nécessaires pour suivre
    la progression du joueur : où il en est dans les objectifs, ce qu'il possède,
    les événements importants déjà rencontrés, etc.

    Paramètres :
        codex (dict) : le codex généré au début de l'histoire.

    Retour :
        dict : un dictionnaire représentant l'état initial du jeu.
    """
    return {
        # Indice du milestone en cours (permet de suivre la progression globale).
        "milestone_index": 0,

        # Drapeaux narratifs permettant de mémoriser des événements importants.
        "flags": {},

        # Inventaire du joueur (objets obtenus au fil de l'histoire).
        "inventory": [],

        # Historique interne des conséquences rencontrées.
        "history": [],

        # Description de l'univers, récupérée depuis le codex.
        "universe": codex.get("univers", "")
    }


def update_state(state, consequences):
    """
    Met à jour l'état narratif en fonction des conséquences renvoyées
    par la scène générée.

    Les conséquences peuvent modifier :
    - l'avancement dans les milestones,
    - les drapeaux narratifs,
    - l'inventaire du joueur,
    - l'historique interne.

    Paramètres :
        state (dict) : état narratif actuel.
        consequences (dict) : informations renvoyées par la scène.

    Retour :
        dict : l'état mis à jour.
    """

    # Si la scène indique une progression dans les milestones,
    # on avance d'une étape.
    if consequences.get("milestone_progress"):
        state["milestone_index"] += 1

    # Mise à jour des drapeaux narratifs.
    # Chaque flag représente un événement ou une condition persistante.
    for k, v in consequences.get("flags", {}).items():
        state["flags"][k] = v

    # Ajout d'objets dans l'inventaire.
    for item in consequences.get("inventory_add", []):
        state["inventory"].append(item)

    # Retrait d'objets de l'inventaire.
    for item in consequences.get("inventory_remove", []):
        if item in state["inventory"]:
            state["inventory"].remove(item)

    # On garde une trace des conséquences pour mémoire interne.
    state["history"].append(consequences)

    return state
