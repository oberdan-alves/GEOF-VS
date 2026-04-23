import tkinter as tk
from tkinter import ttk
import pyodbc

# Conectar ao banco de dados
conn_str = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Revolutions\Revolutions.mdb;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

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

# Função para buscar dados ao selecionar um CODIGOSIS
def buscar_dados_codigosis(codigosis_var, descricao_var, saldolivre_var, unidade_var):
    codigo_sis = codigosis_var.get()
    if codigo_sis:
        cursor.execute('SELECT Descricao, SaldoLivre, Unidade FROM BD WHERE CodigoSIS = ?', (codigo_sis,))
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
    cursor.execute('INSERT INTO CONTROLE (TR, IdOrigem, DtRecebimento, SEI, IdOperador, Cotacao) VALUES (?, ?, ?, ?, ?, ?)',
                   (tr, origem, dtrecebimento, sei, servidor, cotacao))
    cursor.execute('INSERT INTO CONTROLE_ITENS (Item, CodigoSIS, QtdSol) VALUES (?, ?, ?)',
                   (item, codigosis, qtdsol))
    conn.commit()

# Labels e Entries para os campos
label_tr = ttk.Label(root, text="TR:")
entry_tr = ttk.Entry(root, textvariable=tr_var)

label_origem = ttk.Label(root, text="Origem:")
entry_origem = ttk.Entry(root, textvariable=origem_var)

label_dtrecebimento = ttk.Label(root, text="Data de Recebimento:")
entry_dtrecebimento = ttk.Entry(root, textvariable=dtrecebimento_var)

label_sei = ttk.Label(root, text="SEI:")
entry_sei = ttk.Entry(root, textvariable=sei_var)

label_servidor = ttk.Label(root, text="Servidor:")
entry_servidor = ttk.Entry(root, textvariable=servidor_var)

label_cotacao = ttk.Label(root, text="Cotação:")
entry_cotacao = ttk.Entry(root, textvariable=cotacao_var)

label_item = ttk.Label(root, text="Item:")
entry_item = ttk.Entry(root, textvariable=item_var)

label_codigosis = ttk.Label(root, text="Código SIS:")
entry_codigosis = ttk.Entry(root, textvariable=codigosis_var)
entry_codigosis.bind("<FocusOut>", lambda event: buscar_dados_codigosis(codigosis_var, descricao_var, saldolivre_var, unidade_var))

label_descricao = ttk.Label(root, text="Descrição:")
entry_descricao = ttk.Entry(root, textvariable=descricao_var, state='readonly')

label_saldolivre = ttk.Label(root, text="Saldo Livre:")
entry_saldolivre = ttk.Entry(root, textvariable=saldolivre_var, state='readonly')

label_unidade = ttk.Label(root, text="Unidade:")
entry_unidade = ttk.Entry(root, textvariable=unidade_var, state='readonly')

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
entry_origem.grid(row=1, column=1, padx=5, pady=5)

label_dtrecebimento.grid(row=2, column=0, padx=5, pady=5, sticky='e')
entry_dtrecebimento.grid(row=2, column=1, padx=5, pady=5)

label_sei.grid(row=3, column=0, padx=5, pady=5, sticky='e')
entry_sei.grid(row=3, column=1, padx=5, pady=5)

label_servidor.grid(row=4, column=0, padx=5, pady=5, sticky='e')
entry_servidor.grid(row=4, column=1, padx=5, pady=5)

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
