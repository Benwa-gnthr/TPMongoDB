import os
import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "meme_studio"

def clean_memes():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # 1. Lecture (Raw)
    raw_memes = list(db["memes_top_100"].find())
    print(f"📦 {len(raw_memes)} mèmes bruts récupérés.")
    
    clean_data = []
    
    # 2. Transformation
    print("⚙️  Calcul des formats et traduction...")
    for meme in raw_memes:
        # Calcul du ratio (Largeur / Hauteur)
        width = meme.get("width", 1)
        height = meme.get("height", 1)
        ratio = width / height
        
        # Détermination du format
        if 0.9 <= ratio <= 1.1:
            fmt = "Carré (Insta)"
        elif ratio > 1.1:
            fmt = "Paysage (YouTube)"
        else:
            fmt = "Portrait (TikTok)"
            
        # Création du document propre (traduit en FR)
        doc = {
            "id_original": meme.get("id"),
            "titre": meme.get("name"),
            "url_image": meme.get("url"),
            "largeur": width,
            "hauteur": height,
            "nb_zones_texte": meme.get("box_count"),
            "format": fmt,  # Notre champ calculé !
            "ratio": round(ratio, 2)
        }
        clean_data.append(doc)
    
    # 3. Chargement (Clean)
    target_col = db["memes_clean"]
    target_col.drop() # On remplace tout
    target_col.insert_many(clean_data)
    
    print(f"✨ {len(clean_data)} mèmes nettoyés sauvegardés dans 'memes_clean'.")
    client.close()

if __name__ == "__main__":
    clean_memes()