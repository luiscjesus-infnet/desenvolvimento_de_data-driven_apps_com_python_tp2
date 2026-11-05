from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Chatbot com Fake LLM",
    description="Prototipo de chatbot que responde perguntas pre-definidas usando o Fake LLM do LangChain.",
)

app.include_router(router)
