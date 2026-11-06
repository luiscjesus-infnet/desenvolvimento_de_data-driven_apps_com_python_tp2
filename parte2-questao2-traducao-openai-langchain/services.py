import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Uso o modelo da OpenAI pela API compativel da Groq, que tem plano gratuito.
# Para falar direto com a API oficial da OpenAI basta trocar a chave e a URL base
# nas variaveis de ambiente abaixo.
NOME_MODELO = os.environ.get("OPENAI_MODEL", "openai/gpt-oss-20b")
URL_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
CHAVE_API = os.environ.get("GROQ_API_KEY")

prompt = PromptTemplate(
    template=(
        "Translate the sentence below from English to French.\n"
        "Answer only with the translation, without any comment.\n\n"
        "Sentence: {texto}\n"
        "Translation:"
    ),
    input_variables=["texto"],
)

# Monto a cadeia uma unica vez e reaproveito em todas as requisicoes, para nao
# perder tempo criando o cliente da API a cada chamada.
_chain = None


def carregar_chain():
    global _chain
    if _chain is None:
        if not CHAVE_API:
            raise RuntimeError(
                "A variavel de ambiente GROQ_API_KEY nao esta definida."
            )

        # temperature=0 porque em traducao eu quero a resposta mais previsivel
        # possivel, e nao um texto criativo diferente a cada chamada.
        llm = ChatOpenAI(
            model=NOME_MODELO,
            api_key=CHAVE_API,
            base_url=URL_BASE,
            temperature=0,
        )

        # prompt -> modelo -> saida em texto puro
        _chain = prompt | llm | StrOutputParser()

    return _chain


def traduzir(texto):
    chain = carregar_chain()
    resposta = chain.invoke({"texto": texto})
    return resposta.strip()
