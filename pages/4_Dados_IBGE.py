import pandas as pd
import requests
import streamlit as st

from alimenta import coleta, config, dados

st.set_page_config(page_title="Dados IBGE | Alimenta+", page_icon="📊", layout="wide")
st.title("📊 Dados IBGE")


@st.cache_data(ttl=24 * 3600, show_spinner="Consultando o IBGE...")
def municipios_do_estado(uf: str) -> pd.DataFrame:
    return coleta.resumir_municipios(coleta.buscar_municipios(uf))


def ranking_mesorregioes(municipios: pd.DataFrame) -> pd.DataFrame:
    ranking = municipios["Mesorregião"].value_counts().rename_axis("Mesorregião").reset_index(name="Municípios")
    ranking["% do estado"] = (ranking["Municípios"] / len(municipios) * 100).round(1)
    return ranking


uf = st.selectbox("Estado", sorted(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}")
nome_estado = config.ESTADOS[uf]
orgs = dados.filtrar_organizacoes(dados.carregar_organizacoes(), uf=uf)

try:
    municipios = municipios_do_estado(uf)
    ranking = ranking_mesorregioes(municipios)

    col1, col2, col3 = st.columns(3)
    col1.metric("Municípios", len(municipios))
    col2.metric("Mesorregiões", len(ranking))
    col3.metric("Organizações (inclui nacionais)", len(orgs))

    st.subheader(f"Como os municípios de {nome_estado} se distribuem pelo território")
    st.write(
        "O IBGE agrupa os municípios de cada estado em **mesorregiões**: grandes áreas vizinhas, "
        "com características econômicas e sociais parecidas. A tabela abaixo mostra **quantos municípios "
        "existem em cada mesorregião**. Para o Alimenta+, isso ajuda a ver onde está a maior parte das cidades "
        "do estado e, portanto, onde pode haver mais gente a ser alcançada por doações."
    )

    topo = ranking.iloc[0]
    st.info(
        f"Em {nome_estado}, a mesorregião com mais municípios é **{topo['Mesorregião']}**: "
        f"{topo['Municípios']} dos {len(municipios)} municípios do estado ({topo['% do estado']}%)."
    )

    st.dataframe(
        ranking,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Municípios": st.column_config.ProgressColumn(
                "Municípios", format="%d", min_value=0, max_value=int(ranking["Municípios"].max())
            ),
            "% do estado": st.column_config.NumberColumn("% dos municípios do estado", format="%.1f%%"),
        },
    )
    if (ranking["Mesorregião"] == "Não informada").any():
        st.caption("“Não informada”: o IBGE não retornou a mesorregião desses municípios.")

    with st.expander("O que é mesorregião e de onde vêm esses dados?"):
        st.markdown(
            "- **Mesorregião:** divisão regional do IBGE que reúne várias microrregiões (e, dentro delas, municípios) "
            "de uma mesma parte do estado. É uma divisão mais antiga: o IBGE hoje também usa as *regiões "
            "geográficas intermediárias*, mas as mesorregiões ainda aparecem em muitas bases.\n"
            "- **Fonte:** API de Localidades do IBGE, consultada ao abrir esta página (o resultado fica em cache por 24 horas).\n"
        )
    with st.expander("Ver lista completa de municípios"):
        st.dataframe(municipios, hide_index=True, use_container_width=True)
except (requests.RequestException, ValueError):
    guardado = dados.carregar_municipios_por_uf()
    linha = guardado[guardado["UF"] == uf]
    st.warning("Não foi possível consultar o IBGE agora.")
    if not linha.empty:
        st.metric("Municípios (último valor salvo)", linha.iloc[0]["Municípios"])

st.divider()
st.subheader("Panorama da base por estado")
base = dados.carregar_organizacoes()
base = base[base["UF"] != config.NACIONAL]
if base.empty:
    st.info("Sem organizações estaduais cadastradas.")
else:
    st.bar_chart(base.groupby(["UF", "Tipo"]).size().unstack(fill_value=0))
