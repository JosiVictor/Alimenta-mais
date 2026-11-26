"""Mede o modelo de linguagem local neste computador e grava o relatório Docs/LLM/medicoes.md.

O relatório traz: hardware, memória usada, tempo para carregar o modelo, tempo de cada resposta e
exemplos REAIS da API (uma resposta de sucesso e as respostas de erro 422, 503 e 504).

Uso (com a API desligada ou ligada, tanto faz):  python -m scripts.medir_modelo
"""
import json
import os
import platform
import time
from datetime import datetime
from pathlib import Path

import psutil

from alimenta import config, dados, llm_local, llm_prep

TEXTO_PADRAO = (
    "- Banco de alimentos recebe 20 toneladas de frutas e verduras que seriam descartadas\n"
    "- Feira livre doa sobras para famílias em situação de insegurança alimentar\n"
    "- Prefeitura lança programa para reduzir o desperdício de comida"
)


def memoria_mb() -> float:
    return round(psutil.Process().memory_info().rss / 1024**2)


def hardware() -> dict:
    gpu = "não detectada"
    try:
        import torch

        if torch.cuda.is_available():
            gpu = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return {
        "Sistema": platform.platform(),
        "Processador": platform.processor() or "não informado",
        "Núcleos (físicos / lógicos)": f"{psutil.cpu_count(logical=False)} / {psutil.cpu_count(logical=True)}",
        "Memória RAM total": f"{psutil.virtual_memory().total / 1024**3:.1f} GB",
        "Placa de vídeo (GPU)": gpu,
        "Onde o modelo roda": "CPU (o app não usa a GPU)",
    }


def texto_de_exemplo() -> str:
    noticias = dados.carregar_noticias(limite=8)
    noticias = noticias[noticias["UF"] != ""]
    if noticias.empty:
        return TEXTO_PADRAO
    return "\n".join(f"- {t}" for t in noticias["Título"])


def medir_geracoes(texto: str) -> list[dict]:
    casos = [
        ("Resumo padrão", llm_prep.mensagens("resumo", texto, estilo="padrao")),
        ("Resumo para o gestor", llm_prep.mensagens("resumo", texto, estilo="gestor")),
        ("Resumo em tópicos", llm_prep.mensagens("resumo", texto, estilo="topicos")),
    ]
    resultados = []
    for nome, mensagens in casos:
        inicio = time.perf_counter()
        resposta = llm_local.gerar(mensagens, 200)
        resultados.append({"caso": nome, "segundos": round(time.perf_counter() - inicio, 1), "resposta": resposta})
    return resultados


def evidencias_da_api(texto: str) -> list[dict]:
    """Chama a API de verdade (sem precisar ligar o servidor) e guarda as respostas."""
    from fastapi.testclient import TestClient

    from api import main

    client = TestClient(main.app)
    registros = []

    def chamar(titulo, corpo):
        resposta = client.post("/processar_texto", json=corpo)
        registros.append({"titulo": titulo, "status": resposta.status_code, "corpo": resposta.json()})

    chamar("Sucesso (200)", {"texto": texto, "tarefa": "resumo"})
    chamar("Texto muito curto (422)", {"texto": "curto", "tarefa": "resumo"})

    modelo_certo = os.environ.get("ALIMENTA_MODELO")
    os.environ["ALIMENTA_MODELO"] = "modelo-que-nao-existe/teste"
    try:
        chamar("Modelo que não existe (503)", {"texto": texto, "tarefa": "resumo"})
    finally:
        if modelo_certo is None:
            os.environ.pop("ALIMENTA_MODELO")
        else:
            os.environ["ALIMENTA_MODELO"] = modelo_certo

    tempo_normal = main.TIMEOUT_LLM
    main.TIMEOUT_LLM = 0.01
    try:
        chamar("Tempo esgotado (504)", {"texto": texto, "tarefa": "resumo"})
    finally:
        main.TIMEOUT_LLM = tempo_normal
    return registros


def montar_relatorio(maquina, carga, geracoes, evidencias) -> str:
    linhas = [
        "# Medições do modelo local",
        "",
        f"Gerado automaticamente por `python -m scripts.medir_modelo` em {datetime.now():%d/%m/%Y %H:%M}.",
        f"Modelo medido: `{llm_local.nome_modelo()}`.",
        "",
        "## Computador usado",
        "| Item | Valor |",
        "|---|---|",
        *[f"| {chave} | {valor} |" for chave, valor in maquina.items()],
        "",
        "## Carga do modelo",
        "| Medida | Valor |",
        "|---|---|",
        f"| Tempo para carregar na memória | {carga['segundos']} s |",
        f"| Memória do programa antes de carregar | {carga['antes']} MB |",
        f"| Memória do programa depois de carregar | {carga['depois']} MB |",
        f"| Memória do programa depois das respostas | {carga['final']} MB |",
        "",
        "O modelo já estava baixado no disco; o tempo do primeiro download depende da internet.",
        "",
        "## Tempo de cada resposta",
        "| Caso | Tempo |",
        "|---|---|",
        *[f"| {g['caso']} | {g['segundos']} s |" for g in geracoes],
        "",
        "### Respostas geradas",
        *[f"**{g['caso']}**\n\n> {g['resposta']}\n" for g in geracoes],
        "## Exemplos reais da API",
        "Respostas da rota `POST /processar_texto`, obtidas neste computador.",
        "",
    ]
    for e in evidencias:
        linhas += [f"### {e['titulo']}", "```json", json.dumps(e["corpo"], ensure_ascii=False, indent=2), "```", ""]
    return "\n".join(linhas)


def main(saida: Path | None = None) -> Path:
    saida = saida or config.RAIZ / "Docs" / "LLM" / "medicoes.md"
    texto = texto_de_exemplo()

    print("Carregando o modelo (pode demorar na primeira vez)...")
    antes = memoria_mb()
    inicio = time.perf_counter()
    llm_local.carregar()
    segundos = round(time.perf_counter() - inicio, 1)
    depois = memoria_mb()

    print("Gerando respostas de teste...")
    geracoes = medir_geracoes(texto)
    carga = {"segundos": segundos, "antes": antes, "depois": depois, "final": memoria_mb()}

    print("Coletando exemplos da API (sucesso e erros)...")
    evidencias = evidencias_da_api(texto)

    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(montar_relatorio(hardware(), carga, geracoes, evidencias), encoding="utf-8")
    print(f"Pronto! Relatório salvo em {saida}")
    return saida


if __name__ == "__main__":
    main()
