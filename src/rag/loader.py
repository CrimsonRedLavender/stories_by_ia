import json
import os

# Dossier où se trouvent les fichiers JSON contenant les données du RAG.
DATA_DIR = "src/rag/data"


def load_rag(theme: str):
    """
    Charge les données du RAG (lore, personnages, lieux, objets, etc.)
    en fonction d'un thème donné.

    Le RAG est organisé sous forme de plusieurs fichiers JSON,
    chacun représentant une catégorie (par exemple : personnages.json, lieux.json).

    Paramètres :
        theme (str) : thème narratif choisi par le joueur.
                      Seules les entrées correspondant à ce thème seront chargées.

    Retour :
        dict : un dictionnaire où chaque clé est une catégorie
               et chaque valeur est une liste d'entrées filtrées par thème.
    """

    rag = {}

    # On parcourt tous les fichiers du dossier RAG.
    for filename in os.listdir(DATA_DIR):
        # On ignore tout ce qui n'est pas un fichier JSON.
        if not filename.endswith(".json"):
            continue

        path = os.path.join(DATA_DIR, filename)

        # Lecture du fichier JSON.
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)

        # On garde uniquement les entrées correspondant au thème demandé.
        filtered = [e for e in entries if e.get("theme") == theme.lower()]

        # Le nom de la catégorie correspond au nom du fichier sans l'extension.
        category = filename.replace(".json", "")
        rag[category] = filtered

    # On renvoie l'ensemble des catégories filtrées.
    return rag
