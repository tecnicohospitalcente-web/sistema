import streamlit as st
from conexao import supabase


# =========================
# 🧠 FUNÇÃO SEGURA
# =========================
def tratar(res):
    if res is None or not hasattr(res, "data"):
        return []
    return res.data or []


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
# 👤 TOPO
# =========================
def topo_paciente(p):

    st.markdown(f"""
    <div class="topo">
        <h3>👤 {p.get('nome','-')}</h3>
        <small>ID: {p.get('id','-')}</small>
    </div>
    """, unsafe_allow_html=True)


# =========================
# 🩺 EVOLUÇÃO
# =========================
def evolucao(paciente_id):

    st.subheader("📈 Evolução Médica")

    texto = st.text_area("Descrever evolução", key="evo_txt")

    if st.button("Salvar evolução", key="btn_evo"):

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

    dados = tratar(
        supabase.table("evolucoes")
        .select("*")
        .eq("paciente_id", paciente_id)
        .order("created_at", desc=True)
        .execute()
    )

    for d in dados:
        st.markdown(f"""
        <div class="box">
        <b>{d.get('profissional','-')}</b><br>
        <small>{d.get('created_at','')}</small>
        <p>{d.get('descricao','')}</p>
        </div>
        """, unsafe_allow_html=True)


# =========================
# 💊 PRESCRIÇÃO
# =========================
def prescricao(paciente_id):

    st.subheader("💊 Prescrição")

    med = st.text_input("Medicamento", key="med")
    dosagem = st.text_input("Dosagem", key="dos")
    freq = st.text_input("Frequência", key="freq")

    if st.button("Adicionar", key="btn_presc"):

        supabase.table("prescricoes").insert({
            "paciente_id": paciente_id,
            "medicamento": med,
            "dosagem": dosagem,
            "frequencia": freq
        }).execute()

        st.success("Adicionado")
        st.rerun()

    dados = tratar(
        supabase.table("prescricoes")
        .select("*")
        .eq("paciente_id", paciente_id)
        .execute()
    )

    for d in dados:
        st.markdown(f"""
        <div class="box">
        <b>{d.get('medicamento','')}</b><br>
        {d.get('dosagem','')} - {d.get('frequencia','')}
        </div>
        """, unsafe_allow_html=True)


# =========================
# 🧪 EXAMES
# =========================
def exames(paciente_id):

    st.subheader("🧪 Exames")

    nome = st.text_input("Nome exame", key="ex_nome")
    resultado = st.text_area("Resultado", key="ex_res")

    if st.button("Salvar exame", key="btn_exame"):

        supabase.table("exames").insert({
            "paciente_id": paciente_id,
            "nome": nome,
            "resultado": resultado,
            "status": "finalizado"
        }).execute()

        st.success("Salvo")
        st.rerun()

    dados = tratar(
        supabase.table("exames")
        .select("*")
        .eq("paciente_id", paciente_id)
        .execute()
    )

    for d in dados:
        st.markdown(f"""
        <div class="box">
        <b>{d.get('nome','')}</b><br>
        <small>{d.get('status','')}</small>
        <p>{d.get('resultado','')}</p>
        </div>
        """, unsafe_allow_html=True)


# =========================
# ⚡ AÇÕES
# =========================
def acoes(paciente):

    st.markdown("### ⚡ Ações")

    col1, col2 = st.columns(2)

    # CONSULTA
    with col1:
        if st.button("🩺 Consulta", key="btn_consulta"):

            supabase.table("consultas").insert({
                "paciente_id": paciente["id"]
            }).execute()

            st.success("Consulta registrada")
            st.rerun()

    # INTERNAÇÃO
    with col2:

        prioridade = st.selectbox(
            "Prioridade",
            ["Eletivo", "Urgente", "Emergência"],
            key="prioridade"
        )

        if st.button("🏥 Internar", key="btn_internar"):

            leitos = tratar(
                supabase.table("leitos")
                .select("*")
                .eq("status", "livre")
                .limit(1)
                .execute()
            )

            if not leitos:
                st.error("Sem leitos disponíveis")
                return

            leito = leitos[0]

            supabase.table("internacoes").insert({
                "paciente_id": paciente["id"],
                "leito_id": leito["id"],
                "status": "ativo"
            }).execute()

            supabase.table("leitos").update({
                "status": "ocupado"
            }).eq("id", leito["id"]).execute()

            st.success(f"Internado no leito {leito['id']}")
            st.rerun()


# =========================
# 🖥️ TELA
# =========================
def tela():

    css()

    st.title("🧾 Prontuário")

    paciente = st.session_state.get("paciente_prontuario")

    if not paciente:
        st.warning("Abra um paciente primeiro")
        return

    # 🔥 GARANTE QUE É DICT
    if isinstance(paciente, int):
        res = supabase.table("pacientes").select("*").eq("id", paciente).execute()
        dados = tratar(res)
        if not dados:
            st.error("Paciente não encontrado")
            return
        paciente = dados[0]

    topo_paciente(paciente)

    st.markdown("---")

    acoes(paciente)

    st.markdown("---")

    aba1, aba2, aba3 = st.tabs([
        "📈 Evolução",
        "💊 Prescrição",
        "🧪 Exames"
    ])

    with aba1:
        evolucao(paciente["id"])

    with aba2:
        prescricao(paciente["id"])

    with aba3:
        exames(paciente["id"])
