import streamlit as st
from dotenv import load_dotenv
from config_supabase import config_supabase

supabase = config_supabase()
load_dotenv()

def renderizar_gerenciador_de_produtos(user_id):
    st.header("💼 Gerenciador de Produtos")

    # Carregar produtos do Supabase, filtrando pelo user_id
    produtos = supabase.table("produtos").select("*").eq("user_id", user_id).execute().data
    vendas = supabase.table("vendas").select("*").eq("user_id", user_id).execute().data

    st.dataframe(produtos, column_order=[
        "nome", "preco", "descricao", "quantidade", 
        "ativo", "custo", "margem_lucro"
    ], use_container_width=True)

    produto_selecionado = {}

    if produtos:
        nome_produto = [produto["nome"] for produto in produtos]
        produto_selecionado_nome = st.selectbox("Escolha o produto", nome_produto)

        with st.expander("Campanha de Marketing"):

            campanhas = supabase.table("campanha").select("*").eq("user_id", user_id).execute().data
            campanha = {}

            plataforma = st.text_input("Plataforma de anuncio:")
            valor = st.number_input("Valor gasto para a campanha:")
            data_inicio = st.date_input("Data de inicio da campanha").strftime("%Y-%m-%d")
            produto = st.selectbox("Produto na campanha", nome_produto)
            if st.button("Lançar campanha de marketing"):
                if plataforma:
                    if data_inicio:
                        if produto:
                            id_campanha = plataforma + "." + data_inicio + "." + produto
                if plataforma:
                    campanha["plataforma"] = plataforma
                if valor:
                    campanha["valor"] = valor
                if data_inicio:
                    campanha["data_inicio"] = data_inicio
                if produto:
                    campanha["produto"] = produto
                if id_campanha:
                    campanha["id_campanha"] = id_campanha
                campanha["user_id"] = user_id
                
                try:
                    supabase.table("campanha").insert(campanha).execute()
                    st.success("Campanha cadastrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar a campanha: {e}")


        for produto in produtos:
            if produto["nome"] == produto_selecionado_nome:
                nome = produto.get("nome")
                preco = produto.get("preco")
                descricao = produto.get("descricao")
                quantidade = produto.get("quantidade")
                ativo = produto.get("ativo", True)
                c_barras = produto.get("codigo_barras")
                custo = float(produto.get("custo"))
                margem_lucro = produto.get("margem_lucro", 0)

        # Preencher campos com os dados existentes
        produto_nome = st.text_input("Nome do produto", value=nome)
        produto_preco = st.number_input("Preço do Produto", value=preco)
        produto_descricao = st.text_input("Descrição", value=descricao)
        produto_quantidade = st.number_input("Quantidade do produto", value=quantidade)
        produto_ativo = st.toggle("Produto Ativo", value=ativo)
        produto_codigo_barras = st.write("Código de barras:", c_barras)
        produto_custo = st.number_input("Custo do produto", value=custo, step=0.01)

        try:
            margem_lucro = (produto_preco - produto_custo) / produto_custo
        except:
            margem_lucro = 0
        
        st.write("Lucro: ", round(margem_lucro * 100, 2), "%")

        # Preencher dados no dicionário do produto selecionado
        if produto_nome:
            produto_selecionado["nome"] = produto_nome
        if produto_preco:
            produto_selecionado["preco"] = produto_preco
        if produto_descricao:
            produto_selecionado["descricao"] = produto_descricao
        if produto_quantidade:
            produto_selecionado["quantidade"] = produto_quantidade
        if produto_ativo is not None:
            produto_selecionado["ativo"] = produto_ativo
        if produto_codigo_barras:
            produto_selecionado["codigo_barras"] = c_barras
        if produto_custo:
            produto_selecionado["custo"] = produto_custo
        produto_selecionado["margem_lucro"] = margem_lucro

        # Atualizar produto no banco de dados
        if st.button("Salvar Produto"):
            if produto_selecionado:
                # Atualiza no Supabase
                resposta = supabase.table("produtos").update(produto_selecionado).eq("nome", produto_selecionado_nome).execute()
                if resposta.data:
                    st.success("Produto atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao atualizar produto: {resposta.error_message}")
            else:
                st.error("Erro no salvamento.")

        # Excluir produto
        if st.button("Excluir Produto"):
            try:
                venda = next(v for v in vendas if v["produto"] == produto_selecionado_nome)
            except:
                venda = ""
            if venda:
                st.error("Esse produto tem venda associado, por favor desative o produto no gerenciador de produto")
                st.error("Esse produto não poderá ser excluído.")
            else:
                resposta = supabase.table("produtos").delete().eq("nome", produto_selecionado_nome).execute()
                try:
                    if resposta.data:
                        st.success(f"Produto '{produto_selecionado_nome}' excluído com sucesso.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir o produto: {e}")
    else:
        st.warning("Nenhum produto cadastrado.")
