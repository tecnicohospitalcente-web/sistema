from supabase import create_client
import streamlit as st

# =========================
# 🔌 CONEXÃO SUPABASE
# =========================
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()


# =========================
# 🛡️ SAFE QUERY (SEGURO)
# =========================
def safe_query(func, tentativas=3):
    for i in range(tentativas):
        try:
            return func()
        except Exception as e:
            print(f"Erro tentativa {i+1}: {e}")

    return None