"""Preparação dos dados para a etapa de LLMs (TP4): monta prompts e um corpus em JSONL.

Nenhuma chamada a LLM é feita aqui — apenas a preparação dos textos de entrada.
"""
import json

import pandas as pd

from . import config


def contexto_organizacoes(orgs: pd.DataFrame) -> str:
    linhas = []
    for _, o in orgs.iterrows():
        linha = f"- {o['Nome']} ({o['Tipo']}, {o['UF']})"
        if o["Como ajudar"]:
            linha += f": {o['Como ajudar']}"
        if o["Site"]:
            linha += f" Site: {o['Site']}"
        linhas.append(linha)
    return "\n".join(linhas)


def prompt_resumo(noticias: pd.DataFrame, estado: str) -> str:
    titulos = "\n".join(f"- {t}" for t in noticias["Título"])
    return (
        "Você é um analista de segurança alimentar. Com base apenas nas manchetes abaixo, "
        f"escreva um resumo de até 5 linhas sobre desperdício e doação de alimentos em {estado}, "
        "destacando oportunidades de doação.\n\n"
        f"Manchetes:\n{titulos or '(nenhuma notícia coletada)'}"
    )


def prompt_perguntas_respostas(pergunta: str, orgs: pd.DataFrame) -> str:
    return (
        "Responda à pergunta usando somente as organizações listadas. "
        "Se a informação não estiver na lista, diga que não sabe.\n\n"
        f"Organizações:\n{contexto_organizacoes(orgs)}\n\nPergunta: {pergunta}"
    )


def corpus_jsonl(orgs: pd.DataFrame, noticias: pd.DataFrame) -> str:
    """Um documento por linha, pronto para virar base de consulta (Q&A/RAG) na próxima etapa."""
    documentos = []
    for i, o in orgs.reset_index(drop=True).iterrows():
        documentos.append(
            {
                "id": f"org-{i + 1}",
                "fonte": "organizacoes",
                "uf": o["UF"],
                "tipo": o["Tipo"],
                "texto": f"{o['Nome']}. {o['Como ajudar']}".strip(),
                "link": o["Site"],
            }
        )
    for i, n in noticias.reset_index(drop=True).iterrows():
        documentos.append(
            {
                "id": f"noticia-{i + 1}",
                "fonte": "noticias",
                "uf": n["UF"],
                "tipo": "Notícia",
                "texto": n["Título"],
                "link": n["Link"],
            }
        )
    return "\n".join(json.dumps(d, ensure_ascii=False) for d in documentos)
