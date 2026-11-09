import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODELO = "openai/gpt-oss-120b"

NAO_SEI = (
    "Não encontrei essa informação na base da loja. "
    "Confirme com o responsável antes de responder ao cliente."
)

INSTRUCAO = f"""Você é um assistente interno de uma ótica, usado pelos vendedores.

Regras:
1. Responda usando apenas as informações do material fornecido.
2. Se a resposta não estiver no material, responda exatamente: {NAO_SEI}
3. Não use conhecimento próprio sobre óticas, lentes, marcas ou leis.
4. Não invente prazos, condições, documentos nem nomes de marca.
5. Responda em português do Brasil, em no máximo 4 frases.
6. Não dê orientação médica. Se a pergunta envolver sintoma ou saúde, oriente a procurar o oftalmologista.
"""

cliente = Groq()


def montar_contexto(entradas):
    blocos = []
    for categoria, pergunta, resposta in entradas:
        blocos.append(f"[{categoria}] {pergunta}\n{resposta}")
    return "\n\n".join(blocos)


def responder(pergunta, marca, entradas):
    conteudo = (
        f"Marca: {marca}\n\n"
        f"Material da loja:\n{montar_contexto(entradas)}\n\n"
        f"Pergunta do vendedor: {pergunta}"
    )

    retorno = cliente.chat.completions.create(
        model=MODELO,
        temperature=0,
        max_completion_tokens=1000,
        messages=[
            {"role": "system", "content": INSTRUCAO},
            {"role": "user", "content": conteudo},
        ],
    )

    resposta = retorno.choices[0].message.content.strip()
    encontrou = NAO_SEI not in resposta
    return resposta, encontrou
