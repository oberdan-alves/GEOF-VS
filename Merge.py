import os
from PyPDF2 import PdfReader, PdfWriter

def mesclar_pdfs(pasta_pdf, arquivo_saida):
    # Cria um objeto PdfWriter para o arquivo de saída
    pdf_writer = PdfWriter()

    # Itera sobre todos os arquivos na pasta
    for arquivo in os.listdir(pasta_pdf):
        if arquivo.endswith('.pdf'):
            caminho_arquivo = os.path.join(pasta_pdf, arquivo)
            # Cria um objeto PdfReader para cada arquivo PDF
            pdf_reader = PdfReader(caminho_arquivo)
            
            # Adiciona todas as páginas do arquivo PDF ao PdfWriter
            for pagina in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[pagina])
    
    # Salva o arquivo PDF mesclado
    with open(arquivo_saida, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    
    print(f"PDFs mesclados com sucesso em: {arquivo_saida}")

# Defina o caminho para a pasta com PDFs e o arquivo de saída
pasta_pdf = "caminho/para/pasta/propostas"
arquivo_saida = "caminho/para/pasta/ArquivoMesclado.pdf"

# Chama a função para mesclar os PDFs
mesclar_pdfs(pasta_pdf, arquivo_saida)

