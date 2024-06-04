import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['VIDEO_FOLDER'] = 'static/videos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de upload de 16 MB

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def validar_usuario(username, password):
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def criar_usuario(full_name, email, birthdate, username, password, role='user'):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO users (full_name, email, birthdate, username, password, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (full_name, email, birthdate, username, password, role))
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        birthdate = request.form['birthdate']
        username = request.form['username']
        password = request.form['password']

        criar_usuario(full_name, email, birthdate, username, password)
        flash('Usuário registrado com sucesso!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validar_usuario(username, password)
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('home'))
        else:
            flash('Nome de usuário ou senha incorretos!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Você saiu com sucesso!')
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        flash('Você não tem permissão para acessar esta página.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']
        video = request.files['video']
        
        file_path = None
        video_path = None
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
        if video:
            video_path = os.path.join(app.config['VIDEO_FOLDER'], video.filename)
            video.save(video_path)

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO content (title, content, image_path, video_path)
            VALUES (?, ?, ?, ?)
        ''', (title, content, file_path, video_path))
        conn.commit()
        conn.close()

        flash('Conteúdo adicionado com sucesso!')
        return redirect(url_for('admin'))

    return render_template('admin.html')

@app.route('/content')
def content():
    if 'user_id' not in session:
        flash('Você precisa fazer login para acessar esta página.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    contents = conn.execute('SELECT * FROM content').fetchall()
    conn.close()

    return render_template('content.html', contents=contents)

@app.route('/bible')
def bible():
    conn = get_db_connection()
    books = conn.execute('SELECT DISTINCT book FROM bible').fetchall()
    conn.close()
    return render_template('bible.html', books=books)

@app.route('/bible/<book>')
def bible_book(book):
    conn = get_db_connection()
    chapters = conn.execute('SELECT DISTINCT chapter FROM bible WHERE book = ?', (book,)).fetchall()
    conn.close()
    return render_template('bible_book.html', book=book, chapters=chapters)

@app.route('/bible/<book>/<int:chapter>')
def bible_chapter(book, chapter):
    conn = get_db_connection()
    verses = conn.execute('SELECT * FROM bible WHERE book = ? AND chapter = ?', (book, chapter)).fetchall()
    conn.close()
    return render_template('bible_chapter.html', book=book, chapter=chapter, verses=verses)

if __name__ == '__main__':
    app.run(debug=True)
