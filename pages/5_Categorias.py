import streamlit as st
import numpy as np
from controllers.category_controller import CategoryController

st.set_page_config(
    page_title="Categorias",
    page_icon=":material/category:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")

def menu(config):
    col1, col2, col3, col4 = st.columns(4)
   
    if not config['categories_df_renamed'].empty:
        try:
            if col1.button(f"Incluir categoria de {config['title']}", use_container_width=True):
                create(config)
            if col2.button(f"Filtrar categoria de {config['title']}", use_container_width=True):
                read(config)
            if col3.button(f"Alterar categoria de {config['title']}", use_container_width=True):
                update(config)         
            if col4.button(f"Excluir categoria de {config['title']}", use_container_width=True):
                delete(config) 
        except Exception as e:
            st.error(f"Erro ao acessar o dataframe: {e}")
    else:
        try:
            if col1.button(f"Incluir categoria de {config['title']}", use_container_width=True):
                create(config)
            if col2.button(f"Filtrar categoria de {config['title']}", use_container_width=True, disabled=True):
                read(config)
            if col3.button(f"Alterar categoria de {config['title']}", use_container_width=True, disabled=True):
                update(config)         
            if col4.button(f"Excluir categoria de {config['title']}", use_container_width=True, disabled=True):
                delete(config) 
        except Exception as e:
            st.error(f"Erro ao acessar o dataframe: {e}")   
      
@st.dialog("Cadastrar categoria")
def create(config):
    name = st.text_input("Nome:")
    description = st.text_area("Descrição:")

    col1, col2, col3 = st.columns(3)
    if col2.button("Incluir", use_container_width=True):            
        if name:
            result = config['controller'].add_category(config['type'], name, description)
            if result:
                st.session_state[config['type'] + '_category_updated'] = True
                st.session_state[config['type'] + '_category_in_memorie'] = True
                # categories_updated = config['type'] + '_categories_updated'
                # st.session_state[categories_updated] = True
                # categories_in_memorie = config['type'] + '_categories_in_memorie'
                # st.session_state[categories_in_memorie] = True                               
                st.rerun()                
        else:
            st.warning('Campo "Nome" obrigatório!')

@st.dialog("Filtrar categoria")
def read(config):   
    categories = sorted(config['categories_df_renamed']['Nome'].unique())
    category = st.multiselect("Categoria", categories, placeholder='')

    # Valor do tipo está fixo na variável config['type']
    cat_type_selected = config['type']

    # Aplica o filtro combinando o Nome selecionado e o tipo fixo
    mask = (
        config['categories_df_renamed']['Nome'].isin(category) &
        (config['categories_df_renamed']['cat_type'] == cat_type_selected)
    )
    
    df_filtred = config['categories_df_renamed'][mask]
    
    col1, col2, col3 = st.columns(3)
    if col2.button("Filtrar", use_container_width=True):        
        if category:
            st.session_state[config['type'] + '_category_updated'] = True
            st.session_state[config['type'] + '_category'] = df_filtred
            #st.session_state[config['type'] + '_categories_in_memorie'] = True
            # categories_updated = config['type'] + '_categories_updated'
            # st.session_state[categories_updated] = True
            # categories = config['type'] + '_categories'
            # st.session_state[categories] = df_filtred       
            st.rerun()
        else:
            st.warning('Escolha ao menos uma categoria!')

@st.dialog("Excluir categoria")
def delete(config):       
    categories = config['categories_df_renamed']['Nome'].unique()
    categories = np.insert(categories, 0, "Selecione uma categoria")  # Adiciona a opção inicial

    category = st.selectbox("Categoria", categories, placeholder='', index=0)

    # Verifica se o usuário selecionou "Selecione uma categoria"
    if category == "Selecione uma categoria":
        st.warning("Por favor, selecione uma categoria válida.")  # Exibe uma mensagem de aviso
        return  # Interrompe a execução até que uma categoria válida seja selecionada
    
    category_data = config['categories_df_renamed'][config['categories_df_renamed']['Nome'] == category]
    # Verifica se o filtro retornou algum dado
    if category_data.empty:
        st.error("Categoria não encontrada.")
        return
    
    category_data = category_data.iloc[0]  # Obtém o primeiro resultado válido
    
    st.text_input("Nome:", value=category_data["Nome"], disabled=True)
    st.text_area("Descrição:", value=category_data["Descrição"], disabled=True) 
    
    # Inicializar um estado para controle de confirmação, se ainda não existir
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    # Espaço vazio para exibir a mensagem de confirmação/cancelamento
    message_placeholder = st.empty()

    col1, col2, col3 = st.columns(3)
    # Botão para iniciar a exclusão
    if col2.button("Excluir", type="primary", use_container_width=True):
        st.session_state.confirm_delete = True  # Ativar o estado de confirmação

    # Verificar se o estado de confirmação está ativo
    if st.session_state.confirm_delete:
        # Mensagem de confirmação com opção para confirmar ou cancelar
        st.warning(
            f"⚠️ Ao excluir a categoria **{category_data['Nome']}**, "
            "todos os tipos, despesas, receitas e investimentos vinculados a ela serão automaticamente excluídos!\n\n"
            "Deseja realmente continuar?"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Sim, quero excluir", use_container_width=True):
                st.session_state.confirm_delete = False  # Resetar o estado de confirmação
                result = config['controller'].delete_category(category_data['cat_id'])            
                if result:  # Se result for True, significa que o processo foi bem-sucedido
                    #Flags de atualização de sessão
                    st.session_state[config['type'] + '_category_updated'] = True
                    st.session_state[config['type'] + '_category_in_memorie'] = True
                    
                    # categories_updated = config['type'] + '_categories_updated'
                    # st.session_state[categories_updated] = True
                    # categories_in_memorie = config['type'] + '_categories_in_memorie'
                    # st.session_state[categories_in_memorie] = True    

                    # category_deleted = config['type'] + '_category_deleted'
                    # st.session_state[category_deleted] = True       
                    
                    st.rerun()  # Recarrega a página para refletir as mudanças 
        
        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.confirm_delete = False  # Resetar o estado de confirmação
                st.rerun() 

@st.dialog("Alterar categoria")     
def update(config):
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

    category_data = category_data.iloc[0]  # Obtém o primeiro resultado válido
        
    # Input de texto para o nome
    name = st.text_input("Nome:", value=category_data["Nome"])

    # Text area para a descrição
    description = st.text_area("Descrição:", value=category_data["Descrição"])

    # Colunas para os botões
    col1, col2, col3 = st.columns(3)
    
    if col2.button("Alterar", use_container_width=True, type="primary"):         
        # Verifica se o campo foi apagado ou está vazio        
        if not name:
            st.warning("O campo nome não pode estar vazio. Por favor, preencha.")
        else:            
            # Atualiza a categoria            
            result = config['controller'].update_category(category_data['cat_id'], config['type'], name, description)
            
            if result:  # Se result for True, significa que o processo foi bem-sucedido
                # Flags de atualização de sessão
                
                # #usada para atualizar DF na tela de Tipos
                # categories_types_updated = config['type'] + '_categories_types_updated'
                # st.session_state[categories_types_updated] = True
                #usada na tela de categoria
                st.session_state[config['type'] + '_category_updated'] = True
                st.session_state[config['type'] + '_category_in_memorie'] = True

                # categories_updated = config['type'] + '_categories_updated'
                # st.session_state[categories_updated] = True
                
                # categories_in_memorie = config['type'] + '_categories_in_memorie'
                # st.session_state[categories_in_memorie] = True                
                st.rerun()  # Recarrega a página para refletir as mudanças

def category_view():    
    columns = ["cat_id", "cat_type", "cat_name", "cat_description"]
    controller = CategoryController()

    # Listar Categorias
    categories_df = controller.get_categories()
    
    try:
        # Renomear e ordenar o DataFrame
        categories_df_renamed = categories_df[columns].rename(
            columns={"cat_name": "Nome", "cat_description": "Descrição"}
        ).sort_values(by="Nome")
       
        # Criação das abas
        expenses, incomes, investments = st.tabs(["Despesas", "Receitas", "Investimentos"])
       
        # Aba de Despesas
        with expenses:
            # Filtrar apenas os depesas
            expense_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'expense']

            # Configuração para despesa
            config = {
                'type': 'expense',
                'title': 'despesa',
                'controller': controller,
                'categories_df_renamed': expense_df  # Somente despesas
            }
            menu(config)
            st.subheader(f"Categorias de {config['title']}s")
            #F5 and read() 
            if 'expense_category' not in st.session_state:
                st.session_state['expense_category'] = expense_df

            if 'expense_category_updated' not in st.session_state:
                st.session_state['expense_category_updated'] = False

            #dados carregados em tela atualmente
            if st.session_state['expense_category_updated']:       
                st.success("Operação realizada com sucesso!")
                st.session_state['expense_category_updated'] = False 
                st.session_state['page_expense_category_updated'] = True #Controle de atualização na tela de Despesas
                st.session_state['page_type_category_expense_updated'] = True #Controle de atualização na tela de Tipos/Despesas      
                if 'expense_category_in_memorie' not in st.session_state:
                    st.session_state['expense_category_in_memorie'] = False
                if st.session_state['expense_category_in_memorie']:
                    st.session_state['expense_category'] = config['categories_df_renamed']
                    st.session_state['expense_category_in_memorie'] = False

            if st.session_state["expense_category"].empty:
                st.write("Nenhum dado disponível.")
            else:
                st.dataframe(st.session_state['expense_category'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})
                
        # Aba de Serviços
        with incomes:
            # Filtrar apenas as receitas
            income_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'income']        
            
            # Configuração para receitas
            config = {
                'type': 'income',
                'title': 'receita',
                'controller': controller,
                'categories_df_renamed': income_df  # Somente receitas
            }
            menu(config)
            st.subheader(f"Categorias de {config['title']}s")
            #F5 and read()
            if 'income_category' not in st.session_state:
                st.session_state['income_category'] = income_df

            if 'income_category_updated' not in st.session_state:
                st.session_state['income_category_updated'] = False  

            #dados carregados em tela atualmente
            if st.session_state['income_category_updated']:        
                st.success("Operação realizada com sucesso!")
                st.session_state['income_category_updated'] = False
                #st.session_state['page_income_category_updated'] = True #Controle de atualização na tela de Receitas
                st.session_state['page_type_category_income_updated'] = True #Controle de atualização na tela de Tipos/Receitas        
                if 'income_category_in_memorie' not in st.session_state:
                    st.session_state['income_category_in_memorie'] = False
                if st.session_state['income_category_in_memorie']:
                    st.session_state['income_category'] = config['categories_df_renamed']
                    st.session_state['income_category_in_memorie'] = False

            if st.session_state["income_category"].empty:
                st.write("Nenhum dado disponível.")
            else:
                st.dataframe(st.session_state['income_category'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})
        
        # Aba de Investimentos
        with investments:
            # Filtrar apenas as receitas
            investment_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'investment']        
            
            # Configuração para receitas
            config = {
                'type': 'investment',
                'title': 'investimento',
                'controller': controller,
                'categories_df_renamed': investment_df  # Somente investimentos
            }
            menu(config)
            st.subheader(f"Categorias de {config['title']}s")
            #F5 and read()
            if 'investment_category' not in st.session_state:
                st.session_state['investment_category'] = investment_df

            if 'investment_category_updated' not in st.session_state:
                st.session_state['investment_category_updated'] = False

            #dados carregados em tela atualmente
            if st.session_state['investment_category_updated']:        
                st.success("Operação realizada com sucesso!")
                st.session_state['investment_category_updated'] = False
                #st.session_state['page_investment_category_updated'] = True #Controle de atualização na tela de Investimentos
                st.session_state['page_type_category_investment_updated'] = True #Controle de atualização na tela de Tipos/Invetimentos         
                if 'investment_category_in_memorie' not in st.session_state:
                    st.session_state['investment_category_in_memorie'] = False
                if st.session_state['investment_category_in_memorie']:
                    st.session_state['investment_category'] = config['categories_df_renamed']
                    st.session_state['investment_category_in_memorie'] = False

            if st.session_state["investment_category"].empty:
                st.write("Nenhum dado disponível.")
            else:
                st.dataframe(st.session_state['investment_category'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})

        # Botão "Reset"
        if st.button("Recarregar", use_container_width=True, key='btn_categories'):
            st.session_state['expense_category'] = expense_df        
            st.session_state["income_category"] = income_df  # Atualiza o DataFrame mostrado na interface com o filtrado
            st.session_state["investment_category"] = investment_df
            st.rerun() 
    except Exception as e:
        print(e)

category_view()