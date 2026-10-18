# Project Charter — Alimenta+

## 1. Contexto e Problema de Negócio
No Brasil, uma grande quantidade de alimentos é perdida ou desperdiçada, enquanto muitas pessoas ainda enfrentam dificuldade alimentar. Um dos fatores desse problema é a falta de informação e organização entre quem possui excedentes e as organizações que realizam as doações.

**Problema de negócio:** falta de uma ferramenta que cruze dados de excedentes de alimentos com informações de vulnerabilidade alimentar, ajudando a identificar onde as doações são mais necessárias e facilitando sua redistribuição antes que os alimentos sejam perdidos.

## 2. Objetivo Geral
Desenvolver um dashboard interativo, apoiado em coleta de dados via APIs/web scraping e em um LLM (engenharia de prompts), que ajude organizações sociais, poder público e varejo a identificar oportunidades de doação e redistribuição de alimentos, priorizando regiões com maior insegurança alimentar.

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
- Criar uma API com FastAPI, com rotas de consulta (GET) e cadastro (POST).
- Coletar dados do IBGE (API) e notícias (Beautiful Soup).
- Preparar os dados para o uso de LLMs (resumo de notícias e perguntas e respostas).

## 4. Metas e Indicadores de Sucesso (KPIs)
Os principais indicadores do protótipo são: cruzar dados de excedentes e vulnerabilidade, atualizar as informações e realizar testes com organizações. O projeto está alinhado aos ODS 2, 12 e 17.

| Indicador | Situação no TP3 |
|---|---|
| Organizações na base | 17, com cadastro e importação de novas |
| Pontos no mapa | 20 |
| Estados cobertos | 11 |
| Rotas da API | 5 |
| Cruzamento excedente × vulnerabilidade | Pendente |

O cruzamento com vulnerabilidade alimentar continua sendo a meta central. Na próxima etapa, será feita uma primeira versão no nível de estado, usando indicadores do IBGE; a análise por município dependerá da disponibilidade de dados.

## 5. Alinhamento com os ODS da Agenda 2030
- **ODS 2 – Fome Zero e Agricultura Sustentável (foco principal):** atua na meta 2.1 (acesso a alimentos seguros e nutritivos) ao conectar excedentes alimentares a populações em insegurança alimentar.
- **ODS 12 – Consumo e Produção Responsáveis:** atende à meta 12.3, que prevê reduzir pela metade o desperdício de alimentos per capita no varejo e no consumidor até 2030, ao dar visibilidade e agilizar o reaproveitamento de excedentes.
- **ODS 17 – Parcerias e Meios de Implementação:** o modelo depende da articulação entre setor privado, sociedade civil e poder público. A API facilita o compartilhamento de dados entre esses atores.

## 6. Público-Alvo
- **Primário:** bancos de alimentos e ONGs de combate à fome (ex.: Mesa Brasil SESC, bancos de alimentos municipais).
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

## 9. Arquitetura no TP3
- **Aplicação (Streamlit):** `app.py` (menu) e `pages/` com Início, Organizações, Mapa, Notícias, Dados IBGE e API e LLM.
- **API (FastAPI):** `api/main.py`, com documentação automática em `/docs`.
- **Módulos compartilhados:** `alimenta/`, usados pelo app e pela API.
- **Coleta em lote:** `scripts/coletar_dados.py`.
- **Dados:** CSVs na pasta `Data/`.

**Sobre o Selenium:** não foi usado, porque as fontes atuais (API do IBGE e feed RSS de notícias) não têm conteúdo dinâmico. Beautiful Soup e `requests` foram suficientes.

## 10. Preparação para LLMs (próxima etapa)

| Aplicação | Dado de entrada |
|---|---|
| Resumo de notícias | Manchetes coletadas por estado |
| Perguntas e respostas | Organizações cadastradas (ex.: "Onde posso doar alimentos em MG?") |

A página *API e LLM* mostra os prompts já montados e permite baixar um corpus em JSONL com as organizações e as notícias.

## 11. Riscos
- Disponibilidade e granularidade limitada de dados públicos sobre desperdício de alimentos e insegurança alimentar no Brasil.
- Restrições de acesso/legalidade em web scraping de determinados sites.
- Os cadastros ficam em arquivos CSV, que podem se perder em hospedagens com disco temporário.
- As notícias vêm de um feed do Google News, que pode mudar de formato.

## 12. Uso de IA
Partes do código foram feitas com apoio de IA e revisadas pela autora do projeto.