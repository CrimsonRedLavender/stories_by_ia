import streamlit as st

from src.engine.orchestrator import start_story, next_step
from src.engine.auto_continue_agent import should_auto_continue

# Configuration générale de la page Streamlit.
# On définit le titre, l’icône et la mise en page.
st.set_page_config(page_title="Stories by AI", page_icon="📘", layout="wide")

# Initialisation des différentes variables stockées dans la session.
# Elles permettent de conserver l'état du jeu entre les interactions.
if "codex" not in st.session_state:
    st.session_state.codex = None

if "state" not in st.session_state:
    st.session_state.state = None

if "scene" not in st.session_state:
    st.session_state.scene = None

if "theme" not in st.session_state:
    st.session_state.theme = "Fantasy"

if "history" not in st.session_state:
    st.session_state.history = []


def start_new_game():
    """
    Lance une nouvelle histoire.
    Cette fonction demande au moteur narratif de créer un codex, un état initial
    et une première scène. Elle réinitialise aussi l'historique affiché dans l'interface.
    """
    data = start_story(theme=st.session_state.theme)
    st.session_state.codex = data["codex"]
    st.session_state.state = data["state"]
    st.session_state.scene = data["scene"]

    # On remet l'historique à zéro et on ajoute la première scène.
    st.session_state.history = []
    st.session_state.history.append({"scene_text": data["scene"]["scene_text"]})


def process_input(user_input):
    """
    Traite une action du joueur.
    Cette fonction envoie l'action au moteur narratif, récupère la scène suivante,
    met à jour l'état interne et ajoute la scène à l'historique.
    """
    new_scene, new_state = next_step(
        user_input=user_input,
        codex=st.session_state.codex,
        state=st.session_state.state
    )

    # Mise à jour de la scène et de l'état narratif.
    st.session_state.scene = new_scene
    st.session_state.state = new_state

    # On ajoute la scène générée à l'historique affiché dans l'interface.
    entry = {"scene_text": new_scene.get("scene_text", "Scène introuvable.")}
    st.session_state.history.append(entry)

    # On ajoute aussi la scène dans l'historique interne du moteur.
    if "history" not in st.session_state.state:
        st.session_state.state["history"] = []
    st.session_state.state["history"].append(entry)

    # On relance l'application pour rafraîchir l'affichage.
    st.rerun()


# --- Interface utilisateur (UI) ---

with st.sidebar:
    # Titre principal dans la barre latérale.
    st.title("Stories by AI")

    # Choix du thème avant de démarrer une histoire.
    st.subheader("Thème de l'histoire")
    st.session_state.theme = st.selectbox(
        "Choisis un univers :",
        [
            "Fantasy",
        ],
        index=0
    )

    # Bouton pour démarrer une nouvelle histoire.
    if st.button("🔄 Nouvelle histoire"):
        start_new_game()
        st.rerun()

    st.markdown("---")

    # Affichage du codex généré par le moteur narratif.
    st.subheader("Codex (univers)")
    if st.session_state.codex:
        st.json(st.session_state.codex)

    st.markdown("---")

    # Affichage de l'état narratif interne.
    st.subheader("État narratif")
    if st.session_state.state:
        st.json(st.session_state.state)

    st.markdown("---")

    # Historique complet des scènes déjà jouées.
    st.subheader("Historique des scènes")
    with st.expander("Voir l'historique"):
        for i, entry in enumerate(st.session_state.history):
            st.markdown(f"**Scène {i + 1}**")
            st.write(entry["scene_text"])
            st.markdown("---")

    # Export de l'histoire sous forme de fichier texte.
    if st.session_state.history:
        def build_history_text():
            """
            Construit une version texte de l'historique complet,
            utilisée pour l'export en fichier.
            """
            lines = []
            for i, entry in enumerate(st.session_state.history):
                lines.append(f"--- Scène {i + 1} ---\n{entry['scene_text']}\n")
            return "\n".join(lines)

        history_text = build_history_text()

        st.download_button(
            label="Télécharger l'histoire",
            data=history_text,
            file_name="histoire_codex.txt",
            mime="text/plain"
        )


# Si aucune histoire n'a été lancée, on invite l'utilisateur à en créer une.
if st.session_state.codex is None:
    st.info("Clique sur *Nouvelle histoire* dans la barre latérale pour commencer.")
    st.stop()

# On récupère la scène actuelle pour l'afficher.
scene = st.session_state.scene

# Vérifier si la scène doit auto-continuer
state = st.session_state.state
codex = st.session_state.codex

if isinstance(scene, dict) and isinstance(state, dict) and isinstance(codex, dict):
    decision = should_auto_continue(scene, state, codex)
    if decision == "AUTO_CONTINUE":
        process_input("")
        st.stop()

# Affichage de la scène en cours dans un bloc visuel.
st.subheader("Scène actuelle")

st.markdown(
    f"""
    <div style="
        padding: 1.2rem;
        background-color: #1e1e1e;
        border-radius: 8px;
        border: 1px solid #444;
        color: #f0f0f0;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    ">
        {scene["scene_text"]}
    </div>
    """,
    unsafe_allow_html=True
)

# Section des actions possibles.
st.subheader("🎮 Actions possibles")

choices = scene.get("choices", [])

# Si la scène propose des choix prédéfinis, on les affiche sous forme de boutons.
if choices:
    st.write("Choix proposés :")
    cols = st.columns(2)
    for i, c in enumerate(choices):
        if cols[i % 2].button(c):
            process_input(c)

# Champ texte libre pour les actions personnalisées du joueur.
user_input = st.text_input(
    "Ou décris ton action : (effacer manuellement le champ après chaque envoi)",
    key="user_input"
)

# Bouton pour envoyer l'action personnalisée.
if st.button("Envoyer"):
    user_input_value = st.session_state.user_input

    # On vérifie que l'utilisateur a bien écrit quelque chose.
    if user_input_value.strip() == "":
        st.warning("Entre une action pour continuer.")
        st.stop()

    # On transmet l'action au moteur narratif.
    process_input(user_input_value)

    # On vide le champ après l'envoi.
    st.session_state.user_input = ""

    st.rerun()
