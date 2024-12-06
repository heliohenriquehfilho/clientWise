import streamlit as st
from datetime import datetime
import plotly.express as px
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from obter_dados_tabela import obter_dados_tabela
from config_supabase import config_supabase

supabase = config_supabase()

def processar_vendas(vendas):
    """Normaliza as vendas legadas e novas em um único formato."""
    vendas_processadas = []

    for venda in vendas:
        if "produtos" in venda and isinstance(venda["produtos"], list):
            # Venda nova com múltiplos produtos
            for item in venda["produtos"]:
                vendas_processadas.append({
                    "cliente": venda.get("cliente"),
                    "produto": item["nome"],
                    "quantidade": item["quantidade"],
                    "desconto": item.get("desconto", 0),
                    "data_venda": venda["data_venda"],
                    "pagamento": venda.get("pagamento"),
                    "valor_unitario": item["preco"],
                    "valor_total": item["preco"] * item["quantidade"] * (1 - item.get("desconto", 0) / 100),
                })
        else:
            # Venda legada (único produto)
            vendas_processadas.append({
                "cliente": venda.get("cliente"),
                "produto": venda.get("produto"),
                "quantidade": venda.get("quantidade", 1),
                "desconto": venda.get("desconto", 0),
                "data_venda": venda["data_venda"],
                "pagamento": venda.get("pagamento"),
                "valor_unitario": None,  # Preço não especificado diretamente
                "valor_total": venda["valor"],
            })

    return vendas_processadas

def identificar_carro_chefe(vendas):
    """Identifica o produto mais vendido (carro chefe)."""
    total_por_produto = {}
    
    for venda in vendas:
        # Verifica se a chave 'produtos' existe e é uma lista
        produtos = venda.get("produtos", None)
        if produtos is None or not isinstance(produtos, list):  # Se for None ou não for lista, pula
            continue
        
        for produto in produtos:
            if produto is None:
                continue  # Ignorar produtos None, sem alterar o dicionário
            nome_produto = produto.get("nome", "")
            quantidade = produto.get("quantidade", 1)  # Definir quantidade padrão para 1 se não houver
            total_por_produto[nome_produto] = total_por_produto.get(nome_produto, 0) + quantidade

    # Verifica se o dicionário está vazio, retornando uma mensagem adequada caso não haja produtos
    if not total_por_produto:
        return None, 0

    # Encontrar o carro chefe
    carro_chefe = max(total_por_produto, key=total_por_produto.get)
    return carro_chefe, total_por_produto[carro_chefe]

def calcular_lucro_e_custos(vendas, produtos):
    """Calcula lucro, custo e receita total mensal."""
    lucro = custo = total_mensal = 0
    mes_atual = datetime.today().month

    for venda in vendas:
        # Verifique se a venda pertence ao mês atual
        if venda["data_venda"].month == mes_atual:
            if "produtos" in venda and isinstance(venda["produtos"], list):
                # Caso de múltiplos produtos
                for item in venda["produtos"]:
                    produto = next((p for p in produtos if p["nome"] == item["nome"]), None)
                    if produto:
                        quantidade_vendida = item.get("quantidade", 1)
                        desconto = item.get("desconto", 0) / 100  # Convertendo de % para decimal
                        
                        # Calcular receita e custo por produto
                        preco_com_desconto = item["preco"] * (1 - desconto)
                        receita_venda = preco_com_desconto * quantidade_vendida
                        custo_venda = produto["custo"] * quantidade_vendida
                        lucro_venda = (preco_com_desconto - produto["custo"]) * quantidade_vendida
                        
                        # Acumular os totais
                        total_mensal += receita_venda
                        lucro += lucro_venda
                        custo += custo_venda
            elif "produto" in venda:
                # Caso legado (um único produto)
                produto = next((p for p in produtos if p["nome"] == venda["produto"]), None)
                if produto:
                    quantidade_vendida = venda.get("quantidade", 1)
                    desconto = venda.get("desconto", 0) / 100  # Convertendo de % para decimal
                    
                    # Calcular receita e custo
                    preco_com_desconto = produto["preco"] * (1 - desconto)
                    receita_venda = preco_com_desconto * quantidade_vendida
                    custo_venda = produto["custo"] * quantidade_vendida
                    lucro_venda = (preco_com_desconto - produto["custo"]) * quantidade_vendida
                    
                    # Acumular os totais
                    total_mensal += receita_venda
                    lucro += lucro_venda
                    custo += custo_venda

    return lucro, custo, total_mensal

def renderizar_insight_de_vendas(user_id):
    st.header("📊 Vendas")

    vendas = obter_dados_tabela("vendas", user_id)
    clientes = obter_dados_tabela("clientes", user_id)
    produtos = obter_dados_tabela("produtos", user_id)

    # Pre-processamento das datas
    for venda in vendas:
        if "data_venda" in venda:
            venda["data_venda"] = datetime.strptime(venda["data_venda"], "%Y-%m-%d").date()

    carro_chefe, quantidade_vendida = identificar_carro_chefe(vendas)

    total = sum(venda["valor"] for venda in vendas)

    lucro, custo, total_mensal = calcular_lucro_e_custos(vendas, produtos)

    vendas_normalizadas = processar_vendas(vendas)

    # Cálculo das porcentagens
    lucro_porcentagem = (lucro / total_mensal) * 100 if total_mensal else 0
    custo_porcentagem = (custo / total_mensal) * 100 if total_mensal else 0

    # Exibição dos insights
    st.markdown(f"Carro chefe: {carro_chefe} ({quantidade_vendida} vendas)")
    st.markdown(f"Lucro total este mês: R${lucro:.2f} | Lucro em porcentagem: {lucro_porcentagem:.2f}%")
    st.write(f"Custo total este mês: R${custo:.2f} | Custo em porcentagem: {custo_porcentagem:.2f}%")
    st.write(f"Receita total este mês: R${total_mensal:.2f}")

    # Gráficos de vendas
    col1, col2 = st.columns(2)

    with col1:
        vendas_por_data = px.bar(vendas_normalizadas, x="data_venda", y="valor_total", title="Vendas por Data")
        st.write(vendas_por_data)

    with col2:
        vendas_por_produto = px.bar(vendas_normalizadas, x="produto", y="quantidade", title="Vendas por Produto")
        st.write(vendas_por_produto)

    # Tabelas de dados
    st.markdown("Clientes: ")
    st.dataframe(clientes, use_container_width=True)

    st.markdown("Produtos: ")
    st.dataframe(produtos, use_container_width=True)

    st.markdown("Vendas: ")
    st.dataframe(vendas_normalizadas, use_container_width=True)