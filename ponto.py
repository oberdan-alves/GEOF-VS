import re
from typing import Any, Tuple, Union

import pytesseract as ocr
from PIL import Image
from pdf2image import convert_from_path

class Ponto():
    def __init__(self, arquivo, nome):
        self.horasNeg = []
        self.horasExc = []
        self.arquivo = f'{arquivo}'
        self.imagemFolha1 = ''
        self.imagemFolha2 = ''
        self.nome = nome
        self.horastotais = 0
        self.minutostotais = 0
    def convertepdfparaimagem(self):
        pages = convert_from_path(self.arquivo+'.pdf', 300)
        cont = 1
        for page in pages:
            self.imagemFolha1 = f'{self.arquivo}-{cont}-{self.nome}'
            page.save(f"{self.imagemFolha1}.jpg", "JPEG")
            cont = cont + 1
        print('\nImagem criada com sucesso')


    def buscainformacoesnaimagem(self):

        for i in range(1, 4):
            phrase = ocr.image_to_string(Image.open(f'{self.arquivo}-{i}-{self.nome}.jpg'), lang='por')
            cont = re.findall(r'(021)', phrase)
            #print(phrase)
            cont2 = re.findall(r'(011)', phrase)
            print(f'lista do cont = {cont}')
            print(f'quantidade da lista de cont  = {len(cont)}')

            #padrao1 = re.findall(r'(negat\.[)])( )(\w+)(:)(\w+)', phrase)
            padrao1 = re.findall(r'(\w.+)', phrase)
            #padrao1 = re.findall(r'\w.+', phrase)
            print(f'lista do padrao {padrao1}')
            print(f'quantidade da lista do padrao {len(padrao1)}')
            if padrao1 != None:
                for x in range(0, len(cont)):
                    print(f'Primeiro elemnto = {x}')
                    #banconegativo = padrao1[x][2]+padrao1[x][3]+padrao1[x][4]
                    banconegativo = padrao1[x][2] # 0]+padrao1[x][1]+padrao1[x][2]
                    self.horasNeg.append(banconegativo)
                    #continue
                print(f'horas negativas = {self.horasNeg}')

    '''            padrao2 = re.findall(r'(zadas)( )(\w+)(:)(\w+)', phrase)
            print(padrao2)
            if padrao2 != None:
                for x in range(0, len(cont2)):
                    bancopositivo = padrao2[x][2]+padrao2[x][3]+padrao2[x][4]
                    self.horasExc.append(bancopositivo)
                    #continue
                print(f'horas positivas = {self.horasExc}')
    '''

    def calcular_horas(self, saldoH, saldoM):

        horasex = []
        horasneg = []

        for i in self.horasExc:
            eita = i.split(':')
            horasex.append(eita)

        for b in self.horasNeg:
            eita = b.split(':')
            horasneg.append(eita)

        hpos = 0
        hneg = 0
        mpos = 0
        mneg = 0

        for x in range(0, len(self.horasExc)-1):
            hpos += int(horasex[x][0])
            mpos += int(horasex[x][1])

        for x in range(0, len(self.horasNeg)-1):
            hneg -= int(horasneg[x][0])
            mneg -= int(horasneg[x][1])

        #print(f'TOTAL DE HORAS POSITIVAS: {hpos}')
        #print(f'TOTAL DE MINUTOS POSITIVOS: {mpos}')
        #print(f'TOTAL DE HORAS NEGATIVAS: {hneg}')
        #print(f'TOTAL DE MINUTOS NEGATIVOS: {mneg}')

        HORAS_TOTAIS = hpos + hneg + saldoH
        #print(f'HORAS: {HORAS_TOTAIS}')

        MINUTOS_TOTAIS = mpos + mneg + saldoM
        #print(f'MINUTOS TOTAIS: {MINUTOS_TOTAIS}')
        hor = divmod(MINUTOS_TOTAIS, 60)

        #print(f'{hor}\n')
        HORAS_TOTAIS += hor[0]
        a = '=-'*10
        print(f'{a}\n{self.nome}\n{a}\nHoras: {HORAS_TOTAIS}\nMin: {hor[1]}\n')
