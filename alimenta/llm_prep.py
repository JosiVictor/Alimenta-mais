"""Preparação dos textos para o LLM: monta as conversas (prompts) de cada tarefa e o corpus em JSONL.

Nenhuma chamada ao modelo é feita aqui; quem executa o modelo é `llm_local.py`.
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


TAREFAS = ("resumo", "pergunta_resposta")

_SISTEMA = "Você é um assistente que escreve em português do Brasil, de forma clara e objetiva."


def mensagens(tarefa: str, texto: str, pergunta: str | None = None) -> list[dict]:
    """Monta a conversa enviada ao modelo para cada tarefa."""
    if tarefa == "resumo":
        pedido = (
            "Resuma em até 3 frases, usando somente o texto abaixo, o que ele diz sobre "
            f"desperdício e doação de alimentos.\n\nTexto:\n{texto}"
        )
    elif tarefa == "pergunta_resposta":
        if not (pergunta or "").strip():
            raise ValueError("Informe a pergunta para a tarefa de perguntas e respostas.")
        pedido = (
            "Responda à pergunta usando somente as informações do texto. "
            "Se a resposta não estiver no texto, diga que não sabe.\n\n"
            f"Texto:\n{texto}\n\nPergunta: {pergunta.strip()}"
        )
    else:
        raise ValueError(f"Tarefa desconhecida: '{tarefa}'. Use {' ou '.join(TAREFAS)}.")
    return [{"role": "system", "content": _SISTEMA}, {"role": "user", "content": pedido}]


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
