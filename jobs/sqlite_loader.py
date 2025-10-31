# jobs/sqlite_loader.py
import os
import json
import sqlite3
from datetime import date
from config.settings import  DATA_LAKE_PATH
DATA_PATH = DATA_LAKE_PATH
DB_PATH = "data_warehouse.db"

TOPICS = [
    "transactions_secure",
    "transactions_usd",
    "transactions_blacklisted",
    "transactions_completed",
    "transactions_failed",
    "transactions_pending",
    "transactions_processing",
    "transactions_cancelled",
    "spend_last_five_min_by_type",
    "user_spending_by_type"
]


def ensure_folders_exist():
    """Crée les dossiers de stockage s'ils n'existent pas encore"""
    today = date.today().strftime("%Y-%m-%d")
    for topic in TOPICS:
        folder = os.path.join(DATA_PATH, topic, today)
        os.makedirs(folder, exist_ok=True)
    print(f"📂 Tous les dossiers du Data Lake ont été vérifiés/créés ({today}).")


def load_topic_to_sqlite(topic_name):
    """Charge les fichiers JSONL d’un topic vers SQLite"""
    today = date.today().strftime("%Y-%m-%d")
    folder = os.path.join(DATA_PATH, topic_name, today)

    if not os.path.exists(folder):
        print(f"⚠️ Aucun dossier trouvé pour {topic_name} ({folder})")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {topic_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data JSON,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    for file in os.listdir(folder):
        if file.endswith(".jsonl"):
            path = os.path.join(folder, file)
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        cur.execute(f"INSERT INTO {topic_name} (data) VALUES (?)", [json.dumps(record)])
                    except json.JSONDecodeError:
                        print(f"⚠️ Ligne invalide ignorée : {line[:80]}")

    conn.commit()
    conn.close()
    print(f"✅ Données importées dans table {topic_name} depuis {folder}")


if __name__ == "__main__":
    ensure_folders_exist()
    for topic in TOPICS:
        load_topic_to_sqlite(topic)
    print("🎉 Import Data Lake → SQLite terminé.")
