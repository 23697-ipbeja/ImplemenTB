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
import bcrypt
import base64
import getpass
import cv2
import tkinter as tk
from tkinter import filedialog
import numpy as np
 
DATABASE = 'biometric_system.db'

# Criação da base de dados 
def connect_db():
    return sqlite3.connect(DATABASE)

# Criação de password encriptada 
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

# Criação da tabela de utilizadores 
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
                    finger_image TEXT
                )
            ''')
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            if user_count == 0:
                hashed_password = hash_password('admin')
                cursor.execute('INSERT INTO users (username, password, role, finger_image) VALUES (?, ?, ?, ?)', ('admin', hashed_password, 'admin', None))
            conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"Erro no base de dados: {e}")
 
# Pré-processamento da imagem da impressão digital 
def preprocess_fingerprint(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Não foi possível ler a imagem: {image_path}")
        return None
    image = cv2.equalizeHist(image)
    image = cv2.GaussianBlur(image, (5, 5), 0)
    _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return image

# Extrair minúcias da imagem da impressão digital 
def extract_minutiae(image):
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    minutiae = []
    for contour in contours:
        if cv2.contourArea(contour) > 50:
            x, y = contour[0][0]
            minutiae.append((x, y))
    return minutiae

# Codificar a imagem em base64
def read_and_encode_image(image_path):
    # Ler a imagem utilizando OpenCV
    image = cv2.imread(image_path)
    if image is None:
        print(f"Não foi possível ler a imagem: {image_path}")
        return None
    # Converte a imagem para o formato JPEG
    retval, buffer = cv2.imencode('.jpg', image)
    if retval:
        # Codificar o buffer da imagem em base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        return image_base64
    else:
        print("Não foi possível codificar a imagem.")
        return None

# Caixa de dialogo para selecionar a imagem do dedo
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path

# Visualizar as minúcias extraídas
def visualize_minutiae(image, minutiae):
    for x, y in minutiae:
        cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
    cv2.imshow('Minutiae', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
 
# Autenticação biométrica
def biometric_login():
    print("Selecione a imagem do dedo:")
    finger_image_path = select_file()
 
    # Pré-processar a imagem e extrair minúcias
    binary_finger_image = preprocess_fingerprint(finger_image_path)
    provided_minutiae = extract_minutiae(binary_finger_image) if binary_finger_image is not None else None
 
    if not provided_minutiae:
        print("Não foi possível extrair minúcias da imagem do dedo fornecida.")
        return None
 
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, finger_image FROM users')
 
            for user_record in cursor.fetchall():
                user_id, username, stored_minutiae_str = user_record
 
                if stored_minutiae_str:
                    # Converta a string de minúcias armazenadas de volta para uma lista de tuplos
                    stored_minutiae = [tuple(map(int, point.split(','))) for point in stored_minutiae_str.split(';')]
 
                    # Calcular a pontuação de correspondência
                    match_score = len(set(provided_minutiae) & set(stored_minutiae))
                    threshold = 15  # Valor de limiar para a pontuação de correspondência
                    print(f"Provided minutiae: {provided_minutiae}")
                    print(f"Stored minutiae: {stored_minutiae}")
                    print(f"Match score: {match_score}")
                    if match_score > threshold:
                        print(f"Autenticação biométrica bem-sucedida! Bem-vindo(a), {username}.")
                        return user_id
                    else:
                        print(f"Usuário {username} não corresponde. Pontuação de correspondência: {match_score}")
 
            print("Falha na autenticação biométrica.")
            return None
 
    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")
        return None

# Adicionar utilizador à base de dados 
def add_user_to_db():
    username = input("Digite o nome do utilizador: ").strip()
    password = getpass.getpass("Digite a senha: ").strip()
    role = input("Digite a função do utilizador (ex: admin, user): ").strip()
 
    finger_images_paths = []
    for i in range(5):  # Recolhe 5 impressões digitais
        print(f"Selecione a imagem {i+1} do dedo:")
        finger_image_path = select_file()
        if finger_image_path:
            finger_images_paths.append(finger_image_path)
        else:
            print("Erro: Imagem do dedo é obrigatória!")
            return
 
    if not username or not password or not role or len(finger_images_paths) != 5:
        print("Erro: Todos os campos e imagens são obrigatórios!")
        return
 
    minutiae_str_list = []
    for path in finger_images_paths:
        binary_finger_image = preprocess_fingerprint(path)
        provided_minutiae = extract_minutiae(binary_finger_image) if binary_finger_image is not None else None
 
        if not provided_minutiae:
            print(f"Não foi possível extrair minúcias da imagem do dedo fornecida: {path}")
            return
        minutiae_str = ';'.join(f"{x},{y}" for x, y in provided_minutiae)
        minutiae_str_list.append(minutiae_str)
 
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            hashed_password = hash_password(password)
            # Junta todas as minúcias em uma única string separada por vírgulas
            cursor.execute('INSERT INTO users (username, password, role, finger_image) VALUES (?, ?, ?, ?)',
                           (username, hashed_password, role, ','.join(minutiae_str_list)))
            conn.commit()
            print(f"Usuário '{username}' adicionado com sucesso com a função '{role}'.")
    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")

# Listar utilizadores da base de dados
def list_users_from_db():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            users = cursor.fetchall()
            if users:
                print("\nLista de Utilizadores:")
                print(f"{'ID':<5} | {'Username':<20} | {'Role':<10} | {'Finger Image':<15}")
                print("-" * 60)
                for user in users:
                    finger_image_status = 'Yes' if user[4] else 'No'
                    print(f"{user[0]:<5} | {user[1]:<20} | {user[3]:<10} | {finger_image_status:<15}")
            else:
                print("Nenhum utilizador encontrado.")
    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")

# Editar utilizador da base de dados
def edit_user_in_db():
    list_users_from_db()  # Mostrar a lista de usuários para facilitar a escolha do ID
    user_id = input("Digite o ID do utilizador a ser editado: ").strip()
    
    if not user_id.isdigit():
        print("Por favor, forneça um ID válido.")
        return
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, role, finger_image FROM users WHERE id=?', (user_id,))
            user = cursor.fetchone()

            if not user:
                print(f"Nenhum utilizador encontrado com o ID: {user_id}")
                return

            print(f"\nEditando utilizador: {user[0]}")
            print(f"Função atual: {user[1]}")
            print(f"Imagem de impressão digital {'presente' if user[2] else 'ausente'}.\n")

            new_username = input("Digite o novo nome de utilizador (pressione enter para manter o atual): ").strip() or user[0]
            new_role = input("Digite a nova função do utilizador (pressione enter para manter a atual): ").strip() or user[1]

            update_password = input("Deseja atualizar a senha? (s/n): ").strip().lower() == 's'
            new_password = hash_password(getpass.getpass("Digite a nova senha: ").strip()) if update_password else user[2]

            update_finger_image = input("Deseja atualizar a imagem da impressão digital? (s/n): ").strip().lower() == 's'
            if update_finger_image:
                print("Selecione a nova imagem do dedo:")
                finger_image_path = select_file()
                if finger_image_path:
                    new_binary_finger_image = preprocess_fingerprint(finger_image_path)
                    new_provided_minutiae = extract_minutiae(new_binary_finger_image) if new_binary_finger_image is not None else None

                    if not new_provided_minutiae:
                        print("Não foi possível extrair minúcias da nova imagem do dedo fornecida.")
                        return

                    new_finger_image = ';'.join(f"{x},{y}" for x, y in new_provided_minutiae)
                else:
                    print("Nenhuma imagem do dedo foi selecionada. Manter a imagem existente.")
                    new_finger_image = user[2]
            else:
                new_finger_image = user[2]

            cursor.execute('''
                UPDATE users
                SET username=?, password=?, role=?, finger_image=?
                WHERE id=?
            ''', (new_username, new_password, new_role, new_finger_image, user_id))

            conn.commit()
            print(f"\nUsuário com ID {user_id} atualizado com sucesso.")

    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")
    except FileNotFoundError:
        print("Uma das imagens não foi encontrada. Por favor, verifique o caminho e tente novamente.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Apagar utilizador da base de dados
def delete_user_from_db(user_id):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
            conn.commit()
            print(f"Utilizador com ID {user_id} apagado com sucesso.")
    except sqlite3.DatabaseError as e:
        print(f"Erro na base de dados: {e}")

# Autenticação do utilizador 
def authenticate(username, password):
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password, role FROM users WHERE username=?', (username,))
            user_record = cursor.fetchone()
            if user_record:
                hashed_password, role = user_record
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password) and role == 'admin':
                    print(f"Autenticação com sucesso! Bem-vindo {username} ao painel de controlo.")
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

# Menu do painel de controlo 
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

# Função principal 
def main():
    create_user_table()
    while True:
        print("\nMenu Principal")
        print("1 - Login Biometrico")
        print("2 - Painel de Controlo")
        print("3 - Sair")
        choice = input("Escolha uma opção: ")
        if choice == '1':
            biometric_login()
        elif choice == '2':
            painel_controlo()
        elif choice == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
 
if __name__ == "__main__":
    main()