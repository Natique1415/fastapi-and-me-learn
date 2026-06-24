import sqlite3
import os
from app.config import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# this path to the db is relative to this file
DB_PATH = os.path.join(BASE_DIR, settings.db_name)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn

    finally:
        conn.close()


# todo: parameter table_name and db_path
def does_id_exist(id: int, table_name: str, DB_PATH: str) -> bool:
    connection = sqlite3.connect(DB_PATH)
    curr = connection.cursor()
    curr.execute(f"SELECT EXISTS(SELECT 1 from {table_name} WHERE id = ?)", (id,))
    result = curr.fetchone()
    connection.close()
    return bool(result[0])


def get_id(user_mail: str, table_name: str, DB_PATH: str) -> int:
    connection = sqlite3.connect(DB_PATH)
    curr = connection.cursor()
    curr.execute(f"SELECT id FROM {table_name} WHERE email = ?", (user_mail,))
    result = curr.fetchone()
    connection.close()
    return result[0]
