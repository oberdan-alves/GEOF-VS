import tkinter as tk
from tkinter import messagebox
import pyautogui
import time

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Abertura Processos SEI")
        self.master.geometry("420x420")

        self.processo_sei_pos = None
        self.reabrir_processo_pos = None
        self.data_list = []  # Lista de dados
        self.current_line = 0  # Índice da linha atual

        self.lbl_processo_sei = tk.Label(master, text="Posição 'PROCESSO SEI': Não definida")
        self.lbl_processo_sei.pack(pady=10)

        self.lbl_reabrir_processo = tk.Label(master, text="Posição 'REABRIR PROCESSO': Não definida")
        self.lbl_reabrir_processo.pack(pady=10)

        self.btn_set_processo = tk.Button(master, text="Definir Posição 'PROCESSO SEI'", command=self.set_processo_sei)
        self.btn_set_processo.pack(pady=10)

        self.btn_set_reabrir = tk.Button(master, text="Definir Posição 'REABRIR PROCESSO'", command=self.set_reabrir_processo)
        self.btn_set_reabrir.pack(pady=10)

        self.btn_start = tk.Button(master, text="Posições Salvas, Iniciar Processo", command=self.open_data_input)
        self.btn_start.pack(pady=20)

    def set_processo_sei(self):
        self.process_position('PROCESSO SEI')

    def set_reabrir_processo(self):
        self.process_position('REABRIR PROCESSO')

    def process_position(self, process_name):
        messagebox.showinfo("Atenção", f"Clique no OK e coloque o mouse na posição da tela para '{process_name}'. Você tem 3 segundos antes da captura da posição.")
        time.sleep(3)
        pos = pyautogui.position()
        
        if process_name == 'PROCESSO SEI':
            self.processo_sei_pos = pos
            self.lbl_processo_sei.config(text=f"Posição 'PROCESSO SEI': {pos}")
        else:
            self.reabrir_processo_pos = pos
            self.lbl_reabrir_processo.config(text=f"Posição 'REABRIR PROCESSO': {pos}")
        
        messagebox.showinfo("Posição Capturada", f"Posição '{process_name}' capturada em: {pos}")

    def open_data_input(self):
        # Criar a janela de entrada de dados
        self.data_window = tk.Toplevel(self.master)
        self.data_window.title("Entrada Dados/Execução")
        self.data_window.geometry("400x500")

        # Caixa de texto para entrada de dados
        self.textbox = tk.Text(self.data_window, height=10, width=50)
        self.textbox.pack(pady=10)

        # Botão para carregar dados
        self.btn_load_data = tk.Button(self.data_window, text="Cole a lista e clique aqui", command=self.load_data)
        self.btn_load_data.pack(pady=10)

        # Frame para os botões de navegação e execução
        self.button_frame = tk.Frame(self.data_window)
        self.button_frame.pack(pady=10)

        # Label para mostrar a linha atual
        self.lbl_current_line = tk.Label(self.data_window, text="")
        self.lbl_current_line.pack(pady=10)

        # Botões para controle de execução
        self.btn_execute = tk.Button(self.button_frame, text="Executar", command=self.execute_process)
        self.btn_execute.pack(side=tk.LEFT, padx=5)

        self.btn_previous = tk.Button(self.button_frame, text="Voltar", command=self.previous_line)
        self.btn_previous.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(self.button_frame, text="Próximo", command=self.next_line)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        # Inicialmente desativar os botões até que os dados sejam carregados
        self.disable_buttons()

    def load_data(self):
        # Carrega os dados do TextBox
        data = self.textbox.get("1.0", tk.END).strip().splitlines()
        self.data_list = [line for line in data if line.strip()]
        self.current_line = 0

        if self.data_list:
            self.update_current_line_display()
            self.enable_buttons()  # Habilita os botões após o carregamento dos dados
            messagebox.showinfo("Sucesso", "Dados carregados com sucesso!")
        else:
            messagebox.showerror("Erro", "Nenhum dado válido foi inserido.")
            self.disable_buttons()

    def update_current_line_display(self):
        """Atualiza a exibição da linha atual na interface"""
        if 0 <= self.current_line < len(self.data_list):
            self.lbl_current_line.config(text=f"Linha {self.current_line + 1}: {self.data_list[self.current_line]}")
        else:
            self.lbl_current_line.config(text="Nenhuma linha disponível.")

    def disable_buttons(self):
        """Desativa os botões de controle"""
        self.btn_execute.config(state=tk.DISABLED)
        self.btn_previous.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)

    def enable_buttons(self):
        """Ativa os botões de controle"""
        self.btn_execute.config(state=tk.NORMAL)
        self.btn_previous.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)

    def execute_process(self):
        if not self.data_list:
            messagebox.showerror("Erro", "Nenhum dado foi carregado.")
            return

        if self.processo_sei_pos is None or self.reabrir_processo_pos is None:
            messagebox.showerror("Erro", "As posições 'PROCESSO SEI' e 'REABRIR PROCESSO' não estão definidas.")
            return

        if 0 <= self.current_line < len(self.data_list):
            value = self.data_list[self.current_line]
            self.master.lift()

            # Executa os cliques e inserções de forma manual, linha por linha
            print(f"Clicando na posição 'PROCESSO SEI' em {self.processo_sei_pos}")
            pyautogui.click(self.processo_sei_pos)
            time.sleep(3)

            print(f"Digitando o valor: '{value}'")
            pyautogui.typewrite(value)
            time.sleep(3)

            print("Pressionando 'Enter'")
            pyautogui.press('enter')
            time.sleep(5)

            print(f"Clicando na posição 'REABRIR PROCESSO' em {self.reabrir_processo_pos}")
            pyautogui.click(self.reabrir_processo_pos)
            time.sleep(3)

            messagebox.showinfo("Linha Concluída", f"Linha {self.current_line + 1} de {len(self.data_list)} processada.")

    def next_line(self):
        """Avança para a próxima linha, se houver"""
        if self.current_line < len(self.data_list) - 1:
            self.current_line += 1
            self.update_current_line_display()
        else:
            messagebox.showinfo("Fim da Lista", "Você já está na última linha.")
    
    def previous_line(self):
        """Volta para a linha anterior, se houver"""
        if self.current_line > 0:
            self.current_line -= 1
            self.update_current_line_display()
        else:
            messagebox.showinfo("Início da Lista", "Você já está na primeira linha.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
