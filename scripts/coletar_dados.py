"""Coleta notícias e a contagem de municípios de todos os estados e salva em Data/.

Uso:  python -m scripts.coletar_dados [--pausa 1.5]
"""
import argparse
import time

import pandas as pd
import requests

from alimenta import coleta, config, dados


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pausa", type=float, default=1.5, help="segundos entre requisições")
    args = parser.parse_args()

    contagem = []
    for uf in config.ESTADOS:
        print(f"[{uf}] coletando...")
        try:
            novas = coleta.buscar_noticias(uf)
            print(f"      {dados.salvar_noticias(novas)} notícia(s) nova(s)")
            contagem.append({"UF": uf, "Municípios": len(coleta.buscar_municipios(uf))})
        except requests.RequestException as erro:
            print(f"      falhou: {erro}")
        time.sleep(args.pausa)

    if contagem:
        dados.salvar_municipios_por_uf(pd.DataFrame(contagem))
        print("Salvo em Data/municipios_por_uf.csv")


if __name__ == "__main__":
    main()
