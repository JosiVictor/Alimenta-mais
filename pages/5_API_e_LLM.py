import requests
import streamlit as st

from alimenta import config, dados, llm_prep

st.set_page_config(page_title="API e LLM | Alimenta+", page_icon="🤖", layout="wide")
st.title("🤖 API e preparação para LLM")

aba_api, aba_llm = st.tabs(["API (FastAPI)", "Preparação para LLM"])

with aba_api:
    st.write("A API usa os mesmos CSVs do app. Para subir localmente:")
    st.code("uvicorn api.main:app --reload", language="bash")
    st.write("Documentação interativa em `http://localhost:8000/docs`. Rotas:")
    st.markdown(
        "| Método | Rota | Função |\n"
        "|---|---|---|\n"
        "| GET | `/organizacoes?uf=SP&tipo=Doação` | Lista organizações (filtros opcionais) |\n"
        "| POST | `/organizacoes` | Cadastra uma organização |\n"
        "| GET | `/pontos` | Pontos com latitude/longitude |\n"
        "| GET | `/noticias?uf=SP&limite=5` | Notícias já coletadas |\n"
        "| GET | `/health` | Verifica se a API está no ar |"
    )
    st.code(
        'curl -X POST http://localhost:8000/organizacoes -H "Content-Type: application/json" '
        '-d \'{"nome": "Banco de Alimentos de Recife", "tipo": "Doação", "uf": "PE"}\'',
        language="bash",
    )
    url = st.text_input("Testar uma rota (a API precisa estar rodando)", "http://localhost:8000/organizacoes?uf=SP")
    if st.button("Fazer requisição"):
        try:
            resposta = requests.get(url, timeout=5)
            st.write(f"Status: {resposta.status_code}")
            st.json(resposta.json())
        except (requests.RequestException, ValueError):
            st.warning("Não consegui acessar a API nesse endereço.")

with aba_llm:
    st.write(
        "Os dados do projeto alimentam as tarefas de LLM da próxima etapa. "
        "Aqui estão os prompts que poderiam ser enviados."
    )
    uf = st.selectbox("Estado", sorted(config.ESTADOS), format_func=lambda s: f"{s} - {config.ESTADOS[s]}")
    estado = config.ESTADOS[uf]
    orgs = dados.filtrar_organizacoes(dados.carregar_organizacoes(), uf=uf)
    noticias = dados.carregar_noticias(uf=uf, limite=8)

    uso = st.radio("Aplicação", ["Resumo de notícias", "Perguntas e respostas"])
    if uso == "Resumo de notícias":
        prompt = llm_prep.prompt_resumo(noticias, estado)
    else:
        pergunta = st.text_input("Pergunta", f"Onde posso doar alimentos em {estado}?")
        prompt = llm_prep.prompt_perguntas_respostas(pergunta, orgs)
    st.code(prompt, language="text")

    corpus = llm_prep.corpus_jsonl(dados.carregar_organizacoes(), dados.carregar_noticias())
    st.download_button("⬇️ Baixar corpus (JSONL)", corpus.encode("utf-8"), "corpus_alimenta_mais.jsonl", "application/json")
