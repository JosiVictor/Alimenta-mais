# Modelo de linguagem local — escolha e integração (TP4)

## 1. O que foi feito
O Alimenta+ agora tem um modelo de linguagem que roda **no próprio computador**, sem enviar dados para a nuvem. Ele é usado para duas tarefas:

- **Resumo de notícias:** resume as manchetes salvas de um estado.
- **Perguntas e respostas:** responde perguntas (ex.: "Onde posso doar alimentos em MG?") usando a lista de organizações como base.

## 2. Modelo escolhido
**`Qwen/Qwen2.5-0.5B-Instruct`** (HuggingFace), da família Qwen2.5.

```bash
set ALIMENTA_MODELO=Qwen/Qwen2.5-1.5B-Instruct        # Windows (cmd)
$env:ALIMENTA_MODELO = "Qwen/Qwen2.5-1.5B-Instruct"    # Windows (PowerShell)
export ALIMENTA_MODELO=Qwen/Qwen2.5-1.5B-Instruct      # Linux / Mac
```

**Por que um modelo de uso geral?** Modelos específicos de resumo ou de perguntas e respostas costumam ser bons em uma tarefa só. Com um modelo "instruct" as duas tarefas usam o mesmo modelo, só trocando o pedido, o que mantém o projeto simples.

**Como reduzir os erros de um modelo pequeno:**
- o pedido manda usar **somente o texto fornecido** e dizer "não sei" quando a resposta não estiver nele;
- a geração é **determinística** (`do_sample=False`): o mesmo texto gera a mesma resposta;
- a resposta é curta (limite de tokens), o que reduz o espaço para inventar.

## 3. Como a integração funciona

### Rotas
| Método | Rota | Função |
|---|---|---|
| POST | `/processar_texto` | Resume um texto ou responde uma pergunta |
| GET | `/modelo` | Mostra o modelo configurado e se já está carregado |
| POST | `/modelo/carregar` | Carrega o modelo antes do primeiro uso |

**Entrada de `/processar_texto`:**
```json
{
  "texto": "- Banco de alimentos recebe 20 toneladas de doações\n- Feira reduz o desperdício",
  "tarefa": "resumo",
  "pergunta": null,
  "max_novos_tokens": 150
}
```
`tarefa` pode ser `resumo` ou `pergunta_resposta` (nesta, `pergunta` é obrigatória). O texto precisa ter de 10 a 6000 caracteres.

**Saída (Response Model `ResultadoTexto`):**
```json
{
  "tipo_analise": "resumo",
  "texto_processado": "- Banco de alimentos recebe 20 toneladas...",
  "pergunta": null,
  "resultado": "…resposta gerada pelo modelo…",
  "modelo": "Qwen/Qwen2.5-0.5B-Instruct",
  "tempo_segundos": 12.4
}
```

## 4. Tratamento de erros
| Código | Quando acontece | O que a API responde |
|---|---|---|
| 422 | Texto muito curto/longo, tarefa inválida, pergunta ausente | Mensagem dizendo qual campo está errado |
| 503 | `torch`/`transformers` não instalados, falha ao baixar/carregar o modelo, falta de memória | Mensagem explicando o problema |
| 504 | O modelo demorou mais que o limite (180 s, ajustável em `ALIMENTA_TIMEOUT_LLM`) | Sugere um texto menor ou resposta mais curta |
| 502 | O modelo não devolveu nenhuma resposta | Pede para reformular o texto |
| 500 | Erro inesperado | Mensagem genérica (o detalhe fica só no log, para não expor informações internas) |

No app, o erro aparece em vermelho com o código e a mensagem. Se a API estiver desligada, o app avisa como ligá-la.

## 5. Como testar
```bash
pip install -r requirements.txt
uvicorn api.main:app --reload                 
streamlit run app.py                          
```
1. Abra `http://localhost:8000/docs`, escolha `POST /processar_texto` e clique em *Try it out*.
2. Ou use o app: menu **API e LLM → Assistente com LLM local → Gerar com o modelo local**.
3. A primeira execução baixa o modelo (cerca de 1 GB) e pode demorar vários minutos.

Para ver os erros: envie um texto de poucas letras (422); ou rode a API sem `torch` instalado (503).

## 6. Limitações
- Modelos pequenos podem errar ou inventar informações; o resultado deve ser conferido antes de ser usado em decisões.
- Sem placa de vídeo, a geração é lenta; só uma resposta é gerada por vez.
- O modelo não guarda nada: texto e respostas não são salvos.

## 7. Uso de IA
O código e esta documentação foram feitos com apoio do Claude (Anthropic) e revisados pela autora do projeto. O modelo de linguagem usado dentro do app é o Qwen2.5-0.5B-Instruct (Qwen Team, Alibaba).
