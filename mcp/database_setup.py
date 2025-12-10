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