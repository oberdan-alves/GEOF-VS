import sys
import os
from PyPDF2 import PdfMerger

def mesclar_pdfs(lista_path, destino):
    if not os.path.exists(lista_path):
        print(f"Arquivo de lista não encontrado: {lista_path}")
        return

    merger = PdfMerger()

    # Mudança aqui: encoding latin1
    with open(lista_path, 'r', encoding='latin1') as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    if not linhas:
        print("A lista de PDFs está vazia.")
        return

    for pdf in linhas:
        if os.path.exists(pdf):
            merger.append(pdf)
        else:
            print(f"Arquivo não encontrado: {pdf}")

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    merger.write(destino)
    merger.close()
    print(f"PDF mesclado salvo em: {destino}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python mesclar_pdfs.py <lista_txt> <arquivo_saida.pdf>")
    else:
        mesclar_pdfs(sys.argv[1], sys.argv[2])
