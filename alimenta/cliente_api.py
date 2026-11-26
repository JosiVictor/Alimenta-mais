"""Cliente da API do Alimenta+: é por aqui que o app Streamlit lê e grava os dados.

O endereço da API pode ser trocado com a variável de ambiente ALIMENTA_API_URL
(padrão: http://localhost:8000).
"""
import os

import pandas as pd
import requests

from . import config

API_URL = os.getenv("ALIMENTA_API_URL", "http://localhost:8000").rstrip("/")

_ORGANIZACOES = {"nome": "Nome", "tipo": "Tipo", "uf": "UF", "como_ajudar": "Como ajudar", "site": "Site"}
_PONTOS = {"nome": "Nome", "tipo": "Tipo", "uf": "UF", "site": "Site", "lat": "lat", "lon": "lon"}
_NOTICIAS = {"uf": "UF", "titulo": "Título", "fonte": "Fonte", "data": "Data", "link": "Link"}
_MUNICIPIOS = {"municipio": "Município", "mesorregiao": "Mesorregião", "microrregiao": "Microrregião"}
_COLUNAS_MUNICIPIOS = ["Município", "Mesorregião", "Microrregião"]
_RESUMOS = {
    "uf": "UF", "estilo": "Estilo", "resumo": "Resumo", "modelo": "Modelo",
    "noticias_usadas": "Notícias", "gerado_em": "Gerado em", "tempo_segundos": "Tempo (s)",
}


class ApiIndisponivel(Exception):
    """A API não respondeu (provavelmente não está rodando)."""


class ApiErro(Exception):
    """A API respondeu com erro (ex.: 409 organização repetida, 422 dado inválido)."""

    def __init__(self, status: int, detalhe: str):
        super().__init__(detalhe)
        self.status = status
        self.detalhe = detalhe


def _requisitar(metodo: str, caminho: str, timeout: float = 30, **kwargs):
    return requests.request(metodo, f"{API_URL}{caminho}", timeout=timeout, **kwargs)


def _detalhe(resposta) -> str:
    try:
        detalhe = resposta.json().get("detail", "")
    except ValueError:
        detalhe = ""
    if isinstance(detalhe, list):
        detalhe = "; ".join(str(d.get("msg", "")).removeprefix("Value error, ") for d in detalhe)
    return str(detalhe) or f"Erro {resposta.status_code} na API."


def _chamar(metodo: str, caminho: str, **kwargs):
    try:
        resposta = _requisitar(metodo, caminho, **kwargs)
    except requests.RequestException as erro:
        raise ApiIndisponivel(f"Sem resposta da API em {API_URL}") from erro
    if resposta.status_code >= 400:
        raise ApiErro(resposta.status_code, _detalhe(resposta))
    return resposta.json()


def _tabela(registros: list[dict], mapa: dict, colunas: list[str]) -> pd.DataFrame:
    if not registros:
        return pd.DataFrame(columns=colunas)
    return pd.DataFrame(registros).rename(columns=mapa)[colunas]


def _filtro_tipo(tipos: list[str] | None) -> dict:
    """A API filtra por um tipo só; com os dois tipos (ou nenhum) não se filtra."""
    return {"tipo": tipos[0]} if tipos and len(tipos) == 1 else {}


def saude() -> bool:
    return _chamar("GET", "/health").get("status") == "ok"


def organizacoes(uf: str | None = None, tipos: list[str] | None = None, incluir_nacional: bool = True) -> pd.DataFrame:
    params = {"incluir_nacional": str(incluir_nacional).lower(), **_filtro_tipo(tipos)}
    if uf:
        params["uf"] = uf
    return _tabela(_chamar("GET", "/organizacoes", params=params), _ORGANIZACOES, config.COLUNAS_ORGANIZACOES)


def criar_organizacao(nome: str, tipo: str, uf: str, como_ajudar: str = "", site: str = "") -> dict:
    corpo = {"nome": nome, "tipo": tipo, "uf": uf, "como_ajudar": como_ajudar, "site": site}
    return _chamar("POST", "/organizacoes", json=corpo)


def importar_organizacoes(novas: pd.DataFrame) -> tuple[int, int]:
    """Cadastra cada linha do CSV pela API. Retorna (adicionadas, ignoradas)."""
    faltando = [c for c in ("Nome", "Tipo", "UF") if c not in novas.columns]
    if faltando:
        raise ValueError(f"O CSV precisa ter as colunas Nome, Tipo e UF (faltando: {', '.join(faltando)}).")
    adicionadas = ignoradas = 0
    for _, linha in novas.fillna("").iterrows():
        try:
            criar_organizacao(
                str(linha["Nome"]), str(linha["Tipo"]), str(linha["UF"]),
                str(linha.get("Como ajudar", "")), str(linha.get("Site", "")),
            )
            adicionadas += 1
        except ApiErro:
            ignoradas += 1
    return adicionadas, ignoradas


def pontos(uf: str | None = None, tipos: list[str] | None = None) -> pd.DataFrame:
    params = _filtro_tipo(tipos)
    if uf:
        params["uf"] = uf
    return _tabela(_chamar("GET", "/pontos", params=params), _PONTOS, config.COLUNAS_PONTOS)


def noticias(uf: str | None = None, limite: int = 1000) -> pd.DataFrame:
    params = {"limite": limite}
    if uf:
        params["uf"] = uf
    return _tabela(_chamar("GET", "/noticias", params=params), _NOTICIAS, config.COLUNAS_NOTICIAS)


def coletar_noticias(uf: str) -> int:
    """Pede à API para buscar notícias novas do estado. Retorna quantas eram inéditas."""
    return _chamar("POST", "/noticias/coletar", params={"uf": uf})["novas"]


def municipios(uf: str) -> pd.DataFrame:
    return _tabela(_chamar("GET", f"/municipios/{uf}"), _MUNICIPIOS, _COLUNAS_MUNICIPIOS)


# ------------------------------------------------------------------ LLM local
def status_modelo() -> dict:
    return _chamar("GET", "/modelo")


def carregar_modelo() -> dict:
    """Pede à API para carregar o modelo (a primeira vez baixa o modelo e pode levar minutos)."""
    return _chamar("POST", "/modelo/carregar", timeout=900)


def processar_texto(texto: str, tarefa: str = "resumo", pergunta: str | None = None, max_novos_tokens: int = 150,
                    estilo: str = "padrao") -> dict:
    corpo = {"texto": texto, "tarefa": tarefa, "pergunta": pergunta, "max_novos_tokens": max_novos_tokens, "estilo": estilo}
    return _chamar("POST", "/processar_texto", json=corpo, timeout=900)


# --------------------------------------------------------------------- resumos
def gerar_resumo(uf: str, estilo: str = "padrao") -> dict:
    """A API junta as notícias do estado, pede o resumo ao modelo e guarda o resultado."""
    return _chamar("POST", "/resumos/gerar", json={"uf": uf, "estilo": estilo}, timeout=900)


def resumos(uf: str | None = None, limite: int = 100) -> pd.DataFrame:
    params = {"limite": limite}
    if uf:
        params["uf"] = uf
    return _tabela(_chamar("GET", "/resumos", params=params), _RESUMOS, config.COLUNAS_RESUMOS)
