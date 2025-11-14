# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendreceitas import BancoDeDadosReceitas


def abrir_tela_auditoria(master, db, frame_receitas, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, frame_receitas, usuario_logado)
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


class TelaReceitas:
    ALTURA_NAVBAR = 60

    def __init__(self, master, frame_login, usuario_logado):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.master.title("Data Flow - Gerenciamento de Receitas")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosReceitas()

        self.frame_receitas = tk.Frame(master)
        self.frame_receitas.pack(fill="both", expand=True)

        self.receita_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

        self.placeholders = {
            "Nome da Receita:": "Ex.: Bolo de Cenoura",
            "Criador/Autor:": "Ex.: João da Silva",
            "Categoria:": "Ex.: Sobremesa",
            "Tempo de preparo (min):": "Ex.: 60",
            "Número de porções:": "Ex.: 8",
            "Ingredientes:": "Ex.: Cenoura, farinha, açúcar, ovos",
            "Modo de preparo:": "Ex.: Misture os ingredientes e asse"
        }

        self.setup_tela_receitas()
        self.carregar_receitas()

    def remover_foco(self):
        """Remove o foco de todos os Entry, colocando em um widget neutro."""
        self.frame_receitas.focus_set()  # Ou use self.master.focus() se preferir

    def setup_tela_receitas(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)

# ---------- NAVBAR ----------
        self.ALTURA_NAVBAR = 0.10  # Altura relativa (10% da tela)
        frame_navbar = tk.Frame(self.frame_receitas, bg="#1F222B")
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        # Configura grid interno (opcional, para alinhamento)
        frame_navbar.columnconfigure(0, weight=1)
        frame_navbar.columnconfigure(1, weight=1)
        frame_navbar.columnconfigure(2, weight=1)

        # Título centralizado
        titulo = tk.Label(frame_navbar,
                        text="Gerenciador de Receitas",
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
        frame_sidebar = tk.Frame(self.frame_receitas, bg="#1F222B")
        frame_sidebar.place(relx=0, rely=0.09, relwidth=0.05, relheight=0.96)

        icones_sidebar = ["🏠", "👨🏼‍🍳", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg="#1F222B", fg="white",
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=15, padx=5, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#003366"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1F222B"))


        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_receitas, bg="#eaeaea")
        frame_conteudo.place(relx=0.05, rely=0.08, relwidth=0.95, relheight=0.92)
        
        # --- LADO ESQUERDO ---
        frame_esquerdo = tk.Frame(frame_conteudo, bg="#f7f7f7", highlightbackground="#ccc", highlightthickness=1)
        frame_esquerdo.place(relx=0.02, rely=0.03, relwidth=0.28, relheight=0.94)
        frame_esquerdo.configure(bd=2, relief="groove")

        sombra = tk.Frame(frame_conteudo, bg="#d0d0d0")
        sombra.place(relx=0.023, rely=0.036, relwidth=0.28, relheight=0.94)

        frame_esquerdo.lift()

        # ---------- GRID CONFIG ----------
        frame_esquerdo.columnconfigure(0, weight=1)
        frame_esquerdo.columnconfigure(1, weight=3)
        for i in range(20):
            frame_esquerdo.rowconfigure(i, weight=1)

        # ---------- CAMPOS ----------
        lbl_nome = tk.Label(frame_esquerdo, text="Nome da Receita:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_nome.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_nome = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_nome.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_nome, self.placeholders["Nome da Receita:"])
        self.entries_map["Nome da Receita:"] = entry_nome

        lbl_criador = tk.Label(frame_esquerdo, text="Criador/Autor:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_criador.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_criador = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_criador.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_criador, self.placeholders["Criador/Autor:"])
        self.entries_map["Criador/Autor:"] = entry_criador

        lbl_categoria = tk.Label(frame_esquerdo, text="Categoria:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_categoria.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_categoria = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_categoria.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_categoria, self.placeholders["Categoria:"])
        self.entries_map["Categoria:"] = entry_categoria

        lbl_tempo = tk.Label(frame_esquerdo, text="Tempo de preparo (min):", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_tempo.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_tempo = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_tempo.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_tempo, self.placeholders["Tempo de preparo (min):"])
        self.entries_map["Tempo de preparo (min):"] = entry_tempo

        lbl_porcoes = tk.Label(frame_esquerdo, text="Número de porções:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_porcoes.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_porcoes = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_porcoes.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_porcoes, self.placeholders["Número de porções:"])
        self.entries_map["Número de porções:"] = entry_porcoes

        lbl_ingredientes = tk.Label(frame_esquerdo, text="Ingredientes:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_ingredientes.grid(row=10, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_ingredientes = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_ingredientes.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_ingredientes, self.placeholders["Ingredientes:"])
        self.entries_map["Ingredientes:"] = entry_ingredientes

        lbl_modo = tk.Label(frame_esquerdo, text="Modo de preparo:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_modo.grid(row=12, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_modo = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_modo.grid(row=13, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_modo, self.placeholders["Modo de preparo:"])
        self.entries_map["Modo de preparo:"] = entry_modo

        # ---------- BOTÕES CRUD ----------
        def estilizar_botao(botao, cor_base, hover_cor="#bcbcbc"):
            botao.config(bg=cor_base, fg="black", relief="flat", font=button_font, bd=0, cursor="hand2")
            botao.bind("<Enter>", lambda e: botao.config(bg=hover_cor))
            botao.bind("<Leave>", lambda e: botao.config(bg=cor_base))

        btn_adicionar = tk.Button(frame_esquerdo, text="➕ Adicionar / Salvar", command=self.salvar_receita)
        btn_adicionar.grid(row=15, column=0, columnspan=2, sticky="ew", padx=30, pady=(20, 5))
        estilizar_botao(btn_adicionar, "#4CAF50", hover_cor="#2E7D32")

        btn_editar = tk.Button(frame_esquerdo, text="✏️ Editar", command=self.carregar_para_edicao)
        btn_editar.grid(row=16, column=0, columnspan=2, sticky="ew", padx=30, pady=5)
        estilizar_botao(btn_editar, "#FFD700", hover_cor="#FBC02D")

        btn_excluir = tk.Button(frame_esquerdo, text="❌ Excluir", command=self.excluir_receita)
        btn_excluir.grid(row=17, column=0, columnspan=2, sticky="ew", padx=30, pady=5)
        estilizar_botao(btn_excluir, "#E53935", hover_cor="#C62828")


        # --- LADO DIREITO ---
        frame_direito = tk.Frame(frame_conteudo, bg="#f0f0f0")
        frame_direito.place(relx=0.32, rely=0.03, relwidth=0.66, relheight=0.94)

        # Barra de pesquisa (mesmo estilo)
        frame_pesquisa = tk.Frame(frame_direito, bg="white", bd=2, relief="groove")
        frame_pesquisa.place(relx=0.3, rely=0.04, relwidth=0.4, relheight=0.07)

        caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupa2.0.png')
        try:
            imagem_lupa = Image.open(caminho_imagem_lupa).resize((20, 20))
            self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
            tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg="white").pack(side="left", padx=5)
        except Exception:
            self.icone_pesquisa = None
            tk.Label(frame_pesquisa, text="🔍", bg="white").pack(side="left", padx=5)

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12), bg="white", bd=0)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...")
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_receitas)

        # --- TABELA ---
        frame_tabela = tk.Frame(frame_direito, bg="#ffffff", highlightbackground="#bbb", highlightthickness=1)
        frame_tabela.place(relx=0.01, rely=0.15, relwidth=0.98, relheight=0.83)

        # Sombra da tabela
        sombra_tabela = tk.Frame(frame_direito, bg="#d0d0d0")
        sombra_tabela.place(relx=0.013, rely=0.155, relwidth=0.98, relheight=0.83)
        frame_tabela.lift()

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Nome", "Criador/Autor", "Categoria",
                    "Tempo(min)", "Número de Porções", "Ingredientes", "Modo de Preparo"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # --- Cabeçalhos e larguras iniciais (sem for) ---
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.column("ID", anchor="center", width=40)

        self.tree.heading("Nome", text="Nome", anchor="center")
        self.tree.column("Nome", anchor="center", width=100)

        self.tree.heading("Criador/Autor", text="Criador/Autor", anchor="center")
        self.tree.column("Criador/Autor", anchor="center", width=110)

        self.tree.heading("Categoria", text="Categoria", anchor="center")
        self.tree.column("Categoria", anchor="center", width=90)

        self.tree.heading("Tempo(min)", text="Tempo(min)", anchor="center")
        self.tree.column("Tempo(min)", anchor="center", width=90)

        self.tree.heading("Número de Porções", text="Número de Porções", anchor="center")
        self.tree.column("Número de Porções", anchor="center", width=120)

        self.tree.heading("Ingredientes", text="Ingredientes", anchor="center")
        self.tree.column("Ingredientes", anchor="center", width=110)

        self.tree.heading("Modo de Preparo", text="Modo de Preparo", anchor="center")
        self.tree.column("Modo de Preparo", anchor="center", width=120)

        # Empacotar a tabela
        self.tree.pack(fill="both", expand=True)

        # --- Ajuste automático proporcional das colunas ---
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            proporcoes = {
                "ID": 40/880,
                "Nome": 100/880,
                "Criador/Autor": 110/880,
                "Categoria": 90/880,
                "Tempo(min)": 90/880,
                "Número de Porções": 120/880,
                "Ingredientes": 110/880,
                "Modo de Preparo": 120/880
            }
            self.tree.column("ID", width=int(largura_total * proporcoes["ID"]))
            self.tree.column("Nome", width=int(largura_total * proporcoes["Nome"]))
            self.tree.column("Criador/Autor", width=int(largura_total * proporcoes["Criador/Autor"]))
            self.tree.column("Categoria", width=int(largura_total * proporcoes["Categoria"]))
            self.tree.column("Tempo(min)", width=int(largura_total * proporcoes["Tempo(min)"]))
            self.tree.column("Número de Porções", width=int(largura_total * proporcoes["Número de Porções"]))
            self.tree.column("Ingredientes", width=int(largura_total * proporcoes["Ingredientes"]))
            self.tree.column("Modo de Preparo", width=int(largura_total * proporcoes["Modo de Preparo"]))

        self.tree.bind("<Configure>", ajustar_largura_colunas)


    # ---------- Funções CRUD e navegação ----------
    def voltar_lobby(self):
        self.frame_receitas.pack_forget()
        abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)

    def ir_para_auditoria(self):
        self.frame_receitas.pack_forget()
        abrir_tela_auditoria(self.master, self.db, self.frame_receitas, self.usuario_logado)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Receitas")
        self.janela_ajuda.configure(bg="#f9f9f9")

        largura, altura = 500, 350
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
            "📘 AJUDA - Gerenciador de Receitas\n\n"
            "Bem-vindo(a)! Aqui você pode **gerenciar suas Receitas** de forma simples e intuitiva.\n\n"
            "➕ Adicionar / Salvar: Preencha os campos e clique em **'Adicionar / Salvar'**.\n"
            "✏️ Editar: Selecione um item e clique em **'Editar'**, depois **'Salvar'**.\n"
            "❌ Excluir: Selecione uma linha na tabela e clique em **'Excluir'**.\n"
            "🔍 Pesquisar: Digite qualquer termo para filtrar os resultados.\n"
            "📜 Histórico: Acompanhe ações no log de auditoria.\n"
            "🏠 Lobby: Retorna ao menu principal.\n"
            "💡 Dica: Passe o mouse sobre os botões para ver o destaque.\n"
            "────────────────────────────────────────\n"
            "© Data Flow - Sistema de Gerenciamento de Dados"
        )
        label_texto = tk.Label(
            frame_conteudo, text=texto, bg="#f9f9f9", fg="#333",
            justify="left", font=("Helvetica", 12), wraplength=460, anchor="nw"
        )
        label_texto.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------- Botão fechar ----------
        btn_fechar = tk.Button(
            self.janela_ajuda, text="Fechar", bg="#0E80F0", fg="white",
            font=("Helvetica", 11, "bold"), relief="raised", padx=20, pady=6,
            command=self.janela_ajuda.destroy, cursor="hand2"
        )
        btn_fechar.pack(pady=(0, 10))

        # ---------- Fechar janela ----------
        def ao_fechar():
            self.janela_ajuda.destroy()
            self.janela_ajuda = None

        self.janela_ajuda.protocol("WM_DELETE_WINDOW", ao_fechar)

    # ---------- CRUD ----------
    def salvar_receita(self):
        dados = {campo: entry.get().strip() for campo, entry in self.entries_map.items()}
        # remover placeholders
        for campo in list(dados.keys()):
            if dados[campo] == self.placeholders.get(campo):
                dados[campo] = ""

        # checar obrigatórios (simples)
        obrigatorios = list(self.placeholders.keys())
        for campo in obrigatorios:
            if not dados[campo]:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
                return

        # validar inteiros
        try:
            tempo_preparo = int(dados["Tempo de preparo (min):"])
            num_porcoes = int(dados["Número de porções:"])
        except Exception:
            messagebox.showwarning("Aviso", "Digite números válidos para Tempo de Preparo e Número de Porções!")
            return

        # salvar no banco (preservando interface do seu backendreceitas)
        self.db.salvar_receita(
            self.receita_atual_id,
            dados["Nome da Receita:"], dados["Criador/Autor:"], dados["Categoria:"],
            tempo_preparo, num_porcoes, dados["Ingredientes:"], dados["Modo de preparo:"],
            usuario_logado=self.usuario_logado
        )

        if self.receita_atual_id:
            messagebox.showinfo("Sucesso", "Receita atualizada com sucesso!")
            self.receita_atual_id = None
        else:
            messagebox.showinfo("Sucesso", "Receita adicionada com sucesso!")

        self.limpar_campos()
        self.carregar_receitas()
        self.remover_foco()

    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma receita para editar!")
            return
        item = self.tree.item(selected_item)
        receita = item["values"]
        self.receita_atual_id = receita[0]

        # preencher campos (assume a ordem das colunas no tree)
        campos = list(self.placeholders.keys())
        for i, campo in enumerate(campos):
            valor = receita[i + 1] if len(receita) > i + 1 else ""
            entry = self.entries_map[campo]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, valor)
            entry.config(fg="black")
            self.remover_foco()

    def excluir_receita(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma receita para excluir!")
            return
        confirmar = messagebox.askyesno("Confirmação", f"Excluir {len(selected_items)} receita(s)?")
        if confirmar:
            for item in selected_items:
                id_receita = self.tree.item(item)["values"][0]
                self.db.excluir_receita(id_receita, usuario_logado=self.usuario_logado)
            messagebox.showinfo("Sucesso", "Receita(s) excluída(s) com sucesso!")
            self.carregar_receitas()
            self.limpar_campos()
            self.remover_foco()

    def limpar_campos(self):
        for campo, entry in self.entries_map.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            adicionar_placeholder(entry, self.placeholders[campo])
        self.receita_atual_id = None

    def carregar_receitas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        receitas = self.db.consultar_receitas()
        for receita in receitas:
            self.tree.insert("", "end", values=receita)

    def filtrar_receitas(self, event):
        filtro = self.entry_pesquisa.get().lower()
        if filtro == "digite para pesquisar...":
            filtro = ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        receitas_filtradas = self.db.pesquisar_receitas(filtro)
        for receita in receitas_filtradas:
            self.tree.insert("", "end", values=receita)
