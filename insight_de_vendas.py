import streamlit as st
from datetime import datetime
import plotly.express as px
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from obter_dados_tabela import obter_dados_tabela

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url,key)

def identificar_carro_chefe(vendas):
    """Identifica o produto mais vendido (carro chefe)."""
    total_por_produto = {}
    for venda in vendas:
        produto = venda["produto"]
        total_por_produto[produto] = total_por_produto.get(produto, 0) + 1

    carro_chefe = max(total_por_produto, key=total_por_produto.get)
    return carro_chefe, total_por_produto[carro_chefe]

def calcular_lucro_e_custos(vendas, produtos):
    """Calcula lucro, custo e receita total mensal."""
    lucro = custo = total_mensal = 0
    mes_atual = datetime.today().month

    for venda in vendas:
        if venda["data_venda"].month == mes_atual:
            produto = next((p for p in produtos if p["nome"] == venda["produto"]), None)
            if produto:
                # Considere a quantidade vendida
                quantidade_vendida = venda.get("quantidade", 1)

                # Calcule o custo e o lucro corretamente
                custo_venda = produto["custo"] * quantidade_vendida
                lucro_venda = (produto["preco"] - produto["custo"]) * quantidade_vendida

                # Receita da venda
                receita_venda = produto["preco"] * quantidade_vendida

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

    # Cálculo das porcentagens
    lucro_porcentagem = (lucro / total_mensal) * 100 if total_mensal else 0
    custo_porcentagem = (custo / total_mensal) * 100 if total_mensal else 0

    # Exibição dos insights
    st.markdown(f"Carro chefe: {carro_chefe} ({quantidade_vendida} vendas)", help="Quantidade de vendas, não quantidade de produto vendido.")
    st.markdown(f"Lucro total este mês: R${lucro:.2f} | Lucro total em porcentagem: {lucro_porcentagem:.2f}%")
    st.write(f"Custo total este mês: R${custo:.2f} | Custo total em porcentagem: {custo_porcentagem:.2f}%")
    st.write(f"Receita total este mês: R${total_mensal:.2f}")

    # Gráficos de vendas
    col1, col2 = st.columns(2)

    with col1:
        vendas_por_data = px.bar(vendas, x="data_venda", y="valor", title="Vendas por Data")
        st.write(vendas_por_data)

    with col2:
        vendas_por_produto = px.bar(vendas, x="produto", y="quantidade", title="Vendas por Produto")
        st.write(vendas_por_produto)

    # Tabelas de dados
    st.markdown("Clientes: ")
    st.dataframe(
        clientes,
        use_container_width=True,
        column_order=["ativo", "nome", "contato", "idade", "email", "endereco", 
                    "bairro", "cidade", "estado", "cep", "genero"],
        column_config={
            "ativo": "Status Ativo",
            "nome": "Nome Completo",
            "contato": "Número de Contato",
            "idade": "Idade",
            "email": "E-mail",
            "endereco": "Endereço",
            "bairro": "Bairro",
            "cidade": "Cidade",
            "estado": "Estado",
            "cep": "CEP",
            "genero": "Gênero"
        }
    )

    st.markdown("Produtos: ")
    st.dataframe(
        produtos, 
        use_container_width=True,
        column_order=["ativo", "nome", "preco", "descricao", 
                      "quantidade", "custo", "margem_lucro", "tipo"],
        column_config={
            "ativo": "Status Produto",
            "nome": "Produto",
            "preco": "Preço Unitário",
            "descricao": "Descrição",
            "quantidade": "Em Estoque",
            "custo": "Custo Unitário",
            "margem_lucro": "Lucro Unitário (%)",
            "tipo": "Tipo"
        }
    )

    st.markdown("Vendas: ")
    st.dataframe(
        vendas, 
        use_container_width=True,
        column_order=["cliente", "produto", "quantidade", "desconto", 
                      "data_venda", "pagamento", "vendedor", "valor"],
        column_config={
            "cliente": "Cliente",
            "produto": "Produto",
            "quantidade": "Quantidade Vendida",
            "desconto": "Desconto",
            "data_venda": "Data da Venda",
            "pagamento": "Forma de Pagamento",
            "vendedor": "Vendedor",
            "valor": "Valor Total"
        }
    )