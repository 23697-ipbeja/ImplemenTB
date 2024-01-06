import sqlite3
import bcrypt
#from pathlib import Path
import base64
import getpass
 
DATABASE = 'biometric_system.db'
 
def connect_db():
    return sqlite3.connect(DATABASE)
 
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
 
def create_user_table():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    finger_image TEXT,
                    iris_image TEXT
                )
            ''')
 
            # Verifica se há users na tabela
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
 
            # Se não houver users, cria o user admin com senha 'admin'
            if user_count == 0:
                hashed_password = hash_password('admin')  # Hash da senha 'admin'
                cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', hashed_password, 'admin'))
 
            conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Erro no base de dados: {e}")
 
def add_user_to_db():
    username = input("Digite o nome do utilizador: ").strip()
    password = getpass.getpass("Digite a senha: ").strip()
    role = input("Digite a função do utilizador (ex: admin, user): ").strip()
    finger_image_path = input("Caminho da imagem do dedo (deixe em branco se não disponível): ").strip()
    iris_image_path = input("Caminho da imagem da íris (deixe em branco se não disponível): ").strip()
 
    if not username or not password or not role:
        print("Erro: O nome de user, a senha e a função são obrigatórios!")
        return
 
    # Codificar imagens para base64
    finger_image_base64, iris_image_base64 = None, None
    if finger_image_path:
        try:
            with open(finger_image_path, "rb") as finger_file:
                finger_image_base64 = base64.b64encode(finger_file.read()).decode('utf-8')
        except FileNotFoundError:
            print("Imagem do dedo não encontrada.")
 
    if iris_image_path:
        try:
            with open(iris_image_path, "rb") as iris_file:
                iris_image_base64 = base64.b64encode(iris_file.read()).decode('utf-8')
        except FileNotFoundError:
            print("Imagem da íris não encontrada.")
 
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            hashed_password = hash_password(password)  # Hashing da password
 
            cursor.execute('INSERT INTO users (username, password, role, finger_image, iris_image) VALUES (?, ?, ?, ?, ?)',
                           (username, hashed_password, role, finger_image_base64, iris_image_base64))
            conn.commit()
            print(f"user '{username}' adicionado com sucesso com a função '{role}'.")
    except sqlite3.DatabaseError as e:
        print(f"Erro no base de dados: {e}")
 
def edit_user_in_db():
    list_users_from_db()
    user_id = input("Digite o ID do utilizador a ser editado: ").strip()
    if not user_id.isdigit():
        print("Por favor, forneça um ID válido.")
        return
 
    # Obter os detalhes atuais do user
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, role, finger_image, iris_image FROM users WHERE id=?', (user_id,))
            user = cursor.fetchone()
 
            if not user:
                print(f"Nenhum user encontrado com o ID: {user_id}")
                return
 
            print(f"Editando user: {user[0]} (Função atual: {user[1]})")
 
            # Obter novos valores do user
            new_username = input("Digite o novo nome de utilizador (deixe em branco para manter o atual): ").strip() or user[0]
            new_password = getpass.getpass("Digite a nova senha (deixe em branco para manter a atual): ").strip()
            new_role = input("Digite a nova função do utilizador (deixe em branco para manter a atual): ").strip() or user[1]
            finger_image_path = input("Caminho da nova imagem do dedo (deixe em branco para manter a atual): ").strip()
            iris_image_path = input("Caminho da nova imagem da íris (deixe em branco para manter a atual): ").strip()
 
            # Codificar imagens para base64
            new_finger_image = None
            if finger_image_path:
                with open(finger_image_path, "rb") as finger_file:
                    new_finger_image = base64.b64encode(finger_file.read()).decode('utf-8')
            else:
                new_finger_image = user[2]  # Mantem a imagem atual se nenhuma nova for fornecida
 
            new_iris_image = None
            if iris_image_path:
                with open(iris_image_path, "rb") as iris_file:
                    new_iris_image = base64.b64encode(iris_file.read()).decode('utf-8')
            else:
                new_iris_image = user[3]  # Mantem a imagem atual se nenhuma nova for fornecida
 
            # Se a senha foi fornecida, aplica hash
            if new_password:
                hashed_password = hash_password(new_password)
            else:
                # Mantem a senha atual se nenhuma nova for fornecida
                cursor.execute('SELECT password FROM users WHERE id=?', (user_id,))
                hashed_password = cursor.fetchone()[0]
 
            # Atualizar detalhes do user na base de dados
            cursor.execute('''
                UPDATE users
                SET username=?, password=?, role=?, finger_image=?, iris_image=?
                WHERE id=?
            ''', (new_username, hashed_password, new_role, new_finger_image, new_iris_image, user_id))
 
            conn.commit()
            print(f"user com ID {user_id} atualizado com sucesso.")
 
    except sqlite3.DatabaseError as e:
        print(f"Erro no base de dados: {e}")
    except FileNotFoundError:
        print("Uma das imagens não foi encontrada. Por favor, verifique o caminho e tente novamente.")
    except Exception as e: 
        print(f"Porra!, Ocorreu um erro: {e}")
 
def list_users_from_db():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            if users:
                print("\nLista de Utilizadores:")
                print(f"{'ID':<5} {'Username':<20} {'Role':<10} {'Finger Image':<15} {'Iris Image':<15}")
                print("-" * 65)
                for user in users:
                    # Descomente as próximas duas linhas se você quiser exibir as imagens codificadas
                    # finger_image = user[4][:10] + "..." if user[4] else "None"
                    # iris_image = user[5][:10] + "..." if user[5] else "None"
                    print(f"{user[0]:<5} {user[1]:<20} {user[3]:<10} {'Yes' if user[4] else 'No':<15} {'Yes' if user[5] else 'No':<15}")
            else:
                print("Nenhum utilizador encontrado.")
    except sqlite3.DatabaseError as e:
        print(f"Porra!, Erro na base de dados: {e}")
 
def delete_user_from_db(user_id):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
            conn.commit()
            print(f"Utilizador com ID {user_id} apagado com sucesso.")
    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")
 
def authenticate(username, password):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password, role FROM users WHERE username=?', (username,))
            user_record = cursor.fetchone()
 
            if user_record:
                hashed_password, role = user_record
 
                # Verifique se a senha fornecida, após ser hashed, corresponde ao hash armazenado e se o role é 'admin'
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password) and role == 'admin':
                    print(f"Autenticação com sucesso! Bem-vindo {username} ao painel de controle.")
                    return True
                else:
                    print("Acesso negado. Esta área é restrita a administradores.")
                    return False
            else:
                print("Nome de user ou senha incorretos.")
                return False
    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")
    except ValueError as e:
        print(f"Erro ao verificar a senha: {e}")
    return False
 
def painel_controlo():
    username = input("Digite o nome de utilizador: ").strip()
    password = getpass.getpass("Digite a senha: ").strip()
 
    if authenticate(username, password):
        while True:
            print("\nOpção 2 - Painel de Controlo")
            print("1 - Introduzir utilizador")
            print("2 - Apagar utilizador")
            print("3 - Editar utilizador")
            print("4 - Listar utilizadores")
            print("5 - Voltar Atrás")
 
            choice = input("Escolha uma opção: ")
 
            if choice == '1':
                add_user_to_db()
            elif choice == '2':
                list_users_from_db()
                user_id = input("Introduza o ID do utilizador que deseja apagar: ")
                delete_user_from_db(user_id)
            elif choice == '3':
                edit_user_in_db()
            elif choice == '4':
                list_users_from_db()
            elif choice == '5':
                break
            else:
                print("Opção inválida. Tente novamente.")
    else:
        print("Autenticação falhada.")
 
def main():
    create_user_table()
    while True:
        print("\nMenu Principal")
        print("1 - Login Biometrico")
        print("2 - Painel de Controlo")
        print("3 - Sair")
 
        choice = input("Escolha uma opção: ")
 
        if choice == '1':
            # Função de login biometrico aqui
            ...
        elif choice == '2':
            painel_controlo()
        elif choice == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
 
if __name__ == "__main__":
    main()
