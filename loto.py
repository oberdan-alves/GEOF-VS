import pandas as pd
import random

def analisar_lotofacil(caminho_arquivo):
    # Carregar o arquivo (ajustando o separador se necessário)
    df = pd.read_csv(caminho_arquivo)
    
    # Selecionar apenas as colunas das bolas (Bola1 até Bola15)
    colunas_bolas = [f'Bola{i}' for i in range(1, 16)]
    todas_as_bolas = df[colunas_bolas].values.flatten()
    
    # Contar a frequência de cada número (1 a 25)
    frequencias = pd.Series(todas_as_bolas).value_counts().sort_index()
    
    # 1. Os 10 números mais frequentes (Quentes)
    quentes = frequencias.nlargest(10).index.tolist()
    
    # 2. Os 5 números menos frequentes (Frios - para balancear tendência de retorno)
    frios = frequencias.nsmallest(5).index.tolist()
    
    # 3. Gerar sugestão balanceada (Pares e Ímpares)
    sugestao = list(set(quentes + frios))
    
    # Garantir que temos exatamente 15 números (caso haja sobreposição)
    while len(sugestao) < 15:
        num = random.randint(1, 25)
        if num not in sugestao:
            sugestao.append(num)
            
    sugestao.sort()
    
    print(f"--- ANÁLISE DO ARQUIVO: {caminho_arquivo} ---")
    print(f"Números mais sorteados (Top 10): {quentes}")
    print(f"Números menos sorteados (Frios): {frios}")
    print(f"\nSUGESTÃO DE JOGO (15 números):")
    print(sugestao)
    
    # Validação de Pares/Ímpares
    pares = [n for n in sugestao if n % 2 == 0]
    impares = [n for n in sugestao if n % 2 != 0]
    print(f"\nEquilíbrio: {len(pares)} Pares e {len(impares)} Ímpares.")

# Para rodar, basta garantir que o arquivo CSV está na mesma pasta
analisar_lotofacil('Lotofácil (1).xlsx - LOTOFÁCIL.csv')