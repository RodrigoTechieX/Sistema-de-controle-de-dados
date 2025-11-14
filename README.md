# 📊 Data Flow -- Sistema de Gerenciamento de Dados (SGBD Desktop)

Data Flow é um sistema completo desenvolvido em **Python + Tkinter**,
criado para gerenciar múltiplas categorias de dados (filmes/séries,
funcionários, veículos, livros, produtos, etc.) em um ambiente simples,
visual e totalmente offline.

O projeto inclui:\
✔ Interface gráfica moderna\
✔ Módulos separados por categoria\
✔ Banco de dados SQLite incluso\
✔ Geração de PDF\
✔ Funções de auditoria\
✔ Lobby central para navegação\
✔ Telas individuais para cada tipo de cadastro

------------------------------------------------------------------------

## ⭐ Tecnologias Utilizadas

-   **Python 3.x**
-   **Tkinter**
-   **Pillow (PIL)**
-   **SQLite**
-   **ReportLab**

------------------------------------------------------------------------

# ⚙️ Como Instalar e Rodar o Projeto

## 1️⃣ Baixe o projeto

Após baixar o repositório, extraia a pasta:

    Data Flow SGBD/

------------------------------------------------------------------------

## 2️⃣ Instale o Python

Baixe em: https://www.python.org/downloads/\
✔ Lembre-se de marcar **Add Python to PATH**.

------------------------------------------------------------------------

## 3️⃣ Instale as dependências

No terminal dentro da pasta do projeto, execute:

``` bash
pip install pillow reportlab
```

------------------------------------------------------------------------

## 4️⃣ Abra o projeto na sua IDE favorita

Você pode usar: - VS Code\
- PyCharm\
- Thonny\
- IDLE\
- ou qualquer IDE de sua preferência

Localize o arquivo:

    Data Flow SGBD/main.py

------------------------------------------------------------------------

## 5️⃣ Execute o sistema

No terminal ou pela IDE:

``` bash
python main.py
```

------------------------------------------------------------------------

# 📂 Estrutura do Projeto

    Data Flow SGBD/
    │
    ├── main.py
    ├── Lobby.py
    ├── Auditoria.py
    │
    ├── backend.py
    ├── backendfilmeseseries.py
    ├── backendfuncionarios.py
    ├── backendjogos.py
    ├── backendlivros.py
    ├── backendmusicas.py
    ├── backendprodutos.py
    ├── backendreceitas.py
    ├── backendveiculos.py
    │
    ├── tela_filmeseseries.py
    ├── tela_funcionarios.py
    ├── tela_jogos.py
    ├── tela_livros.py
    ├── tela_musicas.py
    ├── tela_produtos.py
    ├── tela_receitas.py
    ├── tela_veiculos.py
    │
    ├── dados.db
    │
    └── imagens/

------------------------------------------------------------------------

# 📝 Observações Importantes

-   Não modifique manualmente o arquivo **dados.db**.\
-   Todas as telas usam seus respectivos backends.\
-   A pasta **imagens/** é essencial para o funcionamento visual e
    geração de PDFs.

------------------------------------------------------------------------

# 🤝 Contribuições

Contribuições são bem-vindas!\
Crie issues, envie sugestões ou abra pull requests.

------------------------------------------------------------------------

## 🧑‍💻 Autor

**Rodrigo Ferreira da Silva Filho**  
✉️ [contato.rodrigo.tech@gmail.com]<br>
🔗 [https://www.linkedin.com/in/rodrigo-ferreira-325527272/]<br>
