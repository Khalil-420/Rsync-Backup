import sqlite3
from app.core.config import *
from fastapi import HTTPException
from pydantic import *
from app.db.init_db import get_db,DATABASE_URL


def add_server_to_db(server: Server):
    db = get_db()
    try:
        exist = get_all_servers_from_db()
        for serv in exist:
            if dict(serv)['host'] == server.host:
                return 0
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO servers (name, host, user, remote_path, local_folder)
            VALUES (?, ?, ?, ?, ?)
            """,
            (server.name, server.host, server.user, server.remote_path, server.local_folder)
        )
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        raise 
    finally:
        db.close()

def get_server_by_id(id: int):
    db = get_db()
    try:
        return db.execute("SELECT * FROM servers WHERE id=?",(id,))
    finally:
        db.close()

def get_all_servers_from_db(offset: int = 0, limit: int = 0):
    db = get_db()
    try:
        if limit <= 0:
            return db.execute("SELECT * FROM servers").fetchall()
        else:
            return db.execute("SELECT * FROM servers LIMIT ? OFFSET ?", (limit, offset)).fetchall()
    finally:
        db.close()


def remove_server_from_db(id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM servers WHERE id=?", (id,))
    existing_server = cursor.fetchone()
    if not existing_server:
        db.close()
        return 0
    cursor.execute("DELETE FROM servers WHERE id=?", (id,))
    db.commit()
    db.close()
    return 1


def fetch_server_by_id(server_id: int) -> Server:
    query = "SELECT * FROM servers WHERE id = ?"

    with sqlite3.connect(DATABASE_URL) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, (server_id,))
        row = cursor.fetchone()

        if row:
            return Server(**dict(row))
        else:
            return None

def update_server_to_db(server_id: int, update_data: dict):
    db = get_db()
    try:
        cursor = db.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(server_id)
        cursor.execute(
            f"""
            UPDATE servers
            SET {set_clause}
            WHERE id = ?
            """,
            values
        )
        db.commit()
        return cursor.rowcount  # Return number of rows updated
    finally:
        db.close()



def update_server_in_db(server_id: int, update_data: Server):
    server = fetch_server_by_id(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    update_data_dict = update_data.model_dump()
    rows_updated = update_server_to_db(server_id, update_data_dict)

    if rows_updated == 0:
        raise HTTPException(status_code=400, detail="Update failed")
    
    return {"message": "Server updated successfully"}



    