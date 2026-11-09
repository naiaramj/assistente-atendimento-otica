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


def salvar_historico(pergunta, resposta, encontrou):
    conn = sqlite3.connect(BANCO)
    cursor = conn.execute(
        "INSERT INTO historico (pergunta, resposta, encontrou_na_base) "
        "VALUES (?, ?, ?)",
        (pergunta, resposta, int(encontrou)),
    )
    novo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return novo_id


def registrar_feedback(historico_id, util):
    conn = sqlite3.connect(BANCO)
    cursor = conn.execute(
        "UPDATE historico SET util = ? WHERE id = ?",
        (int(util), historico_id),
    )
    alterou = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return alterou
