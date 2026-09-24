import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from pathlib import Path

st.set_page_config(page_title="Alimenta+", page_icon="🍽️", layout="wide")

# Pasta para guardar os arquivos
pasta = Path("Data")
pasta.mkdir(exist_ok=True)

# Estados usados no projeto
estados = {
    "SP": "São Paulo",
    "RJ": "Rio de Janeiro",
    "MG": "Minas Gerais",
    "DF": "Distrito Federal",
    "PR": "Paraná",
    "RS": "Rio Grande do Sul",
    "BA": "Bahia",
    "PE": "Pernambuco",
    "CE": "Ceará",
    "AM": "Amazonas",
    "PA": "Pará"
}

# Organizações que já estão cadastradas
organizacoes = [
    ["Banco de Alimentos de São Paulo", "Doação", "SP",
     "Recebe doações de empresas e pessoas físicas.",
     "https://prefeitura.sp.gov.br/web/sesana/w/banco_de_alimentos"],

    ["Banco de Alimentos de Belo Horizonte", "Doação", "MG",
     "Programa municipal que atende instituições cadastradas.",
     "https://prefeitura.pbh.gov.br/seguranca-alimentar-nutricional/equipamentos/banco-de-alimentos"],

    ["Banco de Alimentos de Curitiba", "Doação", "PR",
     "Recebe doações de alimentos.",
     "https://www.curitiba.pr.gov.br"],

    ["Banco Rio de Alimentos (SESC-RJ)", "Doação", "RJ",
     "Recebe doações de empresas e do PAA.",
     "https://www.sesc.com.br/mesabrasil/"],

    ["Banco de Alimentos de Nova Iguaçu", "Doação", "RJ",
     "Banco de alimentos da cidade.",
     ""],

    ["Mesa Brasil SESC", "Doação", "Nacional",
     "Programa presente em vários estados do Brasil.",
     "https://www.sesc.com.br/mesabrasil/"],

    ["Rede Brasileira de Bancos de Alimentos", "Doação", "Nacional",
     "Programa que reúne bancos de alimentos no país.",
     "https://www.gov.br/mds/pt-br/acoes-e-programas/acesso-a-alimentos-e-a-agua/rede-brasileira-de-bancos-de-alimentos"],

    ["Ação da Cidadania", "Doação", "Nacional",
     "ONG que atua no combate à fome.",
     ""],

    ["CEAGESP", "Excedente", "SP", "Central de abastecimento.", "https://www.ceagesp.gov.br"],
    ["CEASA Minas", "Excedente", "MG", "Central de abastecimento.", "https://www.ceasaminas.com.br"],
    ["CEASA Grande Rio", "Excedente", "RJ", "Central de abastecimento.", ""],
    ["CEASA-DF", "Excedente", "DF", "Central de abastecimento.", ""],
    ["CEASA-PR", "Excedente", "PR", "Central de abastecimento.", ""],
    ["CEASA-RS", "Excedente", "RS", "Central de abastecimento.", ""],
    ["CEASA-BA", "Excedente", "BA", "Central de abastecimento.", ""],
    ["CEASA-PE", "Excedente", "PE", "Central de abastecimento.", ""],
    ["CEASA-CE", "Excedente", "CE", "Central de abastecimento.", ""]
]

colunas = ["Nome", "Tipo", "UF", "Como ajudar", "Site"]
df = pd.DataFrame(organizacoes, columns=colunas)

# Guarda organizações adicionadas pelo usuário
if "extras" not in st.session_state:
    st.session_state.extras = pd.DataFrame(columns=colunas)

df = pd.concat([df, st.session_state.extras], ignore_index=True)

st.title("🍽️ Alimenta+")

st.write(
    "O Alimenta+ busca conectar alimentos que poderiam ser desperdiçados "
    "com pessoas e organizações que precisam deles."
)

st.write("Escolha um estado para ver as organizações e as notícias relacionadas.")

# Escolha do estado
uf = st.selectbox("Escolha um estado:", sorted(estados.keys()))
nome_estado = estados[uf]

# Filtro
filtros = st.multiselect(
    "Mostrar:",
    ["Doação", "Excedente"],
    default=["Doação", "Excedente"]
)

# Mostra as organizações
if filtros:
    resultado = df[df["Tipo"].isin(filtros)]
else:
    resultado = df.iloc[0:0]

resultado = resultado[
    (resultado["UF"] == uf) | (resultado["UF"] == "Nacional")
]

st.header("🤝 Organizações")

if len(resultado) == 0:
    st.info("Nenhuma organização encontrada.")
else:
    st.dataframe(
        resultado,
        hide_index=True,
        column_config={"Site": st.column_config.LinkColumn("Site")}
    )

st.divider()

# Consulta os municípios do estado no IBGE
st.header("📊 Dados do estado")

try:
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    resposta = requests.get(url, timeout=10)
    municipios = resposta.json()

    col1, col2 = st.columns(2)
    col1.metric("Municípios", len(municipios))
    col2.metric("Organizações encontradas", len(resultado))

    st.write(
        f"O estado de {nome_estado} possui {len(municipios)} municípios "
        f"e o Alimenta+ encontrou {len(resultado)} organizações na base."
    )

except:
    st.warning("Não foi possível consultar os dados do IBGE agora.")

st.divider()

# Busca notícias
st.header("📰 Notícias sobre alimentos")

try:
    termo = quote(f"desperdício alimentos doação {nome_estado}")
    url = (
        f"https://news.google.com/rss/search?q={termo}"
        "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    )

    resposta = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10
    )

    soup = BeautifulSoup(resposta.content, "xml")
    noticias = soup.find_all("item")[:8]

    dados = []

    for noticia in noticias:
        dados.append({
            "Título": noticia.title.get_text(strip=True),
            "Fonte": noticia.source.get_text(strip=True) if noticia.source else "",
            "Data": noticia.pubDate.get_text(strip=True) if noticia.pubDate else "",
            "Link": noticia.link.get_text(strip=True) if noticia.link else ""
        })

    noticias_df = pd.DataFrame(dados)

    if len(noticias_df) > 0:
        st.dataframe(
            noticias_df,
            hide_index=True,
            column_config={"Link": st.column_config.LinkColumn("Link")}
        )
    else:
        st.info("Nenhuma notícia encontrada.")

except:
    st.warning("Não foi possível buscar as notícias agora.")

st.divider()

# Adicionar uma organização
st.header("➕ Adicionar organização")

with st.form("nova_organizacao"):
    nome = st.text_input("Nome")
    tipo = st.selectbox("Tipo", ["Doação", "Excedente"])
    estado = st.selectbox(
        "Estado",
        ["Nacional"] + sorted(estados.keys())
    )
    site = st.text_input("Site")
    ajuda = st.text_input("Como ajudar")

    adicionar = st.form_submit_button("Adicionar")

if adicionar:
    if nome.strip() == "":
        st.error("Digite o nome da organização.")
    else:
        nova = pd.DataFrame([{
            "Nome": nome,
            "Tipo": tipo,
            "UF": estado,
            "Como ajudar": ajuda,
            "Site": site
        }])

        st.session_state.extras = pd.concat(
            [st.session_state.extras, nova],
            ignore_index=True
        )

        st.success("Organização adicionada!")
        st.rerun()

st.divider()

# Importar CSV
st.header("📁 Importar organizações")

arquivo_csv = st.file_uploader("Escolha um arquivo CSV", type="csv")

if arquivo_csv:
    try:
        novo = pd.read_csv(arquivo_csv)

        if "Nome" not in novo.columns or "Tipo" not in novo.columns or "UF" not in novo.columns:
            st.error("O CSV precisa ter as colunas Nome, Tipo e UF.")
        else:
            if "Como ajudar" not in novo.columns:
                novo["Como ajudar"] = ""

            if "Site" not in novo.columns:
                novo["Site"] = ""

            novo = novo[colunas]

            st.session_state.extras = pd.concat(
                [st.session_state.extras, novo],
                ignore_index=True
            )

            st.success(f"{len(novo)} organização(ões) adicionada(s).")
            st.rerun()

    except:
        st.error("Não foi possível ler o arquivo.")

# Baixar a base
arquivo = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Baixar base em CSV",
    arquivo,
    "organizacoes_alimenta_mais.csv",
    "text/csv"
)

df.to_csv(pasta / "organizacoes_alimenta_mais.csv", index=False)

st.caption("Alimenta+ - ODS 2, ODS 12 e ODS 17")
