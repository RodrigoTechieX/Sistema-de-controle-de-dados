# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
from backend import BancoDeDados
import threading
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Observação: imports usados dentro de exportar_pdf (ImageReader, tempfile, webbrowser, BytesIO, etc.)
# são mantidos dentro da função conforme seu código original.


def abrir_tela_principal(master, db, frame_login):
    from Lobby import TelaPrincipal
    ts = TelaPrincipal(master, db, frame_login)
    ts.iniciar()


class TelaAuditoria:
    ALTURA_NAVBAR = 0.10  # altura relativa (10%)

    def __init__(self, master, db, on_voltar_callback, usuario_logado):
        self.master = master
        self.db = db
        self.on_voltar_callback = on_voltar_callback
        self.usuario_logado = usuario_logado

        # frame principal
        self.frame_auditoria = tk.Frame(self.master, bg="#0F1518")
        self.frame_auditoria.pack(fill="both", expand=True)

        # canvas de fundo para gradiente
        self._bg_canvas = tk.Canvas(self.frame_auditoria, highlightthickness=0)
        self._bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # configura e monta a interface
        self.setup_tela()
        self.carregar_auditoria()

        # redimensiona gradiente ao redimensionar janela
        def _on_resize(event):
            try:
                self._create_gradient(self._bg_canvas, "#1C1F26", "#0B3A52",
                                      offset=int(self.ALTURA_NAVBAR * self.frame_auditoria.winfo_height()))
            except Exception:
                pass

        self.master.bind("<Configure>", _on_resize)

    # -------------------- AJUDA --------------------
    def mostrar_ajuda(self):
        # impede múltiplas janelas de ajuda
        if getattr(self, "janela_ajuda", None) and self.janela_ajuda.winfo_exists():
            self.janela_ajuda.lift()
            return

        ajuda_texto = (
            "📘 AJUDA - HISTÓRICO\n\n"
            "Nesta tela, você pode visualizar todas as alterações feitas no sistema.\n\n"
            "🔍 Pesquisa:\n"
            "Digite um termo para filtrar registros.\n\n"
            "✅ Restaurar Selecionados:\n"
            "Restaura registros que foram EXCLUÍDOS.\n\n"
            "📄 Exportar PDF:\n"
            "Gera um relatório em PDF dos registros selecionados.\n\n"
            "✖️ Excluir Selecionados:\n"
            "Remove registros do histórico permanentemente.\n\n"
            "⚙️ Navegação:\n"
            "Use o botão de voltar (⬅) para retornar ao lobby."
        )

        self.janela_ajuda = tk.Toplevel(self.master)
        self.janela_ajuda.title("Ajuda - Histórico")
        self.janela_ajuda.resizable(False, False)

        # Janela com tema escuro-coerente
        self.janela_ajuda.configure(bg="#17181B")
        largura = 520
        altura = 420
        self.janela_ajuda.geometry(f"{largura}x{altura}")
        self.janela_ajuda.update_idletasks()
        x = (self.janela_ajuda.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.janela_ajuda.winfo_screenheight() // 2) - (altura // 2)
        self.janela_ajuda.geometry(f"{largura}x{altura}+{x}+{y}")

        def ao_fechar():
            if self.janela_ajuda and self.janela_ajuda.winfo_exists():
                self.janela_ajuda.destroy()
            self.janela_ajuda = None

        self.janela_ajuda.protocol("WM_DELETE_WINDOW", ao_fechar)

        label_header = tk.Label(
            self.janela_ajuda, text="❓ AJUDA - HISTÓRICO",
            font=("Helvetica", 14, "bold"),
            bg="#0F1720", fg="#80CFFF", padx=12, pady=8
        )
        label_header.pack(fill="x", padx=12, pady=(12, 6))

        text_frame = tk.Frame(self.janela_ajuda, bg="#0F1720")
        text_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        text_widget = tk.Text(
            text_frame, wrap="word",
            bg="#0F1720", fg="#E6F5FF", font=("Helvetica", 11),
            bd=0, padx=8, pady=8, relief="flat", highlightthickness=0
        )
        text_widget.insert("1.0", ajuda_texto)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

        btn_close = tk.Button(
            self.janela_ajuda, text="Fechar",
            command=ao_fechar,
            font=("Helvetica", 10, "bold"),
            bg="#007ACC", fg="white", activebackground="#009EFF",
            bd=0, padx=10, pady=6, cursor="hand2"
        )
        btn_close.pack(pady=(0, 12))

    # -------------------- UI principal --------------------
    def setup_tela(self):
        diretorio_atual = os.path.dirname(__file__)

        self.master.title("Data Flow - Histórico de Auditoria")


        # cria gradiente inicial
        self._create_gradient(self._bg_canvas, "#1C1F26", "#0B3A52", offset=int(self.ALTURA_NAVBAR * self.frame_auditoria.winfo_height()))

        # NAVBAR superior (estilizada)
        frame_navbar = tk.Frame(self.frame_auditoria, bg="#21252B", height=56)
        frame_navbar.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=self.ALTURA_NAVBAR)

        titulo = tk.Label(
            frame_navbar,
            text="Histórico de Auditoria",
            font=("Helvetica", 14, "bold"),
            fg="#80CFFF",
            bg="#21252B"
        )
        titulo.place(relx=0.5, rely=0.5, anchor="center")

        # Ícone do usuário (se existir)
        caminho_imagem_usuario = os.path.join(diretorio_atual, "imagens", "usuariosistema.png")
        try:
            imagem_usuario = Image.open(caminho_imagem_usuario).resize((18, 18), Image.LANCZOS)
            self.icone_usuario = ImageTk.PhotoImage(imagem_usuario)
        except Exception:
            self.icone_usuario = None

        # Botão de ajuda
        btn_ajuda = tk.Button(
            frame_navbar,
            text="❓",
            font=("Helvetica", 12, "bold"),
            bg="#21252B",
            fg="white",
            borderwidth=0,
            cursor="hand2",
            command=self.mostrar_ajuda,
            activebackground="#1b262b",
            relief="flat"
        )

        # posição dinâmica do botão de ajuda (igual à sua lógica)
        comprimento_nome = len(self.usuario_logado)
        if comprimento_nome <= 10:
            pos_ajuda = 0.88
        elif comprimento_nome <= 20:
            pos_ajuda = 0.80
        elif comprimento_nome <= 30:
            pos_ajuda = 0.75
        elif comprimento_nome <= 40:
            pos_ajuda = 0.70
        else:
            pos_ajuda = 0.65
        btn_ajuda.place(relx=pos_ajuda, rely=0.5, anchor="e")

        # Usuário (lado direito)
        label_usuario = tk.Label(
            frame_navbar,
            text=f"{self.usuario_logado}",
            font=("Helvetica", 11, "bold"),
            bg="#21252B",
            fg="#E6F5FF",
            image=self.icone_usuario,
            compound="left",
            padx=6
        )
        label_usuario.place(relx=0.98, rely=0.5, anchor="e")

        # Botão voltar (ícone à esquerda)
        try:
            caminho_voltar = os.path.join(diretorio_atual, "imagens", "voltar.png")
            imagem_voltar = Image.open(caminho_voltar).resize((60, 25), Image.LANCZOS)
            self.icone_voltar = ImageTk.PhotoImage(imagem_voltar)
        except Exception:
            self.icone_voltar = None

        btn_voltar = tk.Button(
            frame_navbar,
            image=self.icone_voltar,
            command=self.voltar_lobby,
            bg="#21252B",
            borderwidth=0,
            cursor="hand2",
            relief="flat"
        )
        btn_voltar.place(relx=0.02, rely=0.5, anchor="w")

        # CONTEÚDO principal
        frame_conteudo = tk.Frame(self.frame_auditoria, bg="#0F1518")
        frame_conteudo.place(relx=0.0, rely=self.ALTURA_NAVBAR, relwidth=1.0, relheight=1 - self.ALTURA_NAVBAR)

        # topo: pesquisa e botões
        frame_topo_auditoria = tk.Frame(frame_conteudo, bg="#0F1518")
        frame_topo_auditoria.pack(fill="x", pady=(18, 6), padx=12)

        # pesquisa: container com leve borda e fundo escuro
        frame_pesquisa = tk.Frame(frame_topo_auditoria, bg="#15181B", bd=0, highlightthickness=1, highlightbackground="#232B33")
        frame_pesquisa.pack(side="left", padx=(0, 6))

        try:
            caminho_imagem_lupa = os.path.join(diretorio_atual, 'imagens', 'lupa2.0.png')
            imagem_lupa = Image.open(caminho_imagem_lupa).resize((18, 18), Image.LANCZOS)
            self.icone_pesquisa = ImageTk.PhotoImage(imagem_lupa)
        except Exception:
            self.icone_pesquisa = None

        label_lupa = tk.Label(frame_pesquisa, image=self.icone_pesquisa, bg="#15181B")
        label_lupa.pack(side="left", padx=8, pady=6)

        # Campo de pesquisa com placeholder
        self.entry_pesquisa = tk.Entry(
            frame_pesquisa, width=36, font=("Helvetica", 11),
            bg="#0F1518", bd=0, relief="flat", fg="#9BA9B6", insertbackground="#E6F5FF"
        )
        self.entry_pesquisa.pack(side="left", padx=(0, 10), pady=6)
        placeholder_text = "Digite para pesquisar"
        self.entry_pesquisa.insert(0, placeholder_text)

        def on_entry_click(event):
            if self.entry_pesquisa.get() == placeholder_text:
                self.entry_pesquisa.delete(0, "end")
                self.entry_pesquisa.config(fg="#E6F5FF")

        def on_focusout(event):
            if self.entry_pesquisa.get().strip() == "":
                self.entry_pesquisa.insert(0, placeholder_text)
                self.entry_pesquisa.config(fg="#9BA9B6")

        self.entry_pesquisa.bind("<FocusIn>", on_entry_click)
        self.entry_pesquisa.bind("<FocusOut>", on_focusout)
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_auditoria)

        # Botões principais estilizados (usando ttk style para aparência consistente)
        frame_botoes = tk.Frame(frame_topo_auditoria, bg="#0F1518")
        frame_botoes.pack(side="left", padx=(12, 0))

        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except Exception:
            pass

        # --- BOTÃO RESTAURAR ---
        estilo.configure(
            "Aud.Restaurar.TButton",
            font=("Helvetica", 10, "bold"),
            padding=6,
            background="#00B050",  # verde padrão
            foreground="white"
        )
        estilo.map(
            "Aud.Restaurar.TButton",
            background=[("active", "#00D95A")],  # hover mais claro
            foreground=[("active", "white")]
        )

        # --- BOTÃO EXPORTAR ---
        estilo.configure(
            "Aud.Exportar.TButton",
            font=("Helvetica", 10, "bold"),
            padding=6,
            background="#007ACC",
            foreground="white"
        )
        estilo.map(
            "Aud.Exportar.TButton",
            background=[("active", "#009EFF")],
            foreground=[("active", "white")]
        )

        # --- BOTÃO EXCLUIR ---
        estilo.configure(
            "Aud.Excluir.TButton",
            font=("Helvetica", 10, "bold"),
            padding=6,
            background="#D9534F",
            foreground="white"
        )
        estilo.map(
            "Aud.Excluir.TButton",
            background=[("active", "#C9302C")],
            foreground=[("active", "white")]
        )

        # Botões principais
        btn_restaurar = ttk.Button(
            frame_botoes,
            text="✅ Restaurar Selecionados",
            style="Aud.Restaurar.TButton",
            command=self.restaurar_dados
        )
        btn_restaurar.pack(side="left", padx=6)

        btn_exportar = ttk.Button(
            frame_botoes,
            text="📄 Exportar PDF",
            style="Aud.Exportar.TButton",
            command=self.exportar_pdf
        )
        btn_exportar.pack(side="left", padx=6)

        btn_excluir = ttk.Button(
            frame_botoes,
            text="✖️ Excluir Selecionados",
            style="Aud.Excluir.TButton",
            command=self.excluir_registro
        )
        btn_excluir.pack(side="left", padx=6)


        # TABELA de auditoria
        frame_tabela = tk.Frame(frame_conteudo, bg="#0F1518")
        frame_tabela.pack(fill="both", expand=True, padx=12, pady=(12, 12))

        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical")
        scrollbar.pack(side="right", fill="y", padx=(0, 4))

        self.tree_auditoria = ttk.Treeview(
            frame_tabela,
            columns=("ID", "Usuário", "Operação", "Tabela", "Dados", "Data e Hora"),
            show="headings", yscrollcommand=scrollbar.set, selectmode="extended",
            style="Auditoria.Treeview"
        )
        scrollbar.config(command=self.tree_auditoria.yview)

        # Cabeçalhos com estilo
        colunas = [
            ("ID", 60, "center"),
            ("Usuário", 160, "center"),
            ("Operação", 140, "center"),
            ("Tabela", 120, "center"),
            ("Dados", 360, "w"),
            ("Data e Hora", 160, "center")
        ]
        for col, width, anchor in colunas:
            self.tree_auditoria.heading(col, text=col)
            self.tree_auditoria.column(col, anchor=anchor, width=width)

        estilo.configure("Auditoria.Treeview",
                         background="#0F1518",
                         foreground="#E6F5FF",
                         fieldbackground="#0F1518",
                         rowheight=26,
                         font=("Helvetica", 10))
        estilo.configure("Auditoria.Treeview.Heading",
                         background="#131A20",
                         foreground="#80CFFF",
                         font=("Helvetica", 11, "bold"))
        estilo.map("Auditoria.Treeview", background=[("selected", "#007ACC")], foreground=[("selected", "white")])

        # zebra striping
        self.tree_auditoria.tag_configure('oddrow', background="#0F171A")
        self.tree_auditoria.tag_configure('evenrow', background="#101B1E")

        self.tree_auditoria.pack(fill="both", expand=True)

    # -------------------- Carregamento / Filtro --------------------
    def carregar_auditoria(self):
        self.tree_auditoria.delete(*self.tree_auditoria.get_children())
        registros = self.db.consultar_auditoria()
        toggle = 0
        for r in registros:
            tag = 'evenrow' if toggle % 2 == 0 else 'oddrow'
            self.tree_auditoria.insert("", "end", values=r, tags=(tag,))
            toggle += 1

    def filtrar_auditoria(self, event):
        filtro = self.entry_pesquisa.get().lower()
        self.tree_auditoria.delete(*self.tree_auditoria.get_children())
        registros = self.db.pesquisar_auditoria(filtro)
        toggle = 0
        for r in registros:
            tag = 'evenrow' if toggle % 2 == 0 else 'oddrow'
            self.tree_auditoria.insert("", "end", values=r, tags=(tag,))
            toggle += 1

    # -------------------- Restauração (sem alterações lógicas) --------------------
    def restaurar_dados(self):
        selecionados = self.tree_auditoria.selection()
        if not selecionados:
            messagebox.showinfo("Aviso", "Selecione pelo menos um registro do tipo 'EXCLUÍDO' para restaurar.")
            return

        registros_excluidos = []
        for item in selecionados:
            valores = self.tree_auditoria.item(item, "values")
            if len(valores) >= 3 and str(valores[2]).strip().upper() == "EXCLUÍDO":
                registros_excluidos.append(valores)

        if not registros_excluidos:
            messagebox.showinfo("Aviso", "Nenhum dos registros selecionados é do tipo 'EXCLUÍDO'.")
            return

        if not messagebox.askyesno("Confirmação", f"Deseja restaurar {len(registros_excluidos)} registro(s)?"):
            return

        sucesso, falha = 0, 0
        erros = []

        for valores in registros_excluidos:
            try:
                id_auditoria = valores[0]
                tabela = valores[3]
                dados = valores[4]
                usuario = self.usuario_logado

                # Descobre qual banco deve ser chamado com base na tabela (mesma lógica sua)
                if tabela.lower() == "midias":
                    from backendfilmeseseries import BancoDeDadosFilmeseSeries
                    db_alvo = BancoDeDadosFilmeseSeries()
                elif tabela.lower() == "funcionarios":
                    from backendfuncionarios import BancoDeDadosFuncionarios
                    db_alvo = BancoDeDadosFuncionarios()
                elif tabela.lower() == "jogos":
                    from backendjogos import BancoDeDadosJogos
                    db_alvo = BancoDeDadosJogos()
                elif tabela.lower() == "livros":
                    from backendlivros import BancoDeDadosLivros
                    db_alvo = BancoDeDadosLivros()
                elif tabela.lower() == "musicas":
                    from backendmusicas import BancoDeDadosMusicas
                    db_alvo = BancoDeDadosMusicas()
                elif tabela.lower() == "produtos":
                    from backendprodutos import BancoDeDadosProdutos
                    db_alvo = BancoDeDadosProdutos()
                elif tabela.lower() == "receitas":
                    from backendreceitas import BancoDeDadosReceitas
                    db_alvo = BancoDeDadosReceitas()
                elif tabela.lower() == "veiculos":
                    from backendveiculos import BancoDeDadosVeiculos
                    db_alvo = BancoDeDadosVeiculos()
                else:
                    raise ValueError(f"Tabela '{tabela}' não reconhecida.")

                retorno = db_alvo.restaurar_dados(tabela, dados, usuario)

                if retorno is True or (isinstance(retorno, tuple) and retorno[0] is True):
                    sucesso += 1
                else:
                    falha += 1
                    erros.append(f"ID {id_auditoria}: falha ao restaurar.")
            except Exception as e:
                falha += 1
                erros.append(f"ID {valores[0]}: Erro {e}")

        msg_final = f"{sucesso} registro(s) restaurado(s) com sucesso."
        if falha:
            msg_final += f"\n{falha} falharam:\n" + "\n".join(erros[:10])
        messagebox.showinfo("Resultado da Restauração", msg_final)
        self.carregar_auditoria()

    # -------------------- Exclusão --------------------
    def excluir_registro(self):
        selecionados = self.tree_auditoria.selection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um registro para excluir!")
            return

        if not messagebox.askyesno("Confirmação", f"Excluir {len(selecionados)} registro(s)?"):
            return

        ids = [self.tree_auditoria.item(i)["values"][0] for i in selecionados]
        try:
            self.db.excluir_varios_registros_auditoria(ids)
            messagebox.showinfo("Sucesso", "Registros excluídos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir: {e}")
        self.carregar_auditoria()

    # -------------------- Exportar PDF (mantido) --------------------
    def exportar_pdf(self):
        """
        Gera um relatório de auditoria em PDF em memória, mas solicita confirmação antes.
        (Lógica mantida como estava no seu código original.)
        """

        from io import BytesIO
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
        from datetime import datetime
        import os
        from tkinter import messagebox
        import tempfile, webbrowser

        confirmar = messagebox.askyesno(
            "Confirmação",
            "Deseja realmente gerar o PDF com os registros selecionados?"
        )
        if not confirmar:
            return

        registros = [self.tree_auditoria.item(item)["values"] for item in self.tree_auditoria.selection()]

        if not registros:
            messagebox.showwarning("Aviso", "Não há registros para exportar!")
            return

        buffer_pdf = BytesIO()
        topo_imagem_path = os.path.join(os.path.dirname(__file__), "imagens", "logoparapdf.png")

        doc = SimpleDocTemplate(
            buffer_pdf,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=170,
            bottomMargin=30,
            title="Relatório de Histórico"
        )

        styles = getSampleStyleSheet()
        styleN = styles["Normal"]

        dados_tabela = [["ID", "Usuário", "Operação", "Tabela", "Dados", "Data / Hora"]]

        for r in registros:
            data_hora_raw = str(r[5]) if len(r) > 5 else ""
            data_part, hora_part = "", ""
            try:
                if data_hora_raw.strip():
                    dt = datetime.strptime(data_hora_raw, "%Y-%m-%d %H:%M:%S")
                    data_part = dt.strftime("%d/%m/%Y")
                    hora_part = dt.strftime("%H:%M")
            except ValueError:
                if " " in data_hora_raw:
                    data_part, hora_part = data_hora_raw.split(" ", 1)
                else:
                    data_part = data_hora_raw

            from reportlab.lib.enums import TA_CENTER
            style_center = styles["Normal"].clone('centered')
            style_center.alignment = TA_CENTER
            data_hora_junto = f"{data_part}<br/>{hora_part}"

            dados_tabela.append([
                r[0],
                r[1],
                r[2],
                r[3],
                Paragraph(str(r[4]), styleN),
                Paragraph(data_hora_junto, style_center)
            ])

        largura_pagina, _ = A4
        largura_util = largura_pagina - doc.leftMargin - doc.rightMargin

        total_col_widths = 30 + 60 + 65 + 60 + 200 + 75
        col_widths = [
            largura_util * 30 / total_col_widths,
            largura_util * 60 / total_col_widths,
            largura_util * 65 / total_col_widths,
            largura_util * 60 / total_col_widths,
            largura_util * 200 / total_col_widths,
            largura_util * 75 / total_col_widths,
        ]

        table = Table(dados_tabela, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 1), (3, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            ('VALIGN', (0, 1), (3, -1), 'MIDDLE'),
            ('VALIGN', (5, 1), (5, -1), 'MIDDLE'),
            ('VALIGN', (4, 1), (4, -1), 'TOP'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        def cabecalho(canvas, doc):
            largura_pagina, altura_pagina = A4
            try:
                if os.path.exists(topo_imagem_path):
                    img = ImageReader(topo_imagem_path)
                    iw, ih = img.getSize()
                    proporcao = ih / iw
                    escala = 0.9
                    altura_img = largura_pagina * proporcao * escala

                    canvas.drawImage(
                        topo_imagem_path,
                        x=0,
                        y=altura_pagina - altura_img - 10,
                        width=largura_pagina,
                        height=altura_img,
                        preserveAspectRatio=True,
                        mask='auto'
                    )
            except Exception as e:
                print(f"Erro ao carregar imagem do topo: {e}")

            canvas.setFont("Helvetica-Bold", 16)
            canvas.drawString(200, altura_pagina - 110, "Relatório de Histórico")

            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(30, altura_pagina - 155, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')} às {datetime.now().strftime('%H:%M:%S')}")
            canvas.drawString(30, altura_pagina - 170, f"Gerado por: {self.usuario_logado}")

        doc.build([table], onFirstPage=cabecalho, onLaterPages=cabecalho)
        buffer_pdf.seek(0)
        pdf_bytes = buffer_pdf.getvalue()

        temp_path = os.path.join(tempfile.gettempdir(), "Relatório de Histórico.pdf")
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)

        webbrowser.open_new(temp_path)
        messagebox.showinfo("Sucesso", "PDF gerado em memória e aberto automaticamente!")

    # -------------------- Voltar / iniciar --------------------
    # Na TelaAuditoria:
    def voltar_lobby(self):
        self.frame_auditoria.pack_forget()
        
        # Chama a função de callback se existir
        if self.on_voltar_callback:
            try:
                self.on_voltar_callback()  # chama a função que a tela que abriu Auditoria passou
                # Ajusta título se necessário
                if hasattr(self, "titulo_origem"):
                    self.master.title(self.titulo_origem)
            except Exception as e:
                print(f"Erro ao voltar: {e}")



    def iniciar(self):
        self.frame_auditoria.pack(fill="both", expand=True)

    # -------------------- Utilitário: gradiente --------------------
    def _create_gradient(self, canvas, color1, color2, offset=56):
        # desenha linhas horizontais para simular gradiente
        canvas.delete("gradient")
        width = canvas.winfo_width() or self.frame_auditoria.winfo_width() or 1000
        height = canvas.winfo_height() or self.frame_auditoria.winfo_height() or 600
        limit = max(1, height - offset)

        try:
            (r1, g1, b1) = self.frame_auditoria.winfo_rgb(color1)
            (r2, g2, b2) = self.frame_auditoria.winfo_rgb(color2)
        except Exception:
            (r1, g1, b1) = (0, 0, 0)
            (r2, g2, b2) = (0, 0, 0)

        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f'#{nr>>8:02x}{ng>>8:02x}{nb>>8:02x}'
            canvas.create_line(0, i + offset, width, i + offset, fill=color, tags="gradient")
