import tkinter as tk
from tkinter import ttk
import sqlite3

# Conectar ao banco de dados SQLite
conn = sqlite3.connect('Revolutions.mdb')
cursor = conn.cursor()

# Criar a tabela ORIGEM
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ORIGEM (
        ID INTEGER PRIMARY KEY,
        NOME TEXT
    )
''')

# Criar a tabela OPERADOR
cursor.execute('''
    CREATE TABLE IF NOT EXISTS OPERADOR (
        ID INTEGER PRIMARY KEY,
        NOME TEXT
    )
''')

# Criar a tabela BD
cursor.execute('''
    CREATE TABLE IF NOT EXISTS BD (
        CODIGOSIS INTEGER PRIMARY KEY,
        DESCRICAO TEXT,
        SALDOLIVRE REAL,
        UNIDADE TEXT
    )
''')

# Criar a tabela CONTROLE
cursor.execute('''
    CREATE TABLE IF NOT EXISTS CONTROLE (
        TR INTEGER PRIMARY KEY,
        ORIGEM_ID INTEGER,
        DTRECEBIMENTO TEXT,
        SEI TEXT,
        SERVIDOR_ID INTEGER,
        FOREIGN KEY (ORIGEM_ID) REFERENCES ORIGEM(ID),
        FOREIGN KEY (SERVIDOR_ID) REFERENCES OPERADOR(ID)
    )
''')

# Criar a tabela CONTROLE_ITENS
cursor.execute('''
    CREATE TABLE IF NOT EXISTS CONTROLE_ITENS (
        ID INTEGER PRIMARY KEY,
        CONTROLE_TR INTEGER,
        COTACAO TEXT,
        ITEM TEXT,
        CODIGOSIS INTEGER,
        QTDSOL INTEGER,
        FOREIGN KEY (CONTROLE_TR) REFERENCES CONTROLE(TR),
        FOREIGN KEY (CODIGOSIS) REFERENCES BD(CODIGOSIS)
    )
''')

# Função para preencher os campos ao selecionar um CODIGOSIS
def buscar_dados_codigosis(codigosis_var, descricao_var, saldolivre_var, unidade_var):
    codigo_sis = codigosis_var.get()
    if codigo_sis:
        cursor.execute('SELECT DESCRICAO, SALDOLIVRE, UNIDADE FROM BD WHERE CODIGOSIS = ?', (codigo_sis,))
        dados = cursor.fetchone()
        if dados:
            descricao_var.set(dados[0])
            saldolivre_var.set(dados[1])
            unidade_var.set(dados[2])
        else:
            descricao_var.set('')
            saldolivre_var.set('')
            unidade_var.set('')
    else:
        descricao_var.set('')
        saldolivre_var.set('')
        unidade_var.set('')

# Função para salvar os dados no banco de dados
def salvar_dados(tr, origem, dtrecebimento, sei, servidor, cotacao, item, codigosis, qtdsol):
    cursor.execute('INSERT INTO CONTROLE (TR, ORIGEM_ID, DTRECEBIMENTO, SEI, SERVIDOR_ID) VALUES (?, ?, ?, ?, ?)',
                   (tr, origem, dtrecebimento, sei, servidor))
    cursor.execute('INSERT INTO CONTROLE_ITENS (CONTROLE_TR, COTACAO, ITEM, CODIGOSIS, QTDSOL) VALUES (?, ?, ?, ?, ?)',
                   (tr, cotacao, item, codigosis, qtdsol))
    conn.commit()

# Interface gráfica
root = tk.Tk()
root.title("Cadastro de Controle")

# Variáveis para armazenar os valores dos campos
tr_var = tk.StringVar()
origem_var = tk.StringVar()
dtrecebimento_var = tk.StringVar()
sei_var = tk.StringVar()
servidor_var = tk.StringVar()
cotacao_var = tk.StringVar()
item_var = tk.StringVar()
codigosis_var = tk.StringVar()
descricao_var = tk.StringVar()
saldolivre_var = tk.StringVar()
unidade_var = tk.StringVar()
qtdsol_var = tk.StringVar()

# Label e Entry para TR
label_tr = ttk.Label(root, text="TR:")
entry_tr = ttk.Entry(root, textvariable=tr_var)

# Label e Combobox para ORIGEM
label_origem = ttk.Label(root, text="Origem:")
combo_origem = ttk.Combobox(root, textvariable=origem_var, values=["Origem1", "Origem2"])  # Adicione os valores reais

# Label e Entry para DTRECEBIMENTO
label_dtrecebimento = ttk.Label(root, text="Data de Recebimento:")
entry_dtrecebimento = ttk.Entry(root, textvariable=dtrecebimento_var)

# Label e Entry para SEI
label_sei = ttk.Label(root, text="SEI:")
entry_sei = ttk.Entry(root, textvariable=sei_var)

# Label e Combobox para SERVIDOR
label_servidor = ttk.Label(root, text="Servidor:")
combo_servidor = ttk.Combobox(root, textvariable=servidor_var, values=["Servidor1", "Servidor2"])  # Adicione os valores reais

# Label e Entry para COTACAO
label_cotacao = ttk.Label(root, text="Cotação:")
entry_cotacao = ttk.Entry(root, textvariable=cotacao_var)

# Label e Entry para ITEM
label_item = ttk.Label(root, text="Item:")
entry_item = ttk.Entry(root, textvariable=item_var)

# Label e Entry para CODIGOSIS
label_codigosis = ttk.Label(root, text="Código SIS:")
entry_codigosis = ttk.Entry(root, textvariable=codigosis_var)
entry_codigosis.bind("<FocusOut>", lambda event: buscar_dados_codigosis(codigosis_var, descricao_var, saldolivre_var, unidade_var))

# Labels para exibir informações relacionadas ao CODIGOSIS
label_descricao = ttk.Label(root, text="Descrição:")
label_saldolivre = ttk.Label(root, text="Saldo Livre:")
label_unidade = ttk.Label(root, text="Unidade:")

# Entradas desabilitadas para exibir informações relacionadas ao CODIGOSIS
entry_descricao = ttk.Entry(root, textvariable=descricao_var, state='readonly')
entry_saldolivre = ttk.Entry(root, textvariable=saldolivre_var, state='readonly')
entry_unidade = ttk.Entry(root, textvariable=unidade_var, state='readonly')

# Label e Entry para QTDSOL
label_qtdsol = ttk.Label(root, text="Quantidade Solicitada:")
entry_qtdsol = ttk.Entry(root, textvariable=qtdsol_var)

# Botão para salvar os dados
botao_salvar = ttk.Button(root, text="Salvar",
                          command=lambda: salvar_dados(tr_var.get(), origem_var.get(), dtrecebimento_var.get(),
                                                      sei_var.get(), servidor_var.get(), cotacao_var.get(),
                                                      item_var.get(), codigosis_var.get(), qtdsol_var.get()))

# Layout da interface gráfica
label_tr.grid(row=0, column=0, padx=5, pady=5, sticky='e')
entry_tr.grid(row=0, column=1, padx=5, pady=5)

label_origem.grid(row=1, column=0, padx=5, pady=5, sticky='e')
combo_origem.grid(row=1, column=1, padx=5, pady=5)

label_dtrecebimento.grid(row=2, column=0, padx=5, pady=5, sticky='e')
entry_dtrecebimento.grid(row=2, column=1, padx=5, pady=5)

label_sei.grid(row=3, column=0, padx=5, pady=5, sticky='e')
entry_sei.grid(row=3, column=1, padx=5, pady=5)

label_servidor.grid(row=4, column=0, padx=5, pady=5, sticky='e')
combo_servidor.grid(row=4, column=1, padx=5, pady=5)

label_cotacao.grid(row=5, column=0, padx=5, pady=5, sticky='e')
entry_cotacao.grid(row=5, column=1, padx=5, pady=5)

label_item.grid(row=6, column=0, padx=5, pady=5, sticky='e')
entry_item.grid(row=6, column=1, padx=5, pady=5)

label_codigosis.grid(row=7, column=0, padx=5, pady=5, sticky='e')
entry_codigosis.grid(row=7, column=1, padx=5, pady=5)

label_descricao.grid(row=8, column=0, padx=5, pady=5, sticky='e')
entry_descricao.grid(row=8, column=1, padx=5, pady=5)

label_saldolivre.grid(row=9, column=0, padx=5, pady=5, sticky='e')
entry_saldolivre.grid(row=9, column=1, padx=5, pady=5)

label_unidade.grid(row=10, column=0, padx=5, pady=5, sticky='e')
entry_unidade.grid(row=10, column=1, padx=5, pady=5)

label_qtdsol.grid(row=11, column=0, padx=5, pady=5, sticky='e')
entry_qtdsol.grid(row=11, column=1, padx=5, pady=5)

botao_salvar.grid(row=12, column=0, columnspan=2, pady=10)

root.mainloop()
