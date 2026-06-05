import pandas as pd
from database.db import get_connection

EXCEL_PATH = "excel/Alumnas.xlsx"


def normalizar(texto):
    if texto is None:
        return None
    return str(texto).strip().title()


def generar_nombre(nombre, apellido):
    return f"{nombre.strip().title()} {apellido.strip().title()}"


def importar_alumnas():
    df = pd.read_excel(EXCEL_PATH, sheet_name="Alumnas")
    df.columns = df.columns.str.strip()

    with get_connection() as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():

            nombre = normalizar(row.get("Nombre"))
            apellido = normalizar(row.get("Apellido"))
            dia = normalizar(row.get("Día"))

            if not nombre:
                continue

            nombre_completo = generar_nombre(nombre, apellido)

            # 🔍 BUSCAR EXISTENTE
            cursor.execute("""
                SELECT id FROM alumnos
                WHERE nombre = ?
            """, (nombre_completo,))

            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE alumnos
                    SET activo = 1,
                        dia_clase = ?
                    WHERE id = ?
                """, (dia, existe[0]))

            else:
                cursor.execute("""
                    INSERT INTO alumnos (nombre, dia_clase, activo)
                    VALUES (?, ?, 1)
                """, (nombre_completo, dia))

        conn.commit()

    print("✔ Alumnos importados correctamente")

    conn.commit()

    print("✔ Alumnos importados sin duplicados")