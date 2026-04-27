import streamlit as st
import pandas as pd
from conexao import supabase, safe_query


# =========================
# 🧠 INTERNAR PACIENTE
# =========================
def internar(nome, medico, quarto, leito):

    try:
        supabase.table("internacoes").insert({
            "nome_paciente": nome,
            "medico": medico,
            "quarto": quarto,
            "leito": leito,
            "status": "internado"
        }).execute()

        return True

    except Exception as e:
        st.error(f"Erro: {e}")
        return False


# =========================
# 🏥 DAR ALTA
# =========================
def dar_alta(id):

    try:
        supabase.table("internacoes") \
            .update({
                "status": "alta",
                "data_alta": "now()"
            }) \
            .eq("id", id) \
            .execute()

        return True

    except Exception as e:
        st.error(f"Erro: {e}")
        return False


# =========================
# 📄 TELA
# =========================
def tela():

    st.title("🏥 Internações")

    aba1, aba2 = st.tabs(["Internar", "Pacientes Internados"])

    # =========================
    # ➕ INTERNAR
    # =========================
    with aba1:

        st.subheader("Nova Internação")

        nome = st.text_input("Nome do paciente")
        medico = st.text_input("Médico responsável")

        col1, col2 = st.columns(2)

        with col1:
            quarto = st.text_input("Quarto")

        with col2:
            leito = st.text_input("Leito")

        if st.button("Internar paciente", use_container_width=True):

            if not nome:
                st.warning("Informe o nome")
            else:
                if internar(nome, medico, quarto, leito):
                    st.success("Paciente internado!")
                    st.rerun()

    # =========================
    # 📋 LISTA
    # =========================
    with aba2:

        res = safe_query(lambda: supabase.table("internacoes")
                         .select("*")
                         .order("data_entrada", desc=True)
                         .execute())

        df = pd.DataFrame(res.data if res else [])

        if df.empty:
            st.info("Nenhuma internação")
            return

        for _, row in df.iterrows():

            with st.container():

                col1, col2, col3, col4, col5 = st.columns([3,2,2,2,1])

                col1.write(f"**{row['nome_paciente']}**")
                col2.write(row.get("medico", ""))
                col3.write(f"Quarto {row.get('quarto','')}")
                col4.write(f"Status: {row.get('status','')}")

                if row["status"] == "internado":
                    if col5.button("Alta", key=row["id"]):
                        dar_alta(row["id"])
                        st.rerun()