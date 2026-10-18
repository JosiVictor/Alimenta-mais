import streamlit as st

from alimenta import config, dados

st.set_page_config(page_title="Mapa | Alimenta+", page_icon="🗺️", layout="wide")
st.title("🗺️ Mapa de pontos")
st.write("Centrais de abastecimento (**excedente**) e pontos de **doação** cadastrados com coordenadas.")

pontos = dados.carregar_pontos()

col_uf, col_tipo = st.columns(2)
uf = col_uf.selectbox("Estado", ["Todos"] + sorted(config.ESTADOS))
tipos = col_tipo.multiselect("Mostrar", config.TIPOS, default=config.TIPOS)

filtrados = dados.filtrar_pontos(pontos, uf=None if uf == "Todos" else uf, tipos=tipos)

if filtrados.empty:
    st.info("Nenhum ponto encontrado para esse filtro.")
else:
    cores = {"Excedente": "#E4572E", "Doação": "#2E9E5B"}
    mapa = filtrados.assign(cor=filtrados["Tipo"].map(cores))
    st.map(mapa, latitude="lat", longitude="lon", color="cor", size=20000)
    st.caption("🟠 Excedente   🟢 Doação")
    st.dataframe(
        filtrados[["Nome", "Tipo", "UF", "Site"]],
        hide_index=True,
        use_container_width=True,
        column_config={"Site": st.column_config.LinkColumn("Site")},
    )
