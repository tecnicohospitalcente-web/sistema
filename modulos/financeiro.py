import streamlit as st
import pandas as pd
from conexao import supabase, safe_query

# =========================
# 💰 GERAR FATURAMENTO INTELIGENTE
# =========================
def gerar_faturamento(paciente_id, tipo, valor):

    try:
        supabase.table("contas_receber").insert({
            "paciente_id": paciente_id,
            "descricao": tipo,
            "valor": valor,
            "status": "pendente"
        }).execute()

    except Exception as e:
        st.error(f"Erro faturamento: {e}")


# =========================
# 📥 CARREGAR DADOS
# =========================
@st.cache_data(ttl=5)
def carregar_receber():
    res = (lambda: supabase.table("contas_receber")
                     .select("*, pacientes(nome)")
                     .execute())
    return pd.DataFrame(res.data or [])


@st.cache_data(ttl=5)
def carregar_pagar():
    res = (lambda: supabase.table("contas_pagar")
                     .select("*")
                     .execute())
    return pd.DataFrame(res.data or [])


# =========================
# 💸 AÇÕES
# =========================
def pagar_conta(id):
    supabase.table("contas_pagar").update({
        "status": "pago"
    }).eq("id", id).execute()

    st.cache_data.clear()


def receber_conta(id):
    supabase.table("contas_receber").update({
        "status": "recebido"
    }).eq("id", id).execute()

    st.cache_data.clear()


# =========================
# 📦 REGISTRAR COMPRA (ESTOQUE/EMPRESA)
# =========================
def registrar_compra():

    st.subheader("📦 Nova Despesa / Compra")

    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)
    tipo = st.selectbox("Tipo", ["Medicamento", "Equipamento", "Serviço", "Outros"])

    if st.button("Salvar compra"):

        if not descricao or valor <= 0:
            st.warning("Preencha os dados")
            return

        supabase.table("contas_pagar").insert({
            "descricao": f"{tipo} - {descricao}",
            "valor": valor,
            "status": "pendente"
        }).execute()

        st.success("Compra registrada")
        st.cache_data.clear()
        st.rerun()


# =========================
# 📥 RECEBER (COM PACIENTE)
# =========================
def tabela_receber(df):

    st.subheader("📥 Contas a Receber")

    if df.empty:
        st.info("Sem dados")
        return

    for _, row in df.iterrows():

        paciente = ""
        if isinstance(row.get("pacientes"), dict):
            paciente = row["pacientes"].get("nome", "")

        col1, col2, col3, col4, col5 = st.columns([3,2,2,2,2])

        col1.write(f"👤 {paciente}")
        col2.write(row["descricao"])
        col3.write(f"R$ {row['valor']:.2f}")
        col4.write(row["status"])

        if row["status"] != "recebido":
            if col5.button("Receber", key=f"rec_{row['id']}"):
                receber_conta(row["id"])
                st.rerun()


# =========================
# 📤 PAGAR
# =========================
def tabela_pagar(df):

    st.subheader("📤 Contas a Pagar")

    if df.empty:
        st.info("Sem dados")
        return

    for _, row in df.iterrows():

        col1, col2, col3, col4 = st.columns([3,2,2,2])

        col1.write(row["descricao"])
        col2.write(f"R$ {row['valor']:.2f}")
        col3.write(row["status"])

        if row["status"] != "pago":
            if col4.button("Pagar", key=f"pag_{row['id']}"):
                pagar_conta(row["id"])
                st.rerun()


# =========================
# 📊 DASHBOARD FINANCEIRO REAL
# =========================
def dashboard(df_receber, df_pagar):

    st.subheader("📊 Visão Geral Financeira")

    total_receber = df_receber["valor"].sum() if not df_receber.empty else 0
    total_pagar = df_pagar["valor"].sum() if not df_pagar.empty else 0

    recebido = df_receber[df_receber["status"] == "recebido"]["valor"].sum() if not df_receber.empty else 0
    pago = df_pagar[df_pagar["status"] == "pago"]["valor"].sum() if not df_pagar.empty else 0

    saldo = recebido - pago

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Total Receber", f"R$ {total_receber:,.2f}")
    col2.metric("💸 Total Pagar", f"R$ {total_pagar:,.2f}")
    col3.metric("✅ Recebido", f"R$ {recebido:,.2f}")
    col4.metric("🏦 Saldo Real", f"R$ {saldo:,.2f}")

    st.markdown("---")

    # 📊 GRÁFICO POR TIPO
    if not df_receber.empty:

        df_receber["tipo"] = df_receber["descricao"]

        resumo = df_receber.groupby("tipo")["valor"].sum()

        st.bar_chart(resumo)


# =========================
# 📈 RELATÓRIO COMPLETO
# =========================
def relatorio(df_receber, df_pagar):

    st.subheader("📈 Relatório Completo")

    lucro = (
        df_receber[df_receber["status"] == "recebido"]["valor"].sum()
        -
        df_pagar[df_pagar["status"] == "pago"]["valor"].sum()
    )

    st.metric("Lucro / Prejuízo", f"R$ {lucro:,.2f}")

    st.markdown("### 📥 Receitas")
    st.dataframe(df_receber)

    st.markdown("### 📤 Despesas")
    st.dataframe(df_pagar)


# =========================
# 🖥️ TELA PRINCIPAL
# =========================
def tela():

    st.title("💰 Sistema Financeiro Hospitalar")

    df_receber = carregar_receber()
    df_pagar = carregar_pagar()

    aba1, aba2, aba3, aba4 = st.tabs([
        "📊 Dashboard",
        "📥 Receber",
        "📤 Pagar",
        "📈 Relatórios"
    ])

    # 📊 DASHBOARD
    with aba1:
        dashboard(df_receber, df_pagar)

    # 📥 RECEBER
    with aba2:
        tabela_receber(df_receber)

    # 📤 PAGAR
    with aba3:
        registrar_compra()
        st.markdown("---")
        tabela_pagar(df_pagar)

    # 📈 RELATÓRIO
    with aba4:
        relatorio(df_receber, df_pagar)