import streamlit as st
import pandas as pd
from conexao import supabase

def tela():
    st.header("📦 Estoque")

    nome = st.text_input("Produto")
    qtd = st.number_input("Quantidade", min_value=0)
    validade = st.date_input("Validade")

    if st.button("Salvar produto"):
        supabase.table("estoque").insert({
            "nome_produto": nome,
            "quantidade": qtd,
            "validade": str(validade)
        }).execute()

    dados = supabase.table("estoque").select("*").execute()
    st.dataframe(pd.DataFrame(dados.data or []))