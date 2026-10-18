"""Alimenta+ — ponto de entrada (streamlit run app.py). Define o menu de navegação."""
import streamlit as st

st.set_page_config(page_title="Alimenta+", page_icon="🍽️", layout="wide")

navegacao = st.navigation(
    [
        st.Page("pages/0_Inicio.py", title="Início", icon="🏠", default=True),
        st.Page("pages/1_Organizacoes.py", title="Organizações", icon="🤝"),
        st.Page("pages/2_Mapa.py", title="Mapa", icon="🗺️"),
        st.Page("pages/3_Noticias.py", title="Notícias", icon="📰"),
        st.Page("pages/4_Dados_IBGE.py", title="Dados IBGE", icon="📊"),
        st.Page("pages/5_API_e_LLM.py", title="API e LLM", icon="🤖"),
    ]
)
navegacao.run()
