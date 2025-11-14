# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendveiculos import BancoDeDadosVeiculos


def abrir_tela_auditoria(master, db, frame_veiculos, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, frame_veiculos, usuario_logado)
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


class TelaVeiculos:
    ALTURA_NAVBAR = 60

    def __init__(self, master, frame_login, usuario_logado):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.master.title("Data Flow - Veículos")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosVeiculos()

        self.frame_veiculos = tk.Frame(master)
        self.frame_veiculos.pack(fill="both", expand=True)

        self.veiculo_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

        # Placeholders
        self.placeholders = {
            "Marca": "Ex: Toyota",
            "Modelo": "Ex: Corolla",
            "Ano de fabricação": "Ex: 2019",
            "Ano do modelo": "Ex: 2020",
            "Cor": "Ex: Prata",
            "Placa": "Ex: ABC-1234",
            "Quilometragem": "Ex: 45000",
            "Tipo": "Selecione o tipo"
        }

        self.setup_tela_veiculos()
        self.carregar_veiculos()

    def remover_foco(self):
        """Remove o foco de todos os Entry, colocando em um widget neutro."""
        self.frame_veiculos.focus_set()  # Ou use self.master.focus() se preferir

    def setup_tela_veiculos(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)

        # ---------- NAVBAR ----------
        self.ALTURA_NAVBAR = 0.10  # Altura relativa (10% da tela)
        frame_navbar = tk.Frame(self.frame_veiculos, bg="#1F222B")
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        # Configura grid interno (opcional, para alinhamento)
        frame_navbar.columnconfigure(0, weight=1)
        frame_navbar.columnconfigure(1, weight=1)
        frame_navbar.columnconfigure(2, weight=1)

        # Título centralizado
        titulo = tk.Label(frame_navbar,
                        text="Gerenciador de Veículos",
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
        frame_sidebar = tk.Frame(self.frame_veiculos, bg="#1F222B")
        frame_sidebar.place(relx=0, rely=0.09, relwidth=0.05, relheight=0.96)

        icones_sidebar = ["🏠", "🚗", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg="#1F222B", fg="white",
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=15, padx=5, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#003366"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1F222B"))


        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_veiculos, bg="#eaeaea")
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
        for i in range(25):
            frame_esquerdo.rowconfigure(i, weight=1)

        # Fonte igual ao código de filmes e séries
        label_font = ("Raleway", 11, "bold")
        entry_font = ("Raleway", 11)
        button_font = ("Raleway", 11, "bold")

        # ---------- COMBOBOX TIPO ----------
        lbl_tipo = tk.Label(frame_esquerdo, text="Tipo:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_tipo.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))

        combo_tipo = ttk.Combobox(frame_esquerdo, font=entry_font, state="readonly")
        combo_tipo['values'] = ["Carro", "Moto", "Caminhão", "SUV", "Van", "Ônibus"]
        combo_tipo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))

        # Valor inicial já selecionado (igual ao código de filmes e séries)
        combo_tipo.set("Selecione o tipo")

        self.entries_map["Tipo"] = combo_tipo



        # ---------- CAMPOS ----------
        lbl_marca = tk.Label(frame_esquerdo, text="Marca:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_marca.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_marca = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_marca.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_marca, self.placeholders["Marca"])
        self.entries_map["Marca"] = entry_marca

        lbl_modelo = tk.Label(frame_esquerdo, text="Modelo:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_modelo.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_modelo = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_modelo.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_modelo, self.placeholders["Modelo"])
        self.entries_map["Modelo"] = entry_modelo

        lbl_ano_fab = tk.Label(frame_esquerdo, text="Ano de fabricação:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_ano_fab.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_ano_fab = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_ano_fab.grid(row=7, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_ano_fab, self.placeholders["Ano de fabricação"])
        self.entries_map["Ano de fabricação"] = entry_ano_fab

        lbl_ano_mod = tk.Label(frame_esquerdo, text="Ano do modelo:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_ano_mod.grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_ano_mod = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_ano_mod.grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_ano_mod, self.placeholders["Ano do modelo"])
        self.entries_map["Ano do modelo"] = entry_ano_mod

        lbl_cor = tk.Label(frame_esquerdo, text="Cor:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_cor.grid(row=10, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_cor = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_cor.grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_cor, self.placeholders["Cor"])
        self.entries_map["Cor"] = entry_cor

        lbl_placa = tk.Label(frame_esquerdo, text="Placa:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_placa.grid(row=12, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_placa = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_placa.grid(row=13, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_placa, self.placeholders["Placa"])
        self.entries_map["Placa"] = entry_placa

        lbl_km = tk.Label(frame_esquerdo, text="Quilometragem:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_km.grid(row=14, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        entry_km = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_km.grid(row=15, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_km, self.placeholders["Quilometragem"])
        self.entries_map["Quilometragem"] = entry_km

        # ---------- BOTÕES CRUD ----------
        def estilizar_botao(botao, cor_base):
            botao.config(bg=cor_base, fg="black", relief="flat", font=button_font, bd=0)
            botao.bind("<Enter>", lambda e: botao.config(bg="#bcbcbc"))
            botao.bind("<Leave>", lambda e: botao.config(bg=cor_base))

        btn_adicionar = tk.Button(frame_esquerdo, text="➕ Adicionar / Salvar", command=self.salvar_veiculo)
        btn_adicionar.grid(row=17, column=0, columnspan=2, sticky="ew", padx=30, pady=(20, 5))
        estilizar_botao(btn_adicionar, "#4CAF50")

        btn_editar = tk.Button(frame_esquerdo, text="✏️ Editar", command=self.carregar_para_edicao)
        btn_editar.grid(row=18, column=0, columnspan=2, sticky="ew", padx=30, pady=5)
        estilizar_botao(btn_editar, "#FFD700")

        btn_excluir = tk.Button(frame_esquerdo, text="❌ Excluir", command=self.excluir_veiculo)
        btn_excluir.grid(row=19, column=0, columnspan=2, sticky="ew", padx=30, pady=5)
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
            tk.Label(frame_pesquisa, text="🔍", bg="white").pack(side="left", padx=5)

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12), bg="white", bd=0)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...")
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_veiculos)

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
            columns=("ID", "Tipo", "Marca", "Modelo", "Ano/Fab", "Ano/Modelo", "Cor", "Placa", "Quilometragem"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)

        # --- Cabeçalhos e larguras iniciais (sem for) ---
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.column("ID", anchor="center", width=40)

        self.tree.heading("Tipo", text="Tipo", anchor="center")
        self.tree.column("Tipo", anchor="center", width=80)

        self.tree.heading("Marca", text="Marca", anchor="center")
        self.tree.column("Marca", anchor="center", width=90)

        self.tree.heading("Modelo", text="Modelo", anchor="center")
        self.tree.column("Modelo", anchor="center", width=90)

        self.tree.heading("Ano/Fab", text="Ano/Fab", anchor="center")
        self.tree.column("Ano/Fab", anchor="center", width=80)

        self.tree.heading("Ano/Modelo", text="Ano/Modelo", anchor="center")
        self.tree.column("Ano/Modelo", anchor="center", width=90)

        self.tree.heading("Cor", text="Cor", anchor="center")
        self.tree.column("Cor", anchor="center", width=60)

        self.tree.heading("Placa", text="Placa", anchor="center")
        self.tree.column("Placa", anchor="center", width=80)

        self.tree.heading("Quilometragem", text="Quilometragem", anchor="center")
        self.tree.column("Quilometragem", anchor="center", width=110)

        # Empacotar a tabela
        self.tree.pack(fill="both", expand=True)

        # --- Ajuste automático proporcional das colunas ---
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            proporcoes = {
                "ID": 40/720,
                "Tipo": 80/720,
                "Marca": 90/720,
                "Modelo": 90/720,
                "Ano/Fab": 80/720,
                "Ano/Modelo": 90/720,
                "Cor": 60/720,
                "Placa": 80/720,
                "Quilometragem": 110/720
            }
            self.tree.column("ID", width=int(largura_total * proporcoes["ID"]))
            self.tree.column("Tipo", width=int(largura_total * proporcoes["Tipo"]))
            self.tree.column("Marca", width=int(largura_total * proporcoes["Marca"]))
            self.tree.column("Modelo", width=int(largura_total * proporcoes["Modelo"]))
            self.tree.column("Ano/Fab", width=int(largura_total * proporcoes["Ano/Fab"]))
            self.tree.column("Ano/Modelo", width=int(largura_total * proporcoes["Ano/Modelo"]))
            self.tree.column("Cor", width=int(largura_total * proporcoes["Cor"]))
            self.tree.column("Placa", width=int(largura_total * proporcoes["Placa"]))
            self.tree.column("Quilometragem", width=int(largura_total * proporcoes["Quilometragem"]))

        self.tree.bind("<Configure>", ajustar_largura_colunas)


    # ---------- Funções CRUD e navegação ----------
    def voltar_lobby(self):
        self.frame_veiculos.pack_forget()
        abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)

    def ir_para_auditoria(self):
        self.frame_veiculos.pack_forget()
        abrir_tela_auditoria(self.master, self.db, self.frame_veiculos, self.usuario_logado)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Veículos")
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
            "📘 AJUDA - Gerenciador de Veículos\n\n"
            "Bem-vindo(a)! Aqui você pode gerenciar seus veículos de forma simples e intuitiva.\n\n"
            "➕ Adicionar / Salvar: Preencha os campos e clique em 'Adicionar / Salvar'.\n"
            "✏️ Editar: Selecione um veículo, clique em 'Editar', altere os dados e salve.\n"
            "❌ Excluir: Selecione um veículo e clique em 'Excluir'.\n"
            "🔍 Pesquisar: Digite qualquer termo para filtrar a tabela.\n"
            "📜 Histórico: Visualize registros no log de auditoria.\n"
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
    def salvar_veiculo(self):
        try:
            dados = {campo: entry.get().strip() for campo, entry in self.entries_map.items()}

            # substituir placeholders
            for campo in dados:
                if dados[campo] == self.placeholders.get(campo, "") or dados[campo] == "Selecione o tipo":
                    dados[campo] = ""

            # validação obrigatória
            if not dados["Marca"] or not dados["Modelo"] or not dados["Placa"]:
                messagebox.showwarning("Aviso", "Preencha pelo menos Marca, Modelo e Placa!")
                return
            if not dados["Tipo"]:
                messagebox.showwarning("Aviso", "Selecione o Tipo do veículo!")
                return

            # conversão segura
            try:
                ano_fab = int(dados["Ano de fabricação"]) if dados["Ano de fabricação"] else 0
                ano_mod = int(dados["Ano do modelo"]) if dados["Ano do modelo"] else 0
                quilometragem = float(dados["Quilometragem"].replace(",", ".")) if dados["Quilometragem"] else 0.0
            except ValueError:
                messagebox.showwarning("Aviso", "Digite números válidos para Ano e Quilometragem!")
                return

            # chama backend com ordem correta
            self.db.salvar_veiculo(
                self.veiculo_atual_id,
                dados["Tipo"],
                dados["Marca"],
                dados["Modelo"],
                ano_fab,
                ano_mod,
                dados["Cor"],
                dados["Placa"],
                quilometragem,
                usuario_logado=self.usuario_logado
            )

            if self.veiculo_atual_id:
                messagebox.showinfo("Sucesso", "Veículo atualizado com sucesso!")
                self.veiculo_atual_id = None
            else:
                messagebox.showinfo("Sucesso", "Veículo adicionado com sucesso!")

            self.limpar_campos()
            self.carregar_veiculos()
            self.remover_foco() 

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar veículo: {e}")

    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um veículo para editar!")
            return

        item = self.tree.item(selected_item)
        veiculo = item["values"]
        self.veiculo_atual_id = veiculo[0]

        # Mapeamento coluna → campo
        mapeamento = {
            "Tipo": veiculo[1],
            "Marca": veiculo[2],
            "Modelo": veiculo[3],
            "Ano de fabricação": veiculo[4],  # AnoFab
            "Ano do modelo": veiculo[5],      # AnoModelo
            "Cor": veiculo[6],
            "Placa": veiculo[7],
            "Quilometragem": veiculo[8]
        }

        for campo, valor in mapeamento.items():
            widget = self.entries_map[campo]
            if isinstance(widget, ttk.Combobox):
                widget.set(valor if valor else "Selecione o tipo")
            else:
                widget.delete(0, tk.END)
                if valor and str(valor).strip() != "":
                    widget.insert(0, valor)
                    widget.config(fg="black")  # Valor real em preto
                else:
                    placeholder = self.placeholders.get(campo, "")
                    widget.insert(0, placeholder)
                    widget.config(fg="grey")   # Placeholder em cinza
                    self.remover_foco() 



    def excluir_veiculo(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos um veículo para excluir!")
            return

        if messagebox.askyesno("Confirmação", f"Deseja realmente excluir {len(selected_items)} veículo(s)?"):
            erros = []
            for item_id in selected_items:
                try:
                    veiculo_id = self.tree.item(item_id)["values"][0]
                    self.db.excluir_veiculo(veiculo_id, usuario_logado=self.usuario_logado)
                except Exception as e:
                    erros.append(str(e))

            if erros:
                messagebox.showerror("Erro", f"Ocorreram erros ao excluir:\n{chr(10).join(erros)}")
            else:
                messagebox.showinfo("Sucesso", f"{len(selected_items)} veículo(s) excluído(s) com sucesso!")

            self.carregar_veiculos()
            self.remover_foco()


    def carregar_veiculos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for veiculo in self.db.consultar_veiculos():
            self.tree.insert("", "end", values=veiculo)

    def limpar_campos(self):
        for campo, widget in self.entries_map.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("Selecione o tipo")
            else:
                widget.delete(0, tk.END)
                if campo in self.placeholders:
                    widget.insert(0, self.placeholders[campo])
                    widget.config(fg="grey")

    def filtrar_veiculos(self, event=None):
        termo = self.entry_pesquisa.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for veiculo in self.db.pesquisar_veiculos(termo):
            self.tree.insert("", "end", values=veiculo)

    def iniciar(self):
        self.frame_veiculos.pack(fill="both", expand=True)
