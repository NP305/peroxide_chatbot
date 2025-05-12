from pymongo import MongoClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["peroxide_logs"]
collection = db["feedbacks"]

def log_to_mongo(soru, ajan, yanit, geri_bildirim=None, yorum=""):
    entry = {
        "timestamp": datetime.utcnow(),
        "soru": soru,
        "ajan": ajan,
        "yanit": yanit,
        "geri_bildirim": geri_bildirim,
        "yorum": yorum
    }
    collection.insert_one(entry)
