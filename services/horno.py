from database.db import get_connection


def registrar_horno(alumno_id, monto=25000):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO horno (alumno_id, monto)
        VALUES (?, ?)
    """, (alumno_id, monto))

    conn.commit()
    conn.close()