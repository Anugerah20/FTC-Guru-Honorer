# blueprints/main.py
from flask import Blueprint, render_template, request, redirect, url_for, session
import pandas as pd
from sqlalchemy import create_engine
from extensions import mysql
from flask import current_app as app

# from clear_twitter_text import clear_twitter_text
# from normalisasi import normalisasi
# from stopword import stopword
# from tokenized import tokenized
# from stemming import stemming

# Upload file
# from werkzeug.utils import secure_filename
# import os

main = Blueprint('main', __name__)
# app.config['UPLOAD_FOLDER'] = 'uploads/'

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

# Route menampilkan semua tweet
@main.route('/all-tweet', methods=['GET'])
def allTweet():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tweet_guru")
    data = cur.fetchall()
    cur.close()

    username = session['username']
    return render_template('tweetGuru.html', data=data, current_url=request.path, username=username)

# Route menyimpan file CSV ke Database
@main.route('/save-csv-to-database')
def saveCSVToDatabase():
    df = pd.read_csv('dataset/guru_honorer.csv')
    engine = create_engine(f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}")
    df.to_sql('tweet_guru', con=engine, if_exists='replace', index=False)
    return 'File CSV berhasil disimpan ke database'

# Route membuat tabel preprocessing
@main.route('/preprocessing')
def preprocessing():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS preprocessing (
        id INT PRIMARY KEY AUTO_INCREMENT,
        full_text TEXT,
        tweet_id INT,
        FOREIGN KEY (tweet_id) REFERENCES tweet_guru(id)
    )
    """)
    mysql.connection.commit()
    cur.close()
    return 'Tabel preprocessing berhasil dibuat'

@main.route('/csv-preprocessing')
def preprocessingCSV():
    df = pd.read_csv('dataset/hasil_preprocesing_guru_2.csv')
    engine = create_engine(f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}")
    df.to_sql('preprocessing', con=engine, if_exists='append', index=False)
    return 'File CSV preprocessing berhasil disimpan ke database'

# Route menampilkan semua data preprocessing
@main.route('/show-preprocessing', methods=['GET'])
def AllPreprocessing():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM preprocessing")
    data = cur.fetchall()
    cur.close()

    username = session['username']
    return render_template('preprocessing.html', data=data, current_url=request.path, username=username)

# Unggah file CSV preprocessing
# @main.route('/upload', methods=['POST'])
# def uploadFile():
#     if 'file' not in request.files:
#         return redirect(request.url)
#     file = request.files['file']
#     if file.filename == '':
#         return redirect(request.url)
#     if file:
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         df = pd.read_csv(filepath)
#         df = df.drop_duplicates(subset=['full_text'])
#         df = df.dropna(subset=['full_text'])
#         df = df[['full_text', 'username', 'created_at', 'tweet_url']]
#         df['full_text'] = df['full_text'].apply(clear_twitter_text)
#         df['full_text'] = df['full_text'].apply(normalisasi)
#         df['full_text'] = df['full_text'].apply(stopword)
#         df['full_text'] = df['full_text'].apply(tokenized)

#         cur = mysql.connection.cursor()
#         cur.execute("CREATE TABLE IF NOT EXISTS preprocessing (id INT PRIMARY KEY AUTO_INCREMENT, full_text TEXT, username TEXT, created_at TEXT, tweet_url TEXT)")
#         mysql.connection.commit()
#         cur.close()
#         return 'File berhasil diunggah'
        
        # for index, row in df.iterrows():
        #     cur = mysql.connection.cursor()
        #     cur.execute("INSERT INTO preprocessing (full_text) VALUES (%s)", (row['full_text'],))
        #     mysql.connection.commit()
        #     cur.close()


@main.route('/data-training')
def training():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS data_training (
        id INT PRIMARY KEY AUTO_INCREMENT,
        full_text TEXT,
        category VARCHAR(50) NOT NULL
    )
    """)
    mysql.connection.commit()
    cur.close()
    return 'Tabel data training berhasil dibuat'

@main.route('/data-training-csv')
def DataTraining():
    df = pd.read_csv('dataset/data_training_guru_honorer.csv')
    engine = create_engine(f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}")
    df.to_sql('data_training', con=engine, if_exists='append', index=False)
    return 'File CSV data training berhasil disimpan ke database'

# Route menampilkan data training
@main.route('/all-training', methods=['GET'])
def AllTraining():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM data_training")
    data = cur.fetchall()
    cur.close()

    username = session['username']
    return render_template('data-training.html', data=data, current_url=request.path, username=username)

@main.route('/data-testing')
def testing():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS data_testing (
        id INT PRIMARY KEY AUTO_INCREMENT,
        full_text TEXT,
        categories VARCHAR(50) NOT NULL
    )
    """)
    mysql.connection.commit()
    cur.close()
    return 'Tabel data testing berhasil dibuat'

@main.route('/data-testing-csv')
def DataTesting():
    df = pd.read_csv('dataset/data_testing_guru_honorer.csv')
    engine = create_engine(f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}")
    df.to_sql('data_testing', con=engine, if_exists='append', index=False)
    return 'File CSV data testing berhasil disimpan ke database'

# Route menampilkan data testing
@main.route('/all-testing', methods=['GET'])
def AllTesting():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM data_testing")
    data = cur.fetchall()
    cur.close()

    username = session['username']
    return render_template('data-testing.html', data=data, current_url=request.path, username=username)

# Labeling menggunakan kamus
data = pd.read_csv('dataset/hasil_preprocesing_guru_2.csv')

# Membaca kamus lexicon positif dan negatif
with open('dataset/kamus_negatif.txt', 'r') as file:
    positive_words = file.read().splitlines()

with open('dataset/kamus_positif.txt', 'r') as file:
    negative_words = file.read().splitlines()

# Fungsi untuk menentukan kategori kalimat
def categorize_sentence(sentence):
    positive_count = sum(1 for word in sentence.split() if word in positive_words)
    negative_count = sum(1 for word in sentence.split() if word in negative_words)

    if positive_count > negative_count:
        return 'Positif'
    elif positive_count < negative_count:
        return 'Negatif'
    else:
        return 'Netral'
    
@main.route('/labeling-kamus', methods=['GET', 'POST'])
def labeling_kamus():
    if request.method == 'POST':
        sentence = request.form['sentence']
        category = categorize_sentence(sentence)  # Call the function
        return render_template('labeling-kamus.html', sentence=sentence, category=category)
    else:
        return render_template('labeling-kamus.html')

