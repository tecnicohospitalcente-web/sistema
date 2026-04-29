import streamlit as st
import pandas as pd
from conexao import supabase
import plotly.express as px

def tela():
    st.title("📊 Dashboard Geral Hospitalar")

    # =========================
    # 🔄 BUSCAR DADOS
    # =========================
    pagar = supabase.table("contas_pagar").select("*").execute()
    receber = supabase.table("contas_receber").select("*").execute()
    leitos = supabase.table("leitos").select("*").execute()
    internacoes = supabase.table("internacoes").select("*").execute()
    pacientes = supabase.table("pacientes").select("*").execute()

    df_pagar = pd.DataFrame(pagar.data or [])
    df_receber = pd.DataFrame(receber.data or [])
    df_leitos = pd.DataFrame(leitos.data or [])
    df_internacoes = pd.DataFrame(internacoes.data or [])
    df_pacientes = pd.DataFrame(pacientes.data or [])

    # =========================
    # 💰 FINANCEIRO
    # =========================
    total_pagar = df_pagar["valor"].sum() if not df_pagar.empty else 0
    total_receber = df_receber["valor"].sum() if not df_receber.empty else 0
    saldo = total_receber - total_pagar

    # =========================
    # 🏥 LEITOS
    # =========================
    total_leitos = len(df_leitos)
    ocupados = len(df_internacoes[df_internacoes["status"] == "ativo"]) if not df_internacoes.empty else 0
    livres = total_leitos - ocupados

    taxa_ocupacao = (ocupados / total_leitos * 100) if total_leitos > 0 else 0

    # =========================
    # 👤 PACIENTES
    # =========================
    total_pacientes = len(df_pacientes)

    # =========================
    # 📊 CARDS PRINCIPAIS
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Saldo", f"R$ {saldo:,.2f}")
    col2.metric("🏥 Ocupação", f"{ocupados}/{total_leitos}")
    col3.metric("📈 Taxa", f"{taxa_ocupacao:.1f}%")
    col4.metric("👤 Pacientes", total_pacientes)

    st.markdown("---")

    # =========================
    # 📈 FINANCEIRO (GRÁFICO)
    # =========================
    st.subheader("💰 Receita x Despesa")

    if not df_receber.empty or not df_pagar.empty:

        df_receber["tipo"] = "Receita"
        df_pagar["tipo"] = "Despesa"

        df = pd.concat([df_receber, df_pagar], ignore_index=True)

        if "created_at" in df.columns:
            df["data"] = pd.to_datetime(df["created_at"]).dt.date
        else:
            df["data"] = pd.Timestamp.today().date()

        df_group = df.groupby(["data", "tipo"])["valor"].sum().reset_index()

        fig = px.line(df_group, x="data", y="valor", color="tipo")
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🏥 OCUPAÇÃO DE LEITOS
    # =========================
    st.subheader("🏥 Situação dos Leitos")

    df_leitos_status = pd.DataFrame({
        "Status": ["Ocupados", "Livres"],
        "Quantidade": [ocupados, livres]
    })

    fig2 = px.pie(df_leitos_status, names="Status", values="Quantidade")
    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🏥 FATURAMENTO POR SETOR
    # =========================
    st.subheader("🏥 Faturamento por Tipo")

    if not df_receber.empty:

        df_setor = df_receber.groupby("descricao")["valor"].sum().reset_index()

        fig3 = px.bar(df_setor, x="descricao", y="valor")
        st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # 📋 TABELA RESUMO
    # =========================
    st.subheader("📋 Últimos Registros")

    if not df_receber.empty:
        st.dataframe(df_receber.tail(10))

    if not df_pagar.empty:
        st.dataframe(df_pagar.tail(10))