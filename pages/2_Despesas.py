import streamlit as st
from controllers.type_controller import TypeController
from controllers.expense_controller import ExpenseController
from controllers.payment_controller import PaymentController
from models.expense import Expense

st.set_page_config(
    page_title="Despesas",
    page_icon=":material/price_check:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")

# def is_expense_complete(expense_obj):
#     required_fields = [
#         'exp_type_id', 
#         'exp_date', 
#         'exp_value', 
#         'exp_pay_id', 
#         'exp_number_of_installments', 
#         'exp_installment_value', 
#         'exp_description'
#     ]
    
#     for field in required_fields:
#         if getattr(expense_obj, field, None) is None:
#             return False
#     return True


@st.dialog("Cadastrar despesa", width="large")
def create(config):
    col1, col2, col3 = st.columns(3)

    # types = config['types_df']['type_name'].unique()
    # types = np.insert(types, 0, "Selecione um tipo")    
    # type_selected = col1.selectbox("Tipo:",types, placeholder='', index=0)
    # if type_selected == "Selecione um tipo":
    #     st.warning("Por favor, selecione um tipo válido.")
    #     return
    types = config['types_df']['type_name'].unique()
    type_selected = col1.selectbox("Tipo:",types)
    date = col2.date_input("Data:", format="DD/MM/YYYY")
    value = col3.number_input("Valor:", min_value=0.00)
 
    types_data = config['types_df'][config['types_df']['type_name'] == type_selected]
    if types_data.empty:
        st.error("Tipo não encontrado.")
        return
    
    col1, col2, col3 = st.columns(3)

    # payments = config['payments_df']['pay_name'].unique()
    # payments = np.insert(types, 0, "Selecione um pagamento") 
    # payment = col1.selectbox("Pagamento:", payments, placeholder='', index=0)
    # if payment == "Selecione um pagamento":
    #     st.warning("Por favor, selecione um pagamento válido.")
    #     return
    payments = config['payments_df']['pay_name'].unique()
    payment_selected = col1.selectbox("Pagamento:", payments)
    number_of_installments = col2.number_input("Quantidade de parcelas:", min_value=0)
    installments_value = col3.number_input("Valor da parcela:", min_value=0.00)

    payment_data = config['payments_df'][config['payments_df']['pay_name'] == payment_selected]
    if payment_data.empty:
        st.error("Pagamento não encontrado.")
        return

    description = st.text_input("Descrição")

    
    col1, col2, col3 = st.columns(3)
    if col2.button("Incluir", use_container_width=True):  
        # Usa o controller para adicionar o objeto ao banco de dados 
        

        # if is_expense_complete(objExpense):
        #     print("Objeto Expense preenchido corretamente!")
        # else:
        #     print("Faltam valores em alguns atributos do objeto Expense.")
      
        if description:
            objExpense = Expense(
                exp_type_id = int(types_data['type_id'].iloc[0]),
                exp_date = date,
                exp_value = float(value),
                exp_pay_id = int(payment_data['pay_id'].iloc[0]),
                exp_number_of_installments = int(number_of_installments),
                exp_installment_value = float(installments_value),
                exp_description = str(description)
            )
            result = config['controller'].add_expense(objExpense)
            if result:
                # types_updated = config['type'] + '_types_updated'
                # st.session_state[types_updated] = True
                # types_in_memorie = config['type'] + '_types_in_memorie'
                # st.session_state[types_in_memorie] = True                               
                st.rerun()                
        else:
            st.warning('Campo "Descrição" obrigatório!')

@st.dialog("Filtrar despesas")
def read(config):
    expenses = config['expenses_df_renamed']['Nome'].unique()
    expense = st.multiselect("Despesa", expenses, placeholder='')

    mask = (
        config['expenses_df_renamed']['Nome'].isin(expense)
    )

    df_filtred = config['expenses_df_renamed'][mask]
    col1, col2, col3 = st.columns(3)
    if col2.button("Filtrar", use_container_width=True):        
        if expense:
#vai conflitar com Category.py view
            st.session_state['expense_updated'] = True
            st.session_state['expense'] = df_filtred       
            st.rerun()
        else:
            st.warning('Escolha ao menos uma despesa!')

def view_expense():
    #testar se categorias cadastradas
    columns_types = ["type_id", "type_name", "cat_name"]
    controller_type = TypeController()
    types_df = controller_type.get_types()

    if types_df.empty:
        st.info('''
                 Nenhum tipo cadastrado.\n\n
                 Você será redirecionado a página de Tipos.
                 ''')
        if st.button("Ok", use_container_width=True, key='expense'):
            st.switch_page("pages/6_Tipos.py")
        return
    
    columns_payments = ["pay_id", "pay_name"]
    controller_pay = PaymentController()
    payments_df = controller_pay.get_payments()

    if payments_df.empty:
        st.info('''
                 Nenhum pagamento cadastrado.\n\n
                 Você será redirecionado a página de Pagamento.
                 ''')
        if st.button("Ok", use_container_width=True, key='expense'):
            st.switch_page("pages/Pagamentos.py")
        return

    #Columns: [exp_id, exp_date, exp_value, exp_description, exp_type_id,
    # exp_pay_id, exp_number_of_installments, exp_installment_value, 
    # type_id, type_type, type_name, type_description, type_category_id, 
    # pay_id, pay_name, pay_description]
    columns = ["exp_id", "exp_description"]
    controller = ExpenseController()

    expenses_df = controller.get_expenses()

    try:
        expenses_df_renamed = expenses_df[columns].rename(
            columns={"pay_description": "Descrição"}
        ).sort_index(ascending=False)
        st.subheader("Despesas")

        config = {
                'controller': controller,
                'expenses_df_renamed': expenses_df_renamed,
                'payments_df': payments_df,
                'types_df': types_df
                }
        col1, col2, col3, col4 = st.columns(4)
        if not expenses_df.empty:
            try:
                if col1.button("Incluir pagamento", use_container_width=True):
                    create(config)
                if col2.button("Filtrar pagamento", use_container_width=True):
                    read(config)
                if col3.button("Alterar pagamento", use_container_width=True):
                    #update(config)  
                    pass       
                if col4.button("Excluir pagamento", use_container_width=True):
                    #delete(config) 
                    pass
            except Exception as e:
                st.error(f"Erro ao acessar o dataframe: {e}")
        else:
            try:
                if col1.button("Incluir pagamento", use_container_width=True):
                    create(config)
                if col2.button("Filtrar pagamento", use_container_width=True, disabled=True):
                    read(config)
                if col3.button("Alterar pagamento", use_container_width=True, disabled=True):
                    #update(config)
                    pass         
                if col4.button("Excluir pagamento", use_container_width=True, disabled=True):
                    #delete(config)
                    pass 
            except Exception as e:
                st.error(f"Erro ao acessar o dataframe: {e}")   
        
        #F5 and read()
        if 'expense' not in st.session_state:
            st.session_state['expense'] = expenses_df_renamed

        if 'expense_updated' not in st.session_state:
            st.session_state['expense_updated'] = False 

        if st.session_state['expense_updated']:        
            st.success("Operação realizada com sucesso!")
            st.session_state['expense_updated'] = False        
            if 'expense_in_memorie' not in st.session_state:
                st.session_state['expense_in_memorie'] = False
            if st.session_state['expense_in_memorie']:
                st.session_state['expense'] = expenses_df_renamed
                st.session_state['expense_in_memorie'] = False
        if st.session_state["expense"].empty:
            st.write("Nenhum dado disponível.")
        else:
            st.dataframe(st.session_state['expense'], hide_index=True, use_container_width=True, column_config={"exp_id": None})
          
        if st.button("Recarregar", use_container_width=True):
            st.session_state['expense'] = expenses_df_renamed        
            st.rerun() 
    except Exception as e:
        print("Error",e)

view_expense()