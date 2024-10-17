#abas/tipo
#cat Produdots (alimentação, bebida, limpeza, trasnporte, moradia, educação, saude, lazer)
#cat Servicos (comunicação, interterimento)
#cat receita (salario, bonus, aluguel, ...
#cat investimentos (fundos, tesouro direto, "acoes", cripto)
#pagamnento (credito, debito..)

import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="Categorias",
    page_icon=":material/category:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)
columns = ["cat_name", "cat_description"]
#load SQl
if "data" not in st.session_state:
    # 1. Conectar ao banco de dados SQLite
    conn = sqlite3.connect('/home/eoliveira/Documentos/GitHub/Particular/controle_financeiro/db/financial_control.db')
    # 2. Escrever a consulta SQL
    query = "SELECT * FROM category"
    # 3. Usar pandas para ler o resultado da consulta SQL
    df_data = pd.read_sql_query(query, conn)
    # 4. Fechar a conexão com o banco de dados
    conn.close()
    st.session_state["data"] = df_data


def menu(config):    
    col1, col2 = st.columns(2)
    if "action" not in st.session_state:
        if col1.button(f"Incluir categoria de {config['title']}", use_container_width=True):
            create(config)
        if col2.button(f"Filtrar categoria de {config['title']}", use_container_width=True):
            pass        
        #st.dataframe(df_filtred[columns],column_config={}, hide_index=True, use_container_width=True)
 #   else:  
 #       if col1.button("Incluir", use_container_width=True):
 #           create()
 #       if col2.button("Filtrar", use_container_width=True):
 #           pass
        #st.dataframe(st.session_state["action"][columns], hide_index=True, use_container_width=True)
    st.subheader(f"Categorias de {config['title']}s")
    
@st.dialog("Cadastrar categoria")
def create(config):
    name = st.text_input("Nome:")
    description = st.text_area("Descrição:")
    
    if st.button("Aplicar", use_container_width=True):
        df = pd.DataFrame({'Tipo': config['type'],
                           'Nome': [name],
                           'Descrição': [description]})
        df.to_csv('out.csv', mode='a', index=False, header=False)  
        st.rerun() 

products, services = st.tabs(["Produtos", "Serviços"])

with products:
    config = {'type': 'produto', 'title': 'produto'}
    menu(config)       
with services:
    config = {'type': 'service', 'title': 'serviço'}
    menu(config)


st.dataframe(st.session_state['data'][columns], hide_index=True, use_container_width=True)




st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")