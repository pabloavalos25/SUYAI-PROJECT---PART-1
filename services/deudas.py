from database.db import get_connection


# =========================
# CUOTAS
# =========================
def deuda_cuotas(alumno_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM cuotas
        WHERE alumno_id = ? AND estado = 'PENDIENTE'
    """, (alumno_id,))
    cuotas_pendientes = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT cuota_1_10
        FROM configuracion
        WHERE id = 1
    """)
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return 0

    valor_cuota = row[0] or 0

    return cuotas_pendientes * valor_cuota


# =========================
# MATERIALES
# =========================
def deuda_materiales(alumno_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM materiales
        WHERE alumno_id = ?
    """, (alumno_id,))

    materiales = cursor.fetchone()[0] or 0
    conn.close()

    return materiales


# =========================
# PAGOS
# =========================
def total_pagos(alumno_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM pagos
        WHERE alumno_id = ?
    """, (alumno_id,))

    pagos = cursor.fetchone()[0] or 0
    conn.close()

    return pagos


# =========================
# TOTAL GENERAL (COMPATIBLE CON TU SISTEMA ACTUAL)
# =========================
def deuda_total(alumno_id):
    return round(
        deuda_cuotas(alumno_id)
        + deuda_materiales(alumno_id)
        - total_pagos(alumno_id),
        2
    )