from fastapi import FastAPI

from routes import router

app = FastAPI(
    title="Tradutor ingles para frances com OpenAI via LangChain",
    description="API que traduz do ingles para o frances usando um modelo da OpenAI chamado pelo LangChain.",
)

app.include_router(router)
