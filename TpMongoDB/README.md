# 🏦 Crypto Manager & AI Agent Dashboard

Ce projet est une application complète de **Data Engineering** et d'**Intelligence Artificielle**.
Il permet de récupérer des données financières en temps réel, de les stocker dans une base NoSQL (MongoDB), et de les gérer via une interface web pilotée par un **Agent IA autonome**.

---

## 🏗️ Architecture Technique

Le projet repose sur une architecture **ETL (Extract, Transform, Load)** couplée à une interface **Streamlit**.

### 1. Pipeline de Données (Backend)
* **Extraction :** Script Python connectée à l'API publique **CoinGecko** pour récupérer les données de marché en temps réel.
* **Transformation :** Nettoyage des données avec **Pandas** (gestion des types, arrondis, calculs de tendances).
* **Chargement (Load) :** Stockage des documents JSON dans **MongoDB Atlas** (Cluster Cloud).

### 2. Interface & Intelligence (Frontend)
* **Visualisation :** Application **Streamlit** connectée à MongoDB.
* **Moteur IA :** Utilisation de l'API **Groq** (Modèle **Llama 3**) pour :
    * **RAG (Retrieval-Augmented Generation) :** Analyse des données du tableau en temps réel.
    * **Function Calling (Agent) :** L'IA possède des "outils" pour insérer ou supprimer des données dans la base de manière autonome sur demande de l'utilisateur.

---

## 💾 Modèle de Données (NoSQL)

Les données sont stockées dans la collection `market_cap_clean`. Voici la structure d'un document type (JSON) :

```json
{
  "_id": "ObjectId('65a1b2c3d4e5f6g7h8i9j0k1')",
  "nom": "Bitcoin",
  "symbole": "BTC",
  "prix_usd": 42150.55,
  "variation_24h": 1.25,
  "market_cap": 825000000000,
  "categorie": "Top 10",
  "tendance": "🔥 Hausse",
  "image": "[https://assets.coingecko.com/coins/images/1/large/bitcoin.png](https://assets.coingecko.com/coins/images/1/large/bitcoin.png)"
}