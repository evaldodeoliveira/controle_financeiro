import streamlit as st
from controllers.auth_manager import is_authenticated, show_login
import locale
import warnings

st.set_page_config(
    page_title="Receitas",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

warnings.simplefilter("ignore", category=FutureWarning)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def main():
    if not is_authenticated():
        show_login()
        return  # Impede que o restante da página seja carregado
    st.sidebar.button("Sair", on_click=lambda: st.session_state.pop('auth_token', None),use_container_width=True, type="primary")
    st.title("Receitas")
    st.write("Bem-vindo! Aqui você pode gerenciar seus investimentos.")

if __name__ == "__main__":
    main()

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")