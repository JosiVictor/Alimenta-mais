"""Alimenta+ — página inicial."""
import streamlit as st

from alimenta import dados

st.set_page_config(page_title="Início | Alimenta+", page_icon="🍽️", layout="wide")

st.title("🍽️ Alimenta+")
st.write(
    "O Alimenta+ busca conectar alimentos que são desperdiçados, "
    "com pessoas e organizações que precisam deles."
)

orgs = dados.carregar_organizacoes()
pontos = dados.carregar_pontos()
noticias = dados.carregar_noticias()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Organizações", len(orgs))
c2.metric("Doação", int((orgs["Tipo"] == "Doação").sum()))
c3.metric("Excedente", int((orgs["Tipo"] == "Excedente").sum()))
c4.metric("Notícias coletadas", len(noticias))

st.subheader("Navegue pelo app")
st.page_link("pages/1_Organizacoes.py", label="Organizações: consulta, cadastro e importação", icon="🤝")
st.page_link("pages/2_Mapa.py", label="Mapa dos pontos de doação e excedente", icon="🗺️")
st.page_link("pages/3_Noticias.py", label="Notícias sobre desperdício e doação", icon="📰")
st.page_link("pages/4_Dados_IBGE.py", label="Dados IBGE: municípios e panorama da base", icon="📊")
st.page_link("pages/5_API_e_LLM.py", label="API (FastAPI) e preparação para LLM", icon="🤖")

st.caption("Alimenta+ - ODS 2, ODS 12 e ODS 17")
