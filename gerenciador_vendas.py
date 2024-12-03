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

def menu_button(label, icon, key):
    return st.button(
        f"{icon} {label}", key=key, help=f"Navegar para {label}",
        use_container_width=True  # Faz os botões ocuparem toda a largura disponível
    )

def renderizar_gerenciador_de_vendas(user_id):
    print(user_id)

    if "menu_vendas_header" not in st.session_state:
        st.session_state.menu_vendas_header = "Inicio"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if menu_button("Cliente", "👥", "cliente"):
            st.session_state.menu_vendas_header = "Gerenciador de Clientes"

    with col2:
        if menu_button("Produto", "📦", "produto"):
            st.session_state.menu_vendas_header = "Gerenciador de  Produtos"

    with col3:
        if menu_button("Vendas", "💸", "vendas"):
            st.session_state.menu_vendas_header = "Gerenciador de Vendas"

    with col4:
        if menu_button("Vendedores", "👨‍💼", "vendedores"):
            st.session_state.menu_vendas_header = "Gerenciador de Vendedores"

    # Divisor para separar o menu do conteúdo
    st.divider()

    # Conteúdo da página selecionada
    if st.session_state.menu_vendas_header == "Gerenciador de Vendas":
        menu_vendas = st.radio(
            "Navegação",
            [
                "Cadastro de Venda", "Gerenciamento de Vendas", "Insights de Vendas",
            ],
            horizontal=True)

        mapa_funcoes_vendas = {
            "Cadastro de Venda": renderizar_cadastro_de_venda,
            "Gerenciamento de Vendas": renderizar_gerenciamento_de_vendas,
            "Insights de Vendas": renderizar_insight_de_vendas,
        }

        if menu_vendas in mapa_funcoes_vendas:
            mapa_funcoes_vendas[menu_vendas](user_id)

    elif st.session_state.menu_vendas_header == "Gerenciador de Clientes":
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

    elif st.session_state.menu_vendas_header == "Gerenciador de  Produtos":
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

    elif st.session_state.menu_vendas_header == "Gerenciador de Vendedores":
        renderizar_gerenciador_de_vendedores(user_id)
    else:
        st.markdown("Bem-vindo ao **ClientWise**! Selecione uma área para começar.")

    




