# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:

        return redirect(url_for('main.showGuru'))

    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']

        if not username or not pwd:
            flash('Email dan password tidak boleh kosong', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if user and pwd == user.password:
            session['username'] = user.username
            flash('Login berhasil', 'success')
            
            return redirect(url_for('main.showGuru'))
        else:
            flash('Email dan password salah', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:

        return redirect(url_for('main.showGuru'))

    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        email = request.form['email']

        if not username or not pwd or not email:
            flash('Username, email dan password tidak boleh kosong', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(username, pwd, email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
