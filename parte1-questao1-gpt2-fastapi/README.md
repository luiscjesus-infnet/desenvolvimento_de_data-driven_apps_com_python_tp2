# Parte 1 - Questão 1: Geração de texto com GPT-2 (FastAPI + HuggingFace)

API em FastAPI que recebe uma frase em JSON, usa o modelo **GPT-2** da HuggingFace
através da biblioteca `transformers` e devolve a continuação do texto em JSON.

## Estrutura do projeto

```
parte1-questao1-gpt2-fastapi/
+-- main.py            # ponto de entrada: cria a aplicação e registra o router
+-- routes.py          # rotas (endpoints) da API
+-- models.py          # modelos Pydantic de entrada e de saída
+-- services.py        # carga do pipeline do GPT-2 e geração do texto
+-- requirements.txt   # dependências
+-- README.md
```

Separei o código em arquivos por responsabilidade (estrutura *flat*): o `main.py`
só sobe a aplicação, o `routes.py` trata a requisição, o `models.py` define o
contrato de entrada e de saída e o `services.py` concentra o uso do modelo. Assim,
se eu trocar o modelo, mexo apenas no `services.py`.

## Como executar

1. Criar e ativar o ambiente virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

No Linux/macOS: `source .venv/bin/activate`

2. Instalar as dependências:

```powershell
python -m pip install -r requirements.txt
```

3. Subir o servidor:

```powershell
uvicorn main:app --port 8000 --reload
```

Na primeira execução o `transformers` baixa o GPT-2 (cerca de 500 MB) e guarda em
cache, por isso a primeira requisição demora mais que as seguintes.

4. Abrir a documentação automática (Swagger) em:

```
http://127.0.0.1:8000/docs
```

## Endpoints

| Método | Rota           | Descrição                                 |
|--------|----------------|-------------------------------------------|
| GET    | `/`            | Verifica se a API está no ar              |
| POST   | `/gerar-texto` | Recebe um prompt e devolve o texto gerado |

### POST /gerar-texto

Corpo da requisição:

```json
{
  "prompt": "Artificial intelligence is a technology that",
  "max_new_tokens": 50
}
```

O campo `max_new_tokens` é opcional (padrão 50) e limita o tamanho da resposta.

Resposta:

```json
{
  "prompt": "Artificial intelligence is a technology that",
  "texto_gerado": "Artificial intelligence is a technology that has been used in the industry for decades..."
}
```

### Teste pelo terminal

```powershell
curl -X POST "http://127.0.0.1:8000/gerar-texto" -H "Content-Type: application/json" -d "{\"prompt\": \"Artificial intelligence is a technology that\"}"
```

Ou em Python, com a biblioteca `requests`:

```python
import requests

url = "http://127.0.0.1:8000/gerar-texto"
dados = {"prompt": "Artificial intelligence is a technology that"}
resposta = requests.post(url, json=dados)
print(resposta.status_code)
print(resposta.json())
```

## Observações

- O GPT-2 foi treinado em inglês, então os melhores resultados vêm de prompts em inglês.
- O modelo está com `do_sample=True`, ou seja, cada chamada pode devolver um texto
  diferente para o mesmo prompt. Para ter sempre a mesma saída basta usar
  `do_sample=False` no `services.py`.
- O GPT-2 completa texto, não conversa: ele não foi treinado para responder perguntas
  como um chat. As limitações estão discutidas na Questão 4 da Parte 1.

## Códigos de status usados

| Código | Quando acontece                                                       |
|--------|-----------------------------------------------------------------------|
| 200    | Texto gerado com sucesso                                              |
| 400    | `prompt` vazio ou `max_new_tokens` fora da faixa de 1 a 200           |
| 422    | Corpo da requisição fora do formato esperado (validado pelo Pydantic) |
