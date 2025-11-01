# jobs/scheduler.py
import schedule, time
from datetime import datetime
from jobs.sqlite_loader import load_topic_to_sqlite
from jobs.cleanup import clean_old_data
from jobs.permissions_manager import init_permissions_table, list_permissions
from config.settings import DATA_LAKE_PATH


def orchestrate():
    print(f"\n⚙️ [{datetime.now()}] DÉBUT DU PIPELINE : Kafka → Data Lake → SQLite")

    # Vérifie la gouvernance
    init_permissions_table()
    permissions = list_permissions()
    print(f"🔐 Permissions actuelles ({len(permissions)}): {permissions}")

    # Ingestion Data Lake → SQLite
    topics = [
        "TRANSACTIONS_SECURE", "TRANSACTIONS_USD",
        "USER_SPENDING_BY_TYPE", "SPEND_LAST_FIVE_MIN_BY_TYPE",
        "TRANSACTIONS_BLACKLISTED", "TRANSACTIONS_COMPLETED",
        "TRANSACTIONS_FAILED", "TRANSACTIONS_PENDING", "TRANSACTIONS_PROCESSING"
    ]

    for topic in topics:
        try:
            load_topic_to_sqlite(topic)
        except Exception as e:
            print(f"⚠️ Erreur sur {topic}: {e}")

    # Nettoyage des anciens fichiers
    clean_old_data(days=7)

    print("✅ Pipeline exécuté avec succès.\n")


def main():
    orchestrate()  # première exécution immédiate
    schedule.every(10).minutes.do(orchestrate)
    print("🕐 Scheduler actif — pipeline toutes les 10 minutes.")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
