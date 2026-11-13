import re
import unicodedata

from banco import buscar_conhecimento, detectar_marca
from ia import responder

ARQUIVO = "avaliacao.md"


def normalizar(texto):
    texto = unicodedata.normalize("NFKC", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip().lower()


def ler_perguntas(caminho=ARQUIVO):
    perguntas = []
    atual = {}

    with open(caminho, encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if linha.startswith("P:"):
                atual = {"pergunta": linha[2:].strip(), "marca": None}

            elif linha.startswith("MARCA:"):
                atual["marca"] = linha[6:].strip() or None

            elif linha.startswith("ESPERADO:"):
                atual["esperado"] = linha[9:].strip()
                perguntas.append(atual)
                atual = {}

    return perguntas


def avaliar():
    perguntas = ler_perguntas()
    total = len(perguntas)
    acertos = 0
    falhas = []

    print(f"Avaliando {total} perguntas...\n")

    for numero, item in enumerate(perguntas, start=1):
        print(f"[{numero}/{total}] {item['pergunta'][:55]}", end=" ", flush=True)
        marca = item["marca"] or detectar_marca(item["pergunta"])

        if marca is None:
            resposta = ""
            encontrou = False
        else:
            resposta, encontrou = responder(
                item["pergunta"], marca, buscar_conhecimento(marca)
            )

        if item["esperado"] == "NAO_SEI":
            acertou = not encontrou
        else:
            acertou = normalizar(item["esperado"]) in normalizar(resposta)

        if acertou:
            acertos += 1
            print("ok")
        else:
            falhas.append((item["pergunta"], item["esperado"], resposta))
            print("FALHOU")

    print(f"\nAcertos: {acertos} de {total} ({acertos * 100 // total}%)")

    if falhas:
        print("\nFalhas:")
        for pergunta, esperado, resposta in falhas:
            print(f"\n- {pergunta}")
            print(f"  esperado: {esperado}")
            print(f"  resposta: {resposta or '(nenhuma marca identificada)'}")


if __name__ == "__main__":
    avaliar()
