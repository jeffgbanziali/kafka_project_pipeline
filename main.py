# main.py
from consumers.kafka_to_datalake import run_consumer
from jobs.scheduler import main as schedule_jobs
import threading

if __name__ == "__main__":
    print("🚀 Lancement du pipeline Data Lake / SQLite Warehouse...")

    # Thread 1 : Kafka → Data Lake
    consumer_thread = threading.Thread(target=run_consumer)
    consumer_thread.start()

    # Thread 2 : Orchestration & chargement SQLite
    schedule_jobs()
