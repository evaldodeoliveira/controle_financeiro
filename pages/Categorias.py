#abas/tipo
#cat Produdots (alimentação, bebida, limpeza, trasnporte, moradia, educação, saude, lazer)
#cat Servicos (comunicação, interterimento)
#cat receita (salario, bonus, aluguel, ...
#cat investimentos (fundos, tesouro direto, "acoes", cripto)
#pagamnento (credito, debito..)

import streamlit as st
import inspect
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
            #Verificar a função deste "action"
            #if "action" not in st.session_state:
                if col1.button(f"Incluir categoria de {config['title']}", use_container_width=True):
                    create(config)
                if col2.button(f"Filtrar categoria de {config['title']}", use_container_width=True):
                    read(config)
                if col3.button(f"Editar categoria de {config['title']}", use_container_width=True):
                    update(config)         
                if col4.button(f"Excluir categoria de {config['title']}", use_container_width=True):
                    delete(config) 
        except Exception as e:
            print("Erro ao acessar o dataframe", e)
    else:
        try:
            #Verificar a função deste "action"
            #if "action" not in st.session_state:
                if col1.button(f"Incluir categoria de {config['title']}", use_container_width=True):
                    create(config)
                if col2.button(f"Filtrar categoria de {config['title']}", use_container_width=True, disabled=True):
                    read(config)
                if col3.button(f"Editar categoria de {config['title']}", use_container_width=True, disabled=True):
                    update(config)         
                if col4.button(f"Excluir categoria de {config['title']}", use_container_width=True, disabled=True):
                    delete(config) 
        except Exception as e:
            print("Erro ao acessar o dataframe", e)
    
    st.subheader(f"Categorias de {config['title']}s")
    
@st.dialog("Cadastrar categoria")
def create(config):
    name = st.text_input("Nome:")
    description = st.text_area("Descrição:")

    col1, col2, col3 = st.columns(3)
    if col2.button("Incluir", use_container_width=True):            
        if name:
            try:
                config['controller'].add_category(config['type'], name, description)
                st.session_state['categories_updated'] = True  
                st.session_state['categories_in_memorie'] = True          
                st.rerun()                
            except Exception as e:
                st.error(f"Operação não realizada! \n\n Verifique se a categoria já existe!")                      
        else:
            st.error('Campo "Nome" obrigatório!')

@st.dialog("Filtrar categoria")
def read(config):    
    categories = config['categories_df_renamed']['Nome'].unique()
    category = st.multiselect("Categoria", categories, placeholder='')
    mask = config['categories_df_renamed']['Nome'].str.contains('|'.join(category))
    df_filtred = config['categories_df_renamed'][mask]
    #colocar um filtro config['type'] == produto,servico...
    #a ideia é mostra na aba de produto soment categoria de produstos e assim sucessivamente
    #lembrando no caso do F5?? defualt pode ser produtos
    #validar abordagem de clausa de restrição no BD x flitro df

    #Revisar abordagem de segmentar por tipo de categoria, pois remedio e plano são saude, por exemplo
    #ou cria uma tabela de categori para cada um (categoria_produto, cat_servi, cat_invest...)
    #ou tira o unique do nome da tabela categoria (vou tentar esta abordagem e usar o campo type para fltro)
    #se tirar o unique tenho que garantir que o nome da categoria não possa se repetir para o mesmo tipo
    #ex: prod(nome:cerveja, tipo: produto, nome: cerveja, tipo: produto)
    #avaliar modelagem usando especilização:
    #cat(nome, descrição, tipo_id), tipo(id,nome(unique)) não exatamente isto!!!

    #esta dando msg de sucesso ao tentar salvar categoria ja existente (unique)
    #
    #Erro ao clicar nos botões de editar e excluir quando o bd esta vazio
    
    col1, col2, col3 = st.columns(3)
    if col2.button("Filtrar", use_container_width=True):
        if category:
            st.session_state['categories_updated'] = True
            st.session_state["df"] = df_filtred
            st.rerun()
        else:
            st.error('Escolha ao menos uma categoria!')

@st.dialog("Excluir categoria")
def delete(config):
        #if not config['categories_df_renamed'].empty:
        #    try:       
                categories = config['categories_df_renamed']['Nome'].unique()
                category = st.selectbox("Categoria", categories, placeholder='')
                category_data = config['categories_df_renamed'][config['categories_df_renamed']['Nome'] == category].iloc[0]
                st.text_input("Nome:", value=category_data["Nome"], disabled=True)
                st.text_area("Descrição:", value=category_data["Descrição"], disabled=True) 

                col1, col2, col3 = st.columns(3)
                if col2.button("Excluir", use_container_width=True, type="primary"):            
                    config['controller'].delete_category(category_data['cat_id'])
                    st.session_state['categories_updated'] = True  
                    st.session_state['categories_in_memorie'] = True          
                    st.rerun()        
        #    except Exception as e:
        #        print("Erro ao acessar o dataframe", e)
        #else:
        #    pass
            #st.write("Não há dados a serem exibidos!")  


        #categories = config['categories_df_renamed']['Nome'].unique()
        #category = st.selectbox("Categoria", categories)
        #category_data = config['categories_df_renamed'][config['categories_df_renamed']['Nome'] == category].iloc[0]
        #st.text_input("Nome:", value=category_data["Nome"], disabled=True)
        #st.text_area("Descrição:", value=category_data["Descrição"], disabled=True)
      
        # col1, col2, col3 = st.columns(3)
        # if col2.button("Excluir", use_container_width=True, type="primary"):            
        #     config['controller'].delete_category(category_data['cat_id'])
        #     st.session_state['categories_updated'] = True  
        #     st.session_state['categories_in_memorie'] = True          
        #     st.rerun()

@st.dialog("Alterar categoria")     
def update(config):
    categories = config['categories_df_renamed']['Nome'].unique()
    category = st.selectbox("Categoria", categories, placeholder='')
    category_data = config['categories_df_renamed'][config['categories_df_renamed']['Nome'] == category].iloc[0]  
   
    name = st.text_input("Nome:", value=category_data["Nome"])
    description = st.text_area("Descrição:", value=category_data["Descrição"])
#criar mecanismo que force ao menos o campo name ser preenchido a fim de fiar com categoria vazia
    col1, col2, col3 = st.columns(3)
    if col2.button("Alterar", use_container_width=True, type="primary"):          
        config['controller'].update_category(category_data['cat_id'], name, description)
        st.session_state['categories_updated'] = True  
        st.session_state['categories_in_memorie'] = True          
        st.rerun()

def category_view():
    print(f"Executing {inspect.currentframe().f_code.co_name}")
    columns = ["cat_id", "cat_type", "cat_name", "cat_description"]
    controller = CategoryController()

    # Listar Categorias
    categories_df = controller.get_categories()
    try:
        categories_df_renamed = categories_df[columns].rename(columns={"cat_name": "Nome", "cat_description": "Descrição"}).sort_index(ascending=False)

        products, services = st.tabs(["Produtos", "Serviços"])
        with products:
            config = {'type': 'produto', 'title': 'produto', 'controller': controller, 'categories_df_renamed': categories_df_renamed}
            menu(config)       
        with services:
            #config = {'type': 'service', 'title': 'serviço'}
            #menu(config)
            pass

        #F5   
        if 'categories_updated' not in st.session_state:
            st.session_state['categories_updated'] = False
            st.session_state["df"] = categories_df_renamed     

        #dados carregados em tela atualmente
        if st.session_state['categories_updated']:        
            st.success("Operação realizada com sucesso!")
            st.session_state['categories_updated'] = False
            
            if 'categories_in_memorie' not in st.session_state:
                st.session_state['categories_in_memorie'] = False

            if st.session_state['categories_in_memorie']:
                st.session_state["df"] = categories_df_renamed
                st.session_state['categories_in_memorie'] = False
        
        if st.session_state["df"].empty:
            st.write("Nenhum dado disponível.")
        else:
            st.dataframe(st.session_state["df"], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})

        if st.button("Reset"):        
            st.session_state["df"] = categories_df_renamed
            st.rerun() 
    except Exception as e:
        print(e)

category_view()