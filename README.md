# 🍽️ Alimenta+

Aplicação que conecta alimentos que poderiam ser desperdiçados a pessoas e organizações que precisam deles (ODS 2, 12 e 17).

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

streamlit run app.py              # aplicação (menu lateral com as páginas)
uvicorn api.main:app --reload     # API em http://localhost:8000  (docs em /docs)
python -m scripts.coletar_dados   # coleta notícias e municípios de todos os estados
```

Testes: `pip install -r requirements-dev.txt && python -m pytest`

## Páginas do app
| Página | O que faz |
|---|---|
| Início | Resumo da base e atalhos |
| 🤝 Organizações | Filtros, cadastro, importação e download de CSV |
| 🗺️ Mapa | Pontos de doação e excedente |
| 📰 Notícias | Busca e salva notícias por estado |
| 📊 Dados IBGE | Municípios (IBGE) e panorama da base |
| 🤖 API e LLM | Guia da API e prompts/corpus para a etapa de LLM |

## API (FastAPI)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/organizacoes?uf=SP&tipo=Doação&incluir_nacional=true` | Lista organizações |
| POST | `/organizacoes` | Cadastra organização (409 se já existir; 422 se inválida) |
| GET | `/pontos?uf=RJ` | Pontos com latitude/longitude |
| GET | `/noticias?uf=SP&limite=5` | Notícias já coletadas |
| GET | `/health` | Status da API |

```bash
curl "http://localhost:8000/organizacoes?uf=SP"
curl -X POST http://localhost:8000/organizacoes -H "Content-Type: application/json" \
     -d '{"nome": "Banco de Alimentos de Recife", "tipo": "Doação", "uf": "PE"}'
```

## Estrutura
```
app.py                 ponto de entrada e menu de navegação do Streamlit
pages/                 páginas do app (Início, Organizações, Mapa...)
api/main.py            API FastAPI
alimenta/              módulos compartilhados (dados, coleta, llm_prep, config)
scripts/               coleta em lote
Data/                  CSVs usados pelo app e pela API
Docs/                  Project Charter e Data Summary Report
tests/                 testes automatizados
```

## Observações
- Os cadastros ficam em `Data/*.csv`. Em hospedagens com disco temporário (ex.: Streamlit Community Cloud) eles podem ser perdidos ao reiniciar.
- Selenium não foi necessário: as fontes (API do IBGE e RSS) não têm conteúdo dinâmico. Ver `Docs/Project/project_charter.md`.
- **Uso de IA:** partes do código e da documentação foram feitas com apoio do Claude (Anthropic) e revisadas pela autora.
