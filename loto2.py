import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox
import random

# Configuração visual do tema
ctk.set_appearance_mode("Dark")  # Modo escuro ativado
ctk.set_default_color_theme("blue")  # Cor dos botões e destaques

class AppLotofacil(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Lotofácil AI - Analisador Estatístico")
        self.geometry("600x550")

        # --- Layout da Interface ---
        self.label_titulo = ctk.CTkLabel(self, text="ANÁLISE DE TENDÊNCIAS", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=20)

        # Frame de Seleção de Arquivo
        self.frame_busca = ctk.CTkFrame(self)
        self.frame_busca.pack(pady=10, padx=20, fill="x")

        self.entry_caminho = ctk.CTkEntry(self.frame_busca, placeholder_text="Selecione o arquivo Excel...")
        self.entry_caminho.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.btn_buscar = ctk.CTkButton(self.frame_busca, text="BUSCAR EXCEL", command=self.selecionar_arquivo)
        self.btn_buscar.pack(side="right", padx=10)

        # Botão de Processamento
        self.btn_gerar = ctk.CTkButton(self, text="CALCULAR PROBABILIDADES", 
                                       command=self.processar_excel,
                                       fg_color="#27ae60", hover_color="#2ecc71",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_gerar.pack(pady=20)

        # Caixa de Texto para o Resultado (Visual Escuro)
        self.txt_display = ctk.CTkTextbox(self, width=500, height=250, font=("Courier New", 13))
        self.txt_display.pack(pady=10, padx=20)

    def selecionar_arquivo(self):
        # Filtra especificamente por arquivos do Excel (.xlsx)
        arquivo = filedialog.askopenfilename(title="Localizar Planilha Lotofácil",
                                           filetypes=[("Arquivos Excel", "*.xlsx")])
        if arquivo:
            self.entry_caminho.delete(0, "end")
            self.entry_caminho.insert(0, arquivo)

    def processar_excel(self):
        caminho = self.entry_caminho.get()
        if not caminho:
            messagebox.showwarning("Aviso", "Por favor, localize o arquivo .xlsx primeiro.")
            return

        try:
            # Lendo o arquivo Excel diretamente
            # O motor 'openpyxl' garante a compatibilidade com arquivos modernos
            df = pd.read_excel(caminho)

            # Mapeia as colunas de 'Bola1' até 'Bola15'
            colunas_alvo = [f'Bola{i}' for i in range(1, 16)]
            todos_numeros = df[colunas_alvo].values.flatten()
            
            # Cálculo de Frequência
            contagem = pd.Series(todos_numeros).value_counts()
            
            # Estratégia: 10 Quentes (mais saem) + 5 Frias (atrasadas)
            mais_frequentes = contagem.nlargest(10).index.tolist()
            menos_frequentes = contagem.nsmallest(5).index.tolist()
            
            # Geração do jogo final de 15 números
            jogo = sorted(list(set(mais_frequentes + menos_frequentes)))
            
            # Garante que temos exatamente 15 (ajuste por empates na contagem)
            while len(jogo) < 15:
                n = random.randint(1, 25)
                if n not in jogo:
                    jogo.append(n)
            jogo.sort()

            # Exibição estilizada no campo de texto
            self.txt_display.delete("1.0", "end")
            self.txt_display.insert("insert", "=== RESULTADO DA ANÁLISE ===\n\n")
            self.txt_display.insert("insert", f"Arquivo: {caminho.split('/')[-1]}\n")
            self.txt_display.insert("insert", f"Total de Concursos Analisados: {len(df)}\n")
            self.txt_display.insert("insert", "-"*40 + "\n")
            self.txt_display.insert("insert", "SUGESTÃO DE JOGO (15 DEZENAS):\n\n")
            self.txt_display.insert("insert", "  ".join(f"[{n:02d}]" for n in jogo))
            self.txt_display.insert("insert", "\n\n" + "-"*40 + "\n")
            
            # Análise de Paridade (Pares/Ímpares)
            pares = len([n for n in jogo if n % 2 == 0])
            self.txt_display.insert("insert", f"Estatística: {pares} Pares e {15-pares} Ímpares.")

        except Exception as e:
            messagebox.showerror("Erro de Processamento", f"Verifique se as colunas 'Bola1' até 'Bola15' existem na planilha.\nErro: {e}")

if __name__ == "__main__":
    app = AppLotofacil()
    app.mainloop()