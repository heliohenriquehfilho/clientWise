import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from obter_dados_tabela import obter_dados_tabela

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar cliente Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def renderizar_gerenciamento_de_vendas(user_id):
    # Função para carregar dados da tabela
    def carregar_vendas():
        return obter_dados_tabela("vendas", user_id)
    
    vendas = carregar_vendas()

    if vendas:
        st.dataframe(vendas, column_order=["id", "cliente", "produto", "quantidade", "desconto", "data_venda", "pagamento", "vendedor", "valor"])
        
        venda_id = st.selectbox("Selecione o ID da venda", [venda["id"] for venda in vendas])
        
        venda_selecionada = next((venda for venda in vendas if venda["id"] == venda_id), None)
        
        if venda_selecionada:
            st.markdown(f"**Cliente**: {venda_selecionada['cliente']}")
            st.markdown(f"**Produto**: {venda_selecionada['produto']}")
            st.markdown(f"**Quantidade**: {venda_selecionada['quantidade']}")
            st.markdown(f"**Desconto**: {venda_selecionada['desconto']}")
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

