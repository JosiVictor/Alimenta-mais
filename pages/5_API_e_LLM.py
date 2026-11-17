import streamlit as st

from alimenta import cliente_api, config, llm_prep

st.set_page_config(page_title="Assistente LLM | Alimenta+", page_icon="🤖", layout="wide")
st.title("🤖 Assistente com LLM local")

uf = st.selectbox("Estado", sorted(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}")
estado = config.ESTADOS[uf]
orgs = cliente_api.organizacoes(uf=uf)
noticias = cliente_api.noticias(uf=uf, limite=8)

uso = st.radio("O que você quer fazer?", ["Resumir as notícias", "Perguntar sobre as organizações"])
if uso == "Resumir as notícias":
    tarefa, pergunta = "resumo", None
    texto = "\n".join(f"- {t}" for t in noticias["Título"])
    if not texto:
        st.info("Não há notícias salvas para esse estado. Colete na página Notícias.")
else:
    tarefa = "pergunta_resposta"
    sugestoes = [
        f"Onde posso doar alimentos em {estado}?",
        f"Quais organizações recebem doações em {estado}?",
        f"Quais são as centrais de excedente em {estado}?",
        "Existe alguma organização de atuação nacional?",
        "Qual organização tem site?",
    ]
    if not orgs.empty:
        sugestoes.append(f"Como posso ajudar {orgs['Nome'].iloc[0]}?")
    outra = "✏️ Escrever minha própria pergunta"
    escolha = st.selectbox("Escolha uma pergunta", sugestoes + [outra])
    pergunta = st.text_input("Digite sua pergunta") if escolha == outra else escolha
    texto = llm_prep.contexto_organizacoes(orgs)

pronto = bool(texto.strip()) and (tarefa == "resumo" or bool((pergunta or "").strip()))
if pronto:
    with st.expander("Ver o texto enviado ao modelo"):
        st.code(llm_prep.mensagens(tarefa, texto, pergunta)[1]["content"], language="text")

if st.button("✨ Gerar com o modelo local", disabled=not pronto):
    try:
        with st.spinner("Gerando... Na primeira vez o modelo é baixado (cerca de 1 GB) e pode levar vários minutos."):
            resultado = cliente_api.processar_texto(texto, tarefa, pergunta)
    except cliente_api.ApiErro as erro:
        st.error(f"Erro {erro.status}: {erro.detalhe}")
    else:
        st.success(resultado["resultado"])
        st.caption(f"{resultado['modelo']} · {resultado['tempo_segundos']} segundos")

st.divider()
corpus = llm_prep.corpus_jsonl(cliente_api.organizacoes(), cliente_api.noticias())
st.download_button("⬇️ Baixar corpus (JSONL)", corpus.encode("utf-8"), "corpus_alimenta_mais.jsonl", "application/json")
