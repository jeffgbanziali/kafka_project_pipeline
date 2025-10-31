# jobs/sqlite_test_loader.py
import sqlite3
import json
import os
from datetime import date


DATA_LAKE_PATH = "data_lake"
DB_PATH = "data_warehouse.db"

def load_jsonl_to_sqlite(topic_name: str):
    """Charge les fichiers JSON du topic dans SQLite"""
    day = date.today().strftime("%Y-%m-%d")
    folder = os.path.join(DATA_LAKE_PATH, topic_name, day)

    if not os.path.exists(folder):
        print(f"⚠️ Aucun fichier trouvé dans {folder}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Créer une table dynamique selon le topic
    table_name = topic_name.lower()
    print(f"🗄️ Import vers la table {table_name}")

    # Créer la table si elle n'existe pas déjà
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data JSON,
            topic TEXT,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Charger chaque fichier JSONL du dossier
    for file_name in os.listdir(folder):
        if not file_name.endswith(".jsonl"):
            continue
        file_path = os.path.join(folder, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    cur.execute(
                        f"INSERT INTO {table_name} (data, topic) VALUES (?, ?)",
                        (json.dumps(record), topic_name)
                    )
                except json.JSONDecodeError:
                    print(f"⚠️ Ligne invalide ignorée dans {file_name}")

    conn.commit()
    conn.close()
    print(f"✅ Données du topic {topic_name} importées dans {DB_PATH}\n")


if __name__ == "__main__":
    topics = ["TRANSACTIONS_SECURE", "USER_SPENDING_BY_TYPE"]
    for topic in topics:
        load_jsonl_to_sqlite(topic)
    print("🎉 Test SQLite terminé avec succès.")
