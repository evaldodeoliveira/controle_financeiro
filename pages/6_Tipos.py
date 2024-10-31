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
            if col3.button(f"Editar tipo de {config['title']}", use_container_width=True):
                pass
                #update(config)         
            if col4.button(f"Excluir tipo de {config['title']}", use_container_width=True):
                pass
                #delete(config) 
        except Exception as e:
            st.error(f"Erro ao acessar o dataframe: {e}")
    else:
        try:
            if col1.button(f"Incluir tipo de {config['title']}", use_container_width=True):
                create(config)
            if col2.button(f"Filtrar tipo de {config['title']}", use_container_width=True, disabled=True):
                read(config)
            if col3.button(f"Editar tipo de {config['title']}", use_container_width=True, disabled=True):
                pass
                #update(config)         
            if col4.button(f"Excluir tipo de {config['title']}", use_container_width=True, disabled=True):
                pass
                #delete(config) 
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
                types_updated = config['type'] + '_types_updated'
                st.session_state[types_updated] = True
                types_in_memorie = config['type'] + '_types_in_memorie'
                st.session_state[types_in_memorie] = True                               
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
            types_update = config['type'] + '_types_updated'
            st.session_state[types_update] = True
            st.session_state[config['type'] + '_type'] = df_filtred
            st.rerun()
        else:
            st.warning('Escolha ao menos um tipo e/ou categoria!')


def type_view():
    columns_cat = ["cat_id", "cat_type", "cat_name", "cat_description"]
    controller_cat = CategoryController()
    # Listar Categorias
    categories_df = controller_cat.get_categories()

    #   Valida se existe categoria cadastrada
    if categories_df.empty:
        st.info('''
                 Nenhuma categoria cadastrada.\n\n
                 Você será redirecionado a página de Categorias.
                 ''')
        if st.button("Ok", use_container_width=True):
            st.switch_page("pages/5_Categorias.py")
        return

    columns = ["type_id", "type_type", "type_name", "type_description", "cat_name"]
    controller = TypeController()
    # Listar tipos join category
    type_df = controller.get_types()
    #testa se vazio
    #if type_df.empty:
        #st.session_state['expense_types_updated'] = False
       #print("Aqui", type_df)
 
    #print("types_df\n\n", type_df, "\n\ncategories_df\n\n", categories_df)
    
    try:
        # Renomear e ordenar o DataFrame
        types_df_renamed = type_df[columns].rename(
            columns={"type_name": "Nome", "type_description": "Descrição", "cat_name": "Categoria"}
        ).sort_index(ascending=False)

        # Renomear e ordenar o DataFrame
        categories_df_renamed = categories_df[columns_cat].rename(
            columns={"cat_name": "Nome", "cat_description": "Descrição"}
        ).sort_index(ascending=False)
       
        # Criação das abas
        expenses, incomes, investments = st.tabs(["Despesas", "Receitas", "Investimentos"])
       
        # Aba de Despesas
        with expenses:
            if 'expense' not in categories_df['cat_type'].values:
                st.info(f'''
                        Nenhuma categoria de Despesa cadastrada.\n\n
                        Clique no botão abaixo para cadastrar ou siga para as abas Receitas ou Investimentos!
                        ''')
                if st.button("Ok", use_container_width=True):
                    st.switch_page("pages/5_Categorias.py")
                return

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
                #tenho que concatenar a coluna categoria nome aqui
                st.session_state['expense_type'] = expense_df

            if 'expense_types_updated' not in st.session_state:
                st.session_state['expense_types_updated'] = False

            if 'expense_category_deleted' not in st.session_state:
                #st.session_state['expense_type'] = config['types_df_renamed']
                st.session_state['expense_category_deleted'] = False
            
            if st.session_state['expense_category_deleted']:
                st.session_state['expense_type'] = expense_df
                st.session_state['expense_category_deleted'] = False

            #dados carregados em tela atualmente
            if st.session_state['expense_types_updated']:        
                st.success("Operação realizada com sucesso!")
                st.session_state['expense_types_updated'] = False        
                if 'expense_types_in_memorie' not in st.session_state:
                    st.session_state['expense_types_in_memorie'] = False
                if st.session_state['expense_types_in_memorie']:
                    st.session_state['expense_type'] = config['types_df_renamed']
                    st.session_state['expense_types_in_memorie'] = False
            if st.session_state["expense_type"].empty:
                st.write("Nenhum dado disponível.")
            else:
                st.dataframe(st.session_state['expense_type'], hide_index=True, use_container_width=True, column_config={"type_id": None, "type_type": None})
                      
    #     # Aba de Serviços
    #      # Aba de Investimentos
        # Botão "Reset"
        if st.button("Recarregar", use_container_width=True):
            st.session_state['expense_type'] = expense_df        
            # st.session_state["income"] = income_df  # Atualiza o DataFrame mostrado na interface com o filtrado
            # st.session_state["investment"] = investment_df
            st.rerun() 
    except Exception as e:
        print(e)

type_view()