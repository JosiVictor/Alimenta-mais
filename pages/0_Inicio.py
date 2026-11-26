"""Alimenta+ — página inicial."""
import streamlit as st

from alimenta import cliente_api

st.set_page_config(page_title="Início | Alimenta+", page_icon="🍽️", layout="wide")

st.title("🍽️ Alimenta+")
st.subheader("Comida que sobra não deveria virar lixo. Deveria chegar a quem precisa.")
st.write(
    "Todo dia, alimentos bons para consumo são jogados fora, enquanto muita gente passa fome. "
    "O **Alimenta+** reúne em um só lugar **quem recebe doações**, **quem tem excedente para doar** e "
    "**o que está sendo noticiado** sobre desperdício em cada estado, para facilitar que o alimento "
    "chegue a quem precisa antes de se perder."
)

orgs = cliente_api.organizacoes()
noticias = cliente_api.noticias()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Organizações cadastradas", len(orgs))
c2.metric("Recebem doações", int((orgs["Tipo"] == "Doação").sum()))
c3.metric("Têm excedente", int((orgs["Tipo"] == "Excedente").sum()))
c4.metric("Notícias coletadas", len(noticias))

st.divider()

with st.container(border=True):
    st.markdown("### 🥕 Tenho alimentos para doar")
    st.write("Encontre um banco de alimentos ou uma organização perto de você e veja como ajudar.")
    col_a, col_b = st.columns(2)
    col_a.page_link("pages/1_Organizacoes.py", label="Ver organizações", icon="🤝")
    col_b.page_link("pages/2_Mapa.py", label="Ver no mapa", icon="🗺️")

with st.container(border=True):
    st.markdown("### 🤝 Represento uma organização")
    st.write("Cadastre a sua organização ou importe uma lista inteira de uma vez (CSV), para ser encontrada por quem quer doar.")
    st.page_link("pages/1_Organizacoes.py", label="Cadastrar organização", icon="➕")

with st.container(border=True):
    st.markdown("### 🏛️ Sou gestor ou pesquisador")
    st.write(
        "Acompanhe notícias por estado, veja os dados do IBGE e descubra em quais estados "
        "faltam organizações, com resumos escritos por IA."
    )
    col_a, col_b, col_c = st.columns(3)
    col_a.page_link("pages/3_Noticias.py", label="Notícias por estado", icon="📰")
    col_b.page_link("pages/4_Dados_IBGE.py", label="Dados do IBGE", icon="📊")
    col_c.page_link("pages/5_API_e_LLM.py", label="Assistente com IA", icon="🤖")


st.caption("Alimenta+ · ODS 2 (Fome Zero), ODS 12 (Consumo e Produção Responsáveis) e ODS 17 (Parcerias)")
