import sqlite3


DATABASE_URL = "app/db/servers.db"

def start_db():
    conn = sqlite3.connect('app/db/servers.db')
    with open('app/db/schema.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def get_db():
    db = sqlite3.connect(DATABASE_URL)
    db.row_factory = sqlite3.Row 
    return db

def init_db():
    db = get_db()
    try:
        with open("app/db/schema.sql", "r") as schema_file:
            db.executescript(schema_file.read())
    finally:
        db.close()