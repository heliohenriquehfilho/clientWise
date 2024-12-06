import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from obter_dados_tabela import obter_dados_tabela
import json
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar cliente Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Função para formatar o campo 'produtos' JSON
def formatar_produtos(produtos_json):
    """Transforma o campo 'produtos' em JSON para um formato legível"""
    if produtos_json is None:
        return ""  # Retorna uma string vazia caso o valor seja None
    
    produtos_formatados = []
    for produto in produtos_json:
        # Verifica se o produto possui as chaves necessárias antes de tentar acessá-las
        if 'nome' in produto and 'quantidade' in produto and 'desconto' in produto and 'preco' in produto:
            produtos_formatados.append(f"""{produto['nome']} - Quantidade: {produto['quantidade']} - Desconto: {produto['desconto']}% - Preço: R${produto['preco']}""")
    
    return ", ".join(produtos_formatados)

def renderizar_gerenciamento_de_vendas(user_id):
    # Função para carregar dados da tabela
    def carregar_vendas():
        return obter_dados_tabela("vendas", user_id)
    
    vendas = carregar_vendas()

    if vendas:
        # Carregar produtos e vendas do Supabase, filtrando pelo user_id
        produtos = supabase.table("produtos").select("*").eq("user_id", user_id).execute().data
        vendas = supabase.table("vendas").select("*").eq("user_id", user_id).execute().data

        # Aplicar a formatação no campo de 'produtos' para cada venda
        for venda in vendas:
            venda['produtos_formatados'] = formatar_produtos(venda['produtos'])

        # Converter para DataFrame e exibir
        vendas_df = pd.DataFrame(vendas)

        # Exibir o DataFrame com a coluna de produtos formatada
        st.dataframe(vendas_df[['id', 'cliente', "data_venda", 'produtos_formatados', 'valor', 'pagamento', 'vendedor']], use_container_width=True)
        
        venda_id = st.selectbox("Selecione o ID da venda", [venda["id"] for venda in vendas])
        
        venda_selecionada = next((venda for venda in vendas if venda["id"] == venda_id), None)
        
        if venda_selecionada:
            st.markdown(f"**Cliente**: {venda_selecionada['cliente']}")
            st.markdown(f"**Produto**: {venda_selecionada['produtos']}")
            st.markdown(f"**Data da Venda**: {venda_selecionada['data_venda']}")
            st.markdown(f"**Pagamento**: {venda_selecionada['pagamento']}")
            st.markdown(f"**Vendedor**: {venda_selecionada['vendedor']}")
            st.markdown(f"**Valor**: {venda_selecionada['valor']}")
        
            if st.button("Excluir Venda"):
                # Excluir venda pelo ID
                supabase.table("vendas").delete().eq("id", venda_id).execute()
                st.success(f"Venda '{venda_id}' excluída com sucesso.")
                
                # Recarregar dados após a exclusão
                vendas = carregar_vendas()
                st.rerun()  # Recarregar a interface para atualizar a lista
        else:
            st.warning("Venda selecionada não encontrada.")
    else:
        st.info("Nenhuma venda encontrada.")

