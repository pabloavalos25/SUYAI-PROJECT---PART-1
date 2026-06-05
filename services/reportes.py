from database.db import get_connection

def resumen():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.nombre,
            COUNT(c.id) as cuotas_pendientes
        FROM alumnos a
        LEFT JOIN cuotas c ON a.id = c.alumno_id
        WHERE c.estado = 'PENDIENTE'
        GROUP BY a.id
    """)

    for row in cursor.fetchall():
        nombre = row[0]
        cuotas_pendientes = row[1]

        print(f"Alumno: {nombre} | Cuotas pendientes: {cuotas_pendientes}")

    conn.close()