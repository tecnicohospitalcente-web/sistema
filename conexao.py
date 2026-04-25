from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()

def safe_query(func):
    try:
        return func()
    except Exception as e:
        print("Erro Supabase:", e)
        return None
