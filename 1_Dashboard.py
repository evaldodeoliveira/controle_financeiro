import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

#revisar menu items

#load SQl
#if "data" not in st.session_state:
#    df_data = pd.read_csv("datasets/CLEAN_FIFA23_official_data.csv", index_col=0)
#    st.session_state["data"] = df_data

#dashs

#@st.cache_data
#def load_data():
#    df_data = pd.re
#    return df_data

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")