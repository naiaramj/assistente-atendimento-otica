import sqlite3

conn = sqlite3.connect("pontal.db")
conn.execute("DELETE FROM conhecimento")

marca = None
categoria = None
pergunta = None
total = 0

with open("conhecimento.md", encoding="utf-8") as arquivo:
    for linha in arquivo:
        linha = linha.strip()

        if linha.startswith("## Marca:"):
            parte_marca, parte_categoria = linha.split("|")
            marca = parte_marca.split(":", 1)[1].strip()
            categoria = parte_categoria.split(":", 1)[1].strip()

        elif linha.startswith("P:"):
            pergunta = linha[2:].strip()

        elif linha.startswith("R:"):
            resposta = linha[2:].strip()

            if resposta == "A CONFIRMAR":
                continue

            conn.execute(
                "INSERT INTO conhecimento (marca, categoria, pergunta, resposta) "
                "VALUES (?, ?, ?, ?)",
                (marca, categoria, pergunta, resposta),
            )
            total += 1

conn.commit()
conn.close()
print(f"{total} entradas carregadas.")
