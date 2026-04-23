import openpyxl
import inflect

def ler_valor_excel(arquivo_excel, nome_planilha, celula):
    # Abre o arquivo Excel
    workbook = openpyxl.load_workbook(arquivo_excel)
    
    # Seleciona a planilha desejada
    planilha = workbook[nome_planilha]
    
    # Lê o valor da célula
    valor_celula = planilha[celula].value

    # Fecha o arquivo Excel
    workbook.close()
    
    return valor_celula

def converter_para_extenso(valor):
    p = inflect.engine()
    return p.number_to_words(valor, andword=", e ")

def main():
    # Substitua esses valores pelos adequados no seu caso
    arquivo_excel = 'Matrix_2023_HRG.xlsx'
    nome_planilha = 'ISS'
    celula = 'H24'
    
    # Lê o valor da célula no Excel
    valor_excel = ler_valor_excel(arquivo_excel, nome_planilha, celula)
    
    # Converte o valor para extenso em reais
    valor_extenso = converter_para_extenso(valor_excel)
    
    print(f'O valor em extenso de {valor_excel} reais é: {valor_extenso}')

if __name__ == "__main__":
    main()