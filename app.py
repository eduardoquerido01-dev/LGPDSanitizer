import sys
import os
import json
import csv
import re
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

def processar_arquivo(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return

    nome_base, extensao = os.path.splitext(caminho_arquivo)
    extensao = extensao.lower()
    caminho_saida = f"{nome_base}_sanitizado{extensao}"

    if extensao == '.json':
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        dados_sanitizados = anonimizar_registro(dados)
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_sanitizados, f, indent=2, ensure_ascii=False)
            
    elif extensao == '.csv':
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            leitor = list(csv.DictReader(f))
        dados_sanitizados = anonimizar_registro(leitor)
        with open(caminho_saida, 'w', encoding='utf-8', newline='') as f:
            escritor = csv.DictWriter(f, fieldnames=dados_sanitizados[0].keys())
            escritor.writeheader()
            escritor.writerows(dados_sanitizados)

    elif extensao == '.sql':
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        linhas_sanitizadas = []
        for linha in linhas:
            linha_mod = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', lambda m: fake.cpf(), linha)
            linha_mod = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', lambda m: fake.email(), linha_mod)
            linhas_sanitizadas.append(linha_mod)
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.writelines(linhas_sanitizadas)

    print(f" Sucesso! Arquivo sanitizado gerado: {caminho_saida}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        processar_arquivo(sys.argv[1])
    else:
        print("Uso: python app.py <nome_do_arquivo>")