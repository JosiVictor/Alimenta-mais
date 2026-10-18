"""Configurações compartilhadas pelo app Streamlit, pela API e pelos scripts."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ESTADOS = {
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
    "PA": "Pará",
}

TIPOS = ["Doação", "Excedente"]
NACIONAL = "Nacional"

COLUNAS_ORGANIZACOES = ["Nome", "Tipo", "UF", "Como ajudar", "Site"]
COLUNAS_PONTOS = ["Nome", "Tipo", "UF", "Site", "lat", "lon"]
COLUNAS_NOTICIAS = ["UF", "Título", "Fonte", "Data", "Link"]
COLUNAS_MUNICIPIOS_UF = ["UF", "Municípios"]

ARQ_ORGANIZACOES = "organizacoes_alimenta_mais.csv"
ARQ_PONTOS = "pontos_alimenta_mais.csv"
ARQ_NOTICIAS = "noticias.csv"
ARQ_MUNICIPIOS_UF = "municipios_por_uf.csv"


def pasta_dados() -> Path:
    """Pasta dos CSVs. Pode ser trocada pela variável ALIMENTA_DATA_DIR (usado nos testes)."""
    pasta = Path(os.getenv("ALIMENTA_DATA_DIR", RAIZ / "Data"))
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta
