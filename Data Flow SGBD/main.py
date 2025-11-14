import tkinter as tk
import re
import os
from datetime import datetime
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from backend import BancoDeDados
from tkcalendar import DateEntry
from PIL import Image, ImageTk, ImageOps
from Lobby import TelaPrincipal

# Instanciar e configurar banco de dados
db = BancoDeDados()

# --- utilidades ---
def centralizar_janela(janela, largura, altura):
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f'{largura}x{altura}+{x}+{y}')


def alterar_titulo(janela, novo_titulo):
    janela.title(novo_titulo)

# placeholders (defina uma vez só)
def on_click(entry, placeholder, is_password=False):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="#000")
        if is_password:
            entry.config(show="*")

def on_focusout(entry, placeholder, is_password=False):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg="#888")
        if is_password:
            entry.config(show="")

# Obtém o diretório onde o script está localizado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho relativo para as imagens
imagens_dir = os.path.join(script_dir, "imagens")

# --- navegação ---
def cadastrar_usuario():
    frame_login.pack_forget()
    frame_cadastro.pack(fill="both", expand=True)
    alterar_titulo(janela, "Data Flow - Cadastro")
    frame_cadastro.focus_set()

def voltar_login():
    frame_redefinir_senha.pack_forget()
    frame_cadastro.pack_forget()
    frame_login.pack(fill="both", expand=True)
    alterar_titulo(janela, "Data Flow - Sistema de gerenciamento de dados")
    limpar_campos_login()
    resetar_campos_cadastro()
    resetar_tela_redefinir_senha()



def limpar_campos_login():
    # Limpar campo de login
    entry_usuario.delete(0, tk.END)
    entry_usuario.insert(0, "Digite o seu login")
    entry_usuario.config(fg="#888")

    # Limpar campo de senha
    entry_senha_login.delete(0, tk.END)
    entry_senha_login.insert(0, "Digite a sua senha")
    entry_senha_login.config(fg="#888", show="")

    # Resetar ícone do olho
    global mostrar_senha_login
    mostrar_senha_login = False
    botao_olho_login.config(text="👁")

def resetar_campos_cadastro():
    entry_usuario_cadastro.delete(0, tk.END)
    entry_usuario_cadastro.insert(0, "Crie o seu login")
    entry_usuario_cadastro.config(fg="#888")
    
    entry_senha_cadastro.config(show="")
    entry_senha_cadastro.delete(0, tk.END)
    entry_senha_cadastro.insert(0, "Crie a sua senha")
    entry_senha_cadastro.config(fg="#888")
    
    entry_email_cadastro.delete(0, tk.END)
    entry_email_cadastro.insert(0, "Digite o seu e-mail")
    entry_email_cadastro.config(fg="#888")

    # >>> RESET DO CALENDÁRIO <<<
    date_nascimento.set_date(datetime.now())

def resetar_tela_redefinir_senha():
    # Ativar todos os campos (caso estejam desabilitados)
    entry_email_redefinir.config(state="normal")
    entry_codigo.config(state="disabled")
    entry_nova_senha.config(state="disabled")
    entry_confirmar_senha.config(state="disabled")

    # Resetar textos e estilos
    entry_email_redefinir.delete(0, tk.END)
    entry_email_redefinir.insert(0, "Digite o seu e-mail")
    entry_email_redefinir.config(fg="#888")

    entry_codigo.delete(0, tk.END)
    entry_codigo.insert(0, "Digite o código recebido")
    entry_codigo.config(fg="#888")

    entry_nova_senha.delete(0, tk.END)
    entry_nova_senha.insert(0, "Digite a nova senha")
    entry_nova_senha.config(fg="#888", show="*")

    entry_confirmar_senha.delete(0, tk.END)
    entry_confirmar_senha.insert(0, "Digite a nova senha")
    entry_confirmar_senha.config(fg="#888", show="*")

def fazer_login():
    usuario = entry_usuario.get().strip()
    senha = entry_senha_login.get().strip()
    if usuario == "Digite o seu login" or senha == "Digite a sua senha":
        messagebox.showwarning("Aviso", "Preencha login e senha!")
        return
    if db.validar_login(usuario, senha):
        messagebox.showinfo("Sucesso", "Login bem-sucedido!")
        frame_login.pack_forget()
        abrir_tela_principal(usuario)  # Passa o usuário logado aqui
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos!")

def abrir_tela_principal(usuario_logado):
    # Exibe a TelaPrincipal
    TelaPrincipal(janela, db, frame_login, usuario_logado)

    # Boas-vindas depois de 1s
    usuario = entry_usuario.get().strip()
    def exibir_messagebox():
        messagebox.showinfo("Boas-vindas", f"Bem-vindo, {usuario}! aproveite ao máximo o sistema!")
    janela.after(1000, exibir_messagebox)

# Caminho relativo para a imagem
caminho_imagem = os.path.join(os.path.dirname(__file__), 'imagens', 'Dataflow-icon.ico')

# --- janela principal ---
janela = tk.Tk()
janela.title("Data Flow - Sistema de gerenciamento de dados")
janela.iconbitmap(caminho_imagem)
centralizar_janela(janela, 1000, 600)

# --- FRAME LOGIN ---
frame_login = tk.Frame(janela, bg="#FFFFFF")
frame_login.pack(fill="both", expand=True)

# Usuário (login)
tk.Label(frame_login, text="Usuário:", bg="#FFFFFF", font=("Helvetica", 11, "bold")).place(relx=0.348, rely=0.445, anchor="w")

# Frame do campo com borda
frame_usuario_entry = tk.Frame(frame_login, bg="white", highlightthickness=2, highlightbackground="#ccc", highlightcolor="#4a90e2")
frame_usuario_entry.place(relx=0.5, rely=0.48, anchor="center", relwidth=0.3, relheight=0.05)

# Caminho relativo da imagem com base no local do arquivo atual
caminho_base = os.path.dirname(__file__)
caminho_icone_usuario = os.path.join(caminho_base, "imagens", "icone-usuario.png")

# Carregar e redimensionar a imagem
icone_usuario = Image.open(caminho_icone_usuario)
icone_usuario = icone_usuario.resize((14, 14))  # redimensiona para caber
icone_usuario_tk = ImageTk.PhotoImage(icone_usuario)

label_icone = tk.Label(frame_usuario_entry, image=icone_usuario_tk, bg="white")
label_icone.image = icone_usuario_tk  # mantém a referência
label_icone.pack(side="left", padx=5)

# Entry ao lado do ícone
entry_usuario = tk.Entry(frame_usuario_entry, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_usuario.insert(0, "Digite o seu login")
entry_usuario.bind("<FocusIn>", lambda e: on_click(entry_usuario, "Digite o seu login"))
entry_usuario.bind("<FocusOut>", lambda e: on_focusout(entry_usuario, "Digite o seu login"))
entry_usuario.pack(side="left", fill="both", expand=True, padx=(5, 0))


# Senha (login)
tk.Label(frame_login, text="Senha:", bg="#FFFFFF", font=("Helvetica", 11, "bold")).place(relx=0.348, rely=0.543, anchor="w")

mostrar_senha_login = False
def alternar_senha_login():
    global mostrar_senha_login
    mostrar_senha_login = not mostrar_senha_login
    if mostrar_senha_login:
        if entry_senha_login.get() != "Digite a sua senha":
            entry_senha_login.config(show="")
        botao_olho_login.config(text="🙈")
    else:
        if entry_senha_login.get() != "Digite a sua senha":
            entry_senha_login.config(show="*")
        botao_olho_login.config(text="👁")

# Frame do campo senha
frame_senha_login = tk.Frame(frame_login, bg="white", highlightthickness=2, highlightbackground="#ccc", highlightcolor="#4a90e2")
frame_senha_login.place(relx=0.5, rely=0.58, anchor="center", relwidth=0.3, relheight=0.05)

# Ícone de senha (cadeado)
icone_senha_path = os.path.join(imagens_dir, "icone-cadeado.png")
icone_senha = Image.open(icone_senha_path)
icone_senha = icone_senha.resize((14, 14))  # Redimensiona para caber
icone_senha_tk = ImageTk.PhotoImage(icone_senha)

label_icone_senha = tk.Label(frame_senha_login, image=icone_senha_tk, bg="white")
label_icone_senha.image = icone_senha_tk  # mantém a referência
label_icone_senha.pack(side="left", padx=5)

# Entry senha
entry_senha_login = tk.Entry(frame_senha_login, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_senha_login.insert(0, "Digite a sua senha")
entry_senha_login.bind("<FocusIn>", lambda e: on_click(entry_senha_login, "Digite a sua senha", is_password=True))
entry_senha_login.bind("<FocusOut>", lambda e: on_focusout(entry_senha_login, "Digite a sua senha", is_password=True))
entry_senha_login.pack(side="left", fill="both", expand=True, padx=(5, 0))

# Botão olho (mostrar/ocultar senha)
botao_olho_login = tk.Button(frame_senha_login, text="👁", bg="white", relief="flat", command=alternar_senha_login)
botao_olho_login.pack(side="right", padx=(0, 8))


# Esqueci a senha
label_esqueci_senha = tk.Label(frame_login, text="Esqueci a senha", fg="blue", bg="white", font=("Segoe UI", 9, "underline"), cursor="hand2")
label_esqueci_senha.place(relx=0.652, rely=0.621, anchor="e")
def abrir_tela_redefinir_senha():
    resetar_tela_redefinir_senha()
    frame_login.pack_forget()
    frame_redefinir_senha.pack(fill="both", expand=True)
    alterar_titulo(janela, "Data Flow - Redefinir Senha")
    frame_redefinir_senha.focus_set()
label_esqueci_senha.bind("<Button-1>", lambda e: abrir_tela_redefinir_senha())

# Logo login
caminho_imagem = os.path.join(os.path.dirname(__file__), 'imagens', 'dataflowoficial.png')
imagem_login = Image.open(caminho_imagem).convert("RGBA")
pixels = imagem_login.getdata()
nova_imagem_data = []
fundo = (255, 255, 255); tolerancia = 20
for r, g, b, a in pixels:
    if abs(r - fundo[0]) <= tolerancia and abs(g - fundo[1]) <= tolerancia and abs(b - fundo[2]) <= tolerancia:
        nova_imagem_data.append((255, 255, 255, 0))
    else:
        nova_imagem_data.append((r, g, b, a))
imagem_login.putdata(nova_imagem_data)
largura_original, altura_original = imagem_login.size
aspect_ratio_login = largura_original / altura_original
largura_inicial = 280
altura_inicial = int(largura_inicial / aspect_ratio_login)
imagem_login_tk = ImageTk.PhotoImage(imagem_login.resize((largura_inicial, altura_inicial), Image.LANCZOS))
label_imagem_login = tk.Label(frame_login, image=imagem_login_tk, bg="#FFFFFF")
label_imagem_login.image = imagem_login_tk
label_imagem_login.place(relx=0.5, rely=0.23, anchor="center")
def redimensionar_imagem_login(event):
    largura_max = int(event.width * 0.4)
    altura_max = int(event.height * 0.3)
    largura = largura_max
    altura = int(largura / aspect_ratio_login)
    if altura > altura_max:
        altura = altura_max
        largura = int(altura * aspect_ratio_login)
    img_tk = ImageTk.PhotoImage(imagem_login.resize((largura, altura), Image.LANCZOS))
    label_imagem_login.config(image=img_tk)
    label_imagem_login.image = img_tk
frame_login.bind("<Configure>", redimensionar_imagem_login)

# Botões login/cadastro
tk.Button(frame_login, text="Entrar", bg="blue", relief="raised", font="Arial 12 bold", fg="white", command=fazer_login)\
    .place(relx=0.5, rely=0.70, anchor="center", relwidth=0.3, relheight=0.05)
botao_cadastrar = tk.Button(frame_login, text="Cadastrar", fg="gray", bg="white", font="Arial 12 bold",
                            relief="groove", bd=2, highlightthickness=0, command=cadastrar_usuario)
botao_cadastrar.config(highlightbackground="gray", highlightcolor="gray")
botao_cadastrar.place(relx=0.5, rely=0.78, anchor="center", relwidth=0.3, relheight=0.05)

# Rodapé com créditos
label_creditos = tk.Label(
    frame_login,
    text="© 2025 Rodrigo Ferreira | Todos os direitos reservados",
    font=("Arial", 11, "italic"),
    fg="#777777",
    bg="white"
)
label_creditos.pack(side="bottom", pady=5)


# -*- coding: utf-8 -*-
import os
import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import dns.resolver  # Para checar se o e-mail existe

# Função para validar se o e-mail existe (verifica registro MX do domínio)
def email_existe(email):
    padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(padrao_email, email):
        return False
    try:
        dominio = email.split('@')[1]
        registros_mx = dns.resolver.resolve(dominio, 'MX')
        return len(registros_mx) > 0
    except Exception:
        return False

# --- FRAME CADASTRO ---
frame_cadastro = tk.Frame(janela, bg="white")

# Logo cadastro
caminho_imagem_cadastro = os.path.join(os.path.dirname(__file__), 'imagens', 'logocadastro.png')
imagem_original_cadastro = Image.open(caminho_imagem_cadastro).convert("RGBA")
pixels_cadastro = imagem_original_cadastro.getdata()
nova_imagem_data_cadastro = []
for r, g, b, a in pixels_cadastro:
    if abs(r - fundo[0]) <= tolerancia and abs(g - fundo[1]) <= tolerancia and abs(b - fundo[2]) <= tolerancia:
        nova_imagem_data_cadastro.append((255, 255, 255, 0))
    else:
        nova_imagem_data_cadastro.append((r, g, b, a))
imagem_original_cadastro.putdata(nova_imagem_data_cadastro)
largura_original_cadastro, altura_original_cadastro = imagem_original_cadastro.size
aspect_ratio_cadastro = largura_original_cadastro / altura_original_cadastro
largura_inicial_cadastro = 280
altura_inicial_cadastro = int(largura_inicial_cadastro / aspect_ratio_cadastro)
imagem_tk_cadastro = ImageTk.PhotoImage(imagem_original_cadastro.resize((largura_inicial_cadastro, altura_inicial_cadastro), Image.LANCZOS))
label_imagem_cadastro = tk.Label(frame_cadastro, image=imagem_tk_cadastro, bg="#FFFFFF")
label_imagem_cadastro.image = imagem_tk_cadastro
label_imagem_cadastro.place(relx=0.5, rely=0.23, anchor="center")
def redimensionar_imagem_cadastro(event):
    largura_max = int(event.width * 0.4)
    altura_max = int(event.height * 0.3)
    largura = largura_max
    altura = int(largura / aspect_ratio_cadastro)
    if altura > altura_max:
        altura = altura_max
        largura = int(altura * aspect_ratio_cadastro)
    img_tk = ImageTk.PhotoImage(imagem_original_cadastro.resize((largura, altura), Image.LANCZOS))
    label_imagem_cadastro.config(image=img_tk)
    label_imagem_cadastro.image = img_tk
frame_cadastro.bind("<Configure>", redimensionar_imagem_cadastro)

# Placeholders
def on_click2(entry, placeholder, is_password=False):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="#000")
        if is_password:
            entry.config(show="*")

def on_focusout2(entry, placeholder, is_password=False):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg="#888")
        if is_password:
            entry.config(show="")

# --- ENTRIES ---
# Usuário
frame_login_entry = tk.Frame(frame_cadastro, bg="white", highlightthickness=2, highlightbackground="#ccc", highlightcolor="#4a90e2")
frame_login_entry.place(relx=0.5, rely=0.46, anchor="center", relwidth=0.3, relheight=0.05)
icone_usuario_cadastro_path = os.path.join(imagens_dir, "icone-usuario.png")
icone_usuario_cadastro = Image.open(icone_usuario_cadastro_path).resize((14, 14))
icone_usuario_cadastro_tk = ImageTk.PhotoImage(icone_usuario_cadastro)
label_icone = tk.Label(frame_login_entry, image=icone_usuario_cadastro_tk, bg="white")
label_icone.image = icone_usuario_cadastro_tk
label_icone.pack(side="left", padx=5)
entry_usuario_cadastro = tk.Entry(frame_login_entry, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_usuario_cadastro.insert(0, "Crie o seu login")
entry_usuario_cadastro.bind("<FocusIn>", lambda e: on_click2(entry_usuario_cadastro, "Crie o seu login"))
entry_usuario_cadastro.bind("<FocusOut>", lambda e: on_focusout2(entry_usuario_cadastro, "Crie o seu login"))
entry_usuario_cadastro.pack(side="left", fill="both", expand=True, padx=(5, 0))

# Senha
mostrar_senha_cadastro = False
def alternar_senha_cadastro():
    global mostrar_senha_cadastro
    mostrar_senha_cadastro = not mostrar_senha_cadastro
    if mostrar_senha_cadastro:
        if entry_senha_cadastro.get() != "Crie a sua senha":
            entry_senha_cadastro.config(show="")
        botao_olho_cad.config(text="👁")
    else:
        if entry_senha_cadastro.get() != "Crie a sua senha":
            entry_senha_cadastro.config(show="*")
        botao_olho_cad.config(text="👁")

frame_senha_cad = tk.Frame(frame_cadastro, bg="white", highlightthickness=2, highlightbackground="#ccc", highlightcolor="#4a90e2")
frame_senha_cad.place(relx=0.35, rely=0.53, anchor="w", relwidth=0.3, relheight=0.05)
icone_senha_cadastro_path = os.path.join(imagens_dir, "icone-cadeado.png")
icone_senha_cadastro = Image.open(icone_senha_cadastro_path).resize((14, 14))
icone_senha_cadastro_tk = ImageTk.PhotoImage(icone_senha_cadastro)
label_icone_senha = tk.Label(frame_senha_cad, image=icone_senha_cadastro_tk, bg="white")
label_icone_senha.image = icone_senha_cadastro_tk
label_icone_senha.pack(side="left", padx=5)
entry_senha_cadastro = tk.Entry(frame_senha_cad, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_senha_cadastro.insert(0, "Crie a sua senha")
entry_senha_cadastro.bind("<FocusIn>", lambda e: on_click2(entry_senha_cadastro, "Crie a sua senha", is_password=True))
entry_senha_cadastro.bind("<FocusOut>", lambda e: on_focusout2(entry_senha_cadastro, "Crie a sua senha", is_password=True))
entry_senha_cadastro.pack(side="left", fill="both", expand=True, padx=(5, 0))
botao_olho_cad = tk.Button(frame_senha_cad, text="👁", bg="white", relief="flat", command=alternar_senha_cadastro)
botao_olho_cad.pack(side="right", padx=5)

# Data
frame_data = tk.Frame(frame_cadastro, bg="white", highlightthickness=2, highlightbackground="#ccc", highlightcolor="#4a90e2")
frame_data.place(relx=0.351, rely=0.60, anchor="w", relwidth=0.299, relheight=0.05)
icone_calendario_path = os.path.join(imagens_dir, "icone-calendario.png")
icone_calendario = Image.open(icone_calendario_path).resize((14, 14))
icone_calendario_tk = ImageTk.PhotoImage(icone_calendario)
label_icone_data = tk.Label(frame_data, image=icone_calendario_tk, bg="white")
label_icone_data.image = icone_calendario_tk
label_icone_data.pack(side="left", padx=5)
date_nascimento = DateEntry(frame_data, width=18, background="darkblue", foreground="white", borderwidth=0,
                            font=("Segoe UI", 11), date_pattern="dd/MM/yyyy",
                            year=datetime.now().year,
                            maxdate=datetime.now(),
                            mindate=datetime(datetime.now().year - 125, 1, 1),
                            locale="pt_BR")
date_nascimento.pack(side="left", fill="both", expand=True, padx=(5, 0))

# E-mail
frame_email_entry = tk.Frame(frame_cadastro, bg="white", highlightthickness=2, highlightbackground="#ccc", highlightcolor="#4a90e2")
frame_email_entry.place(relx=0.5, rely=0.67, anchor="center", relwidth=0.3, relheight=0.05)
icone_email_path = os.path.join(imagens_dir, "icone-email.png")
icone_email = Image.open(icone_email_path).resize((14, 14))
icone_email_tk = ImageTk.PhotoImage(icone_email)
label_icone_email = tk.Label(frame_email_entry, image=icone_email_tk, bg="white")
label_icone_email.image = icone_email_tk
label_icone_email.pack(side="left", padx=5)
entry_email_cadastro = tk.Entry(frame_email_entry, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_email_cadastro.insert(0, "Digite o seu e-mail")
entry_email_cadastro.bind("<FocusIn>", lambda e: on_click2(entry_email_cadastro, "Digite o seu e-mail"))
entry_email_cadastro.bind("<FocusOut>", lambda e: on_focusout2(entry_email_cadastro, "Digite o seu e-mail"))
entry_email_cadastro.pack(side="left", fill="both", expand=True, padx=(5, 0))

# Função de salvar usuário
def salvar_usuario():
    usuario = entry_usuario_cadastro.get().strip()
    senha = entry_senha_cadastro.get().strip()
    email = entry_email_cadastro.get().strip()
    data_nasc = date_nascimento.get_date()

    if usuario == "Crie o seu login" or not usuario:
        messagebox.showerror("Erro", "Digite o seu login")
        return
    if senha == "Crie a sua senha" or not senha:
        messagebox.showerror("Erro", "Digite a sua senha")
        return
    if email == "Digite o seu e-mail" or not email:
        messagebox.showerror("Erro", "Digite o seu e-mail")
        return
    if not email_existe(email):
        messagebox.showerror("Erro", "Este e-mail não existe na internet")
        return

    sucesso = db.cadastrar_usuario(usuario, senha, email, data_nasc)
    if sucesso:
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
        # Aqui volta para a tela de login
        frame_cadastro.pack_forget()
        frame_login.pack(fill="both", expand=True)
        frame_login.focus_set()
    else:
        messagebox.showerror("Erro", "Usuário ou e-mail já cadastrado")


# Botões cadastro
tk.Button(frame_cadastro, text="Cadastrar", font="Arial 12 bold", bg="#329445", fg="white", command=salvar_usuario)\
    .place(relx=0.5, rely=0.78, anchor="center", relwidth=0.3, relheight=0.05)
tk.Button(frame_cadastro, fg="gray", bg="white", font="Arial 12 bold", relief="groove", bd=2, highlightthickness=0,
          text="Voltar", command=voltar_login)\
    .place(relx=0.5, rely=0.86, anchor="center", relwidth=0.3, relheight=0.05)

# Rodapé
label_creditos = tk.Label(frame_cadastro, text="© 2025 Rodrigo Ferreira | Todos os direitos reservados",
                          font=("Arial", 11, "italic"), fg="#777777", bg="white")
label_creditos.pack(side="bottom", pady=5)


# --- FRAME REDEFINIR SENHA ---
frame_redefinir_senha = tk.Frame(janela, bg="#9ab8e6")

# --- Canvas branco central com cantos arredondados ---
canvas_container = tk.Canvas(frame_redefinir_senha, bg="#9ab8e6", highlightthickness=0)
canvas_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.6)

# Função para desenhar retângulo arredondado
def criar_retangulo_arredondado(canvas, x1, y1, x2, y2, raio=20, **kwargs):
    pontos = [
        x1+raio, y1,
        x2-raio, y1,
        x2, y1,
        x2, y1+raio,
        x2, y2-raio,
        x2, y2,
        x2-raio, y2,
        x1+raio, y2,
        x1, y2,
        x1, y2-raio,
        x1, y1+raio,
        x1, y1
    ]
    return canvas.create_polygon(pontos, smooth=True, **kwargs)

# --- Carrega e prepara a imagem ---
caminho_imagem_redefinir = os.path.join(os.path.dirname(__file__), 'imagens', 'Imagem-redefinirsenha.png')
imagem_redefinir_original = Image.open(caminho_imagem_redefinir).convert("RGBA")

# Remove fundo branco
pixels = imagem_redefinir_original.getdata()
nova_imagem_data = []
fundo = (255, 255, 255)
tolerancia = 20
for r, g, b, a in pixels:
    if abs(r - fundo[0]) <= tolerancia and abs(g - fundo[1]) <= tolerancia and abs(b - fundo[2]) <= tolerancia:
        nova_imagem_data.append((255, 255, 255, 0))
    else:
        nova_imagem_data.append((r, g, b, a))
imagem_redefinir_original.putdata(nova_imagem_data)

# Aspect ratio
largura_original, altura_original = imagem_redefinir_original.size
aspect_ratio_redefinir = largura_original / altura_original

# --- Label da imagem ---
label_imagem_redefinir = tk.Label(canvas_container, bg="white")
label_imagem_redefinir.place(relx=0.5, rely=0.01, anchor="n")

# --- Ajuste do container e imagem ---
def ajustar_container(event=None):
    largura_janela = janela.winfo_width()
    altura_janela = janela.winfo_height()
    if largura_janela <= 1 or altura_janela <= 1:
        return

    largura_canvas = int(largura_janela * 0.4)
    altura_canvas = int(altura_janela * 0.85)

    canvas_container.place_configure(
        relwidth=largura_canvas / largura_janela,
        relheight=altura_canvas / altura_janela
    )

    canvas_container.delete("tudo")
    criar_retangulo_arredondado(canvas_container, 0, 0, largura_canvas, altura_canvas, raio=30, fill="white", outline="#ccc")

    # Redimensiona imagem
    largura_imagem = int(largura_canvas * 0.51)
    altura_imagem = int(largura_imagem / aspect_ratio_redefinir)
    largura_imagem = max(150, largura_imagem)
    altura_imagem = max(80, altura_imagem)
    imagem_redimensionada = imagem_redefinir_original.resize((largura_imagem, altura_imagem), Image.LANCZOS)
    imagem_redefinir_tk = ImageTk.PhotoImage(imagem_redimensionada)
    label_imagem_redefinir.configure(image=imagem_redefinir_tk)
    label_imagem_redefinir.image = imagem_redefinir_tk

    def ajustar_botao(event):
        largura_botao = min(120, frame_email_redefinir.winfo_width() * 0.3)
        altura_botao = 25
        btn_enviar.place_configure(width=largura_botao, height=altura_botao)
    frame_email_redefinir.bind("<Configure>", ajustar_botao)

# --- Bind para redimensionamento ---
canvas_container.bind("<Configure>", ajustar_container)
frame_redefinir_senha.bind("<Configure>", ajustar_container)
janela.bind("<Configure>", ajustar_container)

# --- Funções de placeholder ---
def on_click3(entry, placeholder, is_password=False):
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="#000")
        if is_password:
            entry.config(show="*")
        if entry.cget("state") == "readonly":
            entry.config(state="normal")

def on_focusout3(entry, placeholder, is_password=False):
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg="#888")
        if is_password:
            entry.config(show="")
        if entry != entry_email_redefinir:  # email fica readonly depois de enviar
            entry.config(state="disabled")

# --- Campos e botões ---
# E-mail
tk.Label(canvas_container, text="E-mail cadastrado:", bg="white", font=("Helvetica", 12, "bold"))\
    .place(relx=0.05, rely=0.32, anchor="w")

frame_email_redefinir = tk.Frame(canvas_container, bg="white", highlightthickness=1.5, highlightbackground="#ccc")
frame_email_redefinir.place(relx=0.05, rely=0.336, relwidth=0.9, relheight=0.06)

icone_email_redefinir = Image.open("imagens/icone-email.png").resize((14, 14))
icone_email_redefinir_tk = ImageTk.PhotoImage(icone_email_redefinir)
label_icone_email_redefinir = tk.Label(frame_email_redefinir, image=icone_email_redefinir_tk, bg="white")
label_icone_email_redefinir.image = icone_email_redefinir_tk
label_icone_email_redefinir.pack(side="left", padx=5)

entry_email_redefinir = tk.Entry(frame_email_redefinir, fg="#888", relief="flat", font=("Helvetica", 12))
entry_email_redefinir.insert(0, "Digite o seu e-mail")
entry_email_redefinir.config(state="normal")
entry_email_redefinir.bind("<FocusIn>", lambda e: on_click3(entry_email_redefinir, "Digite o seu e-mail"))
entry_email_redefinir.bind("<FocusOut>", lambda e: on_focusout3(entry_email_redefinir, "Digite o seu e-mail"))
entry_email_redefinir.pack(side="left", fill="both", expand=True, padx=(5, 0))

# Código recebido
tk.Label(canvas_container, text="Código recebido:", bg="white", font=("Helvetica", 12, "bold"))\
    .place(relx=0.05, rely=0.498, anchor="w")
frame_codigo = tk.Frame(canvas_container, bg="white", highlightthickness=1.5, highlightbackground="#ccc")
frame_codigo.place(relx=0.05, rely=0.515, relwidth=0.9, relheight=0.06)
entry_codigo = tk.Entry(frame_codigo, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_codigo.insert(0, "Digite o código recebido")
entry_codigo.config(state="disabled")
entry_codigo.bind("<FocusIn>", lambda e: on_click3(entry_codigo, "Digite o código recebido"))
entry_codigo.bind("<FocusOut>", lambda e: on_focusout3(entry_codigo, "Digite o código recebido"))
entry_codigo.pack(fill="both", expand=True, padx=8)

# Nova senha
tk.Label(canvas_container, text="Nova senha:", bg="white", font=("Helvetica", 12, "bold"))\
    .place(relx=0.05, rely=0.605, anchor="w")
frame_nova_senha = tk.Frame(canvas_container, bg="white", highlightthickness=1.5, highlightbackground="#ccc")
frame_nova_senha.place(relx=0.05, rely=0.62, relwidth=0.9, relheight=0.06)
entry_nova_senha = tk.Entry(frame_nova_senha, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_nova_senha.insert(0, "Digite a nova senha")
entry_nova_senha.config(state="disabled")
entry_nova_senha.bind("<FocusIn>", lambda e: on_click3(entry_nova_senha, "Digite a nova senha", is_password=True))
entry_nova_senha.bind("<FocusOut>", lambda e: on_focusout3(entry_nova_senha, "Digite a nova senha", is_password=True))
entry_nova_senha.pack(fill="both", expand=True, padx=8)

# Confirmar senha
tk.Label(canvas_container, text="Repita a senha:", bg="white", font=("Helvetica", 12, "bold"))\
    .place(relx=0.05, rely=0.71, anchor="w")
frame_confirmar_senha = tk.Frame(canvas_container, bg="white", highlightthickness=1.5, highlightbackground="#ccc")
frame_confirmar_senha.place(relx=0.05, rely=0.728, relwidth=0.9, relheight=0.06)
entry_confirmar_senha = tk.Entry(frame_confirmar_senha, fg="#888", relief="flat", font=("Segoe UI", 10))
entry_confirmar_senha.insert(0, "Repita a nova senha")
entry_confirmar_senha.config(state="disabled")
entry_confirmar_senha.bind("<FocusIn>", lambda e: on_click3(entry_confirmar_senha, "Repita a nova senha", is_password=True))
entry_confirmar_senha.bind("<FocusOut>", lambda e: on_focusout3(entry_confirmar_senha, "Repita a nova senha", is_password=True))
entry_confirmar_senha.pack(fill="both", expand=True, padx=8)

# --- Botão “Enviar Código” ---
def enviar_codigo():
    email = entry_email_redefinir.get().strip()
    if email == "" or email == "Digite o seu e-mail":
        messagebox.showwarning("Aviso", "Digite o e-mail cadastrado.")
        return
    
    # ✅ Verifica se o email está cadastrado
    if not db.verificar_email_existe(email):
        messagebox.showerror("Erro", "Este e-mail não está cadastrado no sistema.")
        return
    
    codigo = db.gerar_codigo(email)
    enviado = db.enviar_codigo_email(email, codigo)
    
    if enviado:
        messagebox.showinfo("Sucesso", f"Código enviado para {email}")
        # Bloqueia o email e habilita os outros campos
        entry_email_redefinir.config(state="readonly")
        for e in [entry_codigo, entry_nova_senha, entry_confirmar_senha]:
            if e.get() in ["Digite o código recebido", "Digite a nova senha", "Repita a nova senha"]:
                e.config(state="normal")
    else:
        messagebox.showerror("Erro", "Não foi possível enviar o código. Verifique sua conexão.")


btn_enviar = tk.Button(canvas_container, text="Enviar Código", bg="#2f80ed", fg="white",
                       font=("Segoe UI", 10, "bold"), relief="flat", command=enviar_codigo)
btn_enviar.place(relx=0.95, rely=0.468, anchor="se", relwidth=0.06, relheight=0.015)

# Redefinir senha
def redefinir_senha():
    email = entry_email_redefinir.get().strip()
    codigo_digitado = entry_codigo.get().strip()
    nova_senha = entry_nova_senha.get().strip()
    confirmar_senha = entry_confirmar_senha.get().strip()

    if not (email and codigo_digitado and nova_senha and confirmar_senha):
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    if nova_senha != confirmar_senha:
        messagebox.showerror("Erro", "As senhas não coincidem.")
        return

    if not db.verificar_codigo(email, codigo_digitado):
        messagebox.showerror("Erro", "Código inválido ou expirado.")
        return

    db.atualizar_senha(email, nova_senha)
    messagebox.showinfo("Sucesso", "Senha redefinida com sucesso!")
    frame_redefinir_senha.pack_forget()
    frame_login.pack(fill="both", expand=True)

tk.Button(canvas_container, text="Redefinir", bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"),
          relief="flat", command=redefinir_senha)\
    .place(relx=0.5, rely=0.86, anchor="center", relwidth=0.9, relheight=0.06)

# Voltar
tk.Button(canvas_container, fg="gray", bg="white", font="Arial 12 bold", relief="groove", bd=2, highlightthickness=0,
          text="Voltar", command=voltar_login)\
    .place(relx=0.5, rely=0.94, anchor="center", relwidth=0.9, relheight=0.06)

# Rodapé
label_creditos = tk.Label(
    frame_redefinir_senha,
    text="© 2025 Rodrigo Ferreira | Todos os direitos reservados",
    font=("Arial", 11, "italic"),
    fg="#777777",
    bg="#9ab8e6"
)
label_creditos.pack(side="bottom", pady=5)


janela.mainloop()
