import streamlit as st
import pymongo
import pandas as pd
from groq import Groq
import os
import requests
from dotenv import load_dotenv
from bson.objectid import ObjectId

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

# Tools IA 
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "create_crypto",
            "description": "Ajouter une nouvelle cryptomonnaie dans la base de données.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {"type": "string", "description": "Le nom de la crypto (ex: Bitcoin)"},
                    "symbole": {"type": "string", "description": "Le ticker (ex: BTC)"},
                    "prix": {"type": "number", "description": "Le prix actuel en USD"},
                    "categorie": {"type": "string", "enum": ["Top 10", "Altcoin", "Meme Coin", "Portfolio Perso"]}
                },
                "required": ["nom", "symbole", "prix", "categorie"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_crypto_by_name",
            "description": "Supprimer une crypto en donnant son nom.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nom": {"type": "string", "description": "Le nom exact de la crypto à supprimer"}
                },
                "required": ["nom"]
            }
        }
    }
]

# fonction helper car l'IA ne connait pas les IDs MongoDB
def delete_crypto_by_name(nom):
    res = collection.delete_one({"nom": nom})
    return "Supprimé avec succès." if res.deleted_count > 0 else "Crypto non trouvée."

tab1, tab2, tab3 = st.tabs(["📈 Vue Marché", "🛠️ Gestion", "🧠 Assistant Llama"])

with tab1:
    st.subheader("📈 Vue Marché Global")

    # BARRE DE RECHERCHE
    col_search, col_filter = st.columns([3, 1])
    
    with col_search:
        # champ de recherche
        search_query = st.text_input("🔍 Rechercher (Nom ou Symbole)", placeholder="Ex: Bitcoin, BTC, doge...")
    
    with col_filter:
        # filtre par catégorie
        filter_cat = st.selectbox("Catégorie", ["Tout", "Top 10", "Altcoin", "Meme Coin"])

    # LOGIQUE DE FILTRAGE (Pandas)
    # DataFrame complet
    df_filtered = df.copy()

    # Filtre Recherche 
    if search_query:

        mask = (
            df_filtered['nom'].str.contains(search_query, case=False, na=False) | 
            df_filtered['symbole'].str.contains(search_query, case=False, na=False)
        )
        df_filtered = df_filtered[mask]

    # Filtre Catégorie
    if filter_cat != "Tout":
        df_filtered = df_filtered[df_filtered['categorie'] == filter_cat]

    # AFFICHAGE
    st.caption(f"{len(df_filtered)} résultats trouvés.")
    
    st.dataframe(
        df_filtered,
        column_order=("image", "nom", "symbole", "prix_usd", "variation_24h", "market_cap", "categorie", "tendance"),
        column_config={
            "image": st.column_config.ImageColumn("Logo", width="small"),
            "nom": "Nom",
            "symbole": "Ticker",
            "prix_usd": st.column_config.NumberColumn("Prix ($)", format="$%.2f"),
            "variation_24h": st.column_config.NumberColumn("Var. 24h", format="%.2f%%"), # Ajoute des couleurs auto
            "market_cap": st.column_config.NumberColumn("Cap. Marché", format="$%d"),
            "categorie": "Catégorie"
        },
        hide_index=True,
        use_container_width=True
    )

with tab2:
    st.subheader("Modifier ou Supprimer une ligne")
    
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

# KPI en bas de page
st.divider()
st.caption(f"Total éléments dans la base : {len(df)}")

import json

with tab3:
    st.header("🕵️‍♂️ Agent Autonome Llama")
    st.caption("Je peux lire, mais aussi AJOUTER et SUPPRIMER des données. Essaie : 'Ajoute le token TestCoin à 50 dollars'.")

    # Historique
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Je suis prêt à gérer ta base de données."}]

    for msg in st.session_state.messages:
        if msg["role"] != "tool": 
            st.chat_message(msg["role"]).write(msg["content"])

    # Input
    if prompt := st.chat_input("Donne-moi un ordre..."):
        
        # 1. Affiche la demande user
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # 2. Contexte
        csv_context = df[['nom', 'prix_usd', 'categorie']].head(30).to_csv(index=False)
        
        client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

        with st.chat_message("assistant"):
            with st.spinner("L'Agent réfléchit..."):
                
                # PREMIER APPEL
                messages_history = [
                    {"role": "system", "content": f"Tu es un gestionnaire de base de données. Tu as accès aux données actuelles :\n{csv_context}\n Si l'utilisateur veut ajouter ou supprimer, UTILISE LES OUTILS fournis."},
                    *st.session_state.messages
                ]
                
                response = client_groq.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_history,
                    tools=tools_schema, 
                    tool_choice="auto"
                )
                
                tool_calls = response.choices[0].message.tool_calls
                ai_msg = response.choices[0].message

                # CAS OU L'IA VEUT UTILISER UN OUTIL 
                if tool_calls:
                    # 1. On sauvegarde le message de l'IA
                    st.session_state.messages.append({
                        "role": ai_msg.role,
                        "content": ai_msg.content,
                        "tool_calls": ai_msg.tool_calls
                    })
                    
                    # 2. Boucle sur les outils
                    for tool_call in tool_calls:
                        func_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        
                        st.info(f"🛠️ Exécution de : {func_name} avec {args}")
                        
                        # Exécution réelle du code Python
                        result_text = ""
                        if func_name == "create_crypto":
                            create_crypto(args["nom"], args["symbole"], args["prix"], args["categorie"])
                            result_text = f"Succès : {args['nom']} a été ajouté."
                        elif func_name == "delete_crypto_by_name":
                            result_text = delete_crypto_by_name(args["nom"])
                        
                        # On renvoie le résultat technique à l'IA
                        st.session_state.messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": func_name,
                            "content": result_text,
                        })

                    # L'IA CONFIRME À L'UTILISATEUR
                    final_response = client_groq.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=st.session_state.messages
                    )
                    final_text = final_response.choices[0].message.content
                    st.write(final_text)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})
                    
                    # refresh pour voir les données à jour
                    if "Succès" in final_text or "Supprimé" in final_text:
                        st.rerun()

                # CONVERSATION NORMALE
                else:
                    final_text = ai_msg.content
                    st.write(final_text)
                    st.session_state.messages.append({"role": "assistant", "content": final_text})