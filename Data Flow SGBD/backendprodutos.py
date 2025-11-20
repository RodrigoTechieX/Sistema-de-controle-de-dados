import sqlite3
from datetime import datetime
from tkinter import messagebox
import time

class BancoDeDadosProdutos:
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

        # Produtos
        cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                            id INTEGER PRIMARY KEY,
                            nome_do_produto TEXT NOT NULL,
                            codigo_sku TEXT UNIQUE,
                            categoria TEXT,
                            fabricante TEXT,
                            preco_unitario REAL,
                            quantidade INTEGER,
                            localizacao_estoque TEXT,
                            data_validade TEXT)''')

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
            cursor.execute("SELECT COUNT(*) FROM produtos")
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

    # -------------------- PRODUTOS -------------------- #
    def salvar_produto(self, id_produto, nome_do_produto, codigo_sku, categoria, fabricante,
                       preco_unitario, quantidade, localizacao_estoque, data_validade, usuario_logado):
        if id_produto is None:
            self.adicionar_produto(nome_do_produto, codigo_sku, categoria, fabricante,
                                   preco_unitario, quantidade, localizacao_estoque,
                                   data_validade, usuario_logado)
        else:
            self.atualizar_produto(id_produto, nome_do_produto, codigo_sku, categoria, fabricante,
                                   preco_unitario, quantidade, localizacao_estoque,
                                   data_validade, usuario_logado)

    def adicionar_produto(self, nome_do_produto, codigo_sku, categoria, fabricante,
                          preco_unitario, quantidade, localizacao_estoque,
                          data_validade, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO produtos 
                          (nome_do_produto, codigo_sku, categoria, fabricante, preco_unitario, quantidade, localizacao_estoque, data_validade) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (nome_do_produto, codigo_sku, categoria, fabricante, preco_unitario,
                        quantidade, localizacao_estoque, data_validade))
        self.conexao.commit()

        dados = f"Nome: {nome_do_produto}, SKU: {codigo_sku}, Categoria: {categoria}, Fabricante: {fabricante}, Preço: {preco_unitario}, Quantidade: {quantidade}, Localização: {localizacao_estoque}, Validade: {data_validade}"
        self.registrar_auditoria("ADICIONADO", "Produtos", dados, usuario_logado)

    def atualizar_produto(self, id_produto, nome_do_produto, codigo_sku, categoria, fabricante,
                          preco_unitario, quantidade, localizacao_estoque, data_validade, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE produtos
                          SET nome_do_produto=?, codigo_sku=?, categoria=?, fabricante=?, 
                              preco_unitario=?, quantidade=?, localizacao_estoque=?, data_validade=?
                          WHERE id=?''',
                       (nome_do_produto, codigo_sku, categoria, fabricante, preco_unitario,
                        quantidade, localizacao_estoque, data_validade, id_produto))
        self.conexao.commit()

        dados = f"ID: {id_produto}, Nome: {nome_do_produto}, SKU: {codigo_sku}, Categoria: {categoria}, Fabricante: {fabricante}, Preço: {preco_unitario}, Quantidade: {quantidade}, Localização: {localizacao_estoque}, Validade: {data_validade}"
        self.registrar_auditoria("EDITADO", "Produtos", dados, usuario_logado)

    def excluir_produto(self, id_produto, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_produto,))
        produto = cursor.fetchone()

        if produto:
            cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
            self.conexao.commit()

            dados = f"ID: {produto[0]}, Nome: {produto[1]}, SKU: {produto[2]}, Categoria: {produto[3]}, Fabricante: {produto[4]}, Preço: {produto[5]}, Quantidade: {produto[6]}, Localização: {produto[7]}, Validade: {produto[8]}"
            self.registrar_auditoria("EXCLUÍDO", "Produtos", dados, usuario_logado)

    # -------------------- RESTAURAR -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado):
        """
        Restaura um produto excluído da tabela de auditoria para a tabela original.
        """
        if tabela.lower() != "produtos":
            return False

        cursor = self.conexao.cursor()
        try:
            # 1️⃣ Extrai campos do texto da auditoria
            campos = {}
            for parte in dados.split(","):
                if ":" in parte:
                    chave, valor = parte.split(":", 1)
                    campos[chave.strip()] = valor.strip()

            nome = campos.get("Nome", "")
            sku = campos.get("SKU", "")
            categoria = campos.get("Categoria", "")
            fabricante = campos.get("Fabricante", "")
            preco = campos.get("Preço", "0").replace("R$", "").strip() or "0"
            quantidade = campos.get("Quantidade", "0")
            localizacao = campos.get("Localização", "")
            validade = campos.get("Validade", "")

            # Conversão segura de tipos
            try:
                preco = float(preco)
            except:
                preco = 0.0
            try:
                quantidade = int(quantidade)
            except:
                quantidade = 0

            # 2️⃣ Tenta inserir novamente o produto
            try:
                cursor.execute("""
                    INSERT INTO produtos 
                    (nome_do_produto, codigo_sku, categoria, fabricante, preco_unitario, quantidade, localizacao_estoque, data_validade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, sku, categoria, fabricante, preco, quantidade, localizacao, validade))
                self.conexao.commit()

            except sqlite3.IntegrityError:
                # Caso o SKU já exista, gera um novo SKU único
                novo_sku = f"{sku}_R{int(time.time())}"
                cursor.execute("""
                    INSERT INTO produtos 
                    (nome_do_produto, codigo_sku, categoria, fabricante, preco_unitario, quantidade, localizacao_estoque, data_validade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, novo_sku, categoria, fabricante, preco, quantidade, localizacao, validade))
                self.conexao.commit()

            # 3️⃣ Registra a restauração na auditoria
            dados_restaurados = f"Nome: {nome}, SKU: {sku}, Categoria: {categoria}, Fabricante: {fabricante}, Preço: {preco}, Quantidade: {quantidade}, Localização: {localizacao}, Validade: {validade}"
            self.registrar_auditoria("RESTAURADO", "Produtos", dados_restaurados, usuario_logado)
            return True

        except Exception as e:
            print("Erro ao restaurar dados:", e)
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_produtos(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM produtos WHERE
                          id LIKE ? OR
                          nome_do_produto LIKE ? OR
                          codigo_sku LIKE ? OR
                          categoria LIKE ? OR
                          fabricante LIKE ? OR
                          preco_unitario LIKE ? OR
                          quantidade LIKE ? OR
                          localizacao_estoque LIKE ? OR
                          data_validade LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 9)
        return cursor.fetchall()

    def consultar_produtos(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM produtos")
        return cursor.fetchall()
