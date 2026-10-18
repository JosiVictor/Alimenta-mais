"""Coleta de dados externos: API de localidades do IBGE e notícias (RSS do Google News + BeautifulSoup)."""
from urllib.parse import quote

import pandas as pd
import requests
from bs4 import BeautifulSoup

from . import config

URL_IBGE_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
URL_NOTICIAS = "https://news.google.com/rss/search?q={termo}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
CABECALHOS = {"User-Agent": "Mozilla/5.0 (Alimenta+ - projeto academico)"}


def buscar_municipios(uf: str, timeout: int = 10) -> list[dict]:
    resposta = requests.get(URL_IBGE_MUNICIPIOS.format(uf=uf), timeout=timeout)
    resposta.raise_for_status()
    return resposta.json()


def _nome_aninhado(municipio: dict, *caminho: str) -> str:
    atual = municipio
    for chave in caminho:
        if not isinstance(atual, dict):
            return "Não informada"
        atual = atual.get(chave)
    return atual if isinstance(atual, str) else "Não informada"


def resumir_municipios(municipios: list[dict]) -> pd.DataFrame:
    linhas = [
        {
            "Município": m.get("nome", ""),
            "Mesorregião": _nome_aninhado(m, "microrregiao", "mesorregiao", "nome"),
            "Microrregião": _nome_aninhado(m, "microrregiao", "nome"),
        }
        for m in municipios
    ]
    return pd.DataFrame(linhas, columns=["Município", "Mesorregião", "Microrregião"])


def buscar_noticias(uf: str, limite: int = 8, timeout: int = 10) -> pd.DataFrame:
    nome_estado = config.ESTADOS[uf]
    termo = quote(f"desperdício alimentos doação {nome_estado}")
    resposta = requests.get(URL_NOTICIAS.format(termo=termo), headers=CABECALHOS, timeout=timeout)
    resposta.raise_for_status()
    return interpretar_rss(resposta.content, uf, limite)


def interpretar_rss(conteudo: bytes, uf: str, limite: int = 8) -> pd.DataFrame:
    sopa = BeautifulSoup(conteudo, "xml")
    linhas = []
    for item in sopa.find_all("item")[:limite]:
        def texto(tag: str) -> str:
            elemento = item.find(tag)
            return elemento.get_text(strip=True) if elemento else ""

        linhas.append(
            {
                "UF": uf,
                "Título": texto("title"),
                "Fonte": texto("source"),
                "Data": texto("pubDate"),
                "Link": texto("link"),
            }
        )
    return pd.DataFrame(linhas, columns=config.COLUNAS_NOTICIAS)
