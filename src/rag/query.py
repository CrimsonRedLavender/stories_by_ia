from src.rag.loader import load_rag
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    """
    Calcule une similarité approximative entre deux chaînes de caractères.
    On utilise SequenceMatcher, qui renvoie un score entre 0 et 1.
    Plus le score est élevé, plus les deux chaînes se ressemblent.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def get_context(user_input: str, theme: str, max_results=5):
    """
    Recherche dans le RAG les éléments les plus pertinents par rapport
    à l'action du joueur. Le but est de fournir au moteur narratif un
    contexte utile (lieux, personnages, objets, etc.) lié à l'univers.

    Paramètres :
        user_input (str) : texte saisi par le joueur.
        theme (str) : thème narratif utilisé pour charger le bon RAG.
        max_results (int) : nombre maximum d'éléments pertinents à renvoyer.

    Retour :
        str : un texte formaté contenant les éléments du RAG les plus pertinents.
    """

    # On charge le RAG correspondant au thème choisi.
    rag = load_rag(theme)
    input_lower = user_input.lower()
    results = []

    # On parcourt toutes les catégories du RAG (personnages, lieux, objets, etc.).
    for category, entries in rag.items():
        # Le champ "theme" n'est pas un élément de contenu, on l'ignore.
        if category == "theme":
            continue

        # Chaque entrée représente un élément du lore.
        for entry in entries:
            score = 0  # score de pertinence pour cette entrée

            # 1. Vérification des mots-clés exacts.
            for kw in entry.get("keywords", []):
                if kw.lower() in input_lower:
                    score += 3

            # 2. Similarité approximative sur les mots-clés.
            for kw in entry.get("keywords", []):
                sim = similarity(kw, input_lower)
                if sim > 0.6:
                    score += int(sim * 2)

            # 3. Matching sur le nom ou le titre de l'entrée.
            name = entry.get("name") or entry.get("title")
            if name:
                if name.lower() in input_lower:
                    score += 4
                else:
                    sim = similarity(name, user_input)
                    if sim > 0.6:
                        score += int(sim * 3)

            # 4. Matching léger sur la description.
            desc = entry.get("description") or entry.get("text")
            if desc:
                # On regarde si un mot de l'entrée utilisateur apparaît dans la description.
                if any(word in desc.lower() for word in input_lower.split()):
                    score += 1

            # Si l'entrée a obtenu un score positif, on la garde.
            if score > 0:
                results.append((score, category, entry))

    # On trie les résultats par score décroissant.
    results.sort(key=lambda x: x[0], reverse=True)

    # On garde uniquement les meilleurs résultats.
    selected = results[:max_results]

    # On construit un texte lisible pour le moteur narratif.
    context = ""
    for score, category, entry in selected:
        name = entry.get("name") or entry.get("title")
        desc = entry.get("description") or entry.get("text")
        context += f"[{category.upper()}] {name} : {desc}\n"

    # Si rien n'est pertinent, on renvoie un message neutre.
    return context if context else "Aucun contexte pertinent trouvé."
