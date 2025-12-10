from datetime import datetime
import mysql.connector
from mysql.connector import Error


def conectar():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="senac",
            database="pi",
            port=3307,
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


def cadastrar_projeto(nome_projeto, data_entrega):
    try:
        sql = "INSERT INTO pi.projeto (nome, data_inicio, data_entrega) VALUES (%s, NOW(), %s);"
        conn = conectar()
        if conn is not None:
            cursor = conn.cursor()
            valores = (nome_projeto, data_entrega)
            cursor.execute(sql, valores)
            conn.commit()
            return True
        else:
            return False
    except Error as e:
        print("Deu ruim!", e)
    finally:
        cursor.close()
        conn.close()


def listar_projetos_e_alunos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT t1.nome FROM pi.projeto as t1 LEFT JOIN pi.aluno as t2 ON t1.id = t2.Projeto_id;"
        )

        for linha in cursor.fetchall():
            print(linha)
    except Error as e:
        print("Deu ruim!", e)
    finally:
        cursor.close()
        conn.close()


def alterar_projeto(id, nome_projeto, data_entrega):
    try:
        sql = "UPDATE projeto SET nome = %s, data_inicio = NOW(), data_entrega = %s WHERE id = %s;"
        conn = conectar()
        if conn is not None:
            cursor = conn.cursor()
            valores = (nome_projeto, data_entrega, id)
            cursor.execute(sql, valores)
            conn.commit()
            print("A tabela projeto foi atualizada com sucesso!")
            return True
        else:
            return False
    except Error as e:
        print("Deu ruim!", e)


def deletar_projeto(id):
    try:
        sql = "DELETE FROM projeto WHERE id = %s"
        conn = conectar()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(sql, (id,))
            conn.commit()
            print("Projeto deletado com sucesso!")
            return True
    except Error as e:
        print("Deu ruim!", e)


def menu():
    while True:
        print("MENU")
        print("1 - Cadastrar Projeto")
        print("2 - Lista Projeto + Alunos")
        print("3 - Alterar Projeto")
        print("4 - Deletar Projeto")
        print("0 - Sair")

        op = int(input("Escolha uma opção: "))
        if op == 0:
            break

        match op:
            case 1:
                print("Você selecionou cadastrar um projeto.")
                nome_projeto = input("Digite o nome do projeto: ")
                dia, mes, ano = map(int, input("Digite o dia/mes/ano").split("/"))
                data_entrega = datetime(ano, mes, dia, 0, 0, 0)
                data_formatada = data_entrega.strftime("%Y-%m-%d")
                cadastrar_projeto(nome_projeto, data_formatada)
                print("Projeto Cadastrado com sucesso!")
            case 2:
                print("Nomes de todos os projetos:")
                listar_projetos_e_alunos()
            case 3:
                id_projeto = input("Digite o id do projeto: ")
                novo_nome_projeto = input("Digite o novo nome do projeto: ")
                dia, mes, ano = map(int, input("Digite o dia/mes/ano").split("/"))
                data_entrega = datetime(ano, mes, dia, 0, 0, 0)
                data_formatada = data_entrega.strftime("%Y-%m-%d")
                alterar_projeto(id_projeto, novo_nome_projeto, data_formatada)
                print("Projeto Cadastrado com sucesso!")
            case 4:
                id_projeto = input("Digite o id do projeto: ")
                deletar_projeto(id_projeto)


if __name__ == "__main__":
    main()
    menu()
