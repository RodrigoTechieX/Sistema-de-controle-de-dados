# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendmusicas import BancoDeDadosMusicas


def abrir_tela_auditoria(master, db, frame_musicas, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, frame_musicas, usuario_logado)
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


class TelaMusicas:
    ALTURA_NAVBAR = 60

    def __init__(self, master, frame_login, usuario_logado):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.master.title("Data Flow - Gerenciamento de Músicas")
        self.master.geometry("1000x600")

        self.db = BancoDeDadosMusicas()
        self.frame_musicas = tk.Frame(master)
        self.frame_musicas.pack(fill="both", expand=True)
        self.musica_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

        self.placeholders = {
            "Título": "Ex.: Imagine",
            "Artista/Banda": "Ex.: John Lennon",
            "Álbum": "Ex.: Imagine",
            "Gravadora": "Ex.: Apple Records",
            "Ano de Lançamento": "Ex.: 1971",
            "Gênero": "Ex.: Rock",
            "Duração": "Ex.: 3.07"
        }

        self.setup_tela_musicas()
        self.carregar_musicas()

    def remover_foco(self):
        """Remove o foco de todos os Entry, colocando em um widget neutro."""
        self.frame_musicas.focus_set()

    def setup_tela_musicas(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)


 # ---------- NAVBAR ----------
        self.ALTURA_NAVBAR = 0.10  # Altura relativa (10% da tela)
        frame_navbar = tk.Frame(self.frame_musicas, bg="#1F222B")
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        # Configura grid interno (opcional, para alinhamento)
        frame_navbar.columnconfigure(0, weight=1)
        frame_navbar.columnconfigure(1, weight=1)
        frame_navbar.columnconfigure(2, weight=1)

        # Título centralizado
        titulo = tk.Label(frame_navbar,
                        text="Gerenciador de Músicas",
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
        frame_sidebar = tk.Frame(self.frame_musicas, bg="#1F222B")
        frame_sidebar.place(relx=0, rely=0.09, relwidth=0.05, relheight=0.98)

        icones_sidebar = ["🏠", "🎵", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg="#1F222B", fg="white",
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=15, padx=5, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#003366"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1F222B"))


        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_musicas, bg="#eaeaea")
        frame_conteudo.place(relx=0.05, rely=0.08, relwidth=0.95, relheight=0.92)

        # --- LADO ESQUERDO ---
        frame_esquerdo = tk.Frame(frame_conteudo, bg="#f7f7f7", highlightbackground="#ccc", highlightthickness=1)
        frame_esquerdo.place(relx=0.02, rely=0.03, relwidth=0.28, relheight=0.94)
        frame_esquerdo.configure(bd=2, relief="groove")

        # Sombra lateral
        sombra = tk.Frame(frame_conteudo, bg="#d0d0d0")
        sombra.place(relx=0.023, rely=0.036, relwidth=0.28, relheight=0.94)
        frame_esquerdo.lift()

        # Configura grid interno
        for i in range(20):
            frame_esquerdo.rowconfigure(i, weight=1)
        frame_esquerdo.columnconfigure(0, weight=1)

        # ---------- CAMPOS ----------
        for idx, (campo, placeholder) in enumerate(self.placeholders.items()):
            lbl = tk.Label(frame_esquerdo, text=campo, font=label_font, bg="#f7f7f7", anchor="w")
            lbl.grid(row=idx*2, column=0, sticky="ew", padx=10, pady=(10 if idx==0 else 0, 0))
            entry = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
            entry.grid(row=idx*2+1, column=0, sticky="ew", padx=10, pady=(0, 8))
            adicionar_placeholder(entry, placeholder)
            self.entries_map[campo] = entry

        # ---------- BOTÕES ----------
        def estilizar_botao(botao, cor_base):
            botao.config(bg=cor_base, fg="black", relief="flat", font=button_font, bd=0)
            botao.bind("<Enter>", lambda e: botao.config(bg="#bcbcbc"))
            botao.bind("<Leave>", lambda e, b=botao, c=cor_base: botao.config(bg=c))

        btn_adicionar = tk.Button(frame_esquerdo, text="➕ Adicionar / Salvar", command=self.salvar_musica)
        btn_adicionar.grid(row=14, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_adicionar, "#4CAF50")

        btn_editar = tk.Button(frame_esquerdo, text="✏️ Editar", command=self.carregar_para_edicao)
        btn_editar.grid(row=15, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_editar, "#FFD700")

        btn_excluir = tk.Button(frame_esquerdo, text="❌ Excluir", command=self.excluir_musica)
        btn_excluir.grid(row=16, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_excluir, "#E53935")

        # --- LADO DIREITO ---
        frame_direito = tk.Frame(frame_conteudo, bg="#f0f0f0")
        frame_direito.place(relx=0.32, rely=0.03, relwidth=0.66, relheight=0.94)

        # Pesquisa
        frame_pesquisa = tk.Frame(frame_direito, bg="white", bd=2, relief="groove")
        frame_pesquisa.place(relx=0.3, rely=0.04, relwidth=0.4, relheight=0.07)

        caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupa2.0.png')
        imagem_lupa = Image.open(caminho_imagem_lupa).resize((20, 20))
        self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
        tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg="white").pack(side="left", padx=5)

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12), bg="white", bd=0)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...")
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_musicas)

        # --- TABELA ---
        frame_tabela = tk.Frame(frame_direito, bg="#ffffff", highlightbackground="#bbb", highlightthickness=1)
        frame_tabela.place(relx=0.01, rely=0.15, relwidth=0.98, relheight=0.82)

        # Sombra da tabela
        sombra_tabela = tk.Frame(frame_direito, bg="#d0d0d0")
        sombra_tabela.place(relx=0.013, rely=0.155, relwidth=0.98, relheight=0.82)
        frame_tabela.lift()

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Título", "Artista/Banda", "Álbum", "Gravadora",
                    "Ano", "Gênero", "Duração"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # --- Cabeçalhos e larguras iniciais (sem for) ---
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.column("ID", anchor="center", width=40)

        self.tree.heading("Título", text="Título", anchor="center")
        self.tree.column("Título", anchor="center", width=110)

        self.tree.heading("Artista/Banda", text="Artista/Banda", anchor="center")
        self.tree.column("Artista/Banda", anchor="center", width=130)

        self.tree.heading("Álbum", text="Álbum", anchor="center")
        self.tree.column("Álbum", anchor="center", width=100)

        self.tree.heading("Gravadora", text="Gravadora", anchor="center")
        self.tree.column("Gravadora", anchor="center", width=100)

        self.tree.heading("Ano", text="Ano", anchor="center")
        self.tree.column("Ano", anchor="center", width=90)

        self.tree.heading("Gênero", text="Gênero", anchor="center")
        self.tree.column("Gênero", anchor="center", width=90)

        self.tree.heading("Duração", text="Duração", anchor="center")
        self.tree.column("Duração", anchor="center", width=80)

        # Empacotar a tabela
        self.tree.pack(fill="both", expand=True)

        # --- Ajuste automático proporcional das colunas ---
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            proporcoes = {
                "ID": 40/750,
                "Título": 110/750,
                "Artista/Banda": 130/750,
                "Álbum": 100/750,
                "Gravadora": 100/750,
                "Ano": 90/750,
                "Gênero": 90/750,
                "Duração": 80/750
            }
            self.tree.column("ID", width=int(largura_total * proporcoes["ID"]))
            self.tree.column("Título", width=int(largura_total * proporcoes["Título"]))
            self.tree.column("Artista/Banda", width=int(largura_total * proporcoes["Artista/Banda"]))
            self.tree.column("Álbum", width=int(largura_total * proporcoes["Álbum"]))
            self.tree.column("Gravadora", width=int(largura_total * proporcoes["Gravadora"]))
            self.tree.column("Ano", width=int(largura_total * proporcoes["Ano"]))
            self.tree.column("Gênero", width=int(largura_total * proporcoes["Gênero"]))
            self.tree.column("Duração", width=int(largura_total * proporcoes["Duração"]))

        self.tree.bind("<Configure>", ajustar_largura_colunas)


    # ---------- FUNÇÕES CRUD E NAVEGAÇÃO ----------
    def ir_para_auditoria(self):
        self.frame_musicas.pack_forget()
        abrir_tela_auditoria(self.master, self.db, self.frame_musicas, self.usuario_logado)

    def voltar_lobby(self):
        self.frame_musicas.pack_forget()
        abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)

    def salvar_musica(self):
        dados = {campo: entry.get().strip() for campo, entry in self.entries_map.items()}

        obrigatorios = ["Título", "Artista/Banda", "Álbum", "Gravadora"]
        for campo in obrigatorios:
            if not dados[campo] or dados[campo] == self.placeholders[campo]:
                messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
                return

        try:
            ano = int(dados["Ano de Lançamento"]) if dados["Ano de Lançamento"] != self.placeholders["Ano de Lançamento"] else 0
        except ValueError:
            messagebox.showwarning("Aviso", "Digite um ano válido!")
            return

        try:
            duracao = float(dados["Duração"].replace(",", ".")) if dados["Duração"] != self.placeholders["Duração"] else 0.0
        except ValueError:
            messagebox.showwarning("Aviso", "Digite um valor válido para Duração!")
            return

        self.db.salvar_musica(
            self.musica_atual_id, dados["Título"], dados["Artista/Banda"], dados["Álbum"],
            dados["Gravadora"], ano, dados.get("Gênero", ""), duracao, self.usuario_logado
        )

        if self.musica_atual_id:
            messagebox.showinfo("Sucesso", "Música atualizada com sucesso!")
            self.musica_atual_id = None
        else:
            messagebox.showinfo("Sucesso", "Música adicionada com sucesso!")

        self.limpar_campos()
        self.carregar_musicas()
        self.remover_foco() 

    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione uma música para editar!")
            return

        item = self.tree.item(selected_item)
        musica = item["values"]
        self.musica_atual_id = musica[0]

        campos = list(self.placeholders.keys())
        for i, campo in enumerate(campos):
            entry = self.entries_map[campo]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, musica[i + 1])
            entry.config(fg="black")
            self.remover_foco() 

    def excluir_musica(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma música para excluir!")
            return

        confirmar = messagebox.askyesno("Confirmação", f"Excluir {len(selected_items)} música(s)?")
        if confirmar:
            for item in selected_items:
                id_musica = self.tree.item(item)["values"][0]
                self.db.excluir_musica(id_musica, self.usuario_logado)
            messagebox.showinfo("Sucesso", "Música(s) excluída(s) com sucesso!")
            self.carregar_musicas()
            self.remover_foco() 

    def limpar_campos(self):
        for campo, entry in self.entries_map.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            adicionar_placeholder(entry, self.placeholders[campo])
        self.musica_atual_id = None

    def carregar_musicas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        musicas = self.db.consultar_musicas()
        for musica in musicas:
            self.tree.insert("", "end", values=musica)

    def filtrar_musicas(self, event):
        filtro = self.entry_pesquisa.get().lower()
        if filtro == "digite para pesquisar...":
            filtro = ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        musicas_filtradas = self.db.pesquisar_musicas(filtro)
        for musica in musicas_filtradas:
            self.tree.insert("", "end", values=musica)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Músicas")
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
            "📘 AJUDA - Gerenciador de Músicas\n\n"
            "Bem-vindo(a)! Aqui você pode gerenciar suas músicas de forma simples e intuitiva.\n\n"
            "➕ Adicionar / Salvar: Preencha os campos e clique em 'Adicionar / Salvar'.\n"
            "✏️ Editar: Selecione um item e clique em 'Editar', depois 'Salvar'.\n"
            "❌ Excluir: Selecione uma linha na tabela e clique em 'Excluir'.\n"
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

        btn_fechar = tk.Button(
            self.janela_ajuda, text="Fechar", bg="#0E80F0", fg="white",
            font=("Helvetica", 11, "bold"), relief="raised", padx=20, pady=6,
            command=self.janela_ajuda.destroy, cursor="hand2"
        )
        btn_fechar.pack(pady=(0, 10))

        def ao_fechar():
            self.janela_ajuda.destroy()
            self.janela_ajuda = None

        self.janela_ajuda.protocol("WM_DELETE_WINDOW", ao_fechar)
