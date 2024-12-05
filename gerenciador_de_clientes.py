import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
import datetime

load_dotenv()

# Configuração do Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

min_date = datetime.date(1900, 1, 1)

def renderizar_gerenciador_de_clientes(user_id):
    st.header("🫂 Gerenciador de clientes")

    # Carregar clientes do Supabase
    clientes = supabase.table("clientes").select("*").eq("user_id", user_id).execute().data
    vendas = supabase.table('vendas').select("*").eq("user_id", user_id).execute().data

    st.dataframe(clientes, column_order=[
        "nome", "endereco", "email", "bairro", "cidade", 
        "estado", "cep", "ativo", "genero", "data_nascimento"
    ])

    if clientes:
        nome_cliente = [cliente["nome"] for cliente in clientes]
        cliente_selecionado = st.selectbox("Selecione o cliente", nome_cliente)

        # Buscar os dados do cliente selecionado
        cliente_atual = next((c for c in clientes if c["nome"] == cliente_selecionado), None)

        if cliente_atual:
            nome = cliente_atual.get("nome")
            contato = cliente_atual.get("contato", "Não encontrado")
            endereco = cliente_atual.get("endereco", "")
            email = cliente_atual.get("email", "")
            bairro = cliente_atual.get("bairro", "")
            cidade = cliente_atual.get("cidade", "")
            estado = cliente_atual.get("estado", "")
            cep = cliente_atual.get("cep", "")
            ativo = cliente_atual.get("ativo", False)
            genero = cliente_atual.get("genero", None)
            cliente_id = cliente_atual.get("client__c", 0)
            data_nascimento_valor = cliente_atual.get("data_nascimento")

            # Verificar se o gênero do cliente está na lista de opções
            genero_opcoes = ["Masculino", "Feminino", "Não Binário", None]
            if genero not in genero_opcoes:
                genero = "" # Valor padrão caso o gênero não esteja na lista

            # Formulário para edição do cliente
            # Formulário para edição do cliente
            cliente_nome = st.text_input("Nome do cliente", value=nome)
            cliente_contato = st.text_input("Contato do cliente", contato)
            cliente_endereco = st.text_input("Endereço do cliente", endereco)
            cliente_email = st.text_input("Endereço de email", email)
            cliente_bairro = st.text_input("Bairro do cliente", bairro)
            cliente_cidade = st.text_input("Cidade do cliente", cidade)
            cliente_estado = st.text_input("Estado do cliente", estado)
            cliente_cep = st.text_input("CEP do cliente", cep)
            cliente_ativo = st.checkbox("Cliente Ativo?", ativo)
            cliente_genero = st.selectbox("Gênero", genero_opcoes, index=genero_opcoes.index(genero))
            cliente_data_nascimento = st.date_input("Data de nascimento", value=pd.to_datetime(data_nascimento_valor), min_value=min_date)


            # Atualizar cliente
            if st.button("Salvar Cliente"):
                cliente_atualizado = {
                    "nome": cliente_nome,
                    "contato": cliente_contato,
                    "endereco": cliente_endereco,
                    "email": cliente_email,
                    "bairro": cliente_bairro,
                    "cidade": cliente_cidade,
                    "estado": cliente_estado,
                    "cep": cliente_cep,
                    "ativo": cliente_ativo,
                    "genero": cliente_genero,
                    "data_nascimento": str(cliente_data_nascimento)  # Converte para string no formato ISO
                }

                # Verificar duplicação antes de salvar
                resposta_duplicada = supabase.table("clientes")\
                    .select("id")\
                    .filter("nome", "eq", cliente_nome)\
                    .filter("contato", "eq", cliente_contato)\
                    .filter("email", "eq", cliente_email)\
                    .filter("user_id", "eq", user_id)\
                    .filter("client__c", "neq", cliente_id)\
                    .execute()

                if resposta_duplicada.data:
                    st.error("Já existe um cliente com essas informações cadastradas.")
                else:
                    supabase.table("clientes").update(cliente_atualizado).eq("client__c", cliente_id).execute()
                    st.success("Cliente atualizado com sucesso.")
                    st.rerun()


            # Excluir cliente
            if st.button("Excluir Cliente"):
                venda = next((v for v in vendas if v["cliente"] == cliente_nome), None)
                if venda:
                    st.error("Esse cliente tem venda associada, por favor desative o cliente no gerenciador de clientes.")
                    st.error("Esse cliente não poderá ser excluído.")
                else:
                    resposta = supabase.table("clientes").delete().eq("client__c", cliente_id).execute()
                    try:
                        if resposta.data:
                            st.success(f"Cliente '{cliente_nome}' excluído com sucesso.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir o cliente: {e}")
    else:
        st.warning("Nenhum cliente cadastrado.")
