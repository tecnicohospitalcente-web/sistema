import streamlit as st
from conexao import supabase, safe_query

def init_session():
    st.session_state.setdefault("logado", False)
    st.session_state.setdefault("usuario", None)
    st.session_state.setdefault("tipo", None)

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
        st.error(f"Erro login: {e}")
        return False


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

        if res and res.data:
            u = res.data[0]
            st.session_state.logado = True
            st.session_state.usuario = u["nome"]
            st.session_state.tipo = u["tipo"]

    except:
        pass


def logout():
    try:
        supabase.auth.sign_out()
    except:
        pass

    st.session_state.clear()
    st.rerun()


def require_login():
    if not st.session_state.get("logado"):
        st.warning("🔐 Faça login")
        st.stop()


def require_role(tipos):
    if st.session_state.get("tipo") not in tipos:
        st.warning("🚫 Acesso restrito")
        st.stop()
