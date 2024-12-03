import streamlit as st
from supabase import create_client, Client
from estilo import aplicar_estilo
import pandas as pd

# Configuração do Supabase
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")

supabase: Client = create_client(url, key)

def renderizar_cadastro_cliente(user_id):
    aplicar_estilo()

    if not user_id:
        st.error("Usuário não autenticado. Por favor, faça login novamente.")
        return

    st.header("👤 Cadastro de Cliente")

    # Opção de cadastro manual ou via CSV
    opcao_cadastro = st.radio(
        "Como deseja cadastrar os clientes?",
        options=["Cadastro Manual", "Upload de CSV"],
        horizontal=True
    )

    if opcao_cadastro == "Cadastro Manual":
        # Cadastro manual como já implementado
        col1, col2 = st.columns(2)
        cliente = {}

        with col2:
            st.write("Cadastramento")
            cliente_nome = st.text_input("Nome do Cliente")
            cliente_contato = st.text_input("Contato do Cliente")
            cliente_endereco = st.text_input("Endereço do Cliente")
            cliente_email = st.text_input("Email do Cliente")

            if cliente_nome:
                cliente["nome"] = cliente_nome
            if cliente_contato:
                cliente["contato"] = cliente_contato
            if cliente_endereco:
                cliente["endereco"] = cliente_endereco
            if cliente_email:
                cliente["email"] = cliente_email

            if st.button("Cadastrar Cliente"):
                if cliente_nome and cliente_contato and cliente_endereco and cliente_email:
                    try:
                        resposta = supabase.table("clientes").select("nome").filter("nome", "eq", cliente_nome).filter("user_id", "eq", user_id).execute()
                        if resposta.data:
                            st.error("Já existe um cliente com esse nome associado a este usuário.")
                        else:
                            cliente["user_id"] = user_id
                            supabase.table("clientes").insert(cliente).execute()
                            st.success("Cliente cadastrado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao cadastrar cliente: {e}")
                else:
                    st.error("Por favor, preencha todos os campos.")
    
    elif opcao_cadastro == "Upload de CSV":
        # Upload de CSV
        uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])

        if uploaded_file:
            # Ler o CSV e exibir o DataFrame
            data = pd.read_csv(uploaded_file, encoding='utf-8')
            st.write("Pré-visualização dos dados:")
            st.dataframe(data.head())
            total_clientes = len(data)

            # Mapear as colunas
            st.markdown("### Mapear Colunas")
            colunas_disponiveis = list(data.columns)
            mapeamento = {
                "nome": st.selectbox("Coluna para o Nome", colunas_disponiveis),
                "contato": st.selectbox("Coluna para o Contato", colunas_disponiveis),
                "endereco": st.selectbox("Coluna para o Endereço", colunas_disponiveis),
                "email": st.selectbox("Coluna para o Email", colunas_disponiveis)
            }

            if st.button("Importar Clientes"):
                erros = []
                duplicados = []  # Lista para armazenar os duplicados encontrados
                progresso = st.progress(0)
                for index, row in data.iterrows():
                    cliente = {
                        "nome": row.get(mapeamento["nome"]),
                        "contato": row.get(mapeamento["contato"]),
                        "endereco": row.get(mapeamento["endereco"]) if pd.notna(row.get(mapeamento["endereco"])) else "",
                        "email": row.get(mapeamento["email"]),
                        "user_id": user_id
                    }

                    # Verificar se os campos essenciais estão preenchidos (nome, contato, email)
                    if not all([cliente["nome"], cliente["contato"], cliente["email"]]):
                        erros.append(f"Dados incompletos na linha {index + 1}: {cliente}")
                        continue

                    # Exibir os dados que estão sendo enviados ao Supabase para depuração
                    # st.write(f"Enviando dados: {cliente}")

                    try:
                        # Verificar se o cliente já existe
                        resposta = supabase.table("clientes").select("nome").filter("nome", "eq", cliente["nome"]).filter("user_id", "eq", user_id).execute()
                        if resposta.data:
                            duplicados.append(cliente['nome'])  # Adicionar cliente duplicado à lista
                        else:
                            resposta_insert = supabase.table("clientes").insert(cliente).execute()
                            if resposta_insert.status_code != 201:
                                erros.append(f"Erro ao salvar {cliente['nome']}: {resposta_insert}")
                    except Exception as e:
                        erros.append(f"Erro ao salvar {cliente['nome']}: {e}")

                    progresso.progress((index + 1) / total_clientes)

                # Exibir mensagens sobre duplicados
                if duplicados:
                    st.warning(f"Os seguintes clientes são duplicados e não foram importados: {', '.join(duplicados)}")

                # Exibir erros se houver
                if erros:
                    st.warning(f"Alguns clientes não foram importados: {', '.join(erros)}")
                else:
                    st.success("Todos os clientes foram importados com sucesso!")




