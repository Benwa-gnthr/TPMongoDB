import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv

# 1. Chargement du mot de passe depuis le .env existant
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# 2. Config SPÉCIFIQUE à ce script (sans toucher au .env)
DB_NAME = "spacex_data"
COLLECTION_NAME = "lancements"
# API V4 de SpaceX (Lancements passés)
API_URL = "https://api.spacexdata.com/v4/launches/past"

def extract_data():
    """Récupère tous les lancements passés"""
    print(f"🚀 Connexion à l'API SpaceX...")
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # On ne garde que les 20 derniers pour l'exercice (l'API en renvoie ~200)
        last_20_launches = data[-20:]
        # On inverse pour avoir le plus récent en premier
        last_20_launches.reverse()
        
        print(f"✅ {len(last_20_launches)} lancements récupérés.")
        return last_20_launches
    except Exception as e:
        print(f"❌ Erreur API : {e}")
        return []

def transform_data(raw_data):
    """Nettoie les données complexes de SpaceX"""
    processed_data = []
    timestamp = datetime.now()
    
    print("⚙️  Extraction des informations clés...")
    
    for launch in raw_data:
        # L'API SpaceX est très riche, on sélectionne ce qui nous intéresse
        document = {
            "flight_number": launch.get("flight_number"),
            "mission_name": launch.get("name"),
            "date_utc": launch.get("date_utc"),
            "success": launch.get("success"), # True/False
            "details": launch.get("details"), # Texte descriptif
            
            # Ici on stocke un OBJET imbriqué (force de MongoDB)
            "media": {
                "patch_image": launch.get("links", {}).get("patch", {}).get("small"),
                "video_link": launch.get("links", {}).get("webcast"),
                "article": launch.get("links", {}).get("article")
            },
            
            "rocket_id": launch.get("rocket"),
            "ingestion_date": timestamp
        }
        processed_data.append(document)
    
    return processed_data

def load_data(data):
    """Envoie vers MongoDB Atlas dans la base 'spacex_data'"""
    if not data:
        print("⚠️ Rien à envoyer.")
        return

    client = None
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # On utilise insert_many
        result = collection.insert_many(data)
        print(f"🌌 Succès ! {len(result.inserted_ids)} lancements ajoutés dans '{DB_NAME}'.")
        
    except Exception as e:
        print(f"❌ Erreur MongoDB : {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    print("--- 🛰️ Démarrage du Pipeline SpaceX 🛰️ ---")
    
    if not MONGO_URI:
        print("❌ Erreur : Impossible de lire MONGO_URI dans le .env")
    else:
        # Exécution du pipeline
        raw = extract_data()
        if raw:
            clean = transform_data(raw)
            load_data(clean)
            
    print("--- Terminé ---")