import streamlit as st
import pandas as pd
from conexao import supabase, safe_query

# =========================
# 💰 GERAR FATURAMENTO
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
# 📥 CONTAS A RECEBER
# =========================
@st.cache_data(ttl=5)
def carregar_receber():
    res = safe_query(lambda: supabase.table("contas_receber")
                     .select("*")
                     .execute())
    return pd.DataFrame(res.data or [])


# =========================
# 📤 CONTAS A PAGAR
# =========================
@st.cache_data(ttl=5)
def carregar_pagar():
    res = safe_query(lambda: supabase.table("contas_pagar")
                     .select("*")
                     .execute())
    return pd.DataFrame(res.data or [])


# =========================
# 💸 PAGAR CONTA
# =========================
def pagar_conta(id):
    supabase.table("contas_pagar").update({
        "status": "pago"
    }).eq("id", id).execute()

    st.cache_data.clear()


# =========================
# 💰 RECEBER CONTA
# =========================
def receber_conta(id):
    supabase.table("contas_receber").update({
        "status": "recebido"
    }).eq("id", id).execute()

    st.cache_data.clear()


# =========================
# 📦 REGISTRAR COMPRA
# =========================
def registrar_compra():

    st.subheader("📦 Registrar Compra")

    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)

    if st.button("Salvar compra"):

        if not descricao or valor <= 0:
            st.warning("Preencha os dados")
            return

        supabase.table("contas_pagar").insert({
            "descricao": descricao,
            "valor": valor,
            "status": "pendente"
        }).execute()

        st.success("Compra registrada")
        st.cache_data.clear()
        st.rerun()


# =========================
# 📄 TABELAS
# =========================
def tabela_receber(df):

    st.subheader("📥 Contas a Receber")

    if df.empty:
        st.info("Sem dados")
        return

    for _, row in df.iterrows():

        col1, col2, col3, col4 = st.columns([3,2,2,2])

        col1.write(row["descricao"])
        col2.write(f"R$ {row['valor']:.2f}")
        col3.write(row["status"])

        if row["status"] != "recebido":
            if col4.button("Receber", key=f"rec_{row['id']}"):
                receber_conta(row["id"])
                st.rerun()


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
# 📈 RELATÓRIO
# =========================
def relatorio(df_receber, df_pagar):

    st.subheader("📊 Relatório Financeiro")

    if df_receber.empty and df_pagar.empty:
        st.info("Sem dados")
        return

    total_receber = df_receber["valor"].sum() if not df_receber.empty else 0
    total_pagar = df_pagar["valor"].sum() if not df_pagar.empty else 0

    lucro = total_receber - total_pagar

    st.metric("Lucro / Prejuízo", f"R$ {lucro:,.2f}")

    st.markdown("### 📥 Receitas")
    st.dataframe(df_receber)

    st.markdown("### 📤 Despesas")
    st.dataframe(df_pagar)


# =========================
# 🖥️ TELA PRINCIPAL
# =========================
def tela():

    st.title("💰 Financeiro")

    df_receber = carregar_receber()
    df_pagar = carregar_pagar()

    aba1, aba2, aba3,  = st.tabs([
        "📥 Receber",
        "📤 Pagar",
        "📈 Relatórios"
    ])


    # 📥 RECEBER
    with aba1:
        tabela_receber(df_receber)

    # 📤 PAGAR
    with aba2:
        registrar_compra()
        st.markdown("---")
        tabela_pagar(df_pagar)

    # 📈 RELATÓRIO
    with aba3:
        relatorio(df_receber, df_pagar)