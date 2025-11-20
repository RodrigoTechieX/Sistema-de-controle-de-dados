# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendprodutos import BancoDeDadosProdutos
from Auditoria import TelaAuditoria


def abrir_tela_auditoria(master, db, on_voltar_callback, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, on_voltar_callback, usuario_logado)
    ts.titulo_origem = "Data Flow - Produtos"
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


class TelaProdutos:
    ALTURA_NAVBAR = 0.10  # mesma abordagem relativa da TelaMusicas

    def __init__(self, master, frame_login, usuario_logado, on_voltar_callback=None):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.on_voltar_callback = on_voltar_callback
        self.master.title("Data Flow - Produtos")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosProdutos()

        # Paleta e estilo (mesma da TelaMusicas)
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

        self.frame_produtos = tk.Frame(master, bg=self._bg_main)
        self.frame_produtos.pack(fill="both", expand=True)

        self.produto_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

        self.placeholders = {
            "Nome do Produto": "Ex: Chocolate ao Leite",
            "Código SKU": "Ex: CHOCL-001",
            "Categoria": "Ex: Alimentos, Bebidas, Eletrônicos",
            "Fabricante": "Ex: Nestlé, Samsung, Apple",
            "Preço unitário": "Ex: 12.50",
            "Quantidade": "Ex: 50",
            "Localização do estoque": "Ex: Prateleira A3, Estoque 2",
            "Data de validade": "Ex: 12/05/2023"
        }

        self.setup_tela_produtos()
        self.carregar_produtos()

    def remover_foco(self):
        self.frame_produtos.focus_set()

    def setup_tela_produtos(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 10, "bold")
        diretorio_atual = os.path.dirname(__file__)

        # ---------- NAVBAR ----------
        frame_navbar = tk.Frame(self.frame_produtos, bg=self._bg_nav)
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        titulo = tk.Label(frame_navbar, text="Gerenciador de Produtos",
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
        frame_sidebar = tk.Frame(self.frame_produtos, bg=self._bg_nav)
        frame_sidebar.place(relx=0, rely=self.ALTURA_NAVBAR, relwidth=0.05, relheight=1 - self.ALTURA_NAVBAR)

        icones_sidebar = ["🏠", "📦", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg=self._bg_nav, fg=self._fg,
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=12, padx=4, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self._sidebar))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self._bg_nav))

        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_produtos, bg=self._bg_main)
        frame_conteudo.place(relx=0.05, rely=self.ALTURA_NAVBAR, relwidth=0.95, relheight=1 - self.ALTURA_NAVBAR)

        # --- LADO ESQUERDO (form) ---
        frame_esquerdo = tk.Frame(frame_conteudo, bg=self._panel, highlightbackground="#232B33", highlightthickness=1)
        frame_esquerdo.place(relx=0.02, rely=0.03, relwidth=0.28, relheight=0.94)
        frame_esquerdo.configure(bd=0)

        # Configura grid interno (exatamente como padrão Filmes/Séries para caber tudo)
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
        # Nome do Produto
        make_label(frame_esquerdo, "Nome do Produto", 0)
        entry_nome = make_entry(frame_esquerdo, 1)
        adicionar_placeholder(entry_nome, self.placeholders["Nome do Produto"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Nome do Produto"] = entry_nome

        # Código SKU
        make_label(frame_esquerdo, "Código SKU", 2)
        entry_sku = make_entry(frame_esquerdo, 3)
        adicionar_placeholder(entry_sku, self.placeholders["Código SKU"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Código SKU"] = entry_sku

        # Categoria
        make_label(frame_esquerdo, "Categoria", 4)
        entry_categoria = make_entry(frame_esquerdo, 5)
        adicionar_placeholder(entry_categoria, self.placeholders["Categoria"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Categoria"] = entry_categoria

        # Fabricante
        make_label(frame_esquerdo, "Fabricante", 6)
        entry_fabricante = make_entry(frame_esquerdo, 7)
        adicionar_placeholder(entry_fabricante, self.placeholders["Fabricante"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Fabricante"] = entry_fabricante

        # Preço unitário
        make_label(frame_esquerdo, "Preço unitário", 8)
        entry_preco = make_entry(frame_esquerdo, 9)
        adicionar_placeholder(entry_preco, self.placeholders["Preço unitário"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Preço unitário"] = entry_preco

        # Quantidade
        make_label(frame_esquerdo, "Quantidade", 10)
        entry_qtd = make_entry(frame_esquerdo, 11)
        adicionar_placeholder(entry_qtd, self.placeholders["Quantidade"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Quantidade"] = entry_qtd

        # Localização do estoque
        make_label(frame_esquerdo, "Localização do estoque", 12)
        entry_local = make_entry(frame_esquerdo, 13)
        adicionar_placeholder(entry_local, self.placeholders["Localização do estoque"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Localização do estoque"] = entry_local

        # Data de validade (agora garantidamente antes dos botões)
        make_label(frame_esquerdo, "Data de validade", 14)
        entry_validade = make_entry(frame_esquerdo, 15)
        adicionar_placeholder(entry_validade, self.placeholders["Data de validade"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Data de validade"] = entry_validade

        # ---------- BOTÕES (linhas 16-18, igual Filmes/Séries) ----------
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

        criar_botao(frame_esquerdo, "➕ Adicionar / Salvar", self.salvar_produto, self._green, 16)
        criar_botao(frame_esquerdo, "✏️ Editar", self.carregar_para_edicao, self._yellow, 17)
        criar_botao(frame_esquerdo, "❌ Excluir", self.excluir_produto, self._red, 18)

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
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_produtos)

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
        estilo.configure("Produtos.Treeview",
                         background=self._panel,
                         foreground=self._fg,
                         fieldbackground=self._panel,
                         rowheight=26,
                         font=("Helvetica", 10))
        estilo.configure("Produtos.Treeview.Heading",
                         background=self._card,
                         foreground=self._accent,
                         font=("Helvetica", 11, "bold"))
        estilo.map("Produtos.Treeview", background=[("selected", self._accent)], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Nome", "SKU", "Categoria", "Fabricante",
                     "Preço unit", "Quantidade", "Localização", "Data de validade"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Produtos.Treeview",
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
                "ID": 40/880,
                "Nome": 100/880,
                "SKU": 60/880,
                "Categoria": 100/880,
                "Fabricante": 100/880,
                "Preço unit": 90/880,
                "Quantidade": 80/880,
                "Localização": 90/880,
                "Data de validade": 100/880
            }
            for k, v in proporcoes.items():
                self.tree.column(k, width=int(largura_total * v))

        self.tree.bind("<Configure>", ajustar_largura_colunas)

    # ---------- FUNÇÕES CRUD E NAVEGAÇÃO ----------
    def ir_para_auditoria(self):
        self.frame_produtos.pack_forget()
        abrir_tela_auditoria(
            self.master, 
            self.db, 
            on_voltar_callback=self.recarregar_tela,  # callback
            usuario_logado=self.usuario_logado
        )

    def recarregar_tela(self):
        self.frame_produtos.pack(fill="both", expand=True)
        self.carregar_produtos()
        self.limpar_campos()


    def voltar_lobby(self):
        # Esconde a tela atual
        try:
            self.frame_produtos.pack_forget()
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


    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Produtos")
        self.janela_ajuda.configure(bg=self._bg_main)

        largura, altura = 520, 420
        x = (self.janela_ajuda.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela_ajuda.winfo_screenheight() // 2) - (altura // 2)
        self.janela_ajuda.geometry(f"{largura}x{altura}+{x}+{y}")

        lbl_titulo = tk.Label(self.janela_ajuda, text="Ajuda - Gerenciador de Produtos",
                              bg=self._bg_main, fg=self._accent, font=("Helvetica", 14, "bold"))
        lbl_titulo.pack(pady=12)

        texto_ajuda = (
            "📦 ADICIONAR PRODUTO(S):\n"
            "Preencha os campos obrigatórios e clique em 'Adicionar / Salvar'.\n\n"
            "🔧 EDITAR PRODUTO(S):\n"
            "Selecione uma linha na tabela e clique em 'Editar'.\n"
            "Altere os campos e clique em 'Adicionar / Salvar'.\n\n"
            "❌ EXCLUIR PRODUTO(S):\n"
            "Selecione uma ou mais linhas e clique em 'Excluir'.\n\n"
            "🔍 PESQUISAR:\n"
            "Digite no campo de pesquisa para filtrar os produtos em tempo real.\n\n"
            "🕓 AUDITORIA:\n"
            "Acompanhe todas as ações feitas pelos usuários.\n\n"
            "⬅️ VOLTAR:\n"
            "Use o botão '🏠' para retornar ao Lobby."
        )
        lbl_texto = tk.Label(self.janela_ajuda, text=texto_ajuda, bg=self._bg_main,
                             fg=self._fg, font=("Helvetica", 11), justify="left")
        lbl_texto.pack(padx=20, pady=10, fill="both", expand=True)

    def salvar_produto(self):
        dados = {campo: entry.get().strip() for campo, entry in self.entries_map.items()}

        obrigatorios = ["Nome do Produto", "Código SKU", "Categoria", "Fabricante"]
        for campo in obrigatorios:
            if not dados[campo] or dados[campo] == self.placeholders[campo]:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
                return

        try:
            preco = float(dados["Preço unitário"].replace(",", ".")) if dados["Preço unitário"] != self.placeholders["Preço unitário"] else 0.0
        except ValueError:
            messagebox.showwarning("Aviso", "Digite um preço válido!")
            return

        try:
            quantidade = int(dados["Quantidade"]) if dados["Quantidade"] != self.placeholders["Quantidade"] else 0
        except ValueError:
            messagebox.showwarning("Aviso", "Digite uma quantidade válida!")
            return

        self.db.salvar_produto(
            self.produto_atual_id,
            dados["Nome do Produto"], dados["Código SKU"], dados["Categoria"], dados["Fabricante"],
            preco, quantidade, dados.get("Localização do estoque", ""), dados.get("Data de validade", ""),
            self.usuario_logado
        )

        if self.produto_atual_id:
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            self.produto_atual_id = None
        else:
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")

        self.limpar_campos()
        self.carregar_produtos()
        self.remover_foco()

    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um produto para editar!")
            return

        item = self.tree.item(selected_item)
        produto = item["values"]
        self.produto_atual_id = produto[0]

        campos = list(self.placeholders.keys())
        for i, campo in enumerate(campos):
            entry = self.entries_map[campo]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, produto[i + 1])
            entry.config(fg=self._fg)
        self.remover_foco()

    def excluir_produto(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos um produto para excluir!")
            return

        confirmar = messagebox.askyesno("Confirmação", f"Excluir {len(selected_items)} produto(s)?")
        if confirmar:
            for item in selected_items:
                id_produto = self.tree.item(item)["values"][0]
                self.db.excluir_produto(id_produto, self.usuario_logado)
            messagebox.showinfo("Sucesso", "Produto(s) excluído(s) com sucesso!")
            self.carregar_produtos()
            self.remover_foco()

    def limpar_campos(self):
        for campo, entry in self.entries_map.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            adicionar_placeholder(entry, self.placeholders[campo], fg_placeholder=self._muted, fg_text=self._fg)
        self.produto_atual_id = None

    def carregar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        produtos = self.db.consultar_produtos()
        toggle = 0
        for produto in produtos:
            tag = 'evenrow' if toggle % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=produto, tags=(tag,))
            toggle += 1

    def filtrar_produtos(self, event):
        filtro = self.entry_pesquisa.get().lower().strip()
        if filtro == "" or filtro == "digite para pesquisar...":
            self.carregar_produtos()
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        produtos_filtrados = self.db.pesquisar_produtos(filtro)
        toggle = 0
        for produto in produtos_filtrados:
            tag = 'evenrow' if toggle % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=produto, tags=(tag,))
            toggle += 1

