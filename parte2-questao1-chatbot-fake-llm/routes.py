from fastapi import APIRouter, HTTPException

from models import MensagemIn, MensagemOut
from services import perguntas_conhecidas, responder

router = APIRouter()


@router.get("/")
def status():
    return {"status": "ok", "modelo": "FakeListLLM (LangChain)"}


@router.get("/perguntas")
def listar_perguntas():
    return {"perguntas": perguntas_conhecidas()}


@router.post("/chat", response_model=MensagemOut)
def chat(entrada: MensagemIn):
    if not entrada.mensagem.strip():
        raise HTTPException(status_code=400, detail="O campo mensagem nao pode estar vazio.")

    resposta = responder(entrada.mensagem)
    return MensagemOut(mensagem=entrada.mensagem, resposta=resposta)
