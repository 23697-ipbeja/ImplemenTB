#                                               
#   IPBEJA: ESTIG                               
#   MESI 22/23                                  
#   Tecnologias Biométricas    
#   Titulo: Implementação de um sistema biométrico                
#   Autores: David Henriques (23697)            
#             Joao Tavanez (3109)               
# 
#            


import sqlite3
import os
import shutil
from pathlib import Path
import base64

def create_user_table():
    conn = sqlite3.connect('biometric_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Valida users na tabela
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Se não houver users, cria admin
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin', 'admin'))

    conn.commit()
    conn.close()


# Função novo user
def add_user_to_db(username, password, role):
    conn = sqlite3.connect('biometric_system.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
    conn.commit()
    conn.close()

def edit_user_in_db(user_id, new_password, new_role, finger_image_path, iris_image_path):
    conn = sqlite3.connect('biometric_system.db')
    cursor = conn.cursor()

        # Encode para base64
    finger_image_base64 = None
    iris_image_base64 = None
    if finger_image_path and iris_image_path:
        with open(finger_image_path, "rb") as finger_file:
            finger_image_base64 = base64.b64encode(finger_file.read()).decode('utf-8')
        with open(iris_image_path, "rb") as iris_file:
            iris_image_base64 = base64.b64encode(iris_file.read()).decode('utf-8')

    # Atualiza info users
    cursor.execute('''
        UPDATE users
        SET password=?, role=?, finger_image=?, iris_image=?
        WHERE id=?
    ''', (new_password, new_role, finger_image_base64, iris_image_base64, user_id))

    conn.commit()
    conn.close()

# Função listar users
def list_users_from_db():
    conn = sqlite3.connect('biometric_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    if users:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}")
    else:
        print("Nenhum utilizador encontrado.")


# Função apagar user
def delete_user_from_db(user_id):
    conn = sqlite3.connect('biometric_system.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def login_biometrico():
    print("Opção 1 - Login Biometrico")

    # Solicita dois ficheiros
    file1 = input("Digite o caminho do primeiro ficheiro: ")
    file2 = input("Digite o caminho do segundo ficheiro: ")


def autenticacao():
    username = input("Digite o nome de utilizador: ")
    password = input("Digite a senha: ")
    conn = sqlite3.connect('biometric_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    return user is not None  # Se já existir o user

def painel_controlo():
    if autenticacao():
        while True:
            print("\nOpção 2 - Painel de Controlo")
            print("1 - Introduzir utilizador")
            print("2 - Apagar utilizador")
            print("3 - Editar utilizador")
            print("4 - Listar utilizadores")
            print("5 - Voltar Atrás")

            choice = input("Escolha uma opção: ")

            if choice == '1':
                username = input("Digite o nome do utilizador: ")
                password = input("Digite a senha: ")
                role = input("Digite a função do utilizador: ")
                add_user_to_db(username, password, role)
                print(f"Utilizador {username} adicionado com sucesso.")
            elif choice == '2':
                list_users_from_db()
                user_id = input("Digite o ID do utilizador a ser apagado: ")
                delete_user_from_db(user_id)
                print(f"Utilizador com ID {user_id} apagado com sucesso.")
            elif choice == '3':
                list_users_from_db()
                user_id = input("Digite o ID do utilizador a ser editado: ")
                new_password = input("Digite a nova senha: ")
                new_role = input("Digite a nova função do utilizador: ")

                finger_image_path = input("Caminho da imagem do dedo: ")
                iris_image_path = input("Caminho da imagem da íris: ")

                edit_user_in_db(user_id, new_password, new_role, finger_image_path, iris_image_path)
                print(f"utilizador com ID {user_id} editado com sucesso.")
            elif choice == '4':
                list_users_from_db()
            elif choice == '5':
                break
            else:
                print("Opção inválida. Tente novamente.")

def main():
    create_user_table() 

    while True:
        print("\nMenu Principal")
        print("1 - Login Biometrico")
        print("2 - Painel de Controlo")
        print("3 - Sair")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            login_biometrico()
        elif choice == '2':
            painel_controlo()
        elif choice == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()

