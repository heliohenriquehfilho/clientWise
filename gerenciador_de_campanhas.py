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

    if campanhas:
        df = pd.DataFrame(campanhas)

        # Exibir campanhas ativas
        st.markdown("### Campanhas Ativas:")
        campanha_ativa = df[df["encerrada"] != True]
        st.dataframe(campanha_ativa, **params_ativas)

        # Exibir campanhas encerradas
        st.markdown("### Campanhas Encerradas:")
        campanha_encerrada = df[df["encerrada"] == True]
        st.dataframe(campanha_encerrada, **params_encerrada)

        # Seleção de campanhas para exclusão
        st.markdown("### Excluir Campanhas:")
        campanhas_para_excluir = []

        # Seleção de campanhas para exclusão
        st.markdown("### Excluir Campanhas:")
        opcoes = [f"{campanha['id_campanha']} - {campanha['produto']} ({campanha['data_inicio']})" for campanha in campanhas]
        campanhas_selecionadas = st.multiselect(
            "Selecione as campanhas para excluir:",
            options=opcoes,
            help="Escolha as campanhas que deseja excluir."
        )

        # Botão para excluir campanhas selecionadas
        if st.button("Excluir Campanhas Selecionadas"):
            if campanhas_selecionadas:
                ids_para_excluir = [opcao.split(" - ")[0] for opcao in campanhas_selecionadas]
                resposta = supabase.table("campanha").delete().in_("id_campanha", ids_para_excluir).execute()
                if resposta.data:
                    st.success("Campanhas excluídas com sucesso.")
                    st.rerun()
                else:
                    st.error("Houve um problema ao excluir as campanhas.")
            else:
                st.warning("Nenhuma campanha selecionada para exclusão.")
    else:
        st.warning("Nenhuma Campanha de Marketing Registrada.")
