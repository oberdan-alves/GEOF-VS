import tkinter as tk
from tkinter import messagebox
import pyautogui
import time
import threading

# ── Paleta ───────────────────────────────────────────────────────────────────
BG        = "#12151e"
BG2       = "#1a1f2e"
BG3       = "#222840"
ACCENT    = "#3b82f6"
ACHOVER   = "#2563eb"
SUCCESS   = "#10b981"
SUHOVER   = "#059669"
DANGER    = "#ef4444"
'''#ef4444'''
DAHOVER   = "#f0e748"
'''#c53030'''
NEUTRAL   = "#2d3554"
NHOVER    = "#3b4470"
YELLOW    = "#facc15"
TEXT      = "#fcfeff"
'''#e2e8f0"'''

TEXT2     = "#f5f576"
'''"#94a3b8  #d1d1b6"'''

TEXT3     = "#fc6570"
'''"#475569   #a37a7d"'''
BORDER    = "#2a3350"

F_TITLE  = ("Segoe UI", 15, "bold")
F_LABEL  = ("Segoe UI", 10)
F_BOLD   = ("Segoe UI", 10, "bold")
F_SMALL  = ("Segoe UI", 9)
F_MONO   = ("Consolas", 10)
F_BIG    = ("Segoe UI", 42, "bold")
F_BTN    = ("Segoe UI", 10, "bold")

def sep(parent, pady=6):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, pady=pady)

class AutomacaoSEIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SEI — Automação de Processos")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.dados            = []
        self.index_atual      = 0
        self.is_running       = False
        self.posicao_incluir  = None
        self.posicao_abrir    = None
        self.tempo_intervalo  = 6
        self._stop_flag       = False

        self._build_ui()

    def _build_ui(self):
        root = self.root

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        hdr = tk.Frame(root, bg=BG3)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="●", fg=ACCENT, bg=BG3,
                 font=("Segoe UI", 16)).pack(side=tk.LEFT, padx=(14,6), pady=10)
        tk.Label(hdr, text="Automação SEI", fg=TEXT, bg=BG3,
                 font=F_TITLE).pack(side=tk.LEFT)
        tk.Label(hdr, text="— Inclusão de Processos Vr02", fg=TEXT2, bg=BG3,
                 font=F_LABEL).pack(side=tk.LEFT, padx=(6,0))

        # ── Corpo: esquerda + direita ─────────────────────────────────────────
        body = tk.Frame(root, bg=BG, padx=14, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,12))

        right = tk.Frame(body, bg=BG, width=240)
        right.pack(side=tk.LEFT, fill=tk.Y)
        right.pack_propagate(False)

        # ── ESQUERDA ──────────────────────────────────────────────────────────
        tk.Label(left, text="LISTA DE PROCESSOS", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,2))
        tk.Label(left, text="Cole um processo por linha:", fg=TEXT2, bg=BG,
                 font=F_LABEL).pack(anchor="w", pady=(0,4))

        self.text_area = tk.Text(
            left, height=11, bg=BG2, fg=TEXT,
            insertbackground=ACCENT, relief=tk.FLAT,
            font=F_MONO, padx=8, pady=8,
            selectbackground=ACCENT, selectforeground=TEXT,
            highlightthickness=1, highlightbackground=BORDER,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        sep(left)

        tk.Label(left, text="CONFIGURAÇÕES", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,4))

        row1 = tk.Frame(left, bg=BG)
        row1.pack(fill=tk.X, pady=3)
        tk.Label(row1, text="Intervalo entre ações (segundos):", fg=TEXT2,
                 bg=BG, font=F_LABEL).pack(side=tk.LEFT)
        self.entry_tempo = tk.Entry(row1, width=5, bg=BG2, fg=TEXT,
                                    insertbackground=ACCENT, relief=tk.FLAT,
                                    font=F_MONO, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_tempo.insert(0, str(self.tempo_intervalo))
        self.entry_tempo.pack(side=tk.LEFT, padx=(8,0))

        row2 = tk.Frame(left, bg=BG)
        row2.pack(fill=tk.X, pady=3)
        tk.Label(row2, text="Retomar a partir do item nº:", fg=TEXT2,
                 bg=BG, font=F_LABEL).pack(side=tk.LEFT)
        self.entry_retomar = tk.Entry(row2, width=5, bg=BG2, fg=TEXT,
                                      insertbackground=ACCENT, relief=tk.FLAT,
                                      font=F_MONO, highlightthickness=1,
                                      highlightbackground=BORDER)
        self.entry_retomar.insert(0, "1")
        self.entry_retomar.pack(side=tk.LEFT, padx=(8,0))
        tk.Label(row2, text="(use após pausar)", fg=TEXT3, bg=BG,
                 font=F_SMALL).pack(side=tk.LEFT, padx=(6,0))

        sep(left)

        tk.Label(left, text="STATUS", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,2))
        self.lbl_status = tk.Label(left, text="Aguardando início…",
                                   fg=TEXT2, bg=BG, font=F_LABEL,
                                   anchor="w", wraplength=360, justify=tk.LEFT)
        self.lbl_status.pack(fill=tk.X, pady=(0,6))

        prog_bg = tk.Frame(left, bg=BORDER, height=8)
        prog_bg.pack(fill=tk.X)
        self.prog_fill = tk.Frame(prog_bg, bg=ACCENT, height=8)
        self.prog_fill.place(relx=0, rely=0, relwidth=0, relheight=1)

        self.lbl_prog = tk.Label(left, text="0 / 0 processos",
                                 fg=TEXT3, bg=BG, font=F_SMALL)
        self.lbl_prog.pack(anchor="w", pady=(4,0))

        # ── DIREITA ───────────────────────────────────────────────────────────
        tk.Label(right, text="FILA DE PROCESSOS", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,4))
        self.queue_frame = tk.Frame(right, bg=BG)
        self.queue_frame.pack(fill=tk.BOTH, expand=True)

        sep(right)

        tk.Label(right, text="PRÓXIMO ITEM EM", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0,2))
        self.lbl_countdown = tk.Label(right, text="—", fg=YELLOW,
                                      bg=BG, font=F_BIG)
        self.lbl_countdown.pack()

        # ── Rodapé: botões ────────────────────────────────────────────────────
        footer = tk.Frame(root, bg=BG3, pady=10)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        inner = tk.Frame(footer, bg=BG3)
        inner.pack()

        self.btn_iniciar = self._btn(inner, "▶  Iniciar",  ACCENT,  ACHOVER, self.iniciar_automacao)
        self.btn_parar   = self._btn(inner, "■  Parar",    DANGER,  DAHOVER, self.parar_automacao, state=tk.DISABLED)
        self.btn_voltar  = self._btn(inner, "◀  Voltar",   NEUTRAL, NHOVER,  self.voltar_item)
        self.btn_adiant  = self._btn(inner, "▶  Adiantar", NEUTRAL, NHOVER,  self.adiantar_item)
        self.btn_retomar = self._btn(inner, "↩  Retomar",  SUCCESS, SUHOVER, self.retomar_posicao)
        for b in (self.btn_iniciar, self.btn_parar,
                  self.btn_voltar, self.btn_adiant, self.btn_retomar):
            b.pack(side=tk.LEFT, padx=5)

    def _btn(self, parent, text, bg, hover, cmd, state=tk.NORMAL):
        b = tk.Button(parent, text=text, bg=bg, fg=TEXT,
                      activebackground=hover, activeforeground=TEXT,
                      relief=tk.FLAT, cursor="hand2",
                      font=F_BTN, padx=14, pady=8,
                      state=state, bd=0, command=cmd)
        b.bind("<Enter>", lambda e, w=b, h=hover: w.config(bg=h))
        b.bind("<Leave>", lambda e, w=b, c=bg:    w.config(bg=c))
        return b

    def _update_queue(self):
        for w in self.queue_frame.winfo_children():
            w.destroy()
        if not self.dados:
            tk.Label(self.queue_frame, text="(sem itens)", fg=TEXT3,
                     bg=BG, font=F_SMALL).pack(anchor="w")
            return
        start = max(0, self.index_atual - 2)
        end   = min(len(self.dados), self.index_atual + 9)
        for i in range(start, end):
            is_cur  = (i == self.index_atual)
            is_done = (i < self.index_atual)
            rbg = BG2 if is_cur else BG
            row = tk.Frame(self.queue_frame, bg=rbg,
                           highlightthickness=1 if is_cur else 0,
                           highlightbackground=ACCENT)
            row.pack(fill=tk.X, pady=1)
            arrow = "➤" if is_cur else ("✓" if is_done else " ")
            afg   = YELLOW if is_cur else (SUCCESS if is_done else TEXT3)
            tk.Label(row, text=arrow, fg=afg, bg=rbg,
                     font=F_BOLD, width=2).pack(side=tk.LEFT, padx=(4,2))
            txt = self.dados[i]
            if len(txt) > 26: txt = txt[:25] + "…"
            fg_  = TEXT  if is_cur else (TEXT3 if is_done else TEXT2)
            fnt_ = F_BOLD if is_cur else F_SMALL
            tk.Label(row, text=f"{i+1}. {txt}", fg=fg_, bg=rbg,
                     font=fnt_, anchor="w", pady=4).pack(side=tk.LEFT)

    def _update_progress(self):
        total = len(self.dados)
        pct   = self.index_atual / total if total else 0
        self.prog_fill.place(relwidth=pct)
        self.lbl_prog.config(text=f"{self.index_atual} / {total} processos")

    def capturar_posicao_mouse(self, mensagem):
        messagebox.showinfo("Instrução", mensagem)
        time.sleep(4)
        return pyautogui.position()

    def _run_countdown(self, seconds=3):
        self._stop_flag = False
        for i in range(seconds, 0, -1):
            if self._stop_flag or not self.is_running:
                self.lbl_countdown.config(text="—")
                return False
            self.lbl_countdown.config(text=str(i))
            time.sleep(1)
        self.lbl_countdown.config(text="—")
        return not self._stop_flag and self.is_running

    def iniciar_automacao(self):
        try:
            A = int(self.entry_tempo.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Insira um número válido para o intervalo.")
            return
        dados_txt  = self.text_area.get("1.0", tk.END).strip()
        self.dados = [d.strip() for d in dados_txt.splitlines() if d.strip()]
        if not self.dados:
            messagebox.showwarning("Aviso", "Cole a lista de processos antes de iniciar.")
            return
        self.posicao_incluir = self.capturar_posicao_mouse(
            "Posicione o mouse no campo de inclusão do processo.\n"
            "A posição será capturada após 4 segundos.")
        messagebox.showinfo("Posição capturada",
                            f"Campo de inclusão: {self.posicao_incluir}")
        self.posicao_abrir = self.capturar_posicao_mouse(
            "Agora posicione o mouse no botão 'Abrir Processo'.\n"
            "A posição será capturada após 4 segundos.")
        messagebox.showinfo("Posição capturada",
                            f"Botão 'Abrir Processo': {self.posicao_abrir}")
        if not self.posicao_incluir or not self.posicao_abrir:
            messagebox.showerror("Erro", "Posições não definidas. Tente novamente.")
            return
        self.index_atual = 0
        self._start_execution()

    def _start_execution(self):
        self.is_running = True
        self._stop_flag = False
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_parar.config(state=tk.NORMAL)
        self._update_queue()
        self._update_progress()
        self.lbl_status.config(
            text=f"Iniciando — Item {self.index_atual + 1} de {len(self.dados)}")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            while self.index_atual < len(self.dados) and self.is_running:
                dado = self.dados[self.index_atual]
                self.lbl_status.config(
                    text=f"Processando item {self.index_atual + 1}: {dado[:45]}")
                self._update_queue()
                pyautogui.click(self.posicao_incluir)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.write(dado, interval=0.03)
                pyautogui.press('enter')
                time.sleep(self.tempo_intervalo)
                pyautogui.click(self.posicao_abrir)
                time.sleep(self.tempo_intervalo)
                self.index_atual += 1
                self._update_progress()
                if self.index_atual < len(self.dados) and self.is_running:
                    self.lbl_status.config(text="Aguardando próximo item…")
                    if not self._run_countdown(3):
                        break
            if self.is_running:
                self.lbl_status.config(text="✅  Todos os processos concluídos!")
                self._finish()
        except Exception as e:
            self.lbl_status.config(text=f"Erro: {e}")
            self._finish()

    def _finish(self):
        self.is_running = False
        self.lbl_countdown.config(text="—")
        self.btn_parar.config(state=tk.DISABLED)
        self.btn_iniciar.config(state=tk.NORMAL)
        self._update_queue()
        self._update_progress()

    def parar_automacao(self):
        self._stop_flag = True
        self.is_running = False
        self.lbl_countdown.config(text="—")
        self.lbl_status.config(
            text=f"⏸  Pausado no item {self.index_atual + 1}. "
                 f"Use '↩ Retomar' ou ajuste o item e clique Retomar.")
        self.btn_parar.config(state=tk.DISABLED)
        self.btn_iniciar.config(state=tk.NORMAL)

    def voltar_item(self):
        if self.index_atual > 0:
            self.index_atual -= 1
            self.entry_retomar.delete(0, tk.END)
            self.entry_retomar.insert(0, str(self.index_atual + 1))
            self._update_queue()
            self._update_progress()
            self.lbl_status.config(text=f"Item ajustado para {self.index_atual + 1}")

    def adiantar_item(self):
        if self.index_atual < len(self.dados) - 1:
            self.index_atual += 1
            self.entry_retomar.delete(0, tk.END)
            self.entry_retomar.insert(0, str(self.index_atual + 1))
            self._update_queue()
            self._update_progress()
            self.lbl_status.config(text=f"Item ajustado para {self.index_atual + 1}")

    def retomar_posicao(self):
        if not self.dados:
            messagebox.showwarning("Aviso", "Cole a lista antes de retomar.")
            return
        if not self.posicao_incluir or not self.posicao_abrir:
            messagebox.showwarning("Aviso",
                "Posições do mouse não capturadas.\n"
                "Clique em 'Iniciar' primeiro para capturá-las.")
            return
        try:
            inicio = int(self.entry_retomar.get()) - 1
        except ValueError:
            messagebox.showwarning("Aviso", "Informe um número válido no campo 'Retomar'.")
            return
        if not (0 <= inicio < len(self.dados)):
            messagebox.showwarning("Aviso",
                f"Número fora do intervalo. Informe entre 1 e {len(self.dados)}.")
            return
        self.index_atual = inicio
        self._start_execution()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=BG)
    w, h = 780, 600
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    AutomacaoSEIApp(root)
    root.mainloop()