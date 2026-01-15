import streamlit as st
import pymongo
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from bson.objectid import ObjectIdxl

st.set_page_config(page_title="Crypto Manager", page_icon="🏦", layout="wide")

# CONNEXION MONGODB
@st.cache_resource
def init_connection():
    load_dotenv()
    return pymongo.MongoClient(os.getenv("MONGO_URI"))

client = init_connection()
db = client["crypto_data"]
collection = db["market_cap_clean"]

# FONCTIONS CRUD

def get_data():
    """READ: Récupère tout"""
    items = list(collection.find())
    for item in items:
        item['_id'] = str(item['_id'])
    return items

def create_crypto(nom, symbole, prix, categorie):
    """CREATE: Ajoute une nouvelle crypto"""
    nouvelle_crypto = {
        "nom": nom,
        "symbole": symbole.upper(),
        "prix_usd": prix,
        "variation_24h": 0, 
        "tendance": "🆕 Nouveau",
        "categorie": categorie,
        "market_cap": 0,
        "image": "https://cdn-icons-png.flaticon.com/512/1213/1213779.png" 
    }
    collection.insert_one(nouvelle_crypto)

def update_crypto(id_str, nouveau_prix, nouvelle_cat):
    """UPDATE: Modifie une crypto existante"""
    collection.update_one(
        {"_id": ObjectId(id_str)},
        {"$set": {"prix_usd": nouveau_prix, "categorie": nouvelle_cat}}
    )

def delete_crypto(id_str):
    """DELETE: Supprime une crypto"""
    collection.delete_one({"_id": ObjectId(id_str)})


st.title("🏦 Crypto CRUD Manager")

with st.sidebar:
    st.header("➕ Ajouter une Crypto")
    with st.form("add_form"):
        new_name = st.text_input("Nom (ex: MonCoin)")
        new_symbol = st.text_input("Symbole (ex: MNC)")
        new_price = st.number_input("Prix ($)", min_value=0.0, format="%.2f")
        new_cat = st.selectbox("Catégorie", ["Top 10", "Altcoin", "Meme Coin", "Portfolio Perso"])
        
        submitted = st.form_submit_button("Ajouter à la base")
        if submitted:
            if new_name and new_symbol:
                create_crypto(new_name, new_symbol, new_price, new_cat)
                st.success(f"{new_name} ajouté !")
                st.rerun() 
            else:
                st.error("Le nom et le symbole sont obligatoires.")

data = get_data()
df = pd.DataFrame(data)

if not data:
    st.info("La base est vide.")
    st.stop()

tab1, tab2 = st.tabs(["📈 Vue Marché (Read)", "🛠️ Gestion (Update/Delete)"])

with tab1:
    # READ
    st.dataframe(
        df,
        column_order=("nom", "symbole", "prix_usd", "categorie", "tendance"),
        use_container_width=True
    )

with tab2:
    st.subheader("Modifier ou Supprimer une ligne")
    
    # Sélecteur pour choisir quelle crypto modifier
    crypto_options = {f"{row['nom']} ({row['symbole']})": row['_id'] for index, row in df.iterrows()}
    selected_label = st.selectbox("Choisir la crypto à gérer :", options=list(crypto_options.keys()))
    
    selected_id = crypto_options[selected_label]
    
    current_crypto = df[df['_id'] == selected_id].iloc[0]

    # UPDATE
    col1, col2 = st.columns(2)
    with col1:
        new_val_price = st.number_input(
            "Nouveau Prix ($)", 
            value=float(current_crypto['prix_usd']),
            key="upd_price"
        )
    with col2:
        new_val_cat = st.selectbox(
            "Nouvelle Catégorie", 
            ["Top 10", "Altcoin", "Meme Coin", "Portfolio Perso"],
            index=["Top 10", "Altcoin", "Meme Coin", "Portfolio Perso"].index(current_crypto['categorie']) if current_crypto['categorie'] in ["Top 10", "Altcoin", "Meme Coin", "Portfolio Perso"] else 1,
            key="upd_cat"
        )
    
    col_btn1, col_btn2 = st.columns([1, 4])
    
    with col_btn1:
        if st.button("💾 Sauvegarder"):
            update_crypto(selected_id, new_val_price, new_val_cat)
            st.success("Modification enregistrée !")
            time.sleep(1)
            st.rerun()
            
    with col_btn2:
        # DELETE
        if st.button("🗑️ Supprimer", type="primary"):
            delete_crypto(selected_id)
            st.warning(f"Crypto supprimée.")
            time.sleep(1)
            st.rerun()

# KPI Rapides en bas de page
st.divider()
st.caption(f"Total éléments dans la base : {len(df)}")