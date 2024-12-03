import streamlit as st
from config_supabase import config_supabase
import pandas as pd

supabase = config_supabase()

def obter_aumento_vendas(user_id, produto, data_inicio, data_fim):

    vendas = supabase.table("vendas").select("*").eq("user_id", user_id).eq("produto", produto).execute().data

    quantidade_vendas = 0
    valor_total = 0
    quantidade_vendas_fora_periodo = 0

    for venda in vendas:
        if venda["data_venda"] >= data_inicio or venda["data_venda"] <= data_fim:
            quantidade_vendas += 1
            valor_total += venda["valor"]
        else:
            quantidade_vendas_fora_periodo += 1

    return quantidade_vendas, valor_total, quantidade_vendas_fora_periodo


def renderizar_gerenciador_de_campanhas(user_id):
    
    campanhas = supabase.table("campanha").select("*").eq("user_id", user_id).execute().data

    dict_traducao = {
        "plataforma": "Plataforma de Anuncios",
        "produto": "Produto",
        "data_inicio": "Inicio do Anuncio",
        "encerrada": "Encerrada",
        "custo_por_clic": "Custo Por Clique",
        "audiencia": "Audiencia",
        "aumento_vendas": "Aumento nas Vendas",
        "renda_total_gerada": "Renda Gerada"
    }
    
    cols_encerrada = ["plataforma", "produto", "data_inicio", "encerrada", "custo_por_clic", "audiencia", "aumento_vendas", "renda_total_gerada"]
    cols_ativas = ["plataforma", "produto", "data_inicio"]

    params_ativas = {'column_config': dict_traducao, 'column_order': cols_ativas, 'use_container_width': True}
    params_encerrada = {'column_config': dict_traducao, 'column_order': cols_encerrada, 'use_container_width': True}

    df = pd.DataFrame(campanhas)

    campanha_ativa = df[df["encerrada"] != True]
    campanha_encerrada = df[df["encerrada"] == True]

    st.markdown("Campanhas Ativas: ")
    st.dataframe(campanha_ativa, **params_ativas)

    id_campanha = [campanha["id_campanha"] for campanha in campanhas if campanha["encerrada"] != True]
    campanha_selecionada = st.selectbox("Selecione a Campanha: ", id_campanha)

    campanha_atual = next((campanha for campanha in campanhas if campanha["id_campanha"] == campanha_selecionada), None)

    if campanha_atual:
        st.markdown(f"**Produto:** {campanha_atual.get('produto')}")
        st.markdown(f"**Plataforma:** {campanha_atual.get('plataforma')}")
        st.markdown(f"**Data de Início:** {campanha_atual.get('data_inicio')}")

        # Encerrar campanha
        with st.popover("Encerrar a Campanha"):
            st.markdown("### Encerrar Campanha")
            custo_por_clic = st.number_input("Qual o custo por clique:", min_value=0.0, step=0.01)
            audiencia = st.number_input("Qual a audiência:", min_value=0, step=1)
            data_fim = st.date_input("Data de fim da campanha").strftime("%Y-%m-%d")

            if st.button("Confirmar Encerramento"):
                if custo_por_clic > 0 and audiencia > 0:

                    quantidade_vendas, valor_total, quantidade_vendas_fora_periodo = obter_aumento_vendas(
                        user_id, campanha_atual["produto"], campanha_atual["data_inicio"], data_fim
                    )

                    if quantidade_vendas_fora_periodo > 0:
                        aumento_vendas = quantidade_vendas / quantidade_vendas_fora_periodo
                    else:
                        aumento_vendas = quantidade_vendas  # Se não houver vendas fora do período, consideramos o total dentro

                    atualizacao = {
                        "custo_por_clic": custo_por_clic,
                        "audiencia": audiencia,
                        "encerrada": True,
                        "data_fim": data_fim,
                        "aumento_vendas": aumento_vendas,
                        "renda_total_gerada": valor_total
                    }
                    resposta = supabase.table("campanha").update(atualizacao).eq("id_campanha", campanha_selecionada).execute()
                    if resposta.data:
                        st.success("Campanha encerrada com sucesso.")
                        st.rerun()
                    else:
                        st.error("Houve um problema ao encerrar a campanha.")
                else:
                    st.error("Preencha todos os campos corretamente.")

    # Exibe campanhas encerradas
    st.markdown("### Campanhas Encerradas:")
    st.dataframe(campanha_encerrada, **params_encerrada)