import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from obter_dados_tabela import obter_dados_tabela

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def obter_vendas_totais(vendedor_nome, user_id):
    """Calcula o total de vendas e rentabilidade de um vendedor específico."""
    vendas = obter_dados_tabela("vendas", user_id)
    vendedor_vendas = [v for v in vendas if v["vendedor"] == vendedor_nome]
    rentabilidade = sum(float(v["valor"]) for v in vendedor_vendas)
    return rentabilidade, vendedor_vendas


def calcular_encargos(vendedor):
    """Calcula encargos como FGTS, férias, 13º salário e aviso prévio de um vendedor."""
    data_contratacao = vendedor["contratacao"]
    data_demissao = datetime.strptime(vendedor["demissao"], "%d-%m-%Y")
    tempo_trabalho = relativedelta(data_demissao, data_contratacao)
    meses_trabalhados = tempo_trabalho.years * 12 + tempo_trabalho.months

    salario = vendedor["Salario"]
    fgts = salario * 0.08
    aviso_previo = 30 + (3 * (meses_trabalhados // 12))
    aviso_previo_valor = (salario / 30) * aviso_previo
    multa_fgts = fgts * 0.4 * meses_trabalhados
    ferias_proporcionais = (salario / 12) * meses_trabalhados
    decimo_terceiro_proporcional = (salario / 12) * meses_trabalhados

    total_encargos = multa_fgts + ferias_proporcionais + decimo_terceiro_proporcional + aviso_previo_valor

    return aviso_previo_valor, multa_fgts, ferias_proporcionais, decimo_terceiro_proporcional, total_encargos, meses_trabalhados


def calcular_salario_total(vendedor):
    """Calcula o salário total considerando os aumentos ao longo do tempo."""
    hoje = datetime.today()
    salario_total = 0
    data_anterior = datetime.strptime(vendedor["contratacao"], "%Y-%m-%d")
    salario_atual = vendedor["salario"]

    if "Aumentos" in vendedor:
        for aumento in sorted(vendedor["aumentos"], key=lambda x: datetime.strptime(x["data"], "%d-%m-%Y")):
            data_aumento = datetime.strptime(aumento["data"], "%d-%m-%Y")
            if data_aumento > hoje:
                break

            meses_periodo = relativedelta(data_aumento, data_anterior).years * 12 + relativedelta(data_aumento, data_anterior).months
            salario_total += meses_periodo * salario_atual

            if "Porcentagem" in aumento:
                salario_atual += salario_atual * (aumento["porcentagem"] / 100)
            elif "Valor" in aumento:
                salario_atual += aumento["valor"]

            data_anterior = data_aumento

    meses_restantes = relativedelta(hoje, data_anterior).years * 12 + relativedelta(hoje, data_anterior).months
    salario_total += meses_restantes * salario_atual

    return salario_total


def renderizar_gerenciador_de_vendedores(user_id):
    st.header("Gerenciador de Vendedor")
    submenu = st.radio("Navegação", ["Registrar Vendedor", "Insight Vendedor", "Demitir Vendedor"], horizontal=True)

    vendedores = supabase.table("vendedores").select("*").eq("user_id", user_id).execute().data

    if submenu == "Registrar Vendedor":
        st.subheader("Registrar novo vendedor")
        
        vendedor = {}
        
        vendedor["nome"] = st.text_input("Nome do vendedor")
        vendedor["telefone"] = st.text_input("Número de telefone")
        vendedor["email"] = st.text_input("Email do vendedor")
        vendedor["idade"] = int(st.number_input("Idade do Vendedor"))
        vendedor["salario"] = st.number_input("Salário")
        vendedor["contratacao"] = st.date_input("Data de contratação").strftime("%Y-%m-%d")

        vendedor["user_id"] = user_id
        # Salvar no Supabase
        if st.button("Cadastrar Vendedor"):
            if vendedor:
                try:
                    resposta = supabase.table("vendedores").select("nome").filter("nome", "eq", vendedor["nome"]).filter("user_id", "eq", user_id).execute()
                    if resposta.data:
                        st.error("Já existe um vendedor com esse nome associado a este usuário.")
                    else:
                        vendedor["user_id"] = user_id
                        supabase.table("vendedores").insert(vendedor).execute()
                        st.success("Vendedor cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao cadastrar vendedor: {e}")
            else:
                st.error("Por favor, preencha todos os campos.")

    elif submenu == "Insight Vendedor" and vendedores:
        vendedor_selecionado = st.selectbox("Selecione o Vendedor", [v["nome"] for v in vendedores])
        vendedor = next(v for v in vendedores if v["nome"] == vendedor_selecionado)

        salario_total = calcular_salario_total(vendedor)

        if vendedor["aumentos"]:
            # Ordenar os aumentos por data (garante que o mais recente seja o último)
            aumentos_ordenados = sorted(vendedor["aumentos"], key=lambda x: x["Data"])
            
            # Pega o último aumento
            ultimo_aumento = aumentos_ordenados[-1]
            
            if "Valor" in ultimo_aumento:
                salario = vendedor["salario"] + ultimo_aumento["Valor"]
            elif "Porcentagem" in ultimo_aumento:
                salario = vendedor["salario"] * (1 + ultimo_aumento["Porcentagem"] / 100)
            else:
                salario = vendedor["salario"]  # Caso não tenha um aumento válido
        else:
            salario = vendedor["salario"]

        vendas_totais = obter_vendas_totais(vendedor_selecionado, user_id)
        ROI = ((vendas_totais[0] - salario_total)/salario_total)*100

        st.write(f"Data de Contratação: {vendedor['contratacao']}")
        st.write(f"Salário Base: R${salario}")
        st.markdown(f"Vendas totais: R${vendas_totais[0]}")
        st.markdown(f"Retorno de investimento total: {ROI:.2f}%")

        # Adicionar aumento
        st.subheader("Adicionar Aumento")
        data_aumento = st.date_input("Data do Aumento")
        tipo_aumento = st.radio("Tipo de Aumento", ["Porcentagem", "Valor"], horizontal=True)
        valor_aumento = st.number_input("Valor do Aumento")

        if st.button("Adicionar Aumento"):
            aumento = {
                "Data": data_aumento.strftime("%Y-%m-%d"),
                tipo_aumento: valor_aumento
            }

            # Garante que 'aumentos' seja sempre uma lista
            if not isinstance(vendedor.get("aumentos"), list):
                vendedor["aumentos"] = []

            vendedor["aumentos"].append(aumento)

            try:
                response = supabase.table("vendedores").update({"aumentos": vendedor["aumentos"]}).eq("id", vendedor["id"]).execute()
                if response:
                    st.success(f"Aumento adicionado com sucesso para {vendedor_selecionado}!")
                else:
                    st.error("Erro ao atualizar os aumentos no banco de dados.")
            except Exception as e:
                st.error(f"Erro ao adicionar aumento: {e}")



        # Calcular salário total
        st.write(f"Investimento total em salários: R${salario_total:.2f}")

    elif submenu == "Demitir Vendedor" and vendedores:
        vendedor_selecionado = st.selectbox("Selecione o Vendedor", [v["nome"] for v in vendedores])
        vendedor = next(v for v in vendedores if v["nome"] == vendedor_selecionado)

        data_demissao = st.date_input("Data de Demissão", datetime.today()).strftime("%Y-%m-%d")
        if st.button("Demitir Vendedor"):
            vendedor["demissao"] = data_demissao
            encargos = calcular_encargos(vendedor)

            # Exibe encargos
            aviso_previo_valor, multa_fgts, ferias_proporcionais, decimo_terceiro_proporcional, total_encargos, meses_trabalhados = encargos
            st.write(f"Valor do aviso prévio: R${aviso_previo_valor:.2f}")
            st.write(f"Multa do FGTS (40%): R${multa_fgts:.2f}")
            st.write(f"Férias Proporcionais: R${ferias_proporcionais:.2f}")
            st.write(f"13º Salário Proporcional: R${decimo_terceiro_proporcional:.2f}")
            st.write(f"Total de Encargos: R${total_encargos:.2f}")
            st.write(f"Tempo trabalhado: {meses_trabalhados} meses")

            # Atualiza o status no Supabase
            response = supabase.table("vendedores").update({"demissao": data_demissao, "encargos_demissao": total_encargos}).eq("id", vendedor["id"]).execute()

            if response.status_code == 200:
                st.success(f"Vendedor {vendedor['nome']} demitido com sucesso!")
            else:
                st.error("Erro ao demitir vendedor.")
    else:
        st.warning("Não há vendedores registrados para essa ação.")
