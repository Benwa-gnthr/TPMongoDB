import streamlit as st
import pymongo
import pandas as pd
import os
from dotenv import load_dotenv

# Config de la page
st.set_page_config(page_title="SpaceX Dashboard", page_icon="🚀", layout="wide")

# Connexion à la base (On utilise le cache pour ne pas reconnecter à chaque clic)
@st.cache_resource
def init_connection():
    load_dotenv()
    return pymongo.MongoClient(os.getenv("MONGO_URI"))

client = init_connection()

# Fonction pour récupérer les données PROPRES
def get_data():
    db = client["spacex_data"]
    items = list(db["lancements_clean"].find())
    return items

# --- INTERFACE ---

st.title("🚀 SpaceX Mission Control")
st.markdown("Ce dashboard visualise les données nettoyées depuis MongoDB Atlas.")

# Chargement des données
data = get_data()
df = pd.DataFrame(data)

# 1. Les KPIs (Indicateurs clés)
col1, col2, col3 = st.columns(3)
col1.metric("Total Lancements", len(df))
col2.metric("Réussites", len(df[df['success'] == True]))
col3.metric("Échecs", len(df[df['success'] == False]))

st.divider()

# 2. Filtres latéraux
status_filter = st.sidebar.selectbox("Filtrer par statut", ["Tous", "Succès", "Échec"])

if status_filter == "Succès":
    filtered_df = df[df['success'] == True]
elif status_filter == "Échec":
    filtered_df = df[df['success'] == False]
else:
    filtered_df = df

# 3. Affichage des missions (Vue "Carte")
st.subheader(f"Derniers lancements ({len(filtered_df)})")

# On affiche les missions sous forme de grille
for index, row in filtered_df.iterrows():
    with st.container():
        c1, c2 = st.columns([1, 4])
        
        with c1:
            # Affichage de l'image (Patch)
            if row['image_url']:
                st.image(row['image_url'], width=100)
            else:
                st.write("🚫 Pas d'image")
        
        with c2:
            st.write(f"### {row['mission_name']} (Vol #{row['flight_number']})")
            if row['success']:
                st.success(f"Statut : {row['status']}")
            else:
                st.error(f"Statut : {row['status']}")
            
            st.write(f"**Détails :** {row['details']}")
            if row['video_url']:
                st.markdown(f"[Voir le lancement sur YouTube]({row['video_url']})")
        
        st.divider()

# 4. Table de données brute (pour les admins)
with st.expander("Voir les données brutes"):
    st.dataframe(filtered_df)