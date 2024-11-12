import streamlit as st
import numpy as np
from controllers.type_controller import TypeController
from controllers.category_controller import CategoryController

st.set_page_config(
    page_title="Tipos",
    page_icon=":material/merge_type:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")


def menu(config):
        col1, col2, col3, col4 = st.columns(4)
    
        if not config['types_df_renamed'].empty:
            try:
                if col1.button(f"Incluir tipo de {config['title']}", use_container_width=True):
                    create(config)
                if col2.button(f"Filtrar tipo de {config['title']}", use_container_width=True):
                    read(config)
                if col3.button(f"Alterar tipo de {config['title']}", use_container_width=True):
                    update(config)         
                if col4.button(f"Excluir tipo de {config['title']}", use_container_width=True):
                    delete(config) 
            except Exception as e:
                st.error(f"Erro ao acessar o dataframe: {e}")
        else:
            try:
                if col1.button(f"Incluir tipo de {config['title']}", use_container_width=True):
                    create(config)
                if col2.button(f"Filtrar tipo de {config['title']}", use_container_width=True, disabled=True):
                    read(config)
                if col3.button(f"Alterar tipo de {config['title']}", use_container_width=True, disabled=True):
                    update(config)         
                if col4.button(f"Excluir tipo de {config['title']}", use_container_width=True, disabled=True):
                    delete(config) 
            except Exception as e:
                st.error(f"Erro ao acessar o dataframe: {e}") 

@st.dialog("Cadastrar tipo")
def create(config):
    name = st.text_input("Nome:")
    description = st.text_area("Descrição:")

     # Recupera as categorias
    categories = config['categories_df_renamed']['Nome'].unique()
    categories = np.insert(categories, 0, "Selecione uma categoria")  # Adiciona a opção inicial

    # Selectbox para seleção de categoria
    category = st.selectbox("Categoria", categories, placeholder='', index=0)
    
    # Verifica se o usuário selecionou "Selecione uma categoria"
    if category == "Selecione uma categoria":
        st.warning("Por favor, selecione uma categoria válida.")  # Exibe uma mensagem de aviso
        return  # Interrompe a execução até que uma categoria válida seja selecionada

    # Obtém os dados da categoria selecionada
    category_data = config['categories_df_renamed'][config['categories_df_renamed']['Nome'] == category]
    
    # Verifica se o filtro retornou algum dado
    if category_data.empty:
        st.error("Categoria não encontrada.")
        return

    col1, col2, col3 = st.columns(3)
    if col2.button("Incluir", use_container_width=True):            
        if name:
            cat_id = int(category_data['cat_id'].iloc[0])
            # Chama o método add_type e verifica se ocorreu erro
            result = config['controller'].add_type(config['type'], name, description, cat_id)
            if result:  # Se result for True, significa que o processo foi bem-sucedido
                st.session_state[config['type'] + '_type_updated'] = True
                st.session_state[config['type'] + '_type_in_memorie'] = True
                # types_updated = config['type'] + '_types_updated'
                # st.session_state[types_updated] = True
                # types_in_memorie = config['type'] + '_types_in_memorie'
                # st.session_state[types_in_memorie] = True                               
                st.rerun()                
        else:
            st.warning('Campo "Nome" obrigatório!')

@st.dialog("Filtrar tipo")
def read(config):      
    # Radio button para escolher o tipo de filtro
    filter_choice = st.radio("Selecione o tipo de filtro", ["Tipo", "Categoria"])

    # Variáveis de seleção
    type_selected = []
    category_selected = []

    # Aplicação do filtro com base na escolha do usuário
    df_filtred = config['types_df_renamed']

    # Filtro baseado na escolha do usuário
    if filter_choice == "Tipo":
        # Multiselect para filtrar por Tipo (Nome)
        type_selected = st.multiselect("Tipo", config['types_df_renamed']['Nome'].unique(), placeholder="Selecione o tipo")
        if type_selected:
            df_filtred = config['types_df_renamed'][config['types_df_renamed']['Nome'].isin(type_selected)]
    else:
        # Multiselect para filtrar por Categoria
        category_selected = st.multiselect("Categoria", config['types_df_renamed']['Categoria'].unique(), placeholder="Selecione a categoria")
        if category_selected:
            df_filtred = config['types_df_renamed'][config['types_df_renamed']['Categoria'].isin(category_selected)]

    #retornar o DF para tela principal e atualizar os sessions states
    col1, col2, col3 = st.columns(3)
    if col2.button("Filtrar", use_container_width=True):        
        if type_selected or category_selected:
            st.session_state[config['type'] + '_type_updated'] = True
            # types_update = config['type'] + '_types_updated'
            # st.session_state[types_update] = True
            st.session_state[config['type'] + '_type'] = df_filtred
            st.rerun()
        else:
            st.warning('Escolha ao menos um tipo e/ou categoria!')

@st.dialog("Alterar tipo")     
def update(config):
    # Recupera os tipos
    types = config['types_df_renamed']['Nome'].unique()
    type_selected = np.insert(types, 0, "Selecione o tipo")  # Adiciona a opção inicial

    # Selectbox para seleção de tipo
    type_selected = st.selectbox("Tipo", type_selected, placeholder='', index=0)
    
    # Verifica se o usuário selecionou "Selecione o tipo"
    if type_selected == "Selecione o tipo":
        st.warning("Por favor, selecione um tipo válido.")  # Exibe uma mensagem de aviso
        return  # Interrompe a execução até que um tipo válido seja selecionado
    
    # Obtém os dados do tipo selecionado
    type_data = config['types_df_renamed'][config['types_df_renamed']['Nome'] == type_selected]
    
    # Verifica se o filtro retornou algum dado
    if type_data.empty:
        st.error("Tipo não encontrado.")
        return

    type_data = type_data.iloc[0]  # Obtém o primeiro resultado válido
        
    name = st.text_input("Nome:", value=type_data["Nome"])
    description = st.text_area("Descrição:", value=type_data["Descrição"])
    #category = st.text_input("Categoria:", value=type_data["Categoria"]) 

     # Recupera as categorias
    categories = config['categories_df_renamed']['Nome'].unique()
    #categories = np.insert(categories, 0, "Selecione uma categoria")  # Adiciona a opção inicial
    categories = np.insert(categories, 0, type_data["Categoria"])  # Adiciona a opção inicial

    # Selectbox para seleção de categoria
    category = st.selectbox("Categoria", categories, placeholder='', index=0)

    # if category == "Selecione uma categoria":
    #     st.warning("Por favor, selecione uma categoria válida.")
    #     return 

    # Obtém os dados da categoria selecionada
    category_data = config['categories_df_renamed'][config['categories_df_renamed']['Nome'] == category]
    
    # # Verifica se o filtro retornou algum dado
    # if category_data.empty:
    #     st.error("Categoria não encontrada.")
    #     return

    category_data = category_data.iloc[0]
    # Colunas para os botões
    col1, col2, col3 = st.columns(3)
    
    if col2.button("Alterar", use_container_width=True, type="primary"):         
        # Verifica se o campo foi apagado ou está vazio        
        if not name:
            st.warning("O campo nome não pode estar vazio. Por favor, preencha.")
        else:            
            # Atualiza a categoria            
            result = config['controller'].update_type(type_data['type_id'], type_data['type_type'], name, description, category_data['cat_id'])
            
            if result:
                st.session_state[config['type'] + '_type_updated'] = True
                st.session_state[config['type'] + '_type_in_memorie'] = True
                #st.session_state['expense_type_updated'] = True #usado tela Despesas
                # types_updated = config['type'] + '_types_updated'
                # st.session_state[types_updated] = True
                # types_in_memorie = config['type'] + '_types_in_memorie'
                # st.session_state[types_in_memorie] = True        
                st.rerun()  # Recarrega a página para refletir as mudanças

@st.dialog("Excluir tipo")
def delete(config):   
    types = config['types_df_renamed']['Nome'].unique()
    types = np.insert(types, 0, "Selecione um tipo")  # Adiciona a opção inicial

    type = st.selectbox("Tipo", types, placeholder='', index=0)

    # Verifica se o usuário selecionou "Selecione um tipo"
    if type == "Selecione um tipo":
        st.warning("Por favor, selecione uma categoria válida.")  # Exibe uma mensagem de aviso
        return  # Interrompe a execução até que uma categoria válida seja selecionada
    
    type_data = config['types_df_renamed'][config['types_df_renamed']['Nome'] == type]
    # Verifica se o filtro retornou algum dado
    if type_data.empty:
        st.error("Tipo não encontrado.")
        return
    
    type_data = type_data.iloc[0]  # Obtém o primeiro resultado válido
    
    st.text_input("Nome:", value=type_data["Nome"], disabled=True)
    st.text_area("Descrição:", value=type_data["Descrição"], disabled=True) 
    st.text_input("Categoria:", value=type_data["Categoria"], disabled=True) 
    
    # Inicializar um estado para controle de confirmação, se ainda não existir
    if "confirm_delete_type" not in st.session_state:
        st.session_state.confirm_delete_type = False


    col1, col2, col3 = st.columns(3)
    # Botão para iniciar a exclusão
    if col2.button("Excluir", type="primary", use_container_width=True):
        st.session_state.confirm_delete_type = True  # Ativar o estado de confirmação

    # Verificar se o estado de confirmação está ativo
    if st.session_state.confirm_delete_type:
        # Mensagem de confirmação com opção para confirmar ou cancelar
        st.warning(
            f"⚠️ Ao excluir o tipo **{type_data['Nome']}**, "
            "todas despesas, receitas e investimentos vinculados a ele serão automaticamente excluídos!\n\n"
            "Deseja realmente continuar?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Sim, quero excluir", use_container_width=True):
                st.session_state.confirm_delete_type = False  # Resetar o estado de confirmação
                result = config['controller'].delete_type(type_data['type_id'])            
                if result:  # Se result for True, significa que o processo foi bem-sucedido
                    #Flags de atualização de sessão
                    st.session_state[config['type'] + '_type_updated'] = True
                    st.session_state[config['type'] + '_type_in_memorie'] = True
                    #st.session_state['expense_type_deleted'] = True #usado tela Despesas
                    # types_updated = config['type'] + '_types_updated'
                    # st.session_state[types_updated] = True
                    # types_in_memorie = config['type'] + '_types_in_memorie'
                    # st.session_state[types_in_memorie] = True    

                    # type_deleted = config['type'] + '_type_deleted' #Usado onde?
                    # st.session_state[type_deleted] = True       
                    st.rerun()  # Recarrega a página para refletir as mudanças 
        
        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.confirm_delete_type = False  # Resetar o estado de confirmação
                st.rerun() 

def type_view():
    columns_cat = ["cat_id", "cat_type", "cat_name", "cat_description"]
    controller_cat = CategoryController()
    # Listar Categorias
    categories_df = controller_cat.get_categories()

    #   Valida se existe categoria cadastrada
    if categories_df.empty:
        st.info('''
                 Nenhuma ***categoria*** cadastrada.\n\n
                 Clique no botão abaixo para ser redirecionado a página de ***Categorias***.
                 ''')
        with st.form(key='category_type_form', border=False):
            submit_button = st.form_submit_button(label="Ok", use_container_width=True)
            if submit_button:                        
                st.switch_page("pages/5_Categorias.py")   
            return   

    columns = ["type_id", "type_type", "type_name", "type_description", "cat_name"]
    controller = TypeController()
    # Listar tipos join category
    type_df = controller.get_types()

    try:
        # Renomear e ordenar o DataFrame
        types_df_renamed = type_df[columns].rename(
            columns={"type_name": "Nome", "type_description": "Descrição", "cat_name": "Categoria"}
        ).sort_values(by="Nome")

        # Renomear e ordenar o DataFrame
        categories_df_renamed = categories_df[columns_cat].rename(
            columns={"cat_name": "Nome", "cat_description": "Descrição"}
        ).sort_values(by="Nome")
       
        # Criação das abas
        expenses, incomes, investments = st.tabs(["Despesas", "Receitas", "Investimentos"])
        # Aba de Despesas
        with expenses:
            #if 'expense' not in categories_df['cat_type'].values:
            if 'cat_type' in categories_df.columns and 'expense' not in categories_df['cat_type'].values:
                st.info(f'''
                        Nenhuma categoria de ***Despesa*** cadastrada.\n\n
                        Clique no botão abaixo para cadastrar ou siga para as abas Receitas ou Investimentos!
                        ''')
                
                with st.form(key='expense_type_form', border=False):
                    submit_button = st.form_submit_button(label="Ok", use_container_width=True)
                    if submit_button:                        
                        #st.session_state['redirect_to_tab'] = 'expenses'  # ou 'expenses' ou 'investments'
                        st.switch_page("pages/5_Categorias.py")               
            else:
                # Filtrar apenas os tipos depesas
                expense_df = types_df_renamed[types_df_renamed['type_type'] == 'expense']

                # Filtrar apenas os depesas
                expense_cat_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'expense']
                
                # Configuração para despesa
                config = {
                    'type': 'expense',
                    'title': 'despesa',
                    'controller': controller,
                    'types_df_renamed': expense_df,  # Somente tipos despesas
                    'categories_df_renamed': expense_cat_df
                }

                menu(config)
                st.subheader(f"Tipos de {config['title']}s")
                #F5 and read() 
                if 'expense_type' not in st.session_state:
                    st.session_state['expense_type'] = expense_df

                if 'expense_type_updated' not in st.session_state:
                    st.session_state['expense_type_updated'] = False

#tem que aplicar em income, inestments...
                if 'page_type_category_expense_updated' not in st.session_state:
                    st.session_state['page_type_category_expense_updated'] = False
                if st.session_state['page_type_category_expense_updated']:
                    st.session_state['expense_type'] = expense_df
                    st.session_state['page_type_category_expense_updated'] = False
                # if 'expense_category_deleted' not in st.session_state:
                #     st.session_state['expense_category_deleted'] = False
                # if st.session_state['expense_category_deleted']:
                #     st.session_state['expense_type'] = expense_df
                #     st.session_state['expense_category_deleted'] = False
                
                # if 'expense_categories_types_updated' not in st.session_state:
                #     st.session_state['expense_categories_types_updated'] = False
                # if st.session_state['expense_categories_types_updated']:
                #     st.session_state['expense_type'] = expense_df
                #     st.session_state['expense_categories_types_updated'] = False

                #dados carregados em tela atualmente
                if st.session_state['expense_type_updated']: 
                    st.success("Operação realizada com sucesso!")
                    st.session_state['expense_type_updated'] = False
                    st.session_state['page_expense_type_updated'] = True #Controle de atualização na tela de Despesas        
                    if 'expense_type_in_memorie' not in st.session_state:
                        st.session_state['expense_type_in_memorie'] = False
                    if st.session_state['expense_type_in_memorie']:
                        st.session_state['expense_type'] = config['types_df_renamed']
                        st.session_state['expense_type_in_memorie'] = False
                if st.session_state["expense_type"].empty:
                    st.write("Nenhum dado disponível.")
                else:
                    st.dataframe(st.session_state['expense_type'], hide_index=True, use_container_width=True, column_config={"type_id": None, "type_type": None})
                
                 # Botão "Reset"
                if st.button("Recarregar", use_container_width=True, key='btn_expense'):
                    st.session_state['expense_type'] = expense_df        
                    st.rerun()
                      
        with incomes:
            if 'cat_type' in categories_df.columns and 'income' not in categories_df['cat_type'].values:
                st.info(f'''
                        Nenhuma categoria de ***Receita*** cadastrada.\n\n
                        Clique no botão abaixo para cadastrar ou siga para as abas Despesas ou Investimentos!
                        ''')
                with st.form(key='income_form', border=False):
                    submit_button = st.form_submit_button(label="Ok", use_container_width=True)
                    if submit_button:
                        #st.session_state['redirect_to_tab'] = 'incomes'  # ou 'expenses' ou 'investments'
                        st.switch_page("pages/5_Categorias.py")          
            else:
                # Filtrar apenas os tipos depesas
                income_df = types_df_renamed[types_df_renamed['type_type'] == 'income']

                # Filtrar apenas os depesas
                income_cat_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'income']
                
                # Configuração para receitas
                config = {
                    'type': 'income',
                    'title': 'receita',
                    'controller': controller,
                    'types_df_renamed': income_df,  # Somente tipos receitas
                    'categories_df_renamed': income_cat_df
                }

                menu(config)
                st.subheader(f"Tipos de {config['title']}s")
                #F5 and read() 
                if 'income_type' not in st.session_state:
                    st.session_state['income_type'] = income_df

                if 'income_type_updated' not in st.session_state:
                    st.session_state['income_type_updated'] = False

                if 'page_type_category_income_updated' not in st.session_state:
                    st.session_state['page_type_category_income_updated'] = False
                if st.session_state['page_type_category_income_updated']:
                    st.session_state['income_type'] = income_df
                    st.session_state['page_type_category_income_updated'] = False

                # if 'income_category_deleted' not in st.session_state:
                #     #st.session_state['expense_type'] = config['types_df_renamed']
                #     st.session_state['income_category_deleted'] = False
                
                # if st.session_state['income_category_deleted']:
                #     st.session_state['income_type'] = income_df
                #     st.session_state['income_category_deleted'] = False

                #dados carregados em tela atualmente
                if st.session_state['income_type_updated']: 
                    st.success("Operação realizada com sucesso!")
                    st.session_state['income_type_updated'] = False        
                    if 'income_type_in_memorie' not in st.session_state:
                        st.session_state['income_type_in_memorie'] = False
                    if st.session_state['income_type_in_memorie']:
                        st.session_state['income_type'] = config['types_df_renamed']
                        st.session_state['income_type_in_memorie'] = False
                if st.session_state["income_type"].empty:
                    st.write("Nenhum dado disponível.")
                else:
                    st.dataframe(st.session_state['income_type'], hide_index=True, use_container_width=True, column_config={"type_id": None, "type_type": None})

                 # Botão "Reset"
                if st.button("Recarregar", use_container_width=True, key='btn_income'):
                    st.session_state["income_type"] = income_df  # Atualiza o DataFrame mostrado na interface com o filtrado
                    st.rerun()
    
        with investments:
            if 'cat_type' in categories_df.columns and 'investment' not in categories_df['cat_type'].values:
                st.info(f'''
                        Nenhuma categoria de ***Investimento*** cadastrada.\n\n
                        Clique no botão abaixo para cadastrar ou siga para as abas Receitas ou Despesas!
                        ''')
                with st.form(key='investment_form', border=False):
                    submit_button = st.form_submit_button(label="Ok", use_container_width=True)
                    if submit_button:
                        #st.session_state['redirect_to_tab'] = 'investments'  # ou 'expenses' ou 'investments'
                        st.switch_page("pages/5_Categorias.py")              
            else:
                # Filtrar apenas os tipos investimentos
                investment_df = types_df_renamed[types_df_renamed['type_type'] == 'investment']

                # Filtrar apenas os investimentos
                investment_cat_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'investment']
                
                # Configuração para investimentos
                config = {
                    'type': 'investment',
                    'title': 'investimento',
                    'controller': controller,
                    'types_df_renamed': investment_df,  # Somente tipos investimentos
                    'categories_df_renamed': investment_cat_df
                }

                menu(config)
                st.subheader(f"Tipos de {config['title']}s")
                #F5 and read() 
                if 'investment_type' not in st.session_state:
                    st.session_state['investment_type'] = investment_df

                if 'investment_type_updated' not in st.session_state:
                    st.session_state['investment_type_updated'] = False

                if 'page_type_category_investment_updated' not in st.session_state:
                    st.session_state['page_type_category_investment_updated'] = False
                if st.session_state['page_type_category_investment_updated']:
                    st.session_state['investment_type'] = investment_df
                    st.session_state['page_type_category_investment_updated'] = False

                # if 'investment_category_deleted' not in st.session_state:
                #     #st.session_state['expense_type'] = config['types_df_renamed']
                #     st.session_state['investment_category_deleted'] = False
                
                # if st.session_state['investment_category_deleted']:
                #     st.session_state['investment_type'] = investment_df
                #     st.session_state['investment_category_deleted'] = False

                #dados carregados em tela atualmente
                if st.session_state['investment_type_updated']: 
                    st.success("Operação realizada com sucesso!")
                    st.session_state['investment_type_updated'] = False        
                    if 'investment_type_in_memorie' not in st.session_state:
                        st.session_state['investment_type_in_memorie'] = False
                    if st.session_state['investment_type_in_memorie']:
                        st.session_state['investment_type'] = config['types_df_renamed']
                        st.session_state['investment_type_in_memorie'] = False
                if st.session_state["investment_type"].empty:
                    st.write("Nenhum dado disponível.")
                else:
                    st.dataframe(st.session_state['investment_type'], hide_index=True, use_container_width=True, column_config={"type_id": None, "type_type": None})
                
                    # Botão "Reset"
                if st.button("Recarregar", use_container_width=True, key='btn_investment'):
                    st.session_state["investment_type"] = investment_df
                    st.rerun()
    except Exception as e:
        print(e)

type_view()