import requests
import json

def ollama_chat(model, messages):
    """
    Envoie une requête au serveur Ollama en mode streaming et récupère
    la réponse complète sous forme de texte.

    Paramètres :
        model (str) : nom du modèle Ollama à utiliser.
        messages (list) : liste de messages au format chat (role + content).

    Retour :
        str : texte complet généré par le modèle.
    """

    # Petit affichage console pour suivre les appels effectués.
    print("\n=== OLLAMA CALL ===")
    print("Model:", model)
    print("Messages:", messages)

    # Requête HTTP vers l'API locale d'Ollama.
    # Le paramètre stream=True permet de recevoir la réponse par morceaux.
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={"model": model, "messages": messages},
        stream=True
    )

    # On va accumuler progressivement les fragments de texte renvoyés.
    full_text = ""

    # Lecture ligne par ligne du flux renvoyé par Ollama.
    for line in response.iter_lines():
        if not line:
            continue  # ignore les lignes vides

        try:
            # Chaque ligne est un petit JSON contenant un fragment de message.
            data = json.loads(line.decode("utf-8"))
        except json.JSONDecodeError:
            # Si une ligne n'est pas du JSON valide, on l'affiche pour debug.
            print("Ligne non JSON :", line)
            continue

        # Les fragments utiles se trouvent dans data["message"]["content"].
        if "message" in data and "content" in data["message"]:
            chunk = data["message"]["content"]
            full_text += chunk  # on concatène le fragment au texte complet

    print("=== FIN OLLAMA ===\n")

    # On renvoie le texte complet généré par le modèle.
    return full_text
