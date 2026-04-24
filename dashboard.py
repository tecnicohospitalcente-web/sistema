import streamlit as st
import pandas as pd
from conexao import supabase

def tela():
    st.title("📊 Dashboard")

    pagar = supabase.table("contas_pagar").select("*").execute()
    receber = supabase.table("contas_receber").select("*").execute()

    df_pagar = pd.DataFrame(pagar.data or [])
    df_receber = pd.DataFrame(receber.data or [])

    total_pagar = df_pagar["valor"].sum() if not df_pagar.empty else 0
    total_receber = df_receber["valor"].sum() if not df_receber.empty else 0
    saldo = total_receber - total_pagar

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class='card'><h4>💸 Pagar</h4><h2>R$ {total_pagar:.2f}</h2></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='card'><h4>💵 Receber</h4><h2>R$ {total_receber:.2f}</h2></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<div class='card'><h4>💰 Saldo</h4><h2>R$ {saldo:.2f}</h2></div>", unsafe_allow_html=True)