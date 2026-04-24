import streamlit as st
from conexao import supabase
from streamlit_local_storage import LocalStorage

# módulos
from modulos import financeiro, dashboard, rh, estoque, convenios, usuarios

st.set_page_config(layout="wide")

localStorage = LocalStorage()

# =========================
# 🧠 ESTADO INICIAL
# =========================
def init_state():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if "tipo" not in st.session_state:
        st.session_state.tipo = None

    if "session" not in st.session_state:
        st.session_state.session = None

init_state()

# =========================
# 🧹 LOGOUT SEGURO
# =========================
def logout():
    keys = ["logado", "usuario", "tipo", "session"]

    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

    try:
        if localStorage.getItem("session"):
            localStorage.deleteItem("session")
    except:
        pass

    st.rerun()

# =========================
# 🔄 RESTAURAR SESSÃO
# =========================
def restaurar_sessao():

    if st.session_state.logado:
        return

    saved = localStorage.getItem("session")

    if not saved:
        return

    try:
        supabase.auth.set_session(
            saved["access_token"],
            saved["refresh_token"]
        )

        user = supabase.auth.get_user()

        if user.user:
            email = user.user.email

            res = supabase.table("usuarios").select("*").eq("email", email).execute()

            if res.data:
                u = res.data[0]

                st.session_state.logado = True
                st.session_state.usuario = u["nome"]
                st.session_state.tipo = u["tipo"]
                st.session_state.session = saved

    except:
        try:
            localStorage.deleteItem("session")
        except:
            pass

restaurar_sessao()

# =========================
# 🔐 LOGIN
# =========================
def login(username, senha):

    try:
        res = supabase.table("usuarios").select("*").eq("username", username).execute()

        if not res.data:
            return None

        user_db = res.data[0]

        auth = supabase.auth.sign_in_with_password({
            "email": user_db["email"],
            "password": senha
        })

        if auth.session:

            session_data = {
                "access_token": auth.session.access_token,
                "refresh_token": auth.session.refresh_token
            }

            st.session_state.logado = True
            st.session_state.usuario = user_db["nome"]
            st.session_state.tipo = user_db["tipo"]
            st.session_state.session = session_data

            localStorage.setItem("session", session_data)

            return user_db

    except Exception as e:
        st.error(f"Erro no login: {e}")

    return None

# =========================
# 🔐 TELA LOGIN
# =========================
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if login(user, senha):
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.stop()

# =========================
# 🎨 NAVBAR
# =========================
col1, col2, col3 = st.columns([1, 6, 2])

with col1:
    try:
        st.image("logo.png", width=70)
    except:
        st.write("🏥")

with col2:
    st.markdown("### 🏥 Sistema Hospitalar SaaS")

with col3:
    st.markdown(f"👤 **{st.session_state.usuario}**")

    if st.button("Sair"):
        logout()

st.markdown("---")

# =========================
# 📋 MENU
# =========================
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

tipo = st.session_state.tipo

colunas = st.columns(6)

if colunas[0].button("📊 Dashboard"):
    st.session_state.menu = "Dashboard"

if tipo in ["admin", "financeiro"]:
    if colunas[1].button("💰 Financeiro"):
        st.session_state.menu = "Financeiro"

if tipo in ["admin", "rh"]:
    if colunas[2].button("👨‍💼 RH"):
        st.session_state.menu = "RH"

if tipo in ["admin", "estoque"]:
    if colunas[3].button("📦 Estoque"):
        st.session_state.menu = "Estoque"

if tipo == "admin":
    if colunas[4].button("🧾 Convênios"):
        st.session_state.menu = "Convênios"

if tipo == "admin":
    if colunas[5].button("👥 Usuários"):
        st.session_state.menu = "Usuarios"

menu = st.session_state.menu

st.markdown("---")

# =========================
# 📄 ROTAS
# =========================
try:

    if menu == "Dashboard":
        dashboard.tela()

    elif menu == "Financeiro":
        financeiro.tela()

    elif menu == "RH":
        rh.tela()

    elif menu == "Estoque":
        estoque.tela()

    elif menu == "Convênios":
        convenios.tela()

    elif menu == "Usuarios":
        usuarios.tela()

except Exception as e:
    st.error(f"Erro ao carregar módulo: {e}")