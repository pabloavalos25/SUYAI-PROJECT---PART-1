from database.db import get_connection
from datetime import datetime


def registrar_pago(alumno_id, monto, medio_pago):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pagos (alumno_id, fecha, monto, medio_pago, observacion)
        VALUES (?, ?, ?, ?, ?)
    """, (
        alumno_id,
        datetime.now().date(),
        monto,
        medio_pago,
        "Pago registrado desde Streamlit"
    ))

    conn.commit()
    conn.close()


def registrar_material(alumno_id, descripcion, monto):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO materiales (alumno_id, fecha, descripcion, monto)
        VALUES (?, ?, ?, ?)
    """, (
        alumno_id,
        datetime.now().date(),
        descripcion,
        monto
    ))

    conn.commit()
    conn.close()