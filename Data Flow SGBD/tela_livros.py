# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendlivros import BancoDeDadosLivros
from Auditoria import TelaAuditoria


def abrir_tela_auditoria(master, db, on_voltar_callback, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, on_voltar_callback, usuario_logado)
    ts.titulo_origem = "Data Flow - Livros"  # título correto ao voltar
    ts.iniciar()


def abrir_tela_principal(master, db, frame_login, usuario_logado):
    from Lobby import TelaPrincipal
    ts = TelaPrincipal(master, db, frame_login, usuario_logado)
    ts.iniciar()


def adicionar_placeholder(entry, placeholder_text, fg_placeholder="#9BA9B6", fg_text="#E6F5FF"):
    """Configura placeholder no estilo tema escuro (desaparece ao focar e reaparece ao desfocar)."""
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg=fg_text)

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(fg=fg_placeholder)

    entry.insert(0, placeholder_text)
    entry.config(fg=fg_placeholder)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


class TelaLivros:
    ALTURA_NAVBAR = 0.10  # mesma abordagem relativa

    def __init__(self, master, frame_login, usuario_logado, on_voltar_callback=None):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.on_voltar_callback = on_voltar_callback 
        self.master.title("Data Flow - Livros")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosLivros()

        # Paleta e estilo (igual ao código de Filmes e Séries)
        self._sidebar = "#007C91"
        self._bg_main = "#0F1518"
        self._bg_nav = "#21252B"
        self._panel = "#0F171A"
        self._card = "#131A20"
        self._fg = "#E6F5FF"
        self._muted = "#9BA9B6"
        self._accent = "#007ACC"
        self._accent_hover = "#009EFF"
        self._green = "#00B050"
        self._red = "#D9534F"
        self._yellow = "#FFD54A"

        self.frame_livros = tk.Frame(master, bg=self._bg_main)
        self.frame_livros.pack(fill="both", expand=True)

        self.livro_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

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
        frame_navbar = tk.Frame(self.frame_livros, bg=self._bg_nav)
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        titulo = tk.Label(frame_navbar,
                          text="Gerenciador de Livros",
                          font=("Helvetica", 14, "bold"),
                          fg=self._accent, bg=self._bg_nav)
        titulo.place(relx=0.5, rely=0.5, anchor="center")

        caminho_imagem_usuario = os.path.join(diretorio_atual, "imagens", "usuariosistema.png")
        try:
            imagem_usuario = Image.open(caminho_imagem_usuario).resize((18, 18), Image.LANCZOS)
            self.icone_usuario = ImageTk.PhotoImage(imagem_usuario)
        except Exception:
            self.icone_usuario = None

        label_usuario = tk.Label(frame_navbar, text=f"{self.usuario_logado}",
                                 font=("Helvetica", 11, "bold"),
                                 bg=self._bg_nav, fg=self._fg,
                                 image=self.icone_usuario, compound="left", padx=6)
        label_usuario.place(relx=0.98, rely=0.5, anchor="e")

        # ---------- SIDEBAR ----------
        frame_sidebar = tk.Frame(self.frame_livros, bg=self._bg_nav)
        frame_sidebar.place(relx=0, rely=self.ALTURA_NAVBAR, relwidth=0.05, relheight=1 - self.ALTURA_NAVBAR)

        icones_sidebar = ["🏠", "📚", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg=self._bg_nav, fg=self._fg,
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=12, padx=4, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self._sidebar))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self._bg_nav))

        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_livros, bg=self._bg_main)
        frame_conteudo.place(relx=0.05, rely=self.ALTURA_NAVBAR, relwidth=0.95, relheight=1 - self.ALTURA_NAVBAR)

        # --- LADO ESQUERDO (form) ---
        frame_esquerdo = tk.Frame(frame_conteudo, bg=self._panel, highlightbackground="#232B33", highlightthickness=1)
        frame_esquerdo.place(relx=0.02, rely=0.03, relwidth=0.28, relheight=0.94)
        frame_esquerdo.configure(bd=0)

        # Configura grid interno
        for i in range(20):
            frame_esquerdo.rowconfigure(i, weight=1)
        frame_esquerdo.columnconfigure(0, weight=1)

        def make_label(frame, text, row):
            lbl = tk.Label(frame, text=text, font=label_font, bg=self._panel, fg=self._fg, anchor="w")
            lbl.grid(row=row, column=0, sticky="ew", padx=12)
            return lbl

        def make_entry(frame, row, pady=(0, 8)):
            ent = tk.Entry(frame, font=entry_font, bg=self._bg_main, fg=self._fg, bd=0, insertbackground=self._fg)
            ent.grid(row=row, column=0, sticky="ew", padx=12, pady=pady)
            ent.config(relief="flat")
            wrapper = tk.Frame(frame, bg=self._card, height=28)
            wrapper.place(in_=ent, relx=0, rely=0, relwidth=1, relheight=1)
            wrapper.lower(ent)
            return ent

        # ORGANIZAÇÃO VERTICAL (labels em linhas pares, entries em linhas ímpares)
        # ISBN
        make_label(frame_esquerdo, "ISBN:", 0)
        entry_isbn = make_entry(frame_esquerdo, 1)
        adicionar_placeholder(entry_isbn, self.placeholders["ISBN"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["ISBN"] = entry_isbn

        # Título
        make_label(frame_esquerdo, "Título:", 2)
        entry_titulo = make_entry(frame_esquerdo, 3)
        adicionar_placeholder(entry_titulo, self.placeholders["Título"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Título"] = entry_titulo

        # Autor(es)
        make_label(frame_esquerdo, "Autor(es):", 4)
        entry_autor = make_entry(frame_esquerdo, 5)
        adicionar_placeholder(entry_autor, self.placeholders["Autor(es)"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Autor(es)"] = entry_autor

        # Editora
        make_label(frame_esquerdo, "Editora:", 6)
        entry_editora = make_entry(frame_esquerdo, 7)
        adicionar_placeholder(entry_editora, self.placeholders["Editora"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Editora"] = entry_editora

        # Ano de publicação
        make_label(frame_esquerdo, "Ano de publicação:", 8)
        entry_ano = make_entry(frame_esquerdo, 9)
        adicionar_placeholder(entry_ano, self.placeholders["Ano de publicação"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Ano de publicação"] = entry_ano

        # Categoria/Gênero
        make_label(frame_esquerdo, "Categoria/Gênero:", 10)
        entry_categoria = make_entry(frame_esquerdo, 11)
        adicionar_placeholder(entry_categoria, self.placeholders["Categoria/Gênero"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Categoria/Gênero"] = entry_categoria

        # Nº de páginas
        make_label(frame_esquerdo, "Nº de páginas:", 12)
        entry_paginas = make_entry(frame_esquerdo, 13)
        adicionar_placeholder(entry_paginas, self.placeholders["Nº de páginas"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Nº de páginas"] = entry_paginas

        # Preço
        make_label(frame_esquerdo, "Preço:", 14)
        entry_preco = make_entry(frame_esquerdo, 15)
        adicionar_placeholder(entry_preco, self.placeholders["Preço"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Preço"] = entry_preco

        # ---------- BOTÕES ----------
        def criar_botao(frame, texto, comando, bg_color, row):
            btn = tk.Button(frame, text=texto, command=comando,
                            bg=bg_color, fg="white", font=button_font, bd=0, relief="flat", cursor="hand2")
            btn.grid(row=row, column=0, sticky="ew", padx=18, pady=(6, 6))
            btn.bind("<Enter>", lambda e, b=btn, c=bg_color: b.config(bg=self._accent_hover if bg_color == self._accent else
                                                                       "#d8be16" if bg_color == self._yellow else
                                                                       "#038633" if bg_color == self._green else
                                                                       "#b22b2b" if bg_color == self._red else self._accent_hover))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=bg_color))
            return btn

        criar_botao(frame_esquerdo, "➕ Adicionar / Salvar", self.salvar_livro, self._green, 17)
        criar_botao(frame_esquerdo, "✏️ Editar", self.carregar_para_edicao, self._yellow, 18)
        criar_botao(frame_esquerdo, "❌ Excluir", self.excluir_livro, self._red, 19)

        # --- LADO DIREITO ---
        frame_direito = tk.Frame(frame_conteudo, bg=self._bg_main)
        frame_direito.place(relx=0.32, rely=0.03, relwidth=0.66, relheight=0.94)

        # Pesquisa
        frame_pesquisa = tk.Frame(frame_direito, bg=self._card, bd=0)
        frame_pesquisa.place(relx=0.03, rely=0.02, relwidth=0.64, relheight=0.07)

        caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupabranca.png')
        try:
            imagem_lupa = Image.open(caminho_imagem_lupa).resize((20, 20), Image.LANCZOS)
            self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
            tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg=self._card).pack(side="left", padx=8)
        except Exception:
            tk.Label(frame_pesquisa, text="🔍", bg=self._card, fg=self._muted).pack(side="left", padx=8)

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12),
                                       bg=self._card, fg=self._muted, bd=0, insertbackground=self._fg)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=8, pady=6)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...", fg_placeholder=self._muted, fg_text=self._fg)
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_livros)

        # --- TABELA ---
        frame_tabela = tk.Frame(frame_direito, bg=self._panel, highlightbackground="#232B33", highlightthickness=1)
        frame_tabela.place(relx=0.01, rely=0.12, relwidth=0.98, relheight=0.83)

        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar_y.pack(side="right", fill="y", padx=(0, 6), pady=6)

        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except Exception:
            pass
        estilo.configure("Livros.Treeview",
                         background=self._panel,
                         foreground=self._fg,
                         fieldbackground=self._panel,
                         rowheight=26,
                         font=("Helvetica", 10))
        estilo.configure("Livros.Treeview.Heading",
                         background=self._card,
                         foreground=self._accent,
                         font=("Helvetica", 11, "bold"))
        estilo.map("Livros.Treeview", background=[("selected", self._accent)], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "ISBN", "Título", "Autor(es)", "Editora", "Ano de publicação", "Categoria/Gênero", "Nº de páginas", "Preço"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Livros.Treeview",
            selectmode="extended"
        )
        scrollbar_y.config(command=self.tree.yview)

        self.tree.tag_configure('oddrow', background=self._panel)
        self.tree.tag_configure('evenrow', background=self._card)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=100, stretch=True)

        self.tree.pack(fill="both", expand=True, padx=6, pady=6)

        # Ajuste proporcional das colunas
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            proporcoes = {
                "ID": 40/845,
                "ISBN": 65/845,
                "Título": 120/845,
                "Autor(es)": 120/845,
                "Editora": 100/845,
                "Ano de publicação": 80/845,
                "Categoria/Gênero": 125/845,
                "Nº de páginas": 80/845,
                "Preço": 80/845
            }
            for k, v in proporcoes.items():
                self.tree.column(k, width=int(largura_total * v))

        self.tree.bind("<Configure>", ajustar_largura_colunas)


    # ---------- FUNÇÕES ----------
    def voltar_lobby(self):
        # Esconde a tela atual
        try:
            self.frame_livros.pack_forget()
        except Exception:
            pass

        # Se houver callback passado pelo Lobby, chame-o (rápido — só reexibe o lobby já criado)
        if getattr(self, "on_voltar_callback", None):
            try:
                self.on_voltar_callback()
                return
            except Exception as e:
                print(f"Erro ao chamar on_voltar_callback: {e}")

        # Fallback: se não tiver callback, cria uma nova TelaPrincipal (comportamento antigo)
        try:
            abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)
        except Exception as e:
            print(f"Erro ao abrir Lobby fallback: {e}")


    def ir_para_auditoria(self):
        self.frame_livros.pack_forget()
        abrir_tela_auditoria(
            self.master, 
            self.db, 
            on_voltar_callback=self.recarregar_tela,  # callback
            usuario_logado=self.usuario_logado
        )

    def recarregar_tela(self):
        self.frame_livros.pack(fill="both", expand=True)
        self.carregar_livros()
        self.limpar_campos()


    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Livros")
        self.janela_ajuda.configure(bg=self._bg_main)

        largura, altura = 520, 420
        x = (self.janela_ajuda.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela_ajuda.winfo_screenheight() // 2) - (altura // 2)
        self.janela_ajuda.geometry(f"{largura}x{altura}+{x}+{y}")

        lbl_titulo = tk.Label(self.janela_ajuda, text="Ajuda - Gerenciador de Livros",
                              bg=self._bg_main, fg=self._accent, font=("Helvetica", 14, "bold"))
        lbl_titulo.pack(pady=12)

        texto_ajuda = (
            "📚 ADICIONAR LIVRO(S):\n"
            "Preencha os campos obrigatórios e clique em 'Adicionar / Salvar'.\n\n"
            "🔧 EDITAR LIVRO(S):\n"
            "Selecione uma linha na tabela e clique em 'Editar'.\n"
            "Altere os campos e clique em 'Adicionar / Salvar'.\n\n"
            "❌ EXCLUIR LIVRO(S):\n"
            "Selecione uma ou mais linhas e clique em 'Excluir'.\n\n"
            "🔍 PESQUISAR:\n"
            "Digite no campo de pesquisa para filtrar os livros em tempo real.\n\n"
            "🕓 HISTÓRICO:\n"
            "Acompanhe todas as ações feitas pelos usuários.\n\n"
            "⬅️ VOLTAR:\n"
            "Use o botão '🏠' para retornar ao Lobby."
        )
        lbl_texto = tk.Label(self.janela_ajuda, text=texto_ajuda, bg=self._bg_main,
                             fg=self._fg, font=("Helvetica", 11), justify="left")
        lbl_texto.pack(padx=20, pady=10, fill="both", expand=True)

    # ---------- CRUD ----------
    def salvar_livro(self):
        dados = {campo: entry.get().strip() for campo, entry in self.entries_map.items()}
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
            self.entries_map[campo].delete(0, tk.END)
            self.entries_map[campo].insert(0, livro[i+1])
            self.entries_map[campo].config(fg="white")

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
        for campo, entry in self.entries_map.items():
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
