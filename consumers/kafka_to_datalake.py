import os
import json
import datetime
import time
from confluent_kafka import Consumer
from config.settings import KAFKA_CONFIG, KAFKA_TOPICS, DATA_LAKE_PATH

BATCH_SIZE = 50  # nombre de messages avant écriture
BATCH_INTERVAL = 10  # secondes max entre deux écritures


def write_batch_to_datalake(topic, messages):
    """Écrit un lot de messages dans le Data Lake"""
    if not messages:
        return

    date_str = datetime.date.today().strftime("%Y-%m-%d")
    topic_dir = os.path.join(DATA_LAKE_PATH, topic, date_str)
    os.makedirs(topic_dir, exist_ok=True)

    file_path = os.path.join(topic_dir, f"{topic}_{date_str}.jsonl")
    with open(file_path, "a", encoding="utf-8") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")

    print(f"📦 {len(messages)} messages enregistrés → {file_path}")


def consume_kafka():
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe(KAFKA_TOPICS)
    print(f"🎧 En écoute sur {', '.join(KAFKA_TOPICS)}")

    # Initialisation Data Lake
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    for topic in KAFKA_TOPICS:
        os.makedirs(os.path.join(DATA_LAKE_PATH, topic, date_str), exist_ok=True)
    print(f"📁 Dossiers du Data Lake initialisés pour la date {date_str}\n")

    try:
        buffers = {topic: [] for topic in KAFKA_TOPICS}
        last_flush_time = time.time()

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Vérifie si temps écoulé pour forcer une écriture
                if time.time() - last_flush_time > BATCH_INTERVAL:
                    for topic, batch in buffers.items():
                        write_batch_to_datalake(topic, batch)
                        buffers[topic] = []
                    last_flush_time = time.time()
                continue

            if msg.error():
                print(f"⚠️ Erreur Kafka : {msg.error()}")
                continue

            try:
                value = json.loads(msg.value().decode("utf-8"))
                buffers[msg.topic()].append(value)

                # Si on a atteint le batch
                if len(buffers[msg.topic()]) >= BATCH_SIZE:
                    write_batch_to_datalake(msg.topic(), buffers[msg.topic()])
                    buffers[msg.topic()] = []

            except Exception as e:
                print(f"💥 Erreur décodage message : {e}")

    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l’utilisateur, sauvegarde des buffers restants...")
        for topic, batch in buffers.items():
            write_batch_to_datalake(topic, batch)
    finally:
        consumer.close()
        print("✅ Consumer arrêté proprement.")


if __name__ == "__main__":
    consume_kafka()
