import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from obter_dados_tabela import obter_dados_tabela

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar cliente Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def calcular_valor_total(preco, desconto, quantidade):
    """Calcula o valor total do produto"""
    return round((preco - (preco * (desconto / 100))) * quantidade, 2)

def renderizar_cadastro_de_venda(user_id):
    st.header("📈 Cadastro de Vendas")

    # Obter dados das tabelas
    clientes = obter_dados_tabela("clientes", user_id)
    produtos = obter_dados_tabela("produtos", user_id)
    vendedores = obter_dados_tabela("vendedores", user_id)

    # Selecione Cliente
    if clientes:
        venda_cliente = st.selectbox("Selecione o cliente", [cliente["nome"] for cliente in clientes])
    else:
        st.error("Nenhum cliente cadastrado.")
        return

    # Selecione os Produtos (multiselect)
    if produtos:
        venda_produtos_nomes = [produto["nome"] for produto in produtos]
        produtos_selecionados = st.multiselect("Selecione os produtos", venda_produtos_nomes)
        produtos_lista = []
        
        for produto_nome in produtos_selecionados:
            produto_selecionado = next((p for p in produtos if p["nome"] == produto_nome), None)
            if produto_selecionado:
                estoque = produto_selecionado["quantidade"]
                ativo = produto_selecionado["ativo"]
                preco = produto_selecionado["preco"]
                tipo = produto_selecionado["tipo"]
                
                # Input de quantidade e desconto para cada produto
                quantidade = int(st.number_input(f"Quantidade de {produto_nome}", min_value=1, max_value=estoque, step=1))
                desconto = st.number_input(f"Desconto para {produto_nome} (%)", min_value=0.0, max_value=100.0, step=0.1)
                
                if tipo == "Fisico" and quantidade > estoque:
                    st.error(f"Estoque insuficiente para o produto {produto_nome}. Disponível: {estoque}.")
                
                if ativo is False:
                    st.error(f"Produto {produto_nome} está inativo.")
                
                produtos_lista.append({
                    "nome": produto_nome,
                    "quantidade": quantidade,
                    "desconto": desconto,
                    "preco": preco,
                })
    else:
        st.error("Nenhum produto cadastrado.")
        return

    # Selecione Vendedor
    if vendedores:
        venda_vendedor_nome = st.selectbox("Selecione o vendedor", [v["nome"] for v in vendedores])
        vendedor_selecionado = next((v for v in vendedores if v["nome"] == venda_vendedor_nome), None)
        if vendedor_selecionado:
            data_contratacao = datetime.strptime(vendedor_selecionado["contratacao"], "%Y-%m-%d").date()
            data_demissao = (
                datetime.strptime(vendedor_selecionado["demissao"], "%Y-%m-%d").date()
                if vendedor_selecionado["demissao"]
                else None
            )
    else:
        st.error("Nenhum vendedor cadastrado.")
        return

    # Outros detalhes da venda
    venda_data = st.date_input("Data da Compra").strftime("%Y-%m-%d")
    venda_pagamento = st.selectbox("Formato de pagamento", ["Crédito", "Débito", "Pix", "Dinheiro"])

    # Calcular valor total
    valor_total_venda = sum([calcular_valor_total(produto["preco"], produto["desconto"], produto["quantidade"]) for produto in produtos_lista])
    st.write(f"O valor total da venda é: R$ {valor_total_venda:.2f}")

    cliente = next(v for v in clientes if v["nome"] == venda_cliente)

    # Validar e salvar venda
    if st.button("Salvar venda"):
        if datetime.strptime(venda_data, "%Y-%m-%d").date() < data_contratacao:
            st.error("Vendedor não contratado na data da venda.")
        elif data_demissao and datetime.strptime(venda_data, "%Y-%m-%d").date() > data_demissao:
            st.error("Vendedor já demitido na data da venda.")
        elif cliente["ativo"] == False:
            st.error("Cliente Inativo.")
        else:
            venda = {
                "user_id": user_id,
                "produtos": produtos_lista,  # Armazenar os produtos como um JSONB
                "cliente": venda_cliente,
                "vendedor": venda_vendedor_nome,
                "data_venda": venda_data,
                "pagamento": venda_pagamento,
                "valor": valor_total_venda,
            }
            try:
                supabase.table("vendas").insert(venda).execute()
                
                # Atualizar o estoque dos produtos vendidos
                for produto in produtos_lista:
                    produto_nome = produto["nome"]
                    quantidade_vendida = produto["quantidade"]
                    produto_selecionado = next((p for p in produtos if p["nome"] == produto_nome), None)
                    if produto_selecionado and produto_selecionado["tipo"] == "Fisico":
                        estoque_atual = produto_selecionado["quantidade"]
                        novo_estoque = estoque_atual - quantidade_vendida
                        supabase.table("produtos").update({"quantidade": novo_estoque}).eq("produto__c", produto_selecionado["produto__c"]).execute()
            
                st.success("Venda cadastrada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar a venda: {e}")