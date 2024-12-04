import streamlit as st
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

from obter_dados_tabela import obter_dados_tabela

def renderizar_gerenciamento_financeiro(user_id):
    st.title("Financeiro")

    # Menu de navegação
    menu = st.radio(
        "Navegação",
        [
            "Cadastrar Despesa", "Insights Financeiros"
        ],
        horizontal=True
    )

    # Mapeamento de funções de renderização
    mapa_funcoes = {
        "Cadastrar Despesa": despesas,
        "Insights Financeiros": insights_financeiros
    }

    if menu in mapa_funcoes:
        mapa_funcoes[menu](user_id)

def despesas(user_id):
    st.title("Aba de Despesas")
    
    contas = {}

    opcoes_despesas = {
        "Àgua": "Fornecedor de Àgua",
        "Luz": "Fornecedor de Luz",
        "Internet": "Fornecedor de Internet",
        "Fornecedor": None,
        "Boleto": None,
    }

    opcao = st.selectbox("Selecione a despesa", list(opcoes_despesas.keys()))
    fornecedor = opcoes_despesas.get(opcao)
    descricao = ""

    valor = st.number_input("Valor da conta")
    data = st.date_input("Data do pagamento").strftime("%Y-%m-%d")
    pagamento = st.selectbox("Forma de pagamento", ["Débito", "Débito Automático", "Dinheiro", "Pix", "Boleto"])

    if opcao in ["Fornecedor", "Boleto"]:
        fornecedor = st.text_input("Qual o fornecedor: ")
        descricao = st.text_input("Descrição: ")

    contas.update({
        "tipo": opcao,
        "descricao": descricao,
        "fornecedor": fornecedor,
        "valor": valor,
        "data_despesa": data,
        "pagamento": pagamento,
        "user_id": user_id
    })

    if st.button("Cadastrar despesa"):
        try:
            supabase.table("despesas").insert(contas).execute()
            st.success("Conta cadastrada!")
        except Exception as e:
            st.error(f"Erro ao salvar a conta: {e}")

def insights_financeiros(user_id):
    vendas = obter_dados_tabela("vendas", user_id)
    despesas = obter_dados_tabela("despesas", user_id)
    investimentos = obter_dados_tabela("investimento", user_id)
    campanhas = obter_dados_tabela("campanha", user_id)

    if not vendas:
        st.warning("Não há vendas registradas.")
    if not despesas:
        st.warning("Não há despesas registradas.")
    if not investimentos:
        st.warning("Não há investimentos registrados.")

    mes_atual = datetime.today().month

    menu_meses = st.selectbox(
        "Navegação Meses",
        [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
        ]
    )

    mapas_meses = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    ano = st.number_input("Qual Ano:", min_value=2000, max_value=datetime.today().year + 10, value=datetime.today().year)

    mes_referente = mapas_meses.get(menu_meses, mes_atual)

    # Filtrar pagamentos do mês nos investimentos
    investimentos_mes_atual = 0
    pagamentos_investimentos = []
    for investimento in investimentos:
        historico = investimento.get("historico_pagamentos", [])
        if isinstance(historico, str):
            try:
                historico = json.loads(historico)
            except json.JSONDecodeError:
                historico = []
        
        for pagamento in historico:
            data_pagamento = datetime.strptime(pagamento["data"], "%Y-%m-%d").date()
            if data_pagamento.month == mes_referente and data_pagamento.year == ano:
                investimentos_mes_atual += pagamento["valor"]
                pagamentos_investimentos.append({
                    "Nome": investimento["nome"],
                    "Data": pagamento["data"],
                    "Valor": pagamento["valor"]
                })

    # Calcular totais de vendas e despesas
    campanhas_mes_atual = sum(
        campanha["valor"]
        for campanha in campanhas
        if "data_inicio" in campanha and datetime.strptime(campanha["data_inicio"], "%Y-%m-%d").date().month == mes_referente
        and datetime.strptime(campanha["data_inicio"], "%Y-%m-%d").date().year == ano
    )

    # Calcular totais de vendas e despesas
    vendas_mes_atual = sum(
        venda["valor"]
        for venda in vendas
        if "data_venda" in venda and datetime.strptime(venda["data_venda"], "%Y-%m-%d").date().month == mes_referente
        and datetime.strptime(venda["data_venda"], "%Y-%m-%d").date().year == ano
    )

    despesas_mes_atual = sum(
        despesa["valor"]
        for despesa in despesas
        if "data_despesa" in despesa and datetime.strptime(despesa["data_despesa"], "%Y-%m-%d").date().month == mes_referente
        and datetime.strptime(despesa["data_despesa"], "%Y-%m-%d").date().year == ano
    )

    # Exibir os resultados
    st.markdown(f"Total de vendas no mês de {menu_meses}: R$ {vendas_mes_atual:.2f}")
    st.markdown(f"Total de despesas no mês de {menu_meses}: R$ {despesas_mes_atual:.2f}")
    st.markdown(f"Total de investimentos pagos no mês de {menu_meses}: R$ {investimentos_mes_atual:.2f}")
    st.markdown(f"Total de campanhas pagos no mês de {menu_meses}: R$ {campanhas_mes_atual:.2f}")

    balanco_mes_atual = vendas_mes_atual - (despesas_mes_atual + investimentos_mes_atual +  campanhas_mes_atual)
    st.markdown(f"Balanço do mês {menu_meses}: R$ {balanco_mes_atual:.2f}")

    if vendas:
        df_vendas = pd.DataFrame(vendas)
        df_vendas['data_venda'] = pd.to_datetime(df_vendas.get('data_venda', []), errors='coerce')

        filtro_entrada = df_vendas[
            (df_vendas['data_venda'].dt.year == ano) & (df_vendas['data_venda'].dt.month == mes_referente)
        ]
        st.markdown("Entradas: ")
        st.dataframe(filtro_entrada, use_container_width=True)

    if despesas:
        df_despesas = pd.DataFrame(despesas)
        df_despesas['data_despesa'] = pd.to_datetime(df_despesas.get('data_despesa', []), errors='coerce')

        filtro_saida = df_despesas[
            (df_despesas['data_despesa'].dt.year == ano) & (df_despesas['data_despesa'].dt.month == mes_referente)
        ]
        st.markdown("Saídas: ")
        st.dataframe(filtro_saida, use_container_width=True)

    # Exibir detalhes dos pagamentos de investimentos
    if pagamentos_investimentos:
        df_pagamentos = pd.DataFrame(pagamentos_investimentos)
        st.markdown("Pagamentos de Investimentos:")
        st.dataframe(df_pagamentos, use_container_width=True)

    if campanhas:
        df_campanhas = pd.DataFrame(campanhas)
        df_campanhas['data_inicio'] = pd.to_datetime(df_campanhas.get('data_inicio', []), errors='coerce')

        filtro_campanhas = df_campanhas[
            (df_campanhas['data_inicio'].dt.year == ano) & (df_campanhas['data_inicio'].dt.month == mes_referente)
        ]
        st.markdown("Campanhas: ")
        st.dataframe(filtro_campanhas, use_container_width=True)
