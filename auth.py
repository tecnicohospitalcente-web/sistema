import streamlit as st
from conexao import supabase, safe_query

# =========================
# 🧠 INIT SESSION (SEMPRE EXISTE)
# =========================
def init_session():
    defaults = {
        "logado": False,
        "usuario": None,
        "tipo": None,
        "session": None
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


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

        # 🔐 salva somente tokens (evita erro JSON)
        session_data = {
            "access_token": auth.session.access_token,
            "refresh_token": auth.session.refresh_token
        }

        st.session_state["logado"] = True
        st.session_state["usuario"] = user_db["nome"]
        st.session_state["tipo"] = user_db["tipo"]
        st.session_state["session"] = session_data

        return True

    except Exception as e:
        st.error(f"Erro login: {e}")
        return False


# =========================
# 🔄 RESTAURAR SESSÃO (SEM LOCAL STORAGE BUG)
# =========================
def restaurar_sessao():
    try:
        # 🔥 usa sessão do próprio Supabase
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

            st.session_state["logado"] = True
            st.session_state["usuario"] = u["nome"]
            st.session_state["tipo"] = u["tipo"]

    except Exception as e:
        print("Erro restaurar:", e)


# =========================
# 🔁 MANTER SESSÃO
# =========================
def manter_sessao():
    try:
        user = supabase.auth.get_user()

        if user and user.user:
            return

        # 🔥 se perdeu sessão → desloga
        logout()

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

    for k in list(st.session_state.keys()):
        del st.session_state[k]

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