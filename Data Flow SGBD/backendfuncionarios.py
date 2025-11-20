import sqlite3
from datetime import datetime
import time

class BancoDeDadosFuncionarios:
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

        # Funcionários
        cursor.execute('''CREATE TABLE IF NOT EXISTS funcionarios (
                            id INTEGER PRIMARY KEY,
                            tipo TEXT,
                            nome TEXT,
                            cpf TEXT UNIQUE,
                            cargo TEXT,
                            setor TEXT,
                            data_admissao TEXT,
                            salario REAL,
                            contato TEXT)''')

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
        cursor.execute("""
            INSERT INTO auditoria (usuario, operacao, tabela, dados, data_hora)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario, operacao, tabela, dados, data_hora))
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
            cursor.execute("SELECT COUNT(*) FROM funcionarios")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar registros: {e}")
            return 0

    def excluir_varios_registros_auditoria(self, lista_ids):
        cursor = self.conexao.cursor()
        cursor.executemany("DELETE FROM auditoria WHERE id = ?", [(id,) for id in lista_ids])
        self.conexao.commit()

    # -------------------- FUNCIONÁRIOS -------------------- #
    def salvar_funcionario(self, id_funcionario, tipo, nome, cpf, cargo, setor,
                           data_admissao, salario, contato, usuario_logado):
        if id_funcionario is None:
            self.adicionar_funcionario(tipo, nome, cpf, cargo, setor,
                                       data_admissao, salario, contato, usuario_logado)
        else:
            self.atualizar_funcionario(id_funcionario, tipo, nome, cpf, cargo, setor,
                                       data_admissao, salario, contato, usuario_logado)

    def adicionar_funcionario(self, tipo, nome, cpf, cargo, setor,
                              data_admissao, salario, contato, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO funcionarios 
                          (tipo, nome, cpf, cargo, setor, data_admissao, salario, contato) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (tipo, nome, cpf, cargo, setor, data_admissao, salario, contato))
        self.conexao.commit()

        dados = f"Tipo: {tipo}, Nome: {nome}, CPF: {cpf}, Cargo: {cargo}, Setor: {setor}, " \
                f"Data de Admissão: {data_admissao}, Salário: {salario}, Contato: {contato}"
        self.registrar_auditoria("ADICIONADO", "Funcionarios", dados, usuario_logado)

    def atualizar_funcionario(self, id_funcionario, tipo, nome, cpf, cargo, setor,
                              data_admissao, salario, contato, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE funcionarios
                          SET tipo=?, nome=?, cpf=?, cargo=?, setor=?, 
                              data_admissao=?, salario=?, contato=?
                          WHERE id=?''',
                       (tipo, nome, cpf, cargo, setor, data_admissao,
                        salario, contato, id_funcionario))
        self.conexao.commit()

        dados = f"ID: {id_funcionario}, Tipo: {tipo}, Nome: {nome}, CPF: {cpf}, Cargo: {cargo}, " \
                f"Setor: {setor}, Data de Admissão: {data_admissao}, Salário: {salario}, Contato: {contato}"
        self.registrar_auditoria("EDITADO", "Funcionarios", dados, usuario_logado)

    def excluir_funcionario(self, id_funcionario, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (id_funcionario,))
        funcionario = cursor.fetchone()

        if funcionario:
            cursor.execute("DELETE FROM funcionarios WHERE id = ?", (id_funcionario,))
            self.conexao.commit()

            dados = f"ID: {funcionario[0]}, Tipo: {funcionario[1]}, Nome: {funcionario[2]}, CPF: {funcionario[3]}, " \
                    f"Cargo: {funcionario[4]}, Setor: {funcionario[5]}, Data de Admissão: {funcionario[6]}, " \
                    f"Salário: {funcionario[7]}, Contato: {funcionario[8]}"
            self.registrar_auditoria("EXCLUÍDO", "Funcionarios", dados, usuario_logado)

    # -------------------- RESTAURAR -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado):
        """
        Restaura um funcionário excluído da tabela de auditoria para a tabela original.
        """
        if tabela.lower() != "funcionarios":
            return False

        cursor = self.conexao.cursor()
        try:
            # 1️⃣ Extrair campos do texto da auditoria
            campos = {}
            for parte in dados.split(","):
                if ":" in parte:
                    chave, valor = parte.split(":", 1)
                    campos[chave.strip()] = valor.strip()

            tipo = campos.get("Tipo", "")
            nome = campos.get("Nome", "")
            cpf = campos.get("CPF", "")
            cargo = campos.get("Cargo", "")
            setor = campos.get("Setor", "")
            data_admissao = campos.get("Data de Admissão", "")
            contato = campos.get("Contato", "")

            try:
                salario = float(campos.get("Salário", "0").replace("R$", "").replace(",", "."))
            except:
                salario = 0.0

            # 2️⃣ Inserir novamente o funcionário
            try:
                cursor.execute("""
                    INSERT INTO funcionarios
                    (tipo, nome, cpf, cargo, setor, data_admissao, salario, contato)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tipo, nome, cpf, cargo, setor, data_admissao, salario, contato))
                self.conexao.commit()

            except sqlite3.IntegrityError:
                # CPF duplicado — gera novo CPF temporário
                novo_cpf = f"{cpf}-R{int(time.time())}"
                cursor.execute("""
                    INSERT INTO funcionarios
                    (tipo, nome, cpf, cargo, setor, data_admissao, salario, contato)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tipo, nome, novo_cpf, cargo, setor, data_admissao, salario, contato))
                self.conexao.commit()

            # 3️⃣ Registrar restauração
            dados_restaurados = f"Tipo: {tipo}, Nome: {nome}, CPF: {cpf}, Cargo: {cargo}, Setor: {setor}, " \
                                f"Data de Admissão: {data_admissao}, Salário: {salario}, Contato: {contato}"
            self.registrar_auditoria("RESTAURADO", "Funcionarios", dados_restaurados, usuario_logado)
            return True

        except Exception as e:
            print("Erro ao restaurar funcionário:", e)
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_funcionarios(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM funcionarios WHERE
                          id LIKE ? OR
                          tipo LIKE ? OR
                          nome LIKE ? OR
                          cpf LIKE ? OR
                          cargo LIKE ? OR
                          setor LIKE ? OR
                          data_admissao LIKE ? OR
                          salario LIKE ? OR
                          contato LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 9)
        return cursor.fetchall()

    def consultar_funcionarios(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM funcionarios")
        return cursor.fetchall()
