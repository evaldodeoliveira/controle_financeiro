#abas/tipo
#cat Produdots (alimentação, bebida, limpeza, trasnporte, moradia, educação, saude, lazer)
#cat Servicos (comunicação, interterimento)
#cat receita (salario, bonus, aluguel, ...
#cat investimentos (fundos, tesouro direto, "acoes", cripto)
#pagamnento (credito, debito..)

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
            if col3.button(f"Editar categoria de {config['title']}", use_container_width=True):
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
            if col3.button(f"Editar categoria de {config['title']}", use_container_width=True, disabled=True):
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
            # Chama o método add_category e verifica se ocorreu erro
            result = config['controller'].add_category(config['type'], name, description)
            
            if result:  # Se result for True, significa que o processo foi bem-sucedido
                categories_updated = config['type'] + '_categories_updated'
                st.session_state[categories_updated] = True
                categories_in_memorie = config['type'] + '_categories_in_memorie'
                st.session_state[categories_in_memorie] = True                               
                st.rerun()                
        else:
            st.warning('Campo "Nome" obrigatório!')

@st.dialog("Filtrar categoria")
def read(config):   
    categories = config['categories_df_renamed']['Nome'].unique()
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
            categories_updated = config['type'] + '_categories_updated'
            st.session_state[categories_updated] = True
            st.session_state[config['type']] = df_filtred       
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

    col1, col2, col3 = st.columns(3)
    if col2.button("Excluir", use_container_width=True, type="primary"): 
        result = config['controller'].delete_category(category_data['cat_id'])            
        if result:  # Se result for True, significa que o processo foi bem-sucedido
            # Flags de atualização de sessão
            categories_updated = config['type'] + '_categories_updated'
            st.session_state[categories_updated] = True
            categories_in_memorie = config['type'] + '_categories_in_memorie'
            st.session_state[categories_in_memorie] = True                     
            st.rerun()  # Recarrega a página para refletir as mudanças           

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
                categories_updated = config['type'] + '_categories_updated'
                st.session_state[categories_updated] = True
                categories_in_memorie = config['type'] + '_categories_in_memorie'
                st.session_state[categories_in_memorie] = True                
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
        ).sort_index(ascending=False)
       
        # Criação das abas
        products, services = st.tabs(["Produtos", "Serviços"])
       
        # Aba de Produtos
        with products:
            # Filtrar apenas os produtos
            product_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'produto']

            # Configuração para produtos
            config = {
                'type': 'produto',
                'title': 'produto',
                'controller': controller,
                'categories_df_renamed': product_df  # Somente produtos
            }
            menu(config)
            st.subheader(f"Categorias de {config['title']}s")
            #F5 and read() 
            if 'produto' not in st.session_state:
                st.session_state['produto'] = product_df

            if 'produto_categories_updated' not in st.session_state:
                st.session_state['produto_categories_updated'] = False
            #dados carregados em tela atualmente
            if st.session_state['produto_categories_updated']:        
                st.success("Operação realizada com sucesso!")
                st.session_state['produto_categories_updated'] = False        
                if 'produto_categories_in_memorie' not in st.session_state:
                    st.session_state['produto_categories_in_memorie'] = False
                if st.session_state['produto_categories_in_memorie']:
                    st.session_state['produto'] = config['categories_df_renamed']
                    st.session_state['produto_categories_in_memorie'] = False
            if st.session_state["produto"].empty:
                st.write("Nenhum dado disponível.")
            else:
                st.dataframe(st.session_state['produto'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})
                      
        # Aba de Serviços
        with services:
            # Filtrar apenas os serviços
            service_df = categories_df_renamed[categories_df_renamed['cat_type'] == 'serviço']        
              
            # Configuração para serviços
            config = {
                'type': 'serviço',
                'title': 'serviço',
                'controller': controller,
                'categories_df_renamed': service_df  # Somente serviços
            }
            menu(config)
            st.subheader(f"Categorias de {config['title']}s")
             #F5 and read()
            if 'serviço' not in st.session_state:
                st.session_state['serviço'] = service_df

            if 'serviço_categories_updated' not in st.session_state:
                st.session_state['serviço_categories_updated'] = False                
            #dados carregados em tela atualmente
            if st.session_state['serviço_categories_updated']:        
                st.success("Operação realizada com sucesso!")
                st.session_state['serviço_categories_updated'] = False        
                if 'serviço_categories_in_memorie' not in st.session_state:
                    st.session_state['serviço_categories_in_memorie'] = False
                if st.session_state['serviço_categories_in_memorie']:
                    st.session_state['serviço'] = config['categories_df_renamed']
                    st.session_state['serviço_categories_in_memorie'] = False
            if st.session_state["serviço"].empty:
                st.write("Nenhum dado disponível.")
            else:
                st.dataframe(st.session_state['serviço'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})
 
        # Botão "Reset"
        if st.button("Reset"):
            st.session_state['produto'] = product_df        
            st.session_state["serviço"] = service_df  # Atualiza o DataFrame mostrado na interface com o filtrado
            st.rerun() 
    except Exception as e:
        print(e)

category_view()

# #avaliar mecanismo para usar mesmo codigo para abas distintas
# F5 and read() 
#             if 'produto' not in st.session_state:
#                 st.session_state['produto'] = product_df

#             if 'produto_categories_updated' not in st.session_state:
#                 st.session_state['produto_categories_updated'] = False
#             dados carregados em tela atualmente
#             if st.session_state['produto_categories_updated']:        
#                 st.success("Operação realizada com sucesso!")
#                 st.session_state['produto_categories_updated'] = False        
#                 if 'produto_categories_in_memorie' not in st.session_state:
#                     st.session_state['produto_categories_in_memorie'] = False
#                 if st.session_state['produto_categories_in_memorie']:
#                     st.session_state['produto'] = config['categories_df_renamed']
#                     st.session_state['produto_categories_in_memorie'] = False
#             if st.session_state["produto"].empty:
#                 st.write("Nenhum dado disponível.")
#             else:
#                 st.dataframe(st.session_state['produto'], hide_index=True, use_container_width=True, column_config={"cat_id": None, "cat_type": None})