import os
import pymongo
import pandas as pd
from dotenv import load_dotenv

# 1. Config
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "spacex_data"
SOURCE_COLLECTION = "lancements"
TARGET_COLLECTION = "lancements_clean"

def clean_and_transfer():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # A. Lecture (READ)
    raw_data = list(db[SOURCE_COLLECTION].find())
    print(f"📦 Données brutes récupérées : {len(raw_data)}")
    
    clean_data = []
    
    # B. Transformation
    for launch in raw_data:
        # 1. Gestion des valeurs nulles (si pas de détails, on met un texte par défaut)
        details_text = launch.get("details")
        if not details_text:
            details_text = "Aucun détail fourni pour cette mission."
            
        # 2. Aplatissage (Flattening) : On sort les liens de l'objet imbriqué
        # C'est crucial pour le Dashboard plus tard
        patch_img = launch.get("media", {}).get("patch_image")
        video_url = launch.get("media", {}).get("video_link")
        
        # 3. Construction du document propre
        clean_doc = {
            "flight_number": launch.get("flight_number"),
            "mission_name": launch.get("mission_name"),
            "date": launch.get("date_utc"), # On pourrait convertir en format Date Python ici
            "success": launch.get("success"),
            "status": "Succès" if launch.get("success") else "Échec", # Plus lisible pour l'humain
            "details": details_text,
            "image_url": patch_img, # Directement accessible
            "video_url": video_url,
            "rocket_id": launch.get("rocket_id")
        }
        clean_data.append(clean_doc)
    
    # C. Écriture (CREATE / UPDATE)
    # On vide la collection propre avant de la remplir (méthode "Full Refresh")
    db[TARGET_COLLECTION].drop() 
    print("🧹 Ancienne collection nettoyée.")
    
    if clean_data:
        db[TARGET_COLLECTION].insert_many(clean_data)
        print(f"✨ Transformation terminée ! {len(clean_data)} documents propres insérés dans '{TARGET_COLLECTION}'.")
    
    client.close()

if __name__ == "__main__":
    clean_and_transfer()