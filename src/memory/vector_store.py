from typing import Dict, Any, List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

# Initialisation du modèle d'embedding utilisé pour convertir les textes
# en vecteurs numériques. Ce modèle est léger et fonctionne en local.
_embeddings = FastEmbedEmbeddings()

# Le vectorstore est stocké dans une variable globale.
# Il sera créé à la première utilisation, puis réutilisé.
_vectorstore = None


def get_vectorstore():
    """
    Retourne l'instance globale du vectorstore FAISS.
    Si elle n'existe pas encore, la fonction en crée une nouvelle.

    Le vectorstore est initialisé avec un texte neutre pour éviter
    d'avoir une base vide, ce qui simplifie les appels suivants.
    """
    global _vectorstore
    if _vectorstore is None:
        # Création d'un vectorstore minimal contenant un seul document.
        _vectorstore = FAISS.from_texts(["Mémoire initiale."], _embeddings)
    return _vectorstore


def add_scene_to_memory(scene_text: str, metadata: Dict[str, Any]):
    """
    Ajoute une scène dans la mémoire vectorielle.

    Paramètres :
        scene_text (str) : texte de la scène à mémoriser.
        metadata (dict) : informations associées à la scène
                          (milestone, flags, etc.).

    Le texte est converti en vecteur puis ajouté à la base FAISS.
    """
    vs = get_vectorstore()
    vs.add_texts([scene_text], metadatas=[metadata])


def search_memory(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Recherche les scènes les plus proches du texte fourni.

    Paramètres :
        query (str) : texte de la requête (souvent l'action du joueur).
        k (int) : nombre maximum de résultats à renvoyer.

    Retour :
        list[dict] : liste de résultats, chaque entrée contenant :
            - "scene_text" : le texte mémorisé
            - "metadata" : les informations associées à cette scène

    Cette fonction permet au moteur narratif de retrouver des scènes
    passées similaires, afin d'assurer une continuité logique.
    """
    vs = get_vectorstore()

    # Recherche vectorielle : FAISS renvoie les documents les plus proches.
    docs = vs.similarity_search(query, k=k)

    results: List[Dict[str, Any]] = []
    for doc in docs:
        results.append({
            "scene_text": doc.page_content,
            "metadata": doc.metadata
        })

    return results
