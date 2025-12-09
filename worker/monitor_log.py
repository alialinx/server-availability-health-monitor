from datetime import datetime
from zoneinfo import ZoneInfo
from app.database.database import get_db

def log_monitor_event(server_id: str,log_type: str,message: str,contacts: list = None,status: str = None,response: str = None):

    log_entry = {
        "server_id": server_id,
        "log_type": log_type,
        "message": message,
        "contacts": contacts or [],
        "status": status,
        "response": response,
        "timestamp": datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M:%S")
    }


    try:
        db = get_db()
        logs_collection = db.monitor_logs
        result = logs_collection.insert_one(log_entry)
    except Exception as e:
        print(f"[ERROR] LOGGING FAILED: {e}")
