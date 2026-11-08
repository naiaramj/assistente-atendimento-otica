import sqlite3

BANCO = "pontal.db"

MARCAS = ["HOYA", "Varilux", "Stock-Lux", "Haytek", "Space Plus", "Kodak", "Zeiss"]


def detectar_marca(pergunta):
    texto = pergunta.lower()
    for marca in MARCAS:
        if marca.lower() in texto:
            return marca
    return None


def buscar_conhecimento(marca):
    conn = sqlite3.connect(BANCO)
    linhas = conn.execute(
        "SELECT categoria, pergunta, resposta "
        "FROM conhecimento "
        "WHERE marca = ? OR marca IS NULL",
        (marca,),
    ).fetchall()
    conn.close()
    return linhas
