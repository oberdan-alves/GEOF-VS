#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Mesclagem de Comprovantes de Pagamento
Desenvolvido para processar autorizações, comprovantes e certidões
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re
import json
from datetime import datetime
from pathlib import Path
import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
import unicodedata


class ComprovanteMesclador:
    def __init__(self, root):
        self.root = root
        self.root.title("Mesclador de Comprovantes de Pagamento")
        self.root.geometry("1200x800")
        
        # Configurações padrão
        self.config_file = "config_mesclador.json"
        self.log_messages = []
        
        # Carregar configurações salvas
        self.load_config()
        
        # Criar interface
        self.create_widgets()
        
    def load_config(self):
        """Carrega configurações salvas anteriormente"""
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
    
    def save_config(self):
        """Salva configurações para uso futuro"""
        config = {
            'pasta_comprovantes': self.entry_pasta_comprovantes.get(),
            'pasta_certidoes': self.entry_pasta_certidoes.get()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def create_widgets(self):
        """Cria a interface gráfica"""
        # Estilo com fontes grandes
        style = ttk.Style()
        style.configure('Large.TLabel', font=('Arial', 12))
        style.configure('Large.TButton', font=('Arial', 12, 'bold'))
        style.configure('Large.TEntry', font=('Arial', 11))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 1. Campo de Data
        row = 0
        ttk.Label(main_frame, text="Data (AAAA-MM-DD):", 
                 style='Large.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_data = ttk.Entry(main_frame, font=('Arial', 12), width=30)
        self.entry_data.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 2. Campo Pasta de Comprovantes (com botão de procurar)
        row += 1
        ttk.Label(main_frame, text="Pasta Comprovantes:", 
                 style='Large.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        
        frame_comprovantes = ttk.Frame(main_frame)
        frame_comprovantes.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        frame_comprovantes.columnconfigure(0, weight=1)
        
        self.entry_pasta_comprovantes = ttk.Entry(frame_comprovantes, font=('Arial', 11))
        self.entry_pasta_comprovantes.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.entry_pasta_comprovantes.insert(0, self.pasta_comprovantes)
        
        ttk.Button(frame_comprovantes, text="...", width=3, 
                  command=lambda: self.browse_folder(self.entry_pasta_comprovantes)).grid(row=0, column=1)
        
        # 2.1. Campo Pasta de Certidões (com botão de procurar)
        row += 1
        ttk.Label(main_frame, text="Pasta Certidões:", 
                 style='Large.TLabel').grid(row=row, column=0, sticky=tk.W, pady=5)
        
        frame_certidoes = ttk.Frame(main_frame)
        frame_certidoes.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        frame_certidoes.columnconfigure(0, weight=1)
        
        self.entry_pasta_certidoes = ttk.Entry(frame_certidoes, font=('Arial', 11))
        self.entry_pasta_certidoes.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.entry_pasta_certidoes.insert(0, self.pasta_certidoes)
        
        ttk.Button(frame_certidoes, text="...", width=3,
                  command=lambda: self.browse_folder(self.entry_pasta_certidoes)).grid(row=0, column=1)
        
        # 3. Botão Iniciar Mesclagem
        row += 1
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="INICIAR MESCLAGEM", 
                  style='Large.TButton', command=self.iniciar_mesclagem,
                  width=30).pack()
        
        # Barra de progresso
        row += 1
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Área de Log
        row += 1
        ttk.Label(main_frame, text="Log de Execução:", 
                 style='Large.TLabel').grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        row += 1
        self.log_text = scrolledtext.ScrolledText(main_frame, height=20, 
                                                   font=('Courier New', 10), wrap=tk.WORD)
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        # Configurar expansão do log
        main_frame.rowconfigure(row, weight=1)
        
        # Botões de salvar log
        row += 1
        button_log_frame = ttk.Frame(main_frame)
        button_log_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_log_frame, text="Salvar Log em TXT", 
                  command=self.salvar_log_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_log_frame, text="Salvar Log em PDF", 
                  command=self.salvar_log_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_log_frame, text="Limpar Log", 
                  command=self.limpar_log).pack(side=tk.LEFT, padx=5)
    
    def browse_folder(self, entry_widget):
        """Abre diálogo para selecionar pasta"""
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)
    
    def log(self, mensagem):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {mensagem}"
        self.log_messages.append(log_entry)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def limpar_log(self):
        """Limpa o log de execução"""
        self.log_text.delete(1.0, tk.END)
        self.log_messages = []
    
    def salvar_log_txt(self):
        """Salva log em arquivo TXT"""
        if not self.log_messages:
            messagebox.showwarning("Aviso", "Não há log para salvar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"log_mesclagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.log_messages))
            self.log(f"Log salvo em: {filename}")
            messagebox.showinfo("Sucesso", f"Log salvo em:\n{filename}")
    
    def salvar_log_pdf(self):
        """Salva log em arquivo PDF"""
        if not self.log_messages:
            messagebox.showwarning("Aviso", "Não há log para salvar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"log_mesclagem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        if filename:
            try:
                doc = SimpleDocTemplate(filename, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                # Título
                title = Paragraph(f"<b>Log de Execução - Mesclagem de Comprovantes</b>", 
                                styles['Title'])
                story.append(title)
                story.append(Spacer(1, 20))
                
                # Conteúdo do log
                for msg in self.log_messages:
                    para = Preformatted(msg, styles['Code'])
                    story.append(para)
                    story.append(Spacer(1, 5))
                
                doc.build(story)
                self.log(f"Log PDF salvo em: {filename}")
                messagebox.showinfo("Sucesso", f"Log PDF salvo em:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar PDF:\n{str(e)}")
    
    def normalizar_texto(self, texto):
        """Remove acentos e converte para maiúsculas para comparação"""
        if not texto:
            return ""
        # Remove acentos
        nfkd = unicodedata.normalize('NFKD', texto)
        texto_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
        return texto_sem_acento.upper()
    
    def comparar_textos_similares(self, texto1, texto2):
        """Compara dois textos ignorando acentos e maiúsculas"""
        return self.normalizar_texto(texto1) == self.normalizar_texto(texto2)
    
    def iniciar_mesclagem(self):
        """Inicia o processo de mesclagem"""
        # Salvar configurações
        self.save_config()
        
        # Validar campos
        data = self.entry_data.get().strip()
        pasta_comp_base = self.entry_pasta_comprovantes.get().strip()
        pasta_cert_base = self.entry_pasta_certidoes.get().strip()
        
        if not data:
            messagebox.showerror("Erro", "Por favor, informe a data")
            return
        
        if not pasta_comp_base:
            messagebox.showerror("Erro", "Por favor, informe a pasta de comprovantes")
            return
        
        if not pasta_cert_base:
            messagebox.showerror("Erro", "Por favor, informe a pasta de certidões")
            return
        
        # Construir caminhos completos
        pasta_comprovantes = os.path.join(pasta_comp_base, data)
        pasta_certidoes = os.path.join(pasta_cert_base, data)
        
        # Verificar se pastas existem
        if not os.path.exists(pasta_comprovantes):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{pasta_comprovantes}")
            return
        
        if not os.path.exists(pasta_certidoes):
            messagebox.showerror("Erro", f"Pasta não encontrada:\n{pasta_certidoes}")
            return
        
        # Criar pasta Mesclados
        pasta_mesclados = os.path.join(pasta_comprovantes, "Mesclados")
        os.makedirs(pasta_mesclados, exist_ok=True)
        
        self.log("=" * 80)
        self.log("INICIANDO PROCESSO DE MESCLAGEM")
        self.log("=" * 80)
        self.log(f"Data: {data}")
        self.log(f"Pasta Comprovantes: {pasta_comprovantes}")
        self.log(f"Pasta Certidões: {pasta_certidoes}")
        self.log(f"Pasta Mesclados: {pasta_mesclados}")
        self.log("")
        
        # Iniciar barra de progresso
        self.progress.start()
        
        try:
            # Processar arquivos
            self.processar_autorizacoes(pasta_comprovantes, pasta_certidoes, pasta_mesclados)
            
            self.log("")
            self.log("=" * 80)
            self.log("PROCESSO CONCLUÍDO COM SUCESSO!")
            self.log("=" * 80)
            messagebox.showinfo("Sucesso", "Mesclagem concluída com sucesso!")
            
        except Exception as e:
            self.log(f"ERRO: {str(e)}")
            messagebox.showerror("Erro", f"Erro durante o processo:\n{str(e)}")
        
        finally:
            self.progress.stop()
    
    def processar_autorizacoes(self, pasta_comprovantes, pasta_certidoes, pasta_mesclados):
        """Processa todos os arquivos de autorização"""
        # Passo 5: Localizar arquivos com "Autorizacao"
        arquivos = os.listdir(pasta_comprovantes)
        arquivos_autorizacao = [f for f in arquivos if "Autorizacao" in f and f.endswith('.pdf')]
        
        self.log(f"Encontrados {len(arquivos_autorizacao)} arquivos de autorização")
        self.log("")
        
        for arquivo_auth in arquivos_autorizacao:
            self.log(f"Processando: {arquivo_auth}")
            
            # Extrair prefixo (antes de "Autorizacao")
            prefixo = arquivo_auth.split("Autorizacao")[0].strip()
            
            # Passo 6: Extrair dados da tabela de autorização
            caminho_auth = os.path.join(pasta_comprovantes, arquivo_auth)
            lista_pagamentos = self.extrair_dados_autorizacao(caminho_auth)
            
            if not lista_pagamentos:
                self.log(f"  Nenhum dado extraído de {arquivo_auth}")
                continue
            
            self.log(f"  Extraídos {len(lista_pagamentos)} pagamentos")
            
            # Passo 7: Localizar arquivo de COMPROVANTES
            arquivo_comprovantes = self.localizar_arquivo_comprovantes(pasta_comprovantes, prefixo)
            
            if not arquivo_comprovantes:
                self.log(f"  AVISO: Arquivo de comprovantes não encontrado para prefixo: {prefixo}")
                continue
            
            self.log(f"  Arquivo de comprovantes: {arquivo_comprovantes}")
            
            # Processar cada pagamento da lista
            for idx, pagamento in enumerate(lista_pagamentos, 1):
                self.log(f"  Processando pagamento {idx}/{len(lista_pagamentos)}: {pagamento['empresa']}")
                self.processar_pagamento(pagamento, arquivo_comprovantes, 
                                       pasta_certidoes, pasta_mesclados)
            
            self.log("")
    
    def extrair_dados_autorizacao(self, caminho_pdf):
        """Extrai dados da tabela de autorização (Passo 6)"""
        lista_pagamentos = []
        
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                for page in pdf.pages:
                    # Extrair tabelas
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        # Procurar cabeçalho
                        header_row = None
                        for i, row in enumerate(table):
                            if any('SEI' in str(cell) for cell in row if cell):
                                header_row = i
                                break
                        
                        if header_row is None:
                            continue
                        
                        # Identificar índices das colunas
                        header = [str(cell).strip() if cell else '' for cell in table[header_row]]
                        
                        indices = {}
                        for col_name in ['SEI', 'Cotação', 'Empresa', 'DANFE', 'Líquido', 'ISS', 'IR']:
                            for i, h in enumerate(header):
                                if col_name.upper() in h.upper():
                                    indices[col_name] = i
                                    break
                        
                        # Verificar se encontrou as colunas necessárias
                        if len(indices) < 7:
                            continue
                        
                        # Extrair dados das linhas
                        for row in table[header_row + 1:]:
                            if not row or len(row) <= max(indices.values()):
                                continue
                            
                            try:
                                sei = str(row[indices['SEI']]).strip()
                                cotacao = str(row[indices['Cotação']]).strip()
                                empresa = str(row[indices['Empresa']]).strip()
                                danfe = str(row[indices['DANFE']]).strip()
                                liquido = str(row[indices['Líquido']]).strip()
                                iss = str(row[indices['ISS']]).strip()
                                ir = str(row[indices['IR']]).strip()
                                
                                # Validar dados
                                if not sei or not empresa:
                                    continue
                                
                                # Extrair 3 primeiros dígitos da cotação
                                cotacao_digitos = re.search(r'(\d{3})', cotacao)
                                if cotacao_digitos:
                                    cotacao_3dig = cotacao_digitos.group(1)
                                else:
                                    cotacao_3dig = cotacao[:3] if len(cotacao) >= 3 else cotacao
                                
                                pagamento = {
                                    'sei': sei,
                                    'cotacao': cotacao,
                                    'cotacao_3dig': cotacao_3dig,
                                    'empresa': empresa,
                                    'danfe': danfe,
                                    'liquido': liquido,
                                    'iss': iss,
                                    'ir': ir
                                }
                                
                                lista_pagamentos.append(pagamento)
                                
                            except (IndexError, AttributeError) as e:
                                continue
        
        except Exception as e:
            self.log(f"    Erro ao extrair dados: {str(e)}")
        
        return lista_pagamentos
    
    def localizar_arquivo_comprovantes(self, pasta, prefixo):
        """Localiza arquivo de comprovantes baseado no prefixo (Passo 7)"""
        arquivos = os.listdir(pasta)
        
        # Procurar arquivo com o mesmo prefixo e "COMPROVANTES"
        for arquivo in arquivos:
            if arquivo.startswith(prefixo) and "COMPROVANTES" in arquivo.upper() and arquivo.endswith('.pdf'):
                return os.path.join(pasta, arquivo)
        
        return None
    
    def processar_pagamento(self, pagamento, arquivo_comprovantes, pasta_certidoes, pasta_mesclados):
        """Processa um pagamento individual (Passos 8-11)"""
        try:
            empresa = pagamento['empresa']
            empresa_nome = empresa.split('(')[0].strip()  # Nome sem o código
            
            # Passo 8, 9, 10: Extrair páginas do comprovante
            paginas_extraidas = self.extrair_paginas_comprovante(
                arquivo_comprovantes, pagamento
            )
            
            if not paginas_extraidas:
                self.log(f"    AVISO: Nenhuma página encontrada no comprovante para {empresa_nome}")
                return
            
            # Passo 11: Localizar certidões
            certidoes = self.localizar_certidoes(pasta_certidoes, empresa_nome)
            
            # Passo 10: Mesclar tudo
            self.mesclar_arquivos(pagamento, paginas_extraidas, certidoes, pasta_mesclados)
            
        except Exception as e:
            self.log(f"    Erro ao processar pagamento: {str(e)}")
    
    def extrair_paginas_comprovante(self, arquivo_comprovantes, pagamento):
        """Extrai páginas relevantes do arquivo de comprovantes (Passos 8, 9, 10)"""
        paginas_dict = {}
        
        try:
            with pdfplumber.open(arquivo_comprovantes) as pdf:
                empresa = pagamento['empresa']
                empresa_nome = empresa.split('(')[0].strip()
                liquido = pagamento['liquido']
                danfe = pagamento['danfe']
                iss = pagamento['iss']
                ir = pagamento['ir']
                
                for page_num, page in enumerate(pdf.pages):
                    texto = page.extract_text()
                    
                    if not texto:
                        continue
                    
                    # Passo 8: Buscar página principal
                    # Tentar busca completa
                    if empresa in texto:
                        paginas_dict['principal'] = page_num
                    # Tentar busca sem código
                    elif empresa_nome in texto:
                        paginas_dict['principal'] = page_num
                    # Tentar busca por valor + NF
                    elif liquido in texto and f"NF{danfe}" in texto:
                        paginas_dict['principal'] = page_num
                    
                    # Passo 9: Buscar página ISS
                    if iss and iss != "0,00" and iss != "0.00":
                        if "ISS" in texto and 'principal' in paginas_dict and page_num != paginas_dict['principal']:
                            paginas_dict['iss'] = page_num
                    
                    # Passo 10: Buscar página IR
                    if ir and ir != "0,00" and ir != "0.00":
                        if "IRRF" in texto and 'principal' in paginas_dict and page_num != paginas_dict['principal']:
                            paginas_dict['ir'] = page_num
        
        except Exception as e:
            self.log(f"    Erro ao extrair páginas: {str(e)}")
        
        return paginas_dict
    
    def localizar_certidoes(self, pasta_certidoes, empresa_nome):
        """Localiza certidões da empresa (Passo 11)"""
        certidoes = []
        
        try:
            # Normalizar nome da empresa para comparação
            empresa_normalizada = self.normalizar_texto(empresa_nome)
            
            # Procurar subpasta com nome similar
            if os.path.exists(pasta_certidoes):
                for item in os.listdir(pasta_certidoes):
                    item_path = os.path.join(pasta_certidoes, item)
                    
                    if os.path.isdir(item_path):
                        item_normalizado = self.normalizar_texto(item)
                        
                        # Comparar nomes
                        if empresa_normalizada == item_normalizado or empresa_normalizada in item_normalizado:
                            # Adicionar todos os PDFs desta pasta
                            for arquivo in os.listdir(item_path):
                                if arquivo.endswith('.pdf'):
                                    certidoes.append(os.path.join(item_path, arquivo))
                            break
        
        except Exception as e:
            self.log(f"    Erro ao localizar certidões: {str(e)}")
        
        return certidoes
    
    def mesclar_arquivos(self, pagamento, paginas_dict, certidoes, pasta_mesclados):
        """Mescla todas as páginas e certidões em um único PDF (Passo 10)"""
        try:
            # Criar nome do arquivo
            cotacao_3dig = pagamento['cotacao_3dig']
            empresa_nome = pagamento['empresa'].split('(')[0].strip()
            danfe = pagamento['danfe']
            sei = pagamento['sei']
            
            nome_arquivo = f"COMPROVANTE DE PAGAMENTO {cotacao_3dig} {empresa_nome} {danfe} {sei}.pdf"
            
            # Limpar nome de caracteres inválidos
            nome_arquivo = re.sub(r'[<>:"/\\|?*]', '', nome_arquivo)
            
            caminho_saida = os.path.join(pasta_mesclados, nome_arquivo)
            
            # Criar PDF mesclado
            writer = PdfWriter()
            
            # Obter arquivo de comprovantes
            arquivo_comprovantes = None
            for root, dirs, files in os.walk(os.path.dirname(pasta_mesclados)):
                for f in files:
                    if "COMPROVANTES" in f.upper() and f.endswith('.pdf'):
                        arquivo_comprovantes = os.path.join(root, f)
                        break
                if arquivo_comprovantes:
                    break
            
            if arquivo_comprovantes and os.path.exists(arquivo_comprovantes):
                reader = PdfReader(arquivo_comprovantes)
                
                # Adicionar páginas extraídas do comprovante
                for tipo in ['principal', 'iss', 'ir']:
                    if tipo in paginas_dict:
                        page_num = paginas_dict[tipo]
                        if page_num < len(reader.pages):
                            writer.add_page(reader.pages[page_num])
            
            # Adicionar certidões
            for certidao in certidoes:
                if os.path.exists(certidao):
                    try:
                        cert_reader = PdfReader(certidao)
                        for page in cert_reader.pages:
                            writer.add_page(page)
                    except Exception as e:
                        self.log(f"    Erro ao adicionar certidão {certidao}: {str(e)}")
            
            # Salvar arquivo mesclado
            if len(writer.pages) > 0:
                with open(caminho_saida, 'wb') as output_file:
                    writer.write(output_file)
                
                self.log(f"    ✓ Criado: {nome_arquivo} ({len(writer.pages)} páginas)")
            else:
                self.log(f"    AVISO: Nenhuma página para mesclar em {nome_arquivo}")
        
        except Exception as e:
            self.log(f"    Erro ao mesclar arquivos: {str(e)}")


def main():
    root = tk.Tk()
    app = ComprovanteMesclador(root)
    root.mainloop()


if __name__ == "__main__":
    main()