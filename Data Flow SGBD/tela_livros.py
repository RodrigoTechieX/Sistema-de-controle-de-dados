# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendlivros import BancoDeDadosLivros


def abrir_tela_auditoria(master, db, frame_livros, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, frame_livros, usuario_logado)
    ts.iniciar()


def abrir_tela_principal(master, db, frame_login, usuario_logado):
    from Lobby import TelaPrincipal
    ts = TelaPrincipal(master, db, frame_login, usuario_logado)
    ts.iniciar()


def adicionar_placeholder(entry, placeholder_text):
    """Configura placeholder que desaparece ao focar e reaparece ao desfocar."""
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg="grey")

    entry.insert(0, placeholder_text)
    entry.config(fg="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


class TelaLivros:
    ALTURA_NAVBAR = 60

    def __init__(self, master, frame_login, usuario_logado):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.master.title("Data Flow - Gerenciamento de Livros")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosLivros()

        self.frame_livros = tk.Frame(master)
        self.frame_livros.pack(fill="both", expand=True)
        self.livro_atual_id = None
        self.janela_ajuda = None
        self.entries = {}

        self.placeholders = {
            "ISBN": "Ex.: 978-85-00000-000-0",
            "Título": "Ex.: O Pequeno Príncipe",
            "Autor(es)": "Ex.: Antoine de Saint-Exupéry",
            "Editora": "Ex.: Companhia das Letras",
            "Ano de publicação": "Ex.: 1943",
            "Categoria/Gênero": "Ex.: Infantojuvenil",
            "Nº de páginas": "Ex.: 96",
            "Preço": "Ex.: 29.90"
        }

        self.setup_tela_livros()
        self.carregar_livros()

    def setup_tela_livros(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)

 # ---------- NAVBAR ----------
        self.ALTURA_NAVBAR = 0.10  # Altura relativa (10% da tela)
        frame_navbar = tk.Frame(self.frame_livros, bg="#1F222B")
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        # Configura grid interno (opcional, para alinhamento)
        frame_navbar.columnconfigure(0, weight=1)
        frame_navbar.columnconfigure(1, weight=1)
        frame_navbar.columnconfigure(2, weight=1)

        # Título centralizado
        titulo = tk.Label(frame_navbar,
                        text="Gerenciador de Livros",
                        font=("Helvetica", 14, "bold"),
                        fg="white", bg="#1F222B")
        titulo.place(relx=0.5, rely=0.45, anchor="center")  # Ajuste fino do rely

        # Ícone do usuário
        caminho_imagem_usuario = os.path.join(diretorio_atual, "imagens", "usuariosistema.png")
        try:
            imagem_usuario = Image.open(caminho_imagem_usuario).resize((16, 18), Image.LANCZOS)
            self.icone_usuario = ImageTk.PhotoImage(imagem_usuario)
        except Exception:
            self.icone_usuario = None

        label_usuario = tk.Label(frame_navbar, text=f"{self.usuario_logado}",
                                font=("Helvetica", 12, "bold"),
                                bg="#1F222B", fg="white",
                                image=self.icone_usuario, compound="left",
                                padx=5, pady=5)
        label_usuario.place(relx=0.95, rely=0.45, anchor="e")  # Pode ajustar relx/rely aqui

        # ---------- SIDEBAR ----------
        frame_sidebar = tk.Frame(self.frame_livros, bg="#1F222B")
        frame_sidebar.place(relx=0, rely=0.09, relwidth=0.05, relheight=0.98)

        icones_sidebar = ["🏠", "📚", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg="#1F222B", fg="white",
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=15, padx=5, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#003366"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1F222B"))


        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_livros, bg="#eaeaea")
        frame_conteudo.place(relx=0.05, rely=0.08, relwidth=0.95, relheight=0.92)

        # --- LADO ESQUERDO (grid sem for) ---
        frame_esquerdo = tk.Frame(frame_conteudo, bg="#f7f7f7", highlightbackground="#ccc", highlightthickness=1)
        frame_esquerdo.place(relx=0.02, rely=0.03, relwidth=0.28, relheight=0.94)
        frame_esquerdo.configure(bd=2, relief="groove")

        sombra = tk.Frame(frame_conteudo, bg="#d0d0d0")
        sombra.place(relx=0.023, rely=0.036, relwidth=0.28, relheight=0.94)
        frame_esquerdo.lift()

        # Configura grid interno
        for i in range(20):
            frame_esquerdo.rowconfigure(i, weight=1)
        frame_esquerdo.columnconfigure(0, weight=1)

        # Campos de entrada
        lbl_isbn = tk.Label(frame_esquerdo, text="ISBN:", font=label_font, bg="#f7f7f7")
        lbl_isbn.grid(row=0, column=0, sticky="w", padx=5, pady=(5,0))
        entry_isbn = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_isbn.grid(row=1, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_isbn, "Ex.: 978-85-00000-000-0")
        self.entries["ISBN"] = entry_isbn

        lbl_titulo = tk.Label(frame_esquerdo, text="Título:", font=label_font, bg="#f7f7f7")
        lbl_titulo.grid(row=2, column=0, sticky="w", padx=5, pady=(5,0))
        entry_titulo = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_titulo.grid(row=3, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_titulo, "Ex.: O Pequeno Príncipe")
        self.entries["Título"] = entry_titulo

        lbl_autor = tk.Label(frame_esquerdo, text="Autor(es):", font=label_font, bg="#f7f7f7")
        lbl_autor.grid(row=4, column=0, sticky="w", padx=5, pady=(5,0))
        entry_autor = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_autor.grid(row=5, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_autor, "Ex.: Antoine de Saint-Exupéry")
        self.entries["Autor(es)"] = entry_autor

        lbl_editora = tk.Label(frame_esquerdo, text="Editora:", font=label_font, bg="#f7f7f7")
        lbl_editora.grid(row=6, column=0, sticky="w", padx=5, pady=(5,0))
        entry_editora = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_editora.grid(row=7, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_editora, "Ex.: Companhia das Letras")
        self.entries["Editora"] = entry_editora

        lbl_ano = tk.Label(frame_esquerdo, text="Ano de publicação:", font=label_font, bg="#f7f7f7")
        lbl_ano.grid(row=8, column=0, sticky="w", padx=5, pady=(5,0))
        entry_ano = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_ano.grid(row=9, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_ano, "Ex.: 1943")
        self.entries["Ano de publicação"] = entry_ano

        lbl_categoria = tk.Label(frame_esquerdo, text="Categoria/Gênero:", font=label_font, bg="#f7f7f7")
        lbl_categoria.grid(row=10, column=0, sticky="w", padx=5, pady=(5,0))
        entry_categoria = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_categoria.grid(row=11, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_categoria, "Ex.: Infantojuvenil")
        self.entries["Categoria/Gênero"] = entry_categoria

        lbl_paginas = tk.Label(frame_esquerdo, text="Nº de páginas:", font=label_font, bg="#f7f7f7")
        lbl_paginas.grid(row=12, column=0, sticky="w", padx=5, pady=(5,0))
        entry_paginas = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_paginas.grid(row=13, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_paginas, "Ex.: 96")
        self.entries["Nº de páginas"] = entry_paginas

        lbl_preco = tk.Label(frame_esquerdo, text="Preço:", font=label_font, bg="#f7f7f7")
        lbl_preco.grid(row=14, column=0, sticky="w", padx=5, pady=(5,0))
        entry_preco = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_preco.grid(row=15, column=0, sticky="ew", padx=5, pady=(0,5))
        adicionar_placeholder(entry_preco, "Ex.: 29.90")
        self.entries["Preço"] = entry_preco

        # Botões CRUD
        def estilizar_botao(botao, cor_base):
            botao.config(bg=cor_base, fg="black", relief="flat", font=button_font, bd=0)
            botao.bind("<Enter>", lambda e: botao.config(bg="#bcbcbc"))
            botao.bind("<Leave>", lambda e: botao.config(bg=cor_base))

        btn_adicionar = tk.Button(frame_esquerdo, text="➕ Adicionar / Salvar", command=self.salvar_livro)
        btn_adicionar.grid(row=16, column=0, sticky="ew", padx=5, pady=(10,5))
        estilizar_botao(btn_adicionar, "#4CAF50")

        btn_editar = tk.Button(frame_esquerdo, text="✏️ Editar", command=self.carregar_para_edicao)
        btn_editar.grid(row=17, column=0, sticky="ew", padx=5, pady=5)
        estilizar_botao(btn_editar, "#FFD700")

        btn_excluir = tk.Button(frame_esquerdo, text="❌ Excluir", command=self.excluir_livro)
        btn_excluir.grid(row=18, column=0, sticky="ew", padx=5, pady=(5,10))
        estilizar_botao(btn_excluir, "#E53935")


        # --- LADO DIREITO ---
        frame_direito = tk.Frame(frame_conteudo, bg="#f0f0f0")
        frame_direito.place(relx=0.32, rely=0.03, relwidth=0.66, relheight=0.94)

        frame_pesquisa = tk.Frame(frame_direito, bg="white", bd=2, relief="groove")
        frame_pesquisa.place(relx=0.3, rely=0.04, relwidth=0.4, relheight=0.07)

        caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupa2.0.png')
        imagem_lupa = Image.open(caminho_imagem_lupa).resize((20, 20))
        self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
        tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg="white").pack(side="left", padx=5)

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12), bg="white", bd=0)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...")
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_livros)

        # --- TABELA ---
        frame_tabela = tk.Frame(frame_direito, bg="#ffffff", highlightbackground="#bbb", highlightthickness=1)
        frame_tabela.place(relx=0.01, rely=0.15, relwidth=0.98, relheight=0.83)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "ISBN", "Título", "Autor(es)", "Editora", "Ano",
                    "Categoria/Gênero", "Nº de páginas", "Preço"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # --- Cabeçalhos e larguras iniciais (sem for) ---
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.column("ID", anchor="center", width=40)

        self.tree.heading("ISBN", text="ISBN", anchor="center")
        self.tree.column("ISBN", anchor="center", width=65)

        self.tree.heading("Título", text="Título", anchor="center")
        self.tree.column("Título", anchor="center", width=120)

        self.tree.heading("Autor(es)", text="Autor(es)", anchor="center")
        self.tree.column("Autor(es)", anchor="center", width=120)

        self.tree.heading("Editora", text="Editora", anchor="center")
        self.tree.column("Editora", anchor="center", width=100)

        self.tree.heading("Ano", text="Ano", anchor="center")
        self.tree.column("Ano", anchor="center", width=50)

        self.tree.heading("Categoria/Gênero", text="Categoria/Gênero", anchor="center")
        self.tree.column("Categoria/Gênero", anchor="center", width=125)

        self.tree.heading("Nº de páginas", text="Nº de páginas", anchor="center")
        self.tree.column("Nº de páginas", anchor="center", width=80)

        self.tree.heading("Preço", text="Preço", anchor="center")
        self.tree.column("Preço", anchor="center", width=80)

        # Empacotar a tabela
        self.tree.pack(fill="both", expand=True)

        # --- Ajuste automático proporcional das colunas ---
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            proporcoes = {
                "ID": 40/845,
                "ISBN": 65/845,
                "Título": 120/845,
                "Autor(es)": 120/845,
                "Editora": 100/845,
                "Ano": 50/845,
                "Categoria/Gênero": 125/845,
                "Nº de páginas": 80/845,
                "Preço": 80/845
            }
            self.tree.column("ID", width=int(largura_total * proporcoes["ID"]))
            self.tree.column("ISBN", width=int(largura_total * proporcoes["ISBN"]))
            self.tree.column("Título", width=int(largura_total * proporcoes["Título"]))
            self.tree.column("Autor(es)", width=int(largura_total * proporcoes["Autor(es)"]))
            self.tree.column("Editora", width=int(largura_total * proporcoes["Editora"]))
            self.tree.column("Ano", width=int(largura_total * proporcoes["Ano"]))
            self.tree.column("Categoria/Gênero", width=int(largura_total * proporcoes["Categoria/Gênero"]))
            self.tree.column("Nº de páginas", width=int(largura_total * proporcoes["Nº de páginas"]))
            self.tree.column("Preço", width=int(largura_total * proporcoes["Preço"]))

        self.tree.bind("<Configure>", ajustar_largura_colunas)


    # ---------- FUNÇÕES ----------
    def voltar_lobby(self):
        self.frame_livros.pack_forget()
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.destroy()
            self.janela_ajuda = None
        abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)

    def ir_para_auditoria(self):
        self.frame_livros.pack_forget()
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.destroy()
            self.janela_ajuda = None
        abrir_tela_auditoria(self.master, self.db, self.frame_livros, self.usuario_logado)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Gerenciador de Livros")
        self.janela_ajuda.configure(bg="#f9f9f9")

        largura = 500
        altura = 350
        pos_x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (largura // 2)
        pos_y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (altura // 2)
        self.janela_ajuda.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        self.janela_ajuda.resizable(False, False)

        frame_container = tk.Frame(self.janela_ajuda, bg="#f9f9f9")
        frame_container.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(frame_container, bg="#f9f9f9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)
        frame_conteudo = tk.Frame(canvas, bg="#f9f9f9")

        frame_conteudo.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_conteudo, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        texto = (
            "📘 AJUDA - Gerenciador de Livros\n\n"
            "Aqui você pode gerenciar seus livros de forma simples e intuitiva.\n\n"
            "➕ Adicionar / Salvar: Preencha os campos e clique em 'Adicionar / Salvar'.\n"
            "✏️ Editar: Selecione um item e clique em 'Editar', depois 'Salvar'.\n"
            "❌ Excluir: Selecione uma linha da tabela e clique em 'Excluir'.\n"
            "🔍 Pesquisar: Digite qualquer termo para filtrar os resultados.\n"
            "📜 Histórico: Acompanhe ações no log de auditoria.\n"
            "🏠 Lobby: Retorna ao menu principal.\n"
            "💡 Dica: Passe o mouse sobre os botões para ver o destaque.\n"
            "────────────────────────────────────────\n"
            "© Data Flow - Sistema de Gerenciamento de Dados"
        )

        label_texto = tk.Label(frame_conteudo, text=texto, bg="#f9f9f9", fg="#333",
                               justify="left", font=("Helvetica", 12), wraplength=460, anchor="nw")
        label_texto.pack(fill="both", expand=True, padx=10, pady=10)

        btn_fechar = tk.Button(self.janela_ajuda, text="Fechar", bg="#0E80F0", fg="white",
                               font=("Helvetica", 11, "bold"), relief="raised", padx=20, pady=6,
                               command=self.janela_ajuda.destroy, cursor="hand2")
        btn_fechar.pack(pady=(0, 10))

        def ao_fechar():
            self.janela_ajuda.destroy()
            self.janela_ajuda = None

        self.janela_ajuda.protocol("WM_DELETE_WINDOW", ao_fechar)

    # ---------- CRUD ----------
    def salvar_livro(self):
        dados = {campo: entry.get().strip() for campo, entry in self.entries.items()}
        for campo, placeholder in self.placeholders.items():
            if dados[campo] == placeholder:
                dados[campo] = ""

        obrigatorios = ["ISBN", "Título", "Autor(es)", "Editora"]
        for campo in obrigatorios:
            if not dados[campo]:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
                return

        try:
            ano = int(dados["Ano de publicação"]) if dados["Ano de publicação"] else 0
            num_paginas = int(dados["Nº de páginas"]) if dados["Nº de páginas"] else 0
            preco = float(dados["Preço"].replace(",", ".")) if dados["Preço"] else 0.0
        except ValueError:
            messagebox.showwarning("Aviso", "Digite valores válidos para Ano, Nº de páginas e Preço!")
            return

        self.db.salvar_livro(self.livro_atual_id, dados["ISBN"], dados["Título"], dados["Autor(es)"],
                             dados["Editora"], ano, dados.get("Categoria/Gênero", ""), num_paginas,
                             preco, self.usuario_logado)

        messagebox.showinfo("Sucesso", "Livro atualizado!" if self.livro_atual_id else "Livro adicionado!")
        self.livro_atual_id = None
        self.limpar_campos()
        self.carregar_livros()

        # Remove foco dos Entry após salvar
        self.frame_livros.focus_set()  # Move o foco para o frame neutro

    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um livro para editar!")
            return
        item = self.tree.item(selected_item)
        livro = item["values"]
        self.livro_atual_id = livro[0]

        campos = list(self.placeholders.keys())
        for i, campo in enumerate(campos):
            self.entries[campo].delete(0, tk.END)
            self.entries[campo].insert(0, livro[i+1])
            self.entries[campo].config(fg="black")

    def excluir_livro(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos um livro para excluir!")
            return
        confirmar = messagebox.askyesno("Confirmação", f"Excluir {len(selected_items)} registro(s)?")
        if confirmar:
            for item in selected_items:
                id_livro = self.tree.item(item)["values"][0]
                self.db.excluir_livro(id_livro, self.usuario_logado)
            messagebox.showinfo("Sucesso", "Registro(s) excluído(s) com sucesso!")
            self.carregar_livros()
            self.limpar_campos()

    def limpar_campos(self):
        for campo, entry in self.entries.items():
            entry.delete(0, tk.END)
            adicionar_placeholder(entry, self.placeholders[campo])
        self.livro_atual_id = None

    def carregar_livros(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        livros = self.db.consultar_livros()
        for livro in livros:
            self.tree.insert("", "end", values=livro)

    def filtrar_livros(self, event=None):
        termo = self.entry_pesquisa.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for livro in self.db.consultar_livros():
            if any(termo in str(valor).lower() for valor in livro):
                self.tree.insert("", "end", values=livro)

    def iniciar(self):
        self.frame_login.pack_forget()
        self.frame_livros.pack(fill="both", expand=True)
