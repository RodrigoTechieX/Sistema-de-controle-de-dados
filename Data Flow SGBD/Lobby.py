# Lobby.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
import threading

# Backends
from backendfilmeseseries import BancoDeDadosFilmeseSeries
from backendprodutos import BancoDeDadosProdutos
from backendveiculos import BancoDeDadosVeiculos
from backendfuncionarios import BancoDeDadosFuncionarios
from backendlivros import BancoDeDadosLivros
from backendmusicas import BancoDeDadosMusicas
from backendjogos import BancoDeDadosJogos
from backendreceitas import BancoDeDadosReceitas
from backend import BancoDeDados  # auditoria / usuário etc.

# Funções para abrir telas específicas
def abrir_tela_filmeseseries(master, frame_login, usuario_logado):
    from tela_filmeseseries import FilmeseSeries
    FilmeseSeries(master, frame_login, usuario_logado)

def abrir_tela_produtos(master, frame_login, usuario_logado):
    from tela_produtos import TelaProdutos
    TelaProdutos(master, frame_login, usuario_logado)

def abrir_tela_veiculos(master, frame_login, usuario_logado):
    from tela_veiculos import TelaVeiculos
    TelaVeiculos(master, frame_login, usuario_logado)

def abrir_tela_funcionarios(master, frame_login, usuario_logado):
    from tela_funcionarios import TelaFuncionarios
    TelaFuncionarios(master, frame_login, usuario_logado)

def abrir_tela_livros(master, frame_login, usuario_logado):
    from tela_livros import TelaLivros
    TelaLivros(master, frame_login, usuario_logado)

def abrir_tela_musicas(master, frame_login, usuario_logado):
    from tela_musicas import TelaMusicas
    TelaMusicas(master, frame_login, usuario_logado)

def abrir_tela_jogos(master, frame_login, usuario_logado):
    from tela_jogos import TelaJogos
    TelaJogos(master, frame_login, usuario_logado)

def abrir_tela_receitas(master, frame_login, usuario_logado):
    from tela_receitas import TelaReceitas
    TelaReceitas(master, frame_login, usuario_logado)

def abrir_tela_auditoria(master, db, TelaPrincipal, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, TelaPrincipal, usuario_logado)
    ts.iniciar()

# Matplotlib (opcional)
try:
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

# ----------------------- MiniCard -----------------------
class MiniCard(tk.Frame):
    """Card moderno com gráfico de barras coloridas e layout aprimorado."""
    def __init__(self, master, title, backend_instance, icon_path=None, update_interval=3000, *args, **kwargs):
        super().__init__(master, bg="#2C2F3A", bd=0, relief="flat", *args, **kwargs)
        self.title = title
        self.backend = backend_instance
        self.update_interval = update_interval
        self.icon_path = icon_path
        self.history = []
        self.dates = []

        self.configure_highlight()
        self.build_ui()
        self.after(500, self.update_values)

    def configure_highlight(self):
        self.config(highlightbackground="#44475A", highlightthickness=1, padx=12, pady=12)
        self.shadow = tk.Frame(self, bg="#1F222B")
        self.shadow.place(relx=0, rely=0, relwidth=1, relheight=1)

    def build_ui(self):
        top = tk.Frame(self, bg="#2C2F3A")
        top.pack(fill="x", anchor="n")

        if self.icon_path and os.path.exists(self.icon_path):
            try:
                img = Image.open(self.icon_path)
                img.thumbnail((32, 32), Image.LANCZOS)
                self.icon_img = ImageTk.PhotoImage(img)
                tk.Label(top, image=self.icon_img, bg="#2C2F3A").pack(side="left", padx=(0, 8))
            except Exception:
                pass

        tk.Label(top, text=self.title, font=("Segoe UI", 11, "bold"), bg="#2C2F3A", fg="#F0F6F9").pack(side="left", anchor="w")
        self.lbl_count = tk.Label(self, text="—", font=("Segoe UI", 22, "bold"), bg="#2C2F3A", fg="#00BCD4")
        self.lbl_count.pack(anchor="w", pady=(10, 2))
        tk.Label(self, text="Registros", font=("Segoe UI", 9), bg="#2C2F3A", fg="#B0BEC5").pack(anchor="w")

        if MATPLOTLIB_AVAILABLE:
            self.fig = Figure(figsize=(2.8, 1.3), dpi=100, facecolor="#2C2F3A")
            self.ax = self.fig.add_subplot(111)
            self.ax.set_facecolor("#1F222B")
            self.ax.margins(x=0)
            for spine in self.ax.spines.values():
                spine.set_visible(False)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.get_tk_widget().pack(fill="x", expand=True, pady=(8, 0))
        else:
            tk.Label(self, text="(gráfico indisponível)", font=("Arial", 8, "italic"), bg="#2C2F3A", fg="#AAA").pack(anchor="w", pady=(6, 0))

    def update_values(self):
        import datetime
        try:
            if hasattr(self.backend, "contar_registros"):
                count = self.backend.contar_registros()
            else:
                count = int(self.backend())
        except Exception:
            count = 0

        today = datetime.date.today()
        if today.strftime("%d/%m") in self.dates:
            idx = self.dates.index(today.strftime("%d/%m"))
            self.history[idx] = count
        else:
            self.dates.append(today.strftime("%d/%m"))
            self.history.append(count)

        last_7_days = [(today - datetime.timedelta(days=i)).strftime("%d/%m") for i in reversed(range(7))]
        new_dates, new_history = [], []
        for d in last_7_days:
            new_dates.append(d)
            new_history.append(self.history[self.dates.index(d)] if d in self.dates else 0)
        self.dates, self.history = new_dates, new_history

        self.lbl_count.config(text=str(count))

        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.ax.set_facecolor("#1F222B")
            self.ax.margins(x=0.05)
            self.ax.tick_params(axis="x", colors="#888", labelsize=7)
            self.ax.tick_params(axis="y", colors="#888", labelsize=7)
            for spine in self.ax.spines.values():
                spine.set_visible(False)
            colors = ["#00BCD4", "#03A9F4", "#2196F3", "#00ACC1", "#0097A7", "#00838F", "#006064"]
            self.ax.bar(self.dates, self.history, color=colors[:len(self.history)], width=0.6)
            self.ax.grid(axis="y", linestyle="--", alpha=0.2)
            self.ax.set_ylim(0, max(self.history)*1.2 if max(self.history) > 0 else 1)
            self.fig.tight_layout(pad=0.3)
            self.canvas.draw_idle()

        self.after(self.update_interval, self.update_values)

# ----------------------- TelaPrincipal -----------------------
class TelaPrincipal:
    def __init__(self, master, db, frame_login, usuario_logado):
        self.master = master
        self.db = db
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado

        self.bd_filmes = BancoDeDadosFilmeseSeries()
        self.bd_produtos = BancoDeDadosProdutos()
        self.bd_veiculos = BancoDeDadosVeiculos()
        self.bd_funcionarios = BancoDeDadosFuncionarios()
        self.bd_livros = BancoDeDadosLivros()
        self.bd_musicas = BancoDeDadosMusicas()
        self.bd_jogos = BancoDeDadosJogos()
        self.bd_receitas = BancoDeDadosReceitas()
        self.bd_auditoria = BancoDeDados()

        self.build_ui()
        self.master.bind("<Configure>", lambda e: None)
        self.master.bind("<Configure>", lambda e: self.create_gradient(self.frame_principal, "#1C1F26", "#1C1F26"))


    def remover_foco(self):
        self.frame_principal.focus_set()

    def build_ui(self):
        alterar_titulo(self.master, "Data Flow - Lobby")
        self.master.geometry("1000x600")

        # Container principal com gradiente
        self.frame_principal = tk.Canvas(self.master, bg="#1C1F26", highlightthickness=0)
        self.frame_principal.pack(fill="both", expand=True)
        self.frame_principal.update()
        self.frame_principal.after(200, lambda: self.create_gradient(self.frame_principal, "#1C1F26", "#1C1F26"))


        # Navbar
        self.navbar = tk.Frame(self.frame_principal, bg="#21252B", height=56)
        self.navbar.place(relx=0, rely=0, relwidth=1)
        lbl_logo = tk.Label(self.navbar, text="Data Flow", bg="#21252B", fg="#F0F6F9", font=("Segoe UI", 14, "bold"))
        lbl_logo.pack(side="left", padx=16)
        lbl_user = tk.Label(self.navbar, text=f"Usuário: {self.usuario_logado}", bg="#21252B", fg="#F0F6F9", font=("Segoe UI", 10))
        lbl_user.pack(side="right", padx=12)
        btn_logout = tk.Button(self.navbar, text="⬅ Voltar", bg="#0097A7", fg="white", relief="flat", command=self.voltar_login)
        btn_logout.pack(side="right", padx=12, pady=8)
        btn_logout.bind("<Enter>", lambda e: btn_logout.config(bg="#007C91"))
        btn_logout.bind("<Leave>", lambda e: btn_logout.config(bg="#0097A7"))

        # Main area
        main_area = tk.Frame(self.frame_principal, bg="#1C1F26")
        main_area.place(x=0, y=56, relwidth=1, relheight=1, height=-56)

        # Sidebar
        sidebar = tk.Frame(main_area, bg="#2C2F3A", width=220)
        sidebar.pack(side="left", fill="y", padx=(12,8), pady=12)
        sidebar.pack_propagate(False)

        base_path = os.path.dirname(__file__)
        def icon_path(name):
            p = os.path.join(base_path, "icones-lobby", name)
            return p if os.path.exists(p) else None

        items = [
            ("🎬", "Filmes / Séries", self.ir_para_filmes, "icone-midias.png"),
            ("🛒", "Produtos", self.ir_para_produtos, "icone-produtos.png"),
            ("🚗", "Veículos", self.ir_para_veiculos, "icone-veiculos.png"),
            ("👔", "Funcionários", self.ir_para_funcionarios, "icone-funcionarios.png"),
            ("📚", "Livros", self.ir_para_livros, "icone-livros.png"),
            ("🎵", "Músicas", self.ir_para_musicas, "icone-musicas.png"),
            ("🎮", "Jogos", self.ir_para_jogos, "icone-jogos.png"),
            ("🍳", "Receitas", self.ir_para_receitas, "icone-receitas.png"),
            ("📝", "Histórico", self.ir_para_auditoria, "icone-historico.png"),
        ]

        for emoji, text, cmd, icon_file in items:
            frame_btn = tk.Frame(sidebar, bg="#2C2F3A")
            frame_btn.pack(fill="x", padx=8, pady=6)
            tkimg = None
            ic_path = icon_path(icon_file)
            if ic_path:
                try:
                    pil = Image.open(ic_path)
                    pil.thumbnail((24, 24), Image.LANCZOS)
                    tkimg = ImageTk.PhotoImage(pil)
                except Exception:
                    tkimg = None
            if tkimg:
                btn = tk.Button(frame_btn, text="  "+text, image=tkimg, compound="left",
                                anchor="w", padx=8, font=("Segoe UI", 10), bg="#2C2F3A", fg="#FFFFFF",
                                relief="flat", bd=0, command=cmd, cursor="hand2")
                btn.image = tkimg
            else:
                btn = tk.Button(frame_btn, text=f"{emoji}  {text}", anchor="w",
                                padx=8, font=("Segoe UI", 12), bg="#2C2F3A", fg="#F0F6F9",
                                relief="flat", bd=0, command=cmd, cursor="hand2")
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#21252B"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#2C2F3A"))

        # Conteúdo principal (cards)
        content = tk.Frame(main_area, bg="#1C1F26")
        content.pack(fill="both", expand=True, padx=(8,12), pady=12)

        self.cards_frame = tk.Frame(content, bg="#1C1F26")
        self.cards_frame.pack(fill="both", expand=True)

        card_defs = [
            ("Filmes / Séries", self.bd_filmes, icon_path("cadastrodefilmeseseries (3).png")),
            ("Produtos", self.bd_produtos, icon_path("cadastrodeprodutos.png")),
            ("Veículos", self.bd_veiculos, icon_path("cadastrodeveiculos.png")),
            ("Funcionários", self.bd_funcionarios, icon_path("cadastrodefuncionarios.png")),
            ("Livros", self.bd_livros, icon_path("cadastrodelivros.png")),
            ("Músicas", self.bd_musicas, icon_path("cadastrodemusicas.png")),
            ("Jogos", self.bd_jogos, icon_path("cadastrodejogos.png")),
            ("Receitas", self.bd_receitas, icon_path("cadastrodereceitas.png")),
            ("Histórico", self.bd_auditoria, icon_path("usuariosistema.png")),
        ]

        self.cards = []
        cols = 3
        for idx, (title, backend_inst, iconp) in enumerate(card_defs):
            r = idx // cols
            c = idx % cols
            card = MiniCard(self.cards_frame, title, backend_inst, iconp, update_interval=3000)
            card.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
            self.cards.append(card)

        rows = (len(card_defs)+cols-1)//cols
        for i in range(rows):
            self.cards_frame.grid_rowconfigure(i, weight=1)
        for j in range(cols):
            self.cards_frame.grid_columnconfigure(j, weight=1)

        self.frame_principal.after(100, self.remover_foco)

    # Gradiente
    def create_gradient(self, canvas, color1, color2, offset=56):
        canvas.delete("gradient")
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        (r1,g1,b1) = canvas.winfo_rgb(color1)
        (r2,g2,b2) = canvas.winfo_rgb(color2)

        limit = height - offset

        r_ratio = float(r2-r1)/limit
        g_ratio = float(g2-g1)/limit
        b_ratio = float(b2-b1)/limit

        for i in range(limit):
            nr = int(r1 + (r_ratio*i))
            ng = int(g1 + (g_ratio*i))
            nb = int(b1 + (b_ratio*i))
            color = f'#{nr>>8:02x}{ng>>8:02x}{nb>>8:02x}'

            canvas.create_line(0, i + offset, width, i + offset, fill=color, tags="gradient")


    # ---------- navegações ----------
    def ir_para_filmes(self):
        self.frame_principal.pack_forget()
        abrir_tela_filmeseseries(self.master, self.frame_login, self.usuario_logado)

    def ir_para_produtos(self):
        self.frame_principal.pack_forget()
        abrir_tela_produtos(self.master, self.frame_login, self.usuario_logado)

    def ir_para_veiculos(self):
        self.frame_principal.pack_forget()
        abrir_tela_veiculos(self.master, self.frame_login, self.usuario_logado)

    def ir_para_funcionarios(self):
        self.frame_principal.pack_forget()
        abrir_tela_funcionarios(self.master, self.frame_login, self.usuario_logado)

    def ir_para_livros(self):
        self.frame_principal.pack_forget()
        abrir_tela_livros(self.master, self.frame_login, self.usuario_logado)

    def ir_para_musicas(self):
        self.frame_principal.pack_forget()
        abrir_tela_musicas(self.master, self.frame_login, self.usuario_logado)

    def ir_para_jogos(self):
        self.frame_principal.pack_forget()
        abrir_tela_jogos(self.master, self.frame_login, self.usuario_logado)

    def ir_para_receitas(self):
        self.frame_principal.pack_forget()
        abrir_tela_receitas(self.master, self.frame_login, self.usuario_logado)

    def ir_para_auditoria(self):
        self.frame_principal.pack_forget()
        abrir_tela_auditoria(self.master, self.db, self.frame_principal, self.usuario_logado)

    def voltar_login(self):
        self.frame_principal.pack_forget()
        self.frame_login.pack(fill="both", expand=True)
        alterar_titulo(self.master, "Data Flow - Sistema de gerenciamento de dados")

# ----------------------- utilitário -----------------------
def alterar_titulo(janela, novo_titulo):
    try:
        janela.title(novo_titulo)
    except Exception:
        pass
