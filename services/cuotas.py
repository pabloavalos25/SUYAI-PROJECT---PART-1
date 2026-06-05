from datetime import datetime
from database.db import get_connection

def generar_cuotas(mes, año):
    conn = get_connection()
    cursor = conn.cursor()

    # obtener alumnos
    cursor.execute("SELECT id FROM alumnos WHERE activo = 1")
    alumnos = cursor.fetchall()

    periodo = f"{mes}-{año}"

    cursor.execute("""
        SELECT COUNT(*) FROM cuotas WHERE periodo = ?
    """, (periodo,))
    
    if cursor.fetchone()[0] > 0:
        print(f" Ya existen cuotas para {periodo}")
        conn.close()
        return

    for (alumno_id,) in alumnos:
        cursor.execute("""
            INSERT INTO cuotas (alumno_id, periodo, estado, fecha_generacion)
            VALUES (?, ?, 'PENDIENTE', ?)
        """, (
            alumno_id,
            periodo,
            datetime.now().date()
        ))

    conn.commit()
    conn.close()

    print(f"Cuotas generadas para {periodo}")