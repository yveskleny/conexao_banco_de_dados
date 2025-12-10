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