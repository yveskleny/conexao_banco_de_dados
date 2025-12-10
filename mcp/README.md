# Uso de LLM para consulta a BD

## 1. Configuração do Banco de Dados
Primeiro, crie um script para configurar o banco de dados. Este é o conhecimento que você passará para o Gemini.

**database_setup.py**
```
import sqlite3

DATABASE_FILE = 'meu_banco.db'

def setup_database():
    """Cria o arquivo do banco de dados e as tabelas."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # 1. Tabela 'Clientes'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clientes (
            cliente_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            data_cadastro TEXT
        );
    ''')

    # 2. Tabela 'Produtos'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Produtos (
            produto_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        );
    ''')

    # 3. Tabela 'Vendas'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Vendas (
            venda_id INTEGER PRIMARY KEY,
            cliente_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER NOT NULL,
            data_venda TEXT,
            FOREIGN KEY (cliente_id) REFERENCES Clientes (cliente_id),
            FOREIGN KEY (produto_id) REFERENCES Produtos (produto_id)
        );
    ''')

    # Insere alguns dados de exemplo
    cursor.execute("INSERT OR IGNORE INTO Clientes VALUES (1, 'Alice Silva', 'alice@email.com', '2023-01-15')")
    cursor.execute("INSERT OR IGNORE INTO Clientes VALUES (2, 'Bruno Costa', 'bruno@email.com', '2023-02-20')")
    cursor.execute("INSERT OR IGNORE INTO Produtos VALUES (101, 'Notebook', 4500.00, 5)")
    cursor.execute("INSERT OR IGNORE INTO Produtos VALUES (102, 'Mouse Gamer', 150.00, 50)")
    cursor.execute("INSERT OR IGNORE INTO Vendas VALUES (1, 1, 101, 1, '2023-10-01')")
    cursor.execute("INSERT OR IGNORE INTO Vendas VALUES (2, 2, 102, 2, '2023-10-05')")
    cursor.execute("INSERT OR IGNORE INTO Vendas VALUES (3, 1, 102, 1, '2023-10-10')")


    conn.commit()
    conn.close()
    print(f"Banco de dados '{DATABASE_FILE}' configurado com sucesso.")

if __name__ == '__main__':
    setup_database()
```

Instrução: Execute este script uma vez (python database_setup.py) para criar o arquivo meu_banco.db.

## 2. Implementação da API Flask
Primeiro, crie um script para configurar o banco de dados. Este é o conhecimento que você passará para o Gemini.

Agora, o código principal que lida com a requisição, o Gemini e o banco de dados.

**app.py**
``` 
from flask import Flask, request, jsonify
from google import genai
from google.genai import types
import sqlite3
import os

# --- Configurações ---
app = Flask(__name__)
DATABASE_FILE = 'meu_banco.db'
# A chave de API do Gemini será carregada automaticamente da variável de ambiente GEMINI_API_KEY
API_KEY = ''
client = genai.Client(api_key=API_KEY)

# Definição do Esquema do Banco de Dados para o Gemini
# ISSO É CRUCIAL: Passa a estrutura do DB para o modelo
DB_SCHEMA = """
O banco de dados SQLite contém 3 tabelas:

1. Clientes:
   - cliente_id (INTEGER PRIMARY KEY)
   - nome (TEXT)
   - email (TEXT)
   - data_cadastro (TEXT)

2. Produtos:
   - produto_id (INTEGER PRIMARY KEY)
   - nome (TEXT)
   - preco (REAL)
   - estoque (INTEGER)

3. Vendas:
   - venda_id (INTEGER PRIMARY KEY)
   - cliente_id (INTEGER) - Chave estrangeira para Clientes.cliente_id
   - produto_id (INTEGER) - Chave estrangeira para Produtos.produto_id
   - quantidade (INTEGER)
   - data_venda (TEXT)

Sua tarefa é CONVERTER o prompt do usuário em uma consulta SQL válida para SQLite.
NÃO inclua nenhuma explicação, apenas o código SQL.
"""

def get_sql_from_gemini(prompt):
    """
    Usa o modelo Gemini para gerar uma consulta SQL a partir de um prompt.
    """
    model_name = 'gemini-2.5-flash'  # Modelo rápido e eficiente

    # Constrói o prompt de engenharia para o Gemini
    full_prompt = f"{DB_SCHEMA}\n\nCONVERTA a seguinte solicitação para SQL:\n'{prompt}'"

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                # Garante que a resposta seja o mais concisa possível (apenas o SQL)
                temperature=0.0
            )
        )
        # O modelo deve retornar APENAS o SQL, sem blocos de código
        sql_query = response.text.strip().replace('```sql', '').replace('```', '').strip()
        return sql_query
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {e}")
        return None

def execute_sql_query(sql_query):
    """
    Executa a consulta SQL no banco de dados SQLite.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Recupera os resultados
        results = cursor.fetchall()
        
        # Obtém os nomes das colunas
        column_names = [description[0] for description in cursor.description]
        
        return results, column_names

    except sqlite3.OperationalError as e:
        # Erro de sintaxe SQL ou nome de tabela/coluna inválido
        return str(e), None
    except Exception as e:
        # Outro erro, como o arquivo do DB não encontrado
        return f"Erro de execução no DB: {e}", None
    finally:
        if conn:
            conn.close()

# --- Endpoint da API ---

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Endpoint principal para receber o prompt e retornar o resultado da consulta.
    """
    data = request.get_json()
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"erro": "O campo 'prompt' é obrigatório."}), 400

    # 1. Geração do SQL (Gemini)
    sql_query = get_sql_from_gemini(user_prompt)

    if not sql_query:
        return jsonify({"erro": "Falha ao gerar a consulta SQL. Verifique o log."}), 500

    if not sql_query.lower().startswith('select'):
        # Uma boa prática de segurança: só permite consultas SELECT
        return jsonify({
            "erro": "Consultas não-SELECT (INSERT, UPDATE, DELETE) não são permitidas via API.",
            "consulta_gerada": sql_query
        }), 403


    # 2. Execução do SQL (SQLite)
    results, column_names = execute_sql_query(sql_query)

    # 3. Formatação da Resposta
    if isinstance(results, str):  # Se for uma mensagem de erro
        return jsonify({
            "status": "erro_db",
            "prompt_original": user_prompt,
            "consulta_gerada": sql_query,
            "mensagem": f"Erro de execução do SQL: {results}"
        }), 500
    
    # Formata os resultados como uma lista de dicionários para JSON
    formatted_results = []
    for row in results:
        formatted_results.append(dict(zip(column_names, row)))

    return jsonify({
        "status": "sucesso",
        "prompt_original": user_prompt,
        "consulta_gerada": sql_query,
        "colunas": column_names,
        "resultados": formatted_results
    })

if __name__ == '__main__':
    # A variável de ambiente do Gemini precisa estar definida para rodar:
    # export GEMINI_API_KEY='SUA_CHAVE_AQUI'
    if not os.getenv('GEMINI_API_KEY'):
        print("ERRO: A variável de ambiente GEMINI_API_KEY não está definida.")
    
    print("Iniciando a API Flask...")
    # Você pode querer usar `debug=True` durante o desenvolvimento
    app.run(port=5000)
```

## 3. Como executar
Primeiro, crie um script para configurar o banco de dados. Este é o conhecimento que você passará para o Gemini.

### 3.1 Instale as dependências
```
pip install Flask google-genai
```

### 3.2 Defina sua chave de API
```
export GEMINI_API_KEY='SUA_CHAVE_AQUI'
ou
API_KEY='SUA_CHAVE_AQUI'
```
### 3.3 Configure o banco de dados
```
python database_setup.py
```

### 3.4 Inicie a API Flask
```
python app.py
```

### 3.5 Teste a API (usando curl ou uma ferramenta como Postman)
* __Prompt de Exemplo__: "Quero o nome e o email de todos os clientes que compraram o produto 'Mouse Gamer'."
```
curl -X POST http://127.0.0.1:5000/query \
-H "Content-Type: application/json" \
-d '{"prompt": "Quero o nome e o email de todos os clientes que compraram o produto Mouse Gamer."}'
```
* __Resposta Esperada (JSON):__
```
{
    "status": "sucesso",
    "prompt_original": "Quero o nome e o email de todos os clientes que compraram o produto Mouse Gamer.",
    "consulta_gerada": "SELECT T1.nome, T1.email FROM Clientes AS T1 INNER JOIN Vendas AS T2 ON T1.cliente_id = T2.cliente_id INNER JOIN Produtos AS T3 ON T2.produto_id = T3.produto_id WHERE T3.nome = 'Mouse Gamer';",
    "colunas": [
        "nome",
        "email"
    ],
    "resultados": [
        {
            "nome": "Bruno Costa",
            "email": "bruno@email.com"
        },
        {
            "nome": "Alice Silva",
            "email": "alice@email.com"
        }
    ]
}
```