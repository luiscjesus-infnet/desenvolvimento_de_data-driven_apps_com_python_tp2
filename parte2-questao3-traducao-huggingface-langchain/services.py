import torch
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline

NOME_MODELO = "Helsinki-NLP/opus-mt-en-de"

dispositivo = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# O opus-mt traduz tudo o que recebe, entao meu template apenas repassa o texto.
# Se eu escrevesse uma instrucao aqui, do tipo "Translate to German:", ela tambem
# seria traduzida e apareceria na resposta.
prompt = PromptTemplate.from_template("{texto}")

_chain = None


def carregar_chain():
    global _chain
    if _chain is None:
        # Primeiro monto o pipeline do transformers, igual na Parte 1.
        pipe = pipeline(
            "translation",
            model=NOME_MODELO,
            device=dispositivo,
        )

        # Depois embrulho esse pipeline no HuggingFacePipeline, que e a classe do
        # LangChain. E isso que me permite usar invoke() e o operador | igual eu
        # faria com o Fake LLM ou com a OpenAI.
        llm = HuggingFacePipeline(pipeline=pipe)

        _chain = prompt | llm | StrOutputParser()

    return _chain


def traduzir(texto):
    chain = carregar_chain()
    resposta = chain.invoke({"texto": texto})
    return resposta.strip()
