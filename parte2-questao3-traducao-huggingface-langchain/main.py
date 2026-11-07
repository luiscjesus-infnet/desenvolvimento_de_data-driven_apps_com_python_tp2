from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Tradutor ingles para alemao com HuggingFace via LangChain",
    description="API que traduz do ingles para o alemao com o modelo Helsinki-NLP/opus-mt-en-de gerenciado pelo LangChain.",
)

app.include_router(router)
