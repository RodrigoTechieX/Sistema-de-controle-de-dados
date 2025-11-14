import sqlite3
from datetime import datetime
import time

class BancoDeDadosReceitas:
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

        # Receitas
        cursor.execute('''CREATE TABLE IF NOT EXISTS receitas (
                            id INTEGER PRIMARY KEY,
                            nome_receita TEXT,
                            criador_autor TEXT,
                            categoria TEXT,
                            tempo_preparo INTEGER,
                            numero_porcoes INTEGER,
                            ingredientes TEXT,
                            modo_preparo TEXT)''')

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
            cursor.execute("SELECT COUNT(*) FROM receitas")
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

    # -------------------- RECEITAS -------------------- #
    def salvar_receita(self, id_receita, nome_receita, criador_autor, categoria, tempo_preparo,
                       numero_porcoes, ingredientes, modo_preparo, usuario_logado):
        if id_receita is None:
            self.adicionar_receita(nome_receita, criador_autor, categoria, tempo_preparo,
                                   numero_porcoes, ingredientes, modo_preparo, usuario_logado)
        else:
            self.atualizar_receita(id_receita, nome_receita, criador_autor, categoria, tempo_preparo,
                                   numero_porcoes, ingredientes, modo_preparo, usuario_logado)

    def adicionar_receita(self, nome_receita, criador_autor, categoria, tempo_preparo,
                          numero_porcoes, ingredientes, modo_preparo, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO receitas
                          (nome_receita, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (nome_receita, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo))
        self.conexao.commit()

        dados = f"Nome: {nome_receita}, Criador/Autor: {criador_autor}, Categoria: {categoria}, " \
                f"Tempo de preparo: {tempo_preparo}, Número de porções: {numero_porcoes}, Ingredientes: {ingredientes}, Modo de preparo: {modo_preparo}"
        self.registrar_auditoria("ADICIONADO", "Receitas", dados, usuario_logado)

    def atualizar_receita(self, id_receita, nome_receita, criador_autor, categoria, tempo_preparo,
                          numero_porcoes, ingredientes, modo_preparo, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE receitas
                          SET nome_receita=?, criador_autor=?, categoria=?, tempo_preparo=?, numero_porcoes=?, ingredientes=?, modo_preparo=?
                          WHERE id=?''',
                       (nome_receita, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo, id_receita))
        self.conexao.commit()

        dados = f"ID: {id_receita}, Nome: {nome_receita}, Criador/Autor: {criador_autor}, Categoria: {categoria}, " \
                f"Tempo de preparo: {tempo_preparo}, Número de porções: {numero_porcoes}, Ingredientes: {ingredientes}, Modo de preparo: {modo_preparo}"
        self.registrar_auditoria("EDITADO", "Receitas", dados, usuario_logado)

    def excluir_receita(self, id_receita, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM receitas WHERE id = ?", (id_receita,))
        receita = cursor.fetchone()

        if receita:
            cursor.execute("DELETE FROM receitas WHERE id = ?", (id_receita,))
            self.conexao.commit()

            dados = f"ID: {receita[0]}, Nome: {receita[1]}, Criador/Autor: {receita[2]}, Categoria: {receita[3]}, " \
                    f"Tempo de preparo: {receita[4]}, Número de porções: {receita[5]}, Ingredientes: {receita[6]}, Modo de preparo: {receita[7]}"
            self.registrar_auditoria("EXCLUÍDO", "Receitas", dados, usuario_logado)

    # -------------------- RESTAURAR -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado):
        if tabela.lower() != "receitas":
            return False

        cursor = self.conexao.cursor()
        try:
            campos = {}
            for parte in dados.split(","):
                if ":" in parte:
                    chave, valor = parte.split(":", 1)
                    campos[chave.strip()] = valor.strip()

            nome_receita = campos.get("Nome", "")
            criador_autor = campos.get("Criador/Autor", "")
            categoria = campos.get("Categoria", "")
            ingredientes = campos.get("Ingredientes", "")
            modo_preparo = campos.get("Modo de preparo", "")

            try:
                tempo_preparo = int(campos.get("Tempo de preparo", 0))
            except:
                tempo_preparo = 0

            try:
                numero_porcoes = int(campos.get("Número de porções", 0))
            except:
                numero_porcoes = 0

            try:
                cursor.execute('''INSERT INTO receitas
                                  (nome_receita, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (nome_receita, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo))
                self.conexao.commit()
            except sqlite3.IntegrityError:
                novo_nome = f"{nome_receita} - R{int(time.time())}"
                cursor.execute('''INSERT INTO receitas
                                  (nome_receita, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)''',
                               (novo_nome, criador_autor, categoria, tempo_preparo, numero_porcoes, ingredientes, modo_preparo))
                self.conexao.commit()

            dados_restaurados = f"Nome: {nome_receita}, Criador/Autor: {criador_autor}, Categoria: {categoria}, " \
                                f"Tempo de preparo: {tempo_preparo}, Número de porções: {numero_porcoes}, " \
                                f"Ingredientes: {ingredientes}, Modo de preparo: {modo_preparo}"
            self.registrar_auditoria("RESTAURADO", "Receitas", dados_restaurados, usuario_logado)
            return True

        except Exception as e:
            print(f"Erro ao restaurar dados: {e}")
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_receitas(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM receitas WHERE
                          id LIKE ? OR
                          nome_receita LIKE ? OR
                          criador_autor LIKE ? OR
                          categoria LIKE ? OR
                          tempo_preparo LIKE ? OR
                          numero_porcoes LIKE ? OR
                          ingredientes LIKE ? OR
                          modo_preparo LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 8)
        return cursor.fetchall()

    def consultar_receitas(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM receitas")
        return cursor.fetchall()
