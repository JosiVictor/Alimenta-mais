import pandas as pd
import streamlit as st

from alimenta import config, dados

st.set_page_config(page_title="Organizações | Alimenta+", page_icon="🤝", layout="wide")
st.title("🤝 Organizações")

if "aviso" in st.session_state:
    st.success(st.session_state.pop("aviso"))

df = dados.carregar_organizacoes()

col_uf, col_tipo = st.columns(2)
uf = col_uf.selectbox("Estado", ["Todos"] + sorted(config.ESTADOS))
tipos = col_tipo.multiselect("Mostrar", config.TIPOS, default=config.TIPOS)

resultado = dados.filtrar_organizacoes(df, uf=None if uf == "Todos" else uf, tipos=tipos)

if resultado.empty:
    st.info("Nenhuma organização encontrada.")
else:
    st.dataframe(
        resultado,
        hide_index=True,
        use_container_width=True,
        column_config={"Site": st.column_config.LinkColumn("Site")},
    )
st.caption(f"{len(resultado)} organização(ões) exibida(s) de {len(df)} na base.")

st.download_button(
    "⬇️ Baixar base completa em CSV",
    df.to_csv(index=False).encode("utf-8"),
    "organizacoes_alimenta_mais.csv",
    "text/csv",
)

st.divider()
aba_form, aba_csv = st.tabs(["➕ Adicionar organização", "📁 Importar CSV"])

with aba_form:
    with st.form("nova_organizacao", clear_on_submit=True):
        nome = st.text_input("Nome")
        tipo = st.selectbox("Tipo", config.TIPOS)
        estado = st.selectbox("Estado", [config.NACIONAL] + sorted(config.ESTADOS))
        ajuda = st.text_input("Como ajudar")
        site = st.text_input("Site")
        enviar = st.form_submit_button("Adicionar")
    if enviar:
        try:
            dados.adicionar_organizacao(nome, tipo, estado, ajuda, site)
        except ValueError as erro:
            st.error(str(erro))
        else:
            st.session_state["aviso"] = f"'{nome.strip()}' foi adicionada e salva na base."
            st.rerun()

with aba_csv:
    st.write("O CSV precisa ter as colunas **Nome**, **Tipo** e **UF** (e, se quiser, *Como ajudar* e *Site*).")
    arquivo = st.file_uploader("Escolha um arquivo CSV", type="csv")
    if arquivo and st.button("Importar"):
        try:
            novas = pd.read_csv(arquivo, dtype=str, encoding="utf-8-sig")
            adicionadas, ignoradas = dados.adicionar_varias(novas)
        except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as erro:
            st.error(f"Não foi possível importar: {erro}")
        else:
            st.session_state["aviso"] = (
                f"{adicionadas} organização(ões) importada(s); {ignoradas} ignorada(s) (inválidas ou repetidas)."
            )
            st.rerun()
