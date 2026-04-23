"""
╔══════════════════════════════════════════════════════════════════╗
║      Mesclador de Comprovantes de Pagamento  v7.0                ║
║  - Se COMPROVANTE inexistente, nenhum arquivo é gerado           ║
║  - ISS/IRRF só buscados se comprovante foi localizado            ║
║  - Comentários e marcadores FIM em todas as seções               ║
╠══════════════════════════════════════════════════════════════════╣
║  pip install pypdf pdfplumber reportlab                          ║
╚══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os, json, re, unicodedata, threading, datetime

# ═══════════════════════════════════════════════════════════════════
#  IMPORTAÇÕES OPCIONAIS — cada biblioteca é testada individualmente
#  para permitir que o programa abra mesmo sem todas instaladas
# ═══════════════════════════════════════════════════════════════════
try:
    from pypdf import PdfReader, PdfWriter   # leitura e escrita de PDFs
    PYPDF_OK = True
except ImportError:
    PYPDF_OK = False

try:
    import pdfplumber                         # extração de tabelas em PDFs
    PDFPLUMBER_OK = True
except ImportError:
    PDFPLUMBER_OK = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    REPORTLAB_OK = True                       # geração do log em PDF
except ImportError:
    REPORTLAB_OK = False
# FIM IMPORTAÇÕES OPCIONAIS


# ═══════════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO PERSISTENTE
#  Salva/carrega as pastas padrão em arquivo JSON no perfil do usuário
# ═══════════════════════════════════════════════════════════════════
CFG_FILE = os.path.join(os.path.expanduser("~"), ".mesclador_v7.json")

def cfg_load():
    """Carrega configurações salvas; retorna {} se não existir."""
    try:
        with open(CFG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def cfg_save(d):
    """Mescla dict 'd' nas configurações existentes e salva."""
    try:
        c = cfg_load()
        c.update(d)
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(c, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
# FIM CONFIGURAÇÃO PERSISTENTE


# ═══════════════════════════════════════════════════════════════════
#  UTILITÁRIOS DE TEXTO
# ═══════════════════════════════════════════════════════════════════

def sem_acento(s):
    """Remove acentos e retorna string em maiúsculo sem espaços extras."""
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper().strip()

def empresa_curta(empresa):
    """
    Extrai o nome da empresa removendo o código entre parênteses.
    Ex: 'DF MEDICAL (704920)'    → 'DF MEDICAL'
        'INOVAMED 0002 (705095)' → 'INOVAMED 0002'
        'SAO BERNARDO (83)'      → 'SAO BERNARDO'
    """
    m = re.match(r"^(.*?)\s*\(", empresa)
    return m.group(1).strip() if m else empresa.strip()

def valor_zero(v):
    """Retorna True se o valor representa zero (não exige ISS/IRRF)."""
    return str(v).strip().replace(" ", "") in ("0,00", "0.00", "0", "", "-", "None", "nan")
# FIM UTILITÁRIOS DE TEXTO


# ═══════════════════════════════════════════════════════════════════
#  LEITURA DA TABELA NO PDF DE AUTORIZAÇÃO
#  Usa pdfplumber para detectar automaticamente as colunas pelo cabeçalho
# ═══════════════════════════════════════════════════════════════════

# Aliases normalizados para cada coluna esperada na tabela
_ALIAS = {
    "sei":     ["SEI", "NUMERO SEI", "NUM SEI", "Nº SEI", "N SEI"],
    "cotacao": ["COTACAO", "COT"],
    "empresa": ["EMPRESA", "FORNECEDOR", "RAZAO SOCIAL"],
    "danfe":   ["DANFE", "NF", "NFe", "NF-E", "NOTA FISCAL", "NUMERO NF"],
    "liquido": ["LIQUIDO", "LIQ", "VLR LIQUIDO", "VALOR LIQUIDO",
                "VALOR LIQ", "VLR LIQ", "VL LIQUIDO"],
    "iss":     ["ISS"],
    "ir":      ["IR", "IRRF"],
}

def _col_match(header, key):
    """Verifica se o cabeçalho corresponde a uma das chaves esperadas."""
    h = sem_acento(header)
    for a in _ALIAS[key]:
        if sem_acento(a) in h or h in sem_acento(a):
            return True
    return False

def ler_autorizacao_pdf(caminho):
    """
    Abre o PDF de Autorização, localiza a tabela pelo cabeçalho
    (linha que contenha 'SEI' e 'EMPRESA') e retorna lista de dicts:
    {sei, cotacao, empresa, danfe, liquido, iss, ir}
    - SEI: remove '-' e '/'
    - Cotação: apenas os dígitos antes da '/' (ex: '466/2025' → '466')
    """
    if not PDFPLUMBER_OK:
        raise ImportError("pdfplumber nao instalado: pip install pdfplumber")

    registros = []

    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            for tabela in (pagina.extract_tables() or []):
                if not tabela:
                    continue

                # Detecta linha de cabeçalho
                hrow = None
                col_map = {}
                for ri, row in enumerate(tabela):
                    vals = [sem_acento(str(c or "")) for c in row]
                    if any("SEI" in v for v in vals) and \
                       any("EMPRESA" in v or "FORNECEDOR" in v for v in vals):
                        hrow = ri
                        for ci, cell in enumerate(row):
                            for key in _ALIAS:
                                if key not in col_map and _col_match(str(cell or ""), key):
                                    col_map[key] = ci
                        break

                if hrow is None:
                    continue

                def gc(row, k):
                    """Obtém valor de uma coluna pelo nome da chave."""
                    i = col_map.get(k)
                    v = row[i] if (i is not None and i < len(row)) else None
                    return str(v).strip() if v is not None else ""

                for row in tabela[hrow + 1:]:
                    if not row or not any(row):
                        continue

                    # SEI: remove '-', '/' e espaços
                    sei = re.sub(r"[-/\s]", "", gc(row, "sei"))
                    if not sei:
                        continue

                    # Cotação: dígitos antes da '/'
                    cot_raw = gc(row, "cotacao")
                    m = re.search(r"(\d{1,3})\s*/", cot_raw)
                    cotacao = m.group(1).zfill(3) if m else re.sub(r"\D", "", cot_raw)[:3].zfill(3)

                    registros.append({
                        "sei":     sei,
                        "cotacao": cotacao,
                        "empresa": gc(row, "empresa"),
                        "danfe":   gc(row, "danfe"),
                        "liquido": gc(row, "liquido"),
                        "iss":     gc(row, "iss"),
                        "ir":      gc(row, "ir"),
                    })

    return registros
# FIM LEITURA DA TABELA NO PDF DE AUTORIZAÇÃO


# ═══════════════════════════════════════════════════════════════════
#  BUSCA DE PÁGINAS NO PDF DE COMPROVANTES
# ═══════════════════════════════════════════════════════════════════

def _txt(reader, idx):
    """Extrai texto de uma página do PDF com segurança."""
    try:
        return reader.pages[idx].extract_text() or ""
    except Exception:
        return ""

def paginas_comprovante(pdf_path, liquido, danfe):
    """
    Localiza páginas no PDF de comprovantes que contenham
    simultaneamente o valor líquido E a referência NF+danfe.
    Aceita variações de formatação (pontos, espaços, zeros à esquerda).
    """
    reader = PdfReader(pdf_path)
    danfe_limpo = danfe.lstrip("0")
    resultado = []

    for i in range(len(reader.pages)):
        txt = _txt(reader, i)

        # Busca valor líquido (com ou sem separadores de milhar)
        liq_flat = re.sub(r"[\s.]", "", liquido).replace(",", "")
        tem_liq = (liquido in txt or
                   liq_flat in re.sub(r"[.\s]", "", txt).replace(",", ""))

        # Busca NF+danfe em várias formatações possíveis
        padroes_nf = [
            rf"NF[\s\-\.]*0*{re.escape(danfe)}",
            rf"NF[\s\-\.]*0*{re.escape(danfe_limpo)}",
            rf"N\.F\.[\s\-\.]*0*{re.escape(danfe)}",
        ]
        tem_nf = any(re.search(p, txt, re.IGNORECASE) for p in padroes_nf)

        if tem_liq and tem_nf:
            resultado.append(i)

    return resultado
# FIM paginas_comprovante

def paginas_keyword(pdf_path, kw):
    """
    Retorna índices de páginas que contenham a palavra-chave (ex: 'ISS', 'IRRF').
    Busca é case-insensitive.
    """
    reader = PdfReader(pdf_path)
    return [i for i in range(len(reader.pages))
            if kw.upper() in (_txt(reader, i)).upper()]
# FIM paginas_keyword

# FIM BUSCA DE PÁGINAS NO PDF DE COMPROVANTES


# ═══════════════════════════════════════════════════════════════════
#  BUSCA DE CERTIDÕES
#  Localiza a subpasta da empresa dentro da pasta de certidões,
#  tolerando diferenças de acentuação e sufixos numéricos.
# ═══════════════════════════════════════════════════════════════════

def arquivos_certidoes(pasta_cert, empresa, log_fn=None):
    """
    Busca PDFs dentro da subpasta correspondente à empresa.
    Usa comparação normalizada (sem acento, maiúsculo) com 4 níveis:
      100 = nome exato
       80 = pasta começa com nome da empresa
       70 = nome da empresa começa com nome da pasta
       50 = um está contido no outro
    Retorna lista de caminhos completos dos PDFs encontrados.
    """
    ec = empresa_curta(empresa)
    ec_norm = sem_acento(ec)

    # Lista itens da pasta preservando nomes reais (com acentos)
    try:
        itens = [(item, sem_acento(item))
                 for item in os.listdir(pasta_cert)
                 if os.path.isdir(os.path.join(pasta_cert, item))]
    except Exception:
        return []

    candidatos = []
    for nome_real, nome_norm in itens:
        score = 0
        if nome_norm == ec_norm:
            score = 100                                         # exato
        elif nome_norm.startswith(ec_norm):
            score = 80                                          # pasta começa com empresa
        elif ec_norm.startswith(nome_norm) and len(nome_norm) >= 3:
            score = 70                                          # empresa começa com pasta
        elif ec_norm in nome_norm or (len(nome_norm) >= 4 and nome_norm in ec_norm):
            score = 50                                          # contido

        if score > 0:
            candidatos.append((score, nome_real, os.path.join(pasta_cert, nome_real)))

    if not candidatos:
        # Emite debug mostrando as pastas disponíveis para diagnóstico
        if log_fn:
            nomes_disp = [n for n, _ in itens[:10]]
            log_fn(f"[DEBUG certidoes] '{ec_norm}' sem match. Pastas: {nomes_disp}")
        return []

    # Usa o candidato de maior score
    candidatos.sort(key=lambda x: -x[0])
    melhor_score, melhor_nome, melhor_path = candidatos[0]

    if log_fn:
        log_fn(f"[DEBUG certidoes] match '{melhor_nome}' (score={melhor_score})")

    return [os.path.join(melhor_path, f)
            for f in sorted(os.listdir(melhor_path))
            if f.lower().endswith(".pdf")]
# FIM BUSCA DE CERTIDÕES


# ═══════════════════════════════════════════════════════════════════
#  MESCLAGEM DE PDFs
# ═══════════════════════════════════════════════════════════════════

def mesclar_pdf(paginas, saida):
    """
    Mescla páginas de múltiplos PDFs em um único arquivo de saída.
    paginas: lista de tuplas (caminho_pdf, indice_pagina)
      - indice_pagina = número (0-based): inclui só aquela página
      - indice_pagina = -1: inclui o arquivo completo
    """
    writer = PdfWriter()
    for caminho, idx in paginas:
        reader = PdfReader(caminho)
        if idx == -1:
            for page in reader.pages:
                writer.add_page(page)
        else:
            writer.add_page(reader.pages[idx])
    with open(saida, "wb") as f:
        writer.write(f)
# FIM MESCLAGEM DE PDFs


# ═══════════════════════════════════════════════════════════════════
#  EXPORTAÇÃO DO LOG PARA PDF
# ═══════════════════════════════════════════════════════════════════

def exportar_log_pdf(texto, caminho):
    """Converte o conteúdo do log (texto simples) em arquivo PDF via reportlab."""
    if not REPORTLAB_OK:
        raise ImportError("reportlab nao instalado: pip install reportlab")
    doc = SimpleDocTemplate(caminho, pagesize=A4,
                            leftMargin=40, rightMargin=40,
                            topMargin=40, bottomMargin=40)
    sty = ParagraphStyle("m", fontName="Courier", fontSize=8,
                         textColor=colors.black, leading=11)
    def esc(t):
        return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    story = [Paragraph(esc(l) or "&nbsp;", sty) for l in texto.split("\n")]
    doc.build(story)
# FIM EXPORTAÇÃO DO LOG PARA PDF


# ═══════════════════════════════════════════════════════════════════
#  INTERFACE GRÁFICA
#  Usa COMPOSIÇÃO (self.root = tk.Tk()) em vez de herança (class App(tk.Tk))
#  para evitar o RecursionError do Python 3.11+
# ═══════════════════════════════════════════════════════════════════

# Paleta de cores da interface escura
BG      = "#181818"   # fundo principal
BG2     = "#212121"   # fundo do painel de campos
BG3     = "#2a2a2a"   # fundo dos campos de entrada
FG      = "#e8e8e8"   # texto principal
FG2     = "#777777"   # texto secundário / botões auxiliares
ACCENT  = "#4da3ff"   # azul de destaque (botão principal, highlight)
ACTHOV  = "#1a6fbe"   # azul escuro (hover do botão principal)
CLR_OK  = "#4ddb6e"   # verde (OK)
CLR_ERR = "#ff5f5f"   # vermelho (ERR)
CLR_WRN = "#ffd050"   # amarelo (AVS)
CLR_INF = "#75caff"   # azul claro (INF)
#CLR_SEP = "#444444"   # cinza (separadores)
CLR_SEP = "#888888"   # cinza (separadores)
CLR_DBG = "#888888"   # cinza médio (DEBUG)
BORDER  = "#353535"   # borda dos campos

# Fontes — tamanhos reduzidos para caber em 1280×800
FT  = ("Segoe UI", 15, "bold")   # título
FL  = ("Segoe UI", 11)            # label dos campos
FE  = ("Segoe UI", 11)            # texto dos campos de entrada
FB  = ("Segoe UI", 12, "bold")    # botão INICIAR
FS  = ("Segoe UI", 10)            # botões pequenos e rodapé
FLG = ("Consolas", 10)            # log de execução


class App:
    """
    Classe principal da aplicação.
    Gerencia a interface gráfica e dispara o processamento em thread separada.
    """

    def __init__(self):
        """Cria a janela principal e constrói todos os widgets."""
        self.root = tk.Tk()
        self.root.title("Mesclador de Comprovantes de Pagamento  v7.0")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 700)
        self.root.configure(bg=BG)
        self._build(cfg_load())   # monta UI com configurações salvas
        self._avisos_deps()       # avisa sobre bibliotecas faltando

    def mainloop(self):
        """Inicia o loop de eventos do tkinter."""
        self.root.mainloop()

    # ═══════════════════════════════════════════════════════════════
    #  BUILD DA INTERFACE
    # ═══════════════════════════════════════════════════════════════
    def _build(self, cfg):
        """Constrói todos os widgets da janela principal."""
        root = self.root

        # Título da aplicação
        tk.Label(root, text="Mesclador de Comprovantes de Pagamento",
                 bg=BG, fg=ACCENT, font=FT).pack(pady=(10, 4))
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=16)
        # FIM Título

        # Painel de campos de entrada
        pnl = tk.Frame(root, bg=BG2)
        pnl.pack(fill="x", padx=16, pady=6)

        # Campo 1 – Data
        r1 = self._row(pnl)
        self._label(r1, "Pasta data  (AAAA-MM-DD):", 32)
        self.v_data = tk.StringVar(
            value=datetime.date.today().strftime("%Y-%m-%d"))
        self._entry(r1, self.v_data, w=14).pack(side="left", ipady=5, padx=(0, 6))
        # FIM Campo 1 – Data

        # Campo 2 – Comprovantes
        r2 = self._row(pnl)
        self._label(r2, "Pasta comprovantes de pagamento:", 32)
        self.v_comp = tk.StringVar(
            value=cfg.get("pasta_comp",
                          r"G:\Meu Drive\Pagamentos\Comprovantes de pagamento"))
        self._entry(r2, self.v_comp).pack(
            side="left", fill="x", expand=True, ipady=5, padx=(0, 4))
        self._btnpasta(r2, self.v_comp)
        # FIM Campo 2 – Comprovantes

        # Campo 2.1 – Certidões (valor EXATO com acentos preservados)
        r3 = self._row(pnl)
        self._label(r3, "Pasta certidoes para pagamento:", 32)
        self.v_cert = tk.StringVar(
            value=cfg.get("pasta_cert",
                          r"G:\Meu Drive\Pagamentos\Certidões para pagamento"))
        self._entry(r3, self.v_cert).pack(
            side="left", fill="x", expand=True, ipady=5, padx=(0, 4))
        self._btnpasta(r3, self.v_cert)
        # FIM Campo 2.1 – Certidões

        # Botão salvar padrão
        fc = tk.Frame(root, bg=BG)
        fc.pack(fill="x", padx=20, pady=(2, 2))
        self._btn(fc, "Salvar como padrao", self._salvar_cfg,
                  bg=BG3, fg=FG2).pack(side="left")
        # FIM Botão salvar padrão

        # Botão principal INICIAR MESCLAGEM
        self.btn = tk.Button(
            root, text="INICIAR MESCLAGEM",
            command=self._iniciar,
            bg=ACCENT, fg="#000000", font=FB, relief="flat",
            cursor="hand2", activebackground=ACTHOV,
            activeforeground="#ffffff", padx=36, pady=8)
        self.btn.pack(pady=4)
        # FIM Botão principal INICIAR MESCLAGEM

        # Barra de progresso animada
        sty = ttk.Style(root)
        sty.theme_use("clam")
        sty.configure("P.Horizontal.TProgressbar",
                      troughcolor=BG3, background=ACCENT, thickness=8)
        self.pb = ttk.Progressbar(root, mode="indeterminate", length=460,
                                  style="P.Horizontal.TProgressbar")
        self.pb.pack(pady=(2, 2))
        # FIM Barra de progresso animada

        # Separador visual
        tk.Frame(root, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(2, 0))

        # Label do log
        tk.Label(root, text="Log de execucao:", bg=BG, fg=FG,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=20, pady=(3, 1))

        # Área de log com scroll
        self.log = scrolledtext.ScrolledText(
            root, bg="#0c0c0c", fg=FG, font=FLG,
            state="disabled", relief="flat", wrap="word",
            selectbackground=ACCENT)
        self.log.pack(fill="both", expand=True, padx=16)

        # Tags de cor para cada tipo de mensagem
        for tag, cor in [("ok",  CLR_OK), ("err", CLR_ERR),
                         ("wrn", CLR_WRN), ("inf", CLR_INF),
                         ("sep", CLR_SEP), ("dbg", CLR_DBG)]:
            self.log.tag_config(tag, foreground=cor)
        # FIM Área de log com scroll

        # Rodapé com botões de exportação
        rd = tk.Frame(root, bg=BG)
        rd.pack(fill="x", padx=16, pady=5)
        self._btn(rd, "Salvar Log TXT",
                  lambda: self._export_log("txt")).pack(side="left", padx=(0, 6))
        self._btn(rd, "Salvar Log PDF",
                  lambda: self._export_log("pdf")).pack(side="left", padx=(0, 6))
        self._btn(rd, "Limpar Log", self._clear_log,
                  bg="#3a1818", fg=CLR_ERR).pack(side="right")
        # FIM Rodapé com botões de exportação

    # FIM BUILD DA INTERFACE

    # ═══════════════════════════════════════════════════════════════
    #  HELPERS DE WIDGETS
    # ═══════════════════════════════════════════════════════════════

    def _row(self, p):
        """Cria e retorna um frame de linha no painel de campos."""
        f = tk.Frame(p, bg=BG2)
        f.pack(fill="x", padx=10, pady=4)
        return f

    def _label(self, p, txt, w=None):
        """Adiciona um label com largura opcional ao frame pai."""
        kw = dict(bg=BG2, fg=FG, font=FL, anchor="w")
        if w: kw["width"] = w
        tk.Label(p, text=txt, **kw).pack(side="left")

    def _entry(self, p, var, w=None):
        """Cria e retorna um campo de entrada estilizado."""
        kw = dict(textvariable=var, bg=BG3, fg=FG, font=FE,
                  insertbackground=FG, relief="flat",
                  highlightthickness=1,
                  highlightbackground=BORDER,
                  highlightcolor=ACCENT)
        if w: kw["width"] = w
        return tk.Entry(p, **kw)

    def _btnpasta(self, p, var):
        """Adiciona botão 'Pasta...' que abre o seletor de diretório."""
        def pick():
            d = filedialog.askdirectory(parent=self.root)
            if d: var.set(d)
        tk.Button(p, text="Pasta...", command=pick,
                  bg=BG3, fg=FG, font=FS, relief="flat", cursor="hand2",
                  activebackground=ACCENT, activeforeground="#000",
                  padx=7, pady=2).pack(side="left")

    def _btn(self, p, txt, cmd, bg=BG3, fg=FG):
        """Cria e retorna um botão pequeno padronizado."""
        return tk.Button(p, text=txt, command=cmd,
                         bg=bg, fg=fg, font=FS, relief="flat",
                         cursor="hand2", activebackground=ACCENT,
                         activeforeground="#000", padx=10, pady=4)

    # FIM HELPERS DE WIDGETS

    # ═══════════════════════════════════════════════════════════════
    #  VERIFICAÇÃO DE DEPENDÊNCIAS
    # ═══════════════════════════════════════════════════════════════

    def _avisos_deps(self):
        """Exibe aviso no log se alguma biblioteca obrigatória não estiver instalada."""
        miss = [lib for lib, ok in [("pypdf",      PYPDF_OK),
                                     ("pdfplumber", PDFPLUMBER_OK),
                                     ("reportlab",  REPORTLAB_OK)]
                if not ok]
        if miss:
            self._w("DEPENDENCIAS FALTANDO — execute no terminal:", "wrn")
            self._w(f"  pip install {' '.join(miss)}", "wrn")

    # FIM VERIFICAÇÃO DE DEPENDÊNCIAS

    # ═══════════════════════════════════════════════════════════════
    #  HELPERS DO LOG
    # ═══════════════════════════════════════════════════════════════

    def _w(self, msg, tag=""):
        """
        Escreve uma linha no log com timestamp.
        Usa root.after() para ser thread-safe.
        """
        def _do():
            self.log.config(state="normal")
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self.log.insert("end", f"[{ts}] {msg}\n", tag)
            self.log.see("end")
            self.log.config(state="disabled")
        self.root.after(0, _do)

    def lok(self, m):  self._w("OK   " + m, "ok")    # sucesso (verde)
    def lerr(self, m): self._w("ERR  " + m, "err")   # erro (vermelho)
    def lwrn(self, m): self._w("AVS  " + m, "wrn")   # aviso (amarelo)
    def linf(self, m): self._w("INF  " + m, "inf")   # informação (azul claro)
    def ldbg(self, m): self._w("DBG  " + m, "dbg")   # debug (cinza)
    def lsep(self, m=""): self._w(("─" * 60) + ("  " + m if m else ""), "sep")

    def _clear_log(self):
        """Limpa todo o conteúdo da área de log."""
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _export_log(self, fmt):
        """Exporta o conteúdo do log para TXT ou PDF conforme solicitado."""
        txt = self.log.get("1.0", "end")
        if fmt == "txt":
            p = filedialog.asksaveasfilename(
                parent=self.root, defaultextension=".txt",
                filetypes=[("Texto", "*.txt")],
                initialfile="log_mesclagem.txt")
            if p:
                with open(p, "w", encoding="utf-8") as f: f.write(txt)
                messagebox.showinfo("Log salvo", f"Salvo em:\n{p}", parent=self.root)
        else:
            p = filedialog.asksaveasfilename(
                parent=self.root, defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile="log_mesclagem.pdf")
            if p:
                try:
                    exportar_log_pdf(txt, p)
                    messagebox.showinfo("Log salvo", f"PDF salvo em:\n{p}", parent=self.root)
                except Exception as ex:
                    messagebox.showerror("Erro", str(ex), parent=self.root)

    # FIM HELPERS DO LOG

    # ═══════════════════════════════════════════════════════════════
    #  SALVAR CONFIGURAÇÃO PADRÃO
    # ═══════════════════════════════════════════════════════════════

    def _salvar_cfg(self):
        """Persiste os valores atuais dos campos de pasta como padrão."""
        cfg_save({"pasta_comp": self.v_comp.get(),
                  "pasta_cert": self.v_cert.get()})
        messagebox.showinfo("Configuracoes", "Padroes salvos!", parent=self.root)

    # FIM SALVAR CONFIGURAÇÃO PADRÃO

    # ═══════════════════════════════════════════════════════════════
    #  DISPARO DO PROCESSAMENTO EM THREAD SEPARADA
    # ═══════════════════════════════════════════════════════════════

    def _iniciar(self):
        """Valida dependências e dispara o processamento em thread separada."""
        if not PYPDF_OK or not PDFPLUMBER_OK:
            messagebox.showerror(
                "Dependencias faltando",
                "Instale:\n  pip install pypdf pdfplumber reportlab",
                parent=self.root)
            return
        self.btn.config(state="disabled", text="Processando...")
        self.pb.start(8)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        """Wrapper que chama _processar e restaura o botão ao finalizar."""
        try:
            self._processar()
        except Exception as ex:
            self.lerr(f"Erro inesperado: {ex}")
            import traceback; traceback.print_exc()
        finally:
            self.pb.stop()
            self.root.after(0, lambda: self.btn.config(
                state="normal", text="INICIAR MESCLAGEM"))

    # FIM DISPARO DO PROCESSAMENTO

    # ═══════════════════════════════════════════════════════════════
    #  LÓGICA PRINCIPAL DE PROCESSAMENTO
    # ═══════════════════════════════════════════════════════════════

    def _processar(self):
        """
        Fluxo completo de processamento:
        1. Valida campos e monta caminhos
        2. Localiza PDFs de Autorização
        3. Para cada Autorização: lê tabela, localiza COMPROVANTES
        4. Para cada registro: busca comprovante, ISS, IRRF, certidões
        5. SE comprovante OK: prossegue com ISS/IRRF/certidões
           SE comprovante INEXISTENTE: bloqueia TUDO para aquele registro
        6. Mescla na ordem: Autorização + Comprovante + ISS + IRRF + Certidões
        7. Gera relatório final de erros
        """
        data      = self.v_data.get().strip()
        base_comp = self.v_comp.get().strip()
        base_cert = self.v_cert.get().strip()   # preserva acentos do campo

        # Validações básicas dos campos
        if not data:
            self.lerr("Informe a pasta data (ex: 2026-01-20)"); return
        if not base_comp:
            self.lerr("Informe a pasta de comprovantes."); return
        if not base_cert:
            self.lerr("Informe a pasta de certidoes."); return
        # FIM Validações básicas

        # Monta caminhos usando valores EXATOS dos campos (acentos preservados)
        pasta_comp      = os.path.join(base_comp, data)
        pasta_cert      = os.path.join(base_cert, data)
        pasta_mesclados = os.path.join(pasta_comp, "Mesclados")

        self.linf(f"Comprovantes : {pasta_comp}")
        self.linf(f"Certidoes    : {pasta_cert}")
        self.linf(f"Mesclados    : {pasta_mesclados}")
        # FIM Monta caminhos

        # Diagnóstico da pasta de certidões
        if os.path.isdir(pasta_cert):
            itens_cert = os.listdir(pasta_cert)
            self.lok(f"Pasta certidoes OK: {len(itens_cert)} subpasta(s)")
            self.ldbg(f"Primeiras subpastas: {itens_cert[:6]}")
        else:
            parent = os.path.dirname(pasta_cert)
            self.lwrn(f"Pasta certidoes NAO encontrada: {pasta_cert}")
            if os.path.isdir(parent):
                self.ldbg(f"Sugestao — pastas em '{parent}': {os.listdir(parent)[:6]}")
        # FIM Diagnóstico da pasta de certidões

        # Verifica pasta de comprovantes
        if not os.path.isdir(pasta_comp):
            self.lerr(f"Pasta comprovantes nao existe: {pasta_comp}"); return

        os.makedirs(pasta_mesclados, exist_ok=True)
        self.lok("Pasta 'Mesclados' criada/verificada.")
        # FIM Verifica pasta de comprovantes

        # Passo 5 – localiza PDFs de Autorização na pasta
        arqs_aut = sorted([
            n for n in os.listdir(pasta_comp)
            if re.search(r"autorizacao", n, re.IGNORECASE)
            and n.lower().endswith(".pdf")
        ])
        if not arqs_aut:
            self.lerr("Nenhum PDF com 'Autorizacao' encontrado."); return
        self.linf(f"{len(arqs_aut)} arquivo(s) de Autorizacao encontrado(s).")
        # FIM Passo 5

        erros = []   # acumula ocorrências para o relatório final

        # Itera sobre cada arquivo de Autorização encontrado
        for nome_aut in arqs_aut:
            self.lsep(nome_aut)
            caminho_aut = os.path.join(pasta_comp, nome_aut)

            # Extrai prefixo do nome (tudo antes de 'Autorizacao')
            m = re.match(r"^(.*?)autorizacao", nome_aut, re.IGNORECASE)
            prefixo = m.group(1) if m else ""

            # Passo 6 – lê tabela do PDF de Autorização
            try:
                regs = ler_autorizacao_pdf(caminho_aut)
            except Exception as ex:
                self.lerr(f"Erro ao ler autorizacao: {ex}"); continue

            if not regs:
                self.lwrn("Nenhum registro lido — confira layout da tabela.")
                continue
            self.lok(f"{len(regs)} registro(s) lidos da autorizacao.")
            # FIM Passo 6

            # Passo 7 – localiza o PDF de COMPROVANTES correspondente
            arq_comp_pdf = None
            for n in os.listdir(pasta_comp):
                if (re.search(r"comprovantes", n, re.IGNORECASE)
                        and n.lower().endswith(".pdf")
                        and sem_acento(n).startswith(sem_acento(prefixo))):
                    arq_comp_pdf = os.path.join(pasta_comp, n)
                    break

            if not arq_comp_pdf:
                self.lerr(f"PDF COMPROVANTES nao encontrado (prefixo='{prefixo}')")
                for r in regs:
                    erros.append({"cotacao": r["cotacao"], "empresa": r["empresa"],
                                  "danfe": r["danfe"], "comp": "INEXISTENTE",
                                  "iss": "N/A", "irrf": "N/A", "cert": "N/A"})
                continue

            self.lok(f"Comprovantes: {os.path.basename(arq_comp_pdf)}")
            # FIM Passo 7

            # Processa cada registro (linha) da tabela de autorização
            for r in regs:
                sei     = r["sei"]
                cotacao = r["cotacao"]
                empresa = r["empresa"]
                danfe   = r["danfe"]
                liquido = r["liquido"]
                iss     = r["iss"]
                ir      = r["ir"]
                ec      = empresa_curta(empresa)

                # Define quais passos são obrigatórios para este registro
                precisa_iss  = not valor_zero(iss)
                precisa_irrf = not valor_zero(ir)

                self.lsep()
                self.linf(
                    f"SEI:{sei} | Cot:{cotacao} | {ec} | "
                    f"DANFE:{danfe} | Liq:{liquido} | "
                    f"ISS:{iss}({'obrig' if precisa_iss else 'N/A'}) | "
                    f"IR:{ir}({'obrig' if precisa_irrf else 'N/A'})")

                # Status inicial: OK ou N/A conforme obrigatoriedade
                status = {
                    "comp": "OK",
                    "iss":  "N/A" if not precisa_iss  else "OK",
                    "irrf": "N/A" if not precisa_irrf else "OK",
                    "cert": "OK",
                }

                # ── Passo 8 – busca página do COMPROVANTE ────────
                pags_comp = []
                try:
                    pags_comp = [(arq_comp_pdf, i)
                                 for i in paginas_comprovante(arq_comp_pdf, liquido, danfe)]
                except Exception as ex:
                    self.lerr(f"Passo 8: {ex}")

                if pags_comp:
                    self.lok(f"Passo 8 - Comprovante: {len(pags_comp)} pag(s)")
                else:
                    status["comp"] = "INEXISTENTE"
                    self.lwrn("Passo 8 - Comprovante INEXISTENTE")
                # FIM Passo 8

                # ── REGRA PRINCIPAL: se Comprovante não localizado,
                #    interrompe TODOS os passos seguintes para este registro
                #    e NÃO gera nenhum arquivo ────────────────────────────
                if status["comp"] == "INEXISTENTE":
                    erros.append({"cotacao": cotacao, "empresa": empresa,
                                  "danfe": danfe, **status})
                    self.lerr("MESCLAGEM BLOQUEADA — Comprovante e todos os "
                              "demais passos cancelados para este registro.")
                    continue   # vai para o próximo registro sem processar ISS/IRRF/certidões
                # FIM REGRA PRINCIPAL

                # ── Passo 9 – busca página ISS (só se obrigatório) ───
                pags_iss = []
                if precisa_iss:
                    try:
                        pags_iss = [(arq_comp_pdf, i)
                                    for i in paginas_keyword(arq_comp_pdf, "ISS")]
                    except Exception as ex:
                        self.lerr(f"Passo 9: {ex}")
                    if pags_iss:
                        self.lok(f"Passo 9 - ISS: {len(pags_iss)} pag(s)")
                    else:
                        status["iss"] = "INEXISTENTE"
                        self.lwrn("Passo 9 - ISS INEXISTENTE")
                # FIM Passo 9

                # ── Passo 10 – busca página IRRF (só se obrigatório) ─
                pags_irrf = []
                if precisa_irrf:
                    try:
                        pags_irrf = [(arq_comp_pdf, i)
                                     for i in paginas_keyword(arq_comp_pdf, "IRRF")]
                    except Exception as ex:
                        self.lerr(f"Passo 10: {ex}")
                    if pags_irrf:
                        self.lok(f"Passo 10 - IRRF: {len(pags_irrf)} pag(s)")
                    else:
                        status["irrf"] = "INEXISTENTE"
                        self.lwrn("Passo 10 - IRRF INEXISTENTE")
                # FIM Passo 10

                # ── Passo 11 – busca certidões da empresa ────────────
                pags_cert = []
                if os.path.isdir(pasta_cert):
                    certs = arquivos_certidoes(pasta_cert, empresa, log_fn=self.ldbg)
                    if certs:
                        pags_cert = [(c, -1) for c in certs]
                        self.lok(f"Passo 11 - Certidoes: {len(certs)} arq(s) [{ec}]")
                    else:
                        status["cert"] = "INEXISTENTE"
                        self.lwrn(f"Passo 11 - Certidoes INEXISTENTE para '{ec}'")
                else:
                    status["cert"] = "INEXISTENTE"
                    self.lwrn(f"Passo 11 - Pasta certidoes nao existe")
                # FIM Passo 11

                # Verifica se ainda há algum INEXISTENTE (ISS, IRRF ou certidões)
                itens_inexistentes = [k for k, v in status.items() if v == "INEXISTENTE"]
                if itens_inexistentes:
                    erros.append({"cotacao": cotacao, "empresa": empresa,
                                  "danfe": danfe, **status})
                    self.lerr(
                        f"MESCLAGEM BLOQUEADA — item(ns) incompleto(s): "
                        f"{', '.join(itens_inexistentes).upper()}")
                    continue   # NÃO gera arquivo
                # FIM Verificação de inexistentes

                # ── Mesclagem na ordem correta ────────────────────────
                # Autorização (completo) + Comprovante + ISS + IRRF + Certidões
                todas_pags = ([(caminho_aut, -1)]   # Autorização completa
                              + pags_comp            # página(s) do comprovante
                              + pags_iss             # página ISS (se aplicável)
                              + pags_irrf            # página IRRF (se aplicável)
                              + pags_cert)           # certidões (arquivos completos)

                nome_out = re.sub(
                    r'[\\/*?:"<>|]', "_",
                    f"PAGAMENTO {cotacao} {ec} {danfe} {sei}.pdf")
                saida = os.path.join(pasta_mesclados, nome_out)

                try:
                    mesclar_pdf(todas_pags, saida)
                    self.lok(f"SALVO: {nome_out}")
                except Exception as ex:
                    self.lerr(f"Erro ao mesclar: {ex}")
                # FIM Mesclagem

            # FIM loop registros

        # FIM loop arquivos de Autorização

        # ── Relatório final de erros ──────────────────────────────
        self.lsep()
        self._w("=" * 64, "sep")
        if erros:
            self.lerr(f"RELATORIO DE ERROS  —  {len(erros)} ocorrencia(s):")
            self._w("=" * 64, "sep")
            for e in erros:
                self.lerr(
                    f"COTACAO {e['cotacao']}, {e['empresa']}, "
                    f"DANFE {e['danfe']}, "
                    f"COMPROVANTE {e['comp']}, "
                    f"ISS {e['iss']}, "
                    f"IRRF {e['irrf']}, "
                    f"CERTIDOES {e['cert']}"
                )
        else:
            self.lok("PROCESSAMENTO CONCLUIDO SEM ERROS")
        self._w("=" * 64, "sep")
        # FIM Relatório final de erros

    # FIM LÓGICA PRINCIPAL DE PROCESSAMENTO

# FIM INTERFACE GRÁFICA


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    miss = [lib for lib, ok in [("pypdf",      PYPDF_OK),
                                  ("pdfplumber", PDFPLUMBER_OK),
                                  ("reportlab",  REPORTLAB_OK)] if not ok]
    if miss:
        print("ATENCAO: Dependencias faltando. Execute:")
        print(f"  pip install {' '.join(miss)}\n")
    App().mainloop()
# FIM ENTRY POINT