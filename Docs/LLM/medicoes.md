# Medições do modelo local

Gerado automaticamente por `python -m scripts.medir_modelo` em 25/11/2026 22:06.
Modelo medido: `Qwen/Qwen2.5-0.5B-Instruct`.

## Computador usado
| Item | Valor |
|---|---|
| Sistema | Windows-10-10.0.19045-SP0 |
| Processador | AMD64 Family 25 Model 68 Stepping 1, AuthenticAMD |
| Núcleos (físicos / lógicos) | 8 / 16 |
| Memória RAM total | 5.7 GB |
| Placa de vídeo (GPU) | não detectada |
| Onde o modelo roda | CPU (o app não usa a GPU) |

## Carga do modelo
| Medida | Valor |
|---|---|
| Tempo para carregar na memória | 16.2 s |
| Memória do programa antes de carregar | 82 MB |
| Memória do programa depois de carregar | 868 MB |
| Memória do programa depois das respostas | 1012 MB |

O modelo já estava baixado no disco; o tempo do primeiro download depende da internet.

## Tempo de cada resposta
| Caso | Tempo |
|---|---|
| Resumo padrão | 15.2 s |
| Resumo para o gestor | 15.6 s |
| Resumo em tópicos | 20.6 s |

### Respostas geradas
**Resumo padrão**

> O texto descreve três iniciativas importantes no Brasil:

1. O projeto CRA (Conselho Regional de Agricultura) promove uma política nacional para reduzir perdas e desperdício de alimentos.
2. O Senado votou um projeto para facilitar doações de alimentos e combatê-lo de desperdício.
3. O Senado aprovou uma proposta para incentivar a doação de alimentos para reduzir o desperdício.

Essas iniciativas visam promover a sustentabilidade alimentar e combater o desperdício de alimentos na população brasileira.

**Resumo para o gestor**

> O texto menciona três projetos importantes relacionados ao tema de desempenho e conservação de alimentos:

1. O projeto criou uma política nacional para reduzir perdas e desperdício de alimentos no país.
2. O CRA votou sobre um projeto que permite doações de alimentos aos mais vulneráveis.
3. O Senado aprovou uma lei que incentiva a doação de alimentos para evitar perdas e desperdício.

Esses projetos têm como objetivo principal combater o desperdício de alimentos e promover a doação de alimentos para pessoas mais necessitadas.

**Resumo em tópicos**

> - Projeto cria política nacional para reduzir perdas e desperdício de alimentos - Portal da Câmara dos Deputados
- CRA vota projeto para facilitar doação de alimentos e combater desperdício - Senado
- Para reduzir desperdício de alimentos, lei prevê doações para pessoas vulneráveis - Confederação Nacional de Municípios (CNM)
- Senado Aprova: Incentivo à doação de alimentos para reduzir o desperdício - Senado Notícias - Senado
- Brasil Sem Desperdício realiza o primeiro encontro do Grupo de Trabalho de redistribuição de al - WWF Brasil
- Banco de Alimentos realiza parceria para combater o desperdício de alimentos - Prefeitura de Vitória
- Governo sanciona lei de combate a perdas e desperdícios de alimentos - Embrapa
- Brasil avança em políticas

## Exemplos reais da API
Respostas da rota `POST /processar_texto`, obtidas neste computador.

### Sucesso (200)
```json
{
  "tipo_analise": "resumo",
  "texto_processado": "- Projeto cria política nacional para reduzir perdas e desperdício de alimentos - Portal da Câmara dos Deputados\n- CRA vota projeto para facilitar doação de alimentos e combater desperdício - Senado\n- Para reduzir desperdício de alimentos, lei prevê doações para pessoas vulneráveis - Confederação Nacional de Municípios (CNM)\n- Senado Aprova: Incentivo à doação de alimentos para reduzir o desperdício — Senado Notícias - Senado\n- Brasil Sem Desperdício realiza o primeiro encontro do Grupo de Trabalho de redistribuição de al - WWF Brasil\n- Banco de Alimentos realiza parceria para combater o desperdício de alimentos - Prefeitura de Vitória\n- Governo sanciona lei de combate a perdas e desperdícios de alimentos - Embrapa\n- Brasil avança em políticas de alimentação e clima, diz estudo - portal do amazonas",
  "pergunta": null,
  "estilo": "padrao",
  "resultado": "O texto descreve três iniciativas importantes no Brasil:\n\n1. O projeto CRA (Conselho Regional de Agricultura) promove uma política nacional para reduzir perdas e desperdício de alimentos.\n2. O Senado votou um projeto para facilitar doações de alimentos e combatê-lo de desperdício.\n3. O Senado aprovou uma proposta para incentivar a doação de alimentos para reduzir o desperdício.\n\nEssas iniciativas visam promover a sustentabilidade alimentar e combater o desperdício de alimentos na população brasileira.",
  "modelo": "Qwen/Qwen2.5-0.5B-Instruct",
  "tempo_segundos": 15.61
}
```

### Texto muito curto (422)
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": [
        "body",
        "texto"
      ],
      "msg": "String should have at least 10 characters",
      "input": "curto",
      "ctx": {
        "min_length": 10
      }
    }
  ]
}
```

### Modelo que não existe (503)
```json
{
  "detail": "Não foi possível carregar o modelo 'modelo-que-nao-existe/teste': modelo-que-nao-existe/teste is not a local folder and is not a valid model identifier listed on 'https://huggingface.co/models'\nIf this is a private repository, make sure to pass a token having permission to this repo either by logging in with `hf auth login` or by passing `token=<your_token>`"
}
```

### Tempo esgotado (504)
```json
{
  "detail": "O modelo demorou mais de 0 segundos. Tente um texto menor ou uma resposta mais curta."
}
```
