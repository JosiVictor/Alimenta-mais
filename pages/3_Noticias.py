import requests
import streamlit as st

from alimenta import coleta, config, dados

st.set_page_config(page_title="Notícias | Alimenta+", page_icon="📰", layout="wide")
st.title("📰 Notícias sobre alimentos")

uf = st.selectbox("Estado", sorted(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}")

if st.button("🔄 Buscar notícias agora"):
    try:
        novas = coleta.buscar_noticias(uf)
        qtd = dados.salvar_noticias(novas)
        st.success(f"{qtd} notícia(s) nova(s) salva(s) em Data/noticias.csv.")
    except (requests.RequestException, ValueError):
        st.warning("Não foi possível buscar as notícias agora. Mostrando as já salvas.")

noticias = dados.carregar_noticias(uf=uf)

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
