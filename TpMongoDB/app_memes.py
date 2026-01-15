import streamlit as st
import pymongo
import os
from dotenv import load_dotenv
from groq import Groq
import pandas as pd

# Config de la page
st.set_page_config(page_title="Meme Studio", page_icon="🐸", layout="wide")

# Connexion
load_dotenv()
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(os.getenv("MONGO_URI"))

client = init_connection()
db = client["meme_studio"]
collection = db["memes_clean"]

# Récupération des données
memes = list(collection.find())
df = pd.DataFrame(memes)

# --- HEADER ---
st.title("🐸 Le Musée du Mème")
st.caption(f"Collection actuelle : {len(memes)} œuvres d'art numérique.")

# --- ONGLETS ---
tab1, tab2 = st.tabs(["🖼️ La Galerie", "🧐 Le Critique IA"])

# === ONGLET 1 : GALERIE VISUELLE ===
with tab1:
    # Filtres avancés
    c1, c2 = st.columns(2)
    with c1:
        # On utilise notre nouveau champ calculé "format"
        filtre_format = st.selectbox("Format d'image", ["Tout", "Carré (Insta)", "Portrait (TikTok)", "Paysage (YouTube)"])
    with c2:
        # On utilise le champ renommé "nb_zones_texte"
        nb_cases = st.slider("Nombre de zones de texte", 2, 5, 2)

    # Application des filtres sur le DataFrame
    df_filtered = df.copy()
    
    if filtre_format != "Tout":
        df_filtered = df_filtered[df_filtered['format'] == filtre_format]
        
    df_filtered = df_filtered[df_filtered['nb_zones_texte'] == nb_cases]
    
    st.subheader(f"Résultats : {len(df_filtered)} mèmes")
    
    # Affichage en grille
    cols = st.columns(3)
    for index, row in df_filtered.iterrows():
        col = cols[index % 3]
        with col:
            st.image(row['url_image'], use_container_width=True)
            st.write(f"**{row['titre']}**")
            
            # On affiche nos métadonnées enrichies
            st.caption(f"📏 {row['format']} | 📝 {row['nb_zones_texte']} textes")

# === ONGLET 2 : AGENT CRITIQUE ===
with tab2:
    st.header("🧐 Le Critique de Mèmes")
    st.markdown("Choisis une œuvre dans la base de données et soumets-la au jugement impitoyable de l'IA.")

    # 1. Préparation du menu déroulant (Titre -> URL)
    # ⚠️ CORRECTION ICI : On utilise les noms francisés du script clean ('titre' et 'url_image')
    meme_options = {row['titre']: row['url_image'] for index, row in df.iterrows()}
    
    # 2. Sélecteur
    selected_meme_titre = st.selectbox("Choisis une œuvre à critiquer :", list(meme_options.keys()))
    
    # 3. Mise en page (Image à gauche, Chat à droite)
    col_img, col_chat = st.columns([1, 2])
    
    with col_img:
        # Affichage de l'image sélectionnée
        if selected_meme_titre:
            image_url = meme_options[selected_meme_titre]
            st.image(image_url, caption=f"Œuvre : {selected_meme_titre}", use_container_width=True)
    
    with col_chat:
        st.info("💡 L'IA va analyser la pertinence culturelle de ce template.")
        
        if st.button("Lancer la critique 🎨"):
            # Initialisation du client Groq
            client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            with st.spinner("Le critique ajuste son monocle..."):
                try:
                    # Prompt amélioré pour le rôle "Critique Snob"
                    prompt = (
                        f"Tu es un critique d'art contemporain très snob et élitiste, mais spécialisé dans les 'Mèmes Internet'. "
                        f"Analyse le potentiel du template de mème intitulé : '{selected_meme_titre}'. "
                        f"Utilise un vocabulaire très soutenu et académique pour décrire ce mème (parle de 'composition', de 'juxtaposition', de 'néo-dadaisme'). "
                        f"Conclus en disant si c'est un 'Chef d'œuvre Dank' ou un 'Déchet Cringe'."
                    )
                    
                    chat_completion = client_groq.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile", # Le meilleur modèle actuel
                        temperature=0.8, # Créativité élevée pour l'humour
                    )
                    
                    # Affichage du résultat
                    response = chat_completion.choices[0].message.content
                    st.success(response)
                    
                except Exception as e:
                    st.error(f"Le critique a renversé son thé (Erreur) : {e}")