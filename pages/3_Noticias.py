import streamlit as st

from alimenta import cliente_api, config

st.set_page_config(page_title="Notícias | Alimenta+", page_icon="📰", layout="wide")
st.title("📰 Notícias sobre alimentos")

uf = st.selectbox("Estado", sorted(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}")

if st.button("🔄 Buscar notícias agora"):
    try:
        qtd = cliente_api.coletar_noticias(uf)
        st.success(f"{qtd} notícia(s) nova(s) salva(s) em Data/noticias.csv.")
    except cliente_api.ApiErro as erro:
        st.warning(f"{erro.detalhe} Mostrando as notícias já salvas.")

noticias = cliente_api.noticias(uf=uf)

if noticias.empty:
    st.info("Nenhuma notícia salva para esse estado ainda. Clique em “Buscar notícias agora”.")
else:
    st.dataframe(
        noticias[["Título", "Fonte", "Data", "Link"]],
        hide_index=True,
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn("Link")},
    )
    st.download_button(
        "⬇️ Baixar notícias em CSV",
        noticias.to_csv(index=False).encode("utf-8"),
        f"noticias_{uf}.csv",
        "text/csv",
    )
