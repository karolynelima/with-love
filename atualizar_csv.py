import csv
import os

# Mapeamento dos álbuns da Ariana Grande para o ano de lançamento
# Adicione outros álbuns ou singles aqui se necessário
anos_albuns = {
    "Yours Truly": "2013",
    "My Everything": "2014",
    "Dangerous Woman": "2016",
    "Sweetener": "2018",
    "Thank U, Next": "2019",
    "Positions": "2020",
    "eternal sunshine": "2024",
    # Adicione aqui outros álbuns, compilações ou EPs se estiverem no seu CSV
}

def atualizar_csv():
    """
    Lê o CSV original, adiciona a coluna 'Ano' e salva em um novo arquivo.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    arquivo_original = os.path.join(script_dir, "ariana_grande_albuns_musicas.csv")
    novo_arquivo = os.path.join(script_dir, "ariana_grande_albuns_musicas_com_ano.csv")

    try:
        with open(arquivo_original, mode='r', encoding='utf-8', newline='') as infile, \
             open(novo_arquivo, mode='w', encoding='utf-8', newline='') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Lê o cabeçalho e adiciona a nova coluna
            cabecalho = next(reader)
            if "Ano" not in cabecalho:
                cabecalho.append("Ano")
            writer.writerow(cabecalho)

            # Encontra o índice da coluna 'Álbum' para fazer a busca do ano
            try:
                indice_album = cabecalho.index("Álbum")
            except ValueError:
                print("Erro: A coluna 'Álbum' não foi encontrada no CSV original.")
                return

            # Itera sobre as linhas, adicionando o ano
            for linha in reader:
                # Garante que a linha não está vazia
                if not linha:
                    continue

                nome_album = linha[indice_album]
                ano = anos_albuns.get(nome_album, "s.d.") # 's.d.' (sem data) se o álbum não for encontrado

                if ano == "s.d.":
                    print(f"Aviso: Álbum '{nome_album}' não encontrado no mapeamento. O ano não foi adicionado.")

                # Adiciona o ano à linha e escreve no novo arquivo
                linha.append(ano)
                writer.writerow(linha)

        print(f"Sucesso! O novo arquivo foi salvo em: {novo_arquivo}")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_original}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    atualizar_csv()
