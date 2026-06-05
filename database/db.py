import sqlite3

DB_PATH = "database/ceramica.db"

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)

def get_connection():
    return sqlite3.connect(DB_PATH)


def crear_tabla():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia TEXT,
        nombre TEXT
    )
    """)

    conn.commit()
    conn.close()