# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendjogos import BancoDeDadosJogos


def abrir_tela_auditoria(master, db, frame_jogos, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, frame_jogos, usuario_logado)
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


class TelaJogos:
    ALTURA_NAVBAR = 60

    def __init__(self, master, frame_login, usuario_logado):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.master.title("Data Flow - Gerenciamento de Jogos")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosJogos()

        self.frame_jogos = tk.Frame(master)
        self.frame_jogos.pack(fill="both", expand=True)

        self.jogo_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

        self.placeholders = {
            "Nome do jogo": "Ex: The Last of Us",
            "Contexto": "Ex: Jogo de ação e sobrevivência em mundo pós-apocalíptico",
            "Desenvolvedora": "Ex: Naughty Dog",
            "Publicadora": "Ex: Sony Interactive Entertainment",
            "Ano de lançamento": "Ex: 2013",
            "Plataformas": "Ex: PlayStation 3, PlayStation 4, PlayStation 5",
            "Gênero": "Ex: Ação, Aventura, Survival Horror",
            "Classificação": "Ex: 18+"
        }

        self.setup_tela_jogos()
        self.carregar_jogos()

    def remover_foco(self):
        """Remove o foco de todos os Entry, colocando em um widget neutro."""
        self.frame_jogos.focus_set()

    def setup_tela_jogos(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)

        # ---------- NAVBAR ----------
        self.ALTURA_NAVBAR = 0.10  # Altura relativa (10% da tela)
        frame_navbar = tk.Frame(self.frame_jogos, bg="#1F222B")
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        # Título centralizado
        titulo = tk.Label(frame_navbar,
                          text="Gerenciador de Jogos",
                          font=("Helvetica", 14, "bold"),
                          fg="white", bg="#1F222B")
        titulo.place(relx=0.5, rely=0.45, anchor="center")

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
        label_usuario.place(relx=0.95, rely=0.45, anchor="e")

        # ---------- SIDEBAR ----------
        frame_sidebar = tk.Frame(self.frame_jogos, bg="#1F222B")
        frame_sidebar.place(relx=0, rely=0.09, relwidth=0.05, relheight=0.98)

        icones_sidebar = ["🏠", "🎮", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg="#1F222B", fg="white",
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=15, padx=5, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#003366"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1F222B"))

        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_jogos, bg="#eaeaea")
        frame_conteudo.place(relx=0.05, rely=0.08, relwidth=0.95, relheight=0.92)

        # --- LADO ESQUERDO ---
        frame_esquerdo = tk.Frame(frame_conteudo, bg="#f7f7f7", highlightbackground="#ccc", highlightthickness=1)
        frame_esquerdo.place(relx=0.02, rely=0.03, relwidth=0.28, relheight=0.94)
        frame_esquerdo.configure(bd=2, relief="groove")

        sombra = tk.Frame(frame_conteudo, bg="#d0d0d0")
        sombra.place(relx=0.023, rely=0.036, relwidth=0.28, relheight=0.94)
        frame_esquerdo.lift()

        # Grid interno
        for i in range(20):
            frame_esquerdo.rowconfigure(i, weight=1)
        frame_esquerdo.columnconfigure(0, weight=1)

        # ---------- CAMPOS ----------
        # Nome do jogo
        lbl_nome = tk.Label(frame_esquerdo, text="Nome do jogo", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_nome.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        entry_nome = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_nome.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_nome, self.placeholders["Nome do jogo"])
        self.entries_map["Nome do jogo"] = entry_nome

        # Contexto
        lbl_contexto = tk.Label(frame_esquerdo, text="Contexto", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_contexto.grid(row=2, column=0, sticky="ew", padx=10)
        entry_contexto = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_contexto.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_contexto, self.placeholders["Contexto"])
        self.entries_map["Contexto"] = entry_contexto

        # Desenvolvedora
        lbl_desenvolvedora = tk.Label(frame_esquerdo, text="Desenvolvedora", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_desenvolvedora.grid(row=4, column=0, sticky="ew", padx=10)
        entry_desenvolvedora = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_desenvolvedora.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_desenvolvedora, self.placeholders["Desenvolvedora"])
        self.entries_map["Desenvolvedora"] = entry_desenvolvedora

        # Publicadora
        lbl_publicadora = tk.Label(frame_esquerdo, text="Publicadora", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_publicadora.grid(row=6, column=0, sticky="ew", padx=10)
        entry_publicadora = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_publicadora.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_publicadora, self.placeholders["Publicadora"])
        self.entries_map["Publicadora"] = entry_publicadora

        # Ano de lançamento
        lbl_ano = tk.Label(frame_esquerdo, text="Ano de lançamento", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_ano.grid(row=8, column=0, sticky="ew", padx=10)
        entry_ano = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_ano.grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_ano, self.placeholders["Ano de lançamento"])
        self.entries_map["Ano de lançamento"] = entry_ano

        # Plataformas
        lbl_plataformas = tk.Label(frame_esquerdo, text="Plataformas", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_plataformas.grid(row=10, column=0, sticky="ew", padx=10)
        entry_plataformas = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_plataformas.grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_plataformas, self.placeholders["Plataformas"])
        self.entries_map["Plataformas"] = entry_plataformas

        # Gênero
        lbl_genero = tk.Label(frame_esquerdo, text="Gênero", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_genero.grid(row=12, column=0, sticky="ew", padx=10)
        entry_genero = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_genero.grid(row=13, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_genero, self.placeholders["Gênero"])
        self.entries_map["Gênero"] = entry_genero

        # Classificação
        lbl_classificacao = tk.Label(frame_esquerdo, text="Classificação", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_classificacao.grid(row=14, column=0, sticky="ew", padx=10)
        entry_classificacao = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_classificacao.grid(row=15, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_classificacao, self.placeholders["Classificação"])
        self.entries_map["Classificação"] = entry_classificacao

        # ---------- BOTÕES ----------
        def estilizar_botao(botao, cor_base):
            botao.config(bg=cor_base, fg="black", relief="flat", font=button_font, bd=0, cursor="hand2")
            botao.bind("<Enter>", lambda e: botao.config(bg="#bcbcbc"))
            botao.bind("<Leave>", lambda e, b=botao, c=cor_base: botao.config(bg=c))

        btn_adicionar = tk.Button(frame_esquerdo, text="➕ Adicionar / Salvar", command=self.salvar_jogo)
        btn_adicionar.grid(row=16, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_adicionar, "#4CAF50")

        btn_editar = tk.Button(frame_esquerdo, text="✏️ Editar", command=self.carregar_para_edicao)
        btn_editar.grid(row=17, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_editar, "#FFD700")

        btn_excluir = tk.Button(frame_esquerdo, text="❌ Excluir", command=self.excluir_jogo)
        btn_excluir.grid(row=18, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_excluir, "#E53935")

        # --- LADO DIREITO ---
        frame_direito = tk.Frame(frame_conteudo, bg="#f0f0f0")
        frame_direito.place(relx=0.32, rely=0.03, relwidth=0.66, relheight=0.94)

        # Pesquisa
        frame_pesquisa = tk.Frame(frame_direito, bg="white", bd=2, relief="groove")
        frame_pesquisa.place(relx=0.3, rely=0.04, relwidth=0.4, relheight=0.07)

        caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupa2.0.png')
        try:
            imagem_lupa = Image.open(caminho_imagem_lupa).resize((20, 20))
            self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
            tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg="white").pack(side="left", padx=5)
        except Exception:
            self.icone_pesquisa = None

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12), bg="white", bd=0)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...")
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_jogos)

        # --- Frame da tabela ---
        frame_tabela = tk.Frame(frame_direito, bg="#ffffff", highlightbackground="#bbb", highlightthickness=1)
        frame_tabela.place(relx=0.01, rely=0.15, relwidth=0.98, relheight=0.83)

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
            columns=("ID", "Nome", "Contexto", "Desenvolvedora", "Publicadora",
                     "Ano", "Plataformas", "Gênero", "Classificação"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # Cabeçalhos e colunas
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.column("ID", anchor="center", width=40)

        self.tree.heading("Nome", text="Nome", anchor="center")
        self.tree.column("Nome", anchor="center", width=140)

        self.tree.heading("Contexto", text="Contexto", anchor="center")
        self.tree.column("Contexto", anchor="center", width=140)

        self.tree.heading("Desenvolvedora", text="Desenvolvedora", anchor="center")
        self.tree.column("Desenvolvedora", anchor="center", width=140)

        self.tree.heading("Publicadora", text="Publicadora", anchor="center")
        self.tree.column("Publicadora", anchor="center", width=140)

        self.tree.heading("Ano", text="Ano", anchor="center")
        self.tree.column("Ano", anchor="center", width=80)

        self.tree.heading("Plataformas", text="Plataformas", anchor="center")
        self.tree.column("Plataformas", anchor="center", width=120)

        self.tree.heading("Gênero", text="Gênero", anchor="center")
        self.tree.column("Gênero", anchor="center", width=100)

        self.tree.heading("Classificação", text="Classificação", anchor="center")
        self.tree.column("Classificação", anchor="center", width=120)

        self.tree.pack(fill="both", expand=True)

        # Ajuste proporcional de colunas
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            proporcoes = {
                "ID": 40/1044,
                "Nome": 140/1044,
                "Contexto": 140/1044,
                "Desenvolvedora": 140/1044,
                "Publicadora": 140/1044,
                "Ano": 80/1044,
                "Plataformas": 120/1044,
                "Gênero": 100/1044,
                "Classificação": 120/1044
            }
            for col, prop in proporcoes.items():
                self.tree.column(col, width=int(largura_total * prop))

        self.tree.bind("<Configure>", ajustar_largura_colunas)

    # ---------- Funções CRUD e navegação ----------
    def voltar_lobby(self):
        self.frame_jogos.pack_forget()
        abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)

    def ir_para_auditoria(self):
        self.frame_jogos.pack_forget()
        abrir_tela_auditoria(self.master, self.db, self.frame_jogos, self.usuario_logado)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Gerenciador de Jogos")
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
            "📘 AJUDA - Gerenciador de Jogos\n\n"
            "Bem-vindo(a)! Aqui você pode gerenciar seus jogos de forma simples e intuitiva.\n\n"
            "🎬 Adicionar / Salvar: Preencha os campos e clique em 'Adicionar / Salvar'.\n"
            "📝 Editar: Selecione um item e clique em 'Editar', depois 'Salvar'.\n"
            "❌ Excluir: Selecione uma linha da tabela e clique em 'Excluir'.\n"
            "🔍 Pesquisar: Digite qualquer termo para filtrar os resultados.\n"
            "📜 Histórico: Acompanhe ações no log de auditoria.\n"
            "🏠 Lobby: Retorna ao menu principal.\n"
            "💡 Dica: Passe o mouse sobre os botões para ver o destaque.\n"
            "────────────────────────────────────────\n"
            "© Data Flow - Sistema de Gerenciamento de Dados"
        )

        tk.Label(frame_conteudo, text=texto, bg="#f9f9f9", fg="#333", justify="left",
                 font=("Helvetica", 12), wraplength=460, anchor="nw").pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(self.janela_ajuda, text="Fechar", bg="#0E80F0", fg="white",
                  font=("Helvetica", 11, "bold"), relief="raised", padx=20, pady=6,
                  command=self.janela_ajuda.destroy, cursor="hand2").pack(pady=(0, 10))

    def salvar_jogo(self):
        # coleta dados dos campos, removendo placeholders
        dados = {}
        for campo, entry in self.entries_map.items():
            val = entry.get().strip()
            if val == self.placeholders.get(campo):
                val = ""
            dados[campo] = val

        obrigatorios = ["Nome do jogo", "Contexto", "Desenvolvedora", "Publicadora",
                        "Plataformas", "Gênero", "Classificação"]
        for campo in obrigatorios:
            if not dados.get(campo):
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
                return

        try:
            ano = int(dados.get("Ano de lançamento", "") or 0)
        except ValueError:
            messagebox.showwarning("Aviso", "Digite um ano válido!")
            return

        sucesso = self.db.salvar_jogo(
            self.jogo_atual_id,
            dados.get("Nome do jogo", ""),
            dados.get("Contexto", ""),
            dados.get("Desenvolvedora", ""),
            dados.get("Publicadora", ""),
            ano,
            dados.get("Plataformas", ""),
            dados.get("Gênero", ""),
            dados.get("Classificação", ""),
            self.usuario_logado
        )

        if sucesso:
            messagebox.showinfo("Sucesso", "Jogo atualizado!" if self.jogo_atual_id else "Jogo adicionado!")
        else:
            messagebox.showerror("Erro", "Ocorreu um erro ao salvar o jogo. Verifique o console.")

        self.jogo_atual_id = None
        self.limpar_campos()
        self.carregar_jogos()
        self.remover_foco() 


    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um jogo para editar!")
            return

        item = self.tree.item(selected_item)
        jogo = item["values"]
        # valores: (id, nome_do_jogo, contexto, desenvolvedora, publicadora, ano_lancamento, plataformas, genero, classificacao)
        self.jogo_atual_id = jogo[0]

        campos = ["Nome do jogo", "Contexto", "Desenvolvedora", "Publicadora",
                  "Ano de lançamento", "Plataformas", "Gênero", "Classificação"]
        for i, campo in enumerate(campos):
            entry = self.entries_map[campo]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            # jogo[i+1] corresponde ao campo correto
            entry.insert(0, str(jogo[i+1]) if jogo[i+1] is not None else "")
            entry.config(fg="black")
            self.remover_foco() 


    def excluir_jogo(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos um jogo para excluir!")
            return
        confirmar = messagebox.askyesno("Confirmação", f"Excluir {len(selected_items)} registro(s)?")
        if confirmar:
            sucesso_geral = True
            for item in selected_items:
                id_jogo = self.tree.item(item)["values"][0]
                sucesso = self.db.excluir_jogo(id_jogo, self.usuario_logado)
                if not sucesso:
                    sucesso_geral = False
            if sucesso_geral:
                messagebox.showinfo("Sucesso", "Registro(s) excluído(s) com sucesso!")
            else:
                messagebox.showwarning("Aviso", "Alguns registros não foram excluídos (verifique o console).")
            self.carregar_jogos()
            self.remover_foco() 


    def limpar_campos(self):
        for campo, entry in self.entries_map.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            adicionar_placeholder(entry, self.placeholders[campo])
        self.jogo_atual_id = None

    def carregar_jogos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        jogos = self.db.consultar_jogos()
        for jogo in jogos:
            self.tree.insert("", "end", values=jogo)

    def filtrar_jogos(self, event):
        filtro = self.entry_pesquisa.get().lower()
        if filtro == "digite para pesquisar...":
            filtro = ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        jogos_filtrados = self.db.pesquisar_jogos(filtro)
        for jogo in jogos_filtrados:
            self.tree.insert("", "end", values=jogo)
