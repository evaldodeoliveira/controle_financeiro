import streamlit as st
import numpy as np
from controllers.type_controller import TypeController
from controllers.category_controller import CategoryController

st.set_page_config(
    page_title="Tipos",
   # page_icon=":material/type:",
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
                pass
                #read(config)
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
                pass
                #read(config)
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
    cat_type = config['categories_df_renamed']['cat_type']
    # Valida se o tipo a ser cadastrado tem despesa cadastrada
    if cat_type.ne(config['type']).all():
        st.error("Cadastre a catagoria despesa!!!!")
        st.write("colocar um botão e confirmação e redirecionar para tipos")
        return
    
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
    types = config['types_df_renamed']['Nome'].unique()
    type = st.multiselect("Tipo", types, placeholder='')

    # Valor do tipo está fixo na variável config['type']
    #type_type_selected = config['type']

    # Aplica o filtro combinando o Nome selecionado e o tipo fixo
    # mask = (
    #     config['categories_df_renamed']['Nome'].isin(type) &
    #     (config['categories_df_renamed']['cat_type'] == type_type_selected)
    # )
    
    #df_filtred = config['categories_df_renamed'][mask]
    
    col1, col2, col3 = st.columns(3)
    if col2.button("Filtrar", use_container_width=True):        
        if type:
            # types_update = config['type'] + '_types_updated'
            # st.session_state[types_update] = True
            # st.session_state[config['type']] = df_filtred       
            st.rerun()
        else:
            st.warning('Escolha ao menos uma categoria!')


def type_view():
    columns_cat = ["cat_id", "cat_type", "cat_name", "cat_description"]
    controller_cat = CategoryController()
    # Listar Categorias
    categories_df = controller_cat.get_categories()

    #   Validar se existe categoria cadastrada
    if categories_df.empty:
        st.error("Cadastre as categorias primeiramente!")
        st.write("colocar um botãod e confirmação e redirecionar para categorias")
        return
    
    columns = ["type_id", "type_type", "type_name", "type_description"]
    controller = TypeController()
    # Listar tipos
    type_df = controller.get_types()
#validar se tipos <> null concat com categoria
 
    print("types_df", type_df, "\n\ncategories_df", categories_df)
    
    try:
        # Renomear e ordenar o DataFrame
        types_df_renamed = type_df[columns].rename(
            columns={"type_name": "Nome", "type_description": "Descrição"}
        ).sort_index(ascending=False)

        # Renomear e ordenar o DataFrame
        categories_df_renamed = categories_df[columns_cat].rename(
            columns={"cat_name": "Nome", "cat_description": "Descrição"}
        ).sort_index(ascending=False)
       
        # Criação das abas
        expenses, incomes, investments = st.tabs(["Despesas", "Receitas", "Investimentos"])
       
        # Aba de Despesas
        with expenses:
            # Filtrar apenas os depesas
            expense_df = types_df_renamed[types_df_renamed['type_type'] == 'expense']

            # Filtrar apenas os depesas
            expense_cat_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'expense']
#validar se vazio não permitir fazer nada nesta aba da tela de tipos
            print("expense_df",expense_df, "\n\nexpense_cat_df", expense_cat_df)
            
            # Configuração para despesa
            config = {
                'type': 'expense',
                'title': 'despesa',
                'controller': controller,
                'types_df_renamed': expense_df,  # Somente despesas
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
    #     with incomes:
    #         # Filtrar apenas as receitas
    #         income_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'income']        
              
    #         # Configuração para receitas
    #         config = {
    #             'type': 'income',
    #             'title': 'receita',
    #             'controller': controller,
    #             'categories_df_renamed': income_df  # Somente receitas
    #         }
    #         menu(config)
    #         st.subheader(f"Categorias de {config['title']}s")
    #          #F5 and read()
    #         if 'income' not in st.session_state:
    #             st.session_state['income'] = income_df

    #         if 'income_categories_updated' not in st.session_state:
    #             st.session_state['income_categories_updated'] = False                
    #         #dados carregados em tela atualmente
    #         if st.session_state['income_categories_updated']:        
    #             st.success("Operação realizada com sucesso!")
    #             st.session_state['income_categories_updated'] = False        
    #             if 'income_categories_in_memorie' not in st.session_state:
    #                 st.session_state['income_categories_in_memorie'] = False
    #             if st.session_state['income_categories_in_memorie']:
    #                 st.session_state['income'] = config['categories_df_renamed']
    #                 st.session_state['income_categories_in_memorie'] = False
    #         if st.session_state["income"].empty:
    #             st.write("Nenhum dado disponível.")
    #         else:
    #             st.dataframe(st.session_state['income'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})
        
    #      # Aba de Investimentos
    #     with investments:
    #         # Filtrar apenas as receitas
    #         investment_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'investment']        
              
    #         # Configuração para receitas
    #         config = {
    #             'type': 'investment',
    #             'title': 'investimento',
    #             'controller': controller,
    #             'categories_df_renamed': investment_df  # Somente investimentos
    #         }
    #         menu(config)
    #         st.subheader(f"Categorias de {config['title']}s")
    #          #F5 and read()
    #         if 'investment' not in st.session_state:
    #             st.session_state['investment'] = investment_df

    #         if 'investment_categories_updated' not in st.session_state:
    #             st.session_state['investment_categories_updated'] = False                
    #         #dados carregados em tela atualmente
    #         if st.session_state['investment_categories_updated']:        
    #             st.success("Operação realizada com sucesso!")
    #             st.session_state['investment_categories_updated'] = False        
    #             if 'investment_categories_in_memorie' not in st.session_state:
    #                 st.session_state['investment_categories_in_memorie'] = False
    #             if st.session_state['investment_categories_in_memorie']:
    #                 st.session_state['investment'] = config['categories_df_renamed']
    #                 st.session_state['investment_categories_in_memorie'] = False
    #         if st.session_state["investment"].empty:
    #             st.write("Nenhum dado disponível.")
    #         else:
    #             st.dataframe(st.session_state['investment'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})
 
        # Botão "Reset"
        if st.button("Recarregar", use_container_width=True):
            # st.session_state['expense'] = expense_df        
            # st.session_state["income"] = income_df  # Atualiza o DataFrame mostrado na interface com o filtrado
            # st.session_state["investment"] = investment_df
            st.rerun() 
    except Exception as e:
        print(e)

type_view()