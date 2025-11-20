import sqlite3
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class BancoDeDados:
    def __init__(self):
        self.conexao = sqlite3.connect("dados.db")
        self.criar_tabelas()
        self.codigos_redefinir = {}

    def criar_tabelas(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE,
                senha TEXT,
                email TEXT,
                data_nascimento TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS redefinir_senhas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                codigo TEXT,
                data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # ✅ Tabela de auditoria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                operacao TEXT,
                tabela TEXT,
                dados TEXT,
                data_hora TEXT
            )
        """)
        self.conexao.commit()

    # --------------------------
    # AUDITORIA
    # --------------------------
    def registrar_auditoria(self, usuario, operacao, tabela, dados):

        cursor = self.conexao.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO auditoria (usuario, operacao, tabela, dados, data_hora)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario, operacao, tabela, dados, data_hora))
        self.conexao.commit()

    def consultar_auditoria(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM auditoria ORDER BY id DESC")
        return cursor.fetchall()

    def pesquisar_auditoria(self, filtro):
        cursor = self.conexao.cursor()
        like = f"%{filtro}%"
        cursor.execute("""
            SELECT * FROM auditoria
            WHERE usuario LIKE ? OR operacao LIKE ? OR tabela LIKE ? OR dados LIKE ? OR data_hora LIKE ?
            ORDER BY id DESC
        """, (like, like, like, like, like))
        return cursor.fetchall()
    
    def contar_registros(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM auditoria")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
        except Exception as e:
            print(f"Erro ao contar registros: {e}")
            return 0
        
    # dentro da classe BancoDeDados
    def get_indicadores(self):
        """
        Retorna um dicionário com contagens de todas as tabelas relevantes.
        Ex: {"filmes": 10, "produtos": 5, ...}
        Se uma tabela não existir, retorna 0 para essa chave.
        """
        cursor = self.conexao.cursor()
        tabelas = {
            "Midias": "Midias",
            "produtos": "produtos",
            "veiculos": "veiculos",
            "funcionarios": "funcionarios",
            "livros": "livros",
            "musicas": "musicas",
            "jogos": "jogos",
            "receitas": "receitas",
            "auditoria": "auditoria",
            # se você usa outro nome, ajuste aqui
        }
        resultados = {}
        for chave, tabela in tabelas.items():
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                r = cursor.fetchone()
                resultados[chave] = r[0] if r else 0
            except Exception as e:
                # se tabela não existe ou erro, devolve 0 e continua
                print(f"[get_indicadores] erro tabela {tabela}: {e}")
                resultados[chave] = 0
        return resultados



    def excluir_varios_registros_auditoria(self, ids):
        cursor = self.conexao.cursor()
        cursor.executemany("DELETE FROM auditoria WHERE id = ?", [(i,) for i in ids])
        self.conexao.commit()

    def restaurar_dados(self, usuario, id_auditoria):
        import json
        from datetime import datetime
        import re

        cursor = self.conexao.cursor()

        try:
            cursor.execute("SELECT operacao, tabela, dados FROM auditoria WHERE id = ?", (id_auditoria,))
            registro = cursor.fetchone()

            if not registro:
                return False, "Registro não encontrado."

            operacao, tabela, dados_raw = registro

            if operacao.upper() != "EXCLUÍDO":
                return False, "Apenas registros com operação 'EXCLUÍDO' podem ser restaurados."

            tabela_norm = tabela.lower().strip()

            # 1) tenta JSON primeiro
            dados_dict = None
            try:
                dados_dict = json.loads(dados_raw)
                if not isinstance(dados_dict, dict):
                    # se veio uma lista ou outro formato, falha
                    dados_dict = None
            except Exception:
                dados_dict = None

            # 2) se não for JSON, tenta parse do formato "Chave: Valor, Chave2: Valor2"
            if dados_dict is None:
                partes = {}
                # quebra respeitando vírgulas, mas evitando quebrar valores que possam conter vírgula
                # aqui assumimos formato simples "Chave: Valor, Chave2: Valor2"
                for p in re.split(r',\s*(?![^()]*\))', str(dados_raw)):
                    if ": " in p:
                        k, v = p.split(": ", 1)
                        partes[k.strip()] = v.strip()
                if not partes:
                    return False, "Não foi possível interpretar os dados; formato inválido."
                dados_dict = partes

            # 3) mapeamentos conhecidos por tabela (Chave legível -> nome da coluna)
            # ajuste/expanda se quiser
            mapping_por_tabela = {
                "livros": {
                    "ID": "id", "ISBN": "isbn", "Título": "titulo", "Titulo": "titulo", "Autor(es)": "autores",
                    "Autores": "autores", "Editora": "editora", "Ano": "ano_publicacao", "Ano de publicação": "ano_publicacao",
                    "Categoria/Gênero": "categoria_genero", "Categoria": "categoria_genero", "Nº de páginas": "numero_paginas",
                    "Numero de paginas": "numero_paginas", "Preço": "preco", "Preco": "preco"
                },
                "musicas": {
                    "ID": "id", "Título": "titulo", "Titulo": "titulo", "Artista/Banda": "artista_banda",
                    "Artista": "artista_banda", "Álbum": "album", "Album": "album", "Gravadora": "gravadora",
                    "Ano de lançamento": "ano_lancamento", "Ano": "ano_lancamento", "Gênero": "genero", "Duracão": "duracao", "Duração": "duracao"
                },
                "jogos": {
                    "ID": "id", "Nome do jogo": "nome_do_jogo", "Contexto": "contexto", "Desenvolvedora": "desenvolvedora",
                    "Publicadora": "publicadora", "Ano de lançamento": "ano_lancamento", "Plataformas": "plataformas",
                    "Gênero": "genero", "Classificação": "classificacao"
                },
                "produtos": {
                    "ID": "id", "Nome": "nome_do_produto", "Nome do produto": "nome_do_produto", "SKU": "codigo_sku",
                    "codigo_sku": "codigo_sku", "Categoria": "categoria", "Fabricante": "fabricante", "Preço": "preco_unitario",
                    "Preco": "preco_unitario", "Quantidade": "quantidade", "Localização": "localizacao_estoque", "Validade": "data_validade"
                },
                "veiculos": {
                    "ID": "id", "Tipo": "tipo", "Marca": "marca", "Modelo": "modelo", "AnoFab": "ano_fabricacao",
                    "AnoMod": "ano_modelo", "Ano": "ano_fabricacao", "Cor": "cor", "Placa": "placa", "Quilometragem": "quilometragem"
                },
                "funcionarios": {
                    "ID": "id", "Tipo": "tipo", "Nome": "nome", "CPF": "cpf", "Cargo": "cargo", "Setor": "setor",
                    "Data de Admissão": "data_admissao", "Salário": "salario", "Salario": "salario", "Contato": "contato"
                },
                "receitas": {
                    "ID": "id", "Nome": "nome_receita", "Nome da receita": "nome_receita", "Criador/Autor": "criador_autor",
                    "Categoria": "categoria", "Tempo de preparo": "tempo_preparo", "Número de porções": "numero_porcoes",
                    "Ingredientes": "ingredientes", "Modo de preparo": "modo_preparo"
                },
                "midias": {
                    "ID": "id", "Tipo": "tipo", "Nome": "nome", "Diretores": "diretores", "Ano de estreia": "ano_estreia",
                    "Plataforma": "plataforma", "Duração": "duracao", "Temporadas": "temporadas", "Episódios": "episodios", "Episodios": "episodios"
                }
            }

            mapping = mapping_por_tabela.get(tabela_norm, {})

            # 4) transforma dados_dict em colunas/valores prontos para inserir
            cols = []
            vals = []
            for k, v in dados_dict.items():
                # tenta mapear por tabela, senão normaliza a chave
                col = mapping.get(k.strip(), None)
                if col is None:
                    # normalização simples: remove acentos/maiusculas -> tenta formar nome de coluna
                    col_guess = k.strip().lower()
                    col_guess = re.sub(r'[^0-9a-z_]', '_', col_guess)  # espaços -> underscore
                    col = col_guess
                # conversão básica de tipos (inteiro/float)
                val = v
                # se valor vazio -> None
                if isinstance(val, str) and val.strip() == "":
                    val = None
                else:
                    # tenta int
                    if isinstance(val, str):
                        val_str = val.strip().replace("R$", "").replace(".", "").replace(",", ".")
                        try:
                            if val_str.isdigit():
                                val = int(val_str)
                            else:
                                valf = float(val_str)
                                # se conversão OK e não é int exato, usa float
                                val = int(valf) if valf.is_integer() else valf
                        except Exception:
                            # deixa como string original
                            val = v
                cols.append(col)
                vals.append(val)

            # 5) remover colunas que coincidam com 'id' (não queremos colocar id manualmente normalmente)
            cols_filtered = []
            vals_filtered = []
            for c, v in zip(cols, vals):
                if c.lower() in ("id", "rowid") or c == "":
                    continue
                cols_filtered.append(c)
                vals_filtered.append(v)

            if not cols_filtered:
                return False, "Nenhuma coluna válida encontrada para inserção."

            # Monta SQL (seguro o suficiente pois colunas vêm de mapeamento/normalização)
            placeholders = ", ".join(["?"] * len(cols_filtered))
            colunas_sql = ", ".join(cols_filtered)

            try:
                cursor.execute(f"INSERT INTO {tabela_norm} ({colunas_sql}) VALUES ({placeholders})", vals_filtered)
                self.conexao.commit()
            except Exception as e:
                return False, f"Erro na inserção na tabela {tabela_norm}: {e}"

            # 6) registrar auditoria de restauração
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                cursor.execute(
                    "INSERT INTO auditoria (usuario, operacao, tabela, dados, data_hora) VALUES (?, ?, ?, ?, ?)",
                    (usuario, "RESTAURADO", tabela_norm, json.dumps(dados_dict, ensure_ascii=False), data_hora)
                )
                self.conexao.commit()
            except Exception as e:
                # não é crítico falhar aqui, mas reporta
                return True, f"Restaurado com sucesso, mas falha ao registrar auditoria: {e}"

            return True, "Dados restaurados com sucesso!"

        except Exception as e:
            return False, f"Erro ao restaurar: {e}"





    # --------------------------
    # USUÁRIOS
    # --------------------------
    def cadastrar_usuario(self, usuario, senha, email, data_nascimento):
        cursor = self.conexao.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (usuario, senha, email, data_nascimento) VALUES (?, ?, ?, ?)",
                (usuario, senha, email, data_nascimento)
            )
            self.conexao.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validar_login(self, usuario, senha):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        return cursor.fetchone() is not None

    def usuario_existe(self, usuario):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        return cursor.fetchone() is not None

    def atualizar_senha(self, email, nova_senha):
        cursor = self.conexao.cursor()
        cursor.execute("UPDATE usuarios SET senha = ? WHERE email = ?", (nova_senha, email))
        self.conexao.commit()

    def gerar_codigo(self, email):
        codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.codigos_redefinir[email] = codigo
        cursor = self.conexao.cursor()
        cursor.execute("INSERT OR REPLACE INTO redefinir_senhas (email, codigo) VALUES (?, ?)", (email, codigo))
        self.conexao.commit()
        return codigo

    def verificar_codigo(self, email, codigo_enviado):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT codigo FROM redefinir_senhas WHERE email = ?", (email,))
        result = cursor.fetchone()
        return result and result[0] == codigo_enviado

    def enviar_codigo_email(self, email_destino, codigo):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_servidor = "smtp.gmail.com"
        smtp_porta = 587
        remetente = "dataflow.auth@gmail.com"
        senha_remetente = "jvrr sgmp hblk rpwp"  # senha de app

        # Cria a mensagem
        mensagem = MIMEMultipart()
        mensagem['From'] = remetente
        mensagem['To'] = email_destino
        mensagem['Subject'] = "Redefinição de Senha – Data Flow"

        # Corpo do e-mail em HTML
        corpo_email_html = f"""
        <html>
        <head>
        <style>
            body {{
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            color: #333333;
            padding: 20px;
            }}
            .container {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
            }}
            h2 {{
            color: #2f80ed;
            }}
            .codigo {{
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
            background-color: #f0f0f0;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
            }}
            p {{
            line-height: 1.5;
            }}
            .footer {{
            margin-top: 30px;
            font-size: 12px;
            color: #888888;
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <h2>Redefinição de Senha – Data Flow</h2>
            <p>Olá,</p>
            <p>Recebemos uma solicitação para redefinir sua senha no sistema <b>Data Flow</b>.</p>
            <p>Use o código abaixo para continuar com o processo de redefinição:</p>
            <div class="codigo">{codigo}</div>
            <p>Se você não solicitou esta alteração, por favor ignore este e-mail.</p>
            <div class="footer">
            © 2025 Data Flow. Todos os direitos reservados.
            </div>
        </div>
        </body>
        </html>
        """

        # Adiciona corpo HTML ao e-mail
        mensagem.attach(MIMEText(corpo_email_html, 'html'))

        # Envia o e-mail
        try:
            servidor = smtplib.SMTP(smtp_servidor, smtp_porta)
            servidor.starttls()
            servidor.login(remetente, senha_remetente)
            servidor.sendmail(remetente, email_destino, mensagem.as_string())
            servidor.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")
            return False


    def verificar_email_existe(self, email):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone() is not None