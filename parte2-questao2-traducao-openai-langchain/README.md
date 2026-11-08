# Parte 2 - Questão 2: Tradução inglês -> francês com OpenAI via LangChain

API em FastAPI que recebe um texto em inglês, traduz para o francês usando um
**modelo da OpenAI chamado pelo LangChain** e devolve a tradução em JSON.

Faz o mesmo trabalho da Questão 2 da Parte 1, mas em vez de rodar um modelo local
com `transformers`, a tradução é feita por um modelo que roda na nuvem e é acessado
por API.

## Estrutura do projeto

```
parte2-questao2-traducao-openai-langchain/
+-- main.py            # ponto de entrada: cria a aplicação e registra o router
+-- routes.py          # rotas (endpoints) da API
+-- models.py          # modelos Pydantic de entrada e de saída
+-- services.py        # prompt, cliente ChatOpenAI e cadeia do LangChain
+-- requirements.txt   # dependências
+-- README.md
```

## Diagrama da arquitetura

```
                           MINHA MAQUINA / MEU SERVIDOR
  CLIENTE        +--------------------------------------------------+
 (Swagger,       |                                                  |
  curl ou        |   FASTAPI                                        |
  requests)      |   +------------------------------------------+   |
     |           |   | routes.py                                |   |
     | POST      |   |  - valida o campo texto                  |   |
     | /traduzir |   |  - trata os erros (400 / 500 / 503)      |   |
     |---------->|   | models.py (Pydantic)                     |   |
     | {"texto"} |   |  - TraducaoIn  (entrada)                 |   |
     |           |   |  - TraducaoOut (saida)                   |   |
     |           |   +--------------------+---------------------+   |
     |           |                        |                         |
     |           |                        v                         |
     |           |   LANGCHAIN (services.py)                        |
     |           |   +------------------------------------------+   |
     |           |   | PromptTemplate                           |   |
     |           |   |  "Translate ... {texto} ..."             |   |
     |           |   |              |                           |   |
     |           |   |              v                           |   |
     |           |   | ChatOpenAI  (model, api_key, base_url,   |   |
     |           |   |              temperature=0)              |   |
     |           |   |              |                           |   |
     |           |   |              v                           |   |
     |           |   | StrOutputParser                          |   |
     |           |   +--------------------+---------------------+   |
     |           |                        |                         |
     |           +------------------------|-------------------------+
     |                                    |
     |                        HTTPS       |  requisicao com
     |                                    |  a chave de API
     |                                    v
     |                    +--------------------------------------+
     |                    |   API DA OPENAI (nuvem)              |
     |                    |   modelo openai/gpt-oss-20b          |
     |                    |   - recebe o prompt                  |
     |                    |   - gera a traducao                  |
     |                    |   - cobra/conta os tokens usados     |
     |                    +------------------+-------------------+
     |                                       |
     |  200 OK                               |  resposta JSON
     |  {"texto_traduzido": ...}             v
     |<--------------------------------------+

  Componentes principais:
    FastAPI    -> expoe o endpoint HTTP, valida a entrada e trata erros
    LangChain  -> monta o prompt, chama o modelo e converte a saida em texto
    OpenAI     -> executa o modelo de linguagem e devolve a traducao
```

### Etapas do fluxo de dados

| Etapa | Componente     | O que faz                                                      |
|-------|----------------|----------------------------------------------------------------|
| 1     | Cliente        | Envia `POST /traduzir` com `{"texto": "..."}` em JSON          |
| 2     | FastAPI        | Valida o corpo com o Pydantic e rejeita texto vazio (HTTP 400) |
| 3     | LangChain      | `PromptTemplate` monta a instrução com o texto do usuário      |
| 4     | LangChain      | `ChatOpenAI` envia a requisição HTTPS para a API com a chave   |
| 5     | OpenAI (nuvem) | O modelo gera a tradução e devolve o JSON de resposta          |
| 6     | LangChain      | `StrOutputParser` extrai apenas o texto da resposta            |
| 7     | FastAPI        | Devolve `TraducaoOut` como JSON com HTTP 200                   |

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

3. Configurar a chave de API em uma variável de ambiente.

Usei o modelo da OpenAI pela API compatível da Groq (`console.groq.com`), que tem
plano gratuito, igual foi mostrado em aula. A chave é gerada em **API Keys**:

```powershell
$env:GROQ_API_KEY = "cole_sua_chave_aqui"
```

No Linux/macOS: `export GROQ_API_KEY="cole_sua_chave_aqui"`

A chave fica somente na variável de ambiente, nunca no código, e o `.gitignore`
também ignora arquivos `.env`.

4. Subir o servidor:

```powershell
uvicorn main:app --port 8000 --reload
```

5. Abrir a documentação automática (Swagger) em:

```
http://127.0.0.1:8000/docs
```

### Usando a API oficial da OpenAI

O `services.py` lê o modelo e a URL base de variáveis de ambiente, então para
apontar para a API paga da OpenAI eu não mexo no código:

```powershell
$env:GROQ_API_KEY    = "sua_chave_da_openai"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL    = "gpt-4o-mini"
```

Isso funciona porque a classe `ChatOpenAI` do LangChain é a mesma nos dois casos:
muda só o endereço e a chave.

## Endpoints

| Método | Rota        | Descrição                                      |
|--------|-------------|------------------------------------------------|
| GET    | `/`         | Verifica se a API está no ar e qual o modelo   |
| POST   | `/traduzir` | Recebe um texto em inglês e devolve em francês |

### POST /traduzir

Corpo da requisição:

```json
{
  "texto": "The cat is on the table."
}
```

Resposta:

```json
{
  "texto_original": "The cat is on the table.",
  "texto_traduzido": "Le chat est sur la table."
}
```

### Teste pelo terminal

```powershell
curl -X POST "http://127.0.0.1:8000/traduzir" -H "Content-Type: application/json" -d "{\"texto\": \"The cat is on the table.\"}"
```

## Decisões que tomei

- **`temperature=0`**: em tradução eu quero a saída mais previsível possível. Com
  temperatura alta o modelo escolhe os tokens de forma mais aleatória e a mesma
  frase pode sair traduzida de um jeito diferente a cada chamada.
- **Prompt pedindo somente a tradução**: sem essa instrução o modelo costuma
  responder com frases extras do tipo "Here is the translation:", o que sujaria o
  JSON de saída.
- **Cadeia criada uma única vez**: a cadeia e o cliente HTTP ficam guardados em uma
  variável do módulo. Montar o cliente em cada requisição somaria tempo à latência,
  que nesta aplicação já depende da rede.
- **`StrOutputParser`**: sem ele a resposta do modelo vem como um objeto com vários
  campos (inclusive a contagem de tokens). O parser deixa só o texto, que é o que a
  minha API precisa devolver.

## Códigos de status usados

| Código | Quando acontece                                                       |
|--------|-----------------------------------------------------------------------|
| 200    | Tradução feita com sucesso                                            |
| 400    | Campo `texto` vazio ou só com espaços                                 |
| 422    | Corpo da requisição fora do formato esperado (validado pelo Pydantic) |
| 500    | A variável de ambiente com a chave de API não foi configurada         |
| 503    | A API do modelo não respondeu ou recusou a chamada                    |
