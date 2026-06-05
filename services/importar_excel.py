import pandas as pd
import sqlite3

EXCEL_PATH = "excel/Alumnas.xlsx"
DB_PATH = "ceramica.db"


def crear_tabla():
    conn = sqlite3.connect(DB_PATH)
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


def importar_alumnas():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Alumnas")

    df.columns = df.columns.str.strip()

    df["Día"] = df["Día"].ffill().str.strip()
    df["Alumnas"] = df["Alumnas"].str.strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia TEXT,
        nombre TEXT,
        UNIQUE(dia, nombre)
    )
    """)

    insertados = 0

    for _, row in df.iterrows():

        dia = row["Día"]
        nombre = row["Alumnas"]

        if pd.isna(nombre):
            continue

        cursor.execute("""
        INSERT OR IGNORE INTO alumnos (dia, nombre)
        VALUES (?, ?)
        """, (dia, nombre))

        insertados += 1

    conn.commit()
    conn.close()

    print("Insertados:", insertados)


def ver_datos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alumnos")
    rows = cursor.fetchall()

    print("\nDATOS EN SQLITE:")
    for r in rows:
        print(r)

    conn.close()


if __name__ == "__main__":
    crear_tabla()
    importar_alumnas()
    ver_datos()