import streamlit as st
from conexao import supabase
from modulos.financeiro import gerar_faturamento

# =========================
# 🎨 CSS PROFISSIONAL
# =========================
def css():
    st.markdown("""
    <style>

    .box {
        background: #020617;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #1f2937;
        margin-bottom: 15px;
    }

    .leito {
        padding: 14px;
        border-radius: 10px;
        text-align: center;
        color: white;
        transition: 0.2s;
        font-size: 14px;
    }

    .leito:hover {
        transform: scale(1.05);
    }

    .livre { background: #16a34a; }
    .ocupado { background: #dc2626; }
    .limpeza { background: #f59e0b; }

    </style>
    """, unsafe_allow_html=True)


# =========================
# 📥 DADOS COMPLETOS
# =========================
@st.cache_data(ttl=5)
def carregar_tudo():

    pacientes = supabase.table("pacientes").select("*").execute().data
    leitos = supabase.table("leitos").select("*").execute().data
    quartos = supabase.table("quartos").select("*").execute().data
    internacoes = supabase.table("internacoes") \
        .select("*").eq("status", "ativo").execute().data

    return pacientes, leitos, quartos, internacoes


# =========================
# 🧠 LEITO INTELIGENTE
# =========================
def escolher_leito(leitos, internacoes, prioridade):

    ocupados = [i["leito_id"] for i in internacoes]
    livres = [l for l in leitos if l["id"] not in ocupados]

    if not livres:
        return None

    if prioridade == "Emergência":
        return livres[0]

    elif prioridade == "Urgente":
        return livres[len(livres)//2]

    return livres[-1]


# =========================
# 🏥 INTERNAR (COMPLETO)
# =========================
def internar(paciente_id, prioridade, leitos, internacoes):

    leito = escolher_leito(leitos, internacoes, prioridade)

    if not leito:
        return False

    # salva internação
    supabase.table("internacoes").insert({
        "paciente_id": paciente_id,
        "leito_id": leito["id"],
        "status": "ativo"
    }).execute()

    # 💰 financeiro automático
    valor = 500 if prioridade == "Eletivo" else 800 if prioridade == "Urgente" else 1200

    gerar_faturamento(paciente_id, "internacao", valor)

    # 🧾 cria prontuário automaticamente
    supabase.table("prontuarios").insert({
        "paciente_id": paciente_id,
        "status": "aberto"
    }).execute()

    st.cache_data.clear()
    return leito


# =========================
# 🗺️ MAPA REAL HOSPITAL
# =========================
def mapa(leitos, quartos, internacoes, pacientes):

    css()

    pacientes_map = {p["id"]: p["nome"] for p in pacientes}
    intern_map = {i["leito_id"]: i for i in internacoes}
    quartos_map = {q["id"]: q for q in quartos}

    estrutura = {}

    for l in leitos:

        quarto = quartos_map.get(l["quarto_id"])
        if not quarto:
            continue

        key = f"{quarto['setor']} | Quarto {quarto['numero']}"

        if key not in estrutura:
            estrutura[key] = []

        intern = intern_map.get(l["id"])

        estrutura[key].append({
            "id": l["id"],
            "numero": l["numero"],
            "status": "ocupado" if intern else "livre",
            "paciente": pacientes_map.get(intern["paciente_id"], "") if intern else ""
        })

    # render
    for setor, leitos_lista in estrutura.items():

        st.markdown(f"<div class='box'><b>{setor}</b>", unsafe_allow_html=True)

        cols = st.columns(5)

        for i, l in enumerate(leitos_lista):

            with cols[i % 5]:

                st.markdown(f"""
                <div class="leito {l['status']}">
                    🛏️ {l['numero']}<br>
                    {l['status'].upper()}<br>
                    <small>{l['paciente']}</small>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Abrir", key=f"l_{l['id']}"):
                    st.session_state.leito = l

        st.markdown("</div>", unsafe_allow_html=True)


# =========================
# ⚙️ PAINEL DO LEITO
# =========================
def painel():

    leito = st.session_state.get("leito")

    if not leito:
        return

    st.markdown("---")
    st.subheader(f"Leito {leito['numero']}")

    if leito["status"] == "ocupado":

        if st.button("Dar alta"):

            supabase.table("internacoes") \
                .update({"status": "alta"}) \
                .eq("leito_id", leito["id"]) \
                .eq("status", "ativo") \
                .execute()

            st.success("Alta realizada")
            st.cache_data.clear()
            st.rerun()

    else:
        st.success("Disponível")


# =========================
# 🖥️ TELA PRINCIPAL
# =========================
def tela():

    st.title("🏥 Internação Inteligente (Nível Hospital)")

    pacientes, leitos, quartos, internacoes = carregar_tudo()

    aba1, aba2, aba3 = st.tabs([
        "👤 Paciente",
        "🩺 Atendimento",
        "🗺️ Mapa"
    ])

    # =========================
    # 👤 PACIENTE
    # =========================
    with aba1:

        nome = st.text_input("Nome do paciente")

        if st.button("Cadastrar"):
            supabase.table("pacientes").insert({"nome": nome}).execute()
            st.success("Paciente cadastrado")
            st.rerun()

    # =========================
    # 🩺 ATENDIMENTO
    # =========================
    with aba2:

        if not pacientes:
            st.warning("Cadastre paciente")
            return

        nomes = [p["nome"] for p in pacientes]

        paciente = st.selectbox("Paciente", nomes)

        paciente_id = [p["id"] for p in pacientes if p["nome"] == paciente][0]

        tipo = st.radio("Tipo", ["Consulta", "Internação"])

        # 🔹 CONSULTA
        if tipo == "Consulta":

            if st.button("Registrar consulta"):

                supabase.table("consultas").insert({
                    "paciente_id": paciente_id
                }).execute()

                gerar_faturamento(paciente_id, "consulta", 150)

                st.success("Consulta registrada")

        # 🔹 INTERNAÇÃO
        else:

            prioridade = st.selectbox(
                "Prioridade",
                ["Eletivo", "Urgente", "Emergência"]
            )

            if st.button("Internar paciente"):

                leito = internar(paciente_id, prioridade, leitos, internacoes)

                if not leito:
                    st.error("Sem leitos disponíveis")
                else:
                    st.success(f"Internado no leito {leito['numero']}")
                    st.rerun()

    # =========================
    # 🗺️ MAPA
    # =========================
    with aba3:
        mapa(leitos, quartos, internacoes, pacientes)
        painel()