from database.db import get_connection


# =========================
# DEUDA DETALLADA PRO
# =========================
def deuda_detallada(alumno_id):
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- CUOTAS ----------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM cuotas
        WHERE alumno_id = ? AND estado = 'PENDIENTE'
    """, (alumno_id,))
    cuotas = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT cuota_1_10
        FROM configuracion
        WHERE id = 1
    """)
    valor = cursor.fetchone()[0] or 0

    deuda_cuota = cuotas * valor

    # ---------------- MATERIAL ----------------
    cursor.execute("""
        SELECT COALESCE(SUM(monto),0)
        FROM materiales
        WHERE alumno_id = ?
    """, (alumno_id,))
    deuda_material = cursor.fetchone()[0] or 0

    # ---------------- HORNO ----------------
    cursor.execute("""
        SELECT COALESCE(SUM(monto),0)
        FROM horno
        WHERE alumno_id = ?
    """, (alumno_id,))
    deuda_horno = cursor.fetchone()[0] or 0

    # ---------------- PAGOS ----------------
    cursor.execute("""
        SELECT COALESCE(SUM(monto),0)
        FROM pagos
        WHERE alumno_id = ?
    """, (alumno_id,))
    pagos = cursor.fetchone()[0] or 0

    conn.close()

    total = deuda_cuota + deuda_material + deuda_horno - pagos

    return {
        "cuota": deuda_cuota,
        "material": deuda_material,
        "horno": deuda_horno,
        "total": total
    }


# =========================
# COMPATIBILIDAD FRONT
# =========================
def deuda_total(alumno_id):
    return deuda_detallada(alumno_id)["total"]


def deuda_cuotas(alumno_id):
    return deuda_detallada(alumno_id)["cuota"]


def deuda_materiales(alumno_id):
    return deuda_detallada(alumno_id)["material"]


def deuda_horno(alumno_id):
    return deuda_detallada(alumno_id)["horno"]