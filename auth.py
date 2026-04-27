import streamlit as st
from conexao import supabase, safe_query
from streamlit_local_storage import LocalStorage

localStorage = LocalStorage()

# =========================
# 🧠 SESSION INIT
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

        if not auth or not auth.session:
            return False

        # 🔥 sessão segura (somente tokens)
        session_data = {
            "access_token": auth.session.access_token,
            "refresh_token": auth.session.refresh_token
        }

        # 💾 salva estado
        st.session_state.logado = True
        st.session_state.usuario = user_db["nome"]
        st.session_state.tipo = user_db["tipo"]
        st.session_state.session = session_data

        # 💾 salva no navegador
        try:
            localStorage.setItem("session", session_data)
        except:
            pass

        return True

    except Exception as e:
        st.error(f"Erro login: {e}")
        return False


# =========================
# 🔄 RESTAURAR SESSÃO
# =========================
def restaurar_sessao():
    try:
        saved = localStorage.getItem("session")

        # 🔥 garante formato correto
        if not saved or not isinstance(saved, dict):
            return

        if "access_token" not in saved:
            return

        supabase.auth.set_session(
            saved["access_token"],
            saved["refresh_token"]
        )

        user = supabase.auth.get_user()

        if not user or not user.user:
            return

        email = user.user.email

        res = safe_query(lambda: supabase.table("usuarios")
                         .select("*")
                         .eq("email", email)
                         .execute())

        if res and res.data:
            u = res.data[0]

            st.session_state.logado = True
            st.session_state.usuario = u["nome"]
            st.session_state.tipo = u["tipo"]
            st.session_state.session = saved

    except Exception as e:
        print("Erro restaurar sessão:", e)
        logout()


# =========================
# 🔁 MANTER SESSÃO
# =========================
def manter_sessao():
    try:
        sess = st.session_state.get("session")

        if not sess:
            return

        if "access_token" not in sess:
            return

        supabase.auth.set_session(
            sess["access_token"],
            sess["refresh_token"]
        )

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

    try:
        localStorage.deleteItem("session")
    except:
        pass

    st.session_state.clear()
    st.rerun()


# =========================
# 🔒 PROTEÇÃO
# =========================
def require_login():
    if not st.session_state.get("logado"):
        st.warning("🔐 Faça login")
        st.stop()


def require_role(tipos):
    if st.session_state.get("tipo") not in tipos:
        st.warning("🚫 Acesso restrito")
        st.stop()