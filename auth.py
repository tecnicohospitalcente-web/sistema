import streamlit as st
from conexao import supabase, safe_query
from streamlit_local_storage import LocalStorage

localStorage = LocalStorage()

# =========================
# 🧠 INICIALIZAR SESSÃO
# =========================
def init_session():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = None

    if "tipo" not in st.session_state:
        st.session_state.tipo = None

    if "session" not in st.session_state:
        st.session_state.session = None


# =========================
# 🔐 LOGIN
# =========================
def login(username, senha):
    try:
        res = safe_query(lambda: supabase.table("usuarios")
                         .select("*")
                         .eq("username", username)
                         .execute())

        if not res or not res.data:
            return False

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

            return True

        return False

    except Exception as e:
        st.error(f"Erro no login: {e}")
        return False


# =========================
# 🔄 RESTAURAR SESSÃO
# =========================
def restaurar_sessao():
    try:
        saved = localStorage.getItem("session")

        if not saved:
            return

        supabase.auth.set_session(
            saved["access_token"],
            saved["refresh_token"]
        )

        user = supabase.auth.get_user()

        if not user.user:
            raise Exception("Sessão inválida")

        email = user.user.email

        res = safe_query(lambda: supabase.table("usuarios")
                         .select("*")
                         .eq("email", email)
                         .execute())

        if not res or not res.data:
            raise Exception("Usuário não encontrado")

        usuario_db = res.data[0]

        st.session_state.logado = True
        st.session_state.usuario = usuario_db["nome"]
        st.session_state.tipo = usuario_db["tipo"]
        st.session_state.session = saved

    except:
        logout()


# =========================
# 🔁 MANTER SESSÃO
# =========================
def manter_sessao():
    if st.session_state.get("session"):
        try:
            supabase.auth.set_session(
                st.session_state.session["access_token"],
                st.session_state.session["refresh_token"]
            )
        except:
            logout()


# =========================
# 🚪 LOGOUT
# =========================
def logout():
    try:
        localStorage.deleteItem("session")
    except:
        pass

    st.session_state.clear()
    st.rerun()
