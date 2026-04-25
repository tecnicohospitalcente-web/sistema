import streamlit as st
import pandas as pd
from conexao import supabase

def tela():
    st.title("👨‍💼 Funcionários")

    nome = st.text_input("Nome")
    cargo = st.text_input("Cargo")

    if st.button("Cadastrar"):
        supabase.table("funcionarios").insert({
            "nome": nome,
            "cargo": cargo
        }).execute()

    dados = supabase.table("funcionarios").select("*").execute()
    st.dataframe(pd.DataFrame(dados.data or []))