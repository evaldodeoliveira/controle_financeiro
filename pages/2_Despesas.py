import streamlit as st
from controllers.auth_middleware import is_authenticated
from controllers.category_controller import CategoryController
from controllers.type_controller import TypeController
from controllers.expense_controller import ExpenseController
from controllers.payment_controller import PaymentController
from models.expense import Expense
import numpy as np
from datetime import timedelta, datetime
import pandas as pd

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


def expense_page():
    is_authenticated()  # Verifica se o usuário está autenticado
    

    def format_to_float(br_value):
        """
        Converte uma string com formato monetário brasileiro para float.
        Exemplo: 'R$ 1.234,56' -> 1234.56
        """
        if br_value.strip() == "":
            st.warning("O campo de valor não pode estar em branco.")
            return None
        try:
            # Remover "R$", pontos e substituir vírgula por ponto
            br_value = br_value.replace("R$", "").replace(".", "").replace(",", ".").strip()
            value = float(br_value)
            if value < 0:
                st.warning("O valor não pode ser negativo.")
                return None
            return value
        except ValueError:
            st.warning("Por favor, insira um valor válido.")
            return None

    def float_to_brazilian_currency(value):
        """
        Converte um float para uma string em formato monetário brasileiro.
        Exemplo: 1234.56 -> 'R$ 1.234,56'
        """
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # @st.cache_data
    # def get_expense():
    #     controller = ExpenseController()
    #     expense_df = controller.get_expenses()
    #     return expense_df

    @st.dialog("Cadastrar despesa", width="large")
    def create(config):
        def get_payment_selection():
            payments = sorted(config['payments_df']['pay_name'].unique())
            payment_selected = st.selectbox("Pagamento:", payments)
            payment_data = config['payments_df'][config['payments_df']['pay_name'] == payment_selected]
            if payment_data.empty:
                st.error("Pagamento não encontrado.")
                return None
            return int(payment_data['pay_id'].iloc[0])

        def get_type_selection():
            types = sorted(config['types_df']['type_name'].unique())
            type_selected = st.selectbox("Tipo:", types)
            types_data = config['types_df'][config['types_df']['type_name'] == type_selected]
            if types_data.empty:
                st.error("Tipo não encontrado.")
                return None
            return int(types_data['type_id'].iloc[0])

        def validate_value(value_input):
            value = format_to_float(value_input)
            if value is None:
                st.error("Valor inválido!")
            return value

        filter_choice = st.radio("Selecione o tipo de despesa", ["À vista", "Parcelada"])

        payment_id = get_payment_selection()
        if payment_id is None:
            return

        type_id = get_type_selection()
        if type_id is None:
            return

        col1, col2, col3 = st.columns(3)
        date = col1.date_input("Data:", format="DD/MM/YYYY")
        description = st.text_input("Descrição")

        if filter_choice == "À vista":
            value_input = col2.text_input("Valor:", value="R$ 0,00")
            value = validate_value(value_input)
            if value is None:
                return

            if st.button("Incluir", use_container_width=True):  
                if description:
                    objExpense = Expense(
                        exp_type_id=type_id,
                        exp_date=date.strftime("%Y-%m-%d"),
                        exp_value=float(value),
                        exp_pay_id=payment_id,
                        exp_description=str(description)
                    )
                    if config['controller'].add_expense(objExpense):
                        st.session_state.update({'expense_updated': True, 'expense_in_memorie': True})
                        st.cache_data.clear()  # Limpa todos os caches   
                        st.cache_resource()                                      
                        st.rerun()                
                else:
                    st.warning('Campo "Descrição" obrigatório!')

        else:  # Para despesa parcelada
            number_of_installments = col3.number_input("Quantidade de parcelas:", min_value=1)
            value_input = col2.text_input("Valor da parcela:", value="R$ 0,00")
            value = validate_value(value_input)
            if value is None:
                return

            if st.button("Incluir", use_container_width=True):  
                if description:
                    exp_final_date_of_installments = date + timedelta(days=30 * (number_of_installments - 1))
                    exp_value_total_installments = value * number_of_installments
                    objExpense = Expense(
                        exp_type_id=type_id,
                        exp_date=date.strftime("%Y-%m-%d"),
                        exp_value=float(value),
                        exp_pay_id=payment_id,
                        exp_number_of_installments=int(number_of_installments),
                        exp_description=str(description),
                        exp_final_date_of_installment=exp_final_date_of_installments,
                        exp_value_total_installments=exp_value_total_installments
                    )
                    if config['controller'].add_expense(objExpense):
                        st.session_state.update({'expense_updated': True, 'expense_in_memorie': True})
                        st.cache_data.clear()  # Limpa todos os caches   
                        st.cache_resource()                         
                        st.rerun()                
                else:
                    st.warning('Campo "Descrição" obrigatório!')

    @st.dialog("Filtrar despesas")
    def read(config):
        #implementar filtros por:
        #data, tipo de pagamento, tipo de despesa, range de valor...
        expenses = sorted(config['expenses_df_renamed']['Descrição'].unique())
        expense = st.multiselect("Despesa", expenses, placeholder='')

        mask = (
            config['expenses_df_renamed']['Descrição'].isin(expense)
        )

        df_filtred = config['expenses_df_renamed'][mask]
        col1, col2, col3 = st.columns(3)
        if col2.button("Filtrar", use_container_width=True):        
            if expense:
                st.session_state['expense_updated'] = True
                st.session_state['expense'] = df_filtred       
                st.rerun()
            else:
                st.warning('Escolha ao menos uma despesa!')

    @st.dialog("Alterar despesa", width="large")     
    def update(config):
        # Create a unique identifier combining description, date, and value
        config['expenses_df_renamed']['Identifier'] = config['expenses_df_renamed'].apply(
            lambda row: f"{row['Descrição']} - {pd.to_datetime(row['Data']).strftime('%d/%m/%Y')} - {row['Valor']}", axis=1
        )

        # Sort and add a placeholder option
        expenses = np.sort(config['expenses_df_renamed']['Identifier'].unique())
        expenses = np.insert(expenses, 0, "Selecione a despesa")

        # Display the select box with unique identifiers
        expense_selected = st.selectbox("Despesa", expenses, index=0)
        if expense_selected == "Selecione a despesa":
            st.warning("Por favor, selecione uma despesa válida.")
            return

        # Find the exact entry by matching the identifier
        expense_data = config['expenses_df_renamed'][config['expenses_df_renamed']['Identifier'] == expense_selected]
        if expense_data.empty:
            st.error("Despesa não encontrada.")
            return

        # Use the first matched row if there are still duplicates
        expense_data = expense_data.iloc[0]

        def get_payment_selection():
            payments = np.sort(config['payments_df']['pay_name'].unique())
            payments = np.insert(payments, 0, expense_data["Pagamento"])
            payment_selected = st.selectbox("Pagamento", payments, placeholder='', index=0)
            payment_data = config['payments_df'][config['payments_df']['pay_name'] == payment_selected]
            if payment_data.empty:
                st.error("Pagamento não encontrado.")
                return None
            return int(payment_data['pay_id'].iloc[0])

        def get_type_selection():
            types = np.sort(config['types_df']['type_name'].unique())
            types = np.insert(types, 0, expense_data["Tipo"])
            type_selected = st.selectbox("Tipo:", types, placeholder='', index=0)
            types_data = config['types_df'][config['types_df']['type_name'] == type_selected]
            if types_data.empty:
                st.error("Tipo não encontrado.")
                return None
            return int(types_data['type_id'].iloc[0])

        def validate_value(value_input):
            value = format_to_float(value_input)
            if value is None:
                st.error("Valor inválido!")
            return value

        payment_id = get_payment_selection()
        if payment_id is None:
            return

        type_id = get_type_selection()
        if type_id is None:
            return

        col1, col2, col3 = st.columns(3)

        obj_date = datetime.strptime(expense_data['Data'], "%Y-%m-%d").date()
        obj_date = col1.date_input("Data:", value=obj_date, format="DD/MM/YYYY")

        description = st.text_input("Descrição:", value=expense_data["Descrição"])

        if expense_data['Quantidade de parcelas'] > 0:
            number_of_installments = col3.number_input(label="Quantidade de parcelas:",value=expense_data['Quantidade de parcelas'], min_value=1)
            value_input = col2.text_input("Valor da parcela:", expense_data['Valor'])
            value = validate_value(value_input)
            if value is None:
                return

            if st.button("Alterar", use_container_width=True, type="primary"):  
                if description:
                    exp_final_date_of_installments = obj_date + timedelta(days=30 * (number_of_installments - 1))
                    exp_value_total_installments = value * number_of_installments
                    objExpense = Expense(
                        exp_id=expense_data['exp_id'],
                        exp_type_id=type_id,
                        exp_date=obj_date.strftime("%Y-%m-%d"),
                        exp_value=float(value),
                        exp_pay_id=payment_id,
                        exp_number_of_installments=int(number_of_installments),
                        exp_description=str(description),
                        exp_final_date_of_installment=exp_final_date_of_installments,
                        exp_value_total_installments=exp_value_total_installments
                    )
                    if config['controller'].update_expense(objExpense):
                        st.cache_data.clear()  # Limpa todos os caches   
                        st.cache_resource()  
                        st.session_state.update({'expense_updated': True, 'expense_in_memorie': True})                               
                        st.rerun()                
                else:
                    st.warning('Campo "Descrição" obrigatório!')
        else:
            value_input = col2.text_input("Valor:", expense_data['Valor'])
            value = validate_value(value_input)
            if value is None:
                return

            if st.button("Alterar", use_container_width=True, type="primary"):  
                if description:
                    objExpense = Expense(
                        exp_id=expense_data['exp_id'],
                        exp_type_id=type_id,
                        exp_date=obj_date.strftime("%Y-%m-%d"),
                        exp_value=float(value),
                        exp_pay_id=payment_id,
                        exp_description=str(description)
                    )
                    if config['controller'].update_expense(objExpense):
                        st.cache_data.clear()  # Limpa todos os caches   
                        st.cache_resource()  
                        st.session_state.update({'expense_updated': True, 'expense_in_memorie': True})                               
                        st.rerun()                
                else:
                    st.warning('Campo "Descrição" obrigatório!')
            
    @st.dialog("Excluir despesa", width="large")     
    def delete(config):
        # Create a unique identifier combining description, date, and value
        config['expenses_df_renamed']['Identifier'] = config['expenses_df_renamed'].apply(
            lambda row: f"{row['Descrição']} - {pd.to_datetime(row['Data']).strftime('%d/%m/%Y')} - {row['Valor']}", axis=1
        )

        # Sort and add a placeholder option
        expenses = np.sort(config['expenses_df_renamed']['Identifier'].unique())
        expenses = np.insert(expenses, 0, "Selecione a despesa")

        # Display the select box with unique identifiers
        expense_selected = st.selectbox("Despesa", expenses, index=0)
        if expense_selected == "Selecione a despesa":
            st.warning("Por favor, selecione uma despesa válida.")
            return

        # Find the exact entry by matching the identifier
        expense_data = config['expenses_df_renamed'][config['expenses_df_renamed']['Identifier'] == expense_selected]
        if expense_data.empty:
            st.error("Despesa não encontrada.")
            return

        # Use the first matched row if there are still duplicates
        expense_data = expense_data.iloc[0]
            
        st.text_input("Pagamento:", value=expense_data["Pagamento"], disabled=True)

        st.text_input("Tipo:", value=expense_data["Tipo"], disabled=True)

        col1, col2, col3 = st.columns(3)

        obj_date = datetime.strptime(expense_data['Data'], "%Y-%m-%d").date()
        obj_date = col1.date_input("Data:", value=obj_date, format="DD/MM/YYYY", disabled=True)

        st.text_input("Descrição:", value=expense_data["Descrição"], disabled=True)

        if expense_data['Quantidade de parcelas'] > 0:
            col3.number_input(label="Quantidade de parcelas:",value=expense_data['Quantidade de parcelas'], disabled=True)
            col2.text_input("Valor da parcela:", expense_data['Valor'], disabled=True)
            
        else:
            col2.text_input("Valor:", expense_data['Valor'], disabled=True)

        # Inicializar um estado para controle de confirmação, se ainda não existir
        if "confirm_delete_expense" not in st.session_state:
            st.session_state.confirm_delete_expense = False

        col1, col2, col3 = st.columns(3)
        # Botão para iniciar a exclusão
        if col2.button("Excluir", type="primary", use_container_width=True):
            st.session_state.confirm_delete_expense = True  # Ativar o estado de confirmação

        # Verificar se o estado de confirmação está ativo
        if st.session_state.confirm_delete_expense:
            st.warning(
                f"⚠️ Deseja realmente continuar?"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Sim, quero excluir", use_container_width=True):
                    st.session_state.confirm_delete_expense = False  # Resetar o estado de confirmação
                    result = config['controller'].delete_expense(expense_data['exp_id'])            
                    if result:
                        st.cache_data.clear()  # Limpa todos os caches   
                        st.cache_resource()                         
                        st.session_state['expense_updated'] = True
                        st.session_state['expense_in_memorie'] = True        
                        st.rerun()
            
            with col2:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.confirm_delete_expense = False
                    st.rerun() 

    def view_expense():
        controller_cat = CategoryController()
        categories_df = controller_cat.get_categories()
        #   Valida se existe categoria de despesa cadastrada
        if categories_df.empty or not (categories_df['cat_type'] == 'expense').any():
            st.info('''
                    Nenhuma ***categoria*** cadastrada.\n\n
                    Clique no botão abaixo para ser redirecionado a página de ***Categorias***.
                    ''')
            with st.form(key='expense_category_form', border=False):
                submit_button = st.form_submit_button(label="Ok", use_container_width=True)
                if submit_button:                        
                    st.switch_page("pages/5_Categorias.py")   
                return 
            
        controller_type = TypeController()
        types_df = controller_type.get_types()
        #filtrar apenas por Despesas
        types_df = types_df[types_df['type_type'] == 'expense']

        if types_df.empty:
            st.info('''
                    Nenhum ***tipo*** cadastrado.\n\n
                    Clique no botão abaixo para ser redirecionado a página ***Tipos***.
                    ''')
            with st.form(key='expense_type_form', border=False):
                submit_button = st.form_submit_button(label="Ok", use_container_width=True)
                if submit_button:                        
                    st.switch_page("pages/6_Tipos.py")
                return
        
        controller_pay = PaymentController()
        payments_df = controller_pay.get_payments()
        if payments_df.empty:
            st.info('''
                    Nenhum ***pagamento*** cadastrado.\n\n
                    Clique no botão abaixo para ser redirecionado a página ***Pagamentos***.
                    ''')
            with st.form(key='expense_payment_form', border=False):
                submit_button = st.form_submit_button(label="Ok", use_container_width=True)
                if submit_button:                        
                    st.switch_page("pages/7_Pagamentos.py")
                return   

        columns = ["exp_id","exp_date", "type_name", "exp_description", "pay_name", "exp_value", "exp_number_of_installments", 
                "exp_value_total_installment", "exp_final_date_of_installment"]
        
        controller = ExpenseController()
        expenses_df = controller.get_expenses()

        #expenses_df = get_expense()

        try:
            expenses_df_renamed = expenses_df[columns].rename(
                columns={
                    "exp_date":"Data",
                    "exp_value": "Valor",
                    "exp_description": "Descrição",
                    "type_name": "Tipo",
                    "pay_name": "Pagamento",
                    "exp_number_of_installments": "Quantidade de parcelas",
                    "exp_value_total_installment": "Valor total das parcelas",
                    "exp_final_date_of_installment": "Última parcela"
                    }
            ).sort_values(by="Data", ascending=False)
            st.subheader("Despesas")

            # Aplicando a formatação nas colunas 'Valor, 'Valor da parcela' e Parcelada
            expenses_df_renamed['Valor'] = expenses_df_renamed['Valor'].apply(float_to_brazilian_currency)
            expenses_df_renamed['Valor total das parcelas'] = expenses_df_renamed['Valor total das parcelas'].apply(float_to_brazilian_currency)

            config = {
                    'controller': controller,
                    'expenses_df_renamed': expenses_df_renamed,
                    'payments_df': payments_df,
                    'types_df': types_df
                    }
            col1, col2, col3, col4 = st.columns(4)
            if not expenses_df.empty:
                try:
                    if col1.button("Incluir despesa", use_container_width=True):
                        create(config)
                    if col2.button("Filtrar despesa", use_container_width=True):
                        read(config)
                    if col3.button("Alterar despesa", use_container_width=True):
                        update(config)       
                    if col4.button("Excluir despesa", use_container_width=True):
                        delete(config) 
                except Exception as e:
                    st.error(f"Erro ao acessar o dataframe: {e}")
            else:
                try:
                    if col1.button("Incluir despesa", use_container_width=True):
                        create(config)
                    if col2.button("Filtrar despesa", use_container_width=True, disabled=True):
                        read(config)
                    if col3.button("Alterar despesa", use_container_width=True, disabled=True):
                        update(config)         
                    if col4.button("Excluir despesa", use_container_width=True, disabled=True):
                        delete(config)
                except Exception as e:
                    st.error(f"Erro ao acessar o dataframe: {e}")   
            
            #F5 and read()
            if 'expense' not in st.session_state:
                st.session_state['expense'] = expenses_df_renamed

            if 'expense_updated' not in st.session_state:
                st.session_state['expense_updated'] = False

            #Atualiza a tela se Categoria foi excluída ou alterada
            if 'page_expense_category_updated' not in st.session_state:
                st.session_state['page_expense_category_updated'] = False
            if st.session_state['page_expense_category_updated']:
                st.session_state['expense'] = expenses_df_renamed
                st.session_state['page_expense_category_updated'] = False

            #Atualiza a tela se Tipo foi excluído ou alterado
            if 'page_expense_type_updated' not in st.session_state:
                st.session_state['page_expense_type_updated'] = False
            if st.session_state['page_expense_type_updated']:
                st.session_state['expense'] = expenses_df_renamed
                st.session_state['page_expense_type_updated'] = False
            
            #Atualiza tela se Pagamento foi excluído ou alterado
            if 'page_expense_payment_updated' not in st.session_state:
                st.session_state['page_expense_payment_updated'] = False
            if st.session_state['page_expense_payment_updated']:
                st.session_state['expense'] = expenses_df_renamed
                st.session_state['page_expense_payment_updated'] = False

            #Atualiza a tela se Despesa foi inserida, alterada ou excluida
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
                st.dataframe(
                    st.session_state['expense'], 
                    hide_index=True, 
                    use_container_width=True, 
                    column_config={
                        "exp_id": None,
                        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                        "Última parcela": st.column_config.DateColumn("Última parcela", format="MM/YYYY"),
                        "Valor": st.column_config.TextColumn("Valor"),
                        "Valor total": st.column_config.TextColumn("Valor total"),
                        "Quantidade de parcelas": st.column_config.TextColumn("Quantidade de parcelas")
                    }
                )
            
            if st.button("Recarregar", use_container_width=True):
                st.session_state['expense'] = expenses_df_renamed        
                st.rerun() 
        except Exception as e:
            print("Error",e)

    view_expense()

    if 'auth_token' not in st.session_state:
        st.rerun()  # Redireciona para a página principal


if __name__ == "__main__":
    expense_page()