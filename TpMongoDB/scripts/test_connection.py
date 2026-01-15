import os
import pymongo
from dotenv import load_dotenv
import sys

# Chargement de la config
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

print("--- 🛠 TEST DE DIAGNOSTIC MONGODB ---")

# présence du .env
if not MONGO_URI:
    print("❌ ERREUR CRITIQUE : Variable MONGO_URI introuvable.")
    print("   -> Vérifie que ton fichier .env existe et contient MONGO_URI.")
    sys.exit(1)

# Masquage du mot de passe pour l'affichage
uri_masked = MONGO_URI.split("@")[-1] if "@" in MONGO_URI else "URI Malformée"
print(f"ℹ️  Tentative de connexion vers : ...@{uri_masked}")

try:
    # Création du client avec un timeout court (5 secondes max)
    # Si ça ne répond pas en 5s = dead
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # commande "ping"
    print("⏳ Envoi du ping au serveur...")
    client.admin.command('ping')
    print("✅ SUCCÈS : Le serveur MongoDB a répondu au ping !")

    # Vérification des accès
    print("📋 Vérification des droits d'accès...")
    dbs = client.list_database_names()
    
    if DB_NAME in dbs:
        print(f"✅ La base de données '{DB_NAME}' existe bien.")
    else:
        print(f"⚠️ La base '{DB_NAME}' n'existe pas encore (elle sera créée à la première insertion).")
        print(f"   -> Bases existantes : {', '.join(dbs)}")

    server_info = client.server_info()
    version = server_info.get("version")
    print(f"Version du serveur Atlas : {version}")

except pymongo.errors.ServerSelectionTimeoutError:
    print("\n❌ ERREUR DE CONNEXION (Timeout)")
    print("   -> Causes possibles :")
    print("      1. Ton adresse IP n'est pas autorisée dans Atlas (Network Access).")
    print("      2. Le lien MONGO_URI est incorrect (cluster0...).")
    print("      3. Tu as un pare-feu/VPN qui bloque le port 27017.")

except pymongo.errors.OperationFailure as e:
    print(f"\n❌ ERREUR D'AUTHENTIFICATION : {e}")
    print("   -> Vérifie ton utilisateur et ton mot de passe dans le .env.")

except Exception as e:
    print(f"\n❌ ERREUR INCONNUE : {e}")

finally:
    if 'client' in locals():
        client.close()
    print("--- FIN DU TEST ---")