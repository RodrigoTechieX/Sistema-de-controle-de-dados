import sqlite3
from datetime import datetime
import time

class BancoDeDadosVeiculos:
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

        # Veículos
        cursor.execute('''CREATE TABLE IF NOT EXISTS veiculos (
                            id INTEGER PRIMARY KEY,
                            tipo TEXT,
                            marca TEXT,
                            modelo TEXT,
                            ano_fabricacao INTEGER,
                            ano_modelo INTEGER,
                            cor TEXT,
                            placa TEXT UNIQUE,
                            quilometragem REAL)''')

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
            cursor.execute("SELECT COUNT(*) FROM veiculos")
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

    # -------------------- VEÍCULOS -------------------- #
    def salvar_veiculo(self, id_veiculo, tipo, marca, modelo, ano_fabricacao, ano_modelo,
                       cor, placa, quilometragem, usuario_logado):
        if id_veiculo is None:
            self.adicionar_veiculo(tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa,
                                   quilometragem, usuario_logado)
        else:
            self.atualizar_veiculo(id_veiculo, tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa,
                                   quilometragem, usuario_logado)

    def adicionar_veiculo(self, tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa,
                          quilometragem, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''INSERT INTO veiculos
                          (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, quilometragem)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, quilometragem))
        self.conexao.commit()

        dados = f"Tipo: {tipo}, Marca: {marca}, Modelo: {modelo}, AnoFab: {ano_fabricacao}, AnoMod: {ano_modelo}, Cor: {cor}, Placa: {placa}, Quilometragem: {quilometragem}"
        self.registrar_auditoria("ADICIONADO", "Veiculos", dados, usuario_logado)

    def atualizar_veiculo(self, id_veiculo, tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa,
                          quilometragem, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute('''UPDATE veiculos
                          SET tipo=?, marca=?, modelo=?, ano_fabricacao=?, ano_modelo=?, cor=?, placa=?, quilometragem=?
                          WHERE id=?''',
                       (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, quilometragem, id_veiculo))
        self.conexao.commit()

        dados = f"ID: {id_veiculo}, Tipo: {tipo}, Marca: {marca}, Modelo: {modelo}, AnoFab: {ano_fabricacao}, AnoMod: {ano_modelo}, Cor: {cor}, Placa: {placa}, Quilometragem: {quilometragem}"
        self.registrar_auditoria("EDITADO", "Veiculos", dados, usuario_logado)

    def excluir_veiculo(self, id_veiculo, usuario_logado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM veiculos WHERE id = ?", (id_veiculo,))
        veiculo = cursor.fetchone()
        if veiculo:
            cursor.execute("DELETE FROM veiculos WHERE id = ?", (id_veiculo,))
            self.conexao.commit()

            dados = f"ID: {veiculo[0]}, Tipo: {veiculo[1]}, Marca: {veiculo[2]}, Modelo: {veiculo[3]}, AnoFab: {veiculo[4]}, AnoMod: {veiculo[5]}, Cor: {veiculo[6]}, Placa: {veiculo[7]}, Quilometragem: {veiculo[8]}"
            self.registrar_auditoria("EXCLUÍDO", "Veiculos", dados, usuario_logado)

    # -------------------- RESTAURAR -------------------- #
    def restaurar_dados(self, tabela, dados, usuario_logado):
        if tabela.lower() != "veiculos":
            return False

        cursor = self.conexao.cursor()
        try:
            campos = {}
            for parte in dados.split(", "):
                if ": " in parte:
                    chave, valor = parte.split(": ", 1)
                    campos[chave.strip()] = valor.strip()

            tipo = campos.get("Tipo", "")
            marca = campos.get("Marca", "")
            modelo = campos.get("Modelo", "")
            cor = campos.get("Cor", "")
            placa = campos.get("Placa", "")

            try:
                ano_fabricacao = int(campos.get("AnoFab", 0))
            except:
                ano_fabricacao = 0

            try:
                ano_modelo = int(campos.get("AnoMod", 0))
            except:
                ano_modelo = 0

            try:
                quilometragem = float(campos.get("Quilometragem", 0))
            except:
                quilometragem = 0.0

            try:
                cursor.execute('''INSERT INTO veiculos
                                  (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, quilometragem)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                               (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, quilometragem))
                self.conexao.commit()
            except sqlite3.IntegrityError:
                placa_nova = f"{placa}-R{int(time.time())}"
                cursor.execute('''INSERT INTO veiculos
                                  (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa, quilometragem)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                               (tipo, marca, modelo, ano_fabricacao, ano_modelo, cor, placa_nova, quilometragem))
                self.conexao.commit()

            dados_restaurados = f"Tipo: {tipo}, Marca: {marca}, Modelo: {modelo}, AnoFab: {ano_fabricacao}, AnoMod: {ano_modelo}, Cor: {cor}, Placa: {placa}, Quilometragem: {quilometragem}"
            self.registrar_auditoria("RESTAURADO", "Veiculos", dados_restaurados, usuario_logado)
            return True

        except Exception as e:
            print(f"Erro ao restaurar veículo: {e}")
            return False

    # -------------------- PESQUISAS -------------------- #
    def pesquisar_veiculos(self, termo_pesquisa):
        cursor = self.conexao.cursor()
        cursor.execute('''SELECT * FROM veiculos WHERE
                          id LIKE ? OR
                          tipo LIKE ? OR
                          marca LIKE ? OR
                          modelo LIKE ? OR
                          ano_fabricacao LIKE ? OR
                          ano_modelo LIKE ? OR
                          cor LIKE ? OR
                          placa LIKE ? OR
                          quilometragem LIKE ?''',
                       ('%' + termo_pesquisa + '%',) * 9)
        return cursor.fetchall()

    def consultar_veiculos(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM veiculos ORDER BY id ASC")
        return cursor.fetchall()
