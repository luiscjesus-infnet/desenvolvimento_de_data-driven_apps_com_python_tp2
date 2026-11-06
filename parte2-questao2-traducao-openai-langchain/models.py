from pydantic import BaseModel


class TraducaoIn(BaseModel):
    texto: str


class TraducaoOut(BaseModel):
    texto_original: str
    texto_traduzido: str
