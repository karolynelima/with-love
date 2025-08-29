import os, csv, re, json

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CSV_PATH = os.path.join(_SCRIPT_DIR, "ariana_grande_albuns_musicas.csv")

_MUSICAS = []
with open(_CSV_PATH, "r", encoding="utf-8", newline="") as f:
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
    padrao = re.compile(r'\b' + re.escape(frase) + r'\b', re.IGNORECASE)
    out = []
    for m in _MUSICAS:
        linhas = (m["letra"] or "").split("\n")
        achados = set()
        for i, linha in enumerate(linhas):
            if padrao.search(linha):
                ini = max(0, i-3); fim = min(len(linhas), i+4)
                trecho = "\n".join(linhas[ini:fim]).strip()
                if trecho:
                    achados.add(trecho)
        if achados:
            destacados = [padrao.sub(r"<strong>\\g<0></strong>", e) for e in sorted(achados)]
            out.append({"album": m["album"], "musica": m["titulo"], "estrofe": "\n\n[...]\n\n".join(destacados)})
    return out

# Vercel chama essa função
def handler(request):
    if request.method != "POST":
        return (json.dumps({"error":"Method Not Allowed"}), 405, {"Content-Type":"application/json"})
    data = request.get_json(silent=True) or {}
    frase = data.get("frase", "")
    resp = _search(frase)
    return (json.dumps(resp, ensure_ascii=False), 200, {"Content-Type":"application/json; charset=utf-8"})
