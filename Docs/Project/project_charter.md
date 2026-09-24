# Project Charter — Alimenta+

## 1. Contexto e Problema de Negócio
No Brasil, uma grande quantidade de alimentos é perdida ou desperdiçada, enquanto muitas pessoas ainda enfrentam dificuldade alimentar. Um dos fatores desse problema é a falta de informação e organização entre quem possui excedentes e as organizações que realizam as doações.

Problema de negócio: falta de uma ferramenta que cruze dados de excedentes de alimentos com informações de vulnerabilidade alimentar, ajudando a identificar onde as doações são mais necessárias e facilitando sua redistribuição antes que os alimentos sejam perdidos.

## 2. Objetivo Geral

Desenvolver um dashboard interativo, apoiado em coleta de dados via APIs/web scraping e em um LLM (engenharia de prompts), que ajude organizações sociais, poder público e varejo a identificar oportunidades de doação e
redistribuição de alimentos, priorizando regiões com maior insegurança alimentar.

## 3. Objetivos Específicos (TP1)

- Definir o problema de negócio e o ODS ao qual o projeto está alinhado.
- Estruturar o projeto segundo CRISP-DM e TDSP.
- Organizar os diretórios e artefatos iniciais do projeto.
- Construir uma aplicação demo em Streamlit com título, descrição, links de referência e uma tabela de amostra
  de dados.

## 4. Metas e Indicadores de Sucesso (KPIs)

Os principais indicadores do protótipo serão: cruzar dados de excedentes e vulnerabilidade em municípios, atualizar as informações e realizar testes com organizações. O projeto estará alinhado aos ODS 2, 12 e 17.

## 5. Alinhamento com os ODS da Agenda 2030

- **ODS 2 – Fome Zero e Agricultura Sustentável (foco principal):** o projeto atua diretamente na meta 2.1
  (acesso a alimentos seguros e nutritivos) ao conectar excedentes alimentares a populações em insegurança
  alimentar.
- **ODS 12 – Consumo e Produção Responsáveis:** atende à meta 12.3, que prevê **reduzir pela metade o
  desperdício de alimentos per capita** no varejo e no consumidor até 2030, ao dar visibilidade e agilizar o
  reaproveitamento de excedentes.
- **ODS 17 – Parcerias e Meios de Implementação:** o modelo de negócio depende da articulação entre setor
  privado (varejo/produtores), sociedade civil (ONGs/bancos de alimentos) e poder público (dados de
  vulnerabilidade social), reforçando parcerias multissetoriais.

## 6. Público-Alvo

- **Primário:** bancos de alimentos e ONGs de combate à fome (ex.: Mesa Brasil SESC, bancos de alimentos
  municipais), que precisam identificar rapidamente fontes de doação.
- **Secundário:** supermercados, feiras livres, CEASAs e produtores rurais, que precisam de um canal simples
  para destinar excedentes antes do descarte.
- **Terciário:** gestores públicos municipais/estaduais de assistência social e segurança alimentar, que usam
  os dados para priorizar políticas públicas.

## 7. Stakeholders
- **Cientista de Dados:** coleta, tratamento e modelagem dos dados, integração com LLM.
- **Desenvolvedor de Aplicação:** desenvolvimento do dashboard em Streamlit.
- **ONGs / Bancos de Alimentos:** usuários finais, validação dos requisitos e testes do protótipo.
- **Poder Público Municipal:** fornecimento de dados de apoio sobre vulnerabilidade social.

## 8. Metodologia: CRISP-DM x TDSP

O projeto utiliza **CRISP-DM** e **TDSP** de forma complementar. O CRISP-DM orienta as etapas de análise dos dados, enquanto o TDSP ajuda a organizar o desenvolvimento do projeto.

| TDSP | CRISP-DM |
| **Business Understanding** | Entendimento do Negócio |
| **Data Acquisition and Understanding** | Entendimento dos Dados |
| **Modeling** | Preparação e Modelagem |
| **Deployment** | Implantação |
| **Customer Acceptance** | Avaliação |

## 9. Riscos Iniciais

- Disponibilidade e granularidade limitada de dados públicos sobre desperdício de alimentos no Brasil.
- Restrições de acesso/legalidade em web scraping de determinados sites.