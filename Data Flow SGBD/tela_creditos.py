# tela_creditos.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import webbrowser
import os
from datetime import datetime

def alterar_titulo(janela, novo_titulo):
    try:
        janela.title(novo_titulo)
    except:
        pass

class TelaCreditos:
    def __init__(self, master, frame_login, usuario_logado, on_voltar_callback=None):
        self.master = master
        self.frame_login = frame_login
        self.usuario_logado = usuario_logado
        self.on_voltar_callback = on_voltar_callback

        self.frame_creditos = tk.Frame(self.master, bg="#1C1F26")
        self.frame_creditos.pack(fill="both", expand=True)

        alterar_titulo(self.master, "Data Flow - Créditos")
        self.build_ui()

    def build_ui(self):
        # Navbar
        navbar = tk.Frame(self.frame_creditos, bg="#21252B", height=56)
        navbar.pack(fill="x")

        lbl_logo = tk.Label(
            navbar, text="Data Flow", bg="#21252B",
            fg="#F0F6F9", font=("Segoe UI", 14, "bold")
        )
        lbl_logo.pack(side="left", padx=16)

        lbl_user = tk.Label(
            navbar, text=f"Usuário: {self.usuario_logado}",
            bg="#21252B", fg="#F0F6F9", font=("Segoe UI", 10)
        )
        lbl_user.pack(side="right", padx=12)

        btn_voltar = tk.Button(
            navbar, text="⬅ Voltar", bg="#0097A7", fg="white",
            relief="flat", padx=8, pady=4,
            command=self.voltar
        )
        btn_voltar.pack(side="right", padx=12, pady=8)
        btn_voltar.bind("<Enter>", lambda e: btn_voltar.config(bg="#007C91"))
        btn_voltar.bind("<Leave>", lambda e: btn_voltar.config(bg="#0097A7"))

        # Conteúdo
        content = tk.Frame(self.frame_creditos, bg="#1C1F26")
        content.pack(fill="both", expand=True, padx=40, pady=40)

        # Caixa central (card estilizado)
        box = tk.Frame(content, bg="#2C2F3A", padx=65, pady=35)
        box.place(relx=0.5, rely=0.5, anchor="center")

        # Título
        tk.Label(
            box, text="Créditos do Sistema",
            font=("Segoe UI", 20, "bold"),
            bg="#2C2F3A", fg="#F0F6F9"
        ).pack(pady=(0, 20))

        # Autor
        tk.Label(
            box, text="Autor:",
            font=("Segoe UI", 13, "bold"),
            bg="#2C2F3A", fg="#00BCD4"
        ).pack(anchor="w")

        tk.Label(
            box, text="Rodrigo Ferreira da Silva Filho",
            font=("Segoe UI", 12),
            bg="#2C2F3A", fg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        # LinkedIn
        tk.Label(
            box, text="LinkedIn:",
            font=("Segoe UI", 13, "bold"),
            bg="#2C2F3A", fg="#00BCD4"
        ).pack(anchor="w")

        lbl_linkedin = tk.Label(
            box,
            text="in/rodrigo-ferreira",
            font=("Segoe UI", 11, "underline"),
            fg="#4FC3F7",
            bg="#2C2F3A",
            cursor="hand2"
        )
        lbl_linkedin.pack(anchor="w", pady=(0, 15))
        lbl_linkedin.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new("https://www.linkedin.com/in/rodrigo-ferreira-325527272")
        )

        # Email
        tk.Label(
            box, text="Email:",
            font=("Segoe UI", 13, "bold"),
            bg="#2C2F3A", fg="#00BCD4"
        ).pack(anchor="w")

        lbl_email = tk.Label(
            box,
            text="contato.rodrigo.tech@gmail.com",
            font=("Segoe UI", 11, "underline"),
            fg="#4FC3F7",
            bg="#2C2F3A",
            cursor="hand2"
        )
        lbl_email.pack(anchor="w", pady=(0, 15))
        lbl_email.bind(
            "<Button-1>",
            lambda e: webbrowser.open_new(
                "https://mail.google.com/mail/?view=cm&fs=1&to=contato.rodrigo.tech@gmail.com"
            )
        )


        # Versão
        tk.Label(
            box, text="Versão do Sistema:",
            font=("Segoe UI", 13, "bold"),
            bg="#2C2F3A", fg="#00BCD4"
        ).pack(anchor="w")

        tk.Label(
            box, text="1.0.0",
            font=("Segoe UI", 12),
            bg="#2C2F3A", fg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        # Tecnologias
        tk.Label(
            box, text="Tecnologias Utilizadas:",
            font=("Segoe UI", 13, "bold"),
            bg="#2C2F3A", fg="#00BCD4"
        ).pack(anchor="w")

        tk.Label(
            box,
            text="Python, Tkinter, Pillow, Matplotlib, SQLite",
            font=("Segoe UI", 12),
            bg="#2C2F3A", fg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        # Footer
        tk.Label(
            box, text=f"© {datetime.now().year}  -  Data Flow",
            font=("Segoe UI", 10, "italic"),
            bg="#2C2F3A", fg="#B0BEC5"
        ).pack(pady=(20, 0))

    def voltar(self):
        self.frame_creditos.pack_forget()
        if self.on_voltar_callback:
            self.on_voltar_callback()
