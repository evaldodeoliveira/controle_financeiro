import streamlit as st
from controllers.auth_controller import AuthController

def is_authenticated():
    """Valida o token JWT e gerencia redirecionamento para login."""
    token = st.session_state.get('auth_token')
    if not token:
        st.warning("Você precisa fazer login para acessar esta página.")
        return False

    user_data = AuthController.verify_jwt(token)
    if not user_data:
        st.error("Sessão expirada. Faça login novamente.")
        st.session_state.pop('auth_token', None)
        return False

    return True

def show_login():
    """Exibe o formulário de login."""
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        token = AuthController.login(username, password)
        if token:
            st.session_state['auth_token'] = token
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")
