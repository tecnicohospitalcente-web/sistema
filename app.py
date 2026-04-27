import streamlit as st
from auth import init_session, restaurar_sessao, manter_sessao, login, logout
from modulos import internacao, dashboard, financeiro, rh, estoque, convenios, usuarios

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="Hospital Centenário",
    page_icon="assets/icon_128.png",
    layout="wide"
)

# =========================
# 🎨 CSS PROFISSIONAL + ANIMAÇÃO
# =========================
st.markdown("""
<style>

/* FUNDO */
.main { background-color: #0f172a; }

/* TEXTOS */
h1,h2,h3,h4,p,span { color: white; }

/* NAVBAR */
.navbar {
    background: #020617;
    padding: 10px 20px;
    border-radius: 10px;
    border: 1px solid #1f2937;
}

/* BOTÕES */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 42px;
    background-color: #111827;
    color: white;
    border: 1px solid #1f2937;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    background-color: #1f2937;
    transform: translateY(-2px);
    border-color: #00A86B;
}

/* MENU RADIO */
div[role="radiogroup"] {
    display: flex;
    gap: 8px;
}

div[role="radiogroup"] label {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.25s ease;
}

/* HOVER */
div[role="radiogroup"] label:hover {
    background-color: #1f2937;
    transform: translateY(-2px);
}

/* ATIVO */
div[role="radiogroup"] input:checked + div {
    background-color: #00A86B !important;
    border: none;
    font-weight: bold;
}

/* ANIMAÇÃO */
.fade {
    animation: fadeIn 0.25s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
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
# 🔐 LOGIN
# =========================
if not st.session_state.logado:

    col1, col2, col3 = st.columns([2,3,2])

    with col2:
        st.image("assets/logo_transparent.png", width=200)

        st.markdown("<h3 style='text-align:center;'>Sistema Hospitalar</h3>", unsafe_allow_html=True)

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
    st.image("assets/logo_transparent.png", width=140)

with col2:
    st.markdown("""
    <h2 style='margin:0;'>Hospital Centenário</h2>
    <p style='color:gray;margin:0;'>Sistema Administrativo</p>
    """, unsafe_allow_html=True)

with col3:
    st.write(f"👤 {st.session_state.usuario}")
    if st.button("Sair"):
        logout()

st.markdown("---")

# =========================
# 📋 MENU (DASHBOARD ÚLTIMO)
# =========================
tipo = st.session_state.tipo

opcoes = []

# ORDEM CORRETA (SISTEMA REAL)
if tipo in ["admin","financeiro"]:
    opcoes.append("💰 Financeiro")

if tipo in ["admin","rh"]:
    opcoes.append("👨‍💼 RH")

if tipo in ["admin","estoque"]:
    opcoes.append("📦 Estoque")

if tipo == "admin":
    opcoes.append("🧾 Convênios")
    opcoes.append("👥 Usuários")

# 🔥 NOVO MÓDULO
opcoes.append("🏥 Internação")

# 🔥 DASHBOARD POR ÚLTIMO
opcoes.append("📊 Dashboard")

menu = st.radio("", opcoes, horizontal=True)

st.markdown("---")

# =========================
# 📄 ROTAS COM ANIMAÇÃO
# =========================
container = st.container()
container.markdown("<div class='fade'>", unsafe_allow_html=True)

try:
    if "Financeiro" in menu:
        financeiro.tela()

    elif "RH" in menu:
        rh.tela()

    elif "Estoque" in menu:
        estoque.tela()

    elif "Convênios" in menu:
        convenios.tela()

    elif "Usuários" in menu:
        usuarios.tela()

    elif "Internação" in menu:
        internacao.tela()

    elif "Dashboard" in menu:
        dashboard.tela()

except Exception as e:
    st.error(f"Erro ao carregar módulo: {e}")

container.markdown("</div>", unsafe_allow_html=True)