# Project Charter — Alimenta+

## 1. Contexto e Problema de Negócio
No Brasil, uma grande quantidade de alimentos é perdida ou desperdiçada, enquanto muitas pessoas ainda enfrentam dificuldade alimentar. Um dos fatores desse problema é a falta de informação e organização entre quem possui excedentes e as organizações que realizam as doações.

**Problema de negócio:** falta de uma ferramenta que cruze dados de excedentes de alimentos com informações de vulnerabilidade alimentar, ajudando a identificar onde as doações são mais necessárias e facilitando sua redistribuição antes que os alimentos sejam perdidos.

## 2. Objetivo Geral
Desenvolver um dashboard interativo, apoiado em coleta de dados via APIs/web scraping e em um LLM, que ajude organizações sociais, poder público e varejo a identificar oportunidades de doação e redistribuição de alimentos, priorizando regiões com maior insegurança alimentar.

## 3. Objetivos Específicos por etapa

**TP1**
- Definir o problema de negócio e o ODS ao qual o projeto está alinhado.
- Estruturar o projeto segundo CRISP-DM e TDSP.
- Organizar os diretórios e artefatos iniciais do projeto.
- Construir uma aplicação demo em Streamlit com título, descrição, links de referência e uma tabela de amostra de dados.

**TP2**
- Aprimorar e evoluir a aplicação desenvolvida no TP1.
- Configurar o ambiente de desenvolvimento (repositório no GitHub, `requirements.txt` e ambiente virtual).
- Implementar uma interface mais interativa (filtros por estado e tipo, cadastro de organizações e importação/download de CSV).
- Integrar novas funcionalidades para melhorar a experiência do usuário e a performance da aplicação (dados do IBGE e notícias por estado).

**TP3**
- Transformar o app em uma aplicação com múltiplas páginas e menu de navegação.
- Salvar em CSV as organizações cadastradas e as notícias coletadas.
- Criar uma API com FastAPI, com rotas de consulta (GET) e cadastro (POST), e fazer o app ler e gravar todos os dados por ela.
- Coletar dados do IBGE (API) e notícias (Beautiful Soup).
- Preparar os dados para o uso de LLMs (resumo de notícias e perguntas e respostas).

**TP4**
- Escolher e justificar um modelo de linguagem para rodar localmente.
- Integrar o modelo ao FastAPI, com a rota `POST /processar_texto`.
- Padronizar as respostas da API com Response Models.
- Tratar erros da API com exceções HTTP claras (ex.: 503 quando o modelo não está disponível).

## 4. Metas e Indicadores de Sucesso (KPIs)
Os principais indicadores do protótipo são: cruzar dados de excedentes e vulnerabilidade, atualizar as informações e realizar testes com organizações. O projeto está alinhado aos ODS 2, 12 e 17.

| Indicador | Situação no TP4 |
|---|---|
| Organizações na base | 17, com cadastro e importação de novas |
| Pontos no mapa | 20 |
| Estados cobertos | 11 |
| Rotas da API | 10 |
| Modelo de linguagem local | Qwen2.5-0.5B-Instruct, usado em `POST /processar_texto` |
| Cruzamento excedente × vulnerabilidade | Pendente |

## 5. Alinhamento com os ODS da Agenda 2030
- **ODS 2 – Fome Zero e Agricultura Sustentável (foco principal):** atua na meta 2.1 (acesso a alimentos seguros e nutritivos) ao conectar excedentes alimentares a populações em insegurança alimentar.
- **ODS 12 – Consumo e Produção Responsáveis:** atende à meta 12.3, que prevê reduzir pela metade o desperdício de alimentos per capita no varejo e no consumidor até 2030, ao dar visibilidade e agilizar o reaproveitamento de excedentes.
- **ODS 17 – Parcerias e Meios de Implementação:** o modelo depende da articulação entre setor privado, sociedade civil e poder público. A API facilita o compartilhamento de dados entre esses atores.

## 6. Público-Alvo
- **Primário:** bancos de alimentos e ONGs de combate à fome.
- **Secundário:** supermercados, feiras livres, CEASAs e produtores rurais.
- **Terciário:** gestores públicos municipais/estaduais de assistência social e segurança alimentar.

## 7. Stakeholders
- **Cientista de Dados:** coleta, tratamento e modelagem dos dados, integração com LLM.
- **Desenvolvedor de Aplicação:** desenvolvimento do dashboard em Streamlit e da API em FastAPI.
- **ONGs / Bancos de Alimentos:** usuários finais, validação dos requisitos e testes do protótipo.
- **Poder Público Municipal:** fornecimento de dados de apoio sobre vulnerabilidade social.

## 8. Metodologia: CRISP-DM x TDSP
O projeto utiliza CRISP-DM e TDSP de forma complementar. O CRISP-DM orienta as etapas de análise dos dados, enquanto o TDSP ajuda a organizar o desenvolvimento do projeto.

| TDSP | CRISP-DM |
|---|---|
| Business Understanding | Entendimento do Negócio |
| Data Acquisition and Understanding | Entendimento dos Dados |
| Modeling | Preparação e Modelagem |
| Deployment | Implantação |
| Customer Acceptance | Avaliação |

## 9. Arquitetura (TP3 e TP4)
- **Aplicação (Streamlit):** `app.py` (menu) e `pages/` com Início, Organizações, Mapa, Notícias, Dados IBGE e API e LLM.
- **API (FastAPI):** `api/main.py`, com documentação automática em `/docs`. É ela que lê e grava os CSVs.
- **Cliente da API:** `alimenta/cliente_api.py`. O app Streamlit não lê os CSVs diretamente: todas as páginas (organizações, mapa, notícias, IBGE e LLM) pedem os dados à API. Por isso a API precisa estar rodando para o app funcionar.
- **Modelo local:** `alimenta/llm_local.py` carrega e executa o modelo; `alimenta/llm_prep.py` monta os pedidos (prompts). `alimenta/` (dados, coleta, preparação para LLM), usados pela API e pelo script de coleta.
- **Coleta em lote:** `scripts/coletar_dados.py`.
- **Dados:** CSVs na pasta `Data/`.

**Selenium:** não foi usado. O feed RSS do Google News é um XML estático e a API do IBGE devolve JSON: nenhuma das duas fontes depende de JavaScript, de cliques ou de formulários, então `requests` e Beautiful Soup resolvem.

## 10. Integração com LLM local (TP4)
Foi integrado um modelo de linguagem que roda no próprio computador (HuggingFace Transformers), sem depender da nuvem.

- **Modelo:** `Qwen/Qwen2.5-0.5B-Instruct`, escolhido por ser leve, falar português e ter licença Apache 2.0. 
- **Rota:** `POST /processar_texto`, com respostas padronizadas (Response Models) e erros tratados (422, 502, 503, 504 e 500).

| Aplicação | Dado de entrada |
|---|---|
| Resumo de notícias | Manchetes coletadas por estado |
| Perguntas e respostas | Organizações cadastradas (ex.: "Onde posso doar alimentos em MG?") |

A página *API e LLM* permite usar o modelo e baixar um corpus em JSON com as organizações e as notícias.

## 11. Riscos
- Disponibilidade e granularidade limitada de dados públicos sobre desperdício de alimentos e insegurança alimentar no Brasil.
- Restrições de acesso/legalidade em web scraping de determinados sites.
- Os cadastros ficam em arquivos CSV, que podem se perder em hospedagens com disco temporário.
- O app depende da API: se ela estiver fora do ar, o app mostra um aviso e não carrega os dados.
- As notícias vêm de um feed do Google News, que pode mudar de formato.
- O modelo de linguagem é pequeno: pode errar ou inventar detalhes, e é lento. Por isso o pedido manda usar só o texto fornecido, e o resultado deve ser conferido.
- Na primeira vez, o modelo precisa ser baixado (cerca de 1 GB).

## 12. Uso de IA
Partes do código e da documentação foram feitas com apoio do Claude (Anthropic) e revisadas pela autora do projeto.
