import csv
import os
import re
import string
from functools import lru_cache

from flask import Flask, jsonify, make_response, request
from flask.wrappers import Response
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

# Tipos para melhor legibilidade
Musica = dict[str, str]
ListaMusicas = list[Musica]
ResultadoBusca = dict[str, str]
ListaResultados = list[ResultadoBusca]

app = Flask(__name__)

# === Configuração ===
# Para melhor prática, origens poderiam vir de variáveis de ambiente
# Ex: origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200")
#     ALLOWED_ORIGINS = origins_str.split(",")
ALLOWED_ORIGINS = [
    "http://localhost:4200",           # dev
    "https://with-love-seven.vercel.app" # prod
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
    arquivo_csv = os.path.join(script_dir, "ariana_grande_albuns_musicas_com_ano.csv")

    musicas_carregadas: ListaMusicas = []
    try:
        with open(arquivo_csv, mode="r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                musicas_carregadas.append({
                    "album":  row.get("Álbum", "Álbum Desconhecido") or "Álbum Desconhecido",
                    "titulo": row.get("Título da Música", "Título Desconhecido") or "Título Desconhecido",
                    "letra":  row.get("Letra", "") or "",
                    # Adicionado para a referência ABNT. O CSV precisa ter essa coluna.
                    "ano":    row.get("Ano", "")
                })
    except FileNotFoundError:
        # Em um app de produção, logar este erro seria importante
        # Levanta uma exceção para que o chamador saiba que o recurso não está disponível.
        raise RuntimeError(f"Arquivo de dados essencial não encontrado: {arquivo_csv}")
    return musicas_carregadas

# === Lógica de Busca ===
def normalizar_texto(texto: str) -> str:
    """Remove pontuações e converte para minúsculas para uma busca flexível."""
    texto_lower = texto.lower()
    return texto_lower.translate(str.maketrans('', '', string.punctuation))

def normalizar_flexivel(texto: str) -> str:
    """Remove pontuações e espaços para uma busca ainda mais flexível."""
    return re.sub(r'[\W_]+', '', texto.lower())

def encontrar_estrofe(letra_original: str, frase_busca: str) -> str | None:
    """Encontra a primeira estrofe que contém a frase de busca, usando texto normalizado."""
    frase_busca_flexivel = normalizar_flexivel(frase_busca)

    for linha in letra_original.split('\n'):
        linha_flexivel = normalizar_flexivel(linha)
        if frase_busca_flexivel in linha_flexivel:
            return linha.strip() # Retorna apenas a linha original onde a correspondência foi encontrada

    return None

def gerar_referencia_abnt(musica: Musica) -> str:
    """Gera uma referência bibliográfica no formato ABNT para uma música."""
    interprete = "GRANDE, Ariana"
    # Título da música em maiúsculas, conforme ABNT
    titulo_musica = musica.get("titulo", "TÍTULO DESCONHECIDO").upper()
    titulo_album = musica.get("album", "")
    # Ano do álbum. 's.d.' (sine data) se não encontrado.
    ano = musica.get("ano") or "s.d."

    # Formato ABNT para faixa de álbum (NBR 6023:2018).
    # Usamos [S.l.] (sine loco) para local e 'Republic Records' como gravadora padrão.
    # O título do álbum vai em negrito, que será renderizado como <strong> no frontend.
    if titulo_album:
        # Destaca o nome do álbum na referência
        referencia_album_destacado = re.sub(f'({re.escape(titulo_album)})', r'<strong>\1</strong>', titulo_album, flags=re.IGNORECASE)
        return (
            f"{interprete}. {titulo_musica}. In: {interprete}. "
            f"{referencia_album_destacado}. [S.l.]: Republic Records, {ano}."
        )

    # Formato para single (música não contida em álbum)
    return f"{interprete}. {titulo_musica}. [S.l.]: Republic Records, {ano}."

def formatar_resultado(musica: Musica, estrofe: str, frase_busca: str) -> ResultadoBusca:
    """Formata as estrofes encontradas para a resposta da API."""
    estrofe_destacada = re.sub(f'({re.escape(frase_busca)})', r'<strong>\1</strong>', estrofe, flags=re.IGNORECASE)
    return {
        "album": musica["album"], # Mantém o case original do álbum
        "musica": musica["titulo"],
        "estrofe": estrofe_destacada,
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

    try:
        todas_as_musicas = carregar_musicas()
    except RuntimeError as e:
        # Se o arquivo CSV não pôde ser carregado, o serviço está indisponível.
        print(f"Erro crítico ao carregar músicas: {e}")
        return jsonify({"erro": "O serviço está temporariamente indisponível. A base de dados de músicas não pôde ser carregada."}), 503

    frase_busca_flexivel = normalizar_flexivel(frase)
    resultados: ListaResultados = []

    for musica in todas_as_musicas:
        letra_original = musica.get("letra", "")
        letra_flexivel = normalizar_flexivel(letra_original)

        if frase_busca_flexivel in letra_flexivel:
            estrofe_encontrada = encontrar_estrofe(letra_original, frase)
            if estrofe_encontrada:
                resultado_formatado = formatar_resultado(musica, estrofe_encontrada, frase)
                resultados.append(resultado_formatado)

    return jsonify(resultados), 200

# Para desenvolvimento local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
