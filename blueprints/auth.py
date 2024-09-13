# blueprints/auth.py
# import yang diperlukan untuk proses login, register, dan logout
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql
import bcrypt

auth = Blueprint('auth', __name__)

# Router untuk memproses login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Cek apakah user sudah melakukan login
    if 'username' in session:
        return redirect(url_for('main.showGuru'))

    # Meminta untuk mengisi username dan password
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        # Cek apakah inputan username dan password kosong
        if not username or not pwd:
            flash('Email dan password tidak boleh kosong', 'danger')
            return redirect(url_for('auth.login'))

        # Perintah mysql proses user melakukan login
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))

        # Perintah untuk menampilkan kodingan SQL
        # EDITOR: Nabil 31/05/2024
        # query = "SELECT username, password FROM users WHERE username = %s"
        # print("Kode query:", cursor.mogrify(query, (username,)))
        # cursor.execute(query, (username,))

        user = cursor.fetchone()
        cursor.close()

        # Cek apakah user dan password sudah cocok dengan data yg ada di database
        # Menggunakan bcrypt untuk hash password
        # if user and pwd == user[1]:
        if user and bcrypt.checkpw(pwd.encode('utf-8'), user[1].encode('utf-8')):
            session['username'] = user[0]
            flash('Login berhasil', 'success')
            return redirect(url_for('main.showGuru'))
        else:
            flash('Email dan password salah', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# Router untuk memproses register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Cek apakah user sudah melakukan login
    if 'username' in session:
        return redirect(url_for('main.showGuru'))

    # Meminta untuk mengisi username, password, dan email
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        email = request.form['email']

        # Cek apakah inputan username, password, dan email kosong
        if not username or not pwd or not email:
            flash('Username, email dan password tidak boleh kosong', 'danger')
            return redirect(url_for('auth.register'))

        # Hash password sebelum disimpan ke database
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), salt).decode('utf-8')

        # Perintah sql untuk memasukkan data user ke database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))

        # Perintah untuk menampilkan kodingan SQL register
        # EDITOR: Nabil 31/05/2024
        # query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        # print("Kode query: ", cursor.mogrify(query, (username, email, pwd)))
        # cursor.execute(query, (username, email, pwd))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

# Route untuk proses keluar dari website
@auth.route('/logout')
def logout():
    # Mengambil username untuk proses keluar
    session.pop('username', None)
    return redirect(url_for('auth.login'))