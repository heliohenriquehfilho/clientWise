import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
st.set_page_config(layout="wide")

# Inicializar o estado de autenticação (antes de qualquer outra coisa)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None

from gerenciamento_financeiro import renderizar_gerenciamento_financeiro
from gerenciador_de_investimento import renderizar_gerenciamento_de_investimento
from gerenciador_vendas import renderizar_gerenciador_de_vendas

# Configuração do Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas.")

try:
    supabase: Client = create_client(url, key)
    print("Conexão com Supabase bem-sucedida!")
except Exception as e:
    print(f"Erro ao criar cliente Supabase: {e}")
    raise

st.title("ClientWise")

# Função para registrar usuários
def registrar_usuario(email, senha):
    try:
        resposta = supabase.auth.sign_up({
            "email": email,
            "password": senha
        })
        if resposta.user:
            print("Usuário registrado com sucesso!")
            return resposta.user.id  # Retorna o user_id
        else:
            print(f"Erro ao registrar usuário: {resposta}")
            return None
    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")
        return None

# Função para autenticar usuários
def autenticar_usuario(email, senha):
    try:
        resposta = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })
        if resposta.user:
            st.session_state.user_id = resposta.user.id  # Salva o user_id na sessão
            return resposta.user.id  # Retorna o user_id
        else:
            return None
    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        return None

# Sistema de autenticação
if not st.session_state.autenticado:
    menu_login = st.sidebar.radio("Autenticação", ["Login", "Registrar"])

    if menu_login == "Registrar":
        st.subheader("Registrar")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Registrar"):
            if email and senha:
                user_id = registrar_usuario(email, senha)
                if user_id:
                    st.success("Usuário registrado com sucesso!")
                    st.success("Por Favor confirme o seu email com o link recebido pelo mesmo.")
                else:
                    st.error("Erro ao registrar usuário. Verifique as informações fornecidas.")
            else:
                st.error("Preencha todos os campos.")

    elif menu_login == "Login":
        st.subheader("Login")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Login"):
            user_id = autenticar_usuario(email, senha)
            if user_id:
                st.success("Login realizado com sucesso!")
                st.session_state.autenticado = True  # Atualiza o estado de autenticação
                st.session_state.user_id = user_id  # Armazena o user_id na sessão
            else:
                st.error("Email ou senha inválidos.")
else:
    # Exibir o menu principal após o login
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.session_state.user_id = None

    user_id = st.session_state.user_id  # Recupera o user_id da sessão

    menu = st.radio(
        "Navegação",
        ["Gerenciador de Vendas", "Gerenciador de Finanças", "Gerenciador de Investimento"],
        horizontal=True
    )
    mapa_funcoes = {
        "Gerenciador de Vendas": renderizar_gerenciador_de_vendas,
        "Gerenciador de Investimento": renderizar_gerenciamento_de_investimento,
        "Gerenciador de Finanças": renderizar_gerenciamento_financeiro
    }
    if menu in mapa_funcoes:
        mapa_funcoes[menu](user_id)
