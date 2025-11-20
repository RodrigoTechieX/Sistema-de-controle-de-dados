import sqlite3
from datetime import datetime

class BancoDeDadosJogos:
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

        # Jogos
        cursor.execute('''CREATE TABLE IF NOT EXISTS jogos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome_do_jogo TEXT NOT NULL,
                            contexto TEXT,
                            desenvolvedora TEXT,
                            publicadora TEXT,
                            ano_lancamento INTEGER,
                            plataformas TEXT,
                            genero TEXT,
                            classificacao TEXT)''')

        # Auditoria
        cursor.execute('''CREATE TABLE IF NOT EXISTS auditoria (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            usuario TEXT,
                            operacao TEXT,
                            tabela TEXT,
                            dados TEXT,
                            data_hora TEXT)''')
        self.conexao.commit()

    # -------------------- AUDITORIA -------------------- #
    def registrar_auditoria(self, operacao, tabela, dados, usuario="Desconhecido"):
        """Registra um evento na tabela de auditoria."""
        try:
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.conexao.cursor()
            cursor.execute(
                """INSERT INTO auditoria (usuario, operacao, tabela, dados, data_hora)
                   VALUES (?, ?, ?, ?, ?)""",
                (usuario, operacao, tabela, dados, data_hora)
            )
            self.conexao.commit()
        except Exception as e:
            # Não levantamos exceção para não quebrar o fluxo do app; apenas logamos.
            print(f"Erro ao registrar auditoria: {e}")

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

    def excluir_varios_registros_auditoria(self, lista_ids):
        cursor = self.conexao.cursor()
        cursor.executemany("DELETE FROM auditoria WHERE id = ?", [(id_,) for id_ in lista_ids])
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

    # -------------------- JOGOS -------------------- #
    def salvar_jogo(self, id_jogo, nome_do_jogo, contexto, desenvolvedora, publicadora,
                    ano_lancamento, plataformas, genero, classificacao, usuario_logado):
        """
        Encaminha para adicionar ou atualizar um jogo.
        Não exibe mensagens — UI trata feedback ao usuário.
        """
        try:
            if not nome_do_jogo or not str(nome_do_jogo).strip():
                # campo obrigatório; frontend deve validar também
                return False

            # conversão segura do ano
            try:
                ano_lancamento = int(ano_lancamento)
            except Exception:
                ano_lancamento = 0

            if not id_jogo:
                return self.adicionar_jogo(nome_do_jogo, contexto, desenvolvedora, publicadora,
                                           ano_lancamento, plataformas, genero, classificacao, usuario_logado)
            else:
                return self.atualizar_jogo(id_jogo, nome_do_jogo, contexto, desenvolvedora, publicadora,
                                           ano_lancamento, plataformas, genero, classificacao, usuario_logado)
        except Exception as e:
            print(f"Erro em salvar_jogo: {e}")
            return False

    def adicionar_jogo(self, nome_do_jogo, contexto, desenvolvedora, publicadora,
                       ano_lancamento, plataformas, genero, classificacao, usuario_logado):
        try:
            cursor = self.conexao.cursor()
            cursor.execute('''INSERT INTO jogos
                              (nome_do_jogo, contexto, desenvolvedora, publicadora,
                               ano_lancamento, plataformas, genero, classificacao)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (nome_do_jogo, contexto, desenvolvedora, publicadora,
                            ano_lancamento, plataformas, genero, classificacao))
            self.conexao.commit()

            dados = (f"Nome do jogo: {nome_do_jogo}, Contexto: {contexto}, Desenvolvedora: {desenvolvedora}, "
                     f"Publicadora: {publicadora}, Ano de lançamento: {ano_lancamento}, Plataformas: {plataformas}, "
                     f"Gênero: {genero}, Classificação: {classificacao}")
            self.registrar_auditoria("ADICIONADO", "Jogos", dados, usuario_logado)
            return True
        except Exception as e:
            print(f"Erro ao adicionar jogo: {e}")
            return False

    def atualizar_jogo(self, id_jogo, nome_do_jogo, contexto, desenvolvedora, publicadora,
                       ano_lancamento, plataformas, genero, classificacao, usuario_logado):
        try:
            cursor = self.conexao.cursor()
            cursor.execute('''UPDATE jogos
                              SET nome_do_jogo=?, contexto=?, desenvolvedora=?, publicadora=?,
                                  ano_lancamento=?, plataformas=?, genero=?, classificacao=?
                              WHERE id=?''',
                           (nome_do_jogo, contexto, desenvolvedora, publicadora, ano_lancamento,
                            plataformas, genero, classificacao, id_jogo))
            self.conexao.commit()

            dados = (f"ID: {id_jogo}, Nome do jogo: {nome_do_jogo}, Contexto: {contexto}, "
                     f"Desenvolvedora: {desenvolvedora}, Publicadora: {publicadora}, "
                     f"Ano de lançamento: {ano_lancamento}, Plataformas: {plataformas}, "
                     f"Gênero: {genero}, Classificação: {classificacao}")
            self.registrar_auditoria("EDITADO", "Jogos", dados, usuario_logado)
            return True
        except Exception as e:
            print(f"Erro ao atualizar jogo: {e}")
            return False

    def excluir_jogo(self, id_jogo, usuario_logado):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT * FROM jogos WHERE id = ?", (id_jogo,))
            jogo = cursor.fetchone()

            if jogo:
                cursor.execute("DELETE FROM jogos WHERE id = ?", (id_jogo,))
                self.conexao.commit()

                dados = (f"ID: {jogo[0]}, Nome do jogo: {jogo[1]}, Contexto: {jogo[2]}, "
                         f"Desenvolvedora: {jogo[3]}, Publicadora: {jogo[4]}, "
                         f"Ano de lançamento: {jogo[5]}, Plataformas: {jogo[6]}, "
                         f"Gênero: {jogo[7]}, Classificação: {jogo[8]}")
                self.registrar_auditoria("EXCLUÍDO", "Jogos", dados, usuario_logado)
                return True
            else:
                return False
        except Exception as e:
            print(f"Erro ao excluir jogo: {e}")
            return False

    # -------------------- RESTAURAR -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado):
        """
        Restaura um registro a partir do campo 'dados' salvo na auditoria.
        Espera string no formato: "Nome do jogo: X, Contexto: Y, Desenvolvedora: Z, ..."
        """
        cursor = self.conexao.cursor()

        if tabela.lower() != "jogos":
            return False

        try:
            partes = {}
            # separa por vírgula, tratando casos onde pode haver vírgula no texto (simples heurística)
            # utiliza split por ", " (com espaço) consistente com o formato de registro gerado
            for p in dados.split(", "):
                chave_valor = p.split(": ", 1)
                if len(chave_valor) == 2:
                    partes[chave_valor[0].strip()] = chave_valor[1].strip()

            nome_do_jogo = partes.get("Nome do jogo", "")
            contexto = partes.get("Contexto", "")
            desenvolvedora = partes.get("Desenvolvedora", "")
            publicadora = partes.get("Publicadora", "")
            plataformas = partes.get("Plataformas", "")
            genero = partes.get("Gênero", "")
            classificacao = partes.get("Classificação", "")
            try:
                ano_lancamento = int(partes.get("Ano de lançamento", "0") or 0)
            except Exception:
                ano_lancamento = 0

            cursor.execute('''INSERT INTO jogos
                              (nome_do_jogo, contexto, desenvolvedora, publicadora,
                               ano_lancamento, plataformas, genero, classificacao)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (nome_do_jogo, contexto, desenvolvedora, publicadora,
                            ano_lancamento, plataformas, genero, classificacao))
            self.conexao.commit()

            dados_restaurados = (f"Nome do jogo: {nome_do_jogo}, Contexto: {contexto}, Desenvolvedora: {desenvolvedora}, "
                                 f"Publicadora: {publicadora}, Plataformas: {plataformas}, Gênero: {genero}, "
                                 f"Classificação: {classificacao}, Ano de lançamento: {ano_lancamento}")
            self.registrar_auditoria("RESTAURADO", "Jogos", dados_restaurados, usuario_logado)
            return True
        except Exception as e:
            print(f"Erro ao restaurar jogo: {e}")
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_jogos(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM jogos WHERE
                          id LIKE ? OR
                          nome_do_jogo LIKE ? OR
                          contexto LIKE ? OR
                          desenvolvedora LIKE ? OR
                          publicadora LIKE ? OR
                          ano_lancamento LIKE ? OR
                          plataformas LIKE ? OR
                          genero LIKE ? OR
                          classificacao LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 9)
        return cursor.fetchall()

    def consultar_jogos(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM jogos")
        return cursor.fetchall()

    def contar_registros(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM jogos")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar registros: {e}")
            return 0
