from typing import Tuple, Dict, Any

from src.engine.codex import generate_codex
from src.engine.scene import generate_scene
from src.engine.state import initial_state, update_state
from src.engine.intent_classifier import classify_intent
from src.engine.auto_continue_agent import should_auto_continue
from src.memory.vector_store import add_scene_to_memory, search_memory


# ============================================================
# MÉMOIRE NARRATIVE : résumé des dernières scènes
# ============================================================

def build_memory_summary(state: Dict[str, Any], max_scenes: int = 3) -> str:
    """
    Construit un résumé compact des dernières scènes pour donner
    une mémoire contextuelle au modèle.

    L'état contient un champ "history" qui stocke les scènes sous forme
    de dictionnaires {"scene_text": "..."}.

    Paramètres :
        state (dict) : état narratif actuel.
        max_scenes (int) : nombre de scènes récentes à inclure.

    Retour :
        str : texte concaténé des dernières scènes, séparées par des délimiteurs.
    """
    history = state.get("history", [])
    if not history:
        return ""

    # On ne garde que les X dernières scènes.
    recent = history[-max_scenes:]

    texts = []
    for entry in recent:
        # On vérifie que l'entrée est bien structurée.
        if isinstance(entry, dict) and "scene_text" in entry:
            texts.append(entry["scene_text"])

    # On sépare les scènes par un séparateur visuel.
    return "\n---\n".join(texts)


# ============================================================
# DÉMARRAGE D'UNE NOUVELLE HISTOIRE
# ============================================================

def start_story(theme: str = "fantasy") -> Dict[str, Any]:
    """
    Initialise une nouvelle histoire :
    - génère un codex narratif
    - crée l'état initial
    - génère la première scène (sans action du joueur)

    Paramètres :
        theme (str) : thème narratif choisi.

    Retour :
        dict : structure contenant le codex, l'état et la première scène.
    """

    codex = generate_codex(theme=theme)
    state = initial_state(codex)

    # On initialise l'historique interne.
    state["history"] = []

    # Première scène générée sans action du joueur.
    scene = generate_scene(
        codex=codex,
        state=state,
        user_input=None,
        memory="",
        long_memory=""
    )

    # On ajoute la première scène à l'historique interne.
    first_text = scene.get("scene_text", "")
    if first_text:
        state["history"].append({"scene_text": first_text})

    return {
        "codex": codex,
        "state": state,
        "scene": scene
    }


# ============================================================
# SCÈNE HORS-JEU
# ============================================================

def handle_out_of_game(user_input: str) -> Dict[str, Any]:
    """
    Réponse standard lorsque le joueur sort du cadre narratif
    (par exemple en posant une question hors-univers).

    Paramètres :
        user_input (str) : texte hors-jeu du joueur.

    Retour :
        dict : scène simple invitant à revenir dans l'histoire.
    """
    text = (
        "Tu sembles t'éloigner de l'aventure. "
        "Si tu veux continuer l'histoire, décris une action dans l'univers du jeu. "
        "Sinon, tu peux quitter la partie à tout moment."
    )

    return {
        "scene_text": text,
        "choices": [],
        "consequences": {}
    }


# ============================================================
# PIPELINE PRINCIPAL
# ============================================================

def next_step(
    user_input: str,
    codex: Dict[str, Any],
    state: Dict[str, Any],
    auto_depth: int = 0
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Pipeline principal exécuté à chaque action du joueur.

    Cette fonction :
    - analyse l'intention du joueur
    - récupère la mémoire courte et longue
    - génère une nouvelle scène
    - met à jour l'état narratif
    - stocke la scène dans la mémoire vectorielle
    - gère l'auto-continue si nécessaire

    Paramètres :
        user_input (str) : action du joueur.
        codex (dict) : codex narratif.
        state (dict) : état narratif actuel.
        auto_depth (int) : profondeur actuelle d'auto-continue.

    Retour :
        (scene, new_state) : la scène générée et l'état mis à jour.
    """

    # On détermine si le joueur est "dans le jeu" ou non.
    if user_input.strip() == "":
        intent = "IN_GAME"  # cas auto-continue : pas de classification
    else:
        intent = classify_intent(user_input)

    print("Intent détecté :", intent)

    # Si le joueur sort du cadre narratif, on renvoie une scène hors-jeu.
    if intent == "OUT_OF_GAME":
        scene = handle_out_of_game(user_input)
        return scene, state

    # Mémoire courte : résumé des dernières scènes.
    memory = build_memory_summary(state)
    print("Mémoire courte transmise au modèle :", memory)

    # Mémoire longue : recherche vectorielle dans les scènes passées.
    long_memory_context = ""
    if user_input.strip():
        results = search_memory(user_input, k=5)
        if results:
            parts = [r["scene_text"] for r in results]
            long_memory_context = "\n---\n".join(parts)

    print("Mémoire longue pertinente :", long_memory_context)

    # Génération de la nouvelle scène.
    scene = generate_scene(
        codex=codex,
        state=state,
        user_input=user_input,
        memory=memory,
        long_memory=long_memory_context
    )

    print("Scene générée :", scene)

    # Mise à jour de l'état narratif selon les conséquences.
    consequences = scene.get("consequences", {})
    new_state = update_state(state, consequences)
    print("Nouvel état :", new_state)

    # Ajout de la scène dans la mémoire vectorielle.
    scene_text = scene.get("scene_text", "")
    if scene_text:
        add_scene_to_memory(
            scene_text,
            metadata={
                "milestone_index": new_state.get("milestone_index"),
                "flags": new_state.get("flags", {})
            }
        )

        # Ajout dans la mémoire interne.
        if "history" not in new_state:
            new_state["history"] = []
        new_state["history"].append({"scene_text": scene_text})

    # Gestion de l'auto-continue : certaines scènes peuvent demander
    # de continuer automatiquement sans action du joueur.
    decision = should_auto_continue(scene, new_state, codex)
    print("Décision auto-continue :", decision)

    if decision == "AUTO_CONTINUE" and auto_depth < 3:
        return next_step(
            user_input="",
            codex=codex,
            state=new_state,
            auto_depth=auto_depth + 1
        )

    return scene, new_state
