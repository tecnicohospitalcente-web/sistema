import streamlit as st
import auth

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="Hospital Centenário",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 🎨 CSS PROFISSIONAL REAL
# =========================
st.markdown("""
<style>

/* FUNDO */
[data-testid="stAppViewContainer"] {
    background: #0b1220;
}

/* REMOVE HEADER */
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
    margin-bottom: 15px;
}

/* MENU */
.stButton>button {
    width: 100%;
    text-align: left;
    background: #020617;
    border: none;
    padding: 12px;
    border-radius: 8px;
    color: #9ca3af;
    font-size: 14px;
}

/* HOVER */
.stButton>button:hover {
    background: #111827;
    color: white;
}

/* ATIVO */
.menu-ativo {
    background: #00A86B !important;
    color: white !important;
    font-weight: 600;
}

/* TOPBAR */
.topbar {
    background: #020617;
    padding: 18px 25px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* CARDS */
.card {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

/* TEXTO */
h1,h2,h3,h4,p,span,label {
    color: #e5e7eb;
}

/* SCROLL */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #1f2937;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🔐 AUTH
# =========================
auth.init_session()

if not st.session_state.get("logado"):
    auth.restaurar_sessao()

auth.manter_sessao()

# =========================
# LOGIN
# =========================
if not st.session_state.get("logado"):

    col1, col2, col3 = st.columns([2,2,2])

    with col2:
        st.image("assets/logo_transparent.png", width=180)
        st.markdown("### Sistema Hospitalar")

        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            if auth.login(user, senha):
                st.rerun()
            else:
                st.error("Usuário inválido")

    st.stop()

# =========================
# MENU STATE
# =========================
if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

# =========================
# SIDEBAR (REAL)
# =========================
with st.sidebar:

    st.markdown("<div class='logo'>", unsafe_allow_html=True)
    st.image("assets/logo_transparent.png", width=110)
    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Sistema Hospitalar")

    opcoes = [
        "Dashboard",
        "Paciente",
        "Internação",
        "Prontuário",
        "Financeiro",
        "Estoque",
        "RH",
        "Convênios",
        "Usuários"
    ]

    for opcao in opcoes:

        is_active = st.session_state.menu == opcao

        btn = st.button(
            f"{'● ' if is_active else ''}{opcao}",
            key=opcao,
            use_container_width=True
        )

        if btn:
            st.session_state.menu = opcao
            st.rerun()

    st.markdown("---")
    st.caption(f"👤 {st.session_state.get('usuario')}")

    if st.button("Sair", use_container_width=True):
        auth.logout()

menu = st.session_state.menu

# =========================
# TOPBAR PROFISSIONAL
# =========================
col1, col2 = st.columns([6,2])

with col1:
    st.markdown(f"""
    <div class='topbar'>
        <div>
            <h3 style='margin:0'>🏥 Hospital Centenário</h3>
            <small style='color:#9ca3af'>{menu}</small>
        </div>
        <div style='color:#9ca3af'>
            🟢 Online
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# ROTAS
# =========================
try:
    if menu == "Dashboard":
        from modulos import dashboard
        dashboard.tela()
    
    elif menu == "Paciente":
        from modulos import pacientes
        pacientes.tela()

    elif menu == "Internação":
        from modulos import internacao
        internacao.tela()

    elif menu == "Prontuário":
        from modulos import prontuario
        prontuario.tela()

    elif menu == "Financeiro":
        from modulos import financeiro
        financeiro.tela()

    elif menu == "Estoque":
        from modulos import estoque
        estoque.tela()

    elif menu == "RH":
        from modulos import rh
        rh.tela()

    elif menu == "Convênios":
        from modulos import convenios
        convenios.tela()

    elif menu == "Usuários":
        from modulos import usuarios
        usuarios.tela()

except Exception as e:
    st.error(f"Erro: {e}")