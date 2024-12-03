import streamlit as st

from cadastro_cliente import renderizar_cadastro_cliente
from cadastro_de_venda import renderizar_cadastro_de_venda
from insight_de_vendas import renderizar_insight_de_vendas
from cadastro_produto import renderizar_cadastro_de_produto
from gerenciador_de_clientes import renderizar_gerenciador_de_clientes
from gerenciador_de_produtos import renderizar_gerenciador_de_produtos
from gerenciador_de_vendedores import renderizar_gerenciador_de_vendedores
from gerenciador_de_vendas import renderizar_gerenciamento_de_vendas

if st.session_state.autenticado:
    user_id = st.session_state.get("user_id")
else:
    st.error("Por favor, faça login para cadastrar clientes.")

def renderizar_gerenciador_de_vendas(user_id):
    print(user_id)
    st.title("Gerenciador de vendas")

    menu_geral = st.radio(
        "Navegação",
        [
            "Cliente", "Produto", "Vendas", "Vendedores"
        ],
        horizontal=True
    )

    if menu_geral == "Cliente":
        # Menu de navegação
        menu_cliente = st.radio(
            "Navegação Cliente",
            [
                "Cadastro de Cliente", "Gerenciador de Clientes",
            ],
            horizontal=True
        )

        # Mapeamento de funções de renderização
        mapa_funcoes_cliente = {
            "Cadastro de Cliente": renderizar_cadastro_cliente,
            "Gerenciador de Clientes": renderizar_gerenciador_de_clientes,
        }

        if menu_cliente  in mapa_funcoes_cliente:
            mapa_funcoes_cliente[menu_cliente](user_id)

    if menu_geral == "Vendas":
        menu_vendas = st.radio(
            "Navegação",
            [
                "Cadastro de Venda", "Gerenciamento de Vendas", "Insights de Vendas",
            ],
            horizontal=True
        )

        mapa_funcoes_vendas = {
            "Cadastro de Venda": renderizar_cadastro_de_venda,
            "Gerenciamento de Vendas": renderizar_gerenciamento_de_vendas,
            "Insights de Vendas": renderizar_insight_de_vendas,
        }

        if menu_vendas in mapa_funcoes_vendas:
            mapa_funcoes_vendas[menu_vendas](user_id)

    if menu_geral == "Produto":
        menu_produtos = st.radio(
            "Navegação",
            [
                "Cadastro de Produto", "Gerenciador de Produtos",
            ],
            horizontal=True
        )

        mapa_funcoes_produtos = {
            "Cadastro de Produto": renderizar_cadastro_de_produto,
            "Gerenciador de Produtos": renderizar_gerenciador_de_produtos,
        }

        if menu_produtos in mapa_funcoes_produtos:
            mapa_funcoes_produtos[menu_produtos](user_id)
    
    if menu_geral == "Vendedores":
        renderizar_gerenciador_de_vendedores(user_id)