# utils/logger.py
import logging
import os

def setup_logger(name, log_file="pipeline.log"):
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{log_file}"
    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
