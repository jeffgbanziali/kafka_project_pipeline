
# 🧠 TP – Data Lake & Data Warehouse
### Projet : Ingestion, transformation et analyse de flux Kafka dans un Data Lake et Data Warehouse
**Auteur :** Jeff Gbanziali  
**École :** EFREI Paris – Master 1 Data Engineering & IA  
**Date :** 31 octobre 2025  

---

## 🚀 Objectif du TP

L’objectif de ce TP est de construire une **chaîne complète de traitement de données** reposant sur :
- **Kafka / Confluent Platform** pour l’ingestion en streaming,  
- **un Data Lake** (stockage brut en JSONL),  
- **un Data Warehouse (SQLite)** pour les analyses,  
- et **une orchestration automatique** via un scheduler Python.

Ce TP simule un cas réel d’ingénierie des données : ingestion, transformation, gouvernance et analyse continue des transactions.

---

## 🏗️ Architecture Globale du Pipeline

```
Kafka / Confluent Platform
        │
        ▼
Python Consumer (confluent_kafka)
        │
        ▼
Data Lake (dossiers JSONL par topic / date)
        │
        ▼
SQLite Data Warehouse
        │
        ▼
Requêtes SQL d’analyse & visualisation
```

---

## ⚙️ 1. Préparation de l’Environnement Kafka

### 📦 Étape 1 : Démarrage de Confluent Kafka (TP1 cp-all-in-one)

> 💡 Le professeur ou évaluateur doit **démarrer le cluster Kafka** depuis le dossier **`cp-all-in-one`** fourni avec le TP1.

Dans un terminal Docker :
```bash
cd cp-all-in-one
docker-compose up -d
```

Cela lance :
- Zookeeper (port 2181)  
- Kafka Broker (9092)  
- Schema Registry (8081)  
- Kafka Connect (8083)  
- ksqlDB Server (8088)  
- Control Center (9021)  
- REST Proxy (8082)

Vérifiez le bon démarrage :
```bash
docker ps
```

Puis ouvrez **Confluent Control Center** :  
👉 [http://localhost:9021](http://localhost:9021)

---

## 📂 2. Structure du Projet

```
data_lake/
├── config/
│   └── settings.py
├── consumers/
│   ├── kafka_to_datalake.py
│   └── fake_kafka_producer.py
├── cp-all-in-one/
│   └── docker-compose.yml
│   └── kafka_producer_transaction.py
├── jobs/
│   ├── sqlite_loader.py
│   ├── cleanup.py
│   ├── permissions_manager.py
│   └── scheduler.py
├── pipeline/
│   ├── TRANSACTIONS_USD/
│   ├── TRANSACTIONS_SECURE/
│   ├── TRANSACTIONS_FAILED/
│   ├── TRANSACTIONS_PENDING/
│   ├── TRANSACTIONS_BLACKLISTED/
│   └── ...
├── analysis/
│   └── run_queries.py
├── data_warehouse.db
├── requirements.txt
└── README.md
```

---

## 🧰 3. Installation & Configuration

### Étape 1 : Créer l’environnement Python
```bash
py -3.11 -m venv venv
venv\Scripts\activate
```

### Étape 2 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 3 : Exemple de requirements.txt
```txt
confluent-kafka
pandas
schedule
sqlite3-binary
reportlab
```

---

## 🛰️ 4. Consommation des flux Kafka vers le Data Lake

### Étape 1 : Vérifiez vos topics dans Kafka
Dans le Control Center (http://localhost:9021) → rubrique **Topics**, assurez-vous que ces topics existent, 
ensuite lancer ce script :

```bash
python -m cp-all-in-one.kafka_producer_transaction
```
Ce script va envoyer des messages dans notre kafka sous cette forme :
```bash

{
  "TRANSACTION_ID": "TXN-bac5ffc7",
  "TIMESTAMP": "2025-10-13T16:38:28.047846Z",
  "USER_ID": "USER-4026",
  "USER_NAME": "Johnson",
  "PRODUCT_ID": "PROD-678",
  "AMOUNT": 339.47,
  "CURRENCY": "AUD",
  "TRANSACTION_TYPE": "payment",
  "STATUS": "pending",
  "LOCATION": {
    "CITY": "Guangzhou",
    "COUNTRY": "China"
  },
  "PAYMENT_METHOD": "apple_pay",
  "PRODUCT_CATEGORY": "books",
  "QUANTITY": 5,
  "SHIPPING_ADDRESS": {
    "STREET": "174 Main St",
    "ZIP": "31472",
    "CITY": "Guangzhou",
    "COUNTRY": "China"
  },
  "DEVICE_INFO": {
    "OS": "MacOS",
    "BROWSER": "Edge",
    "IP_ADDRESS": "4.217.181.91"
  },
  "CUSTOMER_RATING": 3,
  "DISCOUNT_CODE": null,
  "TAX_AMOUNT": 0
}

```

```
TRANSACTIONS_SECURE
TRANSACTIONS_USD
TRANSACTIONS_BLACKLISTED
TRANSACTIONS_FAILED
TRANSACTIONS_PENDING
TRANSACTIONS_PROCESSING
TRANSACTIONS_COMPLETED
USER_SPENDING_BY_TYPE
SPEND_LAST_FIVE_MIN_BY_TYPE
```

### Étape 2 : Lancer le consumer
```bash
python -m consumers.kafka_to_datalake
```

📡 Le script écoute les topics et écrit les données dans :
```
pipeline/<topic>/<date>/<topic>_<date>.jsonl
```

---

## 🏦 5. Chargement dans le Data Warehouse (SQLite)

### Étape 1 : Lancer le chargement
```bash
python -m jobs.sqlite_loader
```

📦 Les fichiers JSONL sont convertis en tables SQLite :
```
data_warehouse.db
├── TRANSACTIONS_SECURE
├── TRANSACTIONS_USD
├── TRANSACTIONS_FAILED
├── USER_SPENDING_BY_TYPE
└── SPEND_LAST_FIVE_MIN_BY_TYPE
```

---

## ⏰ 6. Orchestration & Gouvernance

### Scheduler automatique (toutes les 10 minutes)
```bash
python -m jobs.scheduler
```

Ce fichier orchestre :
- le chargement Data Lake → SQLite  
- le nettoyage des anciens fichiers (> 7 jours)  
- la vérification des permissions

---

## 🔒 7. Gestion des Permissions et Nettoyage

- `permissions_manager.py` → crée une table `permissions` dans SQLite pour chaque utilisateur.  
- `cleanup.py` → supprime automatiquement les anciens fichiers dans `pipeline/` pour limiter l’espace disque.

---

## 📊 8. Analyse et Requêtes SQL

### Méthode 1 — Terminal SQLite

```bash
sqlite3 data_warehouse.db
```

### Exemples d’analyses :
```sql
-- Total dépensé par type de transaction
SELECT json_extract(data, '$.TRANSACTION_TYPE') AS transaction_type,
       SUM(json_extract(data, '$.AMOUNT_USD')) AS total_spent_usd
FROM TRANSACTIONS_USD
GROUP BY transaction_type;

-- Classement des utilisateurs les plus dépensiers
SELECT json_extract(data, '$.USER_ID_HASHED') AS user,
       SUM(json_extract(data, '$.AMOUNT_USD')) AS total
FROM TRANSACTIONS_USD
GROUP BY user
ORDER BY total DESC
LIMIT 10;
```

### Méthode 2 — Script Python
```bash
python -m analysis.run_queries
```

---

## 📅 9. Rapport Final

Le rapport PDF est généré automatiquement : `TP_DataLake_Report.pdf`

Il contient :
- L’architecture du pipeline  
- La structure du projet  
- La gouvernance et le scheduler  
- Les requêtes d’analyse SQL  

---

## 👨‍💻 Auteur

**Jeff Gbanziali**  
Étudiant M1 Data Engineering & Intelligence Artificielle  
📍 EFREI Paris  
📅 Octobre 2025  
