import streamlit as st
from conexao import supabase, safe_query
from streamlit_local_storage import LocalStorage

localStorage = LocalStorage()

# =========================
# 🧠 INICIALIZAR SESSÃO
# =========================
def init_session():

    st.session_state.setdefault("logado", False)
    st.session_state.setdefault("usuario", None)
    st.session_state.setdefault("tipo", None)
    st.session_state.setdefault("session", None)


# =========================
# 🔐 LOGIN
# =========================
def login(username, senha):

    try:
        # 🔎 busca usuário
        res = safe_query(lambda: supabase.table("usuarios")
                         .select("*")
                         .eq("username", username)
                         .execute())

        if not res or not res.data:
            st.warning("Usuário não encontrado")
            return False

        user_db = res.data[0]

        # 🔐 login no auth
        auth = supabase.auth.sign_in_with_password({
            "email": user_db["email"],
            "password": senha
        })

        if auth.session:

            session_data = {
                "access_token": auth.session.access_token,
                "refresh_token": auth.session.refresh_token
            }

            # 💾 salva sessão
            st.session_state.logado = True
            st.session_state.usuario = user_db.get("nome")
            st.session_state.tipo = user_db.get("tipo")
            st.session_state.session = session_data

            localStorage.setItem("session", session_data)

            return True

        st.error("Senha incorreta")
        return False

    except Exception as e:
        st.error(f"Erro no login: {e}")
        return False


# =========================
# 🔄 RESTAURAR SESSÃO
# =========================
def restaurar_sessao():

    saved = localStorage.getItem("session")

    if not saved:
        return

    try:
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
        st.session_state.usuario = usuario_db.get("nome")
        st.session_state.tipo = usuario_db.get("tipo")
        st.session_state.session = saved

    except Exception:
        logout()


# =========================
# 🔁 MANTER SESSÃO VIVA
# =========================
def manter_sessao():

    if not st.session_state.get("session"):
        return

    try:
        supabase.auth.set_session(
            st.session_state.session["access_token"],
            st.session_state.session["refresh_token"]
        )

    except Exception:
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


# =========================
# 🔐 PROTEGER TELA
# =========================
def require_login():

    if not st.session_state.get("logado"):
        st.warning("🔐 Faça login para continuar")
        st.stop()


# =========================
# 🔒 PERMISSÃO
# =========================
def require_role(tipos):

    if st.session_state.get("tipo") not in tipos:
        st.warning("🚫 Acesso restrito")
        st.stop()