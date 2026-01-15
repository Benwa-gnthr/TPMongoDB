import os
import pymongo
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def clean_crypto_data():
    client = pymongo.MongoClient(MONGO_URI)
    db = client["crypto_data"]
    
    # 1. Lecture des données brutes
    raw_data = list(db["market_cap_raw"].find())
    
    clean_data = []
    
    print("⚙️  Nettoyage et Analyse en cours...")
    for coin in raw_data:
        # Analyse de la tendance
        change = coin.get("price_change_percentage_24h", 0)
        trend = "🔥 Hausse" if change > 0 else "🔻 Baisse"
        
        # Catégorisation (Logic Metier)
        rank = coin.get("market_cap_rank")
        category = "Top 10" if rank <= 10 else "Altcoin"
        
        # Construction du document propre
        clean_doc = {
            "nom": coin.get("name"),
            "symbole": coin.get("symbol").upper(),
            "prix_usd": round(coin.get("current_price", 0), 2),
            "variation_24h": round(change, 2),
            "tendance": trend,
            "categorie": category,
            "image": coin.get("image"),
            "market_cap": coin.get("market_cap")
        }
        clean_data.append(clean_doc)
    
    # 2. Écriture dans la collection PROPRE
    db["market_cap_clean"].drop() # On remplace par les données fraîches
    
    if clean_data:
        db["market_cap_clean"].insert_many(clean_data)
        print(f"✨ {len(clean_data)} lignes nettoyées et insérées dans 'market_cap_clean'.")
    
    client.close()

if __name__ == "__main__":
    clean_crypto_data()