# Parte 1 - Questão 2: Tradução inglês -> francês (FastAPI + HuggingFace)

API em FastAPI que recebe um texto em inglês em JSON, traduz para o francês com o
modelo **Helsinki-NLP/opus-mt-en-fr** da HuggingFace e devolve a tradução em JSON.
Funciona tanto com frases curtas quanto com textos mais longos.

## Estrutura do projeto

```
parte1-questao2-traducao-en-fr/
+-- main.py            # ponto de entrada: cria a aplicação e registra o router
+-- routes.py          # rotas (endpoints) da API
+-- models.py          # modelos Pydantic de entrada e de saída
+-- services.py        # carga do pipeline de tradução e quebra do texto em frases
+-- requirements.txt   # dependências
+-- README.md
```

Mantive a mesma organização da Questão 1 para as duas APIs ficarem parecidas e
fáceis de comparar.

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

O pacote `sentencepiece` é obrigatório: o tokenizador dos modelos opus-mt depende
dele e o modelo não carrega sem esse pacote.

3. Subir o servidor:

```powershell
uvicorn main:app --port 8000 --reload
```

A primeira execução baixa o modelo (cerca de 300 MB) e guarda em cache.

4. Abrir a documentação automática (Swagger) em:

```
http://127.0.0.1:8000/docs
```

## Endpoints

| Método | Rota        | Descrição                                      |
|--------|-------------|------------------------------------------------|
| GET    | `/`         | Verifica se a API está no ar                   |
| POST   | `/traduzir` | Recebe um texto em inglês e devolve em francês |

### POST /traduzir - frase curta

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

### POST /traduzir - texto mais longo

```json
{
  "texto": "Machine learning is a field of computer science. It allows computers to learn from data. Today it is used in many companies."
}
```

Resposta:

```json
{
  "texto_original": "Machine learning is a field of computer science. It allows computers to learn from data. Today it is used in many companies.",
  "texto_traduzido": "L'apprentissage automatique est un domaine de l'informatique. Il permet aux ordinateurs d'apprendre à partir de données. Aujourd'hui, il est utilisé dans de nombreuses entreprises."
}
```

### Teste pelo terminal

```powershell
curl -X POST "http://127.0.0.1:8000/traduzir" -H "Content-Type: application/json" -d "{\"texto\": \"The cat is on the table.\"}"
```

## Como trato os textos longos

O opus-mt tem um limite de tokens por chamada (512). Se eu mandasse um texto grande
de uma vez, o final seria cortado e a tradução sairia incompleta. Para resolver isso
eu quebro o texto em frases no `services.py` (nos pontos `.`, `!` e `?`), mando a
lista de frases para o pipeline e junto as traduções no final.

A vantagem é que texto longo também é traduzido inteiro. A desvantagem é que cada
frase é traduzida isolada, sem o contexto da frase anterior, o que pode errar o
gênero de um pronome ou a concordância entre frases. Comento isso na Questão 3.

## Códigos de status usados

| Código | Quando acontece                                                       |
|--------|-----------------------------------------------------------------------|
| 200    | Tradução feita com sucesso                                            |
| 400    | Campo `texto` vazio ou só com espaços                                 |
| 422    | Corpo da requisição fora do formato esperado (validado pelo Pydantic) |
