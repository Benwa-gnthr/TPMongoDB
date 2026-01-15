import os
import requests
import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "meme_studio"
COLLECTION_NAME = "memes_top_100"

def get_memes():
    print("Récupération des mèmes en cours...")
    url = "https://api.imgflip.com/get_memes"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["success"]:
            memes = data["data"]["memes"]
            print(f"✅ {len(memes)} mèmes récupérés !")
            
            # Connexion Mongo
            client = pymongo.MongoClient(MONGO_URI)
            db = client[DB_NAME]
            col = db[COLLECTION_NAME]
            
            # On vide et on remplit (Full Refresh)
            col.drop()
            col.insert_many(memes)
            print("💾 Sauvegardé dans MongoDB Atlas.")
            client.close()
        else:
            print("❌ L'API a refusé la demande.")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    get_memes()