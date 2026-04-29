import streamlit as st
import pandas as pd
from conexao import supabase, safe_query

# =========================
# ⚡ CACHE (PERFORMANCE)
# =========================
@st.cache_data(ttl=5)
def carregar_leitos():

    leitos_res = safe_query(lambda: supabase.table("leitos")
                           .select("id, numero")
                           .execute())

    internacoes_res = safe_query(lambda: supabase.table("internacoes")
                                .select("leito_id, paciente_id")
                                .eq("status", "ativo")
                                .execute())

    pacientes_res = safe_query(lambda: supabase.table("pacientes")
                              .select("id, nome")
                              .execute())

    if not leitos_res or not leitos_res.data:
        return pd.DataFrame()

    leitos = leitos_res.data
    internacoes = internacoes_res.data if internacoes_res else []
    pacientes = pacientes_res.data if pacientes_res else []

    pacientes_map = {p["id"]: p["nome"] for p in pacientes}
    intern_map = {i["leito_id"]: i for i in internacoes}

    for leito in leitos:
        i = intern_map.get(leito["id"])

        if i:
            leito["status"] = "ocupado"
            leito["paciente"] = pacientes_map.get(i["paciente_id"], "Desconhecido")
        else:
            leito["status"] = "livre"
            leito["paciente"] = None

    return pd.DataFrame(leitos)


@st.cache_data(ttl=10)
def carregar_pacientes():
    res = safe_query(lambda: supabase.table("pacientes")
                     .select("id, nome")
                     .execute())

    return pd.DataFrame(res.data or [])


# =========================
# 👤 CADASTRO PACIENTE
# =========================
def cadastrar_paciente():

    st.subheader("👤 Cadastro de Paciente")

    nome = st.text_input("Nome")
    cpf = st.text_input("CPF")
    nascimento = st.date_input("Data de nascimento")
    telefone = st.text_input("Telefone")

    if st.button("Salvar paciente"):

        if not nome:
            st.warning("Nome obrigatório")
            return

        try:
            supabase.table("pacientes").insert({
                "nome": nome,
                "cpf": cpf,
                "data_nascimento": str(nascimento),
                "telefone": telefone
            }).execute()

            st.success("Paciente cadastrado")
            st.cache_data.clear()
            st.rerun()

        except Exception as e:
            st.error(f"Erro: {e}")


# =========================
# 🏥 INTERNAR
# =========================
def internar(paciente_id, leito_id):

    supabase.table("internacoes").insert({
        "paciente_id": paciente_id,
        "leito_id": leito_id,
        "status": "ativo"
    }).execute()

    st.cache_data.clear()


# =========================
# 🚪 ALTA
# =========================
def dar_alta(leito_id):

    supabase.table("internacoes") \
        .update({"status": "alta"}) \
        .eq("leito_id", leito_id) \
        .eq("status", "ativo") \
        .execute()

    st.cache_data.clear()


# =========================
# 🧠 PRIORIDADE
# =========================
def escolher_leito(df, prioridade):

    livres = df[df["status"] == "livre"]

    if livres.empty:
        return None

    if prioridade == "Emergência":
        return livres.iloc[0]

    elif prioridade == "Urgente":
        return livres.iloc[len(livres)//2]

    else:
        return livres.iloc[-1]


# =========================
# 🗺️ MAPA DE LEITOS
# =========================
def mapa_leitos(df):

    st.markdown("### 🗺️ Mapa de Leitos")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", len(df))
    col2.metric("Ocupados", len(df[df["status"] == "ocupado"]))
    col3.metric("Disponíveis", len(df[df["status"] == "livre"]))

    st.markdown("---")

    cols = st.columns(6)

    for i, row in df.iterrows():

        status = row["status"]

        cor = {
            "livre": "#16a34a",
            "ocupado": "#dc2626",
            "limpeza": "#f59e0b"
        }.get(status, "#374151")

        with cols[i % 6]:

            st.markdown(f"""
            <div style="
                background:{cor};
                padding:15px;
                border-radius:10px;
                text-align:center;
                color:white;
            ">
                <b>🛏️ {row['numero']}</b><br>
                {status.upper()}<br>
                <small>{row.get('paciente') or ''}</small>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Selecionar", key=f"leito_{row['id']}"):
                st.session_state.leito_sel = row.to_dict()


# =========================
# ⚙️ PAINEL LEITO
# =========================
def painel_leito():

    leito = st.session_state.get("leito_sel")

    if not leito:
        return

    st.markdown("---")
    st.subheader(f"Leito {leito['numero']}")

    if leito["status"] == "ocupado":

        if st.button("Dar alta"):
            dar_alta(leito["id"])
            st.success("Alta realizada")
            st.rerun()

    elif leito["status"] == "livre":

        st.success("Disponível")

    elif leito["status"] == "limpeza":

        if st.button("Liberar"):
            supabase.table("leitos").update({
                "status": "livre"
            }).eq("id", leito["id"]).execute()

            st.success("Liberado")
            st.rerun()


# =========================
# 🖥️ TELA PRINCIPAL
# =========================
def tela():

    st.title("🏥 Internação / Atendimento")

    df_leitos = carregar_leitos()
    df_pacientes = carregar_pacientes()

    aba1, aba2, aba3 = st.tabs([
        "👤 Pacientes",
        "🩺 Atendimento",
        "🗺️ Mapa de Leitos"
    ])

    # 👤 PACIENTE
    with aba1:
        cadastrar_paciente()

    # 🩺 ATENDIMENTO
    with aba2:

        if df_pacientes.empty:
            st.warning("Cadastre um paciente")
            return

        paciente = st.selectbox("Paciente", df_pacientes["nome"])
        paciente_id = df_pacientes[df_pacientes["nome"] == paciente]["id"].values[0]

        tipo = st.radio("Tipo", ["Consulta", "Internação"])

        if tipo == "Consulta":

            if st.button("Registrar consulta"):

                supabase.table("consultas").insert({
                    "paciente_id": paciente_id,
                    "status": "finalizado"
                }).execute()

                st.success("Consulta registrada")

        else:

            prioridade = st.selectbox(
                "Prioridade",
                ["Eletivo", "Urgente", "Emergência"]
            )

            if st.button("Internar automático"):

                leito = escolher_leito(df_leitos, prioridade)

                if leito is None:
                    st.error("Sem leitos")
                    return

                internar(paciente_id, leito["id"])

                st.success(f"Internado no leito {leito['numero']}")
                st.rerun()

    # 🗺️ MAPA (POR ÚLTIMO)
    with aba3:
        mapa_leitos(df_leitos)
        painel_leito()