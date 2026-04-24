from supabase import create_client
import streamlit as st

# =========================
# 🔐 CONEXÃO SEGURA
# =========================
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()

# =========================
# 🛡️ QUERY SEGURA (ANTI-ERRO)
# =========================
def safe_query(func, tentativas=2):

    for i in range(tentativas):
        try:
            return func()

        except Exception as e:

            # 🔥 tenta reconectar automaticamente
            try:
                supabase.auth.get_user()
            except:
                pass

            if i == tentativas - 1:
                print("Erro Supabase:", e)
                return None