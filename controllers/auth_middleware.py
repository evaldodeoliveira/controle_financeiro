import streamlit as st
from controllers.auth_controller import AuthController

def is_authenticated():
    token = st.session_state.get('auth_token')
    if not token:
        st.error("Você precisa fazer login para acessar esta página.")
        st.stop()

    user_data = AuthController.verify_jwt(token)
    if not user_data:
        st.error("Sessão expirada. Faça login novamente.")
        st.session_state.pop('auth_token', None)
        st.stop()
