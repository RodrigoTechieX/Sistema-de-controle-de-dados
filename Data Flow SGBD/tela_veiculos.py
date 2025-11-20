# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from backendveiculos import BancoDeDadosVeiculos
from Auditoria import TelaAuditoria


def abrir_tela_auditoria(master, db, on_voltar_callback, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, on_voltar_callback, usuario_logado)
    ts.titulo_origem = "Data Flow - Veículos"
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


class TelaVeiculos:
    ALTURA_NAVBAR = 0.10  # mesma abordagem relativa

    def __init__(self, master, frame_login, usuario_logado, on_voltar_callback=None):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.on_voltar_callback = on_voltar_callback
        self.master.title("Data Flow - Veículos")
        self.master.geometry("1000x600")
        self.db = BancoDeDadosVeiculos()

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

        self.frame_veiculos = tk.Frame(master, bg=self._bg_main)
        self.frame_veiculos.pack(fill="both", expand=True)

        self.veiculo_atual_id = None
        self.entries_map = {}
        self.janela_ajuda = None

        self.placeholders = {
            "Tipo": "Selecione o tipo",
            "Marca": "Ex: Toyota",
            "Modelo": "Ex: Corolla",
            "Ano de fabricação": "Ex: 2019",
            "Ano do modelo": "Ex: 2020",
            "Cor": "Ex: Prata",
            "Placa": "Ex: ABC-1234",
            "Quilometragem": "Ex: 45000"
        }

        self.setup_tela_veiculos()
        self.carregar_veiculos()

    def setup_tela_veiculos(self):
        label_font = ("Helvetica", 11, "bold")
        entry_font = ("Helvetica", 11)
        button_font = ("Helvetica", 11, "bold")
        diretorio_atual = os.path.dirname(__file__)

        # ---------- NAVBAR ----------
        frame_navbar = tk.Frame(self.frame_veiculos, bg=self._bg_nav)
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        titulo = tk.Label(frame_navbar,
                          text="Gerenciador de Veículos",
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
        frame_sidebar = tk.Frame(self.frame_veiculos, bg=self._bg_nav)
        frame_sidebar.place(relx=0, rely=self.ALTURA_NAVBAR, relwidth=0.05, relheight=1 - self.ALTURA_NAVBAR)

        icones_sidebar = ["🏠", "🚗", "📜", "❓"]
        comandos_sidebar = [self.voltar_lobby, lambda: None, self.ir_para_auditoria, self.mostrar_ajuda]

        for i, (icone, cmd) in enumerate(zip(icones_sidebar, comandos_sidebar)):
            btn = tk.Button(frame_sidebar, text=icone, bg=self._bg_nav, fg=self._fg,
                            font=("Helvetica", 14), bd=0, cursor="hand2", command=cmd)
            btn.pack(pady=12, padx=4, fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self._sidebar))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self._bg_nav))

        # ---------- CONTEÚDO PRINCIPAL ----------
        frame_conteudo = tk.Frame(self.frame_veiculos, bg=self._bg_main)
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
        # Tipo (Combobox)
        make_label(frame_esquerdo, "Tipo:", 0)
        combo_tipo = ttk.Combobox(frame_esquerdo, font=entry_font, values=["Carro", "Moto", "Caminhão", "SUV", "Van", "Ônibus"], state="readonly")
        combo_tipo.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        combo_tipo.set(self.placeholders["Tipo"])
        self.entries_map["Tipo"] = combo_tipo

        # Marca
        make_label(frame_esquerdo, "Marca:", 2)
        entry_marca = make_entry(frame_esquerdo, 3)
        adicionar_placeholder(entry_marca, self.placeholders["Marca"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Marca"] = entry_marca

        # Modelo
        make_label(frame_esquerdo, "Modelo:", 4)
        entry_modelo = make_entry(frame_esquerdo, 5)
        adicionar_placeholder(entry_modelo, self.placeholders["Modelo"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Modelo"] = entry_modelo

        # Ano de fabricação
        make_label(frame_esquerdo, "Ano de fabricação:", 6)
        entry_ano_fab = make_entry(frame_esquerdo, 7)
        adicionar_placeholder(entry_ano_fab, self.placeholders["Ano de fabricação"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Ano de fabricação"] = entry_ano_fab

        # Ano do modelo
        make_label(frame_esquerdo, "Ano do modelo:", 8)
        entry_ano_mod = make_entry(frame_esquerdo, 9)
        adicionar_placeholder(entry_ano_mod, self.placeholders["Ano do modelo"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Ano do modelo"] = entry_ano_mod

        # Cor
        make_label(frame_esquerdo, "Cor:", 10)
        entry_cor = make_entry(frame_esquerdo, 11)
        adicionar_placeholder(entry_cor, self.placeholders["Cor"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Cor"] = entry_cor

        # Placa
        make_label(frame_esquerdo, "Placa:", 12)
        entry_placa = make_entry(frame_esquerdo, 13)
        adicionar_placeholder(entry_placa, self.placeholders["Placa"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Placa"] = entry_placa

        # Quilometragem
        make_label(frame_esquerdo, "Quilometragem:", 14)
        entry_km = make_entry(frame_esquerdo, 15)
        adicionar_placeholder(entry_km, self.placeholders["Quilometragem"], fg_placeholder=self._muted, fg_text=self._fg)
        self.entries_map["Quilometragem"] = entry_km

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

        criar_botao(frame_esquerdo, "➕ Adicionar / Salvar", self.salvar_veiculo, self._green, 17)
        criar_botao(frame_esquerdo, "✏️ Editar", self.carregar_para_edicao, self._yellow, 18)
        criar_botao(frame_esquerdo, "❌ Excluir", self.excluir_veiculo, self._red, 19)

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
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_veiculos)

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
        estilo.configure("Veiculos.Treeview",
                         background=self._panel,
                         foreground=self._fg,
                         fieldbackground=self._panel,
                         rowheight=26,
                         font=("Helvetica", 10))
        estilo.configure("Veiculos.Treeview.Heading",
                         background=self._card,
                         foreground=self._accent,
                         font=("Helvetica", 11, "bold"))
        estilo.map("Veiculos.Treeview", background=[("selected", self._accent)], foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Tipo", "Marca", "Modelo", "Ano/Fab", "Ano/Modelo", "Cor", "Placa", "Quilometragem"),
            show="headings",
            yscrollcommand=scrollbar_y.set,
            style="Veiculos.Treeview",
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
                "Tipo": 80/880,
                "Marca": 90/880,
                "Modelo": 90/880,
                "Ano/Fab": 80/880,
                "Ano/Modelo": 90/880,
                "Cor": 60/880,
                "Placa": 80/880,
                "Quilometragem": 110/880
            }
            for k, v in proporcoes.items():
                self.tree.column(k, width=int(largura_total * v))

        self.tree.bind("<Configure>", ajustar_largura_colunas)

    # ---------- Funções CRUD e navegação ----------
    def voltar_lobby(self):
        # Esconde a tela atual
        try:
            self.frame_veiculos.pack_forget()
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
        self.frame_veiculos.pack_forget()
        abrir_tela_auditoria(
            self.master, 
            self.db, 
            on_voltar_callback=self.recarregar_tela,  # callback
            usuario_logado=self.usuario_logado
        )

    def recarregar_tela(self):
        self.frame_veiculos.pack(fill="both", expand=True)
        self.carregar_veiculos()
        self.limpar_campos()


    def mostrar_ajuda(self):
        if self.janela_ajuda and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            self.janela_ajuda.focus_force()
            return

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("📘 Ajuda - Veículos")
        self.janela_ajuda.configure(bg=self._bg_main)

        largura, altura = 520, 420
        x = (self.janela_ajuda.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela_ajuda.winfo_screenheight() // 2) - (altura // 2)
        self.janela_ajuda.geometry(f"{largura}x{altura}+{x}+{y}")

        lbl_titulo = tk.Label(self.janela_ajuda, text="Ajuda - Gerenciador de Veículos",
                              bg=self._bg_main, fg=self._accent, font=("Helvetica", 14, "bold"))
        lbl_titulo.pack(pady=12)

        texto_ajuda = (
            "🚗 ADICIONAR VEÍCULO(S):\n"
            "Preencha os campos obrigatórios e clique em 'Adicionar / Salvar'.\n\n"
            "🔧 EDITAR VEÍCULO(S):\n"
            "Selecione uma linha na tabela e clique em 'Editar'.\n"
            "Altere os campos e clique em 'Adicionar / Salvar'.\n\n"
            "❌ EXCLUIR VEÍCULO(S):\n"
            "Selecione uma ou mais linhas e clique em 'Excluir'.\n\n"
            "🔍 PESQUISAR:\n"
            "Digite no campo de pesquisa para filtrar os veículos em tempo real.\n\n"
            "🕓 HISTÓRICO:\n"
            "Acompanhe todas as ações feitas pelos usuários.\n\n"
            "⬅️ VOLTAR:\n"
            "Use o botão '🏠' para retornar ao Lobby."
        )
        lbl_texto = tk.Label(self.janela_ajuda, text=texto_ajuda, bg=self._bg_main,
                             fg=self._fg, font=("Helvetica", 11), justify="left")
        lbl_texto.pack(padx=20, pady=10, fill="both", expand=True)

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
                    widget.config(fg="white")  # Valor real em preto
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

    def remover_foco(self):
        try:
            self.master.focus_set()
        except:
            pass


    def filtrar_veiculos(self, event=None):
        termo = self.entry_pesquisa.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for veiculo in self.db.pesquisar_veiculos(termo):
            self.tree.insert("", "end", values=veiculo)

    def iniciar(self):
        self.frame_veiculos.pack(fill="both", expand=True)
