import tkinter as tk
from tkinter import messagebox
import pyautogui
import time

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Automação de Cliques")
        self.master.geometry("300x300")
        
        self.processo_sei_pos = None
        self.reabrir_processo_pos = None

        self.lbl_processo_sei = tk.Label(master, text="Posição 'PROCESSO SEI': Não definida")
        self.lbl_processo_sei.pack(pady=10)

        self.lbl_reabrir_processo = tk.Label(master, text="Posição 'REABRIR PROCESSO': Não definida")
        self.lbl_reabrir_processo.pack(pady=10)

        self.btn_set_processo = tk.Button(master, text="Definir Posição 'PROCESSO SEI'", command=self.set_processo_sei)
        self.btn_set_processo.pack(pady=10)

        self.btn_set_reabrir = tk.Button(master, text="Definir Posição 'REABRIR PROCESSO'", command=self.set_reabrir_processo)
        self.btn_set_reabrir.pack(pady=10)

        self.btn_next = tk.Button(master, text="Iniciar Processo", command=self.open_data_input)
        self.btn_next.pack(pady=20)

    def set_processo_sei(self):
        self.process_position('PROCESSO SEI')

    def set_reabrir_processo(self):
        self.process_position('REABRIR PROCESSO')

    def process_position(self, process_name):
        messagebox.showinfo("Atenção", f"Clique na posição da tela para '{process_name}'. O programa irá esperar 3 segundos antes de capturar a posição.")
        
        # Aguardar 3 segundos
        time.sleep(3)
        
        # Captura a posição do mouse após a espera
        pos = pyautogui.position()
        
        if process_name == 'PROCESSO SEI':
            self.processo_sei_pos = pos
            self.lbl_processo_sei.config(text=f"Posição 'PROCESSO SEI': {pos}")
        else:
            self.reabrir_processo_pos = pos
            self.lbl_reabrir_processo.config(text=f"Posição 'REABRIR PROCESSO': {pos}")
        
        messagebox.showinfo("Posição Capturada", f"Posição '{process_name}' capturada em: {pos}")

    def open_data_input(self):
        self.data_window = tk.Toplevel(self.master)
        self.data_window.title("Entrada de Dados")
        self.data_window.geometry("400x300")
        
        self.textbox = tk.Text(self.data_window, height=10, width=50)
        self.textbox.pack(pady=10)

        self.btn_execute = tk.Button(self.data_window, text="Executar", command=self.execute_process)
        self.btn_execute.pack(pady=10)

    def execute_process(self):
        if self.processo_sei_pos is None or self.reabrir_processo_pos is None:
            messagebox.showerror("Erro", "As posições 'PROCESSO SEI' e 'REABRIR PROCESSO' não estão definidas.")
            return

        data = self.textbox.get("1.0", tk.END).strip().splitlines()
        
        for value in data:
            if value.strip():
                self.master.lift()

                # Clicar na posição 'PROCESSO SEI'
                print(f"Clicando na posição 'PROCESSO SEI' em {self.processo_sei_pos}")
                pyautogui.click(self.processo_sei_pos)
                time.sleep(3)

                # Colar o valor
                print(f"Digitando o valor: '{value}'")
                pyautogui.typewrite(value)
                time.sleep(3)

                # Pressionar Enter
                print("Pressionando 'Enter'")
                pyautogui.press('enter')
                time.sleep(3)

                # Clicar na posição 'REABRIR PROCESSO'
                print(f"Clicando na posição 'REABRIR PROCESSO' em {self.reabrir_processo_pos}")
                pyautogui.click(self.reabrir_processo_pos)
                time.sleep(3)

        messagebox.showinfo("Concluído", "Processo concluído.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
