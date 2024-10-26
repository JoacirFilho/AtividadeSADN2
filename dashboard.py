import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu  # Certifique-se de instalar com pip install streamlit-option-menu

# Configurações do dashboard
st.set_page_config(page_title="Análise de Transferências - Eleições 2020 e 2024", layout="wide")

# Estilo de flat design
st.markdown(
    """
    <style>
    .title-text { font-size: 26px; font-weight: bold; color: #2C3E50; }
    .stSidebar { background-color: #F7F9F9; }
    .sidebar-content { font-size: 18px; color: #2C3E50; font-weight: bold; }
    .main-content { padding: 20px; }
    .css-18e3th9 { padding: 0 !important; }  /* Ajusta o espaçamento */
    .css-1gk8ejz { font-weight: 700 !important; color: #2C3E50; } /* Coloração do header */
    </style>
    """, unsafe_allow_html=True
)

# Barra de título
st.markdown('<p class="title-text">📊 Análise de Transferências Temporárias - Eleições 2020 e 2024</p>', unsafe_allow_html=True)

# Função para carregar o dataset
def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file, encoding='ISO-8859-1', delimiter=';')
    return None

# Sidebar de navegação e upload dos datasets
with st.sidebar:
    st.markdown('<p class="sidebar-content">📂 Carregar Arquivos</p>', unsafe_allow_html=True)
    uploaded_file_2024 = st.file_uploader("Dataset de 2024", type=["csv"])
    uploaded_file_2020 = st.file_uploader("Dataset de 2020", type=["csv"])
    
    # Menu de navegação
    page = option_menu(
        "Navegação",
        ["Análise Geral", "Análise por UF e Município"],
        icons=["bar-chart-line", "geo-alt"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#F7F9F9"},
            "icon": {"color": "#2C3E50", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#EEE"},
            "nav-link-selected": {"background-color": "#2C3E50", "color": "#FFF"},
        }
    )

# Verifica se os dois datasets foram carregados
if uploaded_file_2024 is not None and uploaded_file_2020 is not None:
    df_2024 = load_data(uploaded_file_2024)
    df_2020 = load_data(uploaded_file_2020)

    # Adiciona uma coluna para o ano e concatena os datasets
    df_2024['Ano'] = 2024
    df_2020['Ano'] = 2020
    data = pd.concat([df_2024, df_2020])

    # Página 1 - Análise Geral
    if page == "Análise Geral":
        st.subheader("🔍 Análise Geral das Transferências")

        # Filtro dinâmico para o ano
        anos_disponiveis = data['Ano'].unique()
        ano_selecionado = st.sidebar.selectbox('Selecione o ano', anos_disponiveis)
        filtered_data = data[data['Ano'] == ano_selecionado]

        # Tabela e valor total
        col1, col2 = st.columns(2)
        col1.metric("Total de Registros", len(filtered_data))
        col2.dataframe(filtered_data.head())

        # Gráficos dinâmicos
        st.subheader("📅 Distribuição da Hora de Geração")
        fig, ax = plt.subplots()
        sns.histplot(pd.to_datetime(filtered_data['HH_GERACAO'], format='%H:%M:%S').dt.hour, kde=False, color='blue', ax=ax)
        ax.set_title(f'Distribuição da Hora de Geração - Ano {ano_selecionado}')
        ax.set_xlabel('Hora do Dia')
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

        # Gráfico de distribuição por UF
        st.subheader('🌎 Distribuição por UF de Origem')
        fig, ax = plt.subplots()
        sns.countplot(data=filtered_data, x='SG_UF_ORIGEM', color='blue', ax=ax)
        ax.set_title(f'Distribuição por UF - Ano {ano_selecionado}')
        ax.set_xlabel('UF de Origem')
        ax.set_ylabel('Frequência')
        st.pyplot(fig)

    # Página 2 - Análise por UF e Município
    elif page == "Análise por UF e Município":
        st.subheader("🗺️ Análise por UF e Município")

        # Filtro para selecionar até dois municípios
        municipios_disponiveis = data['NM_MUNICIPIO_ORIGEM'].unique()
        municipios_selecionados = st.sidebar.multiselect(
            'Selecione até 2 municípios',
            municipios_disponiveis,
            max_selections=2
        )

        # Verifica se dois municípios foram selecionados
        if len(municipios_selecionados) == 2:
            filtered_municipios_data = data[data['NM_MUNICIPIO_ORIGEM'].isin(municipios_selecionados)]

            # Dados de contagem por ano para cada município
            municipio_1 = filtered_municipios_data[filtered_municipios_data['NM_MUNICIPIO_ORIGEM'] == municipios_selecionados[0]]
            municipio_2 = filtered_municipios_data[filtered_municipios_data['NM_MUNICIPIO_ORIGEM'] == municipios_selecionados[1]]

            # Cálculo das diferenças percentuais
            count_2020_municipio_1 = len(municipio_1[municipio_1['Ano'] == 2020])
            count_2024_municipio_1 = len(municipio_1[municipio_1['Ano'] == 2024])
            diff_percent_1 = ((count_2024_municipio_1 - count_2020_municipio_1) / count_2020_municipio_1) * 100 if count_2020_municipio_1 != 0 else 0

            count_2020_municipio_2 = len(municipio_2[municipio_2['Ano'] == 2020])
            count_2024_municipio_2 = len(municipio_2[municipio_2['Ano'] == 2024])
            diff_percent_2 = ((count_2024_municipio_2 - count_2020_municipio_2) / count_2020_municipio_2) * 100 if count_2020_municipio_2 != 0 else 0

            # Gráficos de pizza com anotação de diferença percentual
            st.subheader(f'Distribuição de Transferências - {municipios_selecionados[0]}')
            fig, ax = plt.subplots()
            ax.pie(
                [count_2020_municipio_1, count_2024_municipio_1],
                labels=['2020', '2024'],
                autopct='%1.1f%%',
                startangle=140,
                colors=['#3498db', '#e74c3c']
            )
            ax.set_title(f'Transferências - {municipios_selecionados[0]} (Variação: {diff_percent_1:.2f}%)')
            st.pyplot(fig)

            st.subheader(f'Distribuição de Transferências - {municipios_selecionados[1]}')
            fig, ax = plt.subplots()
            ax.pie(
                [count_2020_municipio_2, count_2024_municipio_2],
                labels=['2020', '2024'],
                autopct='%1.1f%%',
                startangle=140,
                colors=['#3498db', '#e74c3c']
            )
            ax.set_title(f'Transferências - {municipios_selecionados[1]} (Variação: {diff_percent_2:.2f}%)')
            st.pyplot(fig)
        else:
            st.warning("Selecione exatamente 2 municípios para visualizar a análise.")

else:
    st.warning("Por favor, carregue os dois arquivos de dataset (2020 e 2024) para continuar.")
