# Modelo de linguagem local — escolha e integração

## 1. O que o modelo faz no projeto
O Alimenta+ usa um modelo de linguagem que roda **no próprio computador**, sem enviar dados para a nuvem:

- **Sumarização (foco do TP5):** resume as manchetes salvas de um estado, em três estilos (padrão, para o gestor público e em tópicos).
- **Perguntas e respostas:** responde sobre as organizações cadastradas, usando só a lista do app.

## 2. Critérios e comparação
Critérios: **desempenho** (fala português, segue instruções e faz as duas tarefas), **custo local** (cabe em 8 GB de memória, sem placa de vídeo) e **acessibilidade** (baixa pela biblioteca `transformers`, sem cadastro e com licença livre).

A avaliação vem das fichas dos modelos no HuggingFace. **Só o Qwen2.5-0.5B foi testado no projeto**; os outros foram analisados, não executados.

| Modelo | Português | Memória (estimativa) | Acesso e licença | Avaliação |
|---|---|---|---|---|
| **Qwen2.5-0.5B-Instruct** (0,49 bi) | Sim | 1 a 2 GB | Sem cadastro, Apache 2.0 | Cabe no computador e faz as duas tarefas, mas erra mais por ser pequeno. |
| Qwen2.5-1.5B-Instruct (1,5 bi) | Sim | 3 GB ou mais | Sem cadastro, Apache 2.0 | Responde melhor, mas é arriscado com 8 GB. |
| Llama 3.2 1B-Instruct (1,23 bi) | Sim | 3 a 5 GB | **Exige cadastro e aceite da licença da Meta** | Provavelmente melhor, mas o acesso restrito complica a execução por quem corrigir. |
| SmolLM2-360M-Instruct (0,36 bi) | Fraco | cerca de 0,7 GB | Sem cadastro, Apache 2.0 | Mais leve, mas pior em português. |
| Modelo só de resumo  | Varia | Varia | Em geral sem cadastro | Bom em resumo, mas não faz perguntas e respostas. |

**Decisão:** Qwen2.5-0.5B-Instruct, o único que reúne português, as duas tarefas, acesso sem cadastro e memória compatível. Para trocar por um modelo maior, sem mexer no código:

```powershell
$env:ALIMENTA_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"     # Windows (PowerShell)
export ALIMENTA_MODELO=Qwen/Qwen2.5-1.5B-Instruct       # Linux / Mac
```

## 3. Hardware
O modelo roda na **CPU** (sem GPU). Precisa de 3 a 4 GB de memória livre (contando Python, `torch` e o app) e cerca de 1 GB de disco. O primeiro download (cerca de 988 MB) levou vários minutos. Tempos e memória medidos no computador do projeto estão em [`medicoes.md`](medicoes.md), gerado por `python -m scripts.medir_modelo`, junto de exemplos reais da API (sucesso e erros 422, 503 e 504).

## 4. Como a integração funciona
```
Streamlit (Painel / Assistente com IA)
        │  pede à API
        ▼
FastAPI  POST /resumos/gerar  ou  POST /processar_texto     ← valida a entrada (Response Models)
        │
        ▼
alimenta/llm_prep.py   monta o prompt do estilo escolhido
        │
        ▼
alimenta/llm_local.py  carrega o modelo (1ª vez) e gera a resposta com Transformers
```
O modelo é baixado na primeira vez, fica no cache e é carregado na primeira chamada. `torch` e `transformers` só são carregados quando o modelo é usado, então a API sobe mesmo sem eles.

| Método | Rota | Função |
|---|---|---|
| POST | `/resumos/gerar` | Resume as notícias salvas de um estado e guarda o resultado |
| GET | `/resumos` | Lista os resumos gerados |
| POST | `/processar_texto` | Resume um texto qualquer ou responde uma pergunta |
| GET | `/modelo` | Mostra o modelo configurado e se já está carregado |
| POST | `/modelo/carregar` | Carrega o modelo antes do primeiro uso |


## 5. Engenharia de prompts (sumarização)
O mesmo texto é pedido de três jeitos (`alimenta/llm_prep.py`):

| Estilo | Pedido ao modelo |
|---|---|
| `padrao` | Resumir em até 3 frases o que o texto diz sobre desperdício e doação de alimentos |
| `gestor` | Resumir em até 3 frases para um gestor público, destacando o que pode reduzir o desperdício ou ampliar doações |
| `topicos` | Listar de 3 a 5 tópicos curtos com os principais fatos |

## 6. Tratamento de erros
| Código | Quando acontece |
|---|---|
| 404 | `/resumos/gerar` em um estado sem notícias salvas (pede para coletar antes) |
| 422 | Entrada inválida: texto muito curto ou longo, tarefa, estilo ou estado inválidos, pergunta ausente |
| 502 | O modelo não devolveu resposta (pede para reformular o texto) |
| 503 | `torch`/`transformers` ausentes, falha ao baixar ou carregar o modelo, falta de memória |
| 504 | O modelo passou do limite de 180 s (ajustável em `ALIMENTA_TIMEOUT_LLM`) |
| 500 | Erro inesperado (o detalhe fica só no log) |

## 7. Como testar
```bash
pip install -r requirements.txt
python -m uvicorn api.main:app --reload       # 1º terminal
python -m streamlit run app.py                # 2º terminal
```
No menu **Painel**, escolha um estado e um estilo e clique em **Gerar resumo com o modelo local**. Também dá para testar `POST /resumos/gerar` e `POST /processar_texto` em `http://localhost:8000/docs`. A primeira execução baixa o modelo (cerca de 1 GB).

## 8. Limitações
- Modelos pequenos podem errar ou inventar informações; os resumos devem ser conferidos antes de serem usados em decisões.
- O resumo usa só as manchetes, não o texto completo das notícias.
- Sem placa de vídeo a geração é lenta, e só uma resposta é gerada por vez.

## 9. Uso de IA
O código e esta documentação foram feitos com apoio do Claude e revisados pela autora do projeto. O modelo usado dentro do app é o Qwen2.5-0.5B-Instruct.