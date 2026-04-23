import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading

class AutomacaoSEIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automação de Inclusão de Processo SEI")

        # Lista de dados e controle de índice
        self.dados = []
        self.index_atual = 0
        self.is_running = False
        self.posicao_incluir_processo = None
        self.posicao_abrir_processo = None
        self.tempo_intervalo = 6  # Tempo padrão em segundos

        # Interface
        self.label_status = tk.Label(root, text="Cole a lista, depois clique em iniciar", font=("Arial", 14))
        self.label_status.pack(pady=10)

        self.text_area = tk.Text(root, height=10, width=50)
        self.text_area.pack(pady=10)

        self.label_tempo = tk.Label(root, text="Intervalo de tempo entre ações (em segundos):")
        self.label_tempo.pack(pady=5)

        self.entry_tempo = tk.Entry(root)
        self.entry_tempo.insert(0, str(self.tempo_intervalo))  # Insere o valor padrão no campo
        self.entry_tempo.pack(pady=5)

        self.botao_iniciar = tk.Button(root, text="Iniciar", command=self.iniciar_automacao)
        self.botao_iniciar.pack(side=tk.LEFT, padx=10)

        self.botao_parar = tk.Button(root, text="Parar", command=self.parar_automacao)
        self.botao_parar.pack(side=tk.LEFT, padx=10)

        self.botao_voltar = tk.Button(root, text="Voltar Item", command=self.voltar_item)
        self.botao_voltar.pack(side=tk.LEFT, padx=10)

        self.botao_adiantar = tk.Button(root, text="Adiantar Item", command=self.adiantar_item)
        self.botao_adiantar.pack(side=tk.LEFT, padx=10)

    def capturar_posicao_mouse(self, mensagem):
        """Função para capturar a posição do mouse após alguns segundos"""
        messagebox.showinfo("Instrução", mensagem)
        #time.sleep(self.tempo_intervalo)
        time.sleep(4)
        posicao = pyautogui.position()
        return posicao

    def iniciar_automacao(self):
        try:
            self.tempo_intervalo = int(self.entry_tempo.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Por favor, insira um valor numérico para o intervalo de tempo.")
            return

        dados_texto = self.text_area.get("1.0", tk.END).strip()
        self.dados = dados_texto.splitlines()

        if not self.dados:
            messagebox.showwarning("Aviso", "Insira uma lista de dados antes de iniciar.")
            return

        self.posicao_incluir_processo = self.capturar_posicao_mouse(
            "Posicione o mouse no campo onde deseja incluir o processo. O sistema irá capturar a posição."
        )
        messagebox.showinfo("Captura", f"Posição capturada: {self.posicao_incluir_processo}")

        self.posicao_abrir_processo = self.capturar_posicao_mouse(
            "Posicione o mouse no botão 'Abrir Processo'. O sistema irá capturar a posição."
        )
        messagebox.showinfo("Captura", f"Posição 'Abrir Processo' capturada: {self.posicao_abrir_processo}")

        if not self.posicao_incluir_processo or not self.posicao_abrir_processo:
            messagebox.showerror("Erro", "Posições não definidas corretamente.")
            return

        self.label_status.config(text=f"Executando automação - Item {self.index_atual + 1}")
        self.is_running = True
        threading.Thread(target=self.automatizar).start()

    def automatizar(self):
        try:
            while self.index_atual < len(self.dados) and self.is_running:
                dado_atual = self.dados[self.index_atual]

                pyautogui.click(self.posicao_incluir_processo)
                pyautogui.write(dado_atual)
                pyautogui.press('enter')

                time.sleep(self.tempo_intervalo)

                pyautogui.click(self.posicao_abrir_processo)

                time.sleep(self.tempo_intervalo)

                self.index_atual += 1
                self.label_status.config(text=f"Executando automação - Item {self.index_atual + 1}")

            self.label_status.config(text="Automação concluída")

        except Exception as e:
            print(f"Ocorreu um erro durante a automação: {e}")
            self.label_status.config(text="Erro na automação")

    def parar_automacao(self):
        self.is_running = False
        self.label_status.config(text="Automação parada")

    def voltar_item(self):
        if self.index_atual > 0:
            self.index_atual -= 1
            self.label_status.config(text=f"Executando automação - Item {self.index_atual + 1}")

    def adiantar_item(self):
        if self.index_atual < len(self.dados) - 1:
            self.index_atual += 1
            self.label_status.config(text=f"Executando automação - Item {self.index_atual + 1}")

# Inicializando a interface gráfica
if __name__ == "__main__":
    root = tk.Tk()
    app = AutomacaoSEIApp(root)
    root.mainloop()
