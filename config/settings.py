# config/settings.py

KAFKA_CONFIG = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "data_lake_consumer_group",
    "auto.offset.reset": "earliest",
}

KAFKA_TOPICS = [
    "TRANSACTIONS_SECURE",
    "TRANSACTIONS_USD",
    "TRANSACTIONS_BLACKLISTED",
    "TRANSACTIONS_COMPLETED",
    "TRANSACTIONS_FAILED",
    "TRANSACTIONS_PENDING",
    "TRANSACTIONS_PROCESSING",
    "TRANSACTIONS_CANCELLED",
    "USER_SPENDING_BY_TYPE",
    "SPEND_LAST_FIVE_MIN_BY_TYPE"
]


DATA_LAKE_PATH = "pipeline"

# ✅ Nouveau : configuration SQLite
SQLITE_DB_PATH = "data_warehouse.db"
