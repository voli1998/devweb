import sqlite3

# Conectar ao banco de dados (será criado se não existir)
connection = sqlite3.connect('users.db')

with connection:
    # Criar tabela de usuários com todas as colunas necessárias
    connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            birthdate DATE NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        );
    ''')

    # Criar tabela de conteúdo
    connection.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_path TEXT,
            video_path TEXT
        );
    ''')

    # Criar tabela da Bíblia
    connection.execute('''
        CREATE TABLE IF NOT EXISTS bible (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT NOT NULL
        );
    ''')

    # Adicionar um usuário administrador
    connection.execute('''
        INSERT INTO users (full_name, email, birthdate, username, password, role)
        VALUES ('Pandinha Master', 'paulohpjunior1998@gmail.com', '1998-07-20', 'Panda_Master', '060801', 'admin')
    ''')

connection.close()
