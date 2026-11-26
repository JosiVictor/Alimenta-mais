# Data Summary Report — Alimenta+

## 1. Fontes de dados
| Fonte | Dado | Método | Uso | Status |
|---|---|---|---|---|
| FAOSTAT | Dados agrícolas e desperdício | API | Analisar perdas de alimentos | Planejado |
| IBGE – SIDRA | Dados sociais e demográficos | API | Identificar regiões vulneráveis | Planejado |
| ONGs e bancos de alimentos | Locais e informações sociais | Curadoria manual, com cadastro e importação de CSV no app | Encontrar pontos de coleta e distribuição | Em uso |
| IBGE – API de Localidades | Municípios e mesorregiões por estado | API | Página Dados IBGE | Em uso |
| Google News (RSS) | Manchetes sobre desperdício e doação | Web scraping (Beautiful Soup) | Páginas Notícias e Painel, e resumo com LLM | Em uso |

## 2. Dados utilizados por etapa
- **TP1:** amostra de dados simulados, para demonstrar a aplicação.
- **TP2:** organizações de doação e excedente, municípios por estado (IBGE) e notícias por estado.
- **TP3:** os mesmos dados, agora salvos em `Data/` e usados também pela API:
  - `organizacoes_alimenta_mais.csv`: 17 organizações (tipo Doação ou Excedente)
  - `pontos_alimenta_mais.csv`: 20 pontos com coordenadas, para o mapa
  - `noticias.csv`: notícias coletadas por estado
  - `municipios_por_uf.csv`: municípios por estado. Esse arquivo não vem no repositório: é criado ao rodar `python -m scripts.coletar_dados`.
- **TP5:** os dados passam a alimentar o **Painel**, que cruza organizações e notícias por estado (insight "onde falta organização?") e mostra os resumos gerados pela IA.
  - `resumos_alimenta_mais.csv`: resumos das notícias de cada estado (estado, estilo, texto, modelo, quantidade de notícias, data e tempo). É criado ao gerar o primeiro resumo.
  - Retrato da base em 25/11/2026: 17 organizações (8 de Doação e 9 de Excedente; 14 em 9 estados e 3 nacionais; sem organização estadual em AM e PA), 20 pontos em 11 estados e 31 notícias (21 com estado: BA 8, AM 8 e SP 5; 10 sem estado, da fase TP1). Esses números mudam a cada coleta ou cadastro.

## 3. Evolução da coleta (TP2 → TP5)
| Assunto | TP2 | TP3 em diante |
|---|---|---|
| IBGE | Quantidade de municípios do estado | Lista de municípios com mesorregião e microrregião, e ranking por mesorregião |
| Notícias | Manchetes do estado mostradas no app | Notícias salvas em CSV, com estado, fonte, data e link, sem repetição |
| Organizações | Cadastro e importação de CSV no app | Mesmo cadastro, agora gravado pela API e validado (tipo, UF e repetidas) |
| Coleta em lote | Não havia | Script que coleta os 11 estados de uma vez; no TP5, também um botão no Painel ("Buscar notícias de todos os estados") |
| Acesso aos dados | O app lia os dados direto | O app lê e grava tudo pela API |

## 4. Cuidados
- Utilizar fontes públicas e confiáveis.
- Evitar dados pessoais.
- Verificar a atualização dos dados.
- Respeitar as regras dos sites durante o web scraping.
- Organizações e notícias repetidas não são salvas duas vezes.
- As coordenadas do mapa são aproximadas (capital de cada estado), e a veracidade das notícias não é verificada.
- O projeto cobre 11 estados, apenas parte do país.
- O resumo usa só as manchetes, não o texto completo das notícias.

## 5. Uso com LLM (TP4 e TP5)
As manchetes e as descrições das organizações são enviadas, como texto, ao modelo local para o resumo de notícias e para perguntas e respostas sobre onde doar. Nada é enviado para a nuvem. As perguntas e respostas livres não são salvas. A página API e LLM (Assistente com IA no menu) também gera o corpus em JSONL com esses dados. O modelo escolhido está em `Docs/LLM/escolha_do_modelo.md`.

**No TP5**, o modelo resume até 12 manchetes recentes do estado escolhido, em três estilos de prompt (padrão, para o gestor público e em tópicos). O resumo é guardado em `resumos_alimenta_mais.csv` junto do modelo usado e da quantidade de notícias, e o Painel mostra as manchetes usadas ao lado do resumo, para conferência.
