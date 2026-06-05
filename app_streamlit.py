import streamlit as st
import pandas as pd

from database.db import get_connection
from services.deudas import deuda_detallada
from services.movimientos import registrar_pago, registrar_material
from services.historial import obtener_historial
from services.horno import registrar_horno


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="SUYAI", layout="wide")


# =========================
# SESSION
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

if "view" not in st.session_state:
    st.session_state.view = "login"

if "alumno_id" not in st.session_state:
    st.session_state.alumno_id = None

if "alumno_nombre" not in st.session_state:
    st.session_state.alumno_nombre = None

if "horno_toggle" not in st.session_state:
    st.session_state.horno_toggle = False

if "alumno_select_prev" not in st.session_state:
    st.session_state.alumno_select_prev = "Ninguno"

if "filtro_alumnos" not in st.session_state:
    st.session_state.filtro_alumnos = "Activos"


# =========================
# LOGIN
# =========================
def login():
    st.title("Login SUYAI Cerámica")

    user = st.text_input("Usuario", key="login_user")
    pwd = st.text_input("Contraseña", type="password", key="login_pwd")

    if st.button("Ingresar", key="login_btn"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, rol FROM usuarios
            WHERE TRIM(username) = ? AND TRIM(password) = ?
        """, (user.strip(), pwd.strip()))

        data = cursor.fetchone()
        conn.close()

        if data:
            st.session_state.logged = True
            st.session_state.user = data[0]
            st.session_state.rol = data[1]
            st.session_state.view = "dashboard"
            st.rerun()
        else:
            st.error("Credenciales inválidas")


if not st.session_state.logged:
    login()
    st.stop()


# =========================
# DB
# =========================
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, nombre, activo FROM alumnos ORDER BY nombre")
alumnos_all = cursor.fetchall()

alumnos_activos = [(i, n) for i, n, a in alumnos_all if a == 1]
alumnos_inactivos = [(i, n) for i, n, a in alumnos_all if a == 0]


# =========================
# SIDEBAR
# =========================
st.sidebar.title("Navegación")

if st.sidebar.button("Home"):
    st.session_state.view = "dashboard"
    st.session_state.alumno_id = None
    st.session_state.alumno_nombre = None
    st.rerun()

st.sidebar.divider()

alumno_select = st.sidebar.selectbox(
    "👤 Ver alumno",
    ["Ninguno"] + [a[1] for a in alumnos_activos],
    key="alumno_select"
)

if alumno_select != st.session_state.alumno_select_prev:
    st.session_state.alumno_select_prev = alumno_select

    for a in alumnos_activos:
        if alumno_select == a[1]:
            st.session_state.view = "alumno"
            st.session_state.alumno_id = a[0]
            st.session_state.alumno_nombre = a[1]
            st.rerun()


st.sidebar.divider()
st.sidebar.write("🔎 Filtro dashboard")
filtro = st.sidebar.selectbox(
    "Estado alumnos",
    ["Activos", "Inactivos", "Todos"],
    key="filtro_alumnos"
)


# =========================
# HEADER
# =========================
st.title("SUYAI - Taller de Cerámica")

st.sidebar.success(st.session_state.user)

if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.session_state.view = "login"
    st.rerun()


# =========================
# DASHBOARD
# =========================
if st.session_state.view == "dashboard":

    st.subheader("Dashboard general")

    c1, c2, c3 = st.columns(3)

    cursor.execute("SELECT COALESCE(SUM(monto),0) FROM pagos")
    c1.metric("Pagos", f"${cursor.fetchone()[0]}")

    cursor.execute("SELECT COALESCE(SUM(monto),0) FROM materiales")
    c2.metric("Materiales", f"${cursor.fetchone()[0]}")

    cursor.execute("SELECT COUNT(*) FROM cuotas WHERE estado='PENDIENTE'")
    c3.metric("Cuotas pendientes", f"${cursor.fetchone()[0]}")

    st.divider()

    # =========================
    # AGREGAR ALUMNO
    # =========================
    st.subheader("Gestión alumnos")

    with st.expander("➕ Agregar alumno"):

        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre")
        apellido = col2.text_input("Apellido")

        if st.button("Crear alumno"):
            if nombre.strip() and apellido.strip():

                nombre_completo = f"{nombre.strip().title()} {apellido.strip().title()}"

                conn2 = get_connection()
                cur2 = conn2.cursor()

                cur2.execute("SELECT id FROM alumnos WHERE nombre=?", (nombre_completo,))
                existe = cur2.fetchone()

                if existe:
                    st.warning("El alumno ya existe")
                else:
                    cur2.execute("""
                        INSERT INTO alumnos (nombre, dia_clase, activo)
                        VALUES (?, ?, 1)
                    """, (nombre_completo, "Sin asignar"))

                    conn2.commit()
                    st.success("Alumno creado")
                    st.rerun()

                conn2.close()
            else:
                st.error("Completa nombre y apellido")

    st.divider()


    # =========================
    # LISTADOS
    # =========================
    def render_alumno(alumno_id, nombre):
        data = deuda_detallada(alumno_id)

        st.markdown(f"""
        <div style="
            padding:12px;
            border-radius:10px;
            background:#111827;
            margin-bottom:10px;
            color:white;
        ">
            <h4>{nombre}</h4>
            <p>
                Cuotas: <b>${data["cuota"]}</b><br>
                Materiales: <b>${data["material"]}</b><br>
                Horno: <b>${data["horno"]}</b><br>
                Total: <b>${data["total"]}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Ver {nombre}", key=f"view_{alumno_id}"):
            st.session_state.view = "alumno"
            st.session_state.alumno_id = alumno_id
            st.session_state.alumno_nombre = nombre
            st.rerun()


    if filtro in ["Activos", "Todos"]:
        st.subheader("🟢 Alumnos activos")
        for a in alumnos_activos:
            render_alumno(a[0], a[1])

    if filtro in ["Inactivos", "Todos"]:
        st.subheader("🔴 Alumnos inactivos")

        for alumno_id, nombre in alumnos_inactivos:
            col1, col2 = st.columns([3,1])
            col1.write(nombre)

            if col2.button("Reactivar", key=f"react_{alumno_id}"):
                conn2 = get_connection()
                cur2 = conn2.cursor()
                cur2.execute("UPDATE alumnos SET activo=1 WHERE id=?", (alumno_id,))
                conn2.commit()
                conn2.close()

                st.success("Alumno reactivado")
                st.rerun()


# =========================
# ALUMNO
# =========================
elif st.session_state.view == "alumno":

    def volver():
        st.session_state.view = "dashboard"
        st.session_state.alumno_id = None
        st.session_state.alumno_nombre = None
        st.rerun()

    st.button("⬅ Volver al dashboard", on_click=volver)

    alumno_id = st.session_state.alumno_id
    nombre = st.session_state.alumno_nombre

    if alumno_id is None:
        st.session_state.view = "dashboard"
        st.rerun()

    st.title(nombre)

    data = deuda_detallada(alumno_id)

    st.metric("Cuotas", f"${data['cuota']}")
    st.metric("Materiales", f"${data['material']}")
    st.metric("Horno", f"${data['horno']}")
    st.metric("Total", f"${data['total']}")

    st.checkbox("Incluir horno ($25.000)", key="horno_toggle")

    if st.button("Agregar horno"):
        registrar_horno(alumno_id, 25000)
        st.success("Horno agregado")
        st.rerun()

    st.divider()

    st.subheader("Historial")
    df = pd.DataFrame(obtener_historial(alumno_id),
                    columns=["Fecha", "Tipo", "Detalle", "Monto"])
    st.dataframe(df, use_container_width=True)


# =========================
# CLOSE DB
# =========================
conn.close()

st.caption("Sistema Escuela Cerámica")