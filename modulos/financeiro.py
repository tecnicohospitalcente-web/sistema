import streamlit as st
import pandas as pd
from conexao import supabase, safe_query

# =========================
# 🧠 TRATAR RESPOSTA (ANTI ERRO)
# =========================
def tratar(res):
    if res is None or not hasattr(res, "data"):
        return []
    return res.data or []


# =========================
# 📥 DADOS
# =========================
@st.cache_data(ttl=30)
def carregar_receber():
    res = safe_query(lambda: supabase.table("contas_receber")
                     .select("*")
                     .order("created_at", desc=True)
                     .execute())
    return pd.DataFrame(tratar(res))


@st.cache_data(ttl=30)
def carregar_pagar():
    res = safe_query(lambda: supabase.table("contas_pagar")
                     .select("*")
                     .order("created_at", desc=True)
                     .execute())
    return pd.DataFrame(tratar(res))


@st.cache_data(ttl=30)
def carregar_pacientes():
    res = safe_query(lambda: supabase.table("pacientes")
                     .select("id,nome")
                     .execute())
    return tratar(res)


# =========================
# 💸 AÇÕES
# =========================
def receber(id):
    supabase.table("contas_receber") \
        .update({"status": "recebido"}) \
        .eq("id", id).execute()

    st.cache_data.clear()
    st.rerun()


def pagar(id):
    supabase.table("contas_pagar") \
        .update({"status": "pago"}) \
        .eq("id", id).execute()

    st.cache_data.clear()
    st.rerun()


# =========================
# 🧾 RECEITA MANUAL
# =========================
def nova_receita(pacientes):

    st.markdown("### ➕ Nova Receita")

    nomes = ["Sem paciente"] + [p["nome"] for p in pacientes]
    escolha = st.selectbox("Paciente", nomes)

    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.0)

    if st.button("Salvar receita"):

        if not descricao or valor <= 0:
            st.warning("Preencha corretamente")
            return

        paciente_id = None
        if escolha != "Sem paciente":
            paciente_id = next(p["id"] for p in pacientes if p["nome"] == escolha)

        supabase.table("contas_receber").insert({
            "paciente_id": paciente_id,
            "descricao": descricao,
            "valor": valor,
            "status": "pendente"
        }).execute()

        st.success("Receita salva")
        st.cache_data.clear()
        st.rerun()


# =========================
# 📦 DESPESA
# =========================
def nova_despesa():

    st.markdown("### ➕ Nova Despesa")

    descricao = st.text_input("Descrição despesa")
    valor = st.number_input("Valor despesa", min_value=0.0)

    if st.button("Salvar despesa"):

        if not descricao or valor <= 0:
            st.warning("Preencha corretamente")
            return

        supabase.table("contas_pagar").insert({
            "descricao": descricao,
            "valor": valor,
            "status": "pendente"
        }).execute()

        st.success("Despesa salva")
        st.cache_data.clear()
        st.rerun()


# =========================
# 🔎 FILTROS
# =========================
def aplicar_filtros(df, pacientes, prefixo):

    col1, col2, col3 = st.columns(3)

    nomes = ["Todos"] + [p["nome"] for p in pacientes]

    paciente_sel = col1.selectbox(
        "Paciente",
        nomes,
        key=f"{prefixo}_paciente"
    )

    status_sel = col2.selectbox(
        "Status",
        ["Todos", "pendente", "recebido", "pago"],
        key=f"{prefixo}_status"
    )

    data_ini = col3.date_input(
        "Data início",
        value=None,
        key=f"{prefixo}_data"
    )

    if df.empty:
        return df

    if paciente_sel != "Todos":
        pid = next(p["id"] for p in pacientes if p["nome"] == paciente_sel)
        df = df[df["paciente_id"] == pid]

    if status_sel != "Todos":
        df = df[df["status"] == status_sel]

    if data_ini and "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
        df = df[df["created_at"] >= pd.to_datetime(data_ini)]

    return df


# =========================
# 📥 TABELA RECEBER
# =========================
def tabela_receber(df):

    st.markdown("### 📥 Receitas")

    if df.empty:
        st.info("Sem dados")
        return

    for _, row in df.iterrows():

        col1, col2, col3, col4 = st.columns([3,2,2,2])

        col1.write(row.get("descricao", "-"))
        col2.write(f"R$ {row.get('valor',0):.2f}")
        col3.write(row.get("status", "-"))

        if row.get("status") != "recebido":
            if col4.button("Receber", key=f"r_{row['id']}"):
                receber(row["id"])


# =========================
# 📤 TABELA PAGAR
# =========================
def tabela_pagar(df):

    st.markdown("### 📤 Despesas")

    if df.empty:
        st.info("Sem dados")
        return

    for _, row in df.iterrows():

        col1, col2, col3, col4 = st.columns([3,2,2,2])

        col1.write(row.get("descricao", "-"))
        col2.write(f"R$ {row.get('valor',0):.2f}")
        col3.write(row.get("status", "-"))

        if row.get("status") != "pago":
            if col4.button("Pagar", key=f"p_{row['id']}"):
                pagar(row["id"])


# =========================
# 🖥️ TELA
# =========================
def tela():

    st.title("💰 Financeiro")

    pacientes = carregar_pacientes()
    df_r = carregar_receber()
    df_p = carregar_pagar()

    aba1, aba2 = st.tabs([
        "📥 Receber",
        "📤 Pagar"
    ])

    # RECEBER
    with aba1:
        nova_receita(pacientes)
        st.markdown("---")
        df_filtrado = aplicar_filtros(df_r, pacientes)
        tabela_receber(df_filtrado)

    # PAGAR
    with aba2:
        nova_despesa()
        st.markdown("---")
        df_filtrado = aplicar_filtros(df_p, pacientes)
        tabela_pagar(df_filtrado)