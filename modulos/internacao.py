import streamlit as st
import pandas as pd
from conexao import supabase, safe_query

# =========================
# 🔄 CARREGAR DADOS (RÁPIDO)
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

    # 🔥 mapas rápidos (SEM loop pesado)
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


# =========================
# 👤 PACIENTES
# =========================
@st.cache_data(ttl=10)
def carregar_pacientes():
    res = safe_query(lambda: supabase.table("pacientes")
                     .select("id, nome")
                     .execute())

    return pd.DataFrame(res.data or [])


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
# 🧱 MAPA VISUAL
# =========================
def mapa_leitos(df):

    st.markdown("### 🏥 Mapa de Leitos")

    cols = st.columns(5)

    for i, row in df.iterrows():

        status = row["status"]

        cor = {
            "livre": "#16a34a",
            "ocupado": "#dc2626",
            "limpeza": "#f59e0b"
        }.get(status, "#374151")

        with cols[i % 5]:

            st.markdown(f"""
            <div style="
                background:{cor};
                padding:18px;
                border-radius:10px;
                text-align:center;
                color:white;
                margin-bottom:10px;
            ">
                <b>Leito {row['numero']}</b><br>
                {status.upper()}
            </div>
            """, unsafe_allow_html=True)

            if st.button("Selecionar", key=row["id"]):
                st.session_state.leito_sel = row.to_dict()


# =========================
# 🖥️ TELA
# =========================
def tela():

    st.title("🏥 Internação")

    df_leitos = carregar_leitos()
    df_pacientes = carregar_pacientes()

    if df_leitos.empty:
        st.warning("Nenhum leito cadastrado")
        return

    mapa_leitos(df_leitos)

    st.markdown("---")

    leito = st.session_state.get("leito_sel")

    if leito:

        st.subheader(f"Leito {leito['numero']}")

        if leito["status"] == "livre":

            if df_pacientes.empty:
                st.warning("Nenhum paciente cadastrado")
                return

            paciente_nome = st.selectbox(
                "Selecionar paciente",
                df_pacientes["nome"]
            )

            if st.button("Internar"):

                paciente_id = df_pacientes[
                    df_pacientes["nome"] == paciente_nome
                ]["id"].values[0]

                internar(paciente_id, leito["id"])
                st.success("Paciente internado")
                st.rerun()

        elif leito["status"] == "ocupado":

            st.info(f"Paciente: {leito.get('paciente', '---')}")

            if st.button("Dar alta"):
                dar_alta(leito["id"])
                st.success("Alta realizada")
                st.rerun()