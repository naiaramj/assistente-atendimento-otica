# Assistente de Atendimento — Óticas Pontal

Assistente interno que responde dúvidas de garantia, devolução e adaptação de lentes
a partir da base de conhecimento real da loja, e que diz "não sei" quando a
informação não está lá.

![Tela do assistente respondendo uma pergunta sobre garantia, com a marca
selecionada, a fonte da resposta e os botões de avaliação](tela.png)

## Índice

- [O problema](#o-problema)
- [A solução](#a-solução)
- [Stack](#stack)
- [Como funciona](#como-funciona)
- [Avaliação](#avaliação)
- [Desafios e aprendizados](#desafios-e-aprendizados)
- [Base de conhecimento](#base-de-conhecimento)
- [Decisões de projeto](#decisões-de-projeto)
- [Como rodar](#como-rodar)
- [Arquivos](#arquivos)
- [Limitações conhecidas](#limitações-conhecidas)
- [Próximos passos](#próximos-passos)

## O problema

Na ótica, a regra de garantia muda conforme a marca da lente. Prazo de adaptação,
cobertura de tratamento e documentos exigidos são diferentes entre HOYA, Varilux,
Stock-Lux, Haytek, Space Plus, Kodak e Zeiss. Confirmar isso no meio do atendimento
significa procurar certificado ou ligar para o laboratório, com o cliente esperando.
E uma informação errada sobre garantia vira problema na hora de acionar a troca.

## A solução

O vendedor escolhe a marca ou cita na pergunta, e o assistente responde usando
**apenas** as entradas daquela marca mais as regras gerais da loja. Cada pergunta
fica registrada, com indicação de ter sido respondida pela base ou não, o que mostra
quais dúvidas mais aparecem e o que falta cadastrar.

## Stack

- **Python** e **FastAPI** para a API
- **SQLite** com SQL escrito à mão, sem ORM
- **API do Groq** (modelo `openai/gpt-oss-120b`) para gerar a resposta
- HTML, CSS e JavaScript puros na interface

## Como funciona

```
tela  →  POST /perguntar  →  identifica a marca
                          →  busca no banco as entradas da marca + as gerais
                          →  envia só esse material ao modelo
                          →  grava a pergunta no histórico
      ←  resposta + historico_id
```

Três camadas impedem resposta inventada:

1. O modelo recebe só o material daquela marca, nunca a base inteira nem
   conhecimento próprio.
2. A instrução proíbe usar conhecimento externo e manda responder uma frase fixa
   quando a informação não está no material.
3. Dado ainda não confirmado fica marcado como `A CONFIRMAR` no arquivo da base e
   não chega ao banco.

## Avaliação

O projeto tem um script que mede a própria qualidade das respostas:
20 perguntas de teste com gabarito, sendo 13 com resposta na base e 7 em que o
assistente deve recusar.

```bash
python avaliar.py
```

**Resultado atual: 18 de 20 (90%).**

O caminho até esse número diz mais que o número:

| Medição | Resultado | O que aconteceu |
|---|---|---|
| 1ª | 25% | O modelo escreve um espaço fino unicode (U+202F) entre número e unidade, então `"3 meses"` do gabarito não casava com `"3 meses"` da resposta. O erro era do teste, não do modelo. |
| 2ª | 90% | Depois de normalizar os dois textos com `unicodedata.normalize("NFKC", ...)` antes de comparar. |

**O que as 2 falhas restantes revelaram:** o assistente não inventa dado. Das 7
perguntas que ele deveria recusar, acertou 5 — marca que a loja não trabalha, preço,
horário e prazo de entrega, assuntos que a base não cobre de forma alguma. As 2 que
falharam têm uma característica em comum: o assunto perguntado não está na base, mas
**existe outro assunto da mesma marca**. Nesses casos ele responde o assunto vizinho
em vez de dizer que não sabe — perguntado sobre defeitos e tratamentos da Kodak,
respondeu sobre qualidade e material. Não é alucinação, é excesso de prestatividade,
e a correção é no prompt, não no código.

Em uso real, nas 14 perguntas feitas pela interface até agora, nenhuma caiu fora da
base. A avaliação força os casos difíceis de propósito, por isso os dois números são
diferentes e medem coisas diferentes.

## Desafios e aprendizados

**O teste pode estar errado antes do modelo.** A primeira medição acusou 25% e a
tentação era mexer no prompt. A investigação mostrou que as respostas estavam certas
e a comparação é que falhava, por um caractere invisível. Conferir o instrumento
antes de concluir qualquer coisa sobre o medido passou a ser parte do meu processo.

**Restringir o contexto vale mais que pedir para não inventar.** Instrução sozinha
não basta: o resultado veio de mandar ao modelo só o material da marca perguntada.
Quanto menos ele recebe, menos tem o que misturar.

**"Não sei" é funcionalidade, não falha.** Numa ótica, uma garantia errada vira
problema no momento de acionar a troca. Recusar com clareza e indicar a quem
perguntar é mais útil que uma resposta plausível e errada.

**Medir transforma impressão em dado.** Antes da avaliação eu tinha a impressão de
que o assistente ia bem. Depois, passei a ter um número, saber exatamente onde ele
erra e conseguir provar que uma mudança melhorou.

## Base de conhecimento

33 entradas: 24 de garantia por marca e 9 regras gerais de devolução e de tempo de
adaptação. Ficam em `conhecimento.md`, em texto, e um script carrega para o banco:

```bash
python criar_banco.py
python carregar_conhecimento.py
```

Formato de cada bloco:

```
## Marca: HOYA | Categoria: garantia
P: Qual o prazo da garantia de não adaptação das lentes HOYA?
R: 90 dias a partir da emissão da nota fiscal...
```

`Marca: Geral` grava marca vazia no banco, o que faz a regra valer para todas.
Resposta escrita como `A CONFIRMAR` é ignorada na carga.

## Decisões de projeto

- **Busca por marca, não na base inteira.** Mandar tudo ao modelo faz ele misturar
  regras de marcas diferentes, que é justamente o erro que o assistente deve evitar.
- **Uso interno antes de uso pelo cliente.** O vendedor percebe uma resposta errada;
  o cliente não.
- **O painel mostra o total da equipe, nunca quem perguntou.** Se o vendedor souber
  que cada pergunta fica registrada com o nome dele, ele para de perguntar e volta a
  chutar para o cliente.
- **Status de pedido ficou de fora.** É dado operacional, pertence a um CRM, não a
  uma base de conhecimento.
- **A falha do modelo não derruba a API.** A chamada ao Groq está em `try/except`:
  se o limite do plano gratuito for atingido, o vendedor vê uma mensagem clara.

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com a sua chave do Groq:

```
GROQ_API_KEY=sua_chave
```

Depois:

```bash
python criar_banco.py
python carregar_conhecimento.py
uvicorn main:app --reload
```

Abra `http://127.0.0.1:8000`.

## Arquivos

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | rotas da API |
| `banco.py` | todo o acesso ao banco |
| `ia.py` | monta o pedido e chama o modelo |
| `conhecimento.md` | base de conhecimento da loja |
| `carregar_conhecimento.py` | lê o .md e grava no banco |
| `avaliacao.md` | perguntas de teste e gabarito |
| `avaliar.py` | roda a avaliação e calcula o acerto |
| `index.html` | interface do vendedor |

A separação é proposital: trocar o SQLite por Postgres mexe só em `banco.py`;
trocar o modelo mexe só em `ia.py`.

## Limitações conhecidas

- A detecção de marca é por texto exato: "stock lux" sem hífen não é reconhecido.
- Com duas marcas na mesma pergunta, vale a primeira da lista.
- A avaliação confere por palavra-chave, então uma resposta certa escrita de outra
  forma pode ser marcada como errada.
- Parte dos dados da base ainda precisa ser conferida nos certificados de garantia
  de cada fabricante.
- Cada pergunta é isolada: o assistente não guarda o contexto da conversa.

## Próximos passos

- Regra no prompt para recusar assunto ausente mesmo havendo assunto vizinho, e
  nova medição
- Rótulo curto por entrada na base, para o botão de sugestão mostrar "Prazo de
  adaptação" em vez da pergunta inteira
- Busca semântica com embeddings, no lugar do filtro por marca
- Conferidor de pedido antes do envio ao laboratório: checar altura da armação para
  progressiva, material adequado ao grau e medidas preenchidas, reduzindo retrabalho
- Área do gerente para cadastrar e confirmar respostas sem editar arquivo
- Treinamento para quem chega novo, com perguntas vindas do histórico
- Canal no WhatsApp pela API oficial

## Autoria

Náiara Moreira — [LinkedIn](https://linkedin.com/in/naiaramoreira00) ·
[GitHub](https://github.com/naiaramj)
