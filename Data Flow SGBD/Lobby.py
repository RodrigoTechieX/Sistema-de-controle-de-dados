# Lobby.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
import threading
import json
from pathlib import Path
import datetime

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

def abrir_tela_filmeseseries(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_filmeseseries import FilmeseSeries
    # agora passamos o callback para a classe
    ts = FilmeseSeries(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts


def abrir_tela_produtos(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_produtos import TelaProdutos
    ts = TelaProdutos(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts



def abrir_tela_veiculos(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_veiculos import TelaVeiculos
    ts = TelaVeiculos(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts

def abrir_tela_funcionarios(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_funcionarios import TelaFuncionarios
    ts = TelaFuncionarios(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts

def abrir_tela_livros(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_livros import TelaLivros
    ts = TelaLivros(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts

def abrir_tela_musicas(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_musicas import TelaMusicas
    ts = TelaMusicas(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts

def abrir_tela_jogos(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_jogos import TelaJogos
    ts = TelaJogos(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts

def abrir_tela_receitas(master, frame_login, usuario_logado, on_voltar_callback=None):
    from tela_receitas import TelaReceitas
    ts = TelaReceitas(master, frame_login, usuario_logado, on_voltar_callback=on_voltar_callback)
    return ts

def abrir_tela_auditoria(master, db, on_voltar_callback, usuario_logado):
    from Auditoria import TelaAuditoria
    ts = TelaAuditoria(master, db, on_voltar_callback, usuario_logado)
    ts.titulo_origem = "Data Flow - Lobby"
    ts.iniciar()
    return ts  # retorna a instância inteira



def carregar_lobby(self):
    for item in self.tree.get_children():
        self.tree.delete(item)
    lobby = self.db.consultar_lobby()
    for lobby in lobby:
        self.tree.insert("", "end", values=lobby)


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
    """Card moderno com gráfico de barras coloridas e histórico persistido em JSON."""
    def __init__(self, master, title, backend_instance, icon_path=None, update_interval=3000, *args, **kwargs):
        super().__init__(master, bg="#2C2F3A", bd=0, relief="flat", *args, **kwargs)
        self.title = title
        self.backend = backend_instance
        self.update_interval = update_interval
        self.icon_path = icon_path

        # histórico em memória
        self.history = []
        self.dates = []
        self.last_total = None

        # pasta para salvar os JSONs
        self.storage_dir = Path(os.path.dirname(__file__)) / "lobby_data"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        # nome do arquivo baseado no título (sanitize)
        safe_name = "".join(c for c in self.title if c.isalnum() or c in (" ", "_")).rstrip()
        self.storage_file = self.storage_dir / f"mini_card_{safe_name.replace(' ','_').lower()}.json"

        self.configure_highlight()
        self.build_ui()

        # Carrega histórico do disco (se existir)
        self.load_history_from_disk()

        # Se não tinha last_total salvo, inicializa com o total atual do backend (sem gerar pico)
        try:
            if hasattr(self.backend, "contar_registros"):
                initial_total = int(self.backend.contar_registros())
            else:
                # Se o backend for callable sem método, tenta chamá-lo
                initial_total = int(self.backend())
        except Exception:
            initial_total = 0

        if self.last_total is None:
            # Evita contabilizar um pico na primeira inicialização
            self.last_total = initial_total
            # salva para garantir que exista um last_total persistido
            self.save_history_to_disk()

        # começa a atualizar
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

    # ---------- persistence ----------
    def load_history_from_disk(self):
        try:
            if self.storage_file.exists():
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.last_total = data.get("last_total")
                self.dates = data.get("dates", [])
                self.history = data.get("history", [])
            else:
                # arquivo não existe: manter listas vazias
                self.last_total = None
                self.dates = []
                self.history = []
        except Exception as e:
            # erro ao ler: ignora e inicializa vazio
            print(f"Erro ao carregar histórico {self.storage_file}: {e}")
            self.last_total = None
            self.dates = []
            self.history = []

    def save_history_to_disk(self):
        try:
            data = {
                "last_total": self.last_total,
                "dates": self.dates,
                "history": self.history
            }
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico {self.storage_file}: {e}")

    # ---------- atualização ----------
    def update_values(self):
        try:
            if hasattr(self.backend, "contar_registros"):
                total_count = int(self.backend.contar_registros())
            else:
                total_count = int(self.backend())
        except Exception:
            total_count = 0

        today = datetime.date.today().strftime("%d/%m")

        # calcula quantos foram adicionados desde a última leitura
        if self.last_total is None:
            # se por algum motivo estiver None, inicializa e não conta como adicionado
            self.last_total = total_count
            added_today = 0
        else:
            added_today = total_count - self.last_total
            if added_today < 0:
                # se houve exclusão, evita negativo (ou pode registrar como 0)
                added_today = 0

        # atualiza last_total para próxima execução
        self.last_total = total_count

        # atualiza histórico: adiciona somente o que entrou hoje (mantendo acumulado do mesmo dia)
        if today in self.dates:
            idx = self.dates.index(today)
            self.history[idx] = self.history[idx] + added_today
        else:
            self.dates.append(today)
            self.history.append(added_today)

        # mantém só últimos 7 dias
        if len(self.dates) > 7:
            self.dates = self.dates[-7:]
            self.history = self.history[-7:]

        # salva no disco
        self.save_history_to_disk()

        # atualiza a visualização do card
        self.lbl_count.config(text=str(total_count))

        if MATPLOTLIB_AVAILABLE:
            self.ax.clear()
            self.ax.set_facecolor("#1F222B")
            for spine in self.ax.spines.values():
                spine.set_visible(False)
            self.ax.margins(x=0.05)
            self.ax.tick_params(axis="x", colors="#888", labelsize=7)
            self.ax.tick_params(axis="y", colors="#888", labelsize=7)
            colors = ["#00BCD4", "#03A9F4", "#2196F3", "#00ACC1", "#0097A7", "#00838F", "#006064"]
            self.ax.bar(self.dates, self.history, color=colors[:len(self.history)], width=0.6)
            self.ax.grid(axis="y", linestyle="--", alpha=0.2)
            max_val = max(self.history) if self.history else 1
            # evita set_ylim(0,0)
            if max_val <= 0:
                max_val = 1
            self.ax.set_ylim(0, max_val * 1.2)
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
            ("ℹ️", "Créditos", self.ir_para_creditos, "icone-creditos.png"),

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
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#007C91"))
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
        # esconde a tela principal mas não a destrói
        self.frame_principal.pack_forget()
        # abre a tela de filmes e passa um callback para voltar rapidamente ao lobby
        # a função abrir_tela_filmeseseries agora retorna a instância da tela
        self.filmes_tela = abrir_tela_filmeseseries(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.filmes_tela, "iniciar"):
                self.filmes_tela.iniciar()
        except Exception:
            pass


    def ir_para_produtos(self):
        self.frame_principal.pack_forget()
        self.produtos_tela = abrir_tela_produtos(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.produtos_tela, "iniciar"):
                self.produtos_tela.iniciar()
        except Exception:
            pass

    def ir_para_veiculos(self):
        self.frame_principal.pack_forget()
        self.veiculos_tela = abrir_tela_veiculos(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.veiculos_tela, "iniciar"):
                self.veiculos_tela.iniciar()
        except Exception:
            pass

    def ir_para_funcionarios(self):
        self.frame_principal.pack_forget()
        self.funcionarios_tela = abrir_tela_funcionarios(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.funcionarios_tela, "iniciar"):
                self.funcionarios_tela.iniciar()
        except Exception:
            pass

    def ir_para_livros(self):
        self.frame_principal.pack_forget()
        self.livros_tela = abrir_tela_livros(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.livros_tela, "iniciar"):
                self.livros_tela.iniciar()
        except Exception:
            pass

    def ir_para_musicas(self):
        self.frame_principal.pack_forget()
        self.musicas_tela = abrir_tela_musicas(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.musicas_tela, "iniciar"):
                self.musicas_tela.iniciar()
        except Exception:
            pass

    def ir_para_jogos(self):
        self.frame_principal.pack_forget()
        self.jogos_tela = abrir_tela_jogos(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.jogos_tela, "iniciar"):
                self.jogos_tela.iniciar()
        except Exception:
            pass

    def ir_para_receitas(self):
        self.frame_principal.pack_forget()
        self.receitas_tela = abrir_tela_receitas(
            self.master,
            self.frame_login,
            self.usuario_logado,
            on_voltar_callback=self.recarregar_tela
        )
        # se a tela tiver método iniciar, inicia-la (compatibilidade)
        try:
            if hasattr(self.receitas_tela, "iniciar"):
                self.receitas_tela.iniciar()
        except Exception:
            pass

    def ir_para_auditoria(self):
        self.frame_principal.pack_forget()
        self.auditoria_tela = abrir_tela_auditoria(
            self.master,
            self.db,
            on_voltar_callback=self.recarregar_tela,
            usuario_logado=self.usuario_logado
        )
    
    def ir_para_creditos(self):
        self.frame_principal.pack_forget()
        from tela_creditos import TelaCreditos
        TelaCreditos(self.master, self.frame_login, self.usuario_logado,
                    on_voltar_callback=self.recarregar_tela)




    def recarregar_tela(self):
        # Esconde a tela da auditoria, se existir
        if hasattr(self, 'auditoria_tela'):
            try:
                self.auditoria_tela.frame_auditoria.pack_forget()
                # opcionalmente destruir para liberar memória:
                # self.auditoria_tela.frame_auditoria.destroy()
            except Exception as e:
                print(f"Erro ao esconder auditoria: {e}")

        # Mostra a tela principal novamente
        self.frame_principal.pack(fill="both", expand=True)

        # Atualiza o título da janela principal
        alterar_titulo(self.master, "Data Flow - Lobby")

        # Se você tiver métodos para recarregar o conteúdo da tela principal, pode chamá-los aqui.
        # Por exemplo:
        # self.carregar_principal()
        # self.limpar_campos()




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
