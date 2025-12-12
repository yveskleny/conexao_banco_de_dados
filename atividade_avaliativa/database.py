import mysql.connector
from mysql.connector import Error


def conectar():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="app_user",
            password="senha123",
            database="biblioteca",
            port="3307",
        )

        if conn.is_connected():
            print("Conectado ao MySQL com sucesso!")
            return conn

    except Error as e:
        print("Erro: ", e)
        return None


def inserir_autor(nome_autor):
    try:
        sql = "INSERT INTO biblioteca.autores (nome) VALUES (%s);"
        conn = conectar()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(sql, (nome_autor,))
            conn.commit()
            print(f"Autor {nome_autor} adicionado com sucesso!")
            return True
        else:
            return False
    except Error as e:
        print("Erro: ", e)
    finally:
        cursor.close()
        conn.close()

def inserir_livro(titulo, ano_publicacao, editora, nome_autor):
    try:
        sql = "SELECT id FROM biblioteca.autores WHERE nome = %s"
        conn = conectar()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(sql, (nome_autor,))
            conn.commit()
            print(f"Autor {nome_autor} adicionado com sucesso!")
            return True
        else:
            return False
    except Error as e:
        print("Erro: ", e)
    finally:
        cursor.close()
        conn.close()

def inserir_emprestimo(exemplar):
    pass

def atualizar_email(usuario, novo_email):
    pass

def atualizar_data_devolucao():
    pass

def remover_exemplar():
    pass

# somente se não houver vinculos
def remover_autor():
    pass

def remover_registro_multa():
    pass

def listar_livros_e_autores():
    pass

def listar_emprestimos_abertos():
    pass

def main():
    conexao = conectar()

    if conexao:
        cursor = conexao.cursor()
        cursor.execute("SELECT DATABASE();")
        resultado = cursor.fetchone()
        print("Banco conectado:", resultado[0])

        cursor.close()
        conexao.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    main()
    inserir_autor("Machado de Assis")