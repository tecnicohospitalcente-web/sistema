import streamlit as st
from conexao import supabase, safe_query

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

        if auth.user:
            st.session_state.logado = True
            st.session_state.usuario = user_db["nome"]
            st.session_state.tipo = user_db["tipo"]

            return True

        return False

    except Exception as e:
        st.error(f"Erro no login: {e}")
        return False


# =========================
# 🔄 RESTAURAR SESSÃO (Cloud-safe)
# =========================
def restaurar_sessao():
    try:
        user = supabase.auth.get_user()

        if not user or not user.user:
            return

        email = user.user.email

        res = safe_query(lambda: supabase.table("usuarios")
                         .select("*")
                         .eq("email", email)
                         .execute())

        if not res or not res.data:
            return

        usuario_db = res.data[0]

        st.session_state.logado = True
        st.session_state.usuario = usuario_db["nome"]
        st.session_state.tipo = usuario_db["tipo"]

    except:
        pass


# =========================
# 🔁 MANTER SESSÃO
# =========================
def manter_sessao():
    try:
        supabase.auth.get_user()
    except:
        logout()


# =========================
# 🚪 LOGOUT
# =========================
def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass

    st.session_state.clear()
    st.rerun()
