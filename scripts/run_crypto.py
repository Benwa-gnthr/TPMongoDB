import os
import requests
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Config
DB_NAME = "crypto_data"
COLLECTION_RAW = "market_cap_raw" # Collection "Sale"
API_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false"

def extract_crypto():
    print("📡 Récupération des cours crypto...")
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # On ajoute le timestamp d'ingestion
        timestamp = datetime.now()
        for coin in data:
            coin['ingested_at'] = timestamp

        # Connexion MongoDB
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # On vide la table brute pour ne garder que le "snapshot" actuel (l'instant T)
        # Dans un vrai projet Big Data, on garderait l'historique, mais ici on veut le "Live"
        db[COLLECTION_RAW].drop()
        
        if data:
            db[COLLECTION_RAW].insert_many(data)
            print(f"✅ {len(data)} cryptos mises à jour dans '{COLLECTION_RAW}'.")
            
        client.close()
        
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    extract_crypto()