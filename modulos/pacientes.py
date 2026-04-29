import streamlit as st
import pandas as pd
from conexao_db import select_df, select, insert, update

# =========================
# 🎨 CSS
# =========================
def css():
    st.markdown("""
    <style>
    .card {
        background: #020617;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


# =========================
# 📥 CARREGAR PACIENTES
# =========================
@st.cache_data(ttl=5)
def carregar_pacientes():
    return select_df("pacientes", ordem="created_at")


# =========================
# 💾 SALVAR
# =========================
def salvar(dados, id=None):

    if id:
        ok = update("pacientes", dados, {"id": id})
    else:
        ok = insert("pacientes", dados)

    if ok:
        st.cache_data.clear()
        st.success("Salvo com sucesso")
        st.rerun()
    else:
        st.error("Erro ao salvar")


# =========================
# 📊 RESUMO PACIENTE
# =========================
def resumo(paciente):

    st.markdown("### 👤 Informações")

    col1, col2, col3 = st.columns(3)

    col1.metric("Nome", paciente["nome"])
    col2.metric("CPF", paciente.get("cpf", "-"))
    col3.metric("Telefone", paciente.get("telefone", "-"))


# =========================
# 📜 HISTÓRICO
# =========================
def historico(paciente_id):

    consultas = select("consultas", {"paciente_id": paciente_id})
    internacoes = select("internacoes", {"paciente_id": paciente_id})

    st.markdown("### 📜 Histórico")

    st.write(f"🩺 Consultas: {len(consultas)}")
    st.write(f"🏥 Internações: {len(internacoes)}")


# =========================
# 💰 FINANCEIRO
# =========================
def financeiro(paciente_id):

    dados = select("contas_receber", {"paciente_id": paciente_id})

    if not dados:
        st.info("Sem dados financeiros")
        return

    df = pd.DataFrame(dados)

    total = df["valor"].sum()
    pago = df[df["status"] == "recebido"]["valor"].sum()

    col1, col2 = st.columns(2)

    col1.metric("Total", f"R$ {total:.2f}")
    col2.metric("Recebido", f"R$ {pago:.2f}")


# =========================
# 🧾 AÇÕES
# =========================
def acoes(paciente):

    st.markdown("### ⚡ Ações rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧾 Abrir prontuário"):
            st.session_state.menu = "Prontuário"
            st.session_state.paciente_prontuario = paciente["id"]
            st.rerun()

    with col2:
        if st.button("🏥 Internar"):
            st.session_state.menu = "Internação"
            st.session_state.paciente_internar = paciente["id"]
            st.rerun()

    with col3:
        if st.button("💰 Ver financeiro"):
            st.session_state.menu = "Financeiro"
            st.rerun()


# =========================
# 📝 FORM
# =========================
def form(p=None):

    st.markdown("### ➕ Novo / Editar")

    nome = st.text_input("Nome", value=p["nome"] if p else "")
    cpf = st.text_input("CPF", value=p.get("cpf","") if p else "")
    tel = st.text_input("Telefone", value=p.get("telefone","") if p else "")

    if st.button("Salvar paciente"):

        if not nome:
            st.warning("Nome obrigatório")
            return

        salvar({
            "nome": nome,
            "cpf": cpf,
            "telefone": tel
        }, p["id"] if p else None)


# =========================
# 📋 LISTA
# =========================
def lista(df):

    busca = st.text_input("🔍 Buscar")

    if busca:
        df = df[df["nome"].str.contains(busca, case=False)]

    for _, row in df.iterrows():

        col1, col2 = st.columns([5,1])

        with col1:
            st.markdown(f"""
            <div class='card'>
                👤 <b>{row['nome']}</b><br>
                <small>{row.get('cpf','')}</small>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("Abrir", key=row["id"]):
                st.session_state.paciente_sel = row.to_dict()
                st.rerun()


# =========================
# 🖥️ TELA
# =========================
def tela():

    css()

    st.title("👤 Pacientes")

    df = carregar_pacientes()
    paciente = st.session_state.get("paciente_sel")

    aba1, aba2 = st.tabs(["📋 Lista", "➕ Cadastro"])

    # 📋 LISTA
    with aba1:
        if df.empty:
            st.warning("Nenhum paciente")
        else:
            lista(df)

    # ➕ FORM
    with aba2:
        form(paciente)

    # 🔥 DETALHE
    if paciente:

        st.markdown("---")

        col1, col2 = st.columns([2,1])

        with col1:
            resumo(paciente)
            historico(paciente["id"])

        with col2:
            financeiro(paciente["id"])
            acoes(paciente)