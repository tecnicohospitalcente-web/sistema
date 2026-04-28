import streamlit as st
from conexao import supabase, safe_query
from datetime import datetime, timedelta

# ⏱ tempo de sessão (minutos)
SESSION_TIMEOUT = 30


# =========================
# 🧠 INIT SESSION
# =========================
def init_session():
    defaults = {
        "logado": False,
        "usuario": None,
        "tipo": None,
        "last_activity": None
    }

    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


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

        if not auth or not auth.user:
            return False

        # 🔥 salva sessão leve
        st.session_state["logado"] = True
        st.session_state["usuario"] = user_db["nome"]
        st.session_state["tipo"] = user_db["tipo"]
        st.session_state["last_activity"] = datetime.now()

        return True

    except Exception as e:
        st.error(f"Erro login: {e}")
        return False


# =========================
# 🔄 RESTAURAR SESSÃO
# =========================
def restaurar_sessao():
    if st.session_state.get("logado"):
        return

    try:
        user = supabase.auth.get_user()

        if not user or not user.user:
            return

        email = user.user.email

        res = safe_query(lambda: supabase.table("usuarios")
                         .select("nome,tipo,email")
                         .eq("email", email)
                         .execute())

        if res and res.data:
            u = res.data[0]

            st.session_state["logado"] = True
            st.session_state["usuario"] = u["nome"]
            st.session_state["tipo"] = u["tipo"]
            st.session_state["last_activity"] = datetime.now()

    except:
        pass


# =========================
# 🔁 MANTER SESSÃO + AUTO LOGOUT
# =========================
def manter_sessao():
    try:
        if not st.session_state.get("logado"):
            return

        agora = datetime.now()
        ultima = st.session_state.get("last_activity")

        if ultima and (agora - ultima > timedelta(minutes=SESSION_TIMEOUT)):
            st.warning("Sessão expirada 🔐")
            logout()

        # 🔥 atualiza atividade
        st.session_state["last_activity"] = agora

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