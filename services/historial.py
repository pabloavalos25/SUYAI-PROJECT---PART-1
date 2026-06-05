from database.db import get_connection


def obtener_historial(alumno_id):
    conn = get_connection()
    cursor = conn.cursor()

    movimientos = []

    # ======================
    # PAGOS (NEGATIVO)
    # ======================
    cursor.execute("""
        SELECT fecha, monto, medio_pago
        FROM pagos
        WHERE alumno_id = ?
    """, (alumno_id,))
    
    for fecha, monto, medio in cursor.fetchall():
        movimientos.append((
            fecha,
            "Pago",
            medio,
            -monto
        ))

    # ======================
    # MATERIALES (POSITIVO)
    # ======================
    cursor.execute("""
        SELECT fecha, descripcion, monto
        FROM materiales
        WHERE alumno_id = ?
    """, (alumno_id,))
    
    for fecha, desc, monto in cursor.fetchall():
        movimientos.append((
            fecha,
            "Material",
            desc,
            +monto
        ))

    # ======================
    # CUOTAS (DEUDA)
    # ======================
    cursor.execute("""
        SELECT fecha_generacion, periodo
        FROM cuotas
        WHERE alumno_id = ?
    """, (alumno_id,))
    
    for fecha, periodo in cursor.fetchall():
        movimientos.append((
            fecha,
            "Cuota",
            periodo,
            None
        ))

    conn.close()

    # ordenar por fecha
    movimientos.sort(key=lambda x: x[0], reverse=True)

    return movimientos