import streamlit as st
from config_supabase import config_supabase

supabase = config_supabase()

def renderizar_gerenciador_de_campanhas(user_id):
    
    campanhas = supabase.table("campanha").select("*").eq("user_id", user_id).execute().data

    st.dataframe(campanhas)