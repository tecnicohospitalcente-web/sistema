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

/* ===== FUNDO GERAL ===== */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0f172a;
}

/* REMOVE FUNDO BRANCO DO TOPO */
header[data-testid="stHeader"] {
    background: transparent;
}

/* REMOVE FUNDO BRANCO LATERAL */
section[data-testid="stSidebar"] {
    background-color: #020617;
}

/* ===== CONTAINER PRINCIPAL ===== */
.main {
    background-color: #0f172a;
}

/* ===== TEXTOS ===== */
h1, h2, h3, h4, h5, h6, p, span, label {
    color: #e5e7eb !important;
}

/* ===== NAVBAR ===== */
.navbar {
    background: #020617;
    padding: 12px 20px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* ===== CARDS ===== */
.card {
    background: linear-gradient(145deg, #111827, #1f2937);
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
}

/* ===== BOTÕES ===== */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 42px;
    background-color: #111827;
    color: white;
    border: 1px solid #1f2937;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background-color: #1f2937;
    border-color: #00A86B;
    transform: translateY(-1px);
}

/* ===== MENU ===== */
div[role="radiogroup"] {
    display: flex;
    gap: 10px;
}

div[role="radiogroup"] label {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 10px 16px;
    border-radius: 10px;
    cursor: pointer;
    transition: 0.2s;
}

div[role="radiogroup"] label:hover {
    background: #1f2937;
}

/* ITEM ATIVO */
div[role="radiogroup"] input:checked + div {
    background: linear-gradient(90deg, #00A86B, #059669);
    border: none;
    font-weight: bold;
}

/* ===== INPUTS ===== */
input, textarea, select {
    background-color: #020617 !important;
    color: white !important;
    border: 1px solid #1f2937 !important;
}

/* ===== SCROLL ===== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #1f2937;
    border-radius: 10px;
}

/* ===== ANIMAÇÃO ===== */
.fade {
    animation: fadeIn 0.25s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
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
col1, col2, col3 = st.columns([1,6,2])

with col1:
    st.image("assets/logo_transparent.png", width=120)

with col2:
    st.markdown("""
    <div class='navbar'>
        <div>
            <h3 style='margin:0;'>Hospital Centenário</h3>
            <small style='color:gray;'>Sistema Hospitalar Integrado</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

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