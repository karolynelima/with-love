# api/buscar.py
import os
import csv
import re
import json

# --- Carrega CSV uma única vez (cache em memória) ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(_SCRIPT_DIR, "ariana_grande_albuns_musicas.csv")

_MUSICAS = []
with open(_CSV_PATH, mode="r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        _MUSICAS.append({
            "album":  row.get("Álbum", "") or "",
            "titulo": row.get("Título da Música", "") or "",
            "letra":  row.get("Letra", "") or ""
        })


def _search(frase: str):
    frase = (frase or "").strip()
    if not frase:
        return []

    # mesma regra: palavra inteira, case-insensitive
    padrao = re.compile(r'\b' + re.escape(frase) + r'\b', re.IGNORECASE)
    resultados = []

    for m in _MUSICAS:
        linhas = (m["letra"] or "").split("\n")
        estrofes = set()

        for i, linha in enumerate(linhas):
            if padrao.search(linha):
                ini = max(0, i - 3)
                fim = min(len(linhas), i + 4)
                trecho = "\n".join(linhas[ini:fim]).strip()
                if trecho:
                    estrofes.add(trecho)

        if estrofes:
            # destaca a frase com <strong>, mantendo o comportamento
            destacados = [padrao.sub(r"<strong>\\g<0></strong>", e) for e in sorted(estrofes)]
            resultados.append({
                "album":  m["album"],
                "musica": m["titulo"],
                "estrofe": "\n\n[...]\n\n".join(destacados)
            })

    return resultados


# --- Handler para Vercel Python Runtime ---
# A Vercel chamará esta função para /api/buscar
def handler(request):
    # aceita apenas POST, igual ao seu endpoint
    if request.method != "POST":
        return (
            json.dumps({"error": "Method Not Allowed"}),
            405,
            {"Content-Type": "application/json; charset=utf-8"}
        )

    data = request.get_json(silent=True) or {}
    frase = data.get("frase", "")
    resp = _search(frase)

    return (
        json.dumps(resp, ensure_ascii=False),
        200,
        {"Content-Type": "application/json; charset=utf-8"}
    )
