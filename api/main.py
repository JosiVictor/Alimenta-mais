"""API do Alimenta+ (FastAPI).

Como rodar:  uvicorn api.main:app --reload
Documentação interativa: http://localhost:8000/docs
"""
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from alimenta import config, dados

app = FastAPI(
    title="API Alimenta+",
    description="Consulta e cadastro de organizações de doação e centrais de excedente de alimentos.",
    version="1.0.0",
)

Tipo = Literal["Doação", "Excedente"]


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
def listar_noticias(uf: str | None = None, limite: int = Query(default=10, ge=1, le=100)) -> list[dict]:
    uf = _validar_uf_consulta(uf)
    df = dados.carregar_noticias(uf=uf, limite=limite)
    df = df.rename(columns={"Título": "titulo", "Fonte": "fonte", "Data": "data", "Link": "link", "UF": "uf"})
    return df.to_dict(orient="records")
