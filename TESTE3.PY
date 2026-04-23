import openpyxl
from num2words import num2words

def ler_valor_excel(nome_arquivo, nome_planilha, celula):
    # Abre o arquivo do Excel
    workbook = openpyxl.load_workbook(nome_arquivo)
    print(nome_arquivo)

    # Seleciona a planilha
    planilha = workbook[nome_planilha]
    print(nome_da_planilha)
    
    # Lê o valor da célula
    valor = planilha[celula].value
    print(celula)
    
    # Fecha o arquivo do Excel
    workbook.close()
    
    return valor

def converter_para_extenso(valor):
    # Converte o valor para extenso em reais
    extenso = num2words(valor, lang='pt_BR', to='currency', currency='BRL')
    
    return extenso

# Informações do arquivo Excel
arquivo_excel = 'Matrix_2023_HRG.xlsx'
nome_da_planilha = 'ISS'
celula_com_valor = 'H24'

# Lê o valor do Excel
valor_excel = ler_valor_excel(arquivo_excel, nome_da_planilha, celula_com_valor)
print(valor_excel)

# Converte o valor para extenso em reais
extenso_em_reais = converter_para_extenso(valor_excel)

# Imprime o resultado
print(celula_com_valor)
print(f"O valor em reais é: {extenso_em_reais}")