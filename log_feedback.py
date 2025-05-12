import csv
from datetime import datetime
import os

LOG_PATH = "logs/interaction_logs.csv"

def initialize_log():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "soru", "ajan", "yanit", "geri_bildirim", "yorum"])

def log_interaction(soru, ajan, yanit, geri_bildirim=None, yorum=""):
    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().isoformat(),
            soru,
            ajan,
            yanit,
            geri_bildirim,
            yorum
        ])
