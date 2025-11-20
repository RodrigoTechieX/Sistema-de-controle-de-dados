import sqlite3
from datetime import datetime
from tkinter import messagebox


class BancoDeDadosMusicas:
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

        # Músicas
        cursor.execute('''CREATE TABLE IF NOT EXISTS musicas (
                            id INTEGER PRIMARY KEY,
                            titulo TEXT,
                            artista_banda TEXT,
                            album TEXT,
                            gravadora TEXT,
                            ano_lancamento INTEGER,
                            genero TEXT,
                            duracao TEXT)''')

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
            cursor.execute("SELECT COUNT(*) FROM musicas")
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

    # -------------------- MÚSICAS -------------------- #
    def salvar_musica(self, id_musica, titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao, usuario_logado):
        if id_musica is None:
            self.adicionar_musica(titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao, usuario_logado)
        else:
            self.atualizar_musica(id_musica, titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao, usuario_logado)

    def adicionar_musica(self, titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO musicas 
                          (titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao))
        self.conexao.commit()

        dados = f"Título: {titulo}, Artista/Banda: {artista_banda}, Álbum: {album}, Gravadora: {gravadora}, Ano de lançamento: {ano_lancamento}, Gênero: {genero}, Duração: {duracao}"
        self.registrar_auditoria("ADICIONADO", "Musicas", dados, usuario_logado)

    def atualizar_musica(self, id_musica, titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE musicas
                          SET titulo=?, artista_banda=?, album=?, gravadora=?, 
                              ano_lancamento=?, genero=?, duracao=?
                          WHERE id=?''',
                       (titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao, id_musica))
        self.conexao.commit()

        dados = f"ID: {id_musica}, Título: {titulo}, Artista/Banda: {artista_banda}, Álbum: {album}, Gravadora: {gravadora}, Ano de lançamento: {ano_lancamento}, Gênero: {genero}, Duração: {duracao}"
        self.registrar_auditoria("EDITADO", "Musicas", dados, usuario_logado)

    def excluir_musica(self, id_musica, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM musicas WHERE id = ?", (id_musica,))
        musica = cursor.fetchone()

        if musica:
            cursor.execute("DELETE FROM musicas WHERE id = ?", (id_musica,))
            self.conexao.commit()

            dados = f"ID: {musica[0]}, Título: {musica[1]}, Artista/Banda: {musica[2]}, Álbum: {musica[3]}, Gravadora: {musica[4]}, Ano de lançamento: {musica[5]}, Gênero: {musica[6]}, Duração: {musica[7]}"
            self.registrar_auditoria("EXCLUÍDO", "Musicas", dados, usuario_logado)

    def restaurar_dados(self, tabela, dados, usuario_logado, create_new=False):
        import sqlite3, time
        cursor = self.conexao.cursor()

        if tabela.lower() == "musicas":
            try:
                # Quebra os dados da auditoria em chave: valor
                partes = {}
                for p in dados.split(", "):
                    kv = p.split(": ", 1)
                    if len(kv) == 2:
                        partes[kv[0].strip()] = kv[1].strip()

                titulo = partes.get("Título", "")
                artista_banda = partes.get("Artista/Banda", "")
                album = partes.get("Álbum", "")
                gravadora = partes.get("Gravadora", "")
                genero = partes.get("Gênero", "")
                duracao = partes.get("Duração", "")
                try:
                    ano_lancamento = int(partes.get("Ano de lançamento", "0").strip() or 0)
                except ValueError:
                    ano_lancamento = 0

                # Tenta inserir normalmente
                try:
                    cursor.execute('''INSERT INTO musicas
                                    (titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao))
                    self.conexao.commit()
                except sqlite3.IntegrityError:
                    # Se o registro já existir e create_new=True, cria uma cópia única
                    if create_new:
                        titulo_novo = f"{titulo} (R{int(time.time())})"
                        cursor.execute('''INSERT INTO musicas
                                        (titulo, artista_banda, album, gravadora, ano_lancamento, genero, duracao)
                                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (titulo_novo, artista_banda, album, gravadora, ano_lancamento, genero, duracao))
                        self.conexao.commit()
                    else:
                        return False

                # Registra a ação de restauração na auditoria
                dados_restaurados = (
                    f"Título: {titulo}, Artista/Banda: {artista_banda}, Álbum: {album}, "
                    f"Gravadora: {gravadora}, Ano de lançamento: {ano_lancamento}, "
                    f"Gênero: {genero}, Duração: {duracao}"
                )
                self.registrar_auditoria("RESTAURADO", "Musicas", dados_restaurados, usuario_logado)
                return True

            except Exception as e:
                print("Erro ao restaurar música:", e)
                return False

        else:
            return False



    # -------------------- PESQUISAS -------------------- #
    def pesquisar_musicas(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM musicas WHERE
                          id LIKE ? OR
                          titulo LIKE ? OR
                          artista_banda LIKE ? OR
                          album LIKE ? OR
                          gravadora LIKE ? OR
                          ano_lancamento LIKE ? OR
                          genero LIKE ? OR
                          duracao LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 8)
        return cursor.fetchall()

    def consultar_musicas(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM musicas")
        return cursor.fetchall()
