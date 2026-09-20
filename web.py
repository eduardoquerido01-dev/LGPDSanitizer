import streamlit as st
import json
import csv
import re
import io
from faker import Faker

fake = Faker('pt_BR')

def anonimizar_registro(registro):
    if isinstance(registro, dict):
        for chave, valor in registro.items():
            if isinstance(valor, str):
                if re.search(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', valor):
                    registro[chave] = fake.cpf()
                elif '@' in valor and '.' in valor:
                    registro[chave] = fake.email()
                elif 'nome' in chave.lower():
                    registro[chave] = fake.name()
                elif 'telefone' in chave.lower() or 'celular' in chave.lower():
                    registro[chave] = fake.cellphone_number()
            elif isinstance(valor, dict):
                anonimizar_registro(valor)
    elif isinstance(registro, list):
        for item in registro:
            anonimizar_registro(item)
    return registro

# Configuração da página e layout
st.set_page_config(page_title="LGPDSanitizer", page_icon="🛡️", layout="centered")

st.title("🛡️ LGPDSanitizer")
st.subheader("Sanitização e Mascaramento de Dados para Conformidade com a LGPD")
st.markdown("Carregue o seu arquivo (**JSON, CSV ou SQL**) para remover dados sensíveis (PII) instantaneamente.")

st.divider()

# Upload de arquivo
arquivo_enviado = st.file_uploader("Arraste e solte o seu arquivo aqui", type=["json", "csv", "sql"])

if arquivo_enviado is not None:
    nome_arquivo = arquivo_enviado.name
    extensao = nome_arquivo.split(".")[-1].lower()

    st.info(f"📁 Arquivo selecionado: `{nome_arquivo}` ({extensao.upper()})")

    if st.button("🚀 Sanitizar Arquivo Agora", type="primary", use_container_width=True):
        with st.spinner("Processando e anonimizando os dados..."):
            conteudo = arquivo_enviado.getvalue().decode("utf-8")

            if extensao == "json":
                dados = json.loads(conteudo)
                dados_sanitizados = anonimizar_registro(dados)
                resultado = json.dumps(dados_sanitizados, indent=2, ensure_ascii=False)
                mimetype = "application/json"

            elif extensao == "csv":
                leitor = list(csv.DictReader(io.StringIO(conteudo)))
                dados_sanitizados = anonimizar_registro(leitor)
                
                output = io.StringIO()
                escritor = csv.DictWriter(output, fieldnames=dados_sanitizados[0].keys())
                escritor.writeheader()
                escritor.writerows(dados_sanitizados)
                resultado = output.getvalue()
                mimetype = "text/csv"

            elif extensao == "sql":
                linhas = conteudo.splitlines(True)
                linhas_sanitizadas = []
                for linha in linhas:
                    linha_mod = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', lambda m: fake.cpf(), linha)
                    linha_mod = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', lambda m: fake.email(), linha_mod)
                    linhas_sanitizadas.append(linha_mod)
                resultado = "".join(linhas_sanitizadas)
                mimetype = "text/plain"

        st.success("✅ Processamento concluído com sucesso!")
        
        # Área de Prévia dos Dados
        with st.expander("👁️ Ver prévia dos dados sanitizados", expanded=True):
            st.code(resultado[:1000] + ("\n..." if len(resultado) > 1000 else ""), language=extensao)

        # Botão para Baixar
        nome_saida = f"sanitizado_{nome_arquivo}"
        st.download_button(
            label="📥 Descarregar Arquivo Sanitizado",
            data=resultado,
            file_name=nome_saida,
            mime=mimetype,
            use_container_width=True
        )