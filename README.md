# TP2 - Desenvolvimento de Data-Driven Apps com Python

Entrega do Teste de Performance 2. São cinco aplicações práticas, cada uma em um
projeto separado e independente, mais um arquivo PDF com as respostas teóricas, os
diagramas e a tabela comparativa.

- **Aluno:** Luis Claudio de Jesus
- **Turma:** 26E4_3
- **Professor:** Tiago Xavier

## O que tem nesta entrega

| Questão do enunciado | Projeto / arquivo                                  | O que faz                                                        |
|----------------------|-----------------------------------------------------|------------------------------------------------------------------|
| Parte 1 - Questão 1  | [`parte1-questao1-gpt2-fastapi/`](parte1-questao1-gpt2-fastapi/) | Gera texto com o GPT-2 da HuggingFace via FastAPI |
| Parte 1 - Questão 2  | [`parte1-questao2-traducao-en-fr/`](parte1-questao2-traducao-en-fr/) | Traduz inglês -> francês com o opus-mt-en-fr |
| Parte 1 - Questões 3 e 4 | [`respostas-teoricas.pdf`](respostas-teoricas.pdf) | Limitações do modelo de tradução e do GPT-2 |
| Parte 2 - Questão 1  | [`parte2-questao1-chatbot-fake-llm/`](parte2-questao1-chatbot-fake-llm/) | Chatbot simples com Fake LLM do LangChain |
| Parte 2 - Questão 2  | [`parte2-questao2-traducao-openai-langchain/`](parte2-questao2-traducao-openai-langchain/) | Traduz inglês -> francês com a OpenAI via LangChain |
| Parte 2 - Questão 3  | [`parte2-questao3-traducao-huggingface-langchain/`](parte2-questao3-traducao-huggingface-langchain/) | Traduz inglês -> alemão com o opus-mt-en-de via LangChain |
| Parte 2 - Questões 4, 5 e 6 | [`respostas-teoricas.pdf`](respostas-teoricas.pdf) | Limitações do LangChain com OpenAI e com HuggingFace, e a tabela comparativa |

Os diagramas de arquitetura das Questões 1, 2 e 3 da Parte 2 estão no README de cada
projeto e também reproduzidos no Apêndice A do PDF.

## Como executar qualquer uma das aplicações

Cada projeto é independente, tem o seu próprio `requirements.txt` e o seu próprio
`README.md` com as instruções detalhadas, exemplos de requisição e de resposta. O
passo a passo é sempre o mesmo:

```powershell
cd <pasta-do-projeto>
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

No Linux/macOS, a ativação do ambiente virtual é `source .venv/bin/activate`.

Depois é só abrir `http://127.0.0.1:8000/docs` para testar pelo Swagger.

Duas observações importantes:

- Os projetos que usam modelo local (Parte 1 Questões 1 e 2, e Parte 2 Questão 3)
  baixam o modelo na primeira execução, então ela demora mais que as seguintes.
- O projeto da Parte 2 Questão 2 precisa de uma chave de API configurada em variável
  de ambiente. As instruções estão no README dele.

## Organização do código

Todos os cinco projetos seguem a mesma estrutura, para ficar fácil de comparar um com
o outro:

```
projeto/
+-- main.py            # cria a aplicação FastAPI e registra o router
+-- routes.py          # rotas (endpoints) e tratamento de erro com HTTPException
+-- models.py          # modelos Pydantic de entrada e de saída (response_model)
+-- services.py        # a parte que fala com o modelo de linguagem
+-- requirements.txt   # dependências
+-- .gitignore         # ignora .venv, __pycache__ e .env
+-- README.md          # instruções de execução e decisões de projeto
```

A ideia de separar em quatro arquivos é que cada um tenha uma responsabilidade só.
Quem precisa trocar o modelo mexe apenas no `services.py`; quem precisa mudar o
contrato da API mexe apenas no `models.py`. Nas três aplicações da Parte 2 isso fica
bem visível: elas têm praticamente o mesmo `main.py`, `routes.py` e `models.py`, e a
diferença entre elas está concentrada no `services.py`.

## Uso de ferramentas de IA

Utilizei o Claude (Anthropic) como apoio na revisão do texto das respostas, na
conferência da estrutura dos projetos e na revisão do código, conforme autorizado no
enunciado. A declaração completa, com o que foi feito com apoio da ferramenta e o que
foi decidido e verificado por mim, está no Apêndice B do arquivo
[`respostas-teoricas.pdf`](respostas-teoricas.pdf).
