import streamlit as st
import pandas as pd
from conexao import supabase
import plotly.express as px

# =========================
# 🧠 SAFE FETCH (ANTI ERRO)
# =========================
@st.cache_data(ttl=60)
def safe_fetch(table):
    try:
        res = supabase.table(table).select("*").execute()

        if res is None or not hasattr(res, "data"):
            return pd.DataFrame()

        return pd.DataFrame(res.data or [])

    except:
        return pd.DataFrame()


# =========================
# 🖥️ TELA
# =========================
def tela():

    st.title("📊 Dashboard Hospitalar")

    # =========================
    # 📥 DADOS
    # =========================
    df_pagar = safe_fetch("contas_pagar")
    df_receber = safe_fetch("contas_receber")
    df_leitos = safe_fetch("leitos")
    df_internacoes = safe_fetch("internacoes")
    df_pacientes = safe_fetch("pacientes")

    # =========================
    # 💰 FINANCEIRO
    # =========================
    total_pagar = df_pagar["valor"].sum() if "valor" in df_pagar else 0
    total_receber = df_receber["valor"].sum() if "valor" in df_receber else 0
    saldo = total_receber - total_pagar

    # =========================
    # 🏥 LEITOS
    # =========================
    total_leitos = len(df_leitos)

    ocupados = 0
    if not df_internacoes.empty and "status" in df_internacoes:
        ocupados = len(df_internacoes[df_internacoes["status"] == "ativo"])

    livres = total_leitos - ocupados
    taxa = (ocupados / total_leitos * 100) if total_leitos > 0 else 0

    # =========================
    # 👤 PACIENTES
    # =========================
    total_pacientes = len(df_pacientes)

    # =========================
    # 📊 CARDS
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Saldo", f"R$ {saldo:,.2f}")
    col2.metric("🏥 Ocupação", f"{ocupados}/{total_leitos}")
    col3.metric("📈 Taxa", f"{taxa:.1f}%")
    col4.metric("👤 Pacientes", total_pacientes)

    st.markdown("---")

    # =========================
    # 📈 RECEITA x DESPESA
    # =========================
    st.subheader("💰 Receita x Despesa")

    if not df_receber.empty or not df_pagar.empty:

        df_list = []

        if not df_receber.empty and "valor" in df_receber:
            df_receber["tipo"] = "Receita"
            df_list.append(df_receber)

        if not df_pagar.empty and "valor" in df_pagar:
            df_pagar["tipo"] = "Despesa"
            df_list.append(df_pagar)

        if df_list:
            df = pd.concat(df_list)

            if "created_at" in df:
                df["data"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date
            else:
                df["data"] = pd.Timestamp.today().date()

            df_group = df.groupby(["data", "tipo"])["valor"].sum().reset_index()

            fig = px.line(df_group, x="data", y="valor", color="tipo")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 🏥 LEITOS
    # =========================
    st.subheader("🏥 Situação dos Leitos")

    df_leitos_status = pd.DataFrame({
        "Status": ["Ocupados", "Livres"],
        "Quantidade": [ocupados, livres]
    })

    if not df_leitos_status.empty:
        fig2 = px.pie(df_leitos_status, names="Status", values="Quantidade")
        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🏥 FATURAMENTO
    # =========================
    st.subheader("🏥 Faturamento por Tipo")

    if not df_receber.empty and "descricao" in df_receber and "valor" in df_receber:

        df_setor = df_receber.groupby("descricao")["valor"].sum().reset_index()

        fig3 = px.bar(df_setor, x="descricao", y="valor")
        st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # 📋 ÚLTIMOS REGISTROS
    # =========================
    st.subheader("📋 Últimos Registros")

    if not df_receber.empty:
        st.write("📥 Receitas")
        st.dataframe(df_receber.tail(5))

    if not df_pagar.empty:
        st.write("📤 Despesas")
        st.dataframe(df_pagar.tail(5))
