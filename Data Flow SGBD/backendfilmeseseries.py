import sqlite3
from datetime import datetime
import time

class BancoDeDadosFilmeseSeries:
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

        # Filmes e Séries (unificados)
        cursor.execute('''CREATE TABLE IF NOT EXISTS Midias (
                            id INTEGER PRIMARY KEY,
                            tipo TEXT,
                            nome TEXT,
                            diretores TEXT,
                            ano_estreia INTEGER,
                            plataforma TEXT,
                            duracao INTEGER,
                            temporadas INTEGER,
                            episodios INTEGER)''')

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
        cursor = self.conexao.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            cursor.execute("SELECT COUNT(*) FROM Midias")
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

    # -------------------- MÍDIAS -------------------- #
    def salvar_midia(self, id_midia, tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios, usuario_logado):
        """Se id_midia for None, adiciona nova mídia. Caso contrário, atualiza a existente."""
        if id_midia is None:
            self.adicionar_midia(tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios, usuario_logado)
        else:
            self.atualizar_midia(id_midia, tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios, usuario_logado)

    def adicionar_midia(self, tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios, usuario_logado):
        # 🔒 Regras automáticas
        if tipo.strip().lower() == "filme":
            temporadas = 0
            episodios = 0

        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO Midias 
                        (tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios))
        self.conexao.commit()

        dados = (f"Tipo: {tipo}, Nome: {nome}, Diretores: {diretores}, Ano de estreia: {ano_estreia}, "
                f"Plataforma: {plataforma}, Duração: {duracao}, Temporadas: {temporadas}, Episódios: {episodios}")
        self.registrar_auditoria("ADICIONADO", "Midias", dados, usuario_logado)


    def atualizar_midia(self, id_midia, tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE Midias
                          SET tipo=?, nome=?, diretores=?, ano_estreia=?, plataforma=?, duracao=?, temporadas=?, episodios=?
                          WHERE id=?''',
                       (tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios, id_midia))
        self.conexao.commit()

        dados = f"ID: {id_midia}, Tipo: {tipo}, Nome: {nome}, Diretores: {diretores}, Ano de estreia: {ano_estreia}, Plataforma: {plataforma}, Duração: {duracao}, Temporadas: {temporadas}, Episódios: {episodios}"
        self.registrar_auditoria("EDITADO", "Midias", dados, usuario_logado)

    def excluir_midia(self, id_midia, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM Midias WHERE id = ?", (id_midia,))
        midia = cursor.fetchone()

        if midia:
            cursor.execute("DELETE FROM Midias WHERE id = ?", (id_midia,))
            self.conexao.commit()

            dados = f"ID: {midia[0]}, Tipo: {midia[1]}, Nome: {midia[2]}, Diretores: {midia[3]}, Ano de estreia: {midia[4]}, Plataforma: {midia[5]}, Duração: {midia[6]}, Temporadas: {midia[7]}, Episódios: {midia[8]}"
            self.registrar_auditoria("EXCLUÍDO", "Midias", dados, usuario_logado)

    # -------------------- RESTAURAR DADOS -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado, create_new=False):
        """
        Padrão unificado (igual aos backends de Produtos e Funcionários)
        """
        if tabela.lower() != "midias":
            return False

        try:
            cursor = self.conexao.cursor()
            partes = {}
            for p in dados.split(", "):
                kv = p.split(": ", 1)
                if len(kv) == 2:
                    partes[kv[0].strip()] = kv[1].strip()

            tipo = partes.get("Tipo", "")
            nome = partes.get("Nome", "")
            diretores = partes.get("Diretores", "")
            plataforma = partes.get("Plataforma", "")
            try:
                ano_estreia = int(partes.get("Ano de estreia", "0") or 0)
            except ValueError:
                ano_estreia = 0
            try:
                duracao = int(partes.get("Duração", "0") or 0)
            except ValueError:
                duracao = 0
            try:
                temporadas = int(partes.get("Temporadas", "0") or 0)
            except ValueError:
                temporadas = 0
            try:
                episodios = int(partes.get("Episódios", "0") or 0)
            except ValueError:
                episodios = 0

            # Inserção principal
            try:
                cursor.execute("""INSERT INTO Midias
                                  (tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                               (tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios))
                self.conexao.commit()
            except sqlite3.IntegrityError:
                if create_new:
                    nome_novo = f"{nome}-R{int(time.time())}"
                    cursor.execute("""INSERT INTO Midias
                                      (tipo, nome, diretores, ano_estreia, plataforma, duracao, temporadas, episodios)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                   (tipo, nome_novo, diretores, ano_estreia, plataforma, duracao, temporadas, episodios))
                    self.conexao.commit()
                else:
                    return False

            # Registrar auditoria da restauração
            dados_restaurados = f"Tipo: {tipo}, Nome: {nome}, Diretores: {diretores}, Ano de estreia: {ano_estreia}, Plataforma: {plataforma}, Duração: {duracao}, Temporadas: {temporadas}, Episódios: {episodios}"
            self.registrar_auditoria("RESTAURADO", "Midias", dados_restaurados, usuario_logado)
            return True

        except Exception as e:
            print("Erro ao restaurar mídia:", e)
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_midias(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM Midias WHERE
                          id LIKE ? OR
                          tipo LIKE ? OR
                          nome LIKE ? OR 
                          diretores LIKE ? OR 
                          ano_estreia LIKE ? OR 
                          plataforma LIKE ? OR 
                          duracao LIKE ? OR 
                          temporadas LIKE ? OR 
                          episodios LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 9)
        return cursor.fetchall()

    def consultar_midias(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM Midias")
        return cursor.fetchall()