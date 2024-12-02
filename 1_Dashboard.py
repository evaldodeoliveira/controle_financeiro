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


def main():
    #teste
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


    def grafico_teste(df_filtrado):
        # Adicionando coluna de mês ao DataFrame filtrado com formato de string para o eixo X
        df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M').astype(str)

        # Criando uma nova coluna para identificar as despesas com cartão de crédito, considerando as parcelas
        df_filtrado['Despesas_Cartao_Credito'] = 0
        df_filtrado.loc[df_filtrado['Pagamento'] == 'Cartão de Crédito', 'Despesas_Cartao_Credito'] = df_filtrado['Valor'] * df_filtrado['Parcelas']


        # Agrupando por 'Mes' e somando os valores
        despesas_mensal = df_filtrado.groupby('Mes').agg(
            Despesas_Cartao_Credito=('Despesas_Cartao_Credito', 'sum'),
            Despesas_Outras=('Valor', 'sum')
        ).reset_index()

        # Convertendo a coluna 'Mes' de volta para datetime para uma visualização correta no gráfico
        despesas_mensal['Mes'] = pd.to_datetime(despesas_mensal['Mes'], format='%Y-%m')

        # Gerando o gráfico de barras empilhadas
        fig_despesas_mensal = px.bar(despesas_mensal, 
                                    x='Mes', 
                                    y=['Despesas_Cartao_Credito', 'Despesas_Outras'], 
                                    title='Distribuição Mensal das Despesas (Cartão de Crédito vs Outras Despesas)',
                                    labels={'Despesas_Cartao_Credito': 'Despesas com Cartão de Crédito', 'Despesas_Outras': 'Outras Despesas'},
                                    color_discrete_sequence=['#FFA07A', '#98C9E4'])

        # Adicionando os valores totais no topo das barras empilhadas
        for i, row in despesas_mensal.iterrows():
            total = row['Despesas_Cartao_Credito'] + row['Despesas_Outras']
            fig_despesas_mensal.add_annotation(
                x=row['Mes'],
                y=total,
                text=f'{total:.2f}',  # Exibindo o total com 2 casas decimais
                showarrow=False,
                font=dict(size=12, color="white"),
                align="center",
                yanchor="bottom"  # Alinhamento vertical correto
            )

        # Formatando o eixo X para exibir apenas o mês e o ano uma vez (exemplo: "Nov 2024")
        fig_despesas_mensal.update_xaxes(
            tickformat="%b %Y",  # Formato de exibição do mês e ano
            dtick="M1"           # Configura a exibição para cada mês (sem duplicações)
        )

        # Exibindo o gráfico
        st.plotly_chart(fig_despesas_mensal, use_container_width=True, key='teste')

    def payment_type_chart(df):

        # Convert 'Date' column to datetime
        df['Data'] = pd.to_datetime(df['Data'])
        
        # Sidebar for time range selection
        st.sidebar.header("Filtros de tempo")
        start_date = st.sidebar.date_input("Data Início", df['Data'].min())
        end_date = st.sidebar.date_input("Data Fim", df['Data'].max())
        
        # Filter dataframe by selected time range
        filtered_df = df[(df['Data'] >= pd.to_datetime(start_date)) & (df['Data'] <= pd.to_datetime(end_date))]

        # Checkbox to show or hide credit payments
        show_credit = st.checkbox("Pagamentos a prazo", value=True)
        
        # Add a column to differentiate between cash and credit
        filtered_df['Tipo de Pagamento'] = filtered_df['Parcelas'].apply(lambda x: 'Crédito' if x > 0 else 'À Vista')
        
        if not show_credit:
            filtered_df = filtered_df[filtered_df['Tipo de Pagamento'] == 'À Vista']

        # Group data by payment type and date
        grouped_df = filtered_df.groupby(['Tipo de Pagamento', 'Data']).sum(numeric_only=True).reset_index()

        # Create stacked bar chart
        fig = px.bar(
            grouped_df,
            x='Data',
            y='Valor',
            color='Tipo de Pagamento',
            title='Despesas por Tipo de Pagamento',
            labels={'Valor': 'Valor (BRL)', 'Data': 'Mês'},
            barmode='stack'
        )
        
        
        # Update X-axis to show months
        fig.update_xaxes(tickformat="%b %Y")
        
        # Update layout to format values in Brazilian style
        fig.update_yaxes(tickprefix="R$", tickformat=",.")

        # Formatando o eixo X para exibir apenas o mês e o ano uma vez (exemplo: "Nov 2024")
        fig.update_xaxes(
            tickformat="%b %Y",  # Formato de exibição do mês e ano
            dtick="M1"           # Configura a exibição para cada mês (sem duplicações)
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)



    @st.cache_data
    def generate_stacked_bar_chart(df):
        """
        Gera um gráfico de barras empilhadas com valores totais no topo,
        utilizando a coluna 'Última parcela' e assumindo que 'Valor' já é o valor da parcela.
        """
        # Expandir as parcelas usando 'Última parcela'
        parcelas_expandidas = []
        for _, row in df.iterrows():
            if row['Parcelas'] > 0:
                data_inicial = row['Data']
                data_final = row['Última parcela']

                # Gerar todas as parcelas com base em 'Data' e 'Última parcela'
                parcelas = pd.date_range(start=data_inicial, end=data_final, freq='MS')  # Frequência mensal
                for parcela_data in parcelas:
                    parcelas_expandidas.append({'Mes': parcela_data, 'Tipo': 'Crédito', 'Valor': row['Valor']})
            else:
                # Adicionar despesas à vista (sem expansão)
                parcelas_expandidas.append({'Mes': row['Data'], 'Tipo': 'À Vista', 'Valor': row['Valor']})
        # Criar DataFrame consolidado
        df_expansao = pd.DataFrame(parcelas_expandidas)
        # Garantir que a coluna 'Mes' esteja no formato datetime
        df_expansao['Mes'] = pd.to_datetime(df_expansao['Mes']).dt.to_period('M').dt.to_timestamp()

        # Agrupar por mês e tipo de pagamento
        grouped_df = df_expansao.groupby(['Mes', 'Tipo'])['Valor'].sum().reset_index()

        # Criar coluna formatada para valores no tooltip e na barra
        grouped_df["Mes"] = pd.to_datetime(grouped_df["Mes"], format="%Y-%m")
        grouped_df["Mes Formatado"] = grouped_df["Mes"].dt.strftime("%b %Y")  # Coluna formatada
        grouped_df['Valor Formatado'] = grouped_df['Valor'].apply(
            lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

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

        # Estilizar o gráfico
        fig.update_traces(
            hovertemplate=('<b>Tipo:</b> %{customdata[0]}<br>'
                        '<b>Valor:</b> %{customdata[1]}<br>'
                        '<b>Mês:</b> %{customdata[2]} <extra></extra>'
                        )
        )

        # Calcular a altura máxima para posicionar os totais
        total_df = grouped_df.groupby('Mes')['Valor'].sum().reset_index()
        for _, row in total_df.iterrows():
            total_text = f"Total: R${row['Valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            fig.add_annotation(
                x=row['Mes'],
                y=row['Valor'] + 50,  # Ajustar buffer conforme necessário
                text=total_text,
                showarrow=False,
                align="center",
                yanchor="bottom",
            )

        # Personalizar layout
        fig.update_layout(
            xaxis_title='Mês',
            yaxis=dict(
                tickprefix='R$',  # Prefixo para valores no eixo Y
                title='Valor (R$)',
            ),
            xaxis_tickformat="%b %Y",  # Exibe o mês abreviado e o ano
            xaxis=dict(
                tickmode='array',
                tickvals=grouped_df['Mes'],
                ticktext=grouped_df['Mes'].dt.strftime('%b %Y').str.capitalize(),
            ),
        )

        return fig

    @st.cache_data
    def chart_installment_evolution(df_filtrado):
        """
        Gera um gráfico de linha mostrando a evolução das parcelas por mês,
        formatando os valores monetários e a data no padrão brasileiro.
        """

        # Garantir que 'Parcelas' seja numérico
        df_filtrado['Parcelas'] = pd.to_numeric(df_filtrado['Parcelas'], errors='coerce').fillna(0).astype(int)
        df_credito = df_filtrado[df_filtrado['Parcelas'] > 0]

        # Expandir as parcelas usando a lógica baseada nas colunas existentes
        parcelas_expandidas = []
        for _, row in df_credito.iterrows():
            data_inicial = row['Data']
            data_final = row['Última parcela']  # Usa a última parcela para determinar o período
            parcelas = pd.date_range(start=data_inicial, end=data_final, freq='MS')  # Gera parcelas mensais
            
            for parcela_data in parcelas:
                parcelas_expandidas.append({'Data Parcela': parcela_data, 'Valor Parcela': row['Valor']})

        # Verificar se existem parcelas
        if not parcelas_expandidas:
            # Se não houver parcelas, criar um gráfico vazio
            fig = px.line(
                title='Evolução das Parcelas por Mês',
                labels={'Data Parcela': 'Mês do Parcelamento', 'Valor Parcela': 'Montante de Parcelas'}
            )
            fig.add_annotation(
                x=0.5, y=0.5, text="Nenhuma despesa parcelada encontrada.",
                showarrow=False, font=dict(size=16, color="red"), align="center"
            )
            return fig

        # Criar o DataFrame consolidado das parcelas
        df_parcelas = pd.DataFrame(parcelas_expandidas)

        # Agrupar os valores por mês
        montante_mensal = (
            df_parcelas.groupby(df_parcelas['Data Parcela'].dt.to_period("M"))['Valor Parcela'].sum().reset_index()
        )
        montante_mensal['Data Parcela'] = montante_mensal['Data Parcela'].dt.to_timestamp()

        # Adicionar coluna formatada para os tooltips
        montante_mensal['Valor Formatado'] = montante_mensal['Valor Parcela'].apply(
            lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        montante_mensal['Data Formatada'] = montante_mensal['Data Parcela'].dt.strftime('%b de %Y').str.capitalize()

        # Gerar o gráfico de linha
        fig = px.line(
            montante_mensal,
            x='Data Parcela',
            y='Valor Parcela',
            title='Evolução das Parcelas por Mês',
            labels={
                'Data Parcela': 'Mês do Parcelamento',
                'Valor Parcela': 'Montante de Parcelas (R$)'
            },
            hover_data={'Valor Parcela': False, 'Valor Formatado': True, 'Data Formatada': True}  # Exibe valores formatados no tooltip
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
                tickvals=montante_mensal['Data Parcela'],
                ticktext=montante_mensal['Data Parcela'].dt.strftime('%b %Y').str.capitalize()
            )
        )

        return fig
    
#Comparação entre Despesas Fixas e Variáveis
    @st.cache_data
    def generate_stacked_bar_chart_category(df):
        """
        Gera um gráfico de barras empilhadas para custos distintos por categoria, 
        distinguindo pagamentos à vista e a prazo.
        """
        # Transformar as colunas de data no formato datetime
        df["Data"] = pd.to_datetime(df["Data"])
        df["Última parcela"] = pd.to_datetime(df["Última parcela"])

        # Definir tipo de pagamento: À Vista ou A Prazo
        df["Tipo de Custo"] = df["Parcelas"].apply(lambda x: "À Vista" if x == 0 else "A Prazo")

        # Agrupar por Categoria e Tipo de Custo (À Vista / A Prazo)
        grouped_df = df.groupby(["Categoria", "Tipo de Custo"])["Valor total das parcelas"].sum().reset_index()

        # Criar gráfico de barras empilhadas
        fig = px.bar(
            grouped_df,
            x="Categoria",
            y="Valor total das parcelas",
            color="Tipo de Custo",
            text=grouped_df["Valor total das parcelas"].apply(
                lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            title="Custos Totais por Categoria (À Vista e A Prazo)",
            labels={
                "Categoria": "Categoria",
                "Valor total das parcelas": "Valor Total (R$)",
                "Tipo de Custo": "Tipo de Custo"
            },
            color_discrete_map={"À Vista": "blue", "A Prazo": "orange"},  # Definir cores personalizadas
        )

        # Estilizar o gráfico
        fig.update_traces(textposition="inside", textfont_size=12)
        fig.update_layout(
            xaxis_title="Categoria",
            yaxis_title="Valor Total (R$)",
            yaxis_tickprefix="R$",  # Adiciona prefixo para valores no eixo Y
            legend_title="Tipo de Custo",
            barmode="stack",  # Define o modo de barras empilhadas
        )

        return fig


    @st.cache_data
    def generate_stacked_bar_chart_with_month(df):
        """
        Gera um gráfico de barras empilhadas agrupando por mês e categoria,
        distinguindo pagamentos à vista e a prazo.
        """
        # Transformar as colunas de data no formato datetime
        df["Data"] = pd.to_datetime(df["Data"])
        df["Última parcela"] = pd.to_datetime(df["Última parcela"])

        # Criar coluna para o mês da despesa
        df["Mês"] = df["Data"].dt.to_period("M").dt.to_timestamp()

        # Definir tipo de pagamento: À Vista ou A Prazo
        df["Tipo de Custo"] = df["Parcelas"].apply(lambda x: "À Vista" if x == 0 else "A Prazo")

        # Expansão das parcelas (para considerar todos os meses até a última parcela)
        parcelas_expandidas = []
        for _, row in df.iterrows():
            if row["Parcelas"] > 0:
                # Criar todas as parcelas a partir da data inicial até a última parcela
                parcelas = pd.date_range(start=row["Data"], end=row["Última parcela"], freq="MS")
                for parcela_data in parcelas:
                    parcelas_expandidas.append({
                        "Mês": parcela_data,
                        "Categoria": row["Categoria"],
                        "Tipo de Custo": "A Prazo",
                        "Valor": row["Valor"]
                    })
            else:
                # Adicionar valores à vista (sem expansão)
                parcelas_expandidas.append({
                    "Mês": row["Mês"],
                    "Categoria": row["Categoria"],
                    "Tipo de Custo": "À Vista",
                    "Valor": row["Valor"]
                })

        # Criar um novo DataFrame consolidado
        df_expansao = pd.DataFrame(parcelas_expandidas)

        # Agrupar por Mês, Categoria e Tipo de Custo
        grouped_df = (
            df_expansao.groupby(["Mês", "Categoria", "Tipo de Custo"])["Valor"]
            .sum()
            .reset_index()
        )

        # Criar gráfico de barras empilhadas com Mês e Categoria no eixo X
        fig = px.bar(
            grouped_df,
            x="Mês",
            y="Valor",
            color="Tipo de Custo",
            facet_col="Categoria",
            text=grouped_df["Valor"].apply(
                lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ),
            title="Custos por Mês e Categoria (À Vista e A Prazo)",
            labels={
                "Mês": "Mês",
                "Valor": "Valor (R$)",
                "Tipo de Custo": "Tipo de Custo"
            },
            color_discrete_map={"À Vista": "blue", "A Prazo": "orange"},
        )

        # Estilizar o gráfico
        fig.update_traces(textposition="inside", textfont_size=12)
        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Valor Total (R$)",
            yaxis_tickprefix="R$",  # Prefixo para valores no eixo Y
            legend_title="Tipo de Custo",
            barmode="stack",  # Define o modo de barras empilhadas
        )

        return fig



    @st.cache_data
    def generate_pie_chart_by_category(df):
        """
        Gera um gráfico de pizza agrupado por categoria, 
        distinguindo os custos com cores diferentes.
        """
        # Transformar as colunas de data no formato datetime
        df["Data"] = pd.to_datetime(df["Data"])
        df["Última parcela"] = pd.to_datetime(df["Última parcela"])

        # Calcular o total de despesas por categoria
        grouped_df = df.groupby("Categoria")["Valor total das parcelas"].sum().reset_index()

        # Adicionar uma coluna com valores formatados para exibição no gráfico
        grouped_df["Valor Formatado"] = grouped_df["Valor total das parcelas"].apply(
            lambda x: f"R${x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        # Criar gráfico de pizza
        fig = px.pie(
            grouped_df,
            values="Valor total das parcelas",  # Tamanho dos setores
            names="Categoria",                 # Categorias como rótulos
            title="Distribuição de Custos por Categoria",
            hole=0.3,                          # Gráfico de rosca
            labels={
                "Valor total das parcelas": "Valor Total (R$)",
                "Categoria": "Categoria"
            },
            color_discrete_sequence=px.colors.qualitative.Set3  # Paleta de cores para categorias
        )

        # Estilizar o gráfico
        fig.update_traces(
            textinfo="percent+label",  # Exibir rótulos e porcentagem nos setores
            hovertemplate="<b>%{label}</b><br>Valor Total: %{customdata}<extra></extra>",
            customdata=grouped_df["Valor Formatado"]  # Adicionar valor formatado no hover
        )

        fig.update_layout(
            showlegend=True,
            legend_title="Categorias",
        )

        return fig


    def view_dashboard():
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
        print(df_filtrado)
        stacked_bar_chart = generate_stacked_bar_chart(df_filtrado)
        installment_evolution_chart = chart_installment_evolution(df_filtrado)
        stacked_bar_chart_category = generate_stacked_bar_chart_category(df_filtrado)
        stacked_bar_chart_with_month = generate_stacked_bar_chart_with_month(df_filtrado)
        pie_chart_category = generate_pie_chart_by_category(df_filtrado)

        # Exibe os gráficos
        st.plotly_chart(stacked_bar_chart, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(installment_evolution_chart, use_container_width=True)
        with col2:
            st.plotly_chart(stacked_bar_chart_category, use_container_width=True)
        
        st.plotly_chart(stacked_bar_chart_with_month, use_container_width=True)
        st.plotly_chart(pie_chart_category, use_container_width=True)



    view_dashboard()


if __name__ == "__main__":
    main()

st.sidebar.markdown("Desenvolvido por [Evaldo](https://www.linkedin.com/in/evaldodeoliveira/)")

         

          
            # # # Gráficos
            # # # 1. Comparativo de Pagamentos (Tipo de Pagamento)
            # # fig_payment_comparison = px.bar(
            # #     filtered_df, 
            # #     x='exp_payment_method', 
            # #     y='exp_value', 
            # #     title='Comparativo de Pagamentos por Tipo',
            # #     labels={'exp_payment_method': 'Tipo de Pagamento', 'exp_value': 'Valor Gasto'},
            # #     color='exp_payment_method'
            # # )

            

            # # # 3. Distribuição de Despesas por Período (Mensal)
            # # monthly_expenses = (
            # #     filtered_df.groupby(filtered_df['exp_date'].dt.to_period("M"))['exp_value'].sum().reset_index()
            # # )
            # # monthly_expenses['exp_date'] = monthly_expenses['exp_date'].dt.to_timestamp()
            # # fig_monthly_distribution = px.bar(
            # #     monthly_expenses,
            # #     x='exp_date',
            # #     y='exp_value',
            # #     title='Distribuição de Despesas por Período (Mensal)',
            # #     labels={'exp_date': 'Mês', 'exp_value': 'Total de Despesas'}
            # # )

            # # # 4. Comparação entre Despesas Fixas e Variáveis
            # # filtered_df['exp_category_type'] = filtered_df['exp_type'].apply(lambda x: 'Fixa' if x == 'Essencial' else 'Variável')
            # # category_expenses = filtered_df.groupby('exp_category_type')['exp_value'].sum().reset_index()
            # # fig_fixed_vs_variable = px.bar(
            # #     category_expenses,
            # #     x='exp_category_type',
            # #     y='exp_value',
            # #     title='Comparação entre Despesas Fixas e Variáveis',
            # #     labels={'exp_category_type': 'Tipo de Despesa', 'exp_value': 'Valor Total'},
            # #     color='exp_category_type'
            # # )

            # # # Layout dos gráficos
            # # st.subheader("Gráficos")

            # # # Organizando os gráficos em duas colunas
            # # col1, col2 = st.columns(2)

            # # with col1:
            # #     st.plotly_chart(fig_category, use_container_width=True)
            # #     st.plotly_chart(fig_payment_comparison, use_container_width=True)
            # #     st.plotly_chart(fig_monthly_distribution, use_container_width=True)

            # # with col2:
            # #     st.plotly_chart(fig_type, use_container_width=True)
            # #     st.plotly_chart(fig_installments, use_container_width=True)
            # #     st.plotly_chart(fig_fixed_vs_variable, use_container_width=True)




            # # # 1. Gráfico de Despesas por Categoria
            # # despesas_categoria = df_filtrado.groupby('Categoria')['Valor'].sum().reset_index()
            # # fig_categoria = px.bar(despesas_categoria, x='Categoria', y='Valor', title='Despesas por Categoria', color='Categoria')
            # # # Remover rótulos do eixo X
            # # fig_categoria.update_layout(
            # #     xaxis=dict(showticklabels=False)
            # # )
            # #fig_categoria = px.pie(despesas_categoria, values='Valor', names='Categoria', title='Despesas por Categoria')

            # # 2. Gráfico de Despesas por Tipo
            # despesas_tipo = df_filtrado.groupby('Tipo')['Valor'].sum().reset_index()
            # fig_tipo = px.bar(despesas_tipo, x='Tipo', y='Valor', title='Despesas por Tipo', color='Tipo')
            # fig_tipo.update_layout(
            #     xaxis=dict(showticklabels=False)
            # )
            # #fig_tipo = px.pie(despesas_tipo, values='Valor', names='Tipo', title='Despesas por Tipo')


            # # 3. Gráfico Comparativo de Pagamentos
            # # despesas_pagamento = df_filtrado.groupby('Pagamento')['Valor'].sum().reset_index()
            # # fig_pagamento = px.bar(despesas_pagamento, x='Pagamento', y='Valor', title='Despesas por Tipo de Pagamento', color='Pagamento')
            # # # Remover rótulos do eixo X
            # # fig_pagamento.update_layout(
            # #     xaxis=dict(showticklabels=False)
            # # )
            # # Agrupar as despesas por Tipo de Pagamento e somar o Valor e Valor Parcela
            # df_filtrado['Total Valor'] = df_filtrado['Valor'] + df_filtrado['Valor Parcela']

            # despesas_pagamento = df_filtrado.groupby('Pagamento')['Total Valor'].sum().reset_index()

            # # Gerar o gráfico com a soma das despesas por Tipo de Pagamento
            # fig_pagamento = px.bar(despesas_pagamento, 
            #                     x='Pagamento', 
            #                     y='Total Valor', 
            #                     title='Despesas por Tipo de Pagamento', 
            #                     color='Pagamento')

            # # Remover rótulos do eixo X
            # fig_pagamento.update_layout(
            #     xaxis=dict(showticklabels=False)
            # )


            # # 4. Gráfico de Evolução das Parcelas a Vencer
            # parcelas_vencimento = []
            # for _, row in df_filtrado[df_filtrado['Parcelas'] >= 1].iterrows():
            #     for parcela_num in range(1, row['Parcelas'] + 1):
            #         data_parcela = row['Data'] + timedelta(days=30 * parcela_num)
            #         parcelas_vencimento.append({'Data Vencimento': data_parcela, 'Valor Parcela': row['Valor Parcela']})

            # # Verificando se a lista 'parcelas_vencimento' tem dados antes de criar o DataFrame
            # if parcelas_vencimento:
            #     df_parcelas = pd.DataFrame(parcelas_vencimento)
            #     # Convertendo a 'Data Vencimento' para datetime se necessário
            #     df_parcelas['Data Vencimento'] = pd.to_datetime(df_parcelas['Data Vencimento'])

            #     # Agrupando a evolução das parcelas
            #     parcelas_evolucao = df_parcelas.groupby(df_parcelas['Data Vencimento'].dt.to_period("M"))['Valor Parcela'].sum().reset_index()

            #     # Convertendo o Period para timestamp
            #     parcelas_evolucao['Data Vencimento'] = parcelas_evolucao['Data Vencimento'].astype('datetime64[ns]')
            #     fig_parcelas = px.line(parcelas_evolucao, x='Data Vencimento', y='Valor Parcela', title='Evolução das Parcelas a Vencer')
            # else:
            #     # Caso não haja parcelas a vencer, criando uma mensagem para o gráfico
            #     fig_parcelas = px.bar(title='Evolução das Parcelas a Vencer', labels={'x': 'Data', 'y': 'Valor Parcela'})
            #     fig_parcelas.add_annotation(
            #         x=0.5, y=0.5, text="Não há parcelas a vencer", showarrow=False,
            #         font=dict(size=20, color="red"), align="center"
            #     )

            # # 5. Gráfico de Distribuição de Despesas por Período
            # # Adicionando coluna de mês ao DataFrame filtrado com formato de string para o eixo X
            # df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M').astype(str)

            # # Agrupando por 'Mes' e somando os valores
            # despesas_mensal = df_filtrado.groupby('Mes')['Valor'].sum().reset_index()

            # # Convertendo a coluna 'Mes' de volta para datetime para uma visualização correta no gráfico
            # despesas_mensal['Mes'] = pd.to_datetime(despesas_mensal['Mes'], format='%Y-%m')

            # # Gerando o gráfico de barras
            # fig_despesas_mensal = px.bar(despesas_mensal, x='Mes', y='Valor', title='Distribuição Mensal das Despesas')

            # # Formatando o eixo X para exibir apenas o mês e o ano uma vez (exemplo: "Nov 2024")
            # fig_despesas_mensal.update_xaxes(
            #     tickformat="%b %Y",  # Formato de exibição do mês e ano
            #     dtick="M1"           # Configura a exibição para cada mês (sem duplicações)
            # )

            # # # 5. Gráfico de Distribuição de Despesas por Período
            # # # Adicionando coluna de mês ao DataFrame filtrado com formato de string para o eixo X
            # # df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M').astype(str)

            # # # Agrupando por 'Mes' e somando os valores
            # # despesas_mensal = df_filtrado.groupby('Mes')['Valor'].sum().reset_index()

            # # # Convertendo a coluna 'Mes' de volta para datetime para uma visualização correta no gráfico
            # # despesas_mensal['Mes'] = pd.to_datetime(despesas_mensal['Mes'], format='%Y-%m')

            # # # Gerando o gráfico de barras
            # # fig_despesas_mensal = px.bar(despesas_mensal, x='Mes', y='Valor', title='Distribuição Mensal das Despesas')

            # # # Formatando o eixo X para exibir o mês e o ano (exemplo: "Nov 2024")
            # # fig_despesas_mensal.update_xaxes(tickformat="%b %Y")

            # # # 5. Gráfico de Distribuição de Despesas por Período
            # # # Criando uma coluna 'Mes' e agrupando as despesas por mês
            # # df_filtrado['Mes'] = df_filtrado['Data'].dt.to_period('M')
            # # despesas_mensal = df_filtrado.groupby('Mes')['Valor'].sum().reset_index()

            # # # Convertendo o Period para datetime
            # # despesas_mensal['Mes'] = despesas_mensal['Mes'].dt.to_timestamp()
            # # print(despesas_mensal['Mes'].max())
