from database.db import get_connection

def aplicar_pago(alumno_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cuotas
        SET estado = 'PAGADO'
        WHERE id = (
            SELECT id FROM cuotas
            WHERE alumno_id = ? AND estado = 'PENDIENTE'
            LIMIT 1
        )
    """, (alumno_id,))

    conn.commit()
    conn.close()