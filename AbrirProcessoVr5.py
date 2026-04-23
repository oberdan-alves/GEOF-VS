import tkinter as tk
from tkinter import messagebox, ttk
import pyautogui
import time
import threading
import winsound
import pyperclip
import unicodedata
import re

# ── Paleta ───────────────────────────────────────────────────────────────────
BG        = "#12151e"
BG2       = "#1a1f2e"
BG3       = "#222840"
ACCENT    = "#3b82f6"
ACHOVER   = "#2563eb"
SUCCESS   = "#10b981"
SUHOVER   = "#059669"
DANGER    = "#ef4444"
DAHOVER   = "#f0e748"
NEUTRAL   = "#2d3554"
NHOVER    = "#3b4470"
YELLOW    = "#facc15"
TEXT      = "#fcfeff"
TEXT2     = "#f5f576"
TEXT3     = "#fc6570"
BORDER    = "#2a3350"
ORANGE    = "#f97316"
ORHOVER   = "#ea580c"
PURPLE    = "#a855f7"
PURHOVER  = "#9333ea"

F_TITLE  = ("Segoe UI", 15, "bold")
F_LABEL  = ("Segoe UI", 10)
F_BOLD   = ("Segoe UI", 10, "bold")
F_SMALL  = ("Segoe UI", 9)
F_MONO   = ("Consolas", 10)
F_BIG    = ("Segoe UI", 42, "bold")
F_BTN    = ("Segoe UI", 10, "bold")


def sep(parent, pady=6):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill=tk.X, pady=pady)


def normalizar(txt: str) -> str:
    """Remove acentos, caixa e espaços extras para comparação robusta."""
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", txt).strip().lower()


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
        self._blink_job       = None
        self._blink_state     = False

        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    # UI PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = self.root

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        hdr = tk.Frame(root, bg=BG3)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text="●", fg=ACCENT, bg=BG3,
                 font=("Segoe UI", 16)).pack(side=tk.LEFT, padx=(14, 6), pady=10)
        tk.Label(hdr, text="Automação SEI", fg=TEXT, bg=BG3,
                 font=F_TITLE).pack(side=tk.LEFT)
        tk.Label(hdr, text="— Inclusão de Processos Vr05", fg=TEXT2, bg=BG3,
                 font=F_LABEL).pack(side=tk.LEFT, padx=(6, 0))

        # ── Notebook (abas) ───────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook",
                        background=BG, borderwidth=0, tabmargins=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG3, foreground=TEXT2,
                        padding=[16, 8], font=F_BOLD, borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", BG2)],
                  foreground=[("selected", TEXT)])

        self.notebook = ttk.Notebook(root, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # ── Aba 1: Automação ──────────────────────────────────────────────────
        tab_auto = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_auto, text="  ▶  Automação  ")
        self._build_tab_automacao(tab_auto)

        # ── Aba 2: Verificador ────────────────────────────────────────────────
        tab_ver = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab_ver, text="  🔍  Verificador  ")
        self._build_tab_verificador(tab_ver)

    # ─────────────────────────────────────────────────────────────────────────
    # ABA AUTOMAÇÃO (código original preservado)
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_automacao(self, parent):
        body = tk.Frame(parent, bg=BG, padx=14, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        right = tk.Frame(body, bg=BG, width=290)
        right.pack(side=tk.LEFT, fill=tk.Y)
        right.pack_propagate(False)

        # ── Esquerda ──────────────────────────────────────────────────────────
        lista_hdr = tk.Frame(left, bg=BG)
        lista_hdr.pack(fill=tk.X, pady=(0, 2))
        tk.Label(lista_hdr, text="LISTA DE PROCESSOS", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, anchor="w")
        self.btn_limpar = self._btn(lista_hdr, "🗑  Limpar", ORANGE, ORHOVER,
                                    self.limpar_lista)
        self.btn_limpar.pack(side=tk.RIGHT)

        tk.Label(left, text="Cole um processo por linha:", fg=TEXT2, bg=BG,
                 font=F_LABEL).pack(anchor="w", pady=(0, 4))

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
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 4))

        row1 = tk.Frame(left, bg=BG)
        row1.pack(fill=tk.X, pady=3)
        tk.Label(row1, text="Intervalo entre ações (segundos):", fg=TEXT2,
                 bg=BG, font=F_LABEL).pack(side=tk.LEFT)
        self.entry_tempo = tk.Entry(row1, width=5, bg=BG2, fg=TEXT,
                                    insertbackground=ACCENT, relief=tk.FLAT,
                                    font=F_MONO, highlightthickness=1,
                                    highlightbackground=BORDER)
        self.entry_tempo.insert(0, str(self.tempo_intervalo))
        self.entry_tempo.pack(side=tk.LEFT, padx=(8, 0))

        self.lbl_interval_cd = tk.Label(row1, text="", fg=YELLOW,
                                        bg=BG, font=("Segoe UI", 10, "bold"))
        self.lbl_interval_cd.pack(side=tk.LEFT, padx=(10, 0))

        row2 = tk.Frame(left, bg=BG)
        row2.pack(fill=tk.X, pady=3)
        tk.Label(row2, text="Retomar a partir do item nº:", fg=TEXT2,
                 bg=BG, font=F_LABEL).pack(side=tk.LEFT)
        self.entry_retomar = tk.Entry(row2, width=5, bg=BG2, fg=TEXT,
                                      insertbackground=ACCENT, relief=tk.FLAT,
                                      font=F_MONO, highlightthickness=1,
                                      highlightbackground=BORDER)
        self.entry_retomar.insert(0, "1")
        self.entry_retomar.pack(side=tk.LEFT, padx=(8, 0))
        tk.Label(row2, text="(use após pausar)", fg=TEXT3, bg=BG,
                 font=F_SMALL).pack(side=tk.LEFT, padx=(6, 0))

        sep(left)

        tk.Label(left, text="STATUS", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.lbl_status = tk.Label(left, text="Aguardando início…",
                                   fg=TEXT2, bg=BG, font=F_LABEL,
                                   anchor="w", wraplength=420, justify=tk.LEFT)
        self.lbl_status.pack(fill=tk.X, pady=(0, 6))

        prog_bg = tk.Frame(left, bg=BORDER, height=8)
        prog_bg.pack(fill=tk.X)
        self.prog_fill = tk.Frame(prog_bg, bg=ACCENT, height=8)
        self.prog_fill.place(relx=0, rely=0, relwidth=0, relheight=1)

        self.lbl_prog = tk.Label(left, text="0 / 0 processos",
                                 fg=TEXT3, bg=BG, font=F_SMALL)
        self.lbl_prog.pack(anchor="w", pady=(4, 0))

        # ── Direita ───────────────────────────────────────────────────────────
        tk.Label(right, text="FILA DE PROCESSOS", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 4))
        self.queue_frame = tk.Frame(right, bg=BG)
        self.queue_frame.pack(fill=tk.BOTH, expand=True)

        sep(right)

        tk.Label(right, text="PRÓXIMO ITEM EM", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.lbl_countdown = tk.Label(right, text="—", fg=YELLOW,
                                      bg=BG, font=F_BIG)
        self.lbl_countdown.pack()

        # ── Rodapé: botões ────────────────────────────────────────────────────
        footer = tk.Frame(self.root, bg=BG3, pady=10)
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

    # ─────────────────────────────────────────────────────────────────────────
    # ABA VERIFICADOR
    # ─────────────────────────────────────────────────────────────────────────

    def _build_tab_verificador(self, parent):
        """Constrói a aba de verificação de itens na página do SEI."""

        body = tk.Frame(parent, bg=BG, padx=14, pady=10)
        body.pack(fill=tk.BOTH, expand=True)

        # ── Painel esquerdo: controles ─────────────────────────────────────────
        left = tk.Frame(body, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # ── Painel direito: resultados ─────────────────────────────────────────
        right = tk.Frame(body, bg=BG, width=310)
        right.pack(side=tk.LEFT, fill=tk.Y)
        right.pack_propagate(False)

        # ── Instruções ────────────────────────────────────────────────────────
        tk.Label(left, text="VERIFICAÇÃO DE ITENS NA PÁGINA DO SEI",
                 fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))

        info_frame = tk.Frame(left, bg=BG2,
                              highlightthickness=1, highlightbackground=BORDER)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        info_txt = (
            "1. Abra a página do SEI no navegador com os processos visíveis.\n"
            "2. Clique em  \"📋 Capturar página\"  — o programa vai selecionar\n"
            "   tudo (Ctrl+A → Ctrl+C) na janela ativa e ler o conteúdo.\n"
            "3. Ou cole manualmente o conteúdo da página na caixa abaixo.\n"
            "4. Clique em  \"🔍 Verificar\"  para comparar com a lista de processos."
        )
        tk.Label(info_frame, text=info_txt, fg=TEXT2, bg=BG2,
                 font=F_SMALL, justify=tk.LEFT, padx=10, pady=8,
                 anchor="w").pack(fill=tk.X)

        sep(left, pady=4)

        # ── Botões de ação ────────────────────────────────────────────────────
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(fill=tk.X, pady=(0, 8))

        self.btn_capturar = self._btn(
            btn_row, "📋  Capturar página", PURPLE, PURHOVER,
            self._capturar_pagina_thread)
        self.btn_capturar.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_verificar = self._btn(
            btn_row, "🔍  Verificar", ACCENT, ACHOVER,
            self.verificar_itens)
        self.btn_verificar.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_limpar_ver = self._btn(
            btn_row, "🗑  Limpar", ORANGE, ORHOVER,
            self._limpar_verificador)
        self.btn_limpar_ver.pack(side=tk.LEFT)

        # Contador regressivo da captura
        self.lbl_captura_cd = tk.Label(btn_row, text="", fg=YELLOW,
                                       bg=BG, font=("Segoe UI", 10, "bold"))
        self.lbl_captura_cd.pack(side=tk.LEFT, padx=(12, 0))

        # ── Área de conteúdo da página ────────────────────────────────────────
        tk.Label(left, text="CONTEÚDO DA PÁGINA (capturado ou colado):",
                 fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 2))

        self.text_pagina = tk.Text(
            left, height=12, bg=BG2, fg=TEXT,
            insertbackground=ACCENT, relief=tk.FLAT,
            font=F_MONO, padx=8, pady=8,
            selectbackground=ACCENT, selectforeground=TEXT,
            highlightthickness=1, highlightbackground=BORDER,
            wrap=tk.WORD,
        )
        self.text_pagina.pack(fill=tk.BOTH, expand=True)

        self.lbl_ver_status = tk.Label(
            left, text="", fg=TEXT2, bg=BG,
            font=F_SMALL, anchor="w", wraplength=420)
        self.lbl_ver_status.pack(fill=tk.X, pady=(4, 0))

        # ── Painel de resultados (direita) ────────────────────────────────────
        tk.Label(right, text="RESULTADO DA VERIFICAÇÃO", fg=TEXT3, bg=BG,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 6))

        # Métricas
        met_frame = tk.Frame(right, bg=BG)
        met_frame.pack(fill=tk.X, pady=(0, 8))
        met_frame.columnconfigure((0, 1, 2), weight=1)

        self.lbl_m_total   = self._metric(met_frame, "Total",         TEXT,    0)
        self.lbl_m_found   = self._metric(met_frame, "Encontrados",   SUCCESS, 1)
        self.lbl_m_missing = self._metric(met_frame, "Não localizados", DANGER, 2)

        sep(right, pady=4)

        # Filtro de exibição
        filt_frame = tk.Frame(right, bg=BG)
        filt_frame.pack(fill=tk.X, pady=(0, 6))
        tk.Label(filt_frame, text="Exibir:", fg=TEXT3, bg=BG,
                 font=F_SMALL).pack(side=tk.LEFT)

        self._ver_filter = tk.StringVar(value="todos")
        for txt, val in [("Todos", "todos"), ("Não localizados", "faltando"), ("Encontrados", "encontrados")]:
            rb = tk.Radiobutton(
                filt_frame, text=txt, variable=self._ver_filter, value=val,
                bg=BG, fg=TEXT2, selectcolor=BG2, activebackground=BG,
                activeforeground=TEXT, font=F_SMALL, cursor="hand2",
                command=self._render_resultados)
            rb.pack(side=tk.LEFT, padx=(6, 0))

        # Botão copiar não localizados
        self.btn_copiar_falt = self._btn(
            right, "📋  Copiar não localizados", NEUTRAL, NHOVER,
            self._copiar_nao_localizados)
        self.btn_copiar_falt.pack(fill=tk.X, pady=(0, 8))

        # Lista de resultados com scroll
        list_container = tk.Frame(right, bg=BG2,
                                  highlightthickness=1, highlightbackground=BORDER)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.result_canvas = tk.Canvas(list_container, bg=BG2,
                                       highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical",
                                 command=self.result_canvas.yview)
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.result_inner = tk.Frame(self.result_canvas, bg=BG2)
        self.result_canvas_window = self.result_canvas.create_window(
            (0, 0), window=self.result_inner, anchor="nw")

        self.result_inner.bind("<Configure>", self._on_result_configure)
        self.result_canvas.bind("<Configure>", self._on_canvas_configure)

        self._resultados = []
        self._render_resultados()

    def _metric(self, parent, label, color, col):
        frame = tk.Frame(parent, bg=BG3,
                         highlightthickness=1, highlightbackground=BORDER)
        frame.grid(row=0, column=col, padx=2, sticky="ew")
        val = tk.Label(frame, text="—", fg=color, bg=BG3,
                       font=("Segoe UI", 18, "bold"))
        val.pack(pady=(6, 0))
        tk.Label(frame, text=label, fg=TEXT3, bg=BG3,
                 font=("Segoe UI", 7)).pack(pady=(0, 6))
        return val

    def _on_result_configure(self, event):
        self.result_canvas.configure(
            scrollregion=self.result_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.result_canvas.itemconfig(
            self.result_canvas_window, width=event.width)

    # ── Lógica do Verificador ─────────────────────────────────────────────────

    def _capturar_pagina_thread(self):
        """Inicia a captura em thread separada com contagem regressiva."""
        self.btn_capturar.config(state=tk.DISABLED)
        self.lbl_ver_status.config(
            text="⏳ Mude para a janela do SEI agora! Capturando em 3 segundos…",
            fg=YELLOW)
        threading.Thread(target=self._capturar_pagina, daemon=True).start()

    def _capturar_pagina(self):
        """Aguarda 3 s, faz Ctrl+A + Ctrl+C e lê o clipboard."""
        for i in range(3, 0, -1):
            self.lbl_captura_cd.config(text=f"⏱ {i}s")
            time.sleep(1)
        self.lbl_captura_cd.config(text="")

        try:
            # Salva clipboard atual para restaurar depois
            clipboard_anterior = ""
            try:
                clipboard_anterior = pyperclip.paste()
            except Exception:
                pass

            # Seleciona tudo e copia
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.4)
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.6)

            conteudo = pyperclip.paste()

            if not conteudo or conteudo == clipboard_anterior:
                self.lbl_ver_status.config(
                    text="⚠ Nada capturado. Tente colar manualmente o conteúdo da página.",
                    fg=ORANGE)
                self.btn_capturar.config(state=tk.NORMAL)
                return

            # Insere na caixa de texto
            self.text_pagina.delete("1.0", tk.END)
            self.text_pagina.insert("1.0", conteudo)
            chars = len(conteudo)
            self.lbl_ver_status.config(
                text=f"✅ Captura concluída — {chars:,} caracteres recebidos. Clique em 'Verificar'.",
                fg=SUCCESS)

        except Exception as e:
            self.lbl_ver_status.config(
                text=f"Erro na captura: {e}", fg=DANGER)
        finally:
            self.btn_capturar.config(state=tk.NORMAL)

    def verificar_itens(self):
        """Compara a lista de processos com o conteúdo capturado da página."""
        # Pega lista da aba de automação
        dados_txt = self.text_area.get("1.0", tk.END).strip()
        itens = [d.strip() for d in dados_txt.splitlines() if d.strip()]

        if not itens:
            messagebox.showwarning(
                "Lista vazia",
                "Não há processos na lista.\n"
                "Vá à aba 'Automação' e cole os processos primeiro.")
            return

        conteudo = self.text_pagina.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning(
                "Página vazia",
                "Capture ou cole o conteúdo da página do SEI antes de verificar.")
            return

        conteudo_norm = normalizar(conteudo)

        self._resultados = []
        for item in itens:
            encontrado = normalizar(item) in conteudo_norm
            self._resultados.append({"item": item, "encontrado": encontrado})

        total   = len(self._resultados)
        found   = sum(1 for r in self._resultados if r["encontrado"])
        missing = total - found

        self.lbl_m_total.config(text=str(total))
        self.lbl_m_found.config(text=str(found))
        self.lbl_m_missing.config(text=str(missing))

        self._ver_filter.set("todos")
        self._render_resultados()

        resumo = (f"✅ Verificação concluída — {found} encontrado(s), "
                  f"{missing} não localizado(s) de {total} item(ns).")
        self.lbl_ver_status.config(
            text=resumo,
            fg=SUCCESS if missing == 0 else YELLOW)

    def _render_resultados(self):
        """Atualiza a lista de resultados conforme o filtro selecionado."""
        for w in self.result_inner.winfo_children():
            w.destroy()

        filtro = self._ver_filter.get()
        exibir = [
            r for r in self._resultados
            if filtro == "todos"
            or (filtro == "faltando"     and not r["encontrado"])
            or (filtro == "encontrados"  and r["encontrado"])
        ]

        if not exibir:
            tk.Label(self.result_inner,
                     text="(sem itens para exibir)",
                     fg=TEXT3, bg=BG2, font=F_SMALL,
                     pady=12).pack(anchor="w", padx=8)
            return

        for r in exibir:
            enc = r["encontrado"]
            row = tk.Frame(self.result_inner, bg=BG2)
            row.pack(fill=tk.X, padx=4, pady=1)

            # Indicador colorido
            dot_color = SUCCESS if enc else DANGER
            tk.Label(row, text="●", fg=dot_color, bg=BG2,
                     font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(4, 2))

            # Texto do item (truncado se longo)
            txt = r["item"]
            if len(txt) > 35:
                txt = txt[:34] + "…"
            tk.Label(row, text=txt, fg=TEXT if enc else TEXT3,
                     bg=BG2, font=F_SMALL, anchor="w").pack(
                         side=tk.LEFT, fill=tk.X, expand=True)

            # Badge de status
            badge_bg  = "#064e3b" if enc else "#450a0a"
            badge_fg  = SUCCESS   if enc else DANGER
            badge_txt = "✓ OK"    if enc else "✗ Não encontrado"
            lbl_badge = tk.Label(row, text=badge_txt,
                                 fg=badge_fg, bg=badge_bg,
                                 font=("Segoe UI", 7, "bold"),
                                 padx=5, pady=1)
            lbl_badge.pack(side=tk.RIGHT, padx=(0, 4), pady=2)

    def _copiar_nao_localizados(self):
        """Copia para o clipboard somente os itens não localizados."""
        faltando = [r["item"] for r in self._resultados if not r["encontrado"]]
        if not faltando:
            messagebox.showinfo("Copiar", "Nenhum item não localizado para copiar.")
            return
        try:
            pyperclip.copy("\n".join(faltando))
            self.lbl_ver_status.config(
                text=f"📋 {len(faltando)} item(ns) não localizado(s) copiado(s) para o clipboard.",
                fg=YELLOW)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar: {e}")

    def _limpar_verificador(self):
        if messagebox.askyesno("Confirmar", "Limpar conteúdo e resultados do verificador?"):
            self.text_pagina.delete("1.0", tk.END)
            self._resultados = []
            self.lbl_ver_status.config(text="")
            self.lbl_m_total.config(text="—")
            self.lbl_m_found.config(text="—")
            self.lbl_m_missing.config(text="—")
            self._render_resultados()

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS DE WIDGET
    # ─────────────────────────────────────────────────────────────────────────

    def _btn(self, parent, text, bg, hover, cmd, state=tk.NORMAL):
        b = tk.Button(parent, text=text, bg=bg, fg=TEXT,
                      activebackground=hover, activeforeground=TEXT,
                      relief=tk.FLAT, cursor="hand2",
                      font=F_BTN, padx=14, pady=8,
                      state=state, bd=0, command=cmd)
        b.bind("<Enter>", lambda e, w=b, h=hover: w.config(bg=h))
        b.bind("<Leave>", lambda e, w=b, c=bg:    w.config(bg=c))
        return b

    # ─────────────────────────────────────────────────────────────────────────
    # LÓGICA DE AUTOMAÇÃO (original preservada)
    # ─────────────────────────────────────────────────────────────────────────

    def limpar_lista(self):
        if messagebox.askyesno("Confirmar", "Deseja limpar toda a lista de processos?"):
            self.text_area.delete("1.0", tk.END)
            self.dados = []
            self.index_atual = 0
            self._update_queue()
            self._update_progress()
            self.lbl_status.config(text="Lista limpa. Cole novos processos para iniciar.")
            self._stop_blink()
            self.lbl_status.config(fg=TEXT2)

    def _update_queue(self):
        for w in self.queue_frame.winfo_children():
            w.destroy()
        if not self.dados:
            tk.Label(self.queue_frame, text="(sem itens)", fg=TEXT3,
                     bg=BG, font=F_SMALL).pack(anchor="w")
            return
        start = max(0, self.index_atual - 6)
        end   = min(len(self.dados), self.index_atual + 6)
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
                     font=F_BOLD, width=2).pack(side=tk.LEFT, padx=(4, 2))
            txt = self.dados[i]
            if len(txt) > 32: txt = txt[:31] + "…"
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

    def _run_interval_countdown(self, seconds):
        for i in range(seconds, 0, -1):
            if self._stop_flag or not self.is_running:
                self.lbl_interval_cd.config(text="")
                return
            self.lbl_interval_cd.config(text=f"⏱ {i}s")
            time.sleep(1)
        self.lbl_interval_cd.config(text="")

    def _play_completion_sound(self):
        try:
            for _ in range(3):
                winsound.Beep(1000, 200)
                time.sleep(0.1)
            winsound.Beep(1500, 500)
        except Exception:
            pass

    def _start_blink(self):
        self._blink_state = True
        self._do_blink()

    def _do_blink(self):
        if not self._blink_state:
            return
        current = self.lbl_status.cget("fg")
        next_color = SUCCESS if current != SUCCESS else BG
        self.lbl_status.config(fg=next_color)
        self._blink_job = self.root.after(500, self._do_blink)

    def _stop_blink(self):
        self._blink_state = False
        if self._blink_job:
            self.root.after_cancel(self._blink_job)
            self._blink_job = None

    def iniciar_automacao(self):
        try:
            int(self.entry_tempo.get())
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
        self._stop_blink()
        self.lbl_status.config(fg=TEXT2)
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
            intervalo = int(self.entry_tempo.get())
        except ValueError:
            intervalo = self.tempo_intervalo

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

                self._run_interval_countdown(intervalo)
                if self._stop_flag or not self.is_running:
                    break

                pyautogui.click(self.posicao_abrir)

                self._run_interval_countdown(intervalo)
                if self._stop_flag or not self.is_running:
                    break

                self.index_atual += 1
                self._update_progress()

                if self.index_atual < len(self.dados) and self.is_running:
                    self.lbl_status.config(text="Aguardando próximo item…")
                    if not self._run_countdown(3):
                        break

            if self.is_running:
                threading.Thread(target=self._play_completion_sound, daemon=True).start()
                self.lbl_status.config(
                    text="✅  TODOS OS PROCESSOS CONCLUÍDOS!", fg=SUCCESS)
                self._start_blink()
                self._finish()
        except Exception as e:
            self.lbl_status.config(text=f"Erro: {e}", fg=DANGER)
            self._finish()

    def _finish(self):
        self.is_running = False
        self.lbl_countdown.config(text="—")
        self.lbl_interval_cd.config(text="")
        self.btn_parar.config(state=tk.DISABLED)
        self.btn_iniciar.config(state=tk.NORMAL)
        self._update_queue()
        self._update_progress()

    def parar_automacao(self):
        self._stop_flag = True
        self.is_running = False
        self.lbl_countdown.config(text="—")
        self.lbl_interval_cd.config(text="")
        self._stop_blink()
        self.lbl_status.config(
            text=f"⏸  Pausado no item {self.index_atual + 1}. "
                 f"Use '↩ Retomar' ou ajuste o item e clique Retomar.",
            fg=TEXT2)
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


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=BG)
    w, h = 920, 640
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    AutomacaoSEIApp(root)
    root.mainloop()