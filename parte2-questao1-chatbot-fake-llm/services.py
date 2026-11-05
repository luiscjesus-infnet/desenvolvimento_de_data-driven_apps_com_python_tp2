import unicodedata

from langchain_core.language_models.fake import FakeListLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

# Perguntas pre-definidas que o chatbot sabe responder.
RESPOSTAS = {
    "ola": "Ola! Eu sou um chatbot de teste criado com Fake LLM.",
    "bom dia": "Bom dia! Como posso ajudar?",
    "qual o seu nome": "Meu nome e ChatFake, sou um prototipo da disciplina.",
    "o que e langchain": (
        "LangChain e um framework que organiza modelos, prompts e ferramentas "
        "em uma interface padronizada."
    ),
    "o que e fastapi": "FastAPI e um framework Python para criar APIs de forma rapida.",
    "tchau": "Tchau! Ate a proxima.",
}

RESPOSTA_PADRAO = "Desculpe, ainda nao sei responder essa pergunta."

prompt = PromptTemplate.from_template("Pergunta do usuario: {pergunta}")


def normalizar(texto):
    # Deixo tudo em minusculo e tiro acentos e pontuacao do final para o usuario
    # nao precisar digitar exatamente igual a chave do dicionario.
    texto = texto.strip().lower().rstrip("?!.")
    sem_acento = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sem_acento if not unicodedata.combining(c))


def responder(pergunta):
    texto = RESPOSTAS.get(normalizar(pergunta), RESPOSTA_PADRAO)

    # O FakeListLLM devolve as respostas da lista na ordem em que foram passadas.
    # Como eu ja escolhi a resposta no dicionario, monto ele com um item so.
    fake_llm = FakeListLLM(responses=[texto])

    # Pedi ajuda ao Claude para montar a cadeia abaixo.
    # Esta e a cadeia do LangChain: prompt -> modelo -> saida em texto.
    # Para usar um modelo real depois, eu troco apenas o fake_llm.
    chain = prompt | fake_llm | StrOutputParser()

    return chain.invoke({"pergunta": pergunta})


def perguntas_conhecidas():
    return sorted(RESPOSTAS.keys())
