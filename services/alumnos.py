import pandas as pd
from database.db import get_connection

EXCEL_PATH = "excel/Alumnas.xlsx"


def normalizar(texto):
    if texto is None:
        return None
    return str(texto).strip().title()


def importar_alumnas():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Alumnas")
    df.columns = df.columns.str.strip()

    with get_connection() as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():

            nombre = normalizar(row["Alumnas"])
            dia = normalizar(row["Día"])

            if not nombre:
                continue

            # =========================
            # BUSCAR EXISTENTE
            # =========================
            cursor.execute("""
                SELECT id FROM alumnos
                WHERE nombre = ?
            """, (nombre,))

            existe = cursor.fetchone()

            # =========================
            # SI EXISTE → REACTIVAR
            # =========================
            if existe:
                cursor.execute("""
                    UPDATE alumnos
                    SET activo = 1,
                        dia_clase = COALESCE(?, dia_clase)
                    WHERE id = ?
                """, (dia, existe[0]))

            # =========================
            # SI NO EXISTE → INSERTAR
            # =========================
            else:
                cursor.execute("""
                    INSERT INTO alumnos (nombre, dia_clase, activo)
                    VALUES (?, ?, 1)
                """, (nombre, dia))

        conn.commit()

    print("✔ Alumnos importados sin duplicados")