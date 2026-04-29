import streamlit as st
import pandas as pd
from conexao import supabase, safe_query

# =========================
# 🔄 CARREGAR DADOS
# =========================
@st.cache_data(ttl=10)
def carregar_receber():
    res = safe_query(lambda: supabase.table("contas_receber").select("*").execute())
    return pd.DataFrame(res.data or [])

@st.cache_data(ttl=10)
def carregar_pagar():
    res = safe_query(lambda: supabase.table("contas_pagar").select("*").execute())
    return pd.DataFrame(res.data or [])

@st.cache_data(ttl=10)
def carregar_convenios():
    res = safe_query(lambda: supabase.table("convenios").select("*").execute())
    return pd.DataFrame(res.data or [])


# =========================
# 💳 FATURAR ATENDIMENTO
# =========================
def faturar():

    st.subheader("💳 Faturamento")

    tipo = st.radio("Tipo", ["Consulta", "Internação"])

    paciente = st.text_input("Paciente")
    valor = st.number_input("Valor", min_value=0.0)

    forma = st.radio("Forma", ["Particular", "Convênio"])

    convenio_id = None

    if forma == "Convênio":
        df_conv = carregar_convenios()

        if df_conv.empty:
            st.warning("Cadastre convênios primeiro")
            return

        conv = st.selectbox("Convênio", df_conv["nome"])
        convenio_id = df_conv[df_conv["nome"] == conv]["id"].values[0]

    if st.button("Gerar cobrança"):

        supabase.table("contas_receber").insert({
            "descricao": f"{tipo} - {paciente}",
            "valor": valor,
            "status": "pendente",
            "convenio_id": convenio_id
        }).execute()

        st.success("Cobrança gerada")
        st.cache_data.clear()


# =========================
# 📥 CONTAS A RECEBER
# =========================
def contas_receber():

    st.subheader("📥 Contas a Receber")

    df = carregar_receber()

    if df.empty:
        st.info("Nenhuma conta")
        return

    for _, row in df.iterrows():

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            st.write(f"**{row['descricao']}**")

        with col2:
            st.write(f"R$ {row['valor']}")

        with col3:
            if row["status"] == "pendente":
                if st.button("Receber", key=f"rec_{row['id']}"):

                    supabase.table("contas_receber") \
                        .update({"status": "pago"}) \
                        .eq("id", row["id"]) \
                        .execute()

                    st.success("Recebido")
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.success("Pago")


# =========================
# 📤 CONTAS A PAGAR
# =========================
def contas_pagar():

    st.subheader("📤 Contas a Pagar")

    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor a pagar", min_value=0.0)

    if st.button("Adicionar conta"):

        supabase.table("contas_pagar").insert({
            "descricao": descricao,
            "valor": valor,
            "status": "pendente"
        }).execute()

        st.success("Conta adicionada")
        st.cache_data.clear()

    st.markdown("---")

    df = carregar_pagar()

    for _, row in df.iterrows():

        col1, col2, col3 = st.columns([4,2,2])

        with col1:
            st.write(row["descricao"])

        with col2:
            st.write(f"R$ {row['valor']}")

        with col3:
            if row["status"] == "pendente":
                if st.button("Pagar", key=f"pag_{row['id']}"):

                    supabase.table("contas_pagar") \
                        .update({"status": "pago"}) \
                        .eq("id", row["id"]) \
                        .execute()

                    st.success("Pago")
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.success("Pago")


# =========================
# 📊 DASHBOARD FINANCEIRO
# =========================
def dashboard():

    st.subheader("📊 Dashboard Financeiro")

    df_rec = carregar_receber()
    df_pag = carregar_pagar()

    total_receber = df_rec[df_rec["status"] == "pendente"]["valor"].sum() if not df_rec.empty else 0
    total_recebido = df_rec[df_rec["status"] == "pago"]["valor"].sum() if not df_rec.empty else 0
    total_pagar = df_pag[df_pag["status"] == "pendente"]["valor"].sum() if not df_pag.empty else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("A receber", f"R$ {total_receber}")
    col2.metric("Recebido", f"R$ {total_recebido}")
    col3.metric("A pagar", f"R$ {total_pagar}")

    saldo = total_recebido - total_pagar

    st.markdown("---")
    st.subheader(f"💰 Saldo: R$ {saldo}")


# =========================
# 🖥️ TELA PRINCIPAL
# =========================
def tela():

    st.title("💰 Financeiro Hospitalar")

    aba1, aba2, aba3, aba4 = st.tabs([
        "💳 Faturamento",
        "📥 Receber",
        "📤 Pagar",
        "📊 Dashboard"
    ])

    with aba1:
        faturar()

    with aba2:
        contas_receber()

    with aba3:
        contas_pagar()

    with aba4:
        dashboard()