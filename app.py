import streamlit as st
import auth

# =========================
# 🚀 CARREGAMENTO DINÂMICO (ANTI-LENTO)
# =========================
def carregar_modulo(nome):
    if nome == "Internação":
        from modulos import internacao
        internacao.tela()

    elif nome == "Dashboard":
        from modulos import dashboard
        dashboard.tela()

    elif nome == "Financeiro":
        from modulos import financeiro
        financeiro.tela()

    elif nome == "RH":
        from modulos import rh
        rh.tela()

    elif nome == "Estoque":
        from modulos import estoque
        estoque.tela()

    elif nome == "Convênios":
        from modulos import convenios
        convenios.tela()

    elif nome == "Usuários":
        from modulos import usuarios
        usuarios.tela()


# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="Hospital Centenário",
    page_icon="assets/icon_128.png",
    layout="wide"
)

# =========================
# 🎨 CSS (leve e rápido)
# =========================
st.markdown("""
<style>
.main { background-color: #0f172a; }
h1,h2,h3,h4,p,span { color: white; }

.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 42px;
    background-color: #111827;
    color: white;
    border: 1px solid #1f2937;
    transition: 0.2s;
}
.stButton>button:hover {
    background-color: #1f2937;
    border-color: #00A86B;
}

div[role="radiogroup"] {
    display: flex;
    gap: 8px;
}

div[role="radiogroup"] label {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 10px;
    border-radius: 10px;
}

div[role="radiogroup"] input:checked + div {
    background-color: #00A86B !important;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🧠 SESSÃO
# =========================
auth.init_session()

if not st.session_state.get("logado"):
    auth.restaurar_sessao()

auth.manter_sessao()

# =========================
# 🔐 LOGIN
# =========================
if not st.session_state.get("logado"):

    col1, col2, col3 = st.columns([2,3,2])

    with col2:
        st.image("assets/logo_transparent.png", width=200)

        user = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):
            if auth.login(user, senha):
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
    st.markdown("## Hospital Centenário")

with col3:
    st.write(f"👤 {st.session_state.get('usuario')}")
    if st.button("Sair"):
        auth.logout()

st.markdown("---")

# =========================
# 📋 MENU
# =========================
tipo = st.session_state.get("tipo")

opcoes = []

if tipo in ["admin","financeiro"]:
    opcoes.append("💰 Financeiro")

if tipo in ["admin","rh"]:
    opcoes.append("👨‍💼 RH")

if tipo in ["admin","estoque"]:
    opcoes.append("📦 Estoque")

if tipo == "admin":
    opcoes.append("🧾 Convênios")
    opcoes.append("👥 Usuários")

opcoes.append("🏥 Internação")
opcoes.append("📊 Dashboard")

menu = st.radio("", opcoes, horizontal=True)

st.markdown("---")

# =========================
# 🚀 CARREGA SÓ O NECESSÁRIO
# =========================
try:
    for nome in opcoes:
        if nome in menu:
            carregar_modulo(nome.replace("🏥 ", "").replace("📊 ", "").replace("💰 ", "").replace("👨‍💼 ", "").replace("📦 ", "").replace("🧾 ", "").replace("👥 ", ""))

except Exception as e:
    st.error(f"Erro: {e}")