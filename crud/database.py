# mysql-connector-python
import mysql.connector
from mysql.connector import Error


def conectar():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="local_user",
            password="local_password",
            database="local_db",
            port=3306,
        )

        if conexao.is_connected():
            print("Conectado ao MySQL com sucesso!")
            return conexao

    except Error as e:
        print("Erro ao conectar ao MySQL:", e)
        return None


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
