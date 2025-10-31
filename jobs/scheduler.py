# jobs/scheduler.py
import schedule, time
from jobs.sqlite_loader import init_db, load_user_spending
from utils.logger import setup_logger

logger = setup_logger("scheduler")

def orchestrate():
    logger.info("⚙️  Exécution du pipeline : Data Lake → SQLite")
    init_db()
    load_user_spending()

def main():
    orchestrate()  # première exécution immédiate
    schedule.every(10).minutes.do(orchestrate)
    logger.info("🕐 Pipeline planifié toutes les 10 minutes")

    while True:
        schedule.run_pending()
        time.sleep(60)
