from services.alumnos import importar_alumnas
from services.cuotas import generar_cuotas
from services.reportes import resumen


from database.db import get_connection

conn = get_connection()
print("DB REAL:", conn.execute("PRAGMA database_list").fetchall())
conn.close()

if __name__ == "__main__":
    print("=== Sistema Escuela Cerámica ===")


    importar_alumnas()

    generar_cuotas("06", 2026)

    resumen()