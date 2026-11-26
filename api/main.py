"""API do Alimenta+ (FastAPI).

Como rodar:  uvicorn api.main:app --reload
Documentação interativa: http://localhost:8000/docs
"""
import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Literal

import requests
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator, model_validator

from alimenta import coleta, config, dados, llm_local, llm_prep

app = FastAPI(
    title="API Alimenta+",
    description="Consulta e cadastro de organizações de doação e centrais de excedente de alimentos.",
    version="1.3.0",
)

Tipo = Literal["Doação", "Excedente"]
Tarefa = Literal["resumo", "pergunta_resposta"]
Estilo = Literal["padrao", "gestor", "topicos"]

logger = logging.getLogger("alimenta.api")

# Tempo máximo (em segundos) esperando o modelo local responder.
TIMEOUT_LLM = float(os.getenv("ALIMENTA_TIMEOUT_LLM", "180"))


class OrganizacaoIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120, examples=["Banco de Alimentos de Recife"])
    tipo: Tipo
    uf: str = Field(examples=["PE"], description="Sigla do estado ou 'Nacional'.")
    como_ajudar: str = Field(default="", max_length=300)
    site: str = Field(default="", max_length=300)

    @field_validator("uf")
    @classmethod
    def validar_uf(cls, valor: str) -> str:
        return dados.normalizar_uf(valor)

    @field_validator("nome")
    @classmethod
    def limpar_nome(cls, valor: str) -> str:
        return valor.strip()


class Organizacao(OrganizacaoIn):
    pass


class Ponto(BaseModel):
    nome: str
    tipo: Tipo
    uf: str
    site: str
    lat: float
    lon: float


class Noticia(BaseModel):
    uf: str
    titulo: str
    fonte: str
    data: str
    link: str


class Municipio(BaseModel):
    municipio: str
    mesorregiao: str
    microrregiao: str


class ResultadoColeta(BaseModel):
    uf: str
    novas: int


def _validar_uf_estado(uf: str) -> str:
    """Aceita só estados do projeto (sem 'Nacional')."""
    uf = _validar_uf_consulta(uf)
    if uf == config.NACIONAL:
        raise HTTPException(status_code=422, detail="Informe a sigla de um estado.")
    return uf


def _validar_uf_consulta(uf: str | None) -> str | None:
    if uf is None:
        return None
    try:
        return dados.normalizar_uf(uf)
    except ValueError as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro


@app.get("/health", tags=["Geral"], summary="Verifica se a API está no ar")
def health() -> dict:
    return {"status": "ok"}


@app.get("/organizacoes", response_model=list[Organizacao], tags=["Organizações"],
         summary="Lista organizações (GET)")
def listar_organizacoes(
    uf: str | None = Query(default=None, description="Filtra por UF (ex.: SP)."),
    tipo: Tipo | None = Query(default=None, description="Doação ou Excedente."),
    incluir_nacional: bool = Query(default=True, description="Inclui organizações de atuação nacional ao filtrar por UF."),
) -> list[dict]:
    uf = _validar_uf_consulta(uf)
    df = dados.filtrar_organizacoes(
        dados.carregar_organizacoes(), uf=uf, tipos=[tipo] if tipo else None, incluir_nacional=incluir_nacional
    )
    df = df.rename(columns={"Nome": "nome", "Tipo": "tipo", "UF": "uf", "Como ajudar": "como_ajudar", "Site": "site"})
    return df.to_dict(orient="records")


@app.post("/organizacoes", response_model=Organizacao, status_code=status.HTTP_201_CREATED,
          tags=["Organizações"], summary="Cadastra uma organização (POST)")
def criar_organizacao(organizacao: OrganizacaoIn) -> dict:
    try:
        dados.adicionar_organizacao(
            organizacao.nome, organizacao.tipo, organizacao.uf, organizacao.como_ajudar, organizacao.site
        )
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro
    return organizacao.model_dump()


@app.get("/pontos", response_model=list[Ponto], tags=["Mapa"], summary="Lista pontos com coordenadas")
def listar_pontos(uf: str | None = None, tipo: Tipo | None = None) -> list[dict]:
    uf = _validar_uf_consulta(uf)
    df = dados.filtrar_pontos(dados.carregar_pontos(), uf=uf, tipos=[tipo] if tipo else None)
    df = df.rename(columns={"Nome": "nome", "Tipo": "tipo", "UF": "uf", "Site": "site"})
    return df.to_dict(orient="records")


@app.get("/noticias", response_model=list[Noticia], tags=["Notícias"],
         summary="Lista notícias já coletadas")
def listar_noticias(uf: str | None = None, limite: int = Query(default=10, ge=1, le=1000)) -> list[dict]:
    uf = _validar_uf_consulta(uf)
    df = dados.carregar_noticias(uf=uf, limite=limite)
    df = df.rename(columns={"Título": "titulo", "Fonte": "fonte", "Data": "data", "Link": "link", "UF": "uf"})
    return df.to_dict(orient="records")


@app.post("/noticias/coletar", response_model=ResultadoColeta, tags=["Notícias"],
          summary="Busca notícias novas de um estado e salva no CSV")
def coletar_noticias(
    uf: str = Query(description="Sigla do estado (ex.: SP)."),
    limite: int = Query(default=8, ge=1, le=30),
) -> dict:
    uf = _validar_uf_estado(uf)
    try:
        novas = coleta.buscar_noticias(uf, limite=limite)
    except requests.RequestException as erro:
        raise HTTPException(status_code=502, detail="Não foi possível buscar as notícias agora.") from erro
    return {"uf": uf, "novas": dados.salvar_noticias(novas)}


@app.get("/municipios/{uf}", response_model=list[Municipio], tags=["IBGE"],
         summary="Municípios do estado, com mesorregião e microrregião (API do IBGE)")
def listar_municipios(uf: str) -> list[dict]:
    uf = _validar_uf_estado(uf)
    try:
        brutos = coleta.buscar_municipios(uf)
    except requests.RequestException as erro:
        raise HTTPException(status_code=502, detail="Não foi possível consultar o IBGE agora.") from erro
    tabela = coleta.resumir_municipios(brutos)
    tabela = tabela.rename(columns={"Município": "municipio", "Mesorregião": "mesorregiao", "Microrregião": "microrregiao"})
    return tabela.to_dict(orient="records")

class EntradaTexto(BaseModel):
    texto: str = Field(min_length=10, max_length=6000, description="Texto a ser processado pelo modelo.",
                       examples=["- Banco de alimentos recebe 20 toneladas de doações\n- Feira reduz desperdício"])
    tarefa: Tarefa = Field(default="resumo", description="'resumo' ou 'pergunta_resposta'.")
    pergunta: str | None = Field(default=None, max_length=300, description="Obrigatória na tarefa 'pergunta_resposta'.")
    estilo: Estilo = Field(default="padrao", description="Jeito do resumo: 'padrao', 'gestor' ou 'topicos' (só em 'resumo').")
    max_novos_tokens: int = Field(default=150, ge=20, le=300, description="Tamanho máximo da resposta.")

    @model_validator(mode="after")
    def exigir_pergunta(self):
        if self.tarefa == "pergunta_resposta" and not (self.pergunta or "").strip():
            raise ValueError("Informe a pergunta na tarefa 'pergunta_resposta'.")
        return self


class ResultadoTexto(BaseModel):
    tipo_analise: Tarefa = Field(description="Tarefa realizada pelo modelo.")
    texto_processado: str = Field(description="Texto que foi enviado ao modelo.")
    pergunta: str | None = Field(default=None, description="Pergunta feita (só em 'pergunta_resposta').")
    estilo: Estilo | None = Field(default=None, description="Estilo do resumo (só em 'resumo').")
    resultado: str = Field(description="Resposta gerada pelo modelo.")
    modelo: str = Field(description="Nome do modelo usado.")
    tempo_segundos: float = Field(description="Tempo gasto para gerar a resposta.")


class StatusModelo(BaseModel):
    modelo: str
    carregado: bool = Field(description="True se o modelo já está na memória.")


class ErroResposta(BaseModel):
    detail: str


ERROS_LLM = {
    422: {"model": ErroResposta, "description": "Texto ou pergunta inválidos."},
    500: {"model": ErroResposta, "description": "Erro inesperado ao gerar a resposta."},
    502: {"model": ErroResposta, "description": "O modelo não devolveu resposta."},
    503: {"model": ErroResposta, "description": "Modelo indisponível (não instalado, não carregou ou sem memória)."},
    504: {"model": ErroResposta, "description": "O modelo demorou demais para responder."},
}


@app.get("/modelo", response_model=StatusModelo, tags=["LLM"], summary="Mostra qual modelo local está configurado")
def status_modelo() -> dict:
    return llm_local.status()


@app.post("/modelo/carregar", response_model=StatusModelo, tags=["LLM"],
          responses={503: ERROS_LLM[503]}, summary="Carrega o modelo na memória (baixa na primeira vez)")
async def carregar_modelo() -> dict:
    try:
        await asyncio.to_thread(llm_local.carregar)
    except llm_local.ModeloIndisponivel as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    return llm_local.status()


async def _executar_llm(mensagens: list[dict], max_novos_tokens: int) -> tuple[str, float]:
    """Roda o modelo local e traduz cada tipo de falha em um erro HTTP claro."""
    inicio = time.perf_counter()
    try:
        resposta = await asyncio.wait_for(
            asyncio.to_thread(llm_local.gerar, mensagens, max_novos_tokens), timeout=TIMEOUT_LLM
        )
    except llm_local.ModeloIndisponivel as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except asyncio.TimeoutError as erro:
        raise HTTPException(
            status_code=504,
            detail=f"O modelo demorou mais de {TIMEOUT_LLM:.0f} segundos. Tente um texto menor ou uma resposta mais curta.",
        ) from erro
    except Exception as erro:
        logger.exception("Erro inesperado no modelo local")
        raise HTTPException(status_code=500, detail="Erro inesperado ao gerar a resposta.") from erro

    if not resposta.strip():
        raise HTTPException(status_code=502, detail="O modelo não devolveu nenhuma resposta. Tente reformular o texto.")
    return resposta.strip(), round(time.perf_counter() - inicio, 2)


@app.post("/processar_texto", response_model=ResultadoTexto, tags=["LLM"], responses=ERROS_LLM,
          summary="Resume um texto ou responde uma pergunta usando o modelo local")
async def processar_texto(entrada: EntradaTexto) -> dict:
    mensagens = llm_prep.mensagens(entrada.tarefa, entrada.texto, entrada.pergunta, entrada.estilo)
    resposta, tempo = await _executar_llm(mensagens, entrada.max_novos_tokens)
    return {
        "tipo_analise": entrada.tarefa,
        "texto_processado": entrada.texto,
        "pergunta": entrada.pergunta,
        "estilo": entrada.estilo if entrada.tarefa == "resumo" else None,
        "resultado": resposta,
        "modelo": llm_local.nome_modelo(),
        "tempo_segundos": tempo,
    }


# ===================================================== Resumos das notícias (TP5)
class PedidoResumo(BaseModel):
    uf: str = Field(examples=["AM"], description="Sigla do estado cujas notícias serão resumidas.")
    estilo: Estilo = Field(default="padrao", description="'padrao', 'gestor' (para o gestor público) ou 'topicos'.")
    limite_noticias: int = Field(default=12, ge=3, le=30, description="Quantas notícias (as mais recentes salvas) entram no resumo.")

    @field_validator("uf")
    @classmethod
    def validar_estado(cls, valor: str) -> str:
        uf = dados.normalizar_uf(valor)
        if uf == config.NACIONAL:
            raise ValueError("Informe a sigla de um estado.")
        return uf


class ResumoGerado(BaseModel):
    uf: str
    estilo: Estilo
    resumo: str
    modelo: str
    noticias_usadas: int = Field(description="Quantas notícias foram enviadas ao modelo.")
    gerado_em: str = Field(description="Data e hora em que o resumo foi gerado.")
    tempo_segundos: float


@app.post("/resumos/gerar", response_model=ResumoGerado, status_code=status.HTTP_201_CREATED, tags=["Resumos"],
          responses={404: {"model": ErroResposta, "description": "Não há notícias salvas para o estado."}, **ERROS_LLM},
          summary="Resume as notícias salvas de um estado com o modelo local e guarda o resultado")
async def gerar_resumo(pedido: PedidoResumo) -> dict:
    noticias = dados.carregar_noticias(uf=pedido.uf, limite=pedido.limite_noticias)
    if noticias.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Não há notícias salvas para {pedido.uf}. Colete antes (POST /noticias/coletar).",
        )
    texto = "\n".join(f"- {titulo}" for titulo in noticias["Título"])
    mensagens = llm_prep.mensagens("resumo", texto, estilo=pedido.estilo)
    resposta, tempo = await _executar_llm(mensagens, 200)

    registro = {
        "uf": pedido.uf,
        "estilo": pedido.estilo,
        "resumo": resposta,
        "modelo": llm_local.nome_modelo(),
        "noticias_usadas": len(noticias),
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "tempo_segundos": tempo,
    }
    dados.salvar_resumo(
        uf=registro["uf"], estilo=registro["estilo"], resumo=registro["resumo"], modelo=registro["modelo"],
        noticias=registro["noticias_usadas"], gerado_em=registro["gerado_em"], tempo=registro["tempo_segundos"],
    )
    return registro


@app.get("/resumos", response_model=list[ResumoGerado], tags=["Resumos"], summary="Lista os resumos já gerados (mais novos primeiro)")
def listar_resumos(uf: str | None = None, limite: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    uf = _validar_uf_estado(uf) if uf else None
    df = dados.carregar_resumos(uf=uf, limite=limite)
    df = df.rename(columns={"UF": "uf", "Estilo": "estilo", "Resumo": "resumo", "Modelo": "modelo",
                            "Notícias": "noticias_usadas", "Gerado em": "gerado_em", "Tempo (s)": "tempo_segundos"})
    return df.to_dict(orient="records")
