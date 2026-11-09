from fastapi import FastAPI
from pydantic import BaseModel

from banco import MARCAS, detectar_marca, buscar_conhecimento

app = FastAPI()


class Pergunta(BaseModel):
    texto: str
    marca: str | None = None


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
        }

    entradas = buscar_conhecimento(marca)

    return {
        "encontrou": True,
        "marca": marca,
        "entradas": entradas,
    }
