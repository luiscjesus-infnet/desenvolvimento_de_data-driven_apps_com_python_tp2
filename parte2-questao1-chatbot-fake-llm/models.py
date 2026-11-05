from pydantic import BaseModel


class MensagemIn(BaseModel):
    mensagem: str


class MensagemOut(BaseModel):
    mensagem: str
    resposta: str
