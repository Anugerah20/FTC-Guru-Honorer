# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import mysql

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('main.allTweet'))

    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        if not username or not pwd:
            flash('Email dan password tidak boleh kosong', 'danger')
            return redirect(url_for('auth.login'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and pwd == user[1]:
            session['username'] = user[0]
            flash('Login berhasil', 'success')
            return redirect(url_for('main.allTweet'))
        else:
            flash('Email dan password salah', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('main.allTweet'))

    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        email = request.form['email']

        if not username or not pwd or not email:
            flash('Username, email dan password tidak boleh kosong', 'danger')
            return redirect(url_for('auth.register'))

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, pwd))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
