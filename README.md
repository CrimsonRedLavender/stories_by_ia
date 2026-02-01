# Stories by AI

**Stories by AI** est un moteur de jeu narratif interactif propulsé par l'intelligence artificielle. Le joueur décrit ses actions, et l'IA génère dynamiquement un univers cohérent, persistant et riche en détails.

## Présentation
Le moteur ne se contente pas de répondre à l'utilisateur ; il construit une expérience immersive grâce à :
* **Scènes immersives** : Génération dynamique de descriptions textuelles riches.
* **Choix interactifs** : Propositions d'actions adaptées au contexte immédiat.
* **Conséquences persistantes** : Chaque action impacte durablement l'état du monde.
* **Univers cohérent** : Basé sur un codex généré automatiquement en début de partie.
* **Mémoire hybride** : 
    * *Mémoire courte* : Résumé des dernières interactions pour la fluidité.
    * *Mémoire longue (Vectorielle)* : Récupération des scènes passées via **FAISS**.
* **Contexte RAG** : Injection de lore spécifique via des fichiers JSON thématiques.

Le projet fonctionne **100% en local** via **Ollama** (modèle Mistral) et une interface **Streamlit**.

---

## Fonctionnement général
Le moteur suit un pipeline structuré pour garantir la cohérence narrative :

1.  **Codex** : Génération de l'univers (pitch, lieux, personnages, milestones).
2.  **État narratif** : Suivi de la progression, des flags, de l'inventaire et de l'historique.
3.  **Mémoire courte** : Résumé des dernières scènes pour maintenir la cohérence immédiate.
4.  **Mémoire longue vectorielle** : Recherche FAISS pour retrouver des scènes anciennes pertinentes.
5.  **RAG JSON** : Recherche d’éléments du lore liés à l’action du joueur.
6.  **Génération de scène** : Le modèle renvoie un JSON strict :
    ```json
    {
      "scene_text": "...",
      "choices": ["..."],
      "consequences": { "inventory_add": "..." }
    }
    ```
7.  **Auto-continue** : Progression automatique si aucun choix n'est proposé.

---

## Architecture du projet

```text
src/
│
├── engine/
│   ├── codex.py               # Génération du codex narratif
│   ├── scene.py               # Génération des scènes
│   ├── state.py               # Gestion de l'état narratif
│   ├── orchestrator.py        # Pipeline principal du jeu
│   ├── intent_classifier.py   # Détection IN_GAME / OUT_OF_GAME
│   ├── auto_continue_agent.py # Décision d'avancer automatiquement
│
├── rag/
│   ├── data/                  # Fichiers JSON du lore
│   ├── loader.py              # Chargement du RAG
│   ├── query.py               # Recherche d’éléments pertinents
│
├── memory/
│   ├── vector_store.py        # Mémoire longue FAISS
│
├── utils/
│   ├── ollama_client.py       # Client HTTP pour Ollama
│
app.py                         # Interface Streamlit
```
## Moteur Narratif IA

Un moteur de jeu textuel propulsé par l'IA, utilisant Mistral via Ollama, avec mémoire vectorielle et RAG.

---

## Installation

### 1. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 2. Installer Ollama

Téléchargez l'outil sur le site officiel : [https://ollama.com/](https://ollama.com/)

### 3. Installer le modèle Mistral

Ouvrez votre terminal et lancez :
```bash
ollama pull mistral
```

### 4. Lancer l'application
```bash
streamlit run app.py
```

---

## Fichiers RAG

Les fichiers JSON dans `src/rag/data/` servent de base de connaissances au moteur. Ils doivent suivre cette structure :
```json
[
  {
    "theme": "fantasy",
    "name": "Forêt d'Émeraude",
    "description": "Une forêt ancienne où les arbres murmurent des secrets oubliés.",
    "keywords": ["forêt", "arbres", "elfes", "magie"]
  }
]
```

Chaque fichier représente une catégorie (lieux, personnages, objets, bestiaire).

---

## Mémoire longue

Le projet utilise **FAISS** pour vectoriser et stocker les scènes passées afin que l'IA s'en rappelle plus tard.

- **Stockage** : Chaque scène est convertie en vecteur via `add_scene_to_memory(scene_text, metadata)`.
- **Récupération** : Le moteur effectue une recherche de similarité via `search_memory(query)` avant chaque génération de scène.

---

## Exemple de flux narratif

1. **Action** : Le joueur écrit : *"J'examine la porte en pierre."*

2. **Recherche** : Le moteur cherche dans le RAG (infos sur la porte) et dans la mémoire longue (est-ce que la porte était verrouillée avant ?).

3. **Synthèse** : Il combine les faits, le résumé des dernières scènes et le codex dans un prompt unique.

4. **Génération** : Mistral renvoie une réponse structurée affichée dans Streamlit.

---

# Schéma du Pipeline Narratif

Ce schéma illustre le fonctionnement interne complet du moteur narratif de Stories by AI. Il montre comment chaque module interagit pour produire une scène cohérente, mémoriser les événements et maintenir la continuité de l'histoire.

---

## Flux d'exécution
```
┌──────────────────────────────────────────────────────────────┐
│                        DÉMARRAGE DU JEU                      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │  generate_codex()    │  ← Génère l'univers
                    └──────────────────────┘     (pitch, lieux,
                              │                   personnages,
                              ▼                   milestones)
                    ┌──────────────────────┐
                    │  initial_state()     │  ← Initialise l'état
                    └──────────────────────┘     narratif
                              │
                              ▼
                    ┌──────────────────────┐
                    │  generate_scene()    │  ← Première scène
                    └──────────────────────┘     (sans input)
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                     BOUCLE DE JEU (next_step)                │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ classify_intent()    │  ← IN_GAME /
                    └──────────────────────┘     OUT_OF_GAME
                              │
                              ▼
                    ┌──────────────────────┐
                    │build_memory_summary()│
                    └──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ search_memory()      │  ← Recherche FAISS
                    └──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ get_context()        │  ← Récupération RAG
                    └──────────────────────┘     (fichiers JSON)
                              │
                              ▼
                    ┌──────────────────────┐
                    │ generate_scene()     │  ← Génération IA
                    └──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │ update_state()       │  ← Mise à jour
                    └──────────────────────┘     (flags, inventaire,
                              │                   milestones)
                              ▼
                    ┌──────────────────────┐
                    │add_scene_to_memory() │  ← Stockage FAISS
                    └──────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │should_auto_continue? │  ← Décision AUTO /
                    └──────────────────────┘     WAIT
                              │
                              ▼
                  ┌───────────────────────┐
                  │   AUTO_CONTINUE ?     │
                  └───────────────────────┘
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
            (Oui) Boucle          (Non) Attente
            next_step()           d'action joueur
```

---

## Détail des composants

### Phase d'initialisation
- **`generate_codex()`** : Génère l'univers complet (pitch, lieux, personnages, milestones)
- **`initial_state()`** : Initialise l'état narratif du jeu
- **`generate_scene()`** : Crée la première scène sans input joueur

### Boucle de jeu principale
1. **`classify_intent()`** : Détermine si l'action est IN_GAME ou OUT_OF_GAME
2. **`build_memory_summary()`** : Construit un résumé des événements récents
3. **`search_memory()`** : Recherche de similarité dans FAISS
4. **`get_context()`** : Récupère les données pertinentes depuis les fichiers RAG JSON
5. **`generate_scene()`** : Génère la nouvelle scène avec l'IA
6. **`update_state()`** : Met à jour les flags, l'inventaire et les milestones
7. **`add_scene_to_memory()`** : Stocke la scène dans la mémoire vectorielle FAISS
8. **`should_auto_continue()`** : Décide si la narration continue automatiquement ou attend le joueur

---

## Développement

Le code est conçu pour être modulaire :

- **Thèmes** : Ajoutez de nouveaux fichiers JSON pour changer d'univers.
- **Modèles** : Vous pouvez tester d'autres modèles Ollama (Llama3, Gemma) en modifiant le client.
- **Mécaniques** : Le fichier `state.py` permet d'ajouter un système d'inventaire ou de statistiques (PV, Mana, etc.).

---


# Améliorations possibles & limites actuelles

Même si le moteur fonctionne, il peut être largement amélioré pour renforcer la qualité narrative, la fluidité, la cohérence et la rapidité de l'expérience.

---

## Qualité de génération & cohérence narrative

### Traduction parfois approximative
Le modèle peut produire des formulations maladroites ou des tournures anglaises mal traduites.

### Répétitions ou boucles narratives
Certaines scènes tournent en rond, répètent des informations ou n'avancent pas suffisamment l'histoire.

### Progression narrative parfois lente
Le modèle peut s'attarder sur des descriptions ou ignorer les milestones, ce qui ralentit l'avancée de l'intrigue.

### Incohérences entre scènes
Malgré la mémoire courte et longue, il peut arriver que des détails changent ou soient oubliés.

---

## Performance & temps de génération

### Temps de génération parfois long
Selon la scène et le contexte, le modèle peut mettre plusieurs secondes à répondre.

### Auto-continue perfectible
Certaines scènes devraient avancer automatiquement mais nécessitent encore une action manuelle.

### Gestion du contexte perfectible
Le RAG JSON et la mémoire vectorielle peuvent être enrichis pour éviter les pertes de cohérence.

---

## Fonctionnalités multimédia

### Text-to-Speech
Possibilité d'ajouter une lecture audio des scènes (pyttsx3, Coqui TTS, etc.).

### Génération d'images
Intégration possible d'un générateur d'illustrations pour les scènes, lieux ou personnages.

---

## Intelligence narrative

### Meilleure gestion des choix
Certains choix sont trop vagues ou trop similaires ; un système de génération plus contrôlé pourrait améliorer la variété.

### Système de quêtes plus structuré
Les milestones pourraient être transformés en véritables arcs narratifs avec états, sous-objectifs et résolutions.

### Personnalités des personnages
Possibilité d'ajouter des fiches de personnages plus détaillées pour renforcer leur cohérence.

### Gestion des émotions et du ton
Le moteur pourrait adapter le style narratif selon les événements (tension, humour, mystère…).

---

## RAG & mémoire

### RAG JSON plus riche
Ajouter davantage de fichiers thématiques pour augmenter la variété du lore.

### Mémoire longue plus intelligente
Filtrer les scènes pertinentes selon le type d'action (combat, exploration, dialogue…).

### Résumé dynamique amélioré
Le résumé des dernières scènes pourrait être plus synthétique et mieux structuré.

---

## Interface utilisateur

### Mode "lecture automatique"
Avancer automatiquement tant qu'il n'y a pas de choix.

### Mode "résumé rapide"
Afficher un résumé de l'histoire jusqu'ici.

### Mode "debug narratif"
Afficher les prompts envoyés au modèle pour comprendre les décisions.

### Surlignage des éléments importants
Personnages, lieux, objets, indices…

---

## Robustesse & stabilité

### Meilleure gestion des erreurs JSON
Le moteur pourrait corriger automatiquement les erreurs mineures (virgules manquantes, guillemets oubliés…).

### Fallback en cas d'échec de génération
Si le modèle renvoie un JSON invalide, proposer une régénération automatique.

---

# Licence

Projet personnel — libre d'utilisation et de modification.
