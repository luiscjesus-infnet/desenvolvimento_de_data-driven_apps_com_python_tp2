from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Tradutor ingles para frances",
    description="API que traduz textos do ingles para o frances com o modelo Helsinki-NLP/opus-mt-en-fr.",
)

app.include_router(router)
