from fastapi import FastAPI
from pydantic import BaseModel

from banco import (
    MARCAS,
    buscar_conhecimento,
    detectar_marca,
    registrar_feedback,
    salvar_historico,
)
from ia import responder

app = FastAPI()


class Pergunta(BaseModel):
    texto: str
    marca: str | None = None


class Feedback(BaseModel):
    historico_id: int
    util: bool


@app.get("/")
def raiz():
    return {"status": "ok"}


@app.post("/perguntar")
def perguntar(dados: Pergunta):
    marca = dados.marca or detectar_marca(dados.texto)

    if marca is None:
        return {
            "encontrou": False,
            "resposta": "Preciso saber a marca da lente para achar a regra certa.",
            "marcas": MARCAS,
            "historico_id": None,
        }

    entradas = buscar_conhecimento(marca)

    try:
        resposta, encontrou = responder(dados.texto, marca, entradas)
    except Exception:
        return {
            "encontrou": False,
            "marca": marca,
            "resposta": "O assistente está indisponível no momento. Tente de novo em instantes.",
            "historico_id": None,
        }

    historico_id = salvar_historico(dados.texto, resposta, encontrou)

    return {
        "encontrou": encontrou,
        "marca": marca,
        "resposta": resposta,
        "historico_id": historico_id,
    }


@app.post("/feedback")
def feedback(dados: Feedback):
    registrado = registrar_feedback(dados.historico_id, dados.util)
    return {"registrado": registrado}
