# 🍽️ Alimenta+

Aplicação que conecta alimentos que poderiam ser desperdiçados a pessoas e organizações que precisam deles (ODS 2, 12 e 17).

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn api.main:app --reload     # 1º terminal: API em http://localhost:8000  (docs em /docs)
streamlit run app.py              # 2º terminal: aplicação (menu lateral com as páginas)
python -m scripts.coletar_dados   # opcional: coleta notícias e municípios de todos os estados
```

O app Streamlit não lê os CSVs direto: todas as páginas pedem os dados à API (`alimenta/cliente_api.py`). Por isso a API precisa estar rodando antes do app.

## Páginas do app
| Página | O que faz |
|---|---|
| Início | Resumo da base e atalhos |
| 📈 Painel | Do dado ao insight: gráficos, cobertura por estado e **resumo das notícias com IA** |
| 🤝 Organizações | Filtros, cadastro, importação e download de CSV |
| 🗺️ Mapa | Pontos de doação e excedente |
| 📰 Notícias | Busca e salva notícias por estado |
| 📊 Dados IBGE | Municípios (IBGE) e panorama da base |
| 🤖 API e LLM | Assistente com modelo local: resumo de textos e perguntas e respostas |

## API (FastAPI)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/organizacoes?uf=SP&tipo=Doação&incluir_nacional=true` | Lista organizações |
| POST | `/organizacoes` | Cadastra organização (409 se já existir; 422 se inválida) |
| GET | `/pontos?uf=RJ` | Pontos com latitude/longitude |
| GET | `/noticias?uf=SP&limite=5` | Notícias já coletadas |
| POST | `/noticias/coletar?uf=SP` | Busca notícias novas do estado e salva no CSV |
| GET | `/municipios/SP` | Municípios, mesorregiões e microrregiões (IBGE) |
| POST | `/processar_texto` | Resume um texto ou responde uma pergunta com o modelo local |
| GET | `/modelo` | Modelo configurado e se já está carregado |
| POST | `/modelo/carregar` | Carrega o modelo na memória |
| POST | `/resumos/gerar` | Resume as notícias salvas de um estado (3 estilos) e guarda o resultado |
| GET | `/resumos?uf=AM` | Lista os resumos já gerados |
| GET | `/health` | Status da API |

```bash
curl "http://localhost:8000/organizacoes?uf=SP"
curl -X POST http://localhost:8000/organizacoes -H "Content-Type: application/json" \
     -d '{"nome": "Banco de Alimentos de Recife", "tipo": "Doação", "uf": "PE"}'
```

## Modelo de linguagem local e sumarização (TP4 e TP5)
O app usa o `Qwen/Qwen2.5-0.5B-Instruct` (HuggingFace) rodando no próprio computador. Na primeira vez ele é baixado (cerca de 1 GB). Ele resume as notícias de cada estado em três estilos de prompt (padrão, para o gestor público e em tópicos). Comparação entre modelos, hardware e justificativa em `Docs/LLM/escolha_do_modelo.md`.

```bash
curl -X POST http://localhost:8000/processar_texto -H "Content-Type: application/json" \
     -d '{"texto": "Banco de alimentos recebe 20 toneladas de doações de feiras.", "tarefa": "resumo"}'
```

```bash
curl -X POST http://localhost:8000/resumos/gerar -H "Content-Type: application/json" \
     -d '{"uf": "AM", "estilo": "gestor"}'
python -m scripts.medir_modelo   # mede tempo e memória do modelo e gera Docs/LLM/medicoes.md
```

Variáveis opcionais: `ALIMENTA_MODELO` (trocar o modelo) e `ALIMENTA_TIMEOUT_LLM` (tempo máximo de resposta, em segundos).

## Estrutura
```
app.py                 ponto de entrada e menu de navegação do Streamlit
pages/                 páginas do app (Início, Organizações, Mapa...)
api/main.py            API FastAPI
alimenta/              módulos compartilhados (dados, coleta, config), cliente_api.py, llm_prep.py e llm_local.py
scripts/               coleta em lote e medição do modelo
Data/                  CSVs usados pelo app e pela API
Docs/                  Project Charter, Data Summary Report e escolha do modelo (LLM)
```

## Observações
- Os cadastros ficam em `Data/*.csv`. Em hospedagens com disco temporário (ex.: Streamlit Community Cloud) eles podem ser perdidos ao reiniciar.
- Selenium não foi necessário: as fontes (API do IBGE e RSS) não têm conteúdo dinâmico. Ver `Docs/Project/project_charter.md`.
- **Uso de IA:** foi utilizado o Claude (Anthropic) como apoio no código, na documentação e na correção de erros, com revisão e testes da autora. O modelo usado dentro do app é o Qwen2.5-0.5B-Instruct (Qwen Team, Alibaba).
