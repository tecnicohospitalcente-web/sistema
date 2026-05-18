import streamlit as st
import pandas as pd
from conexao import supabase

# =========================
# 📥 CARREGAR
# =========================
@st.cache_data(ttl=10)
def carregar():
    res = supabase.table("estoque").select("*").execute()
    return pd.DataFrame(res.data or [])


# =========================
# ⚠️ ALERTA
# =========================
def alerta_estoque(df):

    if df.empty:
        return

    baixo = df[df["quantidade"] <= df["estoque_min"]]

    if not baixo.empty:
        st.error("⚠️ Estoque baixo")

        for _, row in baixo.iterrows():
            st.write(f"🔴 {row['nome']} | Qtd: {row['quantidade']}")


# =========================
# 💾 NOVO PRODUTO
# =========================
def salvar_produto(nome, categoria, setor, qtd, minimo):

    supabase.table("estoque").insert({
        "nome": nome,
        "categoria": categoria,
        "setor": setor,
        "quantidade": qtd,
        "estoque_min": minimo
    }).execute()

    st.cache_data.clear()
    st.success("Produto cadastrado")
    st.rerun()


# =========================
# 📦 ENTRADA COM LOTE
# =========================
def entrada_lote(produto_id, qtd, lote, validade):

    supabase.table("estoque_lotes").insert({
        "produto_id": produto_id,
        "lote": lote,
        "validade": str(validade),
        "quantidade": qtd
    }).execute()

    produto = supabase.table("estoque") \
        .select("quantidade") \
        .eq("id", produto_id) \
        .single() \
        .execute().data

    nova = produto["quantidade"] + qtd

    supabase.table("estoque") \
        .update({"quantidade": nova}) \
        .eq("id", produto_id) \
        .execute()

    st.cache_data.clear()
    st.success("Entrada registrada")
    st.rerun()


# =========================
# 🔄 SAÍDA FIFO
# =========================
def saida_lote(produto_id, qtd):

    lotes = supabase.table("estoque_lotes") \
        .select("*") \
        .eq("produto_id", produto_id) \
        .order("validade", desc=False) \
        .execute().data

    restante = qtd

    for lote in lotes:

        if restante <= 0:
            break

        if lote["quantidade"] <= restante:

            restante -= lote["quantidade"]

            supabase.table("estoque_lotes") \
                .update({"quantidade": 0}) \
                .eq("id", lote["id"]) \
                .execute()

        else:

            nova = lote["quantidade"] - restante

            supabase.table("estoque_lotes") \
                .update({"quantidade": nova}) \
                .eq("id", lote["id"]) \
                .execute()

            restante = 0

    produto = supabase.table("estoque") \
        .select("quantidade") \
        .eq("id", produto_id) \
        .single() \
        .execute().data

    supabase.table("estoque") \
        .update({"quantidade": produto["quantidade"] - qtd}) \
        .eq("id", produto_id) \
        .execute()

    st.cache_data.clear()
    st.success("Saída registrada")
    st.rerun()


# =========================
# 📦 VER LOTES
# =========================
def ver_lotes(produto_id):

    dados = supabase.table("estoque_lotes") \
        .select("*") \
        .eq("produto_id", produto_id) \
        .execute().data

    if not dados:
        st.info("Sem lotes")
        return

    st.markdown("#### 📦 Lotes")

    for l in dados:
        st.write(f"Lote: {l['lote']} | Qtd: {l['quantidade']} | Val: {l['validade']}")


# =========================
# 📋 LISTA
# =========================
def lista(df):

    busca = st.text_input("🔍 Buscar produto")

    if busca:
        df = df[df["nome"].str.contains(busca, case=False)]

    for _, row in df.iterrows():

        with st.container():

            col1, col2, col3, col4, col5 = st.columns([3,1,1,1,2])

            col1.write(f"💊 {row['nome']}")
            col2.write(row["setor"])
            col3.write(f"Qtd: {row['quantidade']}")
            col4.write(f"Min: {row['estoque_min']}")

            with col5:
                if st.button("Entrada", key=f"e_{row['id']}"):
                    st.session_state.mov = ("entrada", row["id"])

                if st.button("Saída", key=f"s_{row['id']}"):
                    st.session_state.mov = ("saida", row["id"])

                if st.button("Lotes", key=f"l_{row['id']}"):
                    st.session_state.ver_lote = row["id"]

        if st.session_state.get("ver_lote") == row["id"]:
            ver_lotes(row["id"])


# =========================
# 🔄 MODAL MOVIMENTAÇÃO
# =========================
def modal():

    mov = st.session_state.get("mov")

    if not mov:
        return

    tipo, produto_id = mov

    st.markdown("---")
    st.subheader(f"{tipo.upper()}")

    if tipo == "entrada":

        qtd = st.number_input("Quantidade", min_value=1)
        lote = st.text_input("Lote")
        validade = st.date_input("Validade")

        if st.button("Confirmar entrada"):
            if not lote:
                st.warning("Informe lote")
                return

            entrada_lote(produto_id, qtd, lote, validade)

    else:

        qtd = st.number_input("Quantidade", min_value=1)

        if st.button("Confirmar saída"):
            saida_lote(produto_id, qtd)


# =========================
# ➕ NOVO
# =========================
def novo():

    st.markdown("### ➕ Novo Produto")

    nome = st.text_input("Nome")
    categoria = st.selectbox("Categoria", ["medicamento", "material"])
    setor = st.selectbox("Setor", ["farmacia", "enfermaria"])
    qtd = st.number_input("Quantidade inicial", min_value=0)
    minimo = st.number_input("Estoque mínimo", min_value=1, value=5)

    if st.button("Cadastrar produto"):

        if not nome:
            st.warning("Nome obrigatório")
            return

        salvar_produto(nome, categoria, setor, qtd, minimo)


# =========================
# 🖥️ TELA
# =========================
def tela():

    st.title("📦 Estoque Hospitalar")

    df = carregar()

    alerta_estoque(df)

    aba1, aba2 = st.tabs(["📋 Estoque", "➕ Cadastro"])

    with aba1:
        if df.empty:
            st.warning("Sem produtos")
        else:
            lista(df)
            modal()

    with aba2:
        novo()