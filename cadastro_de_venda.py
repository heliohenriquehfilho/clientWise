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
    """Calcula o valor total da venda"""
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

    # Selecione Produto
    if produtos:
        venda_produto_nome = st.selectbox("Selecione o produto", [produto["nome"] for produto in produtos])
        produto_selecionado = next((p for p in produtos if p["nome"] == venda_produto_nome), None)
        if produto_selecionado:
            estoque = produto_selecionado["quantidade"]
            ativo = produto_selecionado["ativo"]
            preco = produto_selecionado["preco"]
            venda_quantidade = int(st.number_input("Quantidade de venda", min_value=1, step=1))
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
    venda_desconto = st.number_input("Desconto em %", min_value=0.0, max_value=100.0, step=0.1)
    venda_pagamento = st.selectbox("Formato de pagamento", ["Crédito", "Débito", "Pix", "Dinheiro"])

    # Calcular valor total
    valor_total_venda = calcular_valor_total(preco, venda_desconto, venda_quantidade)
    st.write(f"O valor total da venda é: R$ {valor_total_venda:.2f}")

    # Validar e salvar venda
    if st.button("Salvar venda"):
        if venda_quantidade > estoque:
            st.error(f"Estoque insuficiente. Disponível: {estoque}.")
        elif ativo is False:
            st.error("Produto inativo.")
        elif datetime.strptime(venda_data, "%Y-%m-%d").date() < data_contratacao:
            st.error("Vendedor não contratado na data da venda.")
        elif data_demissao and datetime.strptime(venda_data, "%Y-%m-%d").date() > data_demissao:
            st.error("Vendedor já demitido na data da venda.")
        else:
            venda = {
                "user_id": user_id,
                "produto": venda_produto_nome,
                "cliente": venda_cliente,
                "vendedor": venda_vendedor_nome,
                "data_venda": venda_data,
                "desconto": venda_desconto,
                "pagamento": venda_pagamento,
                "quantidade": venda_quantidade,
                "valor": valor_total_venda,
            }
            try:
                supabase.table("vendas").insert(venda).execute()
                novo_estoque = estoque - venda_quantidade
                supabase.table("produtos").update({"quantidade": novo_estoque}).eq("id", produto_selecionado["id"]).execute()
            
                st.success("Venda cadastrada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao salvar a venda: {e}")
