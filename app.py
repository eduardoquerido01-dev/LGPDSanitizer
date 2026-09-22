import streamlit as st
import pandas as pd
import re
import io

st.set_page_config(page_title="Anificador LGPDS - Sanitizador de Dados", layout="wide")

st.title("🛡️ Anificador LGPDS - Sanitização de Dados (LGPD)")
st.write("Proteja a privacidade dos seus clientes anonimizando dados sensíveis (PII) instantaneamente.")

# Funções de mascaramento
def mask_email(email):
    if not isinstance(email, str) or '@' not in email:
        return email
    parts = email.split('@')
    user = parts[0]
    domain = parts[1]
    masked_user = user[0] + '***' if len(user) > 1 else '***'
    return f"{masked_user}@{domain}"

def mask_cpf(cpf):
    if not isinstance(cpf, str):
        cpf = str(cpf)
    digits = re.sub(r'\D', '', cpf)
    if len(digits) == 11:
        return f"***.***.***-{digits[-2:]}"
    return cpf

def mask_phone(phone):
    if not isinstance(phone, str):
        phone = str(phone)
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 10:
        ddd = digits[:2]
        last_four = digits[-4:]
        return f"({ddd}) *****-{last_four}"
    return phone

def sanitize_dataframe(df):
    df_clean = df.copy()
    for col in df_clean.columns:
        col_lower = col.lower()
        if 'email' in col_lower or 'e-mail' in col_lower:
            df_clean[col] = df_clean[col].apply(mask_email)
        elif 'cpf' in col_lower:
            df_clean[col] = df_clean[col].apply(mask_cpf)
        elif 'telefone' in col_lower or 'phone' in col_lower or 'celular' in col_lower or 'tel' in col_lower:
            df_clean[col] = df_clean[col].apply(mask_phone)
    return df_clean

# Upload do Ficheiro
uploaded_file = st.file_uploader("Envie a sua planilha (.csv) para sanitização", type=["csv"])

if uploaded_file is not None:
    try:
        # Leitura diretamente da memória RAM
        df = pd.read_csv(uploaded_file)
        
        st.subheader("📋 Prévia dos Dados Originais")
        st.dataframe(df.head(5), use_container_width=True)
        
        # Modo de Demonstração (Freemium): limita a 10 linhas
        total_rows = len(df)
        limit_rows = 10
        
        if total_rows > limit_rows:
            st.warning(f"⚠️ **Modo Demonstração Gratuito:** Sua planilha possui **{total_rows} linhas**, mas na versão gratuita apenas as **primeiras {limit_rows} linhas** serão processadas.")
            df_to_process = df.head(limit_rows)
        else:
            df_to_process = df
            
        # Processamento em memória
        df_sanitized = sanitize_dataframe(df_to_process)
        
        st.subheader("🔒 Prévia dos Dados Sanitizados (Protegidos)")
        st.dataframe(df_sanitized, use_container_width=True)
        
        # Download da versão gratuita
        csv_buffer = io.BytesIO()
        df_sanitized.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_buffer.seek(0)
        
        st.download_button(
            label="⬇️ Descarregar Arquivo Sanitizado (Amostra Grátis)",
            data=csv_buffer,
            file_name="dados_sanitizados_amostra.csv",
            mime="text/csv"
        )
        
        # Banners Comercial de Upsell para o Plano Pago
        st.divider()
        st.info("🚀 **Precisa processar a planilha completa sem limite de linhas?**\n\n"
                "Desbloqueie o **Plano Empresarial Pro** e tenha acesso a:\n"
                "- Processamento de arquivos ilimitados sem restrição de linhas\n"
                "- Suporte prioritário via WhatsApp/E-mail\n"
                "- Garantia de conformidade total e relatório de auditoria\n\n"
                "👉 **[Clique aqui para assinar por R$ 99/mês](https://asasa.com.br)** *(Link de pagamento demonstrativo)*")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")