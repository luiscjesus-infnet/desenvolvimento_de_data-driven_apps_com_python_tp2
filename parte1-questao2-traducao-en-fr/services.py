import re

import torch
from transformers import pipeline

NOME_MODELO = "Helsinki-NLP/opus-mt-en-fr"

dispositivo = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_pipe = None


def carregar_pipeline():
    global _pipe
    if _pipe is None:
        _pipe = pipeline(
            "translation",
            model=NOME_MODELO,
            device=dispositivo,
        )
    return _pipe


def quebrar_em_frases(texto):
    # Montei esta funcao com apoio do Claude.
    # O modelo tem um limite de tokens por vez, entao quebro o texto nos pontos
    # finais, nas exclamacoes e nas interrogacoes. Assim consigo traduzir
    # tambem textos longos, e nao so frases curtas.
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    return [frase for frase in frases if frase]


def traduzir(texto):
    pipe = carregar_pipeline()

    frases = quebrar_em_frases(texto)

    # O pipeline aceita uma lista e devolve uma traducao para cada item dela.
    resultado = pipe(frases)
    traducoes = [item["translation_text"] for item in resultado]

    return " ".join(traducoes)
