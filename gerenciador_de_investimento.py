import streamlit as st
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from obter_dados_tabela import obter_dados_tabela
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def carregar_investimentos(user_id):
    """Carrega os investimentos filtrados pelo user_id."""
    try:
        resposta = supabase.table("investimento").select("*").eq("user_id", user_id).execute()
        return resposta.data if resposta.data else []
    except Exception as e:
        st.error(f"Erro ao carregar investimentos: {e}")
        return []

def salvar_investimento(investimento):
    """Salva o investimento no Supabase."""
    try:
        supabase.table("investimento").insert(investimento).execute()
        st.success("Investimento cadastrado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar investimento: {e}")

def renderizar_gerenciamento_de_investimento(user_id):
    st.title("Gerenciamento de Investimentos")
    
    # Menu de navegação
    menu = st.radio(
        "Navegação",
        ["Cadastrar Investimento", "Pagar Investimento", "Gerenciar Investimento"],
        horizontal=True
    )
    
    # Mapeamento de funções de renderização
    mapa_funcoes = {
        "Cadastrar Investimento": lambda: cadastro_investimento(user_id),
        "Pagar Investimento": lambda: pagamento_investimento(user_id),
        "Gerenciar Investimento": lambda: gerenciar_investimento(user_id),
    }

    if menu in mapa_funcoes:
        mapa_funcoes[menu]()

def cadastro_investimento(user_id):
    """Cadastra um novo investimento vinculado ao user_id."""
    investimento = {"user_id": user_id}

    st.subheader("Cadastrar Investimento")
    investimento["nome"] = st.text_input("Qual o nome do produto/serviço:")
    investimento["descricao"] = st.text_area("Descrição:")
    investimento["valor"] = st.number_input("Valor do investimento", min_value=0.0, step=0.01)
    investimento["tipo_pagamento"] = st.selectbox("Tipo de pagamento", ["Unico", "Mensal", "Anual"])
    recorrencia = st.number_input("Recorrência (meses ou anos)", min_value=0, step=1, help="0 para recorrência indefinida")
    investimento["duracao"] = recorrencia
    investimento["valor_total"] = investimento["valor"] * max(recorrencia, 1)
    investimento["status"] = True
    investimento["pagamentos"] = 0
    investimento["encerrado"] = False
    investimento["historico_pagamentos"] = []  # Inicializa o histórico vazio

    if st.button("Salvar Investimento"):
        if all([investimento.get("nome"), investimento.get("descricao"), investimento.get("valor")]):
            salvar_investimento(investimento)
        else:
            st.error("Preencha todos os campos obrigatórios.")

def pagamento_investimento(user_id):
    """Gerencia os pagamentos de investimentos associados ao user_id."""
    st.subheader("Pagar Investimento")
    investimentos = carregar_investimentos(user_id)
    investimentos_pendentes = [i for i in investimentos if i["status"]]

    if not investimentos_pendentes:
        st.warning("Não há investimentos pendentes para pagamento.")
        return
    
    # Selectbox para escolher o investimento
    investimento_selecionado = st.selectbox(
        "Selecione o investimento",
        investimentos_pendentes,
        format_func=lambda x: x["nome"]
    )

    if investimento_selecionado:
        st.write("Detalhes do Investimento:")
        df = pd.DataFrame([investimento_selecionado])  # Coloca o dicionário em uma lista
        st.dataframe(df, column_order=["nome", "descricao", "tipo_pagamento", "duracao", "valor", "pagamentos", "encerrado"], use_container_width=True)

    # Campo para data e valor do pagamento
    data_pagamento = st.date_input("Data do pagamento", datetime.now().date())
    valor_pagamento = st.number_input("Valor do pagamento", min_value=0.01, step=0.01)

    if st.button("Registrar Pagamento"):
        # Garantir que o histórico esteja inicializado como lista
        historico = investimento_selecionado.get("historico_pagamentos", "[]")
        if isinstance(historico, str):
            try:
                historico = json.loads(historico)
            except json.JSONDecodeError:
                historico = []  # Caso o JSON seja inválido, inicializa como lista vazia

        if not isinstance(historico, list):
            historico = []  # Garante que o histórico seja uma lista

        # Adicionar o novo pagamento ao histórico
        historico.append({
            "data": str(data_pagamento),
            "valor": valor_pagamento
        })

        # Atualizar os pagamentos realizados
        investimento_selecionado["pagamentos"] += 1

        # Atualizar status caso tenha alcançado a duração
        if investimento_selecionado["pagamentos"] >= investimento_selecionado.get("duracao", 1):
            investimento_selecionado["status"] = False
            investimento_selecionado["encerrado"] = True

        try:
            # Atualizar o investimento no Supabase
            supabase.table("investimento").update({
                "historico_pagamentos": json.dumps(historico),
                "pagamentos": investimento_selecionado["pagamentos"],
                "status": investimento_selecionado["status"],
                "encerrado": investimento_selecionado["encerrado"]
            }).eq("id", investimento_selecionado["id"]).execute()

            st.success(f"Pagamento registrado com sucesso para: {investimento_selecionado['nome']}.")
        except Exception as e:
            st.error(f"Erro ao registrar pagamento: {e}")

def gerenciar_investimento(user_id):
    """Exibe e permite gerenciar os investimentos associados ao user_id."""
    st.subheader("Gerenciar Investimentos")
    investimentos = carregar_investimentos(user_id)

    if not investimentos:
        st.warning("Não há investimentos registrados.")
        return

    for investimento in investimentos:
        st.write(f"**{investimento['nome']}** - {'Ativo' if investimento['status'] else 'Encerrado'}")
        st.write(f"Descrição: {investimento['descricao']}")
        st.write(f"Valor: R${investimento['valor']:.2f}")
        st.write(f"Tipo de Pagamento: {investimento['tipo_pagamento']}")
        st.write(f"Pagamentos: {investimento['pagamentos']}/{investimento.get('duracao', 'Indefinido')}")

        # Exibir histórico de pagamentos
        historico = investimento.get("historico_pagamentos", [])
        if isinstance(historico, str):  # Caso o histórico seja uma string JSON
            try:
                historico = json.loads(historico)
            except json.JSONDecodeError:
                historico = []  # Se houver erro na conversão, inicializar como lista vazia
        
        if historico:
            st.write("Histórico de Pagamentos:")
            for pagamento in historico:
                st.write(f"- Data: {pagamento['data']}, Valor: R${pagamento['valor']:.2f}")
        else:
            st.write("Sem pagamentos registrados no histórico.")

        # Botões para encerrar ou renovar o investimento
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Encerrar {investimento['nome']}", key=f"encerrar_{investimento['id']}"):
                try:
                    # Atualizar status no Supabase
                    supabase.table("investimento").update({
                        "status": False,
                        "encerrado": True
                    }).eq("id", investimento["id"]).execute()
                    st.success(f"Investimento '{investimento['nome']}' encerrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao encerrar investimento: {e}")
        with col2:
            if st.button(f"Renovar {investimento['nome']}", key=f"renovar_{investimento['id']}"):
                nova_recorrencia = st.number_input(
                    f"Nova recorrência para {investimento['nome']}", 
                    min_value=1, 
                    step=1, 
                    key=f"nova_recorrencia_{investimento['id']}"
                )
                if st.button(f"Confirmar Renovação {investimento['nome']}", key=f"confirmar_renovar_{investimento['id']}"):
                    try:
                        # Atualizar status e recorrência no Supabase
                        supabase.table("investimento").update({
                            "status": True,
                            "encerrado": False,
                            "duracao": nova_recorrencia,
                            "pagamentos": 0  # Reiniciar contagem de pagamentos
                        }).eq("id", investimento["id"]).execute()
                        st.success(f"Investimento '{investimento['nome']}' renovado com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao renovar investimento: {e}")

        st.write("---")
