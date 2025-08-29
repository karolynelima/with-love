import csv
import re
import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

app = Flask(__name__)

# === CORS ===
ALLOWED_ORIGINS = [
    "http://localhost:4200",           # dev
    "https://with-love-six.vercel.app" # prod
]
CORS(
    app,
    resources={r"/buscar*": {"origins": ALLOWED_ORIGINS}},
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# === Healthcheck opcional ===
@app.get("/health")
def health():
    return {"status": "ok"}

# === CSV ===
script_dir = os.path.dirname(os.path.abspath(__file__))
arquivo_csv = os.path.join(script_dir, "ariana_grande_albuns_musicas.csv")

musicas = []
with open(arquivo_csv, mode="r", encoding="utf-8", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        musicas.append({
            "album":  row.get("Álbum", ""),
            "titulo": row.get("Título da Música", ""),
            "letra":  row.get("Letra", "") or ""
        })

# === Endpoint ===
@app.route("/buscar", methods=["POST", "OPTIONS"])
def buscar_musicas_por_frase():
    # Preflight CORS (navegador envia antes do POST)
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        return resp

    data = request.get_json(force=True, silent=True) or {}
    frase = (data.get("frase") or "").strip()
    if not frase:
        # Retorna vazio pra UX ficar suave (ou mude para 400 se preferir)
        return jsonify([]), 200

    padrao = re.compile(r'\b' + re.escape(frase) + r'\b', re.IGNORECASE)
    resultados = []

    for musica in musicas:
        linhas_originais = (musica["letra"] or "").split("\n")
        estrofes_encontradas = set()

        for i, linha in enumerate(linhas_originais):
            if padrao.search(linha):
                inicio = max(0, i - 3)
                fim = min(len(linhas_originais), i + 4)
                estrofe = "\n".join(linhas_originais[inicio:fim]).strip()
                if estrofe:
                    estrofes_encontradas.add(estrofe)

        if estrofes_encontradas:
            estrofes_destacadas = [
                padrao.sub(r"<strong>\g<0></strong>", e) for e in sorted(estrofes_encontradas)
            ]
            resultados.append({
                "album": musica["album"],
                "musica": musica["titulo"],
                "estrofe": "\n\n[...]\n\n".join(estrofes_destacadas)
            })

    return jsonify(resultados), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
