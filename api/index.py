import csv
import re
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Configuração de CORS mais segura, permitindo apenas o seu frontend
CORS(app, resources={r"/buscar*": {"origins": "https://with-love-six.vercel.app"}})

# Caminho robusto para o arquivo CSV, garantindo que funcione na Vercel
script_dir = os.path.dirname(os.path.abspath(__file__))
arquivo_csv = os.path.join(script_dir, "ariana_grande_albuns_musicas.csv")

# Carregar músicas do CSV para a memória
musicas = []
with open(arquivo_csv, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        musicas.append({
            "album":    row["Álbum"],
            "titulo":   row["Título da Música"],
            "letra":    row["Letra"]
        })

# Rota para buscar músicas (Vercel usará esta função)
@app.route('/buscar', methods=['POST'])
def buscar_musicas_por_frase():
    data = request.json
    frase = data.get('frase', '').lower()

    if not frase:
        return jsonify([])

    resultados = []
    padrao = re.compile(r'\b' + re.escape(frase) + r'\b', re.IGNORECASE)

    for musica in musicas:
        letra_original = musica["letra"]
        linhas_originais = letra_original.split("\n")
        linhas_lower = [linha.lower() for linha in linhas_originais]

        estrofes_encontradas = set()

        for i, linha_lower in enumerate(linhas_lower):
            if padrao.search(linha_lower):
                inicio = max(0, i - 3)
                fim = min(len(linhas_originais), i + 4)
                estrofe = "\n".join(linhas_originais[inicio:fim]).strip()

                if estrofe:
                    estrofes_encontradas.add(estrofe)

        if estrofes_encontradas:
            estrofes_destacadas = [padrao.sub(r'<strong>\g<0></strong>', estrofe) for estrofe in sorted(list(estrofes_encontradas))]
            estrofe_completa = "\n\n[...]\n\n".join(estrofes_destacadas)
            resultados.append({
                "album": musica["album"],
                "musica": musica["titulo"],
                "estrofe": estrofe_completa
            })

    return jsonify(resultados)

# Este bloco só será executado localmente, não na Vercel
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
