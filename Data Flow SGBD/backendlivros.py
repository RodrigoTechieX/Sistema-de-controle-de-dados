import sqlite3
from datetime import datetime
from tkinter import messagebox
import time

class BancoDeDadosLivros:
    def __init__(self):
        self.conexao = sqlite3.connect("dados.db")
        self.criar_tabelas()

    def criar_tabelas(self):
        cursor = self.conexao.cursor()

        # Usuários
        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                            id INTEGER PRIMARY KEY,
                            usuario TEXT UNIQUE,
                            senha TEXT)''')

        # Livros
        cursor.execute('''CREATE TABLE IF NOT EXISTS livros (
                            id INTEGER PRIMARY KEY,
                            isbn TEXT UNIQUE,
                            titulo TEXT,
                            autores TEXT,
                            editora TEXT,
                            ano_publicacao INTEGER,
                            categoria_genero TEXT,
                            numero_paginas INTEGER,
                            preco REAL)''')

        # Auditoria
        cursor.execute('''CREATE TABLE IF NOT EXISTS auditoria (
                            id INTEGER PRIMARY KEY,
                            usuario TEXT,
                            operacao TEXT,
                            tabela TEXT,
                            dados TEXT,
                            data_hora TEXT)''')

        self.conexao.commit()

    # -------------------- AUDITORIA -------------------- #
    def registrar_auditoria(self, operacao, tabela, dados, usuario="Desconhecido"):
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conexao.cursor()
        cursor.execute("""INSERT INTO auditoria 
                          (usuario, operacao, tabela, dados, data_hora) 
                          VALUES (?, ?, ?, ?, ?)""",
                       (usuario, operacao, tabela, dados, data_hora))
        self.conexao.commit()

    def consultar_auditoria(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM auditoria ORDER BY data_hora DESC")
        return cursor.fetchall()

    def pesquisar_auditoria(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM auditoria WHERE
                          id LIKE ? OR
                          usuario LIKE ? OR
                          operacao LIKE ? OR
                          tabela LIKE ? OR
                          dados LIKE ? OR
                          data_hora LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 6)
        return cursor.fetchall()

    def contar_registros(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM livros")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar registros: {e}")
            return 0

    def excluir_varios_registros_auditoria(self, lista_ids):
        cursor = self.conexao.cursor()
        cursor.executemany("DELETE FROM auditoria WHERE id = ?", [(id,) for id in lista_ids])
        self.conexao.commit()

    # -------------------- USUÁRIOS -------------------- #
    def cadastrar_usuario(self, usuario, senha):
        cursor = self.conexao.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validar_login(self, usuario, senha):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        return cursor.fetchone() is not None

    # -------------------- LIVROS -------------------- #
    def salvar_livro(self, id_livro, isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco, usuario_logado):
        if id_livro is None:
            self.adicionar_livro(isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco, usuario_logado)
        else:
            self.atualizar_livro(id_livro, isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco, usuario_logado)

    def adicionar_livro(self, isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO livros
                          (isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco))
        self.conexao.commit()

        dados = f"ISBN: {isbn}, Título: {titulo}, Autor(es): {autores}, Editora: {editora}, Ano: {ano_publicacao}, Categoria/Gênero: {categoria_genero}, Nº de páginas: {numero_paginas}, Preço: {preco}"
        self.registrar_auditoria("ADICIONADO", "Livros", dados, usuario_logado)

    def atualizar_livro(self, id_livro, isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE livros
                          SET isbn=?, titulo=?, autores=?, editora=?, ano_publicacao=?, categoria_genero=?, numero_paginas=?, preco=?
                          WHERE id=?''',
                       (isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco, id_livro))
        self.conexao.commit()

        dados = f"ID: {id_livro}, ISBN: {isbn}, Título: {titulo}, Autor(es): {autores}, Editora: {editora}, Ano: {ano_publicacao}, Categoria/Gênero: {categoria_genero}, Nº de páginas: {numero_paginas}, Preço: {preco}"
        self.registrar_auditoria("EDITADO", "Livros", dados, usuario_logado)

    def excluir_livro(self, id_livro, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
        livro = cursor.fetchone()

        if livro:
            cursor.execute("DELETE FROM livros WHERE id = ?", (id_livro,))
            self.conexao.commit()

            dados = f"ID: {livro[0]}, ISBN: {livro[1]}, Título: {livro[2]}, Autor(es): {livro[3]}, Editora: {livro[4]}, Ano: {livro[5]}, Categoria/Gênero: {livro[6]}, Nº de páginas: {livro[7]}, Preço: {livro[8]}"
            self.registrar_auditoria("EXCLUÍDO", "Livros", dados, usuario_logado)

    # -------------------- RESTAURAR -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado):
        """
        Restaura um livro excluído da tabela de auditoria para a tabela original.
        """
        if tabela.lower() != "livros":
            return False

        cursor = self.conexao.cursor()
        try:
            campos = {}
            for parte in dados.split(","):
                if ":" in parte:
                    chave, valor = parte.split(":", 1)
                    campos[chave.strip()] = valor.strip()

            isbn = campos.get("ISBN", "")
            titulo = campos.get("Título", "")
            autores = campos.get("Autor(es)", "")
            editora = campos.get("Editora", "")
            ano = campos.get("Ano", "0")
            categoria = campos.get("Categoria/Gênero", "")
            paginas = campos.get("Nº de páginas", "0")
            preco = campos.get("Preço", "0").replace("R$", "").strip() or "0"

            try:
                ano = int(ano)
            except:
                ano = 0
            try:
                paginas = int(paginas)
            except:
                paginas = 0
            try:
                preco = float(preco)
            except:
                preco = 0.0

            try:
                cursor.execute('''INSERT INTO livros
                                  (isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                               (isbn, titulo, autores, editora, ano, categoria, paginas, preco))
                self.conexao.commit()
            except sqlite3.IntegrityError:
                # Gera ISBN único se já existir
                novo_isbn = f"{isbn}_R{int(time.time())}"
                cursor.execute('''INSERT INTO livros
                                  (isbn, titulo, autores, editora, ano_publicacao, categoria_genero, numero_paginas, preco)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                               (novo_isbn, titulo, autores, editora, ano, categoria, paginas, preco))
                self.conexao.commit()

            dados_restaurados = f"ISBN: {isbn}, Título: {titulo}, Autor(es): {autores}, Editora: {editora}, Ano: {ano}, Categoria/Gênero: {categoria}, Nº de páginas: {paginas}, Preço: {preco}"
            self.registrar_auditoria("RESTAURADO", "Livros", dados_restaurados, usuario_logado)
            return True

        except Exception as e:
            print(f"Erro ao restaurar dados: {e}")
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_livros(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM livros WHERE
                          id LIKE ? OR
                          isbn LIKE ? OR
                          titulo LIKE ? OR
                          autores LIKE ? OR
                          editora LIKE ? OR
                          ano_publicacao LIKE ? OR
                          categoria_genero LIKE ? OR
                          numero_paginas LIKE ? OR
                          preco LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 9)
        return cursor.fetchall()

    def consultar_livros(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM livros")
        return cursor.fetchall()
