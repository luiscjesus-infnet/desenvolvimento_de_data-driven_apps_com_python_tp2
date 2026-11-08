# Parte 2 - Questão 3: Tradução inglês -> alemão com HuggingFace via LangChain

API em FastAPI que recebe um texto em inglês e devolve a tradução em alemão usando o
modelo **Helsinki-NLP/opus-mt-en-de**, com o **LangChain gerenciando a chamada ao
modelo** através da classe `HuggingFacePipeline`.

É a mesma ideia das Questões 2 da Parte 1 e 2 da Parte 2, mas aqui o modelo roda
localmente (como na Parte 1) e a chamada é padronizada pelo LangChain (como na
Questão 2 da Parte 2).

## Estrutura do projeto

```
parte2-questao3-traducao-huggingface-langchain/
+-- main.py            # ponto de entrada: cria a aplicação e registra o router
+-- routes.py          # rotas (endpoints) da API
+-- models.py          # modelos Pydantic de entrada e de saída
+-- services.py        # pipeline do transformers, HuggingFacePipeline e a cadeia
+-- requirements.txt   # dependências
+-- README.md
```

## Diagrama detalhado da arquitetura

```
 CLIENTE                           MINHA MAQUINA (tudo roda local)
(Swagger,   +=============================================================+
 curl ou    |                                                             |
 requests)  |  CAMADA 1 - FASTAPI  (main.py / routes.py / models.py)      |
    |       |  +-------------------------------------------------------+  |
    |       |  |  main.py                                              |  |
    | POST  |  |    app = FastAPI(...)                                 |  |
    |/traduzir| |   app.include_router(router)                         |  |
    |------>|  |                      |                                |  |
    |{texto}|  |                      v                                |  |
    |       |  |  models.py -> TraducaoIn valida o JSON recebido       |  |
    |       |  |                      |                                |  |
    |       |  |                      v                                |  |
    |       |  |  routes.py -> rejeita texto vazio com HTTP 400        |  |
    |       |  +----------------------+--------------------------------+  |
    |       |                         | chama traduzir(texto)             |
    |       |                         v                                   |
    |       |  CAMADA 2 - LANGCHAIN  (services.py)                        |
    |       |  +-------------------------------------------------------+  |
    |       |  |  PromptTemplate.from_template("{texto}")              |  |
    |       |  |    - so repassa o texto, sem instrucao                |  |
    |       |  |                      |                                |  |
    |       |  |                      v                                |  |
    |       |  |  HuggingFacePipeline(pipeline=pipe)                   |  |
    |       |  |    - adapta o pipeline do transformers para a         |  |
    |       |  |      interface padrao do LangChain (invoke / | )      |  |
    |       |  |    - le a chave "translation_text" da resposta        |  |
    |       |  |                      |                                |  |
    |       |  |                      v                                |  |
    |       |  |  StrOutputParser()                                    |  |
    |       |  |    - converte a saida do modelo em texto puro         |  |
    |       |  |                                                       |  |
    |       |  |  chain = prompt | llm | parser                        |  |
    |       |  |  chain.invoke({"texto": texto})                       |  |
    |       |  +----------------------+--------------------------------+  |
    |       |                         | repassa o texto ao pipeline       |
    |       |                         v                                   |
    |       |  CAMADA 3 - HUGGINGFACE / TRANSFORMERS                      |
    |       |  +-------------------------------------------------------+  |
    |       |  |  pipeline("translation",                              |  |
    |       |  |           model="Helsinki-NLP/opus-mt-en-de",         |  |
    |       |  |           device=cuda ou cpu)                         |  |
    |       |  |                                                       |  |
    |       |  |   (a) tokenizacao - MarianTokenizer, sentencepiece    |  |
    |       |  |              |                                        |  |
    |       |  |              v                                        |  |
    |       |  |   (b) modelo MarianMT (encoder-decoder) roda sobre    |  |
    |       |  |       o PyTorch e gera os tokens em alemao            |  |
    |       |  |              |                                        |  |
    |       |  |              v                                        |  |
    |       |  |   (c) decodificacao -> {"translation_text": "..."}    |  |
    |       |  +-------------------------------------------------------+  |
    |       |                         ^                                   |
    |       |                         | 1a execucao: baixa os pesos do    |
    |       |                         | Hub e guarda no cache local       |
    |       |                  +------+--------------------+              |
    |       |                  |  HUGGINGFACE HUB (nuvem)  |              |
    |       |                  |  so no primeiro download  |              |
    |       |                  +---------------------------+              |
    | 200 OK|                                                             |
    |{traducao}                                                           |
    |<------+=============================================================+

  Interacoes entre os componentes:
    FastAPI     -> LangChain    : chama traduzir(), que executa chain.invoke()
    LangChain   -> HuggingFace  : HuggingFacePipeline repassa o texto ao pipeline
    HuggingFace -> LangChain    : devolve {"translation_text": ...}
    LangChain   -> FastAPI      : StrOutputParser entrega a traducao como string
    FastAPI     -> Cliente      : serializa TraducaoOut e responde em JSON
```

### Etapas do fluxo de dados

| Etapa | Camada      | O que acontece                                                    |
|-------|-------------|-------------------------------------------------------------------|
| 1     | Cliente     | Envia `POST /traduzir` com `{"texto": "..."}` em JSON             |
| 2     | FastAPI     | `TraducaoIn` valida o corpo; texto vazio devolve HTTP 400         |
| 3     | LangChain   | `PromptTemplate` substitui `{texto}` pelo texto recebido          |
| 4     | LangChain   | `HuggingFacePipeline` chama o pipeline do transformers            |
| 5     | HuggingFace | O tokenizador converte o texto em tokens numéricos                |
| 6     | HuggingFace | O modelo MarianMT gera os tokens da tradução e decodifica o texto |
| 7     | LangChain   | `StrOutputParser` entrega apenas a string da tradução             |
| 8     | FastAPI     | Devolve `TraducaoOut` como JSON com HTTP 200                      |

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

O pacote `sentencepiece` é obrigatório para o tokenizador do opus-mt.

3. Subir o servidor:

```powershell
uvicorn main:app --port 8000 --reload
```

A primeira execução baixa o modelo (cerca de 300 MB) e guarda em cache. Depois disso
a aplicação não precisa mais de internet.

4. Abrir a documentação automática (Swagger) em:

```
http://127.0.0.1:8000/docs
```

## Endpoints

| Método | Rota        | Descrição                                     |
|--------|-------------|-----------------------------------------------|
| GET    | `/`         | Verifica se a API está no ar e qual o modelo  |
| POST   | `/traduzir` | Recebe um texto em inglês e devolve em alemão |

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
  "texto_traduzido": "Die Katze liegt auf dem Tisch."
}
```

### Teste pelo terminal

```powershell
curl -X POST "http://127.0.0.1:8000/traduzir" -H "Content-Type: application/json" -d "{\"texto\": \"The cat is on the table.\"}"
```

## Decisões que tomei

- **Template com apenas `{texto}`**: esse foi o ponto que mais me chamou atenção.
  Nas Questões anteriores com LangChain eu escrevo uma instrução no prompt
  ("Translate the sentence below..."), porque do outro lado tem um modelo de chat que
  entende instrução. O opus-mt não é um modelo de chat: ele é um tradutor e traduz
  **tudo** o que recebe. Se eu deixasse a instrução no template, ela viria traduzida
  para o alemão junto com a frase do usuário. Por isso o template aqui só repassa o
  texto, e quem define o par de idiomas é a escolha do modelo (`en-de`), não o prompt.
- **`task="translation"`**: é a tarefa que a classe `HuggingFacePipeline` do LangChain
  aceita para modelos de tradução; ela lê a chave `translation_text` da resposta.
- **Pipeline criado uma única vez**: a cadeia fica guardada em uma variável do módulo.
  Carregar o modelo em cada requisição deixaria a API lenta demais.
- **Sem quebra do texto em frases**: diferente da Questão 2 da Parte 1, aqui eu mando o
  texto em uma única chamada, para manter o código simples e focado na integração com o
  LangChain. Por causa disso, textos maiores que o limite de tokens do modelo são
  truncados. Comento essa limitação na Questão 5.

## Códigos de status usados

| Código | Quando acontece                                                       |
|--------|-----------------------------------------------------------------------|
| 200    | Tradução feita com sucesso                                            |
| 400    | Campo `texto` vazio ou só com espaços                                 |
| 422    | Corpo da requisição fora do formato esperado (validado pelo Pydantic) |
