import streamlit as st
import pandas as pd
from conexao import supabase

# =========================
# 🧠 CRIAR USUÁRIO
# =========================
def criar_usuario(email, senha, username, nome, tipo):

    check = supabase.table("usuarios").select("*").eq("username", username).execute()

    if check.data:
        st.warning("⚠️ Usuário já existe")
        return False

    try:
        with st.spinner("Criando usuário..."):

            auth = supabase.auth.sign_up({
                "email": email,
                "password": senha
            })

            if not auth.user:
                st.error("Erro ao criar usuário no Auth")
                return False

            supabase.table("usuarios").insert({
                "id": auth.user.id,
                "email": email,
                "username": username,
                "nome": nome,
                "tipo": tipo
            }).execute()

            return True

    except Exception as e:
        st.error(f"Erro: {e}")
        return False


# =========================
# 🗑️ DELETAR USUÁRIO
# =========================
def deletar_usuario(user_id):
    try:
        supabase.table("usuarios").delete().eq("id", user_id).execute()
        st.success("Usuário removido")
    except Exception as e:
        st.error(f"Erro: {e}")


# =========================
# 🖥️ TELA
# =========================
def tela():

    # 🔥 verifica usuários
    dados = supabase.table("usuarios").select("*").execute()
    tem_usuario = len(dados.data) > 0 if dados.data else False

    # 🔐 BLOQUEIO CORRETO
    if tem_usuario and st.session_state.get("tipo") != "admin":
        st.warning("🚫 Acesso restrito")
        st.stop()

    st.title("👥 Gestão de Usuários")
    st.caption("Controle de acesso do sistema")

    aba = st.tabs(["Cadastrar", "Lista"])

    # =========================
    # ➕ CADASTRO
    # =========================
    with aba[0]:

        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome completo")
            username = st.text_input("Usuário")

        with col2:
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")

        # 🔥 primeiro usuário
        if not tem_usuario:
            tipo = "admin"
            st.info("👑 Primeiro usuário será administrador")
        else:
            tipo = st.selectbox(
                "Tipo",
                ["admin", "financeiro", "estoque", "rh"]
            )

        if st.button("💾 Criar Usuário", use_container_width=True):

            if not nome or not username or not email or not senha:
                st.warning("Preencha todos os campos")
            else:
                sucesso = criar_usuario(email, senha, username, nome, tipo)

                if sucesso:
                    st.success("Usuário criado!")
                    st.rerun()

    # =========================
    # 📋 LISTA
    # =========================
    with aba[1]:

        dados = supabase.table("usuarios").select("*").execute()
        df = pd.DataFrame(dados.data or [])

        if df.empty:
            st.info("Nenhum usuário cadastrado")
        else:
            for _, row in df.iterrows():

                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                col1.write(row.get("nome", ""))
                col2.write(row.get("username", ""))
                col3.write(row.get("tipo", ""))

                with col4:
                    if st.button("❌", key=row["id"]):
                        deletar_usuario(row["id"])
                        st.rerun()