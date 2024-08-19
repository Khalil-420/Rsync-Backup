from app.core.config import *
from pydantic import *
from app.db.init_db import get_db,DATABASE_URL

def add_notification_to_db(error_message: str):
    try:    
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO notifications (notification_message)
            VALUES (?)
            """,
            (error_message,)
        )
        db.commit()
    except Exception as e:
        print("failed to add notification from database")
    finally:
        db.close()

def get_notifications_from_db():
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("SELECT notification_message FROM notifications")
        rows = cursor.fetchall()
        return [row['notification_message'] for row in rows]
    except Exception as e:  
        print("failed to get notification from database")
    finally:
        db.close()
        
def clear_notifications():
    try:    
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM notifications")
        db.commit()
    except Exception as e:
        print("failed to clean notification from database")
    finally:
        db.close()
    