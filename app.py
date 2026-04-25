import streamlit as st
from auth import init_session, restaurar_sessao, manter_sessao, login, logout
from modulos import dashboard, financeiro, rh, estoque, convenios, usuarios

# =========================
# ⚙️ CONFIG APP
# =========================
st.set_page_config(
    page_title="Hospital Centenário",
    page_icon="assets/icon_128.png",
    layout="wide"
)

# =========================
# 🎨 ESTILO GLOBAL (SaaS)
# =========================
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.block-container {
    padding-top: 2rem;
}
.stButton>button {
    border-radius: 8px;
    height: 45px;
    border: 1px solid #374151;
    background-color: #111827;
    color: white;
}
.stButton>button:hover {
    background-color: #00A86B;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 SESSÃO
# =========================
init_session()

if not st.session_state.logado:
    restaurar_sessao()

manter_sessao()

# =========================
# 🔐 LOGIN (PROFISSIONAL)
# =========================
if not st.session_state.logado:

    col1, col2, col3 = st.columns([2,3,2])

    with col2:
        st.image("assets/logo_transparent.png", width=220)

        st.markdown("""
        <h3 style='text-align:center;'>Sistema Hospitalar</h3>
        <p style='text-align:center; color:gray;'>Acesso restrito</p>
        """, unsafe_allow_html=True)

        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            if login(user, senha):
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

    st.stop()

# =========================
# 🔝 NAVBAR
# =========================
col1, col2, col3 = st.columns([2,6,2])

with col1:
    st.image("assets/logo_transparent.png", width=160)

with col2:
    st.markdown("""
    <h2 style='margin-bottom:0;'>Hospital Centenário</h2>
    <p style='color:gray; margin-top:0;'>Sistema Administrativo</p>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"👤 **{st.session_state.usuario}**")

    if st.button("Sair"):
        logout()

st.markdown("---")

# =========================
# 📋 MENU (TOP SAAS)
# =========================
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

tipo = st.session_state.tipo

col = st.columns(6)

if col[0].button("📊 Dashboard"):
    st.session_state.menu = "Dashboard"

if tipo in ["admin","financeiro"]:
    if col[1].button("💰 Financeiro"):
        st.session_state.menu = "Financeiro"

if tipo in ["admin","rh"]:
    if col[2].button("👨‍💼 RH"):
        st.session_state.menu = "RH"

if tipo in ["admin","estoque"]:
    if col[3].button("📦 Estoque"):
        st.session_state.menu = "Estoque"

if tipo == "admin":
    if col[4].button("🧾 Convênios"):
        st.session_state.menu = "Convênios"

if tipo == "admin":
    if col[5].button("👥 Usuários"):
        st.session_state.menu = "Usuarios"

menu = st.session_state.menu

st.markdown("---")

# =========================
# 📄 ROTAS
# =========================
try:

    if menu == "Dashboard":
        dashboard.tela()

    elif menu == "Financeiro":
        financeiro.tela()

    elif menu == "RH":
        rh.tela()

    elif menu == "Estoque":
        estoque.tela()

    elif menu == "Convênios":
        convenios.tela()

    elif menu == "Usuarios":
        usuarios.tela()

except Exception as e:
    st.error(f"Erro ao carregar módulo: {e}")