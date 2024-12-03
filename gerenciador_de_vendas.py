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
    vendas = obter_dados_tabela("vendas", user_id)
    st.dataframe(vendas, column_order=["id", "cliente", "produto", "quantidade", "desconto", "data_venda", "pagamento", "vendedor", "valor"])

    venda_id = st.selectbox("Selecione o id da venda", [venda["id"] for venda in vendas])

    st.markdown(f"Cliente: {vendas[venda_id-1]["cliente"]}")
    st.markdown(f"Produto: {vendas[venda_id-1]["produto"]}")
    st.markdown(f"Quantidade: {vendas[venda_id-1]["quantidade"]}")
    st.markdown(f"Desconto: {vendas[venda_id-1]["desconto"]}")
    st.markdown(f"Data da Venda: {vendas[venda_id-1]["data_venda"]}")
    st.markdown(f"Pagamento: {vendas[venda_id-1]["pagamento"]}")
    st.markdown(f"Vendedor: {vendas[venda_id-1]["vendedor"]}")
    st.markdown(f"Valor: {vendas[venda_id-1]["valor"]}")

    if st.button("Excluir Venda"):
        supabase.table("vendas").delete().eq("id", venda_id).execute()
        st.success(f"Venda '{venda_id}' excluído com sucesso.")