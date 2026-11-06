from fastapi import APIRouter, HTTPException

from models import TraducaoIn, TraducaoOut
from services import NOME_MODELO, traduzir

router = APIRouter()


@router.get("/")
def status():
    return {"status": "ok", "modelo": NOME_MODELO}


@router.post("/traduzir", response_model=TraducaoOut)
def traduzir_texto(entrada: TraducaoIn):
    if not entrada.texto.strip():
        raise HTTPException(status_code=400, detail="O campo texto nao pode estar vazio.")

    try:
        traducao = traduzir(entrada.texto)
    except RuntimeError as erro:
        # Falta de chave de API e problema de configuracao do servidor, por isso 500.
        raise HTTPException(status_code=500, detail=str(erro))
    except Exception:
        # Se a API externa estiver fora do ar ou recusar a chamada, aviso o cliente
        # que o servico nao esta disponivel agora.
        raise HTTPException(
            status_code=503,
            detail="Nao foi possivel falar com a API do modelo. Tente novamente.",
        )

    return TraducaoOut(texto_original=entrada.texto, texto_traduzido=traducao)
