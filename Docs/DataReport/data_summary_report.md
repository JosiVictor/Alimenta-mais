# Data Summary Report — Alimenta+

## 1. Fontes de dados

| Fonte | Dado | Método | Uso | Status |
|---|---|---|---|---|
| FAOSTAT | Dados agrícolas e desperdício | API | Analisar perdas de alimentos | Planejado |
| IBGE – SIDRA | Dados sociais e demográficos | API | Identificar regiões vulneráveis | Planejado |
| ONGs e bancos de alimentos | Locais e informações sociais | Curadoria manual, com cadastro e importação de CSV no app | Encontrar pontos de coleta e distribuição | Em uso |
| IBGE – API de Localidades | Municípios e mesorregiões por estado | API | Página *Dados IBGE* | Em uso |
| Google News (RSS) | Manchetes sobre desperdício e doação | Web scraping (Beautiful Soup) | Página *Notícias* e resumo com LLM | Em uso |

## 2. Dados utilizados por etapa
- **TP1:** amostra de dados simulados, para demonstrar a aplicação.
- **TP2:** organizações de doação e excedente, municípios por estado (IBGE) e notícias por estado.
- **TP3:** os mesmos dados, agora salvos em `Data/` e usados também pela API:
  - `organizacoes_alimenta_mais.csv`: 17 organizações (tipo *Doação* ou *Excedente*)
  - `pontos_alimenta_mais.csv`: 20 pontos com coordenadas, para o mapa
  - `noticias.csv`: notícias coletadas por estado
  - `municipios_por_uf.csv`: municípios por estado (gerado pelo script de coleta)

## 3. Cuidados
- Utilizar fontes públicas e confiáveis.
- Evitar dados pessoais.
- Verificar a atualização dos dados.
- Respeitar as regras dos sites durante o web scraping.
- Organizações e notícias repetidas não são salvas duas vezes.
- As coordenadas do mapa são aproximadas (capital de cada estado), e a veracidade das notícias não é verificada.
- O projeto cobre 11 estados, apenas parte do país.

## 4. Uso previsto com LLMs
As manchetes e as descrições das organizações serão usadas no resumo de notícias e em perguntas e respostas sobre onde doar.
