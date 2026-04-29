import streamlit as st
import auth

st.set_page_config(
    page_title="Hospital Centenário",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 🎨 CSS PREMIUM
# =========================
st.markdown("""
<style>

/* FUNDO */
[data-testid="stAppViewContainer"] {
    background: #0b1220;
}

/* HEADER */
header[data-testid="stHeader"] {
    background: transparent;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1f2937;
}

/* LOGO */
.logo {
    text-align: center;
    padding: 10px;
}

/* MENU */
.menu-item {
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    cursor: pointer;
    background: #111827;
    border: 1px solid #1f2937;
}
.menu-item:hover {
    background: #1f2937;
}

/* HEADER TOPO */
.topbar {
    background: #020617;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    display: flex;
    justify-content: space-between;
}

/* CARDS */
.card {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

/* BOTÃO */
.stButton>button {
    border-radius: 10px;
    background: #111827;
    color: white;
    border: 1px solid #1f2937;
}
.stButton>button:hover {
    background: #1f2937;
}

/* TEXTO */
h1,h2,h3,h4,p,span,label {
    color: #e5e7eb;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 AUTH
# =========================
auth.init_session()

if not st.session_state.get("logado"):
    auth.restaurar_sessao()

auth.manter_sessao()

# =========================
# 🔐 LOGIN
# =========================
if not st.session_state.get("logado"):

    st.markdown("<h2 style='text-align:center'>Sistema Hospitalar</h2>", unsafe_allow_html=True)

    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if auth.login(user, senha):
            st.rerun()
        else:
            st.error("Erro login")

    st.stop()

# =========================
# 🧭 SIDEBAR MENU
# =========================
with st.sidebar:

    st.markdown("<div class='logo'>", unsafe_allow_html=True)
    st.image("assets/logo_transparent.png", width=120)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Menu")

    menu = st.radio(
        "",
        [
            "📊 Dashboard",
            "🏥 Internação",
            "💰 Financeiro",
            "📦 Estoque",
            "👨‍💼 RH",
            "🧾 Convênios",
            "👥 Usuários"
        ]
    )

    st.markdown("---")

    st.write(f"👤 {st.session_state.get('usuario')}")

    if st.button("Sair"):
        auth.logout()

# =========================
# 🔝 HEADER TOPO
# =========================
st.markdown("""
<div class='topbar'>
    <div>
        <h3 style='margin:0'>Hospital Centenário</h3>
        <small>Sistema Integrado</small>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================
# 🚀 ROTAS
# =========================
try:
    if "Dashboard" in menu:
        from modulos import dashboard
        dashboard.tela()

    elif "Internação" in menu:
        from modulos import internacao
        internacao.tela()

    elif "Financeiro" in menu:
        from modulos import financeiro
        financeiro.tela()

    elif "Estoque" in menu:
        from modulos import estoque
        estoque.tela()

    elif "RH" in menu:
        from modulos import rh
        rh.tela()

    elif "Convênios" in menu:
        from modulos import convenios
        convenios.tela()

    elif "Usuários" in menu:
        from modulos import usuarios
        usuarios.tela()

except Exception as e:
    st.error(f"Erro: {e}")