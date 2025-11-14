# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendfuncionarios import BancoDeDadosFuncionarios


def abrir_tela_auditoria(master, db, frame_funcionarios, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, frame_funcionarios, usuario_logado)
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


class TelaFuncionarios:
    ALTURA_NAVBAR = 60

    def __init__(self, master, frame_login, usuario_logado):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.db = BancoDeDadosFuncionarios()
        self.frame_funcionarios = tk.Frame(master)
        self.frame_funcionarios.pack(fill="both", expand=True)

        self.funcionarios_atual_id = None
        self.janela_ajuda = None
        self.entries_map = {}

        # Placeholders
        self.placeholders = {
            "Tipo:": "Efetivo / Temporário",
            "Nome:": "Ex: João da Silva",
            "CPF:": "Ex: 123.456.789-00",
            "Cargo:": "Ex: Analista de TI",
            "Setor:": "Ex: Tecnologia da Informação",
            "Data de Admissão:": "Ex: 2022/03/15",
            "Salário:": "Ex: R$ 4.500,00",
            "Contato:": "Ex: (11) 91234-5678"
        }

        self.iniciar()

    def iniciar(self):
        self.master.title("Data Flow - Funcionários")
        self.master.geometry("1000x600")
        self.setup_tela_funcionarios()
        self.carregar_funcionarios()

    def setup_tela_funcionarios(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)

        # ---------- NAVBAR ----------
        self.ALTURA_NAVBAR = 0.10  # Altura relativa (10% da tela)
        frame_navbar = tk.Frame(self.frame_funcionarios, bg="#1F222B")
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        # Configura grid interno (opcional, pode ser usado para alinhamento)
        frame_navbar.columnconfigure(0, weight=1)
        frame_navbar.columnconfigure(1, weight=1)
        frame_navbar.columnconfigure(2, weight=1)

        # Título centralizado
        titulo = tk.Label(frame_navbar,
                        text="Gerenciador de Funcionários",
                        font=("Helvetica", 14, "bold"),
                        fg="white",
                        bg="#1F222B")
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
        frame_sidebar = tk.Frame(self.frame_funcionarios, bg="#1F222B")
        frame_sidebar.place(relx=0, rely=0.09, relwidth=0.05, relheight=0.98)

        icones_sidebar = ["🏠", "👥", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg="#1F222B", fg="white",
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=15, padx=5, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#003366"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#1F222B"))


        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_funcionarios, bg="#eaeaea")
        frame_conteudo.place(relx=0.05, rely=0.08, relwidth=0.95, relheight=0.92)

        # --- LADO ESQUERDO ---
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

        # --- Campos do formulário ---
        # Tipo (combo)
        lbl_tipo = tk.Label(frame_esquerdo, text="Tipo:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_tipo.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.combo_tipo = ttk.Combobox(frame_esquerdo, values=["Efetivo", "Temporário"], state="readonly")
        self.combo_tipo.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        self.combo_tipo.set("Selecione...")

        def tipo_alterado(event):
            tipo = self.combo_tipo.get()
            if tipo == "Temporário":
                self.entries_map["Salário:"].config(state="normal")
                
            else:
                self.entries_map["Salário:"].config(state="normal")

        self.combo_tipo.bind("<<ComboboxSelected>>", tipo_alterado)

        # Campos individuais (sem for)
        lbl_nome = tk.Label(frame_esquerdo, text="Nome:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_nome.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 0))
        entry_nome = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_nome.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_nome, self.placeholders.get("Nome:", ""))
        self.entries_map["Nome:"] = entry_nome

        lbl_cpf = tk.Label(frame_esquerdo, text="CPF:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_cpf.grid(row=4, column=0, sticky="ew", padx=10)
        entry_cpf = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_cpf.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_cpf, self.placeholders.get("CPF:", ""))
        self.entries_map["CPF:"] = entry_cpf

        lbl_cargo = tk.Label(frame_esquerdo, text="Cargo:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_cargo.grid(row=6, column=0, sticky="ew", padx=10)
        entry_cargo = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_cargo.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_cargo, self.placeholders.get("Cargo:", ""))
        self.entries_map["Cargo:"] = entry_cargo

        lbl_setor = tk.Label(frame_esquerdo, text="Setor:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_setor.grid(row=8, column=0, sticky="ew", padx=10)
        entry_setor = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_setor.grid(row=9, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_setor, self.placeholders.get("Setor:", ""))
        self.entries_map["Setor:"] = entry_setor

        lbl_admissao = tk.Label(frame_esquerdo, text="Data de Admissão:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_admissao.grid(row=10, column=0, sticky="ew", padx=10)
        entry_admissao = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_admissao.grid(row=11, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_admissao, self.placeholders.get("Data de Admissão:", ""))
        self.entries_map["Data de Admissão:"] = entry_admissao

        lbl_salario = tk.Label(frame_esquerdo, text="Salário:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_salario.grid(row=12, column=0, sticky="ew", padx=10)
        entry_salario = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_salario.grid(row=13, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_salario, self.placeholders.get("Salário:", ""))
        self.entries_map["Salário:"] = entry_salario

        lbl_contato = tk.Label(frame_esquerdo, text="Contato:", font=label_font, bg="#f7f7f7", anchor="w")
        lbl_contato.grid(row=14, column=0, sticky="ew", padx=10)
        entry_contato = tk.Entry(frame_esquerdo, font=entry_font, bg="white", bd=2, relief="groove")
        entry_contato.grid(row=15, column=0, sticky="ew", padx=10, pady=(0, 8))
        adicionar_placeholder(entry_contato, self.placeholders.get("Contato:", ""))
        self.entries_map["Contato:"] = entry_contato

        # ---------- BOTÕES ----------
        def estilizar_botao(botao, cor_base):
            botao.config(bg=cor_base, fg="black", relief="flat", font=button_font, bd=0, cursor="hand2")
            botao.bind("<Enter>", lambda e: botao.config(bg="#bcbcbc"))
            botao.bind("<Leave>", lambda e, c=cor_base: botao.config(bg=c))

        btn_adicionar = tk.Button(frame_esquerdo, text="➕ Adicionar / Salvar", command=self.salvar_funcionario)
        btn_adicionar.grid(row=16, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_adicionar, "#4CAF50")

        btn_editar = tk.Button(frame_esquerdo, text="✏️ Editar", command=self.carregar_para_edicao)
        btn_editar.grid(row=17, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_editar, "#FFD700")

        btn_excluir = tk.Button(frame_esquerdo, text="❌ Excluir", command=self.excluir_funcionarios)
        btn_excluir.grid(row=18, column=0, sticky="ew", padx=20, pady=(5, 5))
        estilizar_botao(btn_excluir, "#E53935")


        # --- LADO DIREITO ---
        frame_direito = tk.Frame(frame_conteudo, bg="#f0f0f0")
        frame_direito.place(relx=0.32, rely=0.03, relwidth=0.66, relheight=0.94)

        # Pesquisa
        frame_pesquisa = tk.Frame(frame_direito, bg="white", bd=2, relief="groove")
        frame_pesquisa.place(relx=0.30, rely=0.04, relwidth=0.4, relheight=0.07)

        caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupa2.0.png')
        try:
            imagem_lupa = Image.open(caminho_imagem_lupa).resize((20, 20))
            self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
        except Exception:
            self.icone_pesquisa = None

        tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg="white").pack(side="left", padx=5)

        self.entry_pesquisa = tk.Entry(frame_pesquisa, font=("Helvetica", 12), bg="white", bd=0)
        self.entry_pesquisa.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        adicionar_placeholder(self.entry_pesquisa, "Digite para pesquisar...")
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_funcionarios)

        # --- TABELA ---
        frame_tabela = tk.Frame(frame_direito, bg="#ffffff", highlightbackground="#bbb", highlightthickness=1)
        frame_tabela.place(relx=0.01, rely=0.15, relwidth=0.98, relheight=0.82)

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar_x = ttk.Scrollbar(frame_tabela, orient="horizontal")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Tipo", "Nome", "CPF", "Cargo", "Setor", "Data de Admissão", "Salário", "Contato"),
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

        self.tree.heading("Nome", text="Nome", anchor="center")
        self.tree.column("Nome", anchor="center", width=180)

        self.tree.heading("CPF", text="CPF", anchor="center")
        self.tree.column("CPF", anchor="center", width=120)

        self.tree.heading("Cargo", text="Cargo", anchor="center")
        self.tree.column("Cargo", anchor="center", width=140)

        self.tree.heading("Setor", text="Setor", anchor="center")
        self.tree.column("Setor", anchor="center", width=140)

        self.tree.heading("Data de Admissão", text="Data de Admissão", anchor="center")
        self.tree.column("Data de Admissão", anchor="center", width=130)

        self.tree.heading("Salário", text="Salário", anchor="center")
        self.tree.column("Salário", anchor="center", width=100)

        self.tree.heading("Contato", text="Contato", anchor="center")
        self.tree.column("Contato", anchor="center", width=150)

        # Empacotar a tabela
        self.tree.pack(fill="both", expand=True)

        # --- Ajuste automático proporcional das colunas ---
        def ajustar_largura_colunas(event):
            largura_total = self.tree.winfo_width()
            # proporção de cada coluna (soma = 1.0)
            proporcoes = {
                "ID": 40/1060,
                "Tipo": 80/1060,
                "Nome": 180/1060,
                "CPF": 120/1060,
                "Cargo": 140/1060,
                "Setor": 140/1060,
                "Data de Admissão": 130/1060,
                "Salário": 100/1060,
                "Contato": 150/1060
            }
            # aplica proporcionalmente
            self.tree.column("ID", width=int(largura_total * proporcoes["ID"]))
            self.tree.column("Tipo", width=int(largura_total * proporcoes["Tipo"]))
            self.tree.column("Nome", width=int(largura_total * proporcoes["Nome"]))
            self.tree.column("CPF", width=int(largura_total * proporcoes["CPF"]))
            self.tree.column("Cargo", width=int(largura_total * proporcoes["Cargo"]))
            self.tree.column("Setor", width=int(largura_total * proporcoes["Setor"]))
            self.tree.column("Data de Admissão", width=int(largura_total * proporcoes["Data de Admissão"]))
            self.tree.column("Salário", width=int(largura_total * proporcoes["Salário"]))
            self.tree.column("Contato", width=int(largura_total * proporcoes["Contato"]))

        self.tree.bind("<Configure>", ajustar_largura_colunas)






    # ---------- NAVEGAÇÃO ----------
    def voltar_lobby(self):
        self.frame_funcionarios.pack_forget()
        abrir_tela_principal(self.master, self.db, self.frame_login, self.usuario_logado)

    def ir_para_auditoria(self):
        self.frame_funcionarios.pack_forget()
        abrir_tela_auditoria(self.master, self.db, self.frame_funcionarios, self.usuario_logado)

    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Funcionários")
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
            "📘 AJUDA - Gerenciador de Funcionários\n\n"
            "Bem-vindo(a)! Aqui você pode gerenciar seus Funcionários de forma simples e intuitiva.\n\n"
            "➕ Adicionar / Salvar: Preencha os campos e clique em 'Adicionar / Salvar'.\n"
            "✏️ Editar: Selecione um item na tabela e clique em 'Editar'.\n"
            "❌ Excluir: Selecione um ou mais itens e clique em 'Excluir'.\n"
            "🔍 Pesquisar: Digite qualquer termo para filtrar os resultados.\n"
            "🏠 Lobby: Retorna ao menu principal.\n"
            "📜 Histórico: Confira o log de auditoria.\n"
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

    # ---------- CRUD ----------
    def salvar_funcionario(self):
        tipo = self.combo_tipo.get().strip()
        nome = self.entries_map["Nome:"].get().strip()
        cpf = self.entries_map["CPF:"].get().strip()
        cargo = self.entries_map["Cargo:"].get().strip()
        setor = self.entries_map["Setor:"].get().strip()
        data_admissao = self.entries_map["Data de Admissão:"].get().strip()
        salario = self.entries_map["Salário:"].get().strip()
        contato = self.entries_map["Contato:"].get().strip()

        # --- VALIDAÇÕES ---
        if tipo == "Selecione..." or not tipo:
            messagebox.showwarning("Aviso", "Selecione o Tipo do funcionário (Efetivo ou Temporário)!")
            return

        if not nome:
            messagebox.showwarning("Aviso", "Preencha o campo Nome!")
            return

        # --- SALÁRIO: nunca zero ---
        salario_val = 0.0
        if not salario or salario in ["R$ 0,00", "0", "0.0"]:
            # Valor padrão mínimo
            salario_val = 1000.0
            self.entries_map["Salário:"].delete(0, tk.END)
            self.entries_map["Salário:"].insert(0, "R$ 1.000,00")
            self.entries_map["Salário:"].config(fg="grey")
        else:
            try:
                valor = salario.replace("R$", "").replace(".", "").replace(",", ".").strip()
                salario_val = float(valor)
                if salario_val <= 0:
                    salario_val = 1000.0
                    self.entries_map["Salário:"].delete(0, tk.END)
                    self.entries_map["Salário:"].insert(0, "R$ 1.000,00")
                    self.entries_map["Salário:"].config(fg="grey")
            except ValueError:
                messagebox.showwarning("Aviso", "Digite um salário válido!")
                return

        # --- SALVAR NO BANCO ---
        try:
            self.db.salvar_funcionario(
                id_funcionario=self.funcionarios_atual_id,
                tipo=tipo,
                nome=nome,
                cpf=cpf,
                cargo=cargo,
                setor=setor,
                data_admissao=data_admissao,
                salario=salario_val,
                contato=contato,
                usuario_logado=self.usuario_logado
            )
            messagebox.showinfo("Sucesso", "Funcionário adicionado/atualizado com sucesso!")
            self.funcionarios_atual_id = None
            self.limpar_campos()
            self.frame_funcionarios.focus_set()
            self.carregar_funcionarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o funcionário: {e}")



    def limpar_campos(self):
            for campo, entry in self.entries_map.items():
                entry.config(state="normal")
                entry.delete(0, tk.END)
                adicionar_placeholder(entry, self.placeholders.get(campo, ""))
            self.combo_tipo.set("Selecione...")
            self.funcionarios_atual_id = None


         

    def carregar_para_edicao(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um funcionário para editar!")
            return
        item = self.tree.item(selected_item)
        func = item["values"]
        self.funcionarios_atual_id = func[0]
        try:
            self.combo_tipo.set(func[1])
        except Exception:
            self.combo_tipo.set("Selecione...")
        campos = ["Nome:", "CPF:", "Cargo:", "Setor:", "Data de Admissão:", "Salário:", "Contato:"]
        for i, campo in enumerate(campos):
            entry = self.entries_map[campo]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, func[i + 2])
            entry.config(fg="black")
        if func[1] == "Temporário":
            self.entries_map["Salário:"].config(state="disabled")

    def excluir_funcionarios(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Aviso", "Selecione pelo menos um funcionário para excluir!")
            return
        if messagebox.askyesno("Confirmação", f"Excluir {len(selected_items)} funcionário(s)?"):
            for item in selected_items:
                id_func = self.tree.item(item)["values"][0]
                self.db.excluir_funcionario(id_func, usuario_logado=self.usuario_logado)
            messagebox.showinfo("Sucesso", "Funcionário(s) excluído(s) com sucesso!")
            self.carregar_funcionarios()

    def limpar_campos(self):
        for campo, entry in self.entries_map.items():
            entry.config(state="normal")
            entry.delete(0, tk.END)
            adicionar_placeholder(entry, self.placeholders.get(campo, ""))
        self.combo_tipo.set("Selecione...")
        self.funcionarios_atual_id = None

    def carregar_funcionarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        funcionarios = self.db.consultar_funcionarios()
        for f in funcionarios:
            self.tree.insert("", "end", values=f)

    def filtrar_funcionarios(self, event):
        filtro = self.entry_pesquisa.get().lower()
        if filtro == "digite para pesquisar...":
            filtro = ""
        for item in self.tree.get_children():
            self.tree.delete(item)
        funcionarios_filtrados = self.db.pesquisar_funcionarios(filtro)
        for f in funcionarios_filtrados:
            self.tree.insert("", "end", values=f)
