import streamlit as st
import pandas as pd
from conexao import supabase

def tela():
    st.title("💰 Financeiro")

    aba = st.tabs(["Pagar", "Receber"])

    with aba[0]:
        st.markdown("### 💸 Novo Lançamento")

        col1, col2, col3 = st.columns(3)

        with col1:
            desc = st.text_input("Descrição")

        with col2:
            valor = st.number_input("Valor", min_value=0.0)

        with col3:
            data = st.date_input("Data")

        if st.button("💾 Salvar", use_container_width=True):
            supabase.table("contas_pagar").insert({
                "descricao": desc,
                "valor": valor,
                "data_vencimento": str(data),
                "status": "pendente"
            }).execute()
            st.success("Salvo!")

        dados = supabase.table("contas_pagar").select("*").execute()
        st.dataframe(pd.DataFrame(dados.data or []), use_container_width=True)

    with aba[1]:
        st.markdown("### 💵 Nova Receita")

        col1, col2, col3 = st.columns(3)

        with col1:
            desc = st.text_input("Descrição ", key="r")

        with col2:
            valor = st.number_input("Valor ", min_value=0.0, key="r2")

        with col3:
            data = st.date_input("Data ", key="r3")

        if st.button("💾 Salvar Receita", use_container_width=True):
            supabase.table("contas_receber").insert({
                "descricao": desc,
                "valor": valor,
                "data_recebimento": str(data),
                "status": "pendente"
            }).execute()
            st.success("Salvo!")

        dados = supabase.table("contas_receber").select("*").execute()
        st.dataframe(pd.DataFrame(dados.data or []), use_container_width=True)