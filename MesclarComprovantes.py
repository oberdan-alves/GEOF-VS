#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Mesclagem de Comprovantes de Pagamento
Versão 2.0 - Reconstruído do zero
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re
import json
from datetime import datetime
import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet
import unicodedata


class MescladorPagamentos:
    def __init__(self, root):
        self.root = root
        self.root.title("Mesclador de Comprovantes de Pagamento v2.0")
        self.root.geometry("1400x900")
        
        
        # Configurar tema escuro
        self.configurar_tema_escuro()
        
        # Arquivo de configuração
        self.config_file = "config_mesclador.json"
        self.log_messages = []
        
        # Carregar configurações
        self.carregar_config()
        
        # Criar interface
        self.criar_interface()
        
    def configurar_tema_escuro(self):
        """Configura cores do tema escuro"""
        # Cores
        self.bg_dark = "#1e1e1e"
        self.bg_medium = "#252526"
        self.bg_light = "#2d2d30"
        self.fg_color = "#cccccc"
        self.fg_bright = "#ffffff"
        self.accent_color = "#0e639c"
        self.success_color = "#4ec9b0"
        self.warning_color = "#ce9178"
        self.error_color = "#f48771"
        
        # Configurar janela principal
        self.root.configure(bg=self.bg_dark)
        
        # Configurar estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores dos widgets
        style.configure('Dark.TFrame', background=self.bg_dark)
        style.configure('Dark.TLabel', background=self.bg_dark, foreground=self.fg_color, font=('Segoe UI', 12))
        style.configure('Dark.TButton', background=self.accent_color, foreground=self.fg_bright, 
                       font=('Segoe UI', 12, 'bold'), borderwidth=0)
        style.map('Dark.TButton', background=[('active', '#1177bb')])
        
    def carregar_config(self):
        """Carrega configurações salvas"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.pasta_comprovantes = config.get('pasta_comprovantes', '')
                    self.pasta_certidoes = config.get('pasta_certidoes', '')
            except:
                self.pasta_comprovantes = ''
                self.pasta_certidoes = ''
        else:
            self.pasta_comprovantes = ''
            self.pasta_certidoes = ''
    
    def salvar_config(self):
        """Salva configurações"""
        config = {
            'pasta_comprovantes': self.entry_pasta_comprovantes.get(),
            'pasta_certidoes': self.entry_pasta_certidoes.get()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def criar_interface(self):
        """Cria a interface gráfica com tema escuro"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_dark, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="MESCLADOR DE COMPROVANTES DE PAGAMENTO",
                         font=('Segoe UI', 20, 'bold'), bg=self.bg_dark, fg=self.fg_bright)
        titulo.pack(pady=(0, 20))
        
        # Frame de inputs
        input_frame = tk.Frame(main_frame, bg=self.bg_dark)
        input_frame.pack(fill=tk.X, pady=10)
        
        # 1. Campo Data
        self.criar_campo_input(input_frame, "Pasta da Data das Certidões (AAAA-MM-DD):", 0, 
                              datetime.now().strftime("%Y-%m-%d"), 'entry_data')
        
        # 2. Campo Pasta Comprovantes
        self.criar_campo_pasta(input_frame, "Pasta Comprovantes:", 1, 
                              self.pasta_comprovantes, 'entry_pasta_comprovantes')
        
        # 2.1. Campo Pasta Certidões
        self.criar_campo_pasta(input_frame, "Pasta Certidões:", 2, 
                              self.pasta_certidoes, 'entry_pasta_certidoes')
        
        # 3. Botão Iniciar Mesclagem
        btn_frame = tk.Frame(main_frame, bg=self.bg_dark)
        btn_frame.pack(pady=20)
        
        self.btn_iniciar = tk.Button(btn_frame, text="⚡ INICIAR MESCLAGEM",
                                     font=('Segoe UI', 14, 'bold'),
                                     bg=self.accent_color, fg=self.fg_bright,
                                     activebackground='#1177bb',
                                     activeforeground=self.fg_bright,
                                     relief=tk.FLAT, padx=40, pady=15,
                                     cursor='hand2',
                                     command=self.iniciar_mesclagem)
        self.btn_iniciar.pack()
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=600)
        self.progress.pack(pady=10)
        
        # Label de status
        self.label_status = tk.Label(main_frame, text="Pronto para iniciar",
                                     font=('Segoe UI', 11), bg=self.bg_dark, fg=self.success_color)
        self.label_status.pack(pady=5)
        
        # Área de Log
        log_label = tk.Label(main_frame, text="📋 LOG DE EXECUÇÃO",
                           font=('Segoe UI', 14, 'bold'), bg=self.bg_dark, fg=self.fg_bright)
        log_label.pack(pady=(20, 10))
        
        # Frame do log
        log_frame = tk.Frame(main_frame, bg=self.bg_light)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15,
                                                  font=('Consolas', 11),
                                                  bg=self.bg_light,
                                                  fg=self.fg_color,
                                                  insertbackground=self.fg_color,
                                                  selectbackground=self.accent_color,
                                                  wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Botões de log
        btn_log_frame = tk.Frame(main_frame, bg=self.bg_dark)
        btn_log_frame.pack(pady=10)
        
        btn_salvar_txt = tk.Button(btn_log_frame, text="💾 Salvar TXT",
                                   font=('Segoe UI', 11), bg=self.bg_medium,
                                   fg=self.fg_color, relief=tk.FLAT,
                                   padx=15, pady=8, cursor='hand2',
                                   command=self.salvar_log_txt)
        btn_salvar_txt.pack(side=tk.LEFT, padx=5)
        
        btn_salvar_pdf = tk.Button(btn_log_frame, text="📄 Salvar PDF",
                                   font=('Segoe UI', 11), bg=self.bg_medium,
                                   fg=self.fg_color, relief=tk.FLAT,
                                   padx=15, pady=8, cursor='hand2',
                                   command=self.salvar_log_pdf)
        btn_salvar_pdf.pack(side=tk.LEFT, padx=5)
        
        btn_limpar = tk.Button(btn_log_frame, text="🗑️ Limpar",
                              font=('Segoe UI', 11), bg=self.bg_medium,
                              fg=self.fg_color, relief=tk.FLAT,
                              padx=15, pady=8, cursor='hand2',
                              command=self.limpar_log)
        btn_limpar.pack(side=tk.LEFT, padx=5)
    
    def criar_campo_input(self, parent, label_text, row, default_value, attr_name):
        """Cria um campo de input simples"""
        label = tk.Label(parent, text=label_text, font=('Segoe UI', 12, 'bold'),
                        bg=self.bg_dark, fg=self.fg_color, anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=8, padx=(0, 10))
        
        entry = tk.Entry(parent, font=('Segoe UI', 12), bg=self.bg_medium,
                        fg=self.fg_bright, insertbackground=self.fg_bright,
                        relief=tk.FLAT, width=50)
        entry.grid(row=row, column=1, sticky='ew', pady=8)
        entry.insert(0, default_value)
        
        parent.columnconfigure(1, weight=1)
        setattr(self, attr_name, entry)
    
    def criar_campo_pasta(self, parent, label_text, row, default_value, attr_name):
        """Cria um campo de pasta com botão de navegação"""
        label = tk.Label(parent, text=label_text, font=('Segoe UI', 12, 'bold'),
                        bg=self.bg_dark, fg=self.fg_color, anchor='w')
        label.grid(row=row, column=0, sticky='w', pady=8, padx=(0, 10))
        
        frame = tk.Frame(parent, bg=self.bg_dark)
        frame.grid(row=row, column=1, sticky='ew', pady=8)
        frame.columnconfigure(0, weight=1)
        
        entry = tk.Entry(frame, font=('Segoe UI', 12), bg=self.bg_medium,
                        fg=self.fg_bright, insertbackground=self.fg_bright,
                        relief=tk.FLAT)
        entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        entry.insert(0, default_value)
        
        btn = tk.Button(frame, text="📁", font=('Segoe UI', 12),
                       bg=self.bg_medium, fg=self.fg_color,
                       relief=tk.FLAT, padx=10, cursor='hand2',
                       command=lambda: self.selecionar_pasta(entry))
        btn.grid(row=0, column=1)
        
        setattr(self, attr_name, entry)
    
    def selecionar_pasta(self, entry):
        """Abre diálogo para selecionar pasta"""
        pasta = filedialog.askdirectory()
        if pasta:
            entry.delete(0, tk.END)
            entry.insert(0, pasta)
    
    def log(self, mensagem, tipo='info'):
        """Adiciona mensagem ao log com cores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Definir cor baseada no tipo
        if tipo == 'success':
            cor = self.success_color
            icone = "✓"
        elif tipo == 'warning':
            cor = self.warning_color
            icone = "⚠"
        elif tipo == 'error':
            cor = self.error_color
            icone = "✗"
        else:
            cor = self.fg_color
            icone = "•"
        
        log_entry = f"[{timestamp}] {icone} {mensagem}"
        self.log_messages.append(log_entry)
        
        # Inserir no widget com cor
        self.log_text.insert(tk.END, f"{log_entry}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def limpar_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)
        self.log_messages = []
        self.atualizar_status("Log limpo", 'success')
    
    def atualizar_status(self, mensagem, tipo='info'):
        """Atualiza a label de status"""
        if tipo == 'success':
            cor = self.success_color
        elif tipo == 'warning':
            cor = self.warning_color
        elif tipo == 'error':
            cor = self.error_color
        else:
            cor = self.fg_color
        
        self.label_status.config(text=mensagem, fg=cor)
    
    def salvar_log_txt(self):
        """Salva log em TXT"""
        if not self.log_messages:
            messagebox.showwarning("Aviso", "Não há log para salvar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialfile=f"log_mesclagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.log_messages))
            self.log(f"Log salvo em: {filename}", 'success')
            messagebox.showinfo("Sucesso", f"Log salvo em:\n{filename}")
    
    def salvar_log_pdf(self):
        """Salva log em PDF"""
        if not self.log_messages:
            messagebox.showwarning("Aviso", "Não há log para salvar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
            initialfile=f"log_mesclagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if filename:
            try:
                doc = SimpleDocTemplate(filename, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                title = Paragraph("<b>Log de Execução - Mesclagem de Comprovantes</b>", styles['Title'])
                story.append(title)
                story.append(Spacer(1, 20))
                
                for msg in self.log_messages:
                    para = Preformatted(msg, styles['Code'])
                    story.append(para)
                    story.append(Spacer(1, 5))
                
                doc.build(story)
                self.log(f"Log PDF salvo em: {filename}", 'success')
                messagebox.showinfo("Sucesso", f"Log PDF salvo em:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar PDF:\n{str(e)}")
    
    def normalizar_texto(self, texto):
        """Remove acentos para comparação"""
        if not texto:
            return ""
        nfkd = unicodedata.normalize('NFKD', texto)
        return "".join([c for c in nfkd if not unicodedata.combining(c)]).upper()
    
    def iniciar_mesclagem(self):
        """Inicia o processo de mesclagem - PASSO 3"""
        # Salvar configurações
        self.salvar_config()
        
        # Validar campos
        data = self.entry_data.get().strip()
        pasta_comp_base = self.entry_pasta_comprovantes.get().strip()
        pasta_cert_base = self.entry_pasta_certidoes.get().strip()
        
        if not data:
            messagebox.showerror("Erro", "Por favor, informe a data")
            return
        
        if not pasta_comp_base or not pasta_cert_base:
            messagebox.showerror("Erro", "Por favor, informe as pastas")
            return
        
        # PASSO 4: Construir caminhos
        pasta_comprovantes = os.path.join(pasta_comp_base, data)
        pasta_certidoes = os.path.join(pasta_cert_base, data)
        
        # Verificar pastas
        if not os.path.exists(pasta_comprovantes):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{pasta_comprovantes}")
            return
        
        if not os.path.exists(pasta_certidoes):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{pasta_certidoes}")
            return
        
        # Criar pasta Mesclados
        pasta_mesclados = os.path.join(pasta_comprovantes, "Mesclados")
        os.makedirs(pasta_mesclados, exist_ok=True)
        
        # Log inicial
        self.log("═" * 80)
        self.log("INICIANDO MESCLAGEM DE COMPROVANTES", 'success')
        self.log("═" * 80)
        self.log(f"Data: {data}")
        self.log(f"Comprovantes: {pasta_comprovantes}")
        self.log(f"Certidões: {pasta_certidoes}")
        self.log(f"Mesclados: {pasta_mesclados}")
        self.log("═" * 80)
        
        # Iniciar progresso
        self.progress.start()
        self.atualizar_status("Processando...", 'warning')
        self.btn_iniciar.config(state='disabled')
        
        try:
            # Processar
            self.processar_mesclagem(pasta_comprovantes, pasta_certidoes, pasta_mesclados)
            
            self.log("═" * 80)
            self.log("PROCESSO CONCLUÍDO COM SUCESSO!", 'success')
            self.log("═" * 80)
            self.atualizar_status("Concluído com sucesso!", 'success')
            messagebox.showinfo("Sucesso", "Mesclagem concluída!")
            
        except Exception as e:
            self.log(f"ERRO FATAL: {str(e)}", 'error')
            self.atualizar_status("Erro na execução", 'error')
            messagebox.showerror("Erro", f"Erro:\n{str(e)}")
        
        finally:
            self.progress.stop()
            self.btn_iniciar.config(state='normal')
    
    def processar_mesclagem(self, pasta_comprovantes, pasta_certidoes, pasta_mesclados):
        """Processa todos os arquivos - PASSO 5"""
        # Localizar arquivos de Autorização
        arquivos = os.listdir(pasta_comprovantes)
        arquivos_autorizacao = [f for f in arquivos if "Autorizacao" in f and f.lower().endswith('.pdf')]
        
        if not arquivos_autorizacao:
            self.log("Nenhum arquivo de autorização encontrado", 'warning')
            return
        
        self.log(f"Encontrados {len(arquivos_autorizacao)} arquivos de autorização", 'success')
        self.log("")
        
        for arquivo_auth in arquivos_autorizacao:
            self.processar_arquivo_autorizacao(arquivo_auth, pasta_comprovantes, 
                                              pasta_certidoes, pasta_mesclados)
    
    def processar_arquivo_autorizacao(self, arquivo_auth, pasta_comprovantes, 
                                      pasta_certidoes, pasta_mesclados):
        """Processa um arquivo de autorização - PASSO 5 e 6"""
        self.log(f"━━━ Processando: {arquivo_auth} ━━━")
        
        # Extrair prefixo
        prefixo = arquivo_auth.split("Autorizacao")[0].strip()
        
        # PASSO 6: Extrair dados da tabela
        caminho_auth = os.path.join(pasta_comprovantes, arquivo_auth)
        lista_pagamentos = self.extrair_tabela_autorizacao(caminho_auth)
        
        if not lista_pagamentos:
            self.log("Nenhum pagamento encontrado na tabela", 'warning')
            self.log("")
            return
        
        self.log(f"Extraídos {len(lista_pagamentos)} pagamentos", 'success')
        
        # PASSO 7: Localizar arquivo de COMPROVANTES
        arquivo_comp = self.localizar_arquivo_comprovantes(pasta_comprovantes, prefixo)
        
        if not arquivo_comp:
            self.log(f"Arquivo COMPROVANTES não encontrado para: {prefixo}", 'error')
            self.log("")
            return
        
        self.log(f"Arquivo COMPROVANTES: {os.path.basename(arquivo_comp)}")
        self.log("")
        
        # Processar cada pagamento
        for idx, pagamento in enumerate(lista_pagamentos, 1):
            self.processar_pagamento(idx, len(lista_pagamentos), pagamento, 
                                    arquivo_comp, pasta_certidoes, pasta_mesclados)
        
        self.log("")
    
    def extrair_tabela_autorizacao(self, caminho_pdf):
        """Extrai dados da tabela de autorização - PASSO 6"""
        lista_pagamentos = []
        
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        # Procurar cabeçalho
                        header_row = None
                        for i, row in enumerate(table):
                            row_text = " ".join([str(cell) for cell in row if cell])
                            if "SEI" in row_text and "Empresa" in row_text:
                                header_row = i
                                break
                        
                        if header_row is None:
                            continue
                        
                        # Mapear colunas
                        header = [str(cell).strip() if cell else '' for cell in table[header_row]]
                        colunas = {}
                        
                        for nome in ['SEI', 'Cotação', 'Empresa', 'DANFE', 'Líquido', 'ISS', 'IR']:
                            for i, h in enumerate(header):
                                if nome.upper() in h.upper():
                                    colunas[nome] = i
                                    break
                        
                        # Verificar se tem todas as colunas
                        if len(colunas) < 7:
                            continue
                        
                        # Extrair dados
                        for row in table[header_row + 1:]:
                            if not row or len(row) <= max(colunas.values()):
                                continue
                            
                            try:
                                sei = str(row[colunas['SEI']]).strip()
                                cotacao = str(row[colunas['Cotação']]).strip()
                                empresa = str(row[colunas['Empresa']]).strip()
                                danfe = str(row[colunas['DANFE']]).strip()
                                liquido = str(row[colunas['Líquido']]).strip()
                                iss = str(row[colunas['ISS']]).strip()
                                ir = str(row[colunas['IR']]).strip()
                                
                                if not sei or not empresa:
                                    continue
                                
                                # Extrair 3 primeiros dígitos da cotação
                                match = re.search(r'(\d{3})', cotacao)
                                cotacao_3dig = match.group(1) if match else cotacao[:3]
                                
                                pagamento = {
                                    'sei': sei,
                                    'cotacao_3dig': cotacao_3dig,
                                    'empresa': empresa,
                                    'danfe': danfe,
                                    'liquido': liquido,
                                    'iss': iss,
                                    'ir': ir
                                }
                                
                                lista_pagamentos.append(pagamento)
                                
                            except (IndexError, AttributeError):
                                continue
        
        except Exception as e:
            self.log(f"Erro ao extrair tabela: {str(e)}", 'error')
        
        return lista_pagamentos
    
    def localizar_arquivo_comprovantes(self, pasta, prefixo):
        """Localiza arquivo de COMPROVANTES - PASSO 7"""
        arquivos = os.listdir(pasta)
        
        for arquivo in arquivos:
            if (arquivo.startswith(prefixo) and 
                "COMPROVANTES" in arquivo.upper() and 
                arquivo.lower().endswith('.pdf')):
                return os.path.join(pasta, arquivo)
        
        return None
    
    def processar_pagamento(self, idx, total, pagamento, arquivo_comp, 
                           pasta_certidoes, pasta_mesclados):
        """Processa um pagamento - PASSOS 8, 9, 10, 11"""
        empresa_completa = pagamento['empresa']
        empresa_nome = empresa_completa.split('(')[0].strip()
        
        self.log(f"  [{idx}/{total}] {empresa_nome}")
        self.log(f"      Líquido: {pagamento['liquido']} | DANFE: {pagamento['danfe']}")
        self.log(f"      ISS: {pagamento['iss']} | IR: {pagamento['ir']}")
        
        # PASSO 8: Buscar página principal
        paginas = self.buscar_paginas_comprovante(arquivo_comp, pagamento)
        
        if not paginas:
            self.log(f"      Nenhuma página encontrada", 'warning')
            return
        
        # PASSO 11: Localizar certidões
        certidoes = self.localizar_certidoes(pasta_certidoes, empresa_nome)
        
        if certidoes:
            self.log(f"      ✓ {len(certidoes)} certidões encontradas", 'success')
        
        # PASSO 10: Mesclar
        self.mesclar_pdf(pagamento, paginas, certidoes, arquivo_comp, pasta_mesclados)
        
        self.log("")
    
    def buscar_paginas_comprovante(self, arquivo_comp, pagamento):
        """Busca páginas no comprovante - PASSO 8, 9, 10"""
        paginas = {}
        
        try:
            with pdfplumber.open(arquivo_comp) as pdf:
                liquido = pagamento['liquido']
                danfe = pagamento['danfe']
                iss = pagamento['iss']
                ir = pagamento['ir']
                
                # Variações de formato
                liquido_vars = [liquido, liquido.replace('.', ','), liquido.replace(',', '.')]
                nf_vars = [f"NF{danfe}", f"NF {danfe}", f"N.F. {danfe}", danfe]
                
                for page_num, page in enumerate(pdf.pages):
                    texto = page.extract_text()
                    if not texto:
                        continue
                    
                    # PASSO 8: Buscar página principal (Líquido + DANFE)
                    tem_liquido = any(v in texto for v in liquido_vars)
                    tem_danfe = any(nf in texto.upper() for nf in [v.upper() for v in nf_vars])
                    
                    if tem_liquido and tem_danfe and 'principal' not in paginas:
                        paginas['principal'] = page_num
                        self.log(f"      → Página {page_num + 1}: Principal", 'success')
                    
                    # PASSO 9: Buscar ISS
                    if iss not in ["0,00", "0.00", "0", "-", ""]:
                        if "ISS" in texto.upper() and 'iss' not in paginas:
                            paginas['iss'] = page_num
                            self.log(f"      → Página {page_num + 1}: ISS", 'success')
                    
                    # PASSO 10: Buscar IR
                    if ir not in ["0,00", "0.00", "0", "-", ""]:
                        if "IRRF" in texto.upper() and 'ir' not in paginas:
                            paginas['ir'] = page_num
                            self.log(f"      → Página {page_num + 1}: IR", 'success')
        
        except Exception as e:
            self.log(f"      Erro ao buscar páginas: {str(e)}", 'error')
        
        return paginas
    
    def localizar_certidoes(self, pasta_certidoes, empresa_nome):
        """Localiza certidões da empresa - PASSO 11"""
        certidoes = []
        
        try:
            empresa_norm = self.normalizar_texto(empresa_nome)
            
            if os.path.exists(pasta_certidoes):
                for item in os.listdir(pasta_certidoes):
                    item_path = os.path.join(pasta_certidoes, item)
                    
                    if os.path.isdir(item_path):
                        item_norm = self.normalizar_texto(item)
                        
                        if empresa_norm == item_norm or empresa_norm in item_norm:
                            # Adicionar todos os PDFs
                            for arquivo in os.listdir(item_path):
                                if arquivo.lower().endswith('.pdf'):
                                    certidoes.append(os.path.join(item_path, arquivo))
                            break
        
        except Exception as e:
            self.log(f"      Erro ao localizar certidões: {str(e)}", 'error')
        
        return certidoes
    
    def mesclar_pdf(self, pagamento, paginas, certidoes, arquivo_comp, pasta_mesclados):
        """Mescla tudo em um PDF - PASSO 10"""
        try:
            # Nome do arquivo
            cotacao = pagamento['cotacao_3dig']
            empresa = pagamento['empresa'].split('(')[0].strip()
            danfe = pagamento['danfe']
            sei = pagamento['sei'].replace('/', '-')
            
            nome = f"PAGAMENTO {cotacao} {empresa} {danfe} {sei}.pdf"
            nome = re.sub(r'[<>:"/\\|?*]', '', nome)
            
            caminho_saida = os.path.join(pasta_mesclados, nome)
            
            # Criar PDF
            writer = PdfWriter()
            
            # Adicionar páginas do comprovante
            reader = PdfReader(arquivo_comp)
            
            for tipo in ['principal', 'iss', 'ir']:
                if tipo in paginas:
                    page_num = paginas[tipo]
                    if page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
            
            # Adicionar certidões
            for certidao in certidoes:
                try:
                    cert_reader = PdfReader(certidao)
                    for page in cert_reader.pages:
                        writer.add_page(page)
                except:
                    pass
            
            # Salvar
            if len(writer.pages) > 0:
                with open(caminho_saida, 'wb') as f:
                    writer.write(f)
                
                self.log(f"      ✓ CRIADO: {nome} ({len(writer.pages)} páginas)", 'success')
            else:
                self.log(f"      Sem páginas para mesclar", 'warning')
        
        except Exception as e:
            self.log(f"      Erro ao mesclar: {str(e)}", 'error')


def main():
    root = tk.Tk()
    app = MescladorPagamentos(root)
    root.mainloop()


if __name__ == "__main__":
    main()