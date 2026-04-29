import streamlit as st
from conexao import supabase
from modulos.financeiro import gerar_faturamento

# =========================
# 🎨 CSS
# =========================
def css():
    st.markdown("""
    <style>

    .box {
        background: #020617;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 15px;
    }

    .topo {
        background: #020617;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 20px;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================
# 👤 TOPO DO PACIENTE
# =========================
def topo_paciente(p):

    st.markdown(f"""
    <div class="topo">
        <h3>👤 {p['nome']}</h3>
        <small>ID: {p['id']}</small>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🩺 EVOLUÇÃO
# =========================
def evolucao(paciente_id):

    st.subheader("📈 Evolução Médica")

    texto = st.text_area("Descrever evolução")

    if st.button("Salvar evolução"):

        if not texto:
            st.warning("Digite algo")
            return

        supabase.table("evolucoes").insert({
            "paciente_id": paciente_id,
            "descricao": texto,
            "profissional": st.session_state.get("usuario")
        }).execute()

        st.success("Salvo")
        st.rerun()

    dados = supabase.table("evolucoes") \
        .select("*") \
        .eq("paciente_id", paciente_id) \
        .order("created_at", desc=True) \
        .execute().data

    for d in dados:
        st.markdown(f"""
        <div class="box">
        <b>{d['profissional']}</b><br>
        <small>{d['created_at']}</small>
        <p>{d['descricao']}</p>
        </div>
        """, unsafe_allow_html=True)


# =========================
# 💊 PRESCRIÇÃO
# =========================
def prescricao(paciente_id):

    st.subheader("💊 Prescrição")

    med = st.text_input("Medicamento")
    dosagem = st.text_input("Dosagem")
    freq = st.text_input("Frequência")

    if st.button("Adicionar prescrição"):

        supabase.table("prescricoes").insert({
            "paciente_id": paciente_id,
            "medicamento": med,
            "dosagem": dosagem,
            "frequencia": freq
        }).execute()

        st.success("Adicionado")
        st.rerun()

    dados = supabase.table("prescricoes") \
        .select("*") \
        .eq("paciente_id", paciente_id) \
        .execute().data

    for d in dados:
        st.markdown(f"""
        <div class="box">
        <b>{d['medicamento']}</b><br>
        {d['dosagem']} - {d['frequencia']}
        </div>
        """, unsafe_allow_html=True)


# =========================
# 🧪 EXAMES
# =========================
def exames(paciente_id):

    st.subheader("🧪 Exames")

    nome = st.text_input("Nome do exame")
    resultado = st.text_area("Resultado")

    if st.button("Registrar exame"):

        supabase.table("exames").insert({
            "paciente_id": paciente_id,
            "nome": nome,
            "resultado": resultado,
            "status": "finalizado"
        }).execute()

        st.success("Exame registrado")
        st.rerun()

    dados = supabase.table("exames") \
        .select("*") \
        .eq("paciente_id", paciente_id) \
        .execute().data

    for d in dados:
        st.markdown(f"""
        <div class="box">
        <b>{d['nome']}</b><br>
        <small>{d['status']}</small>
        <p>{d['resultado']}</p>
        </div>
        """, unsafe_allow_html=True)


# =========================
# 📜 HISTÓRICO
# =========================
def historico(paciente_id):

    st.subheader("📜 Histórico")

    consultas = supabase.table("consultas") \
        .select("*") \
        .eq("paciente_id", paciente_id) \
        .execute().data

    internacoes = supabase.table("internacoes") \
        .select("*") \
        .eq("paciente_id", paciente_id) \
        .execute().data

    financeiro = supabase.table("financeiro") \
        .select("*") \
        .eq("paciente_id", paciente_id) \
        .execute().data

    st.markdown("#### 🩺 Consultas")
    for c in consultas:
        st.write(c)

    st.markdown("#### 🏥 Internações")
    for i in internacoes:
        st.write(i)

    st.markdown("#### 💰 Financeiro")
    for f in financeiro:
        st.write(f)


# =========================
# ⚡ AÇÕES CLÍNICAS
# =========================
def acoes(paciente):

    st.markdown("### ⚡ Ações")

    col1, col2 = st.columns(2)

    # 🩺 CONSULTA
    with col1:
        if st.button("🩺 Registrar consulta"):

            supabase.table("consultas").insert({
                "paciente_id": paciente["id"]
            }).execute()

            gerar_faturamento(paciente["id"], "consulta", 150)

            st.success("Consulta registrada + cobrança")
            st.rerun()

    # 🏥 INTERNAÇÃO
    with col2:

        prioridade = st.selectbox(
            "Prioridade",
            ["Eletivo", "Urgente", "Emergência"]
        )

        if st.button("🏥 Internar paciente"):

            leito = supabase.table("leitos") \
                .select("id") \
                .limit(1) \
                .execute().data

            if not leito:
                st.error("Sem leito")
                return

            supabase.table("internacoes").insert({
                "paciente_id": paciente["id"],
                "leito_id": leito[0]["id"],
                "status": "ativo"
            }).execute()

            valor = 500 if prioridade == "Eletivo" else 800 if prioridade == "Urgente" else 1200

            gerar_faturamento(paciente["id"], "internacao", valor)

            st.success("Internado + faturamento")
            st.rerun()


# =========================
# 🖥️ TELA
# =========================
def tela():

    css()

    st.title("🧾 Prontuário Eletrônico")

    # 🔥 PEGA DIRETO DA SESSÃO
    paciente = st.session_state.get("paciente_prontuario")

    if not paciente:
        st.warning("Abra um paciente pelo módulo Pacientes")
        return

    topo_paciente(paciente)

    st.markdown("---")

    acoes(paciente)

    st.markdown("---")

    aba1, aba2, aba3, aba4 = st.tabs([
        "📈 Evolução",
        "💊 Prescrição",
        "🧪 Exames",
        "📜 Histórico"
    ])

    with aba1:
        evolucao(paciente["id"])

    with aba2:
        prescricao(paciente["id"])

    with aba3:
        exames(paciente["id"])

    with aba4:
        historico(paciente["id"])