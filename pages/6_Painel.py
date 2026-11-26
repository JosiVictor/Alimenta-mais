import pandas as pd
import streamlit as st

from alimenta import cliente_api, config

st.set_page_config(page_title="Painel | Alimenta+", page_icon="📈", layout="wide")
st.title("📈 Painel")


def coletar_todos_os_estados() -> tuple[int, list[str]]:
    estados = list(config.ESTADOS)
    barra = st.progress(0.0, text="Começando...")
    novas, falhas = 0, []
    for i, uf in enumerate(estados):
        barra.progress(i / len(estados), text=f"Buscando notícias: {config.ESTADOS[uf]} ({i + 1}/{len(estados)})")
        try:
            novas += cliente_api.coletar_noticias(uf)
        except (cliente_api.ApiErro, cliente_api.ApiIndisponivel):
            falhas.append(uf)
    barra.progress(1.0, text="Pronto!")
    return novas, falhas


with st.container(border=True):
    st.markdown("**Atualizar os dados do painel**")
    st.caption("Busca as notícias dos 11 estados")
    if st.button("🔄 Buscar notícias de todos os estados"):
        novas, falhas = coletar_todos_os_estados()
        st.session_state["aviso_coleta"] = (novas, falhas)
        st.rerun()
    if "aviso_coleta" in st.session_state:
        novas, falhas = st.session_state["aviso_coleta"]
        st.success(f"Coleta concluída: {novas} notícia(s) nova(s).")
        if falhas:
            st.warning("Não foi possível buscar: " + ", ".join(falhas) + ". Tente de novo mais tarde.")

orgs = cliente_api.organizacoes()
pontos = cliente_api.pontos()
noticias = cliente_api.noticias()
noticias_estado = noticias[noticias["UF"].isin(config.ESTADOS)]
orgs_estado = orgs[orgs["UF"].isin(config.ESTADOS)]

# ------------------------------------------------------------ 1. caminho dos dados
st.subheader("1. O caminho dos dados")
c1, c2, c3, c4 = st.columns(4)
c1.metric("1. Coleta de notícias", len(noticias_estado), f"{len(orgs)} organizações", delta_color="off")
c2.metric("2. Pontos no mapa (sem repetições)", len(pontos))
c3.metric("3. Estados com notícias", noticias_estado["UF"].nunique(), f"{orgs_estado['UF'].nunique()} com organizações", delta_color="off")
resumos_todos = cliente_api.resumos()
c4.metric("4. Resumos gerados pela IA", len(resumos_todos))
st.caption(
    "Coleta: API do IBGE e feed de notícias, guardados em CSV.\n\n"
    "Preparação: validação e remoção de repetidos.\n\n"
    "Análise: cobertura por estado.\n\n"
    "IA: resumo das notícias com um modelo que roda no próprio computador."
)

# ------------------------------------------------------------ 2. os dados
st.subheader("2. Os dados coletados")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Organizações por estado e tipo**")
    por_estado = orgs[orgs["UF"] != config.NACIONAL]
    if por_estado.empty:
        st.info("Sem organizações estaduais.")
    else:
        st.bar_chart(por_estado.groupby(["UF", "Tipo"]).size().unstack(fill_value=0))
with col_b:
    st.markdown("**Notícias coletadas por estado**")
    if noticias_estado.empty:
        st.info("Ainda não há notícias com estado. Colete na página Notícias.")
    else:
        st.bar_chart(noticias_estado.groupby("UF").size())

st.markdown("**Fontes que mais aparecem nas notícias**")
fontes = noticias["Fonte"].replace("", pd.NA).dropna().value_counts().head(8)
if fontes.empty:
    st.info("Sem fontes para mostrar.")
else:
    st.bar_chart(fontes)

# ------------------------------------------------------------ 3. insight de cobertura
st.subheader("3. Insight: onde falta organização?")
st.write(
    "Aqui cruzamos dois dados de cada estado: **quantas notícias** sobre desperdício e doação foram coletadas "
    "(sinal de que o assunto está em evidência) e **quantas organizações** estão cadastradas. "
    "Estado com muita notícia e nenhuma organização é um lugar onde vale procurar parceiros."
)

cobertura = pd.DataFrame({"UF": list(config.ESTADOS)})
cobertura["Estado"] = cobertura["UF"].map(config.ESTADOS)
cobertura["Organizações"] = cobertura["UF"].map(orgs_estado.groupby("UF").size()).fillna(0).astype(int)
cobertura["Notícias"] = cobertura["UF"].map(noticias_estado.groupby("UF").size()).fillna(0).astype(int)


def situacao(linha) -> str:
    if linha["Notícias"] == 0:
        return "Sem notícias coletadas"
    if linha["Organizações"] == 0:
        return "⚠️ Sem organização cadastrada"
    return "Com organização"


cobertura["Situação"] = cobertura.apply(situacao, axis=1)

if cobertura["Notícias"].sum() == 0:
    st.info("Ainda não há notícias. Clique em “Buscar notícias de todos os estados” no topo da página.")
else:
    col_f1, col_f2 = st.columns(2)
    escolhidos = col_f1.multiselect(
        "Estados", list(config.ESTADOS), default=list(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}"
    )
    filtro = col_f2.radio(
        "Mostrar", ["Todos", "⚠️ Sem organização cadastrada", "Com organização"], horizontal=True
    )
    visao = cobertura[cobertura["UF"].isin(escolhidos)]
    if filtro != "Todos":
        visao = visao[visao["Situação"] == filtro]

    sem_org = cobertura[cobertura["Situação"] == "⚠️ Sem organização cadastrada"]
    if not sem_org.empty:
        st.warning(
            "Estados com notícias sobre o tema, mas **sem organização estadual cadastrada**: "
            + ", ".join(sem_org["Estado"])
            + ". É onde vale buscar novas organizações para a base."
        )
    else:
        st.success("Todos os estados com notícias já têm ao menos uma organização cadastrada.")

    ordenada = visao.sort_values(["Organizações", "Notícias"], ascending=[True, False])
    st.dataframe(ordenada.drop(columns="UF"), hide_index=True, use_container_width=True)
    st.bar_chart(ordenada.set_index("Estado")[["Notícias", "Organizações"]])


# ------------------------------------------------------------ 4. resumo com IA
st.subheader("4. Resumo das notícias com IA")
st.write("O modelo local lê as manchetes salvas do estado e escreve um resumo. Você escolhe para quem o resumo é escrito.")

ROTULOS = {"padrao": "Resumo padrão (3 frases)", "gestor": "Para o gestor público", "topicos": "Em tópicos"}
col_uf, col_estilo = st.columns(2)
uf = col_uf.selectbox("Estado", sorted(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}", key="painel_uf")
estilo = col_estilo.radio("Estilo do resumo", list(ROTULOS), format_func=ROTULOS.get, horizontal=True)

do_estado = noticias_estado[noticias_estado["UF"] == uf]
if do_estado.empty:
    st.info(f"Não há notícias salvas para {config.ESTADOS[uf]}. Colete antes na página Notícias.")
else:
    with st.expander(f"Manchetes que serão resumidas ({min(len(do_estado), 12)} de {len(do_estado)})"):
        for titulo in do_estado["Título"].head(12):
            st.write(f"- {titulo}")

if st.button("✨ Gerar resumo com o modelo local", disabled=do_estado.empty):
    try:
        with st.spinner("Gerando... Na primeira vez o modelo é baixado e pode levar vários minutos."):
            resultado = cliente_api.gerar_resumo(uf, estilo)
    except cliente_api.ApiErro as erro:
        st.error(f"Erro {erro.status}: {erro.detalhe}")
    else:
        st.success(resultado["resumo"])
        st.caption(f"{resultado['modelo']} · {resultado['noticias_usadas']} notícias · {resultado['tempo_segundos']} segundos")

historico = cliente_api.resumos(limite=50)
st.markdown("**Resumos já gerados**")
if historico.empty:
    st.info("Nenhum resumo gerado ainda.")
else:
    st.dataframe(historico, hide_index=True, use_container_width=True)
    st.download_button("⬇️ Baixar resumos em CSV", historico.to_csv(index=False).encode("utf-8"), "resumos_alimenta_mais.csv", "text/csv")

st.caption("Alimenta+ contribui para o ODS 2 (Fome Zero) e o ODS 12 (Consumo e Produção Responsáveis, meta 12.3).")
