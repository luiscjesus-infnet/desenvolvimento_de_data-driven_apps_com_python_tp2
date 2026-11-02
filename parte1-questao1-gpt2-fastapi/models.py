from pydantic import BaseModel


# Modelo de entrada: e o que o cliente envia no corpo da requisicao em JSON.
class GeracaoIn(BaseModel):
    prompt: str
    max_new_tokens: int = 50


# Modelo de saida: uso ele no response_model da rota para definir o que a API devolve.
class GeracaoOut(BaseModel):
    prompt: str
    texto_gerado: str
