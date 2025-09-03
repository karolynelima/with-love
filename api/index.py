import csv
import os
import re
from functools import lru_cache
from typing import Dict, List, Set, Any, Tuple

from flask import Flask, jsonify, make_response, request
from flask.wrappers import Response
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

# Tipos para melhor legibilidade
Musica = Dict[str, str]
ListaMusicas = List[Musica]
ResultadoBusca = Dict[str, str]
ListaResultados = List[ResultadoBusca]

app = Flask(__name__)

# === Configuração ===
# Para melhor prática, origens poderiam vir de variáveis de ambiente
# Ex: origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200")
#     ALLOWED_ORIGINS = origins_str.split(",")
ALLOWED_ORIGINS = [
    "http://localhost:4200",           # dev
    "https://with-love-six.vercel.app" # prod
]

# === CORS ===
CORS(
    app,
    resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)

# === Carregamento de Dados ===
@lru_cache(maxsize=1)
def carregar_musicas() -> ListaMusicas:
    """
    Carrega as músicas do arquivo CSV.
    Usa lru_cache para garantir que o arquivo seja lido apenas uma vez.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    arquivo_csv = os.path.join(script_dir, "ariana_grande_albuns_musicas.csv")

    musicas_carregadas: ListaMusicas = []
    try:
        with open(arquivo_csv, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                musicas_carregadas.append({
                    "album":  row.get("Álbum", ""),
                    "titulo": row.get("Título da Música", ""),
                    "letra":  row.get("Letra", "") or "",
                    # Adicionado para a referência ABNT. O CSV precisa ter essa coluna.
                    "ano":    row.get("Ano", "")
                })
    except FileNotFoundError:
        # Em um app de produção, logar este erro seria importante
        print(f"Erro: Arquivo CSV não encontrado em {arquivo_csv}")
        return []
    return musicas_carregadas

# === Lógica de Busca ===
def encontrar_estrofes(musica: Musica, padrao: re.Pattern) -> Set[str]:
    """Encontra e retorna os trechos de letra que correspondem ao padrão."""
    linhas_originais = (musica.get("letra", "") or "").split("\n")
    estrofes_encontradas: Set[str] = set()

    for i, linha in enumerate(linhas_originais):
        if padrao.search(linha):
            # Captura 3 linhas de contexto antes e 3 depois da linha encontrada
            inicio = max(0, i - 3)
            fim = min(len(linhas_originais), i + 4)
            estrofe = "\n".join(linhas_originais[inicio:fim]).strip()
            if estrofe:
                estrofes_encontradas.add(estrofe)
    return estrofes_encontradas

def gerar_referencia_abnt(musica: Musica) -> str:
    """Gera uma referência bibliográfica no formato ABNT para uma música."""
    interprete = "GRANDE, Ariana"
    # Título da música em maiúsculas, conforme ABNT
    titulo_musica = musica.get("titulo", "TÍTULO DESCONHECIDO").upper()
    titulo_album = musica.get("album", "")
    # Ano do álbum. 's.d.' (sine data) se não encontrado.
    ano = musica.get("ano", "s.d.")

    # Formato ABNT para faixa de álbum (NBR 6023:2018).
    # Usamos [S.l.] (sine loco) para local e 'Republic Records' como gravadora padrão.
    # O título do álbum vai em negrito, que será renderizado como <strong> no frontend.
    if titulo_album:
        return (
            f"{interprete}. {titulo_musica}. In: {interprete}. "
            f"<strong>{titulo_album}</strong>. [S.l.]: Republic Records, {ano}."
        )

    # Formato para single (música não contida em álbum)
    return f"{interprete}. {titulo_musica}. [S.l.]: Republic Records, {ano}."

def formatar_resultados(musica: Musica, estrofes: Set[str], padrao: re.Pattern) -> ResultadoBusca:
    """Formata as estrofes encontradas para a resposta da API."""
    estrofes_destacadas = [
        padrao.sub(r"<strong>\g<0></strong>", e) for e in sorted(list(estrofes))
    ]
    return {
        "album": musica["album"],
        "musica": musica["titulo"],
        "estrofe": "\n\n[...]\n\n".join(estrofes_destacadas),
        "referencia_abnt": gerar_referencia_abnt(musica)
    }

# === Endpoints da API ===
@app.route("/api/health")
def health() -> Response:
    """Endpoint de verificação de saúde da API."""
    return jsonify({"status": "ok"})

@app.route("/api/buscar", methods=["POST"])
def buscar_musicas_por_frase() -> Response:
    """
    Endpoint principal que busca uma frase nas letras das músicas.
    """
    try:
        data = request.get_json()
        if not data or "frase" not in data:
            raise BadRequest("O campo 'frase' é obrigatório no corpo da requisição.")
    except BadRequest as e:
        return jsonify({"erro": "Payload inválido.", "detalhes": str(e)}), 400

    frase = (data.get("frase") or "").strip()
    if not frase:
        return jsonify([]), 200

    todas_as_musicas = carregar_musicas()
    if not todas_as_musicas:
        return jsonify({"erro": "Base de dados de músicas não pôde ser carregada."}), 500

    padrao = re.compile(r'\b' + re.escape(frase) + r'\b', re.IGNORECASE)
    resultados: ListaResultados = []

    for musica in todas_as_musicas:
        estrofes_encontradas = encontrar_estrofes(musica, padrao)
        if estrofes_encontradas:
            resultado_formatado = formatar_resultados(musica, estrofes_encontradas, padrao)
            resultados.append(resultado_formatado)

    return jsonify(resultados), 200

# Para desenvolvimento local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
