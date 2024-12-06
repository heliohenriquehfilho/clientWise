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

translations = {
    "Português": {
        "title": "Financeiro",
        "menu_register_expense": "Cadastrar Despesa",
        "menu_financial_insights": "Insights Financeiros",
        "register_expense": "Aba de Despesas",
        "select_expense": "Selecione a despesa",
        "water_supplier": "Fornecedor de Àgua",
        "electricity_supplier": "Fornecedor de Luz",
        "internet_supplier": "Fornecedor de Internet",
        "supplier": "Fornecedor",
        "bill": "Boleto",
        "salary_payment": "Pagamento de Funcionário",
        "expense_value": "Valor da conta",
        "payment_date": "Data do pagamento",
        "payment_method": "Forma de pagamento",
        "payment_method_options": ["Débito", "Débito Automático", "Dinheiro", "Pix", "Boleto"],
        "add_supplier": "Qual o fornecedor: ",
        "description": "Descrição: ",
        "register_expense_button": "Cadastrar despesa",
        "expense_registered": "Conta cadastrada!",
        "error_registering_expense": "Erro ao salvar a conta: {e}",
        "no_sales": "Não há vendas registradas.",
        "no_expenses": "Não há despesas registradas.",
        "no_investments": "Não há investimentos registrados.",
        "sales_total": "Total de vendas no mês de {month}: R$ {total:.2f}",
        "expenses_total": "Total de despesas no mês de {month}: R$ {total:.2f}",
        "investments_paid_total": "Total de investimentos pagos no mês de {month}: R$ {total:.2f}",
        "campaigns_paid_total": "Total de campanhas pagos no mês de {month}: R$ {total:.2f}",
        "monthly_balance": "Balanço do mês {month}: R$ {balance:.2f}",
        "enter_month": "Navegação Meses",
        "months": [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ],
        "year": "Qual Ano:",
        "sales": "Entradas: ",
        "expenses": "Saídas: ",
        "investment_payments": "Pagamentos de Investimentos:",
        "campaigns": "Campanhas: ",
    },
    "English": {
        "title": "Financial",
        "menu_register_expense": "Register Expense",
        "menu_financial_insights": "Financial Insights",
        "register_expense": "Expense Tab",
        "select_expense": "Select Expense",
        "water_supplier": "Water Supplier",
        "electricity_supplier": "Electricity Supplier",
        "internet_supplier": "Internet Supplier",
        "supplier": "Supplier",
        "bill": "Bill",
        "salary_payment": "Employee Payment",
        "expense_value": "Bill Value",
        "payment_date": "Payment Date",
        "payment_method": "Payment Method",
        "payment_method_options": ["Debit", "Automatic Debit", "Cash", "Pix", "Bill"],
        "add_supplier": "Which supplier: ",
        "description": "Description: ",
        "register_expense_button": "Register expense",
        "expense_registered": "Expense registered!",
        "error_registering_expense": "Error registering expense: {e}",
        "no_sales": "No sales recorded.",
        "no_expenses": "No expenses recorded.",
        "no_investments": "No investments recorded.",
        "sales_total": "Total sales in {month}: R$ {total:.2f}",
        "expenses_total": "Total expenses in {month}: R$ {total:.2f}",
        "investments_paid_total": "Total investments paid in {month}: R$ {total:.2f}",
        "campaigns_paid_total": "Total campaigns paid in {month}: R$ {total:.2f}",
        "monthly_balance": "Balance for {month}: R$ {balance:.2f}",
        "enter_month": "Month Navigation",
        "months": [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ],
        "year": "Which Year:",
        "sales": "Sales: ",
        "expenses": "Expenses: ",
        "investment_payments": "Investment Payments:",
        "campaigns": "Campaigns: ",
    }
}

# Função para obter o texto traduzido
def t(key):
    return translations[st.session_state.language].get(key, key)

def renderizar_gerenciamento_financeiro(user_id):
    st.title(t("title"))

    # Menu de navegação
    menu = st.radio(
        "Navegação",
        [
            t("menu_register_expense"), t("menu_financial_insights")
        ],
        horizontal=True
    )

    # Mapeamento de funções de renderização
    mapa_funcoes = {
        t("menu_register_expense"): despesas,
        t("menu_financial_insights"): insights_financeiros
    }

    if menu in mapa_funcoes:
        mapa_funcoes[menu](user_id)

def despesas(user_id):
    st.title(t("register_expense"))
    
    contas = {}

    opcoes_despesas = {
        t("water_supplier"): "Fornecedor de Àgua",
        t("electricity_supplier"): "Fornecedor de Luz",
        t("internet_supplier"): "Fornecedor de Internet",
        t("supplier"): None,
        t("bill"): None,
        t("salary_payment"): None,
    }

    opcao = st.selectbox(t("select_expense"), list(opcoes_despesas.keys()))
    fornecedor = opcoes_despesas.get(opcao)
    descricao = ""

    valor = st.number_input(t("expense_value"))
    data = st.date_input(t("payment_date")).strftime("%Y-%m-%d")
    pagamento = st.selectbox(t("payment_method"), t("payment_method_options"))

    if opcao in ["Fornecedor", "Boleto"]:
        fornecedor = st.text_input(t("add_supplier"))
        descricao = st.text_input(t("description"))

    contas.update({
        "tipo": opcao,
        "descricao": descricao,
        "fornecedor": fornecedor,
        "valor": valor,
        "data_despesa": data,
        "pagamento": pagamento,
        "user_id": user_id
    })

    if st.button(t("register_expense_button")):
        try:
            supabase.table("despesas").insert(contas).execute()
            st.success(t("expense_registered"))
        except Exception as e:
            st.error(t(f"error_registering_expense"))

def insights_financeiros(user_id):
    vendas = obter_dados_tabela("vendas", user_id)
    despesas = obter_dados_tabela("despesas", user_id)
    investimentos = obter_dados_tabela("investimento", user_id)
    campanhas = obter_dados_tabela("campanha", user_id)

    if not vendas:
        st.warning(t("no_sales"))
    if not despesas:
        st.warning(t("no_expenses"))
    if not investimentos:
        st.warning(t("no_investments"))

    mes_atual = datetime.today().month

    menu_meses = st.selectbox(
        t("enter_month"),t("months"), index=mes_atual-1
    )

    mapas_meses = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }

    ano = st.number_input(t("year"), min_value=2000, max_value=datetime.today().year + 10, value=datetime.today().year)

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
    st.markdown(t("sales_total").format(month=menu_meses, total=vendas_mes_atual))
    st.markdown(t("expenses_total").format(month=menu_meses, total=despesas_mes_atual))
    st.markdown(t("investments_paid_total").format(month=menu_meses, total=investimentos_mes_atual))
    st.markdown(t("campaigns_paid_total").format(month=menu_meses, total=campanhas_mes_atual))

    balanco_mes_atual = vendas_mes_atual - (despesas_mes_atual + investimentos_mes_atual +  campanhas_mes_atual)
    st.markdown(t("monthly_balance").format(month=menu_meses, balance=balanco_mes_atual))

    if vendas:
        df_vendas = pd.DataFrame(vendas)
        df_vendas['data_venda'] = pd.to_datetime(df_vendas.get('data_venda', []), errors='coerce')

        filtro_entrada = df_vendas[
            (df_vendas['data_venda'].dt.year == ano) & (df_vendas['data_venda'].dt.month == mes_referente)
        ]
        st.markdown(t("sales"))
        st.dataframe(filtro_entrada, use_container_width=True)

    if despesas:
        df_despesas = pd.DataFrame(despesas)
        df_despesas['data_despesa'] = pd.to_datetime(df_despesas.get('data_despesa', []), errors='coerce')

        filtro_saida = df_despesas[
            (df_despesas['data_despesa'].dt.year == ano) & (df_despesas['data_despesa'].dt.month == mes_referente)
        ]
        st.markdown(t("expenses"))
        st.dataframe(filtro_saida, use_container_width=True)

    # Exibir detalhes dos pagamentos de investimentos
    if pagamentos_investimentos:
        df_pagamentos = pd.DataFrame(pagamentos_investimentos)
        st.markdown(t("investment_payments"))
        st.dataframe(df_pagamentos, use_container_width=True)

    if campanhas:
        df_campanhas = pd.DataFrame(campanhas)
        df_campanhas['data_inicio'] = pd.to_datetime(df_campanhas.get('data_inicio', []), errors='coerce')

        filtro_campanhas = df_campanhas[
            (df_campanhas['data_inicio'].dt.year == ano) & (df_campanhas['data_inicio'].dt.month == mes_referente)
        ]
        st.markdown(t("campaigns"))
        st.dataframe(filtro_campanhas, use_container_width=True)
