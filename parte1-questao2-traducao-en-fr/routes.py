from fastapi import APIRouter, HTTPException

from models import TraducaoIn, TraducaoOut
from services import traduzir

router = APIRouter()


@router.get("/")
def status():
    return {"status": "ok", "modelo": "Helsinki-NLP/opus-mt-en-fr"}


@router.post("/traduzir", response_model=TraducaoOut)
def traduzir_texto(entrada: TraducaoIn):
    if not entrada.texto.strip():
        raise HTTPException(status_code=400, detail="O campo texto nao pode estar vazio.")

    traducao = traduzir(entrada.texto)
    return TraducaoOut(texto_original=entrada.texto, texto_traduzido=traducao)
