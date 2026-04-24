import streamlit as st
import pandas as pd
from conexao import supabase

def tela():
    st.title("🧾 Convênios")

    nome = st.text_input("Nome")

    if st.button("Salvar"):
        supabase.table("convenios").insert({
            "nome": nome
        }).execute()

    dados = supabase.table("convenios").select("*").execute()
    st.dataframe(pd.DataFrame(dados.data or []))