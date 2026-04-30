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
        font-size: 14px;
    }
    .livre { background: #16a34a; }
    .ocupado { background: #dc2626; }
    .limpeza { background: #f59e0b; }
    </style>
    """, unsafe_allow_html=True)


# =========================
# 📥 DADOS
# =========================
@st.cache_data(ttl=3)
def carregar():
    return (
        supabase.table("pacientes").select("id,nome").execute().data,
        supabase.table("leitos").select("*").execute().data,
        supabase.table("quartos").select("*").execute().data,
        supabase.table("internacoes").select("*").eq("status","ativo").execute().data,
        supabase.table("prontuarios").select("*").eq("status","aberto").execute().data
    )


# =========================
# 🧠 REGRAS
# =========================
def paciente_internado(paciente_id):
    r = supabase.table("internacoes") \
        .select("id") \
        .eq("paciente_id", paciente_id) \
        .eq("status","ativo") \
        .execute().data
    return len(r) > 0


def escolher_leito(leitos):
    livres = [l for l in leitos if l["status"] == "livre"]
    return livres[0] if livres else None


# =========================
# 🏥 INTERNAR
# =========================
def internar(paciente_id, leitos):

    if paciente_internado(paciente_id):
        st.warning("Paciente já está internado")
        return None

    leito = escolher_leito(leitos)

    if not leito:
        return None

    # cria internação
    supabase.table("internacoes").insert({
        "paciente_id": paciente_id,
        "leito_id": leito["id"],
        "status": "ativo"
    }).execute()

    # atualiza leito
    supabase.table("leitos").update({
        "status": "ocupado"
    }).eq("id", leito["id"]).execute()

    # prontuário
    supabase.table("prontuarios").insert({
        "paciente_id": paciente_id,
        "status": "aberto"
    }).execute()

    gerar_faturamento(paciente_id, "internacao", 800)

    st.cache_data.clear()
    return leito


# =========================
# 🗺️ MAPA
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
            "status": l["status"],
            "paciente": pacientes_map.get(intern["paciente_id"], "") if intern else ""
        })

    for setor, lista in estrutura.items():

        st.markdown(f"<div class='box'><b>{setor}</b>", unsafe_allow_html=True)

        cols = st.columns(5)

        for i, l in enumerate(lista):

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
# ⚙️ PAINEL LEITO
# =========================
def painel(leitos):

    leito = st.session_state.get("leito")
    if not leito:
        return

    st.subheader(f"Leito {leito['numero']}")

    # 🔴 OCUPADO
    if leito["status"] == "ocupado":

        if st.button("Dar alta"):

            supabase.table("internacoes") \
                .update({"status": "alta"}) \
                .eq("leito_id", leito["id"]) \
                .eq("status","ativo") \
                .execute()

            supabase.table("leitos").update({
                "status": "limpeza"
            }).eq("id", leito["id"]).execute()

            st.success("Alta realizada")
            st.rerun()

        # 🔁 transferência
        livres = [l for l in leitos if l["status"] == "livre"]

        if livres:
            destino = st.selectbox("Transferir para", [l["id"] for l in livres])

            if st.button("Confirmar transferência"):

                supabase.table("internacoes") \
                    .update({"leito_id": destino}) \
                    .eq("leito_id", leito["id"]) \
                    .eq("status","ativo") \
                    .execute()

                supabase.table("leitos").update({"status":"limpeza"}).eq("id", leito["id"]).execute()
                supabase.table("leitos").update({"status":"ocupado"}).eq("id", destino).execute()

                st.success("Transferido")
                st.rerun()

    # 🟡 LIMPEZA
    elif leito["status"] == "limpeza":

        if st.button("Finalizar limpeza"):
            supabase.table("leitos").update({
                "status": "livre"
            }).eq("id", leito["id"]).execute()

            st.success("Liberado")
            st.rerun()

    else:
        st.success("Disponível")


# =========================
# 📋 PRONTUÁRIO
# =========================
def prontuario(prontuarios):

    st.subheader("📋 Prontuário")

    mapa = {p["paciente_id"]: p for p in prontuarios}

    paciente_id = st.session_state.get("paciente_prontuario")

    if not paciente_id:
        return

    pront = mapa.get(paciente_id)

    if not pront:
        st.warning("Sem prontuário")
        return

    evolucoes = supabase.table("evolucoes") \
        .select("*") \
        .eq("prontuario_id", pront["id"]) \
        .execute().data

    for e in evolucoes:
        st.write(e["descricao"])

    texto = st.text_area("Nova evolução")

    if st.button("Salvar evolução"):
        supabase.table("evolucoes").insert({
            "prontuario_id": pront["id"],
            "descricao": texto
        }).execute()
        st.rerun()


# =========================
# 🖥️ TELA
# =========================
def tela():

    st.title("🏥 Sistema Hospitalar")

    pacientes, leitos, quartos, internacoes, prontuarios = carregar()

    aba1, aba2, aba3, aba4 = st.tabs([
        "👤 Paciente",
        "🩺 Atendimento",
        "🗺️ Leitos",
        "📋 Prontuário"
    ])

    # 👤
    with aba1:
        nome = st.text_input("Nome")

        if st.button("Cadastrar"):
            supabase.table("pacientes").insert({"nome": nome}).execute()
            st.rerun()

    # 🩺
    with aba2:

        if not pacientes:
            return

        nomes = [p["nome"] for p in pacientes]
        paciente = st.selectbox("Paciente", nomes)
        paciente_id = [p["id"] for p in pacientes if p["nome"] == paciente][0]

        if st.button("Internar"):
            leito = internar(paciente_id, leitos)

            if leito:
                st.success(f"Leito {leito['numero']}")

        if st.button("Abrir prontuário"):
            st.session_state.paciente_prontuario = paciente_id

    # 🗺️
    with aba3:
        mapa(leitos, quartos, internacoes, pacientes)
        painel(leitos)

    # 📋
    with aba4:
        prontuario(prontuarios)