import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="ClientWise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Define o menu lateral como recolhido por padrão
)

load_dotenv()

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

st.title("ClientWise v0.0.5 🚀")

with st.expander("📢 Novidades da versão 0.0.5"):
    st.markdown("""
    ### 🆕 Novidades e Melhorias
    - **Gerenciamento de Marketing:** Nova opção para criar, gerenciar e encerrar campanhas de marketing.
    """)

st.divider()  # Adiciona uma linha divisória para separação visual

# Função para criar botões com ícones e nomes
def menu_button(label, icon, key):
    return st.button(
        f"{icon} {label}", key=key, help=f"Navegar para {label}",
        use_container_width=True  # Faz os botões ocuparem toda a largura disponível
    )

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
                st.session_state.autenticado = True  # Atualiza o estado de autenticação
                st.session_state.user_id = user_id  # Armazena o user_id na sessão
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Email ou senha inválidos.")
else:
    # Exibir o menu principal após o login
    if st.sidebar.button("Sair"):
        st.session_state.autenticado = False
        st.session_state.user_id = None
        st.rerun()

    user_id = st.session_state.user_id  # Recupera o user_id da sessão

    # Estado inicial do menu
    if "menu" not in st.session_state:
        st.session_state.menu = "Inicio"

    # Layout do menu principal
    st.title("ClientWise")
    st.markdown("### Escolha uma área para gerenciar:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if menu_button("Gerenciador de Vendas", "📈", "gerenciamento_vendas"):
            st.session_state.menu = "Gerenciador de Vendas"

    with col2:
        if menu_button("Gerenciador de Finanças", "💰", "financas"):
            st.session_state.menu = "Gerenciador de Finanças"

    with col3:
        if menu_button("Gerenciador de Investimentos", "📊", "investimentos"):
            st.session_state.menu = "Gerenciador de Investimentos"

    # Divisor para separar o menu do conteúdo
    st.divider()

    # Conteúdo da página selecionada
    if st.session_state.menu == "Gerenciador de Vendas":
        st.subheader("Gerenciador de Vendas")
        renderizar_gerenciador_de_vendas(user_id)
    elif st.session_state.menu == "Gerenciador de Finanças":
        st.subheader("Gerenciador de Finanças")
        renderizar_gerenciamento_financeiro(user_id)
    elif st.session_state.menu == "Gerenciador de Investimentos":
        st.subheader("Gerenciador de Investimentos")
        renderizar_gerenciamento_de_investimento(user_id)
    else:
        st.markdown("Bem-vindo ao **ClientWise**! Selecione uma área para começar.")
