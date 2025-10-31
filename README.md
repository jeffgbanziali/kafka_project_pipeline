# 🧠 TP – Data Lake & Data Warehouse (Confluent + Kafka + SQLite)

## 🎯 Objectif du TP
Ce projet met en place une **chaîne complète de traitement de données en streaming et batch**, basée sur **Kafka (Confluent Platform)**, un **Data Lake** (stockage local structuré) et un **Data Warehouse** sous **SQLite**.

L’objectif est de :  
- Créer un pipeline de bout en bout depuis Kafka jusqu’au stockage analytique.  
- Appliquer les principes de l’ingénierie des données : ingestion, transformation, stockage, et analyse.  
- Manipuler des flux de transactions sécurisées, agrégées et horodatées.

---

## 🏗️ Architecture générale

```text
Kafka Topics  →  Data Lake (JSONL)  →  SQLite Data Warehouse
   ↑
   └── KSQL Streams & Tables (transactions, status, spending, blacklist…)
```

### Étapes principales :
1. **Ingestion Kafka :**
   - Utilisation de Confluent Platform (`docker-compose`) pour héberger Kafka, Schema Registry, KSQLDB, etc.
   - Topics créés :  
     `TRANSACTIONS_SECURE`, `TRANSACTIONS_USD`, `TRANSACTIONS_BLACKLISTED`,  
     `TRANSACTIONS_COMPLETED`, `TRANSACTIONS_FAILED`, `TRANSACTIONS_PENDING`,  
     `TRANSACTIONS_PROCESSING`, `TRANSACTIONS_CANCELLED`,  
     `USER_SPENDING_BY_TYPE`, `SPEND_LAST_FIVE_MIN_BY_TYPE`.

2. **Data Lake :**
   - Stockage local des messages JSON dans :  
     `pipeline/<topic>/<date>/<topic>_<date>.jsonl`
   - Structuration journalière.
   - Enrichissement automatique via le consumer Kafka.

3. **Data Warehouse (SQLite) :**
   - Chargement automatique depuis le Data Lake.
   - Tables créées automatiquement :  
     `TRANSACTIONS_SECURE`, `TRANSACTIONS_USD`, `USER_SPENDING_BY_TYPE`,  
     `SPEND_LAST_FIVE_MIN_BY_TYPE`, etc.
   - Chaque table contient :
     ```sql
     id INTEGER PRIMARY KEY,
     data JSON,
     imported_at TIMESTAMP
     ```

---

## ⚙️ Installation

### 1️⃣ Cloner le projet
```bash
git clone <repo-url>
cd data_lake
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3️⃣ Lancer la stack Kafka Confluent
```bash
docker-compose up -d
```

### 4️⃣ Démarrer le consumer Kafka → Data Lake
```bash
python -m consumers.kafka_to_datalake
```

Le script écoute tous les topics listés dans `config/settings.py` et écrit les messages dans `pipeline/`.

### 5️⃣ Charger les données dans SQLite
```bash
python -m jobs.sqlite_loader
```

Une base `data_warehouse.db` est alors créée/actualisée.

---

## 🔄 Pipeline de traitement

### **1. KSQL Streams**
Les streams créés depuis `TRANSACTIONS_SECURE` :
```sql
CREATE STREAM TRANSACTIONS_USD AS
SELECT
  TRANSACTION_ID,
  USER_ID_HASHED,
  AMOUNT,
  CURRENCY,
  TRANSACTION_TYPE,
  STATUS,
  CASE
    WHEN CURRENCY = 'EUR' THEN AMOUNT * 1.1
    WHEN CURRENCY = 'GBP' THEN AMOUNT * 1.25
    WHEN CURRENCY = 'CAD' THEN AMOUNT * 0.74
    ELSE AMOUNT
  END AS AMOUNT_USD,
  'USD' AS TARGET_CURRENCY
FROM TRANSACTIONS_SECURE
EMIT CHANGES;
```

### **2. Tables analytiques**
Exemple : total dépensé par utilisateur et par type :
```sql
CREATE TABLE USER_SPENDING_BY_TYPE AS
SELECT USER_ID_HASHED, TRANSACTION_TYPE,
       SUM(AMOUNT_USD) AS TOTAL_SPENT_USD
FROM TRANSACTIONS_USD
GROUP BY USER_ID_HASHED, TRANSACTION_TYPE
EMIT CHANGES;
```

### **3. Fenêtres glissantes (5 minutes)**
```sql
CREATE TABLE SPEND_LAST_FIVE_MIN_BY_TYPE AS
SELECT TRANSACTION_TYPE,
       SUM(AMOUNT_USD) AS TOTAL_LAST5MIN
FROM TRANSACTIONS_USD
WINDOW HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)
GROUP BY TRANSACTION_TYPE
EMIT CHANGES;
```

---

## 🧩 Structure du projet

```text
data_lake/
├── config/
│   └── settings.py              # Configuration générale (Kafka, Data Lake, Topics)
├── consumers/
│   ├── kafka_to_datalake.py     # Consumer Kafka → Data Lake
│   └── fake_kafka_producer.py   # Générateur de données de test
├── jobs/
│   └── sqlite_loader.py         # Charge le Data Lake → SQLite
├── pipeline/
│   ├── TRANSACTIONS_SECURE/
│   ├── TRANSACTIONS_USD/
│   ├── TRANSACTIONS_BLACKLISTED/
│   ├── USER_SPENDING_BY_TYPE/
│   └── SPEND_LAST_FIVE_MIN_BY_TYPE/
└── data_warehouse.db            # Base SQLite générée automatiquement
```

---

## 🧮 Analyse dans SQLite

### Lister les tables
```sql
.tables
```

### Voir les premières lignes
```sql
SELECT * FROM TRANSACTIONS_USD LIMIT 5;
```

### Extraire des champs JSON
```sql
SELECT
  json_extract(data, '$.TRANSACTION_ID') AS TRANSACTION_ID,
  json_extract(data, '$.AMOUNT_USD') AS AMOUNT_USD,
  json_extract(data, '$.TRANSACTION_TYPE') AS TRANSACTION_TYPE
FROM TRANSACTIONS_USD
LIMIT 10;
```

### Agréger par type
```sql
SELECT
  json_extract(data, '$.TRANSACTION_TYPE') AS type,
  SUM(json_extract(data, '$.AMOUNT_USD')) AS total
FROM TRANSACTIONS_USD
GROUP BY type;
```

---

## 🧠 Points d’apprentissage

| Thème | Compétence acquise |
|-------|--------------------|
| Kafka / Confluent | Création de topics, production et consommation de flux |
| KSQLDB | Manipulation de données en streaming et agrégation temps réel |
| Data Lake | Stockage brut JSON structuré par date et sujet |
| Data Warehouse | Intégration analytique (SQLite) |
| Python | Automatisation du pipeline (producers, consumers, loaders) |

---

## 🏁 Résultat final

✅ Un pipeline de données complet :  
Kafka → KSQL → Data Lake (JSON) → SQLite (analytique).

✅ Une architecture conforme à un **mini-lab d’ingénierie de données moderne**.  
✅ Réutilisable pour d’autres sujets (IoT, transactions bancaires, logs web, etc.).

---

📅 Date de réalisation : **31/10/2025**  
👨‍💻 Auteur : **Jeff Gbanziali**
