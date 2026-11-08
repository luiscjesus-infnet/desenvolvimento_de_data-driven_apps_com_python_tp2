# Parte 2 - Questão 1: Chatbot simples com Fake LLM (FastAPI + LangChain)

Protótipo de chatbot que recebe um texto via FastAPI e devolve uma resposta simulada
pelo **Fake LLM** do LangChain (`FakeListLLM`). O chatbot responde a um conjunto de
perguntas pré-definidas e, quando não conhece a pergunta, devolve uma resposta padrão.

## Estrutura do projeto

```
parte2-questao1-chatbot-fake-llm/
+-- main.py            # ponto de entrada: cria a aplicação e registra o router
+-- routes.py          # rotas (endpoints) da API
+-- models.py          # modelos Pydantic de entrada e de saída
+-- services.py        # perguntas pré-definidas, prompt e cadeia com o Fake LLM
+-- requirements.txt   # dependências
+-- README.md
```

## Diagrama da arquitetura

```
   CLIENTE                         APLICACAO FASTAPI
  (Swagger,          +--------------------------------------------+
   curl ou           |                                            |
   requests)         |  routes.py                                 |
      |              |  recebe a requisicao e valida o campo      |
      |  POST /chat  |             |                              |
      |  {"mensagem"}|             v                              |
      |------------->|  models.py (Pydantic)  -> MensagemIn       |
      |              |             |                              |
      |              |             v                              |
      |              |  services.py                               |
      |              |  +--------------------------------------+  |
      |              |  | 1. normaliza o texto digitado        |  |
      |              |  | 2. busca a resposta no dicionario    |  |
      |              |  |    de perguntas pre-definidas        |  |
      |              |  +------------------+-------------------+  |
      |              |                     |                      |
      |              |                     v                      |
      |              |  CADEIA (chain) DO LANGCHAIN               |
      |              |  +--------------------------------------+  |
      |              |  |  PromptTemplate                      |  |
      |              |  |         |                            |  |
      |              |  |         v                            |  |
      |              |  |  FakeListLLM        <== PONTO DE     |  |
      |              |  |  (resposta simulada)    TROCA        |  |
      |              |  |         |                            |  |
      |              |  |         v                            |  |
      |              |  |  StrOutputParser                     |  |
      |              |  +------------------+-------------------+  |
      |              |                     |                      |
      |  200 OK      |                     v                      |
      |  {"resposta"}|  models.py (Pydantic)  -> MensagemOut      |
      |<-------------|                                            |
      |              +--------------------------------------------+

   O bloco marcado como PONTO DE TROCA e o unico que muda para usar
   um modelo real (ChatOpenAI ou HuggingFacePipeline).
```

### Etapas do fluxo de dados

| Etapa | Onde acontece | O que faz                                                         |
|-------|---------------|-------------------------------------------------------------------|
| 1     | Cliente       | Envia `POST /chat` com `{"mensagem": "..."}` em JSON              |
| 2     | `routes.py`   | Recebe a requisição e rejeita mensagem vazia (HTTP 400)           |
| 3     | `models.py`   | O Pydantic valida o corpo da requisição (`MensagemIn`)            |
| 4     | `services.py` | Normaliza o texto e procura a resposta no dicionário              |
| 5     | `services.py` | Monta a cadeia `PromptTemplate -> FakeListLLM -> StrOutputParser` |
| 6     | `services.py` | Chama `chain.invoke()` e recebe a resposta simulada               |
| 7     | `routes.py`   | Devolve `MensagemOut` como JSON com HTTP 200                      |

## Por que usar Fake LLM para testes rápidos

O Fake LLM é o equivalente de um *mock* no desenvolvimento de software: ele ocupa o
lugar do modelo de linguagem dentro da cadeia, mas devolve respostas que eu mesmo
defini. Isso é importante por cinco motivos:

1. **Velocidade.** Um modelo real precisa ser baixado, carregado na memória e
   executado. Mesmo um modelo pequeno leva alguns segundos por chamada. O Fake LLM
   responde na hora, então eu testo a aplicação inteira em um ciclo muito mais curto.
2. **Custo zero.** Não existe chamada a API paga. Durante o desenvolvimento eu faria
   dezenas de chamadas por hora, e todas elas gastariam tokens de uma API comercial
   sem nenhuma necessidade.
3. **Determinismo.** O modelo real tem aleatoriedade (`do_sample`, `temperature`), ou
   seja, a mesma entrada pode gerar saídas diferentes. Com resposta fixa eu consigo
   escrever teste automatizado e saber que, se o resultado mudou, foi o meu código que
   mudou, e não o modelo.
4. **Isolamento do que está sendo testado.** O que eu quero validar aqui é a API: as
   rotas, a validação do Pydantic, o tratamento de erro e o formato do JSON de saída.
   Nada disso depende da qualidade da resposta do modelo.
5. **Sem limite de taxa.** APIs comerciais limitam a quantidade de requisições por
   minuto. Em desenvolvimento isso atrapalha ou bloqueia o trabalho.

O ganho principal é que, por causa da interface padronizada do LangChain, trocar o
Fake LLM por um modelo real depois custa **uma linha**: tanto o `FakeListLLM` quanto o
`ChatOpenAI` e o `HuggingFacePipeline` são chamados com `invoke()` e podem ser
encadeados com o operador `|`. O prompt, o parser, as rotas e os modelos Pydantic
continuam iguais. As Questões 2 e 3 desta parte mostram exatamente essa troca.

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

4. Abrir a documentação automática (Swagger) em:

```
http://127.0.0.1:8000/docs
```

Como esta aplicação não baixa nenhum modelo, ela sobe em segundos.

## Endpoints

| Método | Rota         | Descrição                                       |
|--------|--------------|-------------------------------------------------|
| GET    | `/`          | Verifica se a API está no ar                    |
| GET    | `/perguntas` | Lista as perguntas que o chatbot sabe responder |
| POST   | `/chat`      | Recebe uma mensagem e devolve a resposta        |

### POST /chat

Corpo da requisição:

```json
{
  "mensagem": "O que e LangChain?"
}
```

Resposta:

```json
{
  "mensagem": "O que e LangChain?",
  "resposta": "LangChain e um framework que organiza modelos, prompts e ferramentas em uma interface padronizada."
}
```

Pergunta que o chatbot não conhece:

```json
{
  "mensagem": "Qual a cotacao do dolar hoje?"
}
```

```json
{
  "mensagem": "Qual a cotacao do dolar hoje?",
  "resposta": "Desculpe, ainda nao sei responder essa pergunta."
}
```

### Perguntas pré-definidas

- `ola`
- `bom dia`
- `qual o seu nome`
- `o que e langchain`
- `o que e fastapi`
- `tchau`

A comparação ignora maiúsculas, acentos e a pontuação final, então
`"O que é LangChain?"` e `"o que e langchain"` chegam na mesma resposta.

### Teste pelo terminal

```powershell
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d "{\"mensagem\": \"ola\"}"
```

## Códigos de status usados

| Código | Quando acontece                                                       |
|--------|-----------------------------------------------------------------------|
| 200    | Resposta devolvida com sucesso                                        |
| 400    | Campo `mensagem` vazio ou só com espaços                              |
| 422    | Corpo da requisição fora do formato esperado (validado pelo Pydantic) |
