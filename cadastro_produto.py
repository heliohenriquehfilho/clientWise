import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Configuração do Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def renderizar_cadastro_de_produto(user_id):
    st.header("📝 Cadastro de Produto")

    # Campos do produto
    produto_nome = st.text_input("Nome do Produto")
    produto_descricao = st.text_input("Descrição do Produto")
    produto_valor = st.number_input("Valor do produto")
    produto_tipo = st.selectbox("Qual a forma do produto: ", ["Fisico", "Digital"])

    produto = {}

    if produto_nome:
        produto["nome"] = produto_nome
    if produto_descricao:
        produto["descricao"] = produto_descricao
    if produto_valor:
        produto["preco"] = produto_valor
    if produto_tipo:
        if produto_tipo == "Fisico":
            produto["tipo"] = produto_tipo
            produto_quantidade = st.number_input("Quantidade do produto")
            if produto_quantidade:
                produto["quantidade"] = int(produto_quantidade)
        elif produto_tipo == "Digital":
            produto["tipo"] = produto_tipo
            produto["quantidade"] = 0

    # Associar o produto ao user_id
    produto["user_id"] = user_id  # Associar ao usuário logado

    # Salvar no Supabase
    if st.button("Cadastrar Produto"):
        if produto:
            try:
                # Inserir o produto no banco de dados do Supabase
                resposta = supabase.table("produtos").select("nome").filter("nome", "eq", produto_nome).filter("user_id", "eq", user_id).execute()
                if resposta.data:
                    st.error("Já existe um cliente com esse nome associado a este usuário.")
                else:
                    produto["user_id"] = user_id
                    supabase.table("produtos").insert(produto).execute()
                    st.success("Produto cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar produto: {e}")
        else:
            st.error("Por favor, preencha todos os campos.")