from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Gerador de texto com GPT-2",
    description="API que recebe uma frase e devolve a continuacao gerada pelo GPT-2.",
)

app.include_router(router)
