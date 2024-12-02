import streamlit as st
from supabase import create_client, Client
from estilo import aplicar_estilo

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

    col1, col2 = st.columns(2)

    # Dicionário para armazenar os dados do cliente
    cliente = {}

    with col2:
        st.write("Cadastramento")
        # Entradas de dados para o cliente
        cliente_nome = st.text_input("Nome do Cliente")
        cliente_contato = st.text_input("Contato do Cliente")
        cliente_endereco = st.text_input("Endereço do Cliente")
        cliente_email = st.text_input("Email do Cliente")

        # Preencher o dicionário com os dados fornecidos
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
                    # Verificar se o cliente já existe no Supabase
                    resposta = supabase.table("clientes").select("nome").filter("nome", "eq", cliente_nome).filter("user_id", "eq", user_id).execute()
                    if resposta.data:
                        st.error("Já existe um cliente com esse nome associado a este usuário.")
                    else:
                        # Adicionar o cliente ao Supabase
                        cliente["user_id"] = user_id  # Associar o cliente ao usuário logado
                        supabase.table("clientes").insert(cliente).execute()
                        st.success("Cliente cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar cliente: {e}")
            else:
                st.error("Por favor, preencha todos os campos.")

