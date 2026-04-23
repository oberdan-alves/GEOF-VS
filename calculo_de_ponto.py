import re

import PyPDF2
import tesseract as tesseract
from PIL import Image
from pdf2image import convert_from_path
from pytesseract import pytesseract

'''
reader = PyPDF2.PdfFileReader('Ponto14102019.pdf', 'rb')
p = reader.getPage(0)
text = p.extractText()
print (text)
'''
'''pdf_file = open('Ponto14102019.pdf', 'rb')
pdf_reader = PyPDF2.PdfFileReader(pdf_file)
pag = pdf_reader.getPage(0)'''


pages = convert_from_path('Ponto14102019.pdf', 300)
pdf_file = 'Ponto14102019.pdf'[:-4]
cont = 1
for page in pages:
    page.save(f"{pdf_file}{cont}.jpg", "JPEG")
    cont = cont + 1
print('\nImagens criadas com sucesso')
print(pages)



'tesseract d:\CursoemVideo\Ponto141020191.jpg -l ara -psm 3 d:\CursoemVideo\test_ara pdf



'''def confere_data():
    texto = []
    padrao = re.compile('(\d\d)/(\d\d)/(\d\d\d\d)')
    emissao_string = padrao.search('Ponto14102019.pdf')
    texto.append(emissao_string.split()[2])
    emissao = texto[0]
    data_de_emissao = time.strptime(emissao, "%d/%m/%Y")
    payday = f'{self.dia}/{self.mes}/{self.ano}'   
    data_do_pagamento = time.strptime(payday, "%d/%m/%Y")
    return data_do_pagamento >= data_de_emissao and data_do_pagamento <= data_de_vencimento
    print(padrao)
    print(emissao)
    print(data_de_emissao)
    print(payday)
    print(data_do_pagamento)

confere_data()
'''
