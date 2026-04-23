import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import openpyxl
from openpyxl import load_workbook
import os
import subprocess
from datetime import datetime
import shutil

CONFIG_FILE = 'config.json'

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Formulário de Entrada de Dados")

        # Definir o ano atual como padrão
        self.ano_atual = datetime.now().year
        
        # Adicionar widgets ao layout
        tk.Label(root, text="Número da Cotação (3 dígitos):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.numero_entry = tk.Entry(root)
        self.numero_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Hospital:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.hospital_combobox = ttk.Combobox(root, values=["HRG", "APS", "HRG INV", "APS INV"])
        self.hospital_combobox.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(root, text="Ano da Cotação:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.ano_combobox = ttk.Combobox(root, values=["2023", "2022", "2021", "2020"], state="readonly")
        self.ano_combobox.set(str(self.ano_atual))  # Define o ano atual como valor padrão
        self.ano_combobox.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(root, text="Pasta de Trabalho:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.pasta_combobox = ttk.Combobox(root, values=["C:", "D:", "G:\\Meu Drive", "H:\\Meu Drive", "M:\\Meu Drive", "\\\\srv-fs\\HRG_GEOF"], state="readonly")
        self.pasta_combobox.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(root, text="Operador:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.operador_combobox = ttk.Combobox(root, values=["Bruno", "Clayton", "Guilherme", "Jefferson", "Oberdan", "Roéslei"], state="readonly")
        self.operador_combobox.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(root, text="Bimestre:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.bimestre_combobox = ttk.Combobox(root, values=["1", "2", "3", "4", "5", "6"], state="readonly")
        self.bimestre_combobox.grid(row=5, column=1, padx=10, pady=5)

        # Botão Enviar
        submit_button = tk.Button(root, text="Enviar", command=self.submit_form)
        submit_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Botão Criar Pasta
        criar_pasta_button = tk.Button(root, text="Criar Pasta", command=self.criar_pasta)
        criar_pasta_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Carregar configurações salvas
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.numero_entry.insert(0, config.get('numero_cotacao', ''))
                self.hospital_combobox.set(config.get('hospital', ''))
                self.ano_combobox.set(config.get('ano_cotacao', str(self.ano_atual)))
                self.pasta_combobox.set(config.get('pasta_de_trabalho', ''))
                self.operador_combobox.set(config.get('operador', ''))
                self.bimestre_combobox.set(config.get('bimestre', ''))

    def save_config(self):
        config = {
            #'numero_cotacao': self.numero_entry.get(),
            'hospital': self.hospital_combobox.get(),
            'ano_cotacao': self.ano_combobox.get(),
            'pasta_de_trabalho': self.pasta_combobox.get(),
            'operador': self.operador_combobox.get(),
            'bimestre': self.bimestre_combobox.get()
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def submit_form(self):
        # Obter valores dos widgets
        self.numero_cotacao = self.numero_entry.get()
        self.hospital = self.hospital_combobox.get()
        self.ano_cotacao = self.ano_combobox.get()
        self.pasta_de_trabalho = self.pasta_combobox.get()
        self.operador = self.operador_combobox.get()
        self.bimestre = self.bimestre_combobox.get()

        # Validar valores
        if not self.validate_cotacao(self.numero_cotacao):
            messagebox.showerror("Erro", "Número da Cotação deve ser um número de 3 dígitos.")
            return

        if not self.validate_ano(self.ano_cotacao):
            messagebox.showerror("Erro", "Ano inválido.")
            return

        # Salvar configurações
        self.save_config()

        # Exibir os valores ou fazer algo com eles
        self.display_results()

    def validate_cotacao(self, cotacao):
        return len(cotacao) == 3 and cotacao.isdigit()

    def validate_ano(self, ano):
        valid_years = {'2024', '2023', '2022', '2021', '2020'}
        return ano in valid_years

    def endereco_cotacao(self):
        # Garantir que a unidade de disco termina com uma barra invertida
        if not self.pasta_de_trabalho.endswith('\\'):
            self.pasta_de_trabalho += '\\'
        return os.path.join(self.pasta_de_trabalho, "GEOF", self.hospital, f"PDPAS {self.ano_cotacao}", self.numero_cotacao)

    def criar_pasta(self):
        # Construir o caminho da pasta
        proposta_path = self.endereco_cotacao()
        print(proposta_path)

        # Verificar e criar a pasta
        try:
            if not os.path.exists(proposta_path):
                os.makedirs(proposta_path)
                os.makedirs(os.path.join(proposta_path, "PROPOSTAS"))
                messagebox.showinfo("Sucesso", f"Pasta criada para a cotação {self.numero_cotacao}.")
            else:
                messagebox.showinfo("Info", f"A pasta para a cotação {self.numero_cotacao} já existe.")
            
            # Abrir o Windows Explorer na pasta criada
            subprocess.Popen(f'explorer "{proposta_path}"')
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível criar a pasta: {e}")

    def wb_matrix(self):
        end_matrix = os.path.join(self.pasta_de_trabalho, "GEOF", self.hospital, f"PDPAS {self.ano_cotacao}", "MATRIX", f"Matrix_{self.ano_cotacao}_{self.hospital}.xlsx")
        if not os.path.exists(end_matrix):
            raise FileNotFoundError(f"Arquivo não existe. Verifique se o caminho está correto: {end_matrix}")
        return load_workbook(end_matrix)
'''

def gerar_arquivo(wb_path, criar_cotacao_sheet_name, endereco_pasta_cotacao, hospital, ano_cotacao):
    # Abrir o arquivo do Excel
    wb = openpyxl.load_workbook(wb_path)
    criar_cotacao = wb[criar_cotacao_sheet_name]

    # Encontrar a última linha com dados na coluna A
    linhafinal = criar_cotacao.max_row
    
    for i in range(2, linhafinal + 1):
        n = criar_cotacao[f"A{i}"].value
        
        # Aqui você precisa definir como obter o caminho do arquivo para o matrix
        # Esse exemplo assume que nMatrix(hospital, ano_cotacao) é um nome de arquivo
        matrix_wb_name = nMatrix(hospital, ano_cotacao)
        
        # Abrir a planilha do matrix
        matrix_wb_path = os.path.join(endereco_pasta_cotacao, matrix_wb_name)
        if os.path.exists(matrix_wb_path):
            # Copiar o arquivo para o novo local
            destino_path = os.path.join(endereco_pasta_cotacao, n_cotacao(n))
            shutil.copy(matrix_wb_path, destino_path)
        else:
            print(f"Arquivo {matrix_wb_name} não encontrado em {endereco_pasta_cotacao}")
    
    # Fechar a planilha original (não é necessário em Python, pois o arquivo é salvo no final da função)

def nMatrix(hospital, ano_cotacao):
    # Função de exemplo que deve retornar o nome do arquivo baseado no hospital e ano
    return f"{hospital}_{ano_cotacao}.xlsx"

def n_cotacao(n):
    # Função de exemplo que deve retornar o nome do arquivo de destino baseado no valor n
    return f"cotacao_{n}.xlsx"

# Exemplo de uso
wb_path = "caminho_para_o_arquivo_excel.xlsx"
criar_cotacao_sheet_name = "Nome_da_Aba"
endereco_pasta_cotacao = "caminho_para_pasta_cotacao"
hospital = "HospitalXYZ"
ano_cotacao = 2024

gerar_arquivo(wb_path, criar_cotacao_sheet_name, endereco_pasta_cotacao, hospital, ano_cotacao)


'''

    def preparar_cotacao_a_publicar(self):
        workbook = load_workbook('caminho/para/criar_cotacao.xlsx')
        sheet = workbook.active
        max_row = sheet.max_row
        for i in range(2, max_row + 1):
            numero = sheet[f"A{i}"].value
            mycotacao = self.wb_cotacao(numero)
            mycotacao['Mapa']['I1'] = f"{sheet[f'A{i}'].value}/{self.ano_cotacao}"
            
            # Calcular a planilha (Openpyxl não tem cálculo automático como o Excel, você pode precisar atualizar os dados manualmente)
            
            planilha = ""
            if sheet[f"B{i}"].value == "NUAL":
                planilha = "Cot.A"
            elif sheet[f"B{i}"].value == "NFH":
                planilha = "Cot.F"
            elif sheet[f"B{i}"].value == "NPDOC":
                planilha = "Cot.N"
            elif sheet[f"B{i}"].value == "NAGMP":
                planilha = "Cot.M"
            elif sheet[f"B{i}"].value == "NECFM":
                planilha = "Cot.Eng"
            
            if planilha:
                self.esconder_linha_cot(self.n_cotacao(numero), planilha)
            
            self.fechar_cotacao_salve(i, self.n_cotacao(numero))

    # Funções adicionais (exemplo placeholders)
    def wb_cotacao(self, numero):
        # Substitua com a lógica real
        pass

    def esconder_linha_cot(self, n_cotacao, planilha):
        # Substitua com a lógica real
        pass

    def fechar_cotacao_salve(self, i, n_cotacao):
        # Substitua com a lógica real
        pass

    def display_results(self):
        result_message = (
            f"Número da Cotação: {self.numero_cotacao}\n"
            f"Hosptial: {self.hospital}\n"
            f"Ano da Cotação: {self.ano_cotacao}\n"
            f"Pasta de Trabalho: {self.pasta_de_trabalho}\n"
            f"Operador: {self.operador}\n"
            f"Bimestre: {self.bimestre}"
        )
        messagebox.showinfo("Dados Enviados", result_message)

# Criar a janela principal
root = tk.Tk()
app = App(root)
root.mainloop()
