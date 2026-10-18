"""Leitura e gravação dos CSVs do projeto (fonte única usada pelo app e pela API)."""
import pandas as pd

from . import config


def _ler_csv(arquivo: str, colunas: list[str]) -> pd.DataFrame:
    caminho = config.pasta_dados() / arquivo
    if not caminho.exists():
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig").fillna("")
    for coluna in colunas:
        if coluna not in df.columns:
            df[coluna] = ""
    return df[colunas]


def _salvar_csv(df: pd.DataFrame, arquivo: str) -> None:
    caminho = config.pasta_dados() / arquivo
    temporario = caminho.with_suffix(".tmp")
    df.to_csv(temporario, index=False, encoding="utf-8")
    temporario.replace(caminho)


# ---------------------------------------------------------------- organizações
def carregar_organizacoes() -> pd.DataFrame:
    return _ler_csv(config.ARQ_ORGANIZACOES, config.COLUNAS_ORGANIZACOES)


def normalizar_uf(uf: str) -> str:
    """Devolve a UF em maiúsculas ou 'Nacional'. Levanta ValueError se for inválida."""
    uf = (uf or "").strip()
    if uf.lower() == config.NACIONAL.lower():
        return config.NACIONAL
    if uf.upper() in config.ESTADOS:
        return uf.upper()
    raise ValueError(f"UF inválida: '{uf}'. Use {', '.join(config.ESTADOS)} ou Nacional.")


def _chave(nome: str, tipo: str, uf: str) -> tuple[str, str, str]:
    return (nome.strip().lower(), tipo, uf)


def adicionar_organizacao(nome: str, tipo: str, uf: str, como_ajudar: str = "", site: str = "") -> dict:
    """Valida e grava uma organização. Levanta ValueError se inválida ou duplicada."""
    nome = (nome or "").strip()
    if len(nome) < 2:
        raise ValueError("Digite o nome da organização.")
    if tipo not in config.TIPOS:
        raise ValueError(f"Tipo inválido: '{tipo}'. Use {' ou '.join(config.TIPOS)}.")
    uf = normalizar_uf(uf)

    df = carregar_organizacoes()
    existentes = {_chave(n, t, u) for n, t, u in zip(df["Nome"], df["Tipo"], df["UF"])}
    if _chave(nome, tipo, uf) in existentes:
        raise ValueError("Essa organização já está cadastrada.")

    nova = {
        "Nome": nome,
        "Tipo": tipo,
        "UF": uf,
        "Como ajudar": (como_ajudar or "").strip(),
        "Site": (site or "").strip(),
    }
    df = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
    _salvar_csv(df, config.ARQ_ORGANIZACOES)
    return nova


def adicionar_varias(novas: pd.DataFrame) -> tuple[int, int]:
    """Importa um DataFrame (colunas Nome, Tipo, UF + opcionais). Retorna (adicionadas, ignoradas)."""
    faltando = [c for c in ("Nome", "Tipo", "UF") if c not in novas.columns]
    if faltando:
        raise ValueError(f"O CSV precisa ter as colunas Nome, Tipo e UF (faltando: {', '.join(faltando)}).")
    adicionadas = ignoradas = 0
    for _, linha in novas.fillna("").iterrows():
        try:
            adicionar_organizacao(
                str(linha["Nome"]),
                str(linha["Tipo"]),
                str(linha["UF"]),
                str(linha.get("Como ajudar", "")),
                str(linha.get("Site", "")),
            )
            adicionadas += 1
        except ValueError:
            ignoradas += 1
    return adicionadas, ignoradas


def filtrar_organizacoes(df: pd.DataFrame, uf: str | None = None, tipos: list[str] | None = None,
                         incluir_nacional: bool = True) -> pd.DataFrame:
    if tipos:
        df = df[df["Tipo"].isin(tipos)]
    if uf:
        mascara = df["UF"] == uf
        if incluir_nacional:
            mascara |= df["UF"] == config.NACIONAL
        df = df[mascara]
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------- pontos
def carregar_pontos() -> pd.DataFrame:
    df = _ler_csv(config.ARQ_PONTOS, config.COLUNAS_PONTOS)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    return df.dropna(subset=["lat", "lon"]).reset_index(drop=True)


def filtrar_pontos(df: pd.DataFrame, uf: str | None = None, tipos: list[str] | None = None) -> pd.DataFrame:
    if tipos:
        df = df[df["Tipo"].isin(tipos)]
    if uf:
        df = df[df["UF"] == uf]
    return df.reset_index(drop=True)


# -------------------------------------------------------------------- notícias
def carregar_noticias(uf: str | None = None, limite: int | None = None) -> pd.DataFrame:
    df = _ler_csv(config.ARQ_NOTICIAS, config.COLUNAS_NOTICIAS)
    if uf:
        df = df[df["UF"] == uf]
    if limite:
        df = df.head(limite)
    return df.reset_index(drop=True)


def salvar_noticias(novas: pd.DataFrame) -> int:
    """Junta notícias novas às já salvas (sem repetir o mesmo link). Retorna quantas são novas."""
    atuais = _ler_csv(config.ARQ_NOTICIAS, config.COLUNAS_NOTICIAS)
    links = set(atuais["Link"])
    inéditas = novas[~novas["Link"].isin(links)].drop_duplicates(subset="Link")
    total = pd.concat([inéditas[config.COLUNAS_NOTICIAS], atuais], ignore_index=True)
    _salvar_csv(total, config.ARQ_NOTICIAS)
    return len(inéditas)


# ----------------------------------------------------------- municípios por UF
def carregar_municipios_por_uf() -> pd.DataFrame:
    return _ler_csv(config.ARQ_MUNICIPIOS_UF, config.COLUNAS_MUNICIPIOS_UF)


def salvar_municipios_por_uf(df: pd.DataFrame) -> None:
    _salvar_csv(df[config.COLUNAS_MUNICIPIOS_UF], config.ARQ_MUNICIPIOS_UF)
