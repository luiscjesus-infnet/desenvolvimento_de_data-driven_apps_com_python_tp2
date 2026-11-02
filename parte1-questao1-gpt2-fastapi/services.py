import torch
from transformers import pipeline, GenerationConfig

NOME_MODELO = "openai-community/gpt2"

# Se a maquina tiver placa de video eu uso a GPU, senao uso a CPU mesmo.
dispositivo = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Guardo o pipeline nesta variavel para carregar o modelo uma unica vez.
# Se eu carregasse dentro da rota, o modelo seria montado de novo em cada
# requisicao e a API ficaria muito lenta.
_pipe = None


def carregar_pipeline():
    global _pipe
    if _pipe is None:
        _pipe = pipeline(
            "text-generation",
            model=NOME_MODELO,
            device=dispositivo,
        )
    return _pipe


def gerar_texto(prompt, max_new_tokens=50):
    pipe = carregar_pipeline()

    # Esses parametros controlam como o modelo escolhe os proximos tokens.
    # Pedi ajuda do Claude para entender o que cada um deles faz.
    config = GenerationConfig(
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
    )

    resultado = pipe(
        prompt,
        generation_config=config,
        clean_up_tokenization_spaces=True,
    )

    # O pipeline devolve uma lista de dicionarios. Como enviei um prompt so,
    # pego a primeira posicao e a chave generated_text.
    return resultado[0]["generated_text"]
