from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()


def safe_query(func, tentativas=3):
    for i in range(tentativas):
        try:
            return func()
        except Exception as e:
            print(f"Erro tentativa {i+1}: {e}")
            try:
                supabase.auth.get_user()
            except:
                pass
            if i == tentativas - 1:
                return None