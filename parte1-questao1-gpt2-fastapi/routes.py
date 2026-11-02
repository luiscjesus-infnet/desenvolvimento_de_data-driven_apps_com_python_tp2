from fastapi import APIRouter, HTTPException

from models import GeracaoIn, GeracaoOut
from services import gerar_texto

router = APIRouter()


@router.get("/")
def status():
    return {"status": "ok", "modelo": "openai-community/gpt2"}


# Deixei a funcao sem async porque a chamada do modelo e bloqueante.
# Assim o FastAPI executa ela em uma thread separada e o servidor nao trava.
@router.post("/gerar-texto", response_model=GeracaoOut)
def gerar(entrada: GeracaoIn):
    if not entrada.prompt.strip():
        raise HTTPException(status_code=400, detail="O campo prompt nao pode estar vazio.")

    if entrada.max_new_tokens < 1 or entrada.max_new_tokens > 200:
        raise HTTPException(
            status_code=400,
            detail="O campo max_new_tokens deve ficar entre 1 e 200.",
        )

    texto = gerar_texto(entrada.prompt, entrada.max_new_tokens)
    return GeracaoOut(prompt=entrada.prompt, texto_gerado=texto)
