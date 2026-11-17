"""Modelo de linguagem local, executado no próprio computador com HuggingFace Transformers.

O modelo é baixado do HuggingFace Hub na primeira vez e fica no cache da máquina; depois disso
roda sem internet. Para trocar de modelo, defina a variável de ambiente ALIMENTA_MODELO
(ex.: Qwen/Qwen2.5-1.5B-Instruct, se o computador tiver memória de sobra).

As bibliotecas pesadas (torch e transformers) só são importadas quando o modelo é usado, então a API
e o app sobem normalmente mesmo sem elas; nesse caso as rotas de LLM respondem 503 com uma explicação.
"""
import os
import threading

MODELO_PADRAO = "Qwen/Qwen2.5-0.5B-Instruct"

_trava = threading.Lock()
_carregado: dict = {"nome": None, "tokenizer": None, "modelo": None}


class ModeloIndisponivel(Exception):
    """O modelo não está pronto: biblioteca ausente, falha no download/carga ou falta de memória."""


def nome_modelo() -> str:
    return os.getenv("ALIMENTA_MODELO", MODELO_PADRAO)


def _importar_bibliotecas():
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as erro:
        raise ModeloIndisponivel(
            "As bibliotecas 'transformers' e 'torch' não estão instaladas. Rode: pip install transformers torch"
        ) from erro
    return torch, AutoTokenizer, AutoModelForCausalLM


def esta_carregado() -> bool:
    return _carregado["modelo"] is not None and _carregado["nome"] == nome_modelo()


def status() -> dict:
    return {"modelo": nome_modelo(), "carregado": esta_carregado()}


def carregar() -> None:
    """Carrega o modelo na memória (baixa do HuggingFace se ainda não estiver na máquina)."""
    with _trava:
        _carregar_sem_trava()


def _carregar_sem_trava() -> None:
    if esta_carregado():
        return
    nome = nome_modelo()
    _, AutoTokenizer, AutoModelForCausalLM = _importar_bibliotecas()
    try:
        tokenizer = AutoTokenizer.from_pretrained(nome)
        modelo = AutoModelForCausalLM.from_pretrained(nome)
        modelo.eval()
    except Exception as erro:  # nome errado, sem internet no 1º download, disco cheio, pouca memória...
        raise ModeloIndisponivel(f"Não foi possível carregar o modelo '{nome}': {erro}") from erro
    _carregado.update(nome=nome, tokenizer=tokenizer, modelo=modelo)


def gerar(mensagens: list[dict], max_novos_tokens: int = 150) -> str:
    """Gera a resposta do modelo para uma conversa no formato [{'role': ..., 'content': ...}]."""
    with _trava:
        _carregar_sem_trava()
        torch, _, _ = _importar_bibliotecas()
        tokenizer, modelo = _carregado["tokenizer"], _carregado["modelo"]
        try:
            prompt = tokenizer.apply_chat_template(mensagens, tokenize=False, add_generation_prompt=True)
            entradas = tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                saida = modelo.generate(
                    **entradas,
                    max_new_tokens=max_novos_tokens,
                    do_sample=False,  # sem sorteio: a mesma entrada dá a mesma resposta
                    pad_token_id=tokenizer.eos_token_id,
                )
            novos = saida[0][entradas["input_ids"].shape[1]:]
            return tokenizer.decode(novos, skip_special_tokens=True).strip()
        except RuntimeError as erro:  # ex.: falta de memória durante a geração
            raise ModeloIndisponivel(f"O modelo falhou ao gerar a resposta: {erro}") from erro
