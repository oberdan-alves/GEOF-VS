import tkinter as tk  
from tkinter import messagebox  
import pyautogui  
import time  
  
class App(tk.Tk):  
   def __init__(self):  
      super().__init__()  
      self.title("Processo SEI")  
      self.geometry("400x300")  
  
      # Criação dos campos de entrada para as localizações  
      self.label_processo_sei = tk.Label(self, text="PROCESSO SEI")  
      self.label_processo_sei.grid(row=0, column=0)  
      self.entry_processo_sei = tk.Entry(self)  
      self.entry_processo_sei.grid(row=0, column=1)  
  
      self.label_reabrir_processo = tk.Label(self, text="REABRIR PROCESSO")  
      self.label_reabrir_processo.grid(row=1, column=0)  
      self.entry_reabrir_processo = tk.Entry(self)  
      self.entry_reabrir_processo.grid(row=1, column=1)  
  
      # Botão para capturar a primeira localização  
      self.button_capturar_processo_sei = tk.Button(self, text="Capturar PROCESSO SEI", command=self.capturar_processo_sei)  
      self.button_capturar_processo_sei.grid(row=2, column=0)  
  
      # Botão para capturar a segunda localização  
      self.button_capturar_reabrir_processo = tk.Button(self, text="Capturar REABRIR PROCESSO", command=self.capturar_reabrir_processo)  
      self.button_capturar_reabrir_processo.grid(row=2, column=1)  
  
      # Campo de texto para mostrar as localizações capturadas  
      self.text_localizacoes = tk.Text(self, height=5, width=40)  
      self.text_localizacoes.grid(row=3, column=0, columnspan=2)  
  
      # Campo de entrada para a listagem de processos  
      self.label_processos = tk.Label(self, text="Processos")  
      self.label_processos.grid(row=4, column=0)  
      self.entry_processos = tk.Text(self, height=10, width=40)  
      self.entry_processos.grid(row=4, column=1)  
  
      # Botão para executar o processo  
      self.button_executar = tk.Button(self, text="Executar", command=self.executar_processo)  
      self.button_executar.grid(row=5, column=0)  
  
      # Variáveis para armazenar as localizações e a linha atual  
      self.localizacao_processo_sei = None  
      self.localizacao_reabrir_processo = None  
      self.linha_atual = 0  
  
   def capturar_processo_sei(self):  
      # Aguarda 3 segundos antes de capturar a localização  
      time.sleep(3)  
      self.localizacao_processo_sei = pyautogui.position()  
      self.text_localizacoes.delete(1.0, tk.END)  
      self.text_localizacoes.insert(tk.END, f"PROCESSO SEI: {self.localizacao_processo_sei}")  
  
   def capturar_reabrir_processo(self):  
      # Aguarda 3 segundos antes de capturar a localização  
      time.sleep(3)  
      self.localizacao_reabrir_processo = pyautogui.position()  
      self.text_localizacoes.delete(1.0, tk.END)  
      self.text_localizacoes.insert(tk.END, f"REABRIR PROCESSO: {self.localizacao_reabrir_processo}")  
  
   def executar_processo(self):  
      # Pega a linha atual da listagem de processos  
      linha = self.entry_processos.get(f"{self.linha_atual+1}.0", f"{self.linha_atual+2}.0")  
      # Vai para a posição salva "PROCESSO SEI" e cola os dados da linha escolhida  
      pyautogui.moveTo(self.localizacao_processo_sei)  
      pyautogui.click()  
      pyautogui.typewrite(linha)  
      pyautogui.press("enter")  
      # Para o processo aguardando novas instruções  
      messagebox.showinfo("Processo executado", "Processo executado com sucesso!")  
      # Incrementa a linha atual  
      self.linha_atual += 1  
  
if __name__ == "__main__":  
   app = App()  
   app.mainloop()
