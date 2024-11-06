import streamlit as st
import numpy as np
from controllers.payment_controller import PaymentController

st.set_page_config(
    page_title="Pagamentos",
    page_icon=":material/payments:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")

@st.dialog("Cadastrar pagamento")
def create(config):
    name = st.text_input("Nome:")
    description = st.text_area("Descrição:")

    col1, col2, col3 = st.columns(3)
    if col2.button("Incluir", use_container_width=True):            
        if name:
            result = config['controller'].add_payment(name, description)
            
            if result: 
                st.session_state['payment_updated'] = True
                st.session_state['payment_in_memorie'] = True                               
                st.rerun()                
        else:
            st.warning('Campo "Nome" obrigatório!')

@st.dialog("Filtrar pagamento")
def read(config):
    payments = config['payments_df_renamed']['Nome'].unique()
    payment = st.multiselect("Pagamento", payments, placeholder='')

    mask = (
        config['payments_df_renamed']['Nome'].isin(payment)
    )

    df_filtred = config['payments_df_renamed'][mask]
    col1, col2, col3 = st.columns(3)
    if col2.button("Filtrar", use_container_width=True):        
        if payment:
            st.session_state['payment_updated'] = True
            st.session_state['payment'] = df_filtred       
            st.rerun()
        else:
            st.warning('Escolha ao menos um pagamento!')

@st.dialog("Alterar pagamento")
def update(config):
    payments = config['payments_df_renamed']['Nome'].unique()
    payments = np.insert(payments, 0, "Selecione um pagamento")

    payment = st.selectbox("Pagamento", payments, placeholder='', index=0)
    
    if payment == "Selecione um pagamento":
        st.warning("Por favor, selecione um pagamento válida.")
        return
    
    payment_data = config['payments_df_renamed'][config['payments_df_renamed']['Nome'] == payment]
    
    if payment_data.empty:
        st.error("Pagamento não encontrado.")
        return

    payment_data = payment_data.iloc[0]
        
    name = st.text_input("Nome:", value=payment_data["Nome"])

    description = st.text_area("Descrição:", value=payment_data["Descrição"])

    col1, col2, col3 = st.columns(3)
    
    if col2.button("Alterar", use_container_width=True, type="primary"):         
        if not name:
            st.warning("O campo nome não pode estar vazio. Por favor, preencha.")
        else:            
            result = config['controller'].update_payment(payment_data['pay_id'], name, description)
            
            if result:
                st.session_state['payment_updated'] = True
                st.session_state['payment_in_memorie'] = True                
                st.rerun()

@st.dialog("Excluir pagamento")
def delete(config):
    payments = config['payments_df_renamed']['Nome'].unique()
    payments = np.insert(payments, 0, "Selecione um pagamento")

    payment = st.selectbox("Pagamento", payments, placeholder='', index=0)

    if payment == "Selecione um pagamento":
        st.warning("Por favor, selecione um pagamento válido.")
        return
    
    payment_data = config['payments_df_renamed'][config['payments_df_renamed']['Nome'] == payment]
    if payment_data.empty:
        st.error("Pagamento não encontrado.")
        return
    
    payment_data = payment_data.iloc[0]
    
    st.text_input("Nome:", value=payment_data["Nome"], disabled=True)
    st.text_area("Descrição:", value=payment_data["Descrição"], disabled=True) 
    
    if "confirm_delete_payment" not in st.session_state:
        st.session_state.confirm_delete_payment = False

    # Espaço vazio para exibir a mensagem de confirmação/cancelamento
    #message_placeholder = st.empty()

    col1, col2, col3 = st.columns(3)
    if col2.button("Excluir", type="primary", use_container_width=True):
        st.session_state.confirm_delete_payment = True

    if st.session_state.confirm_delete_payment:
        # Mensagem de confirmação com opção para confirmar ou cancelar
        st.warning(
            f"⚠️ Ao excluir o pagamento **{payment_data['Nome']}**, "
            "todos as despesas vinculadas a ele serão automaticamente excluídas!\n\n"
            "Deseja realmente continuar?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Sim, quero excluir", use_container_width=True):
                st.session_state.confirm_delete = False 
                result = config['controller'].delete_payment(payment_data['pay_id'])            
                if result:                     
                    st.session_state['payment_updated'] = True
                    st.session_state['payment_in_memorie'] = True    
#usar na tela de despesas???
                    st.session_state['payment_deleted'] = True       
                    st.rerun() 
        
        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.confirm_delete_payment = False
                st.rerun() 

def payment_view():    
    columns = ["pay_id", "pay_name", "pay_description"]
    controller = PaymentController()

    payments_df = controller.get_payments()
    
    try:
        payments_df_renamed = payments_df[columns].rename(
            columns={"pay_name": "Nome", "pay_description": "Descrição"}
        ).sort_index(ascending=False)
        st.subheader("Pagamentos")

        config = {
                'controller': controller,
                'payments_df_renamed': payments_df_renamed
                }
        col1, col2, col3, col4 = st.columns(4)
        if not payments_df_renamed.empty:
            try:
                if col1.button("Incluir pagamento", use_container_width=True):
                    create(config)
                if col2.button("Filtrar pagamento", use_container_width=True):
                    read(config)
                if col3.button("Alterar pagamento", use_container_width=True):
                    update(config)         
                if col4.button("Excluir pagamento", use_container_width=True):
                    delete(config) 
            except Exception as e:
                st.error(f"Erro ao acessar o dataframe: {e}")
        else:
            try:
                if col1.button("Incluir pagamento", use_container_width=True):
                    create(config)
                if col2.button("Filtrar pagamento", use_container_width=True, disabled=True):
                    read(config)
                if col3.button("Alterar pagamento", use_container_width=True, disabled=True):
                    update(config)         
                if col4.button("Excluir pagamento", use_container_width=True, disabled=True):
                    delete(config) 
            except Exception as e:
                st.error(f"Erro ao acessar o dataframe: {e}")   
        
        #F5 and read()
        if 'payment' not in st.session_state:
            st.session_state['payment'] = payments_df_renamed

        if 'payment_updated' not in st.session_state:
            st.session_state['payment_updated'] = False 

        if st.session_state['payment_updated']:        
            st.success("Operação realizada com sucesso!")
            st.session_state['payment_updated'] = False        
            if 'payment_in_memorie' not in st.session_state:
                st.session_state['payment_in_memorie'] = False
            if st.session_state['payment_in_memorie']:
                st.session_state['payment'] = payments_df_renamed
                st.session_state['payment_in_memorie'] = False
        if st.session_state["payment"].empty:
            st.write("Nenhum dado disponível.")
        else:
            st.dataframe(st.session_state['payment'], hide_index=True, use_container_width=True, column_config={"pay_id": None})
          
        if st.button("Recarregar", use_container_width=True):
            st.session_state['payment'] = payments_df_renamed        
            st.rerun() 
    except Exception as e:
        print("Error",e)

payment_view()