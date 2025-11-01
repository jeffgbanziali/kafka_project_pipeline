# jobs/cleanup.py
import os
import shutil
from datetime import datetime, timedelta
from config.settings import DATA_LAKE_PATH

def clean_old_data(days: int = 7):
    """Supprime les dossiers de plus de X jours dans le Data Lake."""
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)

    print(f"Nettoyage du Data Lake (avant le {cutoff_date.date()})...")

    for topic in os.listdir(DATA_LAKE_PATH):
        topic_path = os.path.join(DATA_LAKE_PATH, topic)
        if not os.path.isdir(topic_path):
            continue

        for folder in os.listdir(topic_path):
            folder_path = os.path.join(topic_path, folder)
            try:
                folder_date = datetime.strptime(folder, "%Y-%m-%d")
                if folder_date < cutoff_date:
                    shutil.rmtree(folder_path)
                    print(f"🗑️ Dossier supprimé : {folder_path}")
            except ValueError:
                continue

    print("✅ Nettoyage terminé.")
