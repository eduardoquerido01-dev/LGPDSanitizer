import streamlit as st
import pandas as pd
import json
import re
from supabase import create_client

# Configuração da página
st.set_page_config(page_title="LGPDSanitizer", page_icon="🛡️", layout="wide")

# Inicialização do Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Estado da sessão para utilizador
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------------------------------------------
# FUNÇÕES DE SANITIZAÇÃO (MASCARAMENTO DE PII)
# -------------------------------------------------------------
def mask_cpf(text):
    if not isinstance(text, str):
        text = str(text)
    # Procura CPFs com ou sem pontuação
    cpf_pattern = r'\b\d{3}[\.\s]?\d{3}[\.\s]?\d{3}[-\s]?\d{2}\b'
    return re.sub(cpf_pattern, '***.***.***-**', text)

def mask_email(text):
    if not isinstance(text, str):
        text = str(text)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    def replace_email(match):
        email = match.group(0)
        parts = email.split('@')
        name = parts[0]
        domain = parts[1]
        masked_name = name[0] + '***' if len(name) > 1 else '***'
        return f"{masked_name}@{domain}"
    return re.sub(email_pattern, replace_email, text)

def mask_phone(text):
    if not isinstance(text, str):
        text = str(text)
    # Captura telefones com ou sem +55, DDD e hífen
    phone_pattern = r'(\+?55\s?)?(\(?\d{2}\)?\s?)?(\d{4,5})[-.\s]?(\d{4})'
    return re.sub(phone_pattern, r'\1\2*****-\4', text)

def sanitize_value(val):
    if isinstance(val, str):
        val = mask_cpf(val)
        val = mask_email(val)
        val = mask_phone(val)
    return val

# -------------------------------------------------------------
# TELA DE AUTENTICAÇÃO E PAINEL PRINCIPAL
# -------------------------------------------------------------
st.title("🛡️ LGPDSanitizer")
st.subheader("Sanitização e Mascaramento de Dados em Conformidade com a LGPD")
st.write("Carregue o seu arquivo (CSV ou JSON) para remover dados sensíveis (PII) instantaneamente.")

uploaded_file = st.file_uploader("Arraste e solte o seu arquivo aqui", type=["csv", "json"])

if uploaded_file is not None:
    st.info(f"📁 Arquivo selecionado: **{uploaded_file.name}**")
    
    if st.button("🚀 Sanitizar Arquivo Agora", type="primary"):
        file_type = uploaded_file.name.split(".")[-1].lower()

        if file_type == "csv":
            df = pd.read_csv(uploaded_file, dtype=str)
            # Aplica o mascaramento em todas as células
            df_sanitized = df.map(sanitize_value)

            st.success("✅ Processamento concluído com sucesso!")
            
            with st.expander("👁️ Ver prévia dos dados sanitizados", expanded=True):
                st.dataframe(df_sanitized)

            csv_data = df_sanitized.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarregar Arquivo Sanitizado",
                data=csv_data,
                file_name=f"sanitizado_{uploaded_file.name}",
                mime="text/csv"
            )

        elif file_type == "json":
            data = json.load(uploaded_file)
            raw_str = json.dumps(data)
            sanitized_str = sanitize_value(raw_str)
            sanitized_json = json.loads(sanitized_str)

            st.success("✅ Processamento concluído com sucesso!")
            
            with st.expander("👁️ Ver prévia dos dados sanitizados", expanded=True):
                st.json(sanitized_json)

            st.download_button(
                label="📥 Descarregar Arquivo Sanitizado",
                data=json.dumps(sanitized_json, indent=2),
                file_name=f"sanitizado_{uploaded_file.name}",
                mime="application/json"
            )