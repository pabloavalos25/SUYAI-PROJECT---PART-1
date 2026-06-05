from database.db import get_connection

conn = get_connection()

print("TABLA ALUMNOS:")
print(conn.execute("PRAGMA table_info(alumnos)").fetchall())

print("\nDB PATH REAL:")
print(conn.execute("PRAGMA database_list").fetchall())

conn.close()


conn = get_connection()
print(conn.execute("SELECT * FROM configuracion").fetchall())
conn.close()