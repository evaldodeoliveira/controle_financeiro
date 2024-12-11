import streamlit as st
from controllers.auth_manager import is_authenticated, show_login
#from controllers.auth_controller import AuthController
import pandas as pd
import plotly.express as px
from datetime import date, timedelta, datetime
from controllers.expense_controller import ExpenseController
from controllers.category_controller import CategoryController
import locale
import warnings
from repositories.database_repository import DataManager

#from repositories.user_repository import UserRepository

# import plotly.io as pio

st.set_page_config(
    page_title="Dashboard",
    page_icon=":material/dashboard:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
    }
)

warnings.simplefilter("ignore", category=FutureWarning)
# Define o locale para português
# locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Para Linux
# locale.setlocale(locale.LC_TIME, 'pt_BR')      # Para Windows, caso o anterior não funcione

# Configurando o Plotly para exibir os meses em português
#pio.templates.default = "plotly_dark"  # Opcional: define um tema escuro para o gráfico

# Configuração do locale para exibir datas e valores em formato brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def expand_installments(row):
    """
    Expande parcelas para cada mês com base na data inicial e no número de parcelas.
    Inicia no mês subsequente ao mes da compra.
    Ex: se compra realizada em 01/12/2024 em duas parcelas de 100,00.
    Serão mostradas nos meses 01/25 e 02/25
    """
    installments = []
    if row['Parcelas'] > 0:  # Se for um pagamento parcelado
        date_start = row['Data']
        date_end = row['Última parcela']

        # Gerar todas as parcelas com base em 'Data' e 'Última parcela'
        dates_installments = pd.date_range(start=date_start, end=date_end, freq='MS')  # Frequência mensal, começa sempre no 1º do mes seguinte
        value_installment = row['Valor']  # Valor de cada parcela
        for date_installment in dates_installments:
            installments.append({'Mes': date_installment, 'Tipo': 'Crédito', 'Valor': value_installment})
    else:
        # Adicionar despesa à vista como uma única entrada
        installments.append({'Mes': row['Data'], 'Tipo': 'À Vista', 'Valor': row['Valor']})
    return installments

def expand_installments_v2(row):
    """
    Expande parcelas para cada mês com base na data inicial e no número de parcelas,
    garantindo que a primeira parcela seja registrada no mesmo mês da data inicial.
    """
    installments = []
    if row['Parcelas'] > 0:  # Se for pagamento parcelado
        date_start = row['Data']
        num_installments = row['Parcelas']
        value_installment = row['Valor']  # Valor de cada parcela

        # Gerar todas as parcelas começando do mês da data inicial
        for i in range(num_installments):
            installment_date = date_start + pd.DateOffset(months=i) #pega primeira parcela
            installments.append({'Mes': installment_date, 'Tipo': 'Crédito', 'Valor': value_installment})
    else:
        # Adicionar despesa à vista como uma única entrada
        installments.append({'Mes': row['Data'], 'Tipo': 'À Vista', 'Valor': row['Valor']})
    return installments

#colocar em um arquivo util.py, pois usa em mais arquivos
def format_brl(value):
    return f"R${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def get_expense():
    # Obtém os dados
    expense_controller = ExpenseController()
    expense_df = expense_controller.get_expenses()

    if not isinstance(expense_df, pd.DataFrame):
        # Se não for um DataFrame, cria um DataFrame vazio
        expense_df = pd.DataFrame()

    return expense_df

@st.cache_data
def get_category():
    category_controller = CategoryController()
    category_df = category_controller.get_categories()

    if not isinstance(category_df, pd.DataFrame):
        # Se não for um DataFrame, cria um DataFrame vazio
        category_df = pd.DataFrame()

    return category_df

@st.cache_data
def get_filtered_data(expense_df, category_df):
    """
    Filtra e formata o DataFrame consolidado entre despesas e categorias.
    """
    # Combina despesas com categorias
    merged_df = pd.merge(
        expense_df, 
        category_df, 
        left_on='type_category_id', 
        right_on='cat_id', 
        how='left', 
        suffixes=('', '_category')
    )

    # Seleciona e renomeia colunas
    merged_df = merged_df[[
        'exp_date', 'exp_value', 'exp_description', 'exp_number_of_installments', 
        'exp_final_date_of_installment', 'exp_value_total_installment', 
        'cat_name', 'type_name', 'pay_name'
    ]].rename(columns={
        'exp_date': 'Data', 
        'exp_value': 'Valor', 
        'exp_description': 'Descrição Despesa',
        'exp_number_of_installments': 'Parcelas',
        'exp_final_date_of_installment': 'Última parcela',
        'exp_value_total_installment': 'Valor total das parcelas',
        'cat_name': 'Categoria', 
        'type_name': 'Tipo',
        'pay_name': 'Pagamento'
    })

    # Converte colunas de data
    merged_df['Data'] = pd.to_datetime(merged_df['Data'])
    merged_df['Última parcela'] = pd.to_datetime(merged_df['Última parcela'])

    return merged_df

@st.cache_data
def chart_installment_evolution_v2(df_filtrado):
    """
    Gera um gráfico de linha mostrando a evolução das parcelas por mês,
    considerando todas as parcelas a partir da data de registro
    até a última parcela, sem aplicar filtros de data.
    """

    # Garantir que 'Parcelas' seja numérico
    df_filtrado['Parcelas'] = pd.to_numeric(df_filtrado['Parcelas'], errors='coerce').fillna(0).astype(int)
    df_credito = df_filtrado[df_filtrado['Parcelas'] > 0]

    # Expandir as parcelas usando a função expand_installments
    parcelas_expandidas = []
    for _, row in df_credito.iterrows():
        parcelas_expandidas.extend(expand_installments_v2(row))

    # Criar DataFrame consolidado das parcelas
    if not parcelas_expandidas:
        # Se não houver parcelas, criar um gráfico vazio
        fig = px.line(
            title='Evolução das Parcelas por Mês - V2',
            labels={'Mes': 'Mês do Parcelamento', 'Valor': 'Montante de Parcelas'}
        )
        fig.add_annotation(
            x=0.5, y=0.5, text="Nenhuma despesa parcelada encontrada.",
            showarrow=False, font=dict(size=16, color="red"), align="center"
        )
        return fig

    df_parcelas = pd.DataFrame(parcelas_expandidas)

    # Agrupar os valores por mês
    montante_mensal = (
        df_parcelas.groupby(df_parcelas['Mes'].dt.to_period("M"))['Valor'].sum().reset_index()
    )
    montante_mensal['Mes'] = montante_mensal['Mes'].dt.to_timestamp()

    # Adicionar colunas formatadas para os tooltips
    montante_mensal['Valor Formatado'] = montante_mensal['Valor'].apply(format_brl)
    montante_mensal['Data Formatada'] = montante_mensal['Mes'].dt.strftime('%b de %Y').str.capitalize()

    # Gerar o gráfico de linha
    fig = px.line(
        montante_mensal,
        x='Mes',
        y='Valor',
        title='Evolução das Parcelas por Mês',
        labels={
            'Mes': 'Mês do Parcelamento',
            'Valor': 'Montante de Parcelas (R$)'
        },
        hover_data={'Valor': False, 'Valor Formatado': True, 'Data Formatada': True}  # Exibe valores formatados no tooltip
    )

    # Estilizar o gráfico
    fig.update_traces(
        mode="lines+markers",
        line=dict(width=2),
        hovertemplate='<b>Mês:</b> %{customdata[1]}<br><b>Montante:</b> %{customdata[0]}<extra></extra>'
    )
    fig.update_layout(
        yaxis=dict(
            tickprefix='R$',  # Prefixo no eixo Y
            title='Montante de Parcelas (R$)'
        ),
        xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
        xaxis=dict(
            tickmode='array',
            tickvals=montante_mensal['Mes'],
            ticktext=montante_mensal['Mes'].dt.strftime('%b %Y').str.capitalize()
        ),
        #title_x=0.3,
    )

    return fig

@st.cache_data
def generate_pie_chart_category_v2(df, data_inicio, data_fim):
    """
    Gera um gráfico de pizza para custos por categoria,
    distinguindo pagamentos à vista e a prazo,
    com tooltip detalhado incluindo valores de Crédito e À Vista.
    Aplica lógica de expansão de parcelas e filtro por data.
    """
    # Expandir as parcelas de cada despesa
    parcelas_expandidas = []
    for _, row in df.iterrows():
        parcelas = expand_installments_v2(row)
        for parcela in parcelas:
            parcela['Categoria'] = row.get('Categoria', None)  # Propaga a categoria original
            parcela['Tipo de Pagamento'] = row.get('Tipo de Pagamento', None)  # Propaga o tipo de pagamento (Crédito ou À Vista)
        parcelas_expandidas.extend(parcelas)

    # Criar DataFrame consolidado das parcelas
    df_expansion = pd.DataFrame(parcelas_expandidas)

    # Garantir que as colunas necessárias existem no DataFrame
    required_columns = ['Mes', 'Tipo de Pagamento', 'Valor', 'Categoria']
    missing_columns = [col for col in required_columns if col not in df_expansion.columns]
    if missing_columns:
        raise ValueError(f"As seguintes colunas estão ausentes no DataFrame expandido: {missing_columns}")

    # Garantir que a coluna 'Mes' esteja no formato datetime
    df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes'], errors='coerce').dt.to_period('M').dt.to_timestamp()

    # Filtrar o DataFrame com base nas datas selecionadas
    df_filtered = df_expansion[
        (df_expansion['Mes'] >= pd.to_datetime(data_inicio)) &
        (df_expansion['Mes'] <= pd.to_datetime(data_fim))
    ]

    # Garantir que não há valores nulos nas colunas essenciais
    df_filtered = df_filtered.dropna(subset=['Categoria', 'Tipo de Pagamento', 'Valor'])

    # Calcular o valor ajustado para cada entrada
    df_filtered["Valor Ajustado"] = df_filtered.apply(
        lambda row: row["Valor"] if row["Tipo de Pagamento"] == "Crédito" else row["Valor"], axis=1
    )

    # Agrupar por Categoria e Tipo de Pagamento
    grouped_df = (
        df_filtered
        .groupby(["Categoria", "Tipo de Pagamento"], as_index=False)["Valor Ajustado"]
        .sum()
    )

    # Calcular os totais por Categoria
    total_df = grouped_df.groupby("Categoria", as_index=False)["Valor Ajustado"].sum()
    total_df = total_df.rename(columns={"Valor Ajustado": "Valor Total"})

    # Adicionar valores de Crédito e À Vista em colunas separadas
    pivot_df = grouped_df.pivot(index="Categoria", columns="Tipo de Pagamento", values="Valor Ajustado").reset_index().fillna(0)

    # Garantir que as colunas "À Vista" e "Crédito" existam, inicializando com 0 se necessário
    if "À Vista" not in pivot_df.columns:
        pivot_df["À Vista"] = 0.0
    if "Crédito" not in pivot_df.columns:
        pivot_df["Crédito"] = 0.0

    # Combinar os dados totais com os valores detalhados
    final_df = total_df.merge(pivot_df, on="Categoria", how="left")
    final_df["Valor Formatado"] = final_df["Valor Total"].apply(format_brl)
    final_df["À Vista Formatado"] = final_df["À Vista"].apply(format_brl)
    final_df["Crédito Formatado"] = final_df["Crédito"].apply(format_brl)
    final_df["Porcentagem"] = (final_df["Valor Total"] / final_df["Valor Total"].sum()) * 100

    # Criar gráfico de pizza
    fig = px.pie(
        final_df,
        names="Categoria",
        values="Valor Total",
        title="Despesas por Categoria (À Vista + Crédito)",
        hole=0.4,  # Gráfico do tipo "donut"
    )

    # Estilizar o gráfico
    fig.update_traces(
        hovertemplate=(
            '<b>Categoria: </b> %{label}<br>'
            '<b>Total: </b>' + final_df["Valor Formatado"] + '<br>'
            '<b>À Vista: </b>' + final_df["À Vista Formatado"] + '<br>'
            '<b>Crédito: </b>' + final_df["Crédito Formatado"] + '<br>'
            '<extra></extra>'
        )
    )

    fig.update_layout(
        legend_title="Categoria de Despesa",
        #title_x=0.1,
    )

    return fig

@st.cache_data
def generate_grouped_bar_chart_by_month_type_v2(df, data_inicio, data_fim):
    """
    Gera um gráfico de barras agrupadas para representar despesas agrupadas por Mês (formato: Out 2024) e Tipo,
    removendo categorias ausentes e ajustando o alinhamento das barras para meses específicos.
    
    Args:
        df (pd.DataFrame): DataFrame contendo as colunas necessárias.
        data_inicio (str): Data inicial no formato 'YYYY-MM-DD'.
        data_fim (str): Data final no formato 'YYYY-MM-DD'.
    
    Returns:
        fig: Objeto Plotly Figure.
    """
    # Expandir parcelas usando expand_installments
    parcelas_expandidas = []
    for _, row in df.iterrows():
        parcelas = expand_installments_v2(row)
        for parcela in parcelas:
            parcela['Tipo'] = row.get('Tipo', None)  # Propagar o tipo de despesa
            parcela['Tipo de Pagamento'] = row.get('Tipo de Pagamento', None)  # Propagar o tipo de pagamento
        parcelas_expandidas.extend(parcelas)

    # Criar DataFrame consolidado das parcelas
    df_expansion = pd.DataFrame(parcelas_expandidas)

    # Garantir que as colunas necessárias existem no DataFrame expandido
    required_columns = ['Mes', 'Tipo', 'Valor', 'Tipo de Pagamento']
    missing_columns = [col for col in required_columns if col not in df_expansion.columns]
    if missing_columns:
        raise ValueError(f"As seguintes colunas estão ausentes no DataFrame expandido: {missing_columns}")

    # Garantir que a coluna 'Mes' esteja no formato datetime
    df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes'], errors='coerce').dt.to_period('M').dt.to_timestamp()

    # Filtrar o DataFrame com base nas datas selecionadas
    df_filtered = df_expansion[
        (df_expansion['Mes'] >= pd.to_datetime(data_inicio)) &
        (df_expansion['Mes'] <= pd.to_datetime(data_fim))
    ]

    # Garantir que não há valores nulos nas colunas essenciais
    df_filtered = df_filtered.dropna(subset=['Tipo', 'Mes', 'Valor'])

    # Calcular o valor ajustado (todos os valores serão somados, independentemente do tipo de pagamento)
    df_filtered["Valor Ajustado"] = df_filtered["Valor"]

    # Adicionar coluna com o formato de mês no padrão brasileiro (Ex.: "Out 2024")
    df_filtered["Mês Formatado"] = df_filtered["Mes"].dt.strftime('%b %Y').str.capitalize()

    # Agrupar os dados por mês formatado e tipo
    grouped_df = (
        df_filtered
        .groupby(["Mês Formatado", "Tipo"], as_index=False)["Valor Ajustado"]
        .sum()
    )

    # Remover as categorias com valor ajustado igual a zero
    grouped_df = grouped_df[grouped_df["Valor Ajustado"] > 0]

    # Garantir que os meses estão ordenados corretamente
    meses_ordenados = (
        pd.to_datetime(grouped_df["Mês Formatado"], format='%b %Y', errors='coerce')
        .drop_duplicates()
        .sort_values()
    )
    categorias_ordenadas = meses_ordenados.dt.strftime('%b %Y').str.capitalize().tolist()

    # Garantir que o DataFrame esteja ordenado pelas colunas corretamente
    grouped_df["Mês Formatado"] = pd.Categorical(
        grouped_df["Mês Formatado"],
        categories=categorias_ordenadas,
        ordered=True
    )
    grouped_df = grouped_df.sort_values("Mês Formatado")

    grouped_df['Valor Formatado'] = grouped_df['Valor Ajustado'].apply(format_brl)


    # Criar o gráfico de barras agrupadas
    fig = px.bar(
        grouped_df,
        x="Mês Formatado",  # Agrupamento por mês no formato "Out 2024"
        y="Valor Ajustado",  # Valores no eixo Y
        color="Tipo",  # Diferencia os tipos por cor
        text_auto=True,  # Exibe os valores diretamente nas barras
        title="Despesas por Tipo e Mês",
        # labels={
        #     "Valor Ajustado": "Valor Total (R$)",
        #     "Mês Formatado": "Mês",
        #     "Tipo": "Tipo de Despesa",
        # }
        custom_data=['Tipo']
    )

            # Estilizar o gráfico
    fig.update_traces(
        hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
                    '<b>Valor:</b> %{y}<br>'
                    '<b>Mês:</b> %{x} <extra></extra>'
                    ),
    )

    # Ajustar o limite do eixo Y para garantir que valores pequenos sejam visíveis
    fig.update_layout(
        xaxis_title='Mês',
        yaxis=dict(
            tickprefix='R$',  # Prefixo para valores no eixo Y
            title='Valor Total (R$)',
            #range=[0, grouped_df['Valor'].max() + 400],  # Ajusta o limite inferior para não cortar as barras pequenas
        ),
        #xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
        # xaxis=dict(
        #     tickmode='array',
        #     tickvals=grouped_df['Mes'],
        #     ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
        # ),
        legend_title="Tipo de Despesa",
        #title_x=0.4,
        bargap=0.15,  # Espaçamento entre grupos de barras
        barmode='group',  # Assegura que a barra seja empilhada corretamente
        xaxis=dict(tickmode='array', tickvals=grouped_df['Mês Formatado'].unique())  # Alinhamento dinâmico dos meses
    )

    # Estilizar o layout para barras agrupadas
    # fig.update_layout(
    #     barmode="group",  # Barras agrupadas lado a lado
    #     xaxis_title="Mês",
    #     yaxis_title="Valor Total (R$)",
    #     legend_title="Tipo de Despesa",
    #     title_x=0.5,
    #     bargap=0.15,  # Espaçamento entre grupos de barras
    #     xaxis=dict(tickmode='array', tickvals=grouped_df['Mês Formatado'].unique())  # Alinhamento dinâmico dos meses
    # )

    return fig

@st.cache_data
def generate_stacked_bar_chart_v3(df, data_inicio, data_fim):
    """
    Gera o gráfico de barras empilhadas com base nas despesas, exibindo as parcelas
    dentro do intervalo de datas informado.
    """
    # Expandir as parcelas de cada despesa
    expanded_installments = []
    for _, row in df.iterrows():
        expanded_installments.extend(expand_installments_v2(row))

    # Criar DataFrame consolidado
    df_expansion = pd.DataFrame(expanded_installments)

    # Garantir que a coluna 'Mes' esteja no formato datetime
    df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes']).dt.to_period('M').dt.to_timestamp()

    # Filtrar o DataFrame com base nas datas selecionadas
    df_expansion_filtered = df_expansion[
        (df_expansion['Mes'] >= pd.to_datetime(data_inicio)) & 
        (df_expansion['Mes'] <= pd.to_datetime(data_fim))
    ]

    # Agrupar por mês e tipo de pagamento
    grouped_df = df_expansion_filtered.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()

    # Formatar valores e datas para exibição
    grouped_df['Mes Formatado'] = grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize()
    grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    # Criar o gráfico de barras empilhadas
    fig = px.bar(
        grouped_df,
        x='Mes',
        y='Valor',
        color='Tipo',
        title='Despesas Totais por Mês (À Vista + Crédito)',
        color_discrete_map={'À Vista': 'blue', 'Crédito': 'orange'},
        text=grouped_df['Valor Formatado'],  # Exibe os valores formatados dentro das barras
        hover_data={'Tipo': True, 'Valor Formatado': True, 'Mes Formatado': True}  # Exibe valores formatados no tooltip
    )

    # Adicionar os totais no topo das barras
    total_df = grouped_df.groupby('Mes')['Valor'].sum().reset_index()
    for _, row in total_df.iterrows():
        total_text = f"Total: {format_brl(row['Valor'])}"
        fig.add_annotation(
            x=row['Mes'],
            y=row['Valor'] + 50,  # Ajustar buffer conforme necessário para que o texto não sobreponha a barra
            text=total_text,
            showarrow=False,
            align="center",
            yanchor="bottom",
        )

    # Estilizar o gráfico
    fig.update_traces(
        hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
                    '<b>Valor:</b> %{customdata[1]}<br>'
                    '<b>Mês:</b> %{customdata[2]} <extra></extra>'
                    ),
        #marker=dict(line=dict(width=0.5, color='white'))
    )

    # Ajustar o limite do eixo Y para garantir que valores pequenos sejam visíveis
    fig.update_layout(
        xaxis_title='Mês',
        yaxis=dict(
            tickprefix='R$',  # Prefixo para valores no eixo Y
            title='Valor Total (R$)',
            #range=[0, grouped_df['Valor'].max() + 1000],  # Ajusta o limite inferior para não cortar as barras pequenas
        ),
        xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
        xaxis=dict(
            tickmode='array',
            tickvals=grouped_df['Mes'],
            ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
        ),
        barmode='stack',  # Assegura que a barra seja empilhada corretamente
        legend_title="Tipo de Pagamento",
        #title_x=0.35,
        bargap=0.15,  # Espaçamento entre grupos de barras
    )

    return fig

@st.cache_data
def generate_grouped_bar_chart_by_day_type(df, data_inicio, data_fim):
    # Garantindo que a coluna 'Data' esteja no formato datetime
    df["Data"] = pd.to_datetime(df["Data"])
    df["Dia"] = df["Data"].dt.strftime("%d/%m/%Y")  # Criar uma coluna para exibição no formato brasileiro

    # Filtrar o DataFrame com base nas datas de início e fim fornecidas
    df_filtered = df[(df["Data"] >= pd.to_datetime(data_inicio)) & 
                    (df["Data"] <= pd.to_datetime(data_fim))]

    # Agrupando os dados por 'Data' e 'Tipo', somando os valores
    grouped_df = df_filtered.groupby(['Data', 'Tipo'], as_index=False)['Valor'].sum()
    grouped_df['Dia'] = grouped_df['Data'].dt.strftime("%d/%m/%Y")  # Adiciona a coluna para exibição
    grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    # Ordenando o DataFrame pelas datas
    grouped_df = grouped_df.sort_values('Data')  # Ordena cronologicamente pelas datas

    # Criando o gráfico de barras agrupadas
    fig = px.bar(
        grouped_df,
        x="Data",  # Usar a coluna 'Data' como base para alinhamento correto
        y="Valor",
        color="Tipo",
        title="Despesas por Tipo e Dia",
        barmode="group",  # Exibe as barras lado a lado
        custom_data=['Tipo'],
    )

    # Estilizar o gráfico
    fig.update_traces(
        hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
                    '<b>Valor:</b> %{y}<br>'
                    '<b>Data:</b> %{x|%d/%m/%Y} <extra></extra>'),
    )

    # Ajustes no layout
    fig.update_layout(
        xaxis=dict(
            title="Dia",
            tickmode="array",  # Exibe apenas as datas relevantes
            tickvals=grouped_df["Data"],  # Apenas datas presentes no agrupamento
            ticktext=grouped_df["Dia"],  # Exibe as datas formatadas no eixo X
        ),
        yaxis=dict(
            tickprefix='R$',  # Prefixo para valores no eixo Y
            title='Valor Total (R$)',
        ),
        legend_title="Tipo de Despesa",
        #title_x=0.4,
        bargap=0.15,  # Espaçamento entre grupos de barras
    )

    return fig

def manager_expense():
    expense_df = get_expense()
    if expense_df.empty:
        st.info('''
                    Nenhuma ***despesa*** cadastrada.\n\n
                    Clique no botão abaixo para ser redirecionado a página de ***Despesas***.
                    ''')
        with st.form(key='dash_expense_form', border=False):
            submit_button = st.form_submit_button(label="Ok", use_container_width=True)
            if submit_button:                        
                st.switch_page("pages/2_Despesas.py")   
            return 

    category_df = get_category()
    if category_df.empty:
        st.info('''
                Nenhuma ***categoria*** cadastrada.\n\n
                Clique no botão abaixo para ser redirecionado a página de ***Categorias***.
                ''')
        with st.form(key='dash_category_form', border=False):
            submit_button = st.form_submit_button(label="Ok", use_container_width=True)
            if submit_button:                        
                st.switch_page("pages/5_Categorias.py")   
            return 

    # Filtra os dados
    df_expense_final = get_filtered_data(expense_df, category_df)

    # Configura os filtros de data
    st.title("Dashboard de Despesas")
    data_inicio = st.date_input("Data Início:", date.today() - timedelta(days=365), format="DD/MM/YYYY")
    data_fim = st.date_input("Data Fim", date.today(), format="DD/MM/YYYY")

    # Filtra despesas por intervalo de datas
    df_filtrado = df_expense_final[
        (df_expense_final['Data'] >= pd.to_datetime(data_inicio)) &
        (df_expense_final['Data'] <= pd.to_datetime(data_fim))
    ].copy()

    # Adiciona coluna para tipo de pagamento (À vista ou Crédito)
    df_filtrado['Tipo de Pagamento'] = df_filtrado['Parcelas'].apply(
        lambda x: 'Crédito' if x > 0 else 'À Vista'
    )

    # Checkbox para filtrar apenas despesas à vista
    if not st.checkbox("Exibir pagamentos a prazo", value=True):
        df_filtrado = df_filtrado[df_filtrado['Tipo de Pagamento'] == 'À Vista']

    # Gera gráficos
    installment_evolution_chart_v2 = chart_installment_evolution_v2(df_filtrado)
    pie_chart_category_v2 = generate_pie_chart_category_v2(df_filtrado, data_inicio, data_fim)
    grouped_bar_chart_by_month_type_v2 = generate_grouped_bar_chart_by_month_type_v2(df_filtrado, data_inicio, data_fim)
    stacked_bar_chart_v3 = generate_stacked_bar_chart_v3(df_filtrado, data_inicio, data_fim)
    grouped_bar_chart_by_day_type = generate_grouped_bar_chart_by_day_type(df_filtrado, data_inicio, data_fim)

    # Exibe os gráficos
    st.plotly_chart(stacked_bar_chart_v3, use_container_width=True)
    st.plotly_chart(grouped_bar_chart_by_month_type_v2, use_container_width=True)
    st.plotly_chart(grouped_bar_chart_by_day_type, use_container_width=True)
    st.plotly_chart(pie_chart_category_v2, use_container_width=True)
    st.plotly_chart(installment_evolution_chart_v2, use_container_width=True)
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.plotly_chart(pie_chart_category_v2, use_container_width=True)
    # with col2:
    #     st.plotly_chart(installment_evolution_chart_v2, use_container_width=True)

def main():
    # Inicializar banco de dados
    try:
        print("Inicializando o banco de dados...")
        DataManager()
        print("Banco de dados configurado com sucesso.")
    except Exception as e:
        print(f"Erro durante a inicialização do banco de dados: {e}")
        return

    if not is_authenticated():
        show_login()
        return  # Impede que o restante da página seja carregado
    
    st.sidebar.button("Sair", on_click=lambda: st.session_state.pop('auth_token', None), use_container_width=True, type="primary")


    # @st.cache_data
    # def get_expense():
    #     # Obtém os dados
    #     expense_controller = ExpenseController()
    #     expense_df = expense_controller.get_expenses()

    #     if not isinstance(expense_df, pd.DataFrame):
    #         # Se não for um DataFrame, cria um DataFrame vazio
    #         expense_df = pd.DataFrame()

    #     return expense_df

    # @st.cache_data
    # def get_category():
    #     category_controller = CategoryController()
    #     category_df = category_controller.get_categories()

    #     if not isinstance(category_df, pd.DataFrame):
    #         # Se não for um DataFrame, cria um DataFrame vazio
    #         category_df = pd.DataFrame()

    #     return category_df

    # @st.cache_data
    # def get_filtered_data(expense_df, category_df):
    #     """
    #     Filtra e formata o DataFrame consolidado entre despesas e categorias.
    #     """
    #     # Combina despesas com categorias
    #     merged_df = pd.merge(
    #         expense_df, 
    #         category_df, 
    #         left_on='type_category_id', 
    #         right_on='cat_id', 
    #         how='left', 
    #         suffixes=('', '_category')
    #     )

    #     # Seleciona e renomeia colunas
    #     merged_df = merged_df[[
    #         'exp_date', 'exp_value', 'exp_description', 'exp_number_of_installments', 
    #         'exp_final_date_of_installment', 'exp_value_total_installment', 
    #         'cat_name', 'type_name', 'pay_name'
    #     ]].rename(columns={
    #         'exp_date': 'Data', 
    #         'exp_value': 'Valor', 
    #         'exp_description': 'Descrição Despesa',
    #         'exp_number_of_installments': 'Parcelas',
    #         'exp_final_date_of_installment': 'Última parcela',
    #         'exp_value_total_installment': 'Valor total das parcelas',
    #         'cat_name': 'Categoria', 
    #         'type_name': 'Tipo',
    #         'pay_name': 'Pagamento'
    #     })

    #     # Converte colunas de data
    #     merged_df['Data'] = pd.to_datetime(merged_df['Data'])
    #     merged_df['Última parcela'] = pd.to_datetime(merged_df['Última parcela'])

    #     return merged_df


    # def grafico_teste(df_filtrado):
    #     # Adicionando coluna de mês ao DataFrame filtrado com formato de string para o eixo X
    #     df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M').astype(str)

    #     # Criando uma nova coluna para identificar as despesas com cartão de crédito, considerando as parcelas
    #     df_filtrado['Despesas_Cartao_Credito'] = 0
    #     df_filtrado.loc[df_filtrado['Pagamento'] == 'Cartão de Crédito', 'Despesas_Cartao_Credito'] = df_filtrado['Valor'] * df_filtrado['Parcelas']


    #     # Agrupando por 'Mes' e somando os valores
    #     despesas_mensal = df_filtrado.groupby('Mes').agg(
    #         Despesas_Cartao_Credito=('Despesas_Cartao_Credito', 'sum'),
    #         Despesas_Outras=('Valor', 'sum')
    #     ).reset_index()

    #     # Convertendo a coluna 'Mes' de volta para datetime para uma visualização correta no gráfico
    #     despesas_mensal['Mes'] = pd.to_datetime(despesas_mensal['Mes'], format='%Y-%m')

    #     # Gerando o gráfico de barras empilhadas
    #     fig_despesas_mensal = px.bar(despesas_mensal, 
    #                                 x='Mes', 
    #                                 y=['Despesas_Cartao_Credito', 'Despesas_Outras'], 
    #                                 title='Distribuição Mensal das Despesas (Cartão de Crédito vs Outras Despesas)',
    #                                 labels={'Despesas_Cartao_Credito': 'Despesas com Cartão de Crédito', 'Despesas_Outras': 'Outras Despesas'},
    #                                 color_discrete_sequence=['#FFA07A', '#98C9E4'])

    #     # Adicionando os valores totais no topo das barras empilhadas
    #     for i, row in despesas_mensal.iterrows():
    #         total = row['Despesas_Cartao_Credito'] + row['Despesas_Outras']
    #         fig_despesas_mensal.add_annotation(
    #             x=row['Mes'],
    #             y=total,
    #             text=f'{total:.2f}',  # Exibindo o total com 2 casas decimais
    #             showarrow=False,
    #             font=dict(size=12, color="white"),
    #             align="center",
    #             yanchor="bottom"  # Alinhamento vertical correto
    #         )

    #     # Formatando o eixo X para exibir apenas o mês e o ano uma vez (exemplo: "Nov 2024")
    #     fig_despesas_mensal.update_xaxes(
    #         tickformat="%b %Y",  # Formato de exibição do mês e ano
    #         dtick="M1"           # Configura a exibição para cada mês (sem duplicações)
    #     )

    #     # Exibindo o gráfico
    #     st.plotly_chart(fig_despesas_mensal, use_container_width=True, key='teste')

    # def payment_type_chart(df):

    #     # Convert 'Date' column to datetime
    #     df['Data'] = pd.to_datetime(df['Data'])
        
    #     # Sidebar for time range selection
    #     st.sidebar.header("Filtros de tempo")
    #     start_date = st.sidebar.date_input("Data Início", df['Data'].min())
    #     end_date = st.sidebar.date_input("Data Fim", df['Data'].max())
        
    #     # Filter dataframe by selected time range
    #     filtered_df = df[(df['Data'] >= pd.to_datetime(start_date)) & (df['Data'] <= pd.to_datetime(end_date))]

    #     # Checkbox to show or hide credit payments
    #     show_credit = st.checkbox("Pagamentos a prazo", value=True)
        
    #     # Add a column to differentiate between cash and credit
    #     filtered_df['Tipo de Pagamento'] = filtered_df['Parcelas'].apply(lambda x: 'Crédito' if x > 0 else 'À Vista')
        
    #     if not show_credit:
    #         filtered_df = filtered_df[filtered_df['Tipo de Pagamento'] == 'À Vista']

    #     # Group data by payment type and date
    #     grouped_df = filtered_df.groupby(['Tipo de Pagamento', 'Data']).sum(numeric_only=True).reset_index()

    #     # Create stacked bar chart
    #     fig = px.bar(
    #         grouped_df,
    #         x='Data',
    #         y='Valor',
    #         color='Tipo de Pagamento',
    #         title='Despesas por Tipo de Pagamento',
    #         labels={'Valor': 'Valor (BRL)', 'Data': 'Mês'},
    #         barmode='stack'
    #     )
        
        
    #     # Update X-axis to show months
    #     fig.update_xaxes(tickformat="%b %Y")
        
    #     # Update layout to format values in Brazilian style
    #     fig.update_yaxes(tickprefix="R$", tickformat=",.")

    #     # Formatando o eixo X para exibir apenas o mês e o ano uma vez (exemplo: "Nov 2024")
    #     fig.update_xaxes(
    #         tickformat="%b %Y",  # Formato de exibição do mês e ano
    #         dtick="M1"           # Configura a exibição para cada mês (sem duplicações)
    #     )
        
    #     # Display chart
    #     st.plotly_chart(fig, use_container_width=True)



    # @st.cache_data
    # def generate_stacked_bar_chart(df):
    #     """
    #     Gera um gráfico de barras empilhadas com valores totais no topo,
    #     utilizando a coluna 'Última parcela' e assumindo que 'Valor' já é o valor da parcela.
    #     """
    #     # # Expandir as parcelas usando 'Última parcela'
    #     # parcelas_expandidas = []
    #     # for _, row in df.iterrows():
    #     #     if row['Parcelas'] > 0:
    #     #         data_inicial = row['Data']
    #     #         data_final = row['Última parcela']

    #     #         # Gerar todas as parcelas com base em 'Data' e 'Última parcela'
    #     #         parcelas = pd.date_range(start=data_inicial, end=data_final, freq='MS')  # Frequência mensal
    #     #         for parcela_data in parcelas:
    #     #             parcelas_expandidas.append({'Mes': parcela_data, 'Tipo': 'Crédito', 'Valor': row['Valor']})
    #     #     else:
    #     #         # Adicionar despesas à vista (sem expansão)
    #     #         parcelas_expandidas.append({'Mes': row['Data'], 'Tipo': 'À Vista', 'Valor': row['Valor']})
    #     # Expande as parcelas usando a função `expand_parcelas`
    #     expanded_installments = []
    #     for _, row in df.iterrows():
    #         expanded_installments.extend(expand_installments(row))
    #     # Criar DataFrame consolidado
    #     df_expansion = pd.DataFrame(expanded_installments)
    #     # Garantir que a coluna 'Mes' esteja no formato datetime
    #     df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes']).dt.to_period('M').dt.to_timestamp()

    #     # Agrupar por mês e tipo de pagamento
    #     grouped_df = df_expansion.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()

    #     # Criar coluna formatada para valores no tooltip e na barra
    #     # grouped_df["Mes"] = pd.to_datetime(grouped_df["Mes"], format="%Y-%m")
    #     # grouped_df["Mes Formatado"] = grouped_df["Mes"].dt.strftime("%b %Y")  # Coluna formatada
    #     # grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(
    #     #     lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #     # )
        
    #     # Formatar valores e datas para exibição
    #     grouped_df['Mes Formatado'] = grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize()
    #     grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    #     # Criar o gráfico de barras empilhadas
    #     fig = px.bar(
    #         grouped_df,
    #         x='Mes',
    #         y='Valor',
    #         color='Tipo',
    #         title='Despesas Totais por Mês (À Vista + Crédito)',
    #         color_discrete_map={'À Vista': 'blue', 'Crédito': 'orange'},
    #         text=grouped_df['Valor Formatado'],  # Exibe os valores formatados dentro das barras
    #         hover_data={'Tipo': True, 'Valor Formatado': True, 'Mes Formatado': True}  # Exibe valores formatados no tooltip
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
    #                     '<b>Valor:</b> %{customdata[1]}<br>'
    #                     '<b>Mês:</b> %{customdata[2]} <extra></extra>'
    #                     )
    #     )

    #     # Calcular a altura máxima para posicionar os totais
    #     total_df = grouped_df.groupby('Mes')['Valor'].sum().reset_index()
    #     for _, row in total_df.iterrows():
    #         #total_text = f"Total: R${row['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #         total_text = f"Total: {format_brl(row['Valor'])}"
    #         fig.add_annotation(
    #             x=row['Mes'],
    #             y=row['Valor'] + 50,  # Ajustar buffer conforme necessário
    #             text=total_text,
    #             showarrow=False,
    #             align="center",
    #             yanchor="bottom",
    #         )

    #     # Personalizar layout
    #     fig.update_layout(
    #         xaxis_title='Mês',
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo para valores no eixo Y
    #             title='Valor (R$)',
    #         ),
    #         xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         xaxis=dict(
    #             tickmode='array',
    #             tickvals=grouped_df['Mes'],
    #             ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
    #         ),
    #     )

    #     return fig

    # @st.cache_data
    # def chart_installment_evolution(df_filtrado):
    #     """
    #     Gera um gráfico de linha mostrando a evolução das parcelas por mês,
    #     formatando os valores monetários e a data no padrão brasileiro.
    #     """

    #     #Garantir que 'Parcelas' seja numérico
    #     df_filtrado['Parcelas'] = pd.to_numeric(df_filtrado['Parcelas'], errors='coerce').fillna(0).astype(int)
    #     df_credito = df_filtrado[df_filtrado['Parcelas'] > 0]

    #     #Expandir as parcelas usando a lógica baseada nas colunas existentes
    #     parcelas_expandidas = []
    #     for _, row in df_credito.iterrows():
    #         data_inicial = row['Data']
    #         data_final = row['Última parcela']  # Usa a última parcela para determinar o período
    #         parcelas = pd.date_range(start=data_inicial, end=data_final, freq='MS')  # Gera parcelas mensais
            
    #         for parcela_data in parcelas:
    #             parcelas_expandidas.append({'Data Parcela': parcela_data, 'Valor Parcela': row['Valor']})

    #     # Verificar se existem parcelas
    #     if not parcelas_expandidas:
    #         # Se não houver parcelas, criar um gráfico vazio
    #         fig = px.line(
    #             title='Evolução das Parcelas por Mês',
    #             labels={'Data Parcela': 'Mês do Parcelamento', 'Valor Parcela': 'Montante de Parcelas'}
    #         )
    #         fig.add_annotation(
    #             x=0.5, y=0.5, text="Nenhuma despesa parcelada encontrada.",
    #             showarrow=False, font=dict(size=16, color="red"), align="center"
    #         )
    #         return fig

    #     # Criar o DataFrame consolidado das parcelas
    #     df_parcelas = pd.DataFrame(parcelas_expandidas)

    #     # Agrupar os valores por mês
    #     montante_mensal = (
    #         df_parcelas.groupby(df_parcelas['Data Parcela'].dt.to_period("M"))['Valor Parcela'].sum().reset_index()
    #     )
    #     montante_mensal['Data Parcela'] = montante_mensal['Data Parcela'].dt.to_timestamp()

    #     # Adicionar coluna formatada para os tooltips
    #     montante_mensal['Valor Formatado'] = montante_mensal['Valor Parcela'].apply(format_brl
    #         #lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #     )
    #     montante_mensal['Data Formatada'] = montante_mensal['Data Parcela'].dt.strftime('%b de %Y').str.capitalize()

    #     # Gerar o gráfico de linha
    #     fig = px.line(
    #         montante_mensal,
    #         x='Data Parcela',
    #         y='Valor Parcela',
    #         title='Evolução das Parcelas por Mês',
    #         labels={
    #             'Data Parcela': 'Mês do Parcelamento',
    #             'Valor Parcela': 'Montante de Parcelas (R$)'
    #         },
    #         hover_data={'Valor Parcela': False, 'Valor Formatado': True, 'Data Formatada': True}  # Exibe valores formatados no tooltip
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         mode="lines+markers",
    #         line=dict(width=2),
    #         hovertemplate='<b>Mês:</b> %{customdata[1]}<br><b>Montante:</b> %{customdata[0]}<extra></extra>'
    #     )
    #     fig.update_layout(
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo no eixo Y
    #             title='Montante de Parcelas (R$)'
    #         ),
    #         xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         xaxis=dict(
    #             tickmode='array',
    #             tickvals=montante_mensal['Data Parcela'],
    #             ticktext=montante_mensal['Data Parcela'].dt.strftime('%b %Y').str.capitalize()
    #         )
    #     )

    #     return fig
    
    # @st.cache_data
    # def chart_installment_evolution_v2(df_filtrado):
    #     """
    #     Gera um gráfico de linha mostrando a evolução das parcelas por mês,
    #     considerando todas as parcelas a partir da data de registro
    #     até a última parcela, sem aplicar filtros de data.
    #     """

    #     # Garantir que 'Parcelas' seja numérico
    #     df_filtrado['Parcelas'] = pd.to_numeric(df_filtrado['Parcelas'], errors='coerce').fillna(0).astype(int)
    #     df_credito = df_filtrado[df_filtrado['Parcelas'] > 0]

    #     # Expandir as parcelas usando a função expand_installments
    #     parcelas_expandidas = []
    #     for _, row in df_credito.iterrows():
    #         parcelas_expandidas.extend(expand_installments_v2(row))

    #     # Criar DataFrame consolidado das parcelas
    #     if not parcelas_expandidas:
    #         # Se não houver parcelas, criar um gráfico vazio
    #         fig = px.line(
    #             title='Evolução das Parcelas por Mês - V2',
    #             labels={'Mes': 'Mês do Parcelamento', 'Valor': 'Montante de Parcelas'}
    #         )
    #         fig.add_annotation(
    #             x=0.5, y=0.5, text="Nenhuma despesa parcelada encontrada.",
    #             showarrow=False, font=dict(size=16, color="red"), align="center"
    #         )
    #         return fig

    #     df_parcelas = pd.DataFrame(parcelas_expandidas)

    #     # Agrupar os valores por mês
    #     montante_mensal = (
    #         df_parcelas.groupby(df_parcelas['Mes'].dt.to_period("M"))['Valor'].sum().reset_index()
    #     )
    #     montante_mensal['Mes'] = montante_mensal['Mes'].dt.to_timestamp()

    #     # Adicionar colunas formatadas para os tooltips
    #     montante_mensal['Valor Formatado'] = montante_mensal['Valor'].apply(format_brl)
    #     montante_mensal['Data Formatada'] = montante_mensal['Mes'].dt.strftime('%b de %Y').str.capitalize()

    #     # Gerar o gráfico de linha
    #     fig = px.line(
    #         montante_mensal,
    #         x='Mes',
    #         y='Valor',
    #         title='Evolução das Parcelas por Mês',
    #         labels={
    #             'Mes': 'Mês do Parcelamento',
    #             'Valor': 'Montante de Parcelas (R$)'
    #         },
    #         hover_data={'Valor': False, 'Valor Formatado': True, 'Data Formatada': True}  # Exibe valores formatados no tooltip
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         mode="lines+markers",
    #         line=dict(width=2),
    #         hovertemplate='<b>Mês:</b> %{customdata[1]}<br><b>Montante:</b> %{customdata[0]}<extra></extra>'
    #     )
    #     fig.update_layout(
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo no eixo Y
    #             title='Montante de Parcelas (R$)'
    #         ),
    #         xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         xaxis=dict(
    #             tickmode='array',
    #             tickvals=montante_mensal['Mes'],
    #             ticktext=montante_mensal['Mes'].dt.strftime('%b %Y').str.capitalize()
    #         )
    #     )

    #     return fig

    
# #Comparação entre Despesas Fixas, Variáveis,supérfulas ...
#     @st.cache_data
#     def generate_stacked_bar_chart_category(df):
#         """
#         Gera um gráfico de barras empilhadas para custos distintos por categoria, 
#         distinguindo pagamentos à vista e a prazo.
#         """
#         # Criar coluna "Tipo de Custo" para distinguir entre À Vista e A Prazo
#         #df["Tipo de Custo"] = df["Parcelas"].apply(lambda x: "À Vista" if x == 0 else "Crédito")

#         # Ajustar o valor baseado no tipo de custo
#         df["Valor Ajustado"] = df.apply(
#             lambda row: row["Valor total das parcelas"] if row["Tipo de Pagamento"] == "Crédito" else row["Valor"], 
#             axis=1
#         )

#         # Agrupar por Categoria e Tipo de Custo
#         grouped_df = df.groupby(["Categoria", "Tipo de Pagamento"])["Valor Ajustado"].sum().reset_index()

#         # Calcular os totais por Categoria para exibir no topo das barras
#         total_df = grouped_df.groupby("Categoria")["Valor Ajustado"].sum().reset_index()
# #formatar o valor ajustado.apply(format_brl)

#         # grouped_df["Valor Formatado"] = df["Valor Ajustado"].apply(format_brl)
#         # print( grouped_df["Valor Formatado"])
#         grouped_df['Valor Formatado'] = grouped_df['Valor Ajustado'].apply(format_brl)

#         # Criar gráfico de barras empilhadas
#         fig = px.bar(
#             grouped_df,
#             x="Categoria",
#             y="Valor Ajustado",
#             color="Tipo de Pagamento",
#             text=grouped_df["Valor Ajustado"].apply(format_brl),
#             title="Despesas por Categoria (À Vista + Crédito)",
#             # labels={
#             #     "Categoria": "Categoria",
#             #     "Valor Ajustado": "Valor Total (R$)",
#             #     "Tipo de Pagamento": "Tipo de Pagamento"
#             # },
#             color_discrete_map={"À Vista": "blue", "Crédito": "orange"},  # Definir cores personalizadas
#             custom_data=['Tipo de Pagamento', 'Valor Formatado']
#         )

#         # Estilizar o gráfico
#         fig.update_traces(
#             hovertemplate=(
#                         '<b>Categoria:</b> %{x}<br>'
#                         '<b>Tipo:</b> %{customdata[0]}<br>'
#                         '<b>Valor:</b> %{customdata[1]}<br>'
#                         '<extra></extra>'
#                         )
#         )

       
#         # fig.update_traces(
#         #     hovertemplate="<b>Categoria:</b> %{x}<br>"
#         #                 "<b>Tipo:</b> %{customdata[0]}<br>"
#         #                 "<b>Valor:</b> R$%{customdata[1]:,.2f}<extra></extra>",
#         #     customdata=grouped_df[["Tipo de Pagamento", "Valor Ajustado"]].values,  # Passar dados corretos para o tooltip
#         # )

#         # Adicionar anotações no topo das barras (valor total por categoria)
#         for _, row in total_df.iterrows():
#             total_text = f"Total: {format_brl(row['Valor Ajustado'])}"
#             fig.add_annotation(
#                 x=row["Categoria"],
#                 y=row["Valor Ajustado"] + 50,  # Ajustar espaço acima das barras
#                 text=total_text,
#                 showarrow=False,
#                 align="center",
#                 yanchor="bottom",
#             )


#         # # Ajustar layout do gráfico
#         # fig.update_layout(
#         #     # xaxis_title="Categoria",
#         #     # yaxis_title="Valor Total (R$)",
#         #     # yaxis_tickprefix="R$",
#         #     # legend_title="Tipo de Pagamento",
#         #     barmode="stack",  # Define o modo de barras empilhadas
#         # )

#                 # Personalizar layout
#         fig.update_layout(
#             # xaxis_title='Categoria',
#             # yaxis=dict(
#             #     tickprefix='R$',  # Prefixo para valores no eixo Y
#             #     title='Valor Total (R$)',
#             # ),
#             xaxis=dict(
#                 tickmode='array',
#                 tickvals=grouped_df['Categoria'],
#                 # ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
#             ),
#             barmode="stack",
#         )

#         return fig
   


    # @st.cache_data
    # def generate_stacked_bar_chart_with_month(df):
    #     """
    #     Gera um gráfico de barras empilhadas agrupando por mês e categoria,
    #     distinguindo pagamentos à vista e a prazo.
    #     """
    #     # Transformar as colunas de data no formato datetime
    #     df["Data"] = pd.to_datetime(df["Data"])
    #     df["Última parcela"] = pd.to_datetime(df["Última parcela"])

    #     # Criar coluna para o mês da despesa
    #     df["Mês"] = df["Data"].dt.to_period("M").dt.to_timestamp()

    #     # Definir tipo de pagamento: À Vista ou A Prazo
    #     df["Tipo de Custo"] = df["Parcelas"].apply(lambda x: "À Vista" if x == 0 else "A Prazo")

    #     # Expansão das parcelas (para considerar todos os meses até a última parcela)
    #     parcelas_expandidas = []
    #     for _, row in df.iterrows():
    #         if row["Parcelas"] > 0:
    #             # Criar todas as parcelas a partir da data inicial até a última parcela
    #             parcelas = pd.date_range(start=row["Data"], end=row["Última parcela"], freq="MS")
    #             for parcela_data in parcelas:
    #                 parcelas_expandidas.append({
    #                     "Mês": parcela_data,
    #                     "Categoria": row["Categoria"],
    #                     "Tipo de Custo": "A Prazo",
    #                     "Valor": row["Valor"]
    #                 })
    #         else:
    #             # Adicionar valores à vista (sem expansão)
    #             parcelas_expandidas.append({
    #                 "Mês": row["Mês"],
    #                 "Categoria": row["Categoria"],
    #                 "Tipo de Custo": "À Vista",
    #                 "Valor": row["Valor"]
    #             })

    #     # Criar um novo DataFrame consolidado
    #     df_expansao = pd.DataFrame(parcelas_expandidas)

    #     # Agrupar por Mês, Categoria e Tipo de Custo
    #     grouped_df = (
    #         df_expansao.groupby(["Mês", "Categoria", "Tipo de Custo"])["Valor"]
    #         .sum()
    #         .reset_index()
    #     )

    #     # Criar gráfico de barras empilhadas com Mês e Categoria no eixo X
    #     fig = px.bar(
    #         grouped_df,
    #         x="Mês",
    #         y="Valor",
    #         color="Tipo de Custo",
    #         facet_col="Categoria",
    #         text=grouped_df["Valor"].apply(
    #             lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #         ),
    #         title="Custos por Mês e Categoria (À Vista e A Prazo)",
    #         labels={
    #             "Mês": "Mês",
    #             "Valor": "Valor (R$)",
    #             "Tipo de Custo": "Tipo de Custo"
    #         },
    #         color_discrete_map={"À Vista": "blue", "A Prazo": "orange"},
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(textposition="inside", textfont_size=12)
    #     fig.update_layout(
    #         xaxis_title="Mês",
    #         yaxis_title="Valor Total (R$)",
    #         yaxis_tickprefix="R$",  # Prefixo para valores no eixo Y
    #         legend_title="Tipo de Custo",
    #         barmode="stack",  # Define o modo de barras empilhadas
    #     )

    #     return fig

 
    # @st.cache_data
    # def generate_pie_chart_category(df):
    #     """
    #     Gera um gráfico de pizza para custos por categoria,
    #     distinguindo pagamentos à vista e a prazo,
    #     com tooltip detalhado incluindo valores de Crédito e À Vista.
    #     """

    #     # Calcular o valor ajustado para cada entrada
    #     df["Valor Ajustado"] = df.apply(
    #         lambda row: row["Valor total das parcelas"] if row["Tipo de Pagamento"] == "Crédito" else row["Valor"], 
    #         axis=1
    #     )

    #     # Agrupar por Categoria e Tipo de Pagamento
    #     grouped_df = df.groupby(["Categoria", "Tipo de Pagamento"])["Valor Ajustado"].sum().reset_index()
    #     # Calcular os totais por Categoria
    #     total_df = grouped_df.groupby("Categoria")["Valor Ajustado"].sum().reset_index()
    #     total_df = total_df.rename(columns={"Valor Ajustado": "Valor Total"})

    #     # # Adicionar valores de Crédito e À Vista em colunas separadas
    #     pivot_df = grouped_df.pivot(index="Categoria", columns="Tipo de Pagamento", values="Valor Ajustado").reset_index().fillna(0)

    #     # Garantir que as colunas "À Vista" e "Crédito" existam, inicializando com 0 se necessário
    #     if "À Vista" not in pivot_df.columns:
    #         pivot_df["À Vista"] = 0.0
    #     if "Crédito" not in pivot_df.columns:
    #         pivot_df["Crédito"] = 0.0

    #     # Combinar os dados totais com os valores detalhados
    #     final_df = total_df.merge(pivot_df, on="Categoria")
    #     final_df["Valor Formatado"] = final_df["Valor Total"].apply(format_brl)
    #     final_df['À Vista Formatado'] = final_df['À Vista'].apply(lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    #     final_df["Crédito Formatado"] = final_df["Crédito"].apply(format_brl)
    #     final_df["Porcentagem"] = final_df["Valor Total"] / final_df["Valor Total"].sum() * 100

    #     # Criar gráfico de pizza
    #     fig = px.pie(
    #         final_df,
    #         names="Categoria",
    #         values="Valor Total",
    #         title="Despesas por Categoria (À Vista + Crédito)",
    #         hole=0.4,  # Gráfico do tipo "donut"
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=(
    #             '<b>Categoria: </b> %{label}<br>'
    #             '<b>Total: </b>' + final_df["Valor Formatado"] + '<br>'
    #             '<b>À Vista: </b>' + final_df["À Vista Formatado"] + '<br>'
    #             '<b>Crédito: </b>' + final_df["Crédito Formatado"] + '<br>'
    #             '<extra></extra>'
    #         )
    #     )

    #     return fig

    # @st.cache_data
    # def generate_pie_chart_category_v2(df, data_inicio, data_fim):
    #     """
    #     Gera um gráfico de pizza para custos por categoria,
    #     distinguindo pagamentos à vista e a prazo,
    #     com tooltip detalhado incluindo valores de Crédito e À Vista.
    #     Aplica lógica de expansão de parcelas e filtro por data.
    #     """
    #     # Expandir as parcelas de cada despesa
    #     parcelas_expandidas = []
    #     for _, row in df.iterrows():
    #         parcelas = expand_installments_v2(row)
    #         for parcela in parcelas:
    #             parcela['Categoria'] = row.get('Categoria', None)  # Propaga a categoria original
    #             parcela['Tipo de Pagamento'] = row.get('Tipo de Pagamento', None)  # Propaga o tipo de pagamento (Crédito ou À Vista)
    #         parcelas_expandidas.extend(parcelas)

    #     # Criar DataFrame consolidado das parcelas
    #     df_expansion = pd.DataFrame(parcelas_expandidas)

    #     # Garantir que as colunas necessárias existem no DataFrame
    #     required_columns = ['Mes', 'Tipo de Pagamento', 'Valor', 'Categoria']
    #     missing_columns = [col for col in required_columns if col not in df_expansion.columns]
    #     if missing_columns:
    #         raise ValueError(f"As seguintes colunas estão ausentes no DataFrame expandido: {missing_columns}")

    #     # Garantir que a coluna 'Mes' esteja no formato datetime
    #     df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes'], errors='coerce').dt.to_period('M').dt.to_timestamp()

    #     # Filtrar o DataFrame com base nas datas selecionadas
    #     df_filtered = df_expansion[
    #         (df_expansion['Mes'] >= pd.to_datetime(data_inicio)) &
    #         (df_expansion['Mes'] <= pd.to_datetime(data_fim))
    #     ]

    #     # Garantir que não há valores nulos nas colunas essenciais
    #     df_filtered = df_filtered.dropna(subset=['Categoria', 'Tipo de Pagamento', 'Valor'])

    #     # Calcular o valor ajustado para cada entrada
    #     df_filtered["Valor Ajustado"] = df_filtered.apply(
    #         lambda row: row["Valor"] if row["Tipo de Pagamento"] == "Crédito" else row["Valor"], axis=1
    #     )

    #     # Agrupar por Categoria e Tipo de Pagamento
    #     grouped_df = (
    #         df_filtered
    #         .groupby(["Categoria", "Tipo de Pagamento"], as_index=False)["Valor Ajustado"]
    #         .sum()
    #     )

    #     # Calcular os totais por Categoria
    #     total_df = grouped_df.groupby("Categoria", as_index=False)["Valor Ajustado"].sum()
    #     total_df = total_df.rename(columns={"Valor Ajustado": "Valor Total"})

    #     # Adicionar valores de Crédito e À Vista em colunas separadas
    #     pivot_df = grouped_df.pivot(index="Categoria", columns="Tipo de Pagamento", values="Valor Ajustado").reset_index().fillna(0)

    #     # Garantir que as colunas "À Vista" e "Crédito" existam, inicializando com 0 se necessário
    #     if "À Vista" not in pivot_df.columns:
    #         pivot_df["À Vista"] = 0.0
    #     if "Crédito" not in pivot_df.columns:
    #         pivot_df["Crédito"] = 0.0

    #     # Combinar os dados totais com os valores detalhados
    #     final_df = total_df.merge(pivot_df, on="Categoria", how="left")
    #     final_df["Valor Formatado"] = final_df["Valor Total"].apply(format_brl)
    #     final_df["À Vista Formatado"] = final_df["À Vista"].apply(format_brl)
    #     final_df["Crédito Formatado"] = final_df["Crédito"].apply(format_brl)
    #     final_df["Porcentagem"] = (final_df["Valor Total"] / final_df["Valor Total"].sum()) * 100

    #     # Criar gráfico de pizza
    #     fig = px.pie(
    #         final_df,
    #         names="Categoria",
    #         values="Valor Total",
    #         title="Despesas por Categoria (À Vista + Crédito)",
    #         hole=0.4,  # Gráfico do tipo "donut"
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=(
    #             '<b>Categoria: </b> %{label}<br>'
    #             '<b>Total: </b>' + final_df["Valor Formatado"] + '<br>'
    #             '<b>À Vista: </b>' + final_df["À Vista Formatado"] + '<br>'
    #             '<b>Crédito: </b>' + final_df["Crédito Formatado"] + '<br>'
    #             '<extra></extra>'
    #         )
    #     )

    #     fig.update_layout(
    #         legend_title="Categoria de Despesa",
    #     )

    #     return fig


    # @st.cache_data
    # def generate_stacked_bar_chart_type(df):
    #     """
    #     Gera um gráfico de barras empilhadas para representar despesas agrupadas por Dia e Tipo.
        
    #     Args:
    #         df (pd.DataFrame): DataFrame contendo as colunas necessárias.
        
    #     Returns:
    #         fig: Objeto Plotly Figure.
    #     """
    #     # Converter a coluna 'Data' para datetime e criar a coluna 'Dia'
    #     df["Data"] = pd.to_datetime(df["Data"])
    #     df["Dia"] = df["Data"].dt.strftime("%d/%m/%Y")
        
    #     # Calcular o valor ajustado (considerando parcelas ou valor direto)
    #     df["Valor Ajustado"] = df.apply(
    #         lambda row: row["Valor total das parcelas"] if row["Tipo de Pagamento"] == "Crédito" else row["Valor"], 
    #         axis=1
    #     )
        
    #     # Agrupar os dados por dia e tipo
    #     grouped_df = df.groupby(["Dia", "Tipo"])["Valor Ajustado"].sum().reset_index()
        
    #     # Criar o gráfico de barras empilhadas
    #     fig = px.bar(
    #         grouped_df,
    #         x="Dia",  # Agrupamento por dia
    #         y="Valor Ajustado",  # Valores no eixo Y
    #         color="Tipo",  # Diferencia os tipos por cor
    #         text_auto=True,  # Exibe os valores diretamente nas barras
    #         title="Despesas por Tipo e Dia",
    #         labels={
    #             "Valor Ajustado": "Valor Total (R$)",
    #             "Dia": "Dia",
    #             "Tipo": "Tipo de Despesa",
    #         }
    #     )
        
    #     # Estilizar o layout
    #     fig.update_layout(
    #         barmode="group",  # Empilhar as barras
    #         xaxis_title="Dia",
    #         yaxis_title="Valor Total (R$)",
    #         legend_title="Tipo de Despesa",
    #         title_x=0.5,
    #         bargap=0.15,  # Espaçamento entre grupos de barras
    #     )
        
    #     return fig


    # @st.cache_data
    # def generate_grouped_bar_chart_by_month_type(df):
    #     """
    #     Gera um gráfico de barras agrupadas para representar despesas agrupadas por Mês e Tipo.
        
    #     Args:
    #         df (pd.DataFrame): DataFrame contendo as colunas necessárias.
        
    #     Returns:
    #         fig: Objeto Plotly Figure.
    #     """
    #     # Converter a coluna 'Data' para datetime e criar a coluna 'Mês'
    #     df["Data"] = pd.to_datetime(df["Data"])
    #     df["Mês"] = df["Data"].dt.strftime("%Y-%m")  # Formato YYYY-MM para agrupamento por mês
        
    #     # Calcular o valor ajustado (considerando parcelas ou valor direto)
    #     df["Valor Ajustado"] = df.apply(
    #         lambda row: row["Valor total das parcelas"] if row["Tipo de Pagamento"] == "Crédito" else row["Valor"], 
    #         axis=1
    #     )
        
    #     # Agrupar os dados por mês e tipo
    #     grouped_df = df.groupby(["Mês", "Tipo"])["Valor Ajustado"].sum().reset_index()
        
    #     # Criar o gráfico de barras agrupadas
    #     fig = px.bar(
    #         grouped_df,
    #         x="Mês",  # Agrupamento por mês
    #         y="Valor Ajustado",  # Valores no eixo Y
    #         color="Tipo",  # Diferencia os tipos por cor
    #         text_auto=True,  # Exibe os valores diretamente nas barras
    #         title="Despesas por Tipo e Mês",
    #         labels={
    #             "Valor Ajustado": "Valor Total (R$)",
    #             "Mês": "Mês",
    #             "Tipo": "Tipo de Despesa",
    #         }
    #     )
        
    #     # Estilizar o layout para barras agrupadas
    #     fig.update_layout(
    #         barmode="group",  # Barras agrupadas lado a lado
    #         xaxis_title="Mês",
    #         yaxis_title="Valor Total (R$)",
    #         legend_title="Tipo de Despesa",
    #         title_x=0.5,
    #         bargap=0.15,  # Espaçamento entre grupos de barras
    #     )
        
    #     return fig
    
    # @st.cache_data
    # def generate_grouped_bar_chart_by_month_type_v2(df, data_inicio, data_fim):
    #     """
    #     Gera um gráfico de barras agrupadas para representar despesas agrupadas por Mês (formato: Out 2024) e Tipo,
    #     removendo categorias ausentes e ajustando o alinhamento das barras para meses específicos.
        
    #     Args:
    #         df (pd.DataFrame): DataFrame contendo as colunas necessárias.
    #         data_inicio (str): Data inicial no formato 'YYYY-MM-DD'.
    #         data_fim (str): Data final no formato 'YYYY-MM-DD'.
        
    #     Returns:
    #         fig: Objeto Plotly Figure.
    #     """
    #     # Expandir parcelas usando expand_installments
    #     parcelas_expandidas = []
    #     for _, row in df.iterrows():
    #         parcelas = expand_installments_v2(row)
    #         for parcela in parcelas:
    #             parcela['Tipo'] = row.get('Tipo', None)  # Propagar o tipo de despesa
    #             parcela['Tipo de Pagamento'] = row.get('Tipo de Pagamento', None)  # Propagar o tipo de pagamento
    #         parcelas_expandidas.extend(parcelas)

    #     # Criar DataFrame consolidado das parcelas
    #     df_expansion = pd.DataFrame(parcelas_expandidas)

    #     # Garantir que as colunas necessárias existem no DataFrame expandido
    #     required_columns = ['Mes', 'Tipo', 'Valor', 'Tipo de Pagamento']
    #     missing_columns = [col for col in required_columns if col not in df_expansion.columns]
    #     if missing_columns:
    #         raise ValueError(f"As seguintes colunas estão ausentes no DataFrame expandido: {missing_columns}")

    #     # Garantir que a coluna 'Mes' esteja no formato datetime
    #     df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes'], errors='coerce').dt.to_period('M').dt.to_timestamp()

    #     # Filtrar o DataFrame com base nas datas selecionadas
    #     df_filtered = df_expansion[
    #         (df_expansion['Mes'] >= pd.to_datetime(data_inicio)) &
    #         (df_expansion['Mes'] <= pd.to_datetime(data_fim))
    #     ]

    #     # Garantir que não há valores nulos nas colunas essenciais
    #     df_filtered = df_filtered.dropna(subset=['Tipo', 'Mes', 'Valor'])

    #     # Calcular o valor ajustado (todos os valores serão somados, independentemente do tipo de pagamento)
    #     df_filtered["Valor Ajustado"] = df_filtered["Valor"]

    #     # Adicionar coluna com o formato de mês no padrão brasileiro (Ex.: "Out 2024")
    #     df_filtered["Mês Formatado"] = df_filtered["Mes"].dt.strftime('%b %Y').str.capitalize()

    #     # Agrupar os dados por mês formatado e tipo
    #     grouped_df = (
    #         df_filtered
    #         .groupby(["Mês Formatado", "Tipo"], as_index=False)["Valor Ajustado"]
    #         .sum()
    #     )

    #     # Remover as categorias com valor ajustado igual a zero
    #     grouped_df = grouped_df[grouped_df["Valor Ajustado"] > 0]

    #     # Garantir que os meses estão ordenados corretamente
    #     meses_ordenados = (
    #         pd.to_datetime(grouped_df["Mês Formatado"], format='%b %Y', errors='coerce')
    #         .drop_duplicates()
    #         .sort_values()
    #     )
    #     categorias_ordenadas = meses_ordenados.dt.strftime('%b %Y').str.capitalize().tolist()

    #     # Garantir que o DataFrame esteja ordenado pelas colunas corretamente
    #     grouped_df["Mês Formatado"] = pd.Categorical(
    #         grouped_df["Mês Formatado"],
    #         categories=categorias_ordenadas,
    #         ordered=True
    #     )
    #     grouped_df = grouped_df.sort_values("Mês Formatado")

    #     grouped_df['Valor Formatado'] = grouped_df['Valor Ajustado'].apply(format_brl)


    #     # Criar o gráfico de barras agrupadas
    #     fig = px.bar(
    #         grouped_df,
    #         x="Mês Formatado",  # Agrupamento por mês no formato "Out 2024"
    #         y="Valor Ajustado",  # Valores no eixo Y
    #         color="Tipo",  # Diferencia os tipos por cor
    #         text_auto=True,  # Exibe os valores diretamente nas barras
    #         title="Despesas por Tipo e Mês",
    #         # labels={
    #         #     "Valor Ajustado": "Valor Total (R$)",
    #         #     "Mês Formatado": "Mês",
    #         #     "Tipo": "Tipo de Despesa",
    #         # }
    #         custom_data=['Tipo']
    #     )

    #             # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
    #                     '<b>Valor:</b> %{y}<br>'
    #                     '<b>Mês:</b> %{x} <extra></extra>'
    #                     ),
    #         #marker=dict(line=dict(width=0.5, color='white'))
    #     )

    #      # Ajustar o limite do eixo Y para garantir que valores pequenos sejam visíveis
    #     fig.update_layout(
    #         xaxis_title='Mês',
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo para valores no eixo Y
    #             title='Valor Total (R$)',
    #             #range=[0, grouped_df['Valor'].max() + 400],  # Ajusta o limite inferior para não cortar as barras pequenas
    #         ),
    #         #xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         # xaxis=dict(
    #         #     tickmode='array',
    #         #     tickvals=grouped_df['Mes'],
    #         #     ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
    #         # ),
    #         legend_title="Tipo de Despesa",
    #         title_x=0.5,
    #         bargap=0.15,  # Espaçamento entre grupos de barras
    #         barmode='group',  # Assegura que a barra seja empilhada corretamente
    #         xaxis=dict(tickmode='array', tickvals=grouped_df['Mês Formatado'].unique())  # Alinhamento dinâmico dos meses
    #     )

    #     # Estilizar o layout para barras agrupadas
    #     # fig.update_layout(
    #     #     barmode="group",  # Barras agrupadas lado a lado
    #     #     xaxis_title="Mês",
    #     #     yaxis_title="Valor Total (R$)",
    #     #     legend_title="Tipo de Despesa",
    #     #     title_x=0.5,
    #     #     bargap=0.15,  # Espaçamento entre grupos de barras
    #     #     xaxis=dict(tickmode='array', tickvals=grouped_df['Mês Formatado'].unique())  # Alinhamento dinâmico dos meses
    #     # )

    #     return fig





    # @st.cache_data
    # def generate_stacked_bar_chart_v1(df):
    #     """
    #     Gera um gráfico de barras empilhadas sem os totais no topo das barras,
    #     considerando apenas a parcela na data de cadastro da despesa.
    #     """
    #     def adjust_installments(row):
    #         """
    #         Ajusta as parcelas para considerar apenas a data inicial da despesa.
    #         """
    #         installments = []
    #         if row['Parcelas'] > 0:  # Se for pagamento parcelado
    #             # Apenas o registro da parcela na data de cadastro
    #             installments.append({'Mes': row['Data'], 'Tipo': 'Crédito', 'Valor': row['Valor']})
    #         else:
    #             # Despesas à vista como uma única entrada
    #             installments.append({'Mes': row['Data'], 'Tipo': 'À Vista', 'Valor': row['Valor']})
    #         return installments

    #     # Aplicar a função `adjust_installments` a cada linha do DataFrame
    #     adjusted_installments = []
    #     for _, row in df.iterrows():
    #         adjusted_installments.extend(adjust_installments(row))

    #     # Criar DataFrame consolidado
    #     adjusted_df = pd.DataFrame(adjusted_installments)

    #     # Garantir que a coluna 'Mes' esteja no formato datetime
    #     adjusted_df['Mes'] = pd.to_datetime(adjusted_df['Mes']).dt.to_period('M').dt.to_timestamp()

    #     # Agrupar por mês e tipo de pagamento
    #     grouped_df = adjusted_df.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()

    #     # Formatar valores e datas para exibição
    #     grouped_df['Mes Formatado'] = grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize()
    #     grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    #     # Criar o gráfico de barras empilhadas
    #     fig = px.bar(
    #         grouped_df,
    #         x='Mes',
    #         y='Valor',
    #         color='Tipo',
    #         title='Despesas Totais por Mês (À Vista + Crédito)',
    #         color_discrete_map={'À Vista': 'blue', 'Crédito': 'orange'},
    #         text=grouped_df['Valor Formatado'],  # Exibe os valores formatados dentro das barras
    #         hover_data={'Tipo': True, 'Valor Formatado': True, 'Mes Formatado': True}  # Exibe valores formatados no tooltip
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
    #                     '<b>Valor:</b> %{customdata[1]}<br>'
    #                     '<b>Mês:</b> %{customdata[2]} <extra></extra>'
    #                     ),
    #     )

    #     # Ajustar o eixo y para garantir que valores baixos sejam visíveis
    #     fig.update_layout(
    #         xaxis_title='Mês',
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo para valores no eixo Y
    #             title='Valor (R$)',
    #             range=[0, grouped_df['Valor'].max() + 400],  # Ajusta o limite inferior para não cortar as barras pequenas
    #         ),
    #         xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         xaxis=dict(
    #             tickmode='array',
    #             tickvals=grouped_df['Mes'],
    #             ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
    #         ),
    #         barmode='stack',  # Assegura que a barra seja empilhada corretamente
    #     )

    #     return fig


    # @st.cache_data
    # def generate_stacked_bar_chart_v2(df):
    #     """
    #     Gera um gráfico de barras empilhadas com valores totais no topo, mantendo a atualização
    #     automática do gráfico quando itens da legenda são ocultados.
    #     """
    #     def adjust_installments(row):
    #         """
    #         Ajusta as parcelas para considerar apenas a data inicial da despesa.
    #         """
    #         installments = []
    #         if row['Parcelas'] > 0:  # Se for pagamento parcelado
    #             # Apenas o registro da parcela na data de cadastro
    #             installments.append({'Mes': row['Data'], 'Tipo': 'Crédito', 'Valor': row['Valor']})
    #         else:
    #             # Despesas à vista como uma única entrada
    #             installments.append({'Mes': row['Data'], 'Tipo': 'À Vista', 'Valor': row['Valor']})
    #         return installments

    #     # Aplicar a função `adjust_installments` a cada linha do DataFrame
    #     adjusted_installments = []
    #     for _, row in df.iterrows():
    #         adjusted_installments.extend(adjust_installments(row))

    #     # Criar DataFrame consolidado
    #     adjusted_df = pd.DataFrame(adjusted_installments)

    #     # Garantir que a coluna 'Mes' esteja no formato datetime
    #     adjusted_df['Mes'] = pd.to_datetime(adjusted_df['Mes']).dt.to_period('M').dt.to_timestamp()

    #     # Agrupar por mês e tipo de pagamento
    #     grouped_df = adjusted_df.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()

    #     # Formatar valores e datas para exibição
    #     grouped_df['Mes Formatado'] = grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize()
    #     grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    #     # Criar o gráfico de barras empilhadas
    #     fig = px.bar(
    #         grouped_df,
    #         x='Mes',
    #         y='Valor',
    #         color='Tipo',
    #         title='Despesas Totais por Mês (À Vista + Crédito)',
    #         color_discrete_map={'À Vista': 'blue', 'Crédito': 'orange'},
    #         text=grouped_df['Valor Formatado'],  # Exibe os valores formatados dentro das barras
    #         hover_data={'Tipo': True, 'Valor Formatado': True, 'Mes Formatado': True}  # Exibe valores formatados no tooltip
    #     )

    #     # Adicionar os totais no topo das barras
    #     total_df = grouped_df.groupby('Mes')['Valor'].sum().reset_index()
    #     for _, row in total_df.iterrows():
    #         total_text = f"Total: {format_brl(row['Valor'])}"
    #         fig.add_annotation(
    #             x=row['Mes'],
    #             y=row['Valor'] + 50,  # Ajustar buffer conforme necessário para que o texto não sobreponha a barra
    #             text=total_text,
    #             showarrow=False,
    #             align="center",
    #             yanchor="bottom",
    #         )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
    #                     '<b>Valor:</b> %{customdata[1]}<br>'
    #                     '<b>Mês:</b> %{customdata[2]} <extra></extra>'
    #                     ),
    #         # Ajustar o tamanho da barra para garantir que valores pequenos sejam visíveis
    #         #marker=dict(line=dict(width=0.5, color='white'))
    #     )

    #     # Ajustar o eixo y para garantir que valores baixos sejam visíveis
    #     fig.update_layout(
    #         xaxis_title='Mês',
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo para valores no eixo Y
    #             title='Valor (R$)',
    #             range=[0, grouped_df['Valor'].max() + 400],  # Ajusta o limite inferior para não cortar as barras pequenas
    #         ),
    #         xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         xaxis=dict(
    #             tickmode='array',
    #             tickvals=grouped_df['Mes'],
    #             ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
    #         ),
    #         barmode='stack',  # Assegura que a barra seja empilhada corretamente
    #     )

    #     return fig



    # @st.cache_data
    # def generate_stacked_bar_chart_v3(df, data_inicio, data_fim):
    #     """
    #     Gera o gráfico de barras empilhadas com base nas despesas, exibindo as parcelas
    #     dentro do intervalo de datas informado.
    #     """
    #     # Expandir as parcelas de cada despesa
    #     expanded_installments = []
    #     for _, row in df.iterrows():
    #         expanded_installments.extend(expand_installments_v2(row))

    #     # Criar DataFrame consolidado
    #     df_expansion = pd.DataFrame(expanded_installments)

    #     # Garantir que a coluna 'Mes' esteja no formato datetime
    #     df_expansion['Mes'] = pd.to_datetime(df_expansion['Mes']).dt.to_period('M').dt.to_timestamp()

    #     # Filtrar o DataFrame com base nas datas selecionadas
    #     df_expansion_filtered = df_expansion[
    #         (df_expansion['Mes'] >= pd.to_datetime(data_inicio)) & 
    #         (df_expansion['Mes'] <= pd.to_datetime(data_fim))
    #     ]

    #     # Agrupar por mês e tipo de pagamento
    #     grouped_df = df_expansion_filtered.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()

    #     # Formatar valores e datas para exibição
    #     grouped_df['Mes Formatado'] = grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize()
    #     grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    #     # Criar o gráfico de barras empilhadas
    #     fig = px.bar(
    #         grouped_df,
    #         x='Mes',
    #         y='Valor',
    #         color='Tipo',
    #         title='Despesas Totais por Mês (À Vista + Crédito)',
    #         color_discrete_map={'À Vista': 'blue', 'Crédito': 'orange'},
    #         text=grouped_df['Valor Formatado'],  # Exibe os valores formatados dentro das barras
    #         hover_data={'Tipo': True, 'Valor Formatado': True, 'Mes Formatado': True}  # Exibe valores formatados no tooltip
    #     )

    #     # Adicionar os totais no topo das barras
    #     total_df = grouped_df.groupby('Mes')['Valor'].sum().reset_index()
    #     for _, row in total_df.iterrows():
    #         total_text = f"Total: {format_brl(row['Valor'])}"
    #         fig.add_annotation(
    #             x=row['Mes'],
    #             y=row['Valor'] + 50,  # Ajustar buffer conforme necessário para que o texto não sobreponha a barra
    #             text=total_text,
    #             showarrow=False,
    #             align="center",
    #             yanchor="bottom",
    #         )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
    #                     '<b>Valor:</b> %{customdata[1]}<br>'
    #                     '<b>Mês:</b> %{customdata[2]} <extra></extra>'
    #                     ),
    #         #marker=dict(line=dict(width=0.5, color='white'))
    #     )

    #     # Ajustar o limite do eixo Y para garantir que valores pequenos sejam visíveis
    #     fig.update_layout(
    #         xaxis_title='Mês',
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo para valores no eixo Y
    #             title='Valor Total (R$)',
    #             range=[0, grouped_df['Valor'].max() + 500],  # Ajusta o limite inferior para não cortar as barras pequenas
    #         ),
    #         xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
    #         xaxis=dict(
    #             tickmode='array',
    #             tickvals=grouped_df['Mes'],
    #             ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
    #         ),
    #         barmode='stack',  # Assegura que a barra seja empilhada corretamente
    #         legend_title="Tipo de Pagamento",
    #         title_x=0.5,
    #         bargap=0.15,  # Espaçamento entre grupos de barras
    #     )

    #     return fig


    # @st.cache_data
    # def generate_grouped_bar_chart_by_day_type(df, data_inicio, data_fim):
    #     # Garantindo que a coluna 'Data' esteja no formato datetime
    #     df["Data"] = pd.to_datetime(df["Data"])
    #     df["Dia"] = df["Data"].dt.strftime("%d/%m/%Y")  # Criar uma coluna para exibição no formato brasileiro

    #     # Filtrar o DataFrame com base nas datas de início e fim fornecidas
    #     df_filtered = df[(df["Data"] >= pd.to_datetime(data_inicio)) & 
    #                     (df["Data"] <= pd.to_datetime(data_fim))]

    #     # Agrupando os dados por 'Data' e 'Tipo', somando os valores
    #     grouped_df = df_filtered.groupby(['Data', 'Tipo'], as_index=False)['Valor'].sum()
    #     grouped_df['Dia'] = grouped_df['Data'].dt.strftime("%d/%m/%Y")  # Adiciona a coluna para exibição
    #     grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(format_brl)

    #     # Ordenando o DataFrame pelas datas
    #     grouped_df = grouped_df.sort_values('Data')  # Ordena cronologicamente pelas datas

    #     # Criando o gráfico de barras agrupadas
    #     fig = px.bar(
    #         grouped_df,
    #         x="Data",  # Usar a coluna 'Data' como base para alinhamento correto
    #         y="Valor",
    #         color="Tipo",
    #         title="Despesas por Tipo e Dia",
    #         barmode="group",  # Exibe as barras lado a lado
    #         custom_data=['Tipo'],
    #     )

    #     # Estilizar o gráfico
    #     fig.update_traces(
    #         hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
    #                     '<b>Valor:</b> %{y}<br>'
    #                     '<b>Data:</b> %{x|%d/%m/%Y} <extra></extra>'),
    #     )

    #     # Ajustes no layout
    #     fig.update_layout(
    #         xaxis=dict(
    #             title="Dia",
    #             tickmode="array",  # Exibe apenas as datas relevantes
    #             tickvals=grouped_df["Data"],  # Apenas datas presentes no agrupamento
    #             ticktext=grouped_df["Dia"],  # Exibe as datas formatadas no eixo X
    #         ),
    #         yaxis=dict(
    #             tickprefix='R$',  # Prefixo para valores no eixo Y
    #             title='Valor Total (R$)',
    #         ),
    #         legend_title="Tipo de Despesa",
    #         title_x=0.5,
    #         bargap=0.15,  # Espaçamento entre grupos de barras
    #     )

    #     return fig





    def view_dashboard():
        # Criação das abas
        general, expenses, incomes, investments = st.tabs(["Geral", "Despesas", "Receitas", "Investimentos"])
        
        with general:
            st.header("Dash geral")
        with expenses:
            manager_expense()
            # expense_df = get_expense()
            # if expense_df.empty:
            #     st.info('''
            #                 Nenhuma ***despesa*** cadastrada.\n\n
            #                 Clique no botão abaixo para ser redirecionado a página de ***Despesas***.
            #                 ''')
            #     with st.form(key='dash_expense_form', border=False):
            #         submit_button = st.form_submit_button(label="Ok", use_container_width=True)
            #         if submit_button:                        
            #             st.switch_page("pages/2_Despesas.py")   
            #         return 

            # category_df = get_category()
            # if category_df.empty:
            #     st.info('''
            #             Nenhuma ***categoria*** cadastrada.\n\n
            #             Clique no botão abaixo para ser redirecionado a página de ***Categorias***.
            #             ''')
            #     with st.form(key='dash_category_form', border=False):
            #         submit_button = st.form_submit_button(label="Ok", use_container_width=True)
            #         if submit_button:                        
            #             st.switch_page("pages/5_Categorias.py")   
            #         return 

            # # Filtra os dados
            # df_expense_final = get_filtered_data(expense_df, category_df)

            # # Configura os filtros de data
            # st.title("Dashboard de Despesas")
            # data_inicio = st.date_input("Data Início:", date.today() - timedelta(days=365), format="DD/MM/YYYY")
            # data_fim = st.date_input("Data Fim", date.today(), format="DD/MM/YYYY")

            # # Filtra despesas por intervalo de datas
            # df_filtrado = df_expense_final[
            #     (df_expense_final['Data'] >= pd.to_datetime(data_inicio)) &
            #     (df_expense_final['Data'] <= pd.to_datetime(data_fim))
            # ].copy()

            # # Adiciona coluna para tipo de pagamento (À vista ou Crédito)
            # df_filtrado['Tipo de Pagamento'] = df_filtrado['Parcelas'].apply(
            #     lambda x: 'Crédito' if x > 0 else 'À Vista'
            # )

            # # Checkbox para filtrar apenas despesas à vista
            # if not st.checkbox("Exibir pagamentos a prazo", value=True):
            #     df_filtrado = df_filtrado[df_filtrado['Tipo de Pagamento'] == 'À Vista']

            # # Gera gráficos
            # #stacked_bar_chart = generate_stacked_bar_chart(df_filtrado)
            # #installment_evolution_chart = chart_installment_evolution(df_filtrado)
            # installment_evolution_chart_v2 = chart_installment_evolution_v2(df_filtrado)
            # #stacked_bar_chart_category = generate_stacked_bar_chart_category(df_filtrado)
            # #stacked_bar_chart_with_month = generate_stacked_bar_chart_with_month(df_filtrado)
            # #pie_chart_category = generate_pie_chart_category(df_filtrado)
            # pie_chart_category_v2 = generate_pie_chart_category_v2(df_filtrado, data_inicio, data_fim)
            # stacked_bar_chart_type = generate_stacked_bar_chart_type(df_filtrado)
            # #grouped_bar_chart_by_month_type = generate_grouped_bar_chart_by_month_type(df_filtrado)
            # grouped_bar_chart_by_month_type_v2 = generate_grouped_bar_chart_by_month_type_v2(df_filtrado, data_inicio, data_fim)
            # #stacked_bar_chart_v1 = generate_stacked_bar_chart_v1(df_filtrado)
            # #stacked_bar_chart_v2 = generate_stacked_bar_chart_v2(df_filtrado)
            # stacked_bar_chart_v3 = generate_stacked_bar_chart_v3(df_filtrado, data_inicio, data_fim)
            # grouped_bar_chart_by_day_type = generate_grouped_bar_chart_by_day_type(df_filtrado, data_inicio, data_fim)


            # # Exibe os gráficos
            # # st.plotly_chart(stacked_bar_chart, use_container_width=True)
            # # st.plotly_chart(stacked_bar_chart_v1, use_container_width=True)
            # # st.plotly_chart(stacked_bar_chart_v2, use_container_width=True)
            # st.plotly_chart(stacked_bar_chart_v3, use_container_width=True)

            # col1, col2 = st.columns(2)
            # with col1:
            #     st.plotly_chart(installment_evolution_chart_v2, use_container_width=True)
            # with col2:
            #     st.plotly_chart(pie_chart_category_v2, use_container_width=True)
            
            
            # #st.plotly_chart(pie_chart_category_v2, use_container_width=True)
            # #st.plotly_chart(stacked_bar_chart_category, use_container_width=True)
            # #st.plotly_chart(stacked_bar_chart_with_month, use_container_width=True)
            # st.plotly_chart(grouped_bar_chart_by_month_type_v2, use_container_width=True)
            # #st.plotly_chart(grouped_bar_chart_by_month_type, use_container_width=True)
            # #st.plotly_chart(stacked_bar_chart_type, use_container_width=True)
            # st.plotly_chart(grouped_bar_chart_by_day_type, use_container_width=True)

        with incomes:
            st.header('Dash Receitas')
        with investments:
            st.header('Dash Investimento')

    view_dashboard()


if __name__ == "__main__":
    main()


st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")