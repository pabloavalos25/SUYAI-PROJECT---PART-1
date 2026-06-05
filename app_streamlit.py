import streamlit as st
import pandas as pd

from database.db import get_connection
from services.deudas import deuda_total, deuda_cuotas, deuda_materiales, deuda_detallada
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


# =========================
# LOGIN BLOCK
# =========================
if not st.session_state.logged:
    login()
    st.stop()


# =========================
# DB
# =========================
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, nombre FROM alumnos WHERE activo=1 ORDER BY nombre")
alumnos = cursor.fetchall()

dict_alumnos = {nombre: aid for aid, nombre in alumnos}


# =========================
# SIDEBAR
# =========================
st.sidebar.title("Navegación")

if st.sidebar.button("🏠 Dashboard"):
    st.session_state.view = "dashboard"
    st.session_state.alumno_id = None
    st.session_state.alumno_nombre = None
    st.rerun()

st.sidebar.divider()


alumno_select = st.sidebar.selectbox(
    "👤 Ver alumno",
    ["Ninguno"] + [a[1] for a in alumnos],
    key="alumno_select"
)

if alumno_select != st.session_state.alumno_select_prev:
    st.session_state.alumno_select_prev = alumno_select

    if alumno_select != "Ninguno":
        alumno_id = dict_alumnos.get(alumno_select)

        if alumno_id:
            st.session_state.view = "alumno"
            st.session_state.alumno_id = alumno_id
            st.session_state.alumno_nombre = alumno_select
            st.rerun()


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
    c1.metric("Pagos", cursor.fetchone()[0])

    cursor.execute("SELECT COALESCE(SUM(monto),0) FROM materiales")
    c2.metric("Materiales", cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM cuotas WHERE estado='PENDIENTE'")
    c3.metric("Cuotas pendientes", cursor.fetchone()[0])

    st.divider()

    st.subheader("Alumnos")

    for alumno_id, nombre in alumnos:

        data = deuda_detallada(alumno_id)

        cuota = data["cuota"]
        material = data["material"]
        horno = data["horno"]
        total = data["total"]

        with st.container():
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
                        💳 Cuotas: <b>${cuota}</b><br>
                        🧱 Materiales: <b>${material}</b><br>
                        🔥 Horno: <b>${horno}</b><br>
                        💰 Total: <b>${total}</b>
                    </p>
                </div>
            """, unsafe_allow_html=True)

            if st.button(f"Ver {nombre}", key=f"view_{alumno_id}"):
                st.session_state.view = "alumno"
                st.session_state.alumno_id = alumno_id
                st.session_state.alumno_nombre = nombre
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

    cuota = data["cuota"]
    material = data["material"]
    horno_base = data["horno"]

    horno = 25000 if st.session_state.horno_toggle else 0
    total = cuota + material + horno

    col1, col2, col3 = st.columns(3)

    col1.metric("Cuotas", f"${cuota}")
    col2.metric("Materiales", f"${material}")
    col3.metric("Total", f"${total}")

    st.checkbox("🔥 Incluir horno ($25.000)", key="horno_toggle")

    st.button("➕ Agregar horno", on_click=lambda: (
        registrar_horno(alumno_id, 25000),
        st.rerun()
    ))

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💳 Pago")
        monto = st.number_input("Monto pago", min_value=0, step=1000)
        medio = st.selectbox("Medio", ["Efectivo", "Transferencia", "Tarjeta"])

        if st.button("Confirmar pago"):
            registrar_pago(alumno_id, monto, medio)
            st.rerun()

    with col2:
        st.subheader("🧱 Materiales")
        desc = st.text_input("Descripción")
        monto_mat = st.number_input("Monto material", min_value=0, step=1000)

        if st.button("Agregar material"):
            registrar_material(alumno_id, desc, monto_mat)
            st.rerun()

    st.divider()

    st.subheader("Historial")

    historial = obtener_historial(alumno_id)
    df = pd.DataFrame(historial, columns=["Fecha", "Tipo", "Detalle", "Monto"])
    st.dataframe(df, use_container_width=True)


# =========================
# CLOSE DB
# =========================
conn.close()

st.caption("Sistema Escuela Cerámica")