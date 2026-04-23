import openpyxl
import inflect

def numero_para_extenso(numero):
    p = inflect.engine()
    return p.number_to_words(numero, andword=" e ")

def ler_valor_em_excel(arquivo_excel, nome_planilha, celula):
    workbook = openpyxl.load_workbook(arquivo_excel)
    planilha = workbook[nome_planilha]
    valor = planilha[celula].value
    return valor

def main():
    # Substitua 'seu_arquivo.xlsx', 'SuaPlanilha' e 'A1' pelos valores adequados
    '''arquivo_excel = 'seu_arquivo.xlsx'''
    arquivo_excel = 'Matrix_2023_HRG.xlsx'
    '''nome_planilha = 'SuaPlanilha'''
    nome_planilha = 'ISS'
    celula = 'H24'

    valor_lido = ler_valor_em_excel(arquivo_excel, nome_planilha, celula)

    if valor_lido is not None:
        valor_extenso = numero_para_extenso(valor_lido)
        ''' valor_extenso = numero_para_extenso(valor_lido)'''
        '''extenso = num2words(valor, lang='pt_BR', to='currency', currency='BRL')'''
        print(f'O valor {valor_lido} em extenso é: {valor_extenso}')
    else:
        print('Célula vazia ou valor inválido.')

if __name__ == "__main__":
    main()