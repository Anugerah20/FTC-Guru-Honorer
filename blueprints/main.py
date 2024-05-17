# blueprints/main.py
from flask import Blueprint, flash, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from sqlalchemy import create_engine
from extensions import mysql
from flask import current_app as app
from dateutil import parser as date_parser
from datetime import datetime

# Import fungsi preprocessing
from clear_twitter_text import clear_twitter_text
from normalisasi import normalisasi
from stopword import stopword
from tokenized import tokenized
from stemming import stemming

# Upload file
from werkzeug.utils import secure_filename
import os

# data uji dan data latih
from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
# from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder
import joblib

main = Blueprint('main', __name__)
# Upload file
# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route index
# @main.route('/')
# def index():
#     return render_template('upload.html')

# @main.route('/upload-file',methods=['POST'])
# def uploadFile():

#      uploaded_file = request.files['file']

#      if uploaded_file.filename != '':
#           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
#           uploaded_file.save(file_path)
#           parseCSV(file_path)

#           return redirect(url_for('home'))
     
# def parseCSV(file_path):
#     col_names = [
#         'conversation_id_str'
#     ]
#     col_names = [
#         'conversation_id_str', 'created_at', 'favorite_count', 'full_text', 'id_str',
#         'image_url', 'in_reply_to_screen_name', 'lang', 'location', 'quote_count',
#         'reply_count', 'retweet_count', 'tweet_url', 'user_id_str', 'username'
#     ]

#     csvData = pd.read_csv(file_path,names=col_names,header=None)


#     for i, row in csvData.iterrows():
#         sql = """INSERT INTO tweet_guru (
#                 conversation_id_str, created_at, favorite_count, full_text, id_str,
#                 image_url, in_reply_to_screen_name, lang, location, quote_count,
#                 reply_count, retweet_count, tweet_url, user_id_str, username
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

#         value = (
#             row['conversation_id_str'], row['created_at'], row['favorite_count'], row['full_text'], row['id_str'],
#             row['image_url'], row['in_reply_to_screen_name'], row['lang'], row['location'], row['quote_count'],
#             row['reply_count'], row['retweet_count'], row['tweet_url'], row['user_id_str'], row['username']
#         )
#         mycursor = mysql.connection.cursor()  # Add this line to define mycursor
#         mycursor.execute(sql,value)
#         mysql.connection.commit()

# Route index
@main.route('/')
def index():
    return redirect(url_for('main.showGuru'))

# Route upload file CSV dan simpan ke database
@main.route('/upload-file', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = save_uploaded_file(uploaded_file)
            if file_path:
                parse_and_insert_csv(file_path)
                flash('File berhasil diunggah dan disimpan ke database', 'success')
                return redirect(url_for('main.showGuru'))
    return render_template('tweetGuru.html')

def save_uploaded_file(uploaded_file):
    file_path = None
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    except Exception as e:
        print("Error saving uploaded file:", str(e))
    return file_path

def parse_and_insert_csv(file_path):
    try:
        print("Parsing and inserting CSV file:", file_path)
        col_names = [
            'conversation_id_str', 'created_at', 'favorite_count', 'full_text', 'id_str',
            'image_url', 'in_reply_to_screen_name', 'lang', 'location', 'quote_count',
            'reply_count', 'retweet_count', 'tweet_url', 'user_id_str', 'username'
        ]
        csvData = pd.read_csv(file_path, names=col_names, header=None)
        csvData.replace('nan', None, inplace=True)

        for i, row in csvData.iterrows():
            location = deleteNonAsciiCharacters(row['location'])
            row = row.fillna('')
            created_at = row['created_at']

            # Menggunakan dateutil.parser.parse() untuk mem-parse created_at_str
            try:
                # created_at_obj = date_parser.parse(created_at)
                created_at_obj = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                print("Tidak dapat mem-parse created_at:", created_at)
                # Lewati baris ini dan lanjutkan ke baris berikutnya
                continue

            # created_at_datetime = datetime.fromtimestamp(created_at.timestamp())
            # row['created_at'] = created_at_datetime.strftime('%Y-%m-%d %H:%M:%S')

            sql = """INSERT INTO guru (
                conversation_id_str, created_at, favorite_count, full_text, id_str,
                image_url, in_reply_to_screen_name, lang, location, quote_count,
                reply_count, retweet_count, tweet_url, user_id_str, username
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            values = (
                row['conversation_id_str'], created_at_obj, row['favorite_count'], row['full_text'], row['id_str'],
                row['image_url'], row['in_reply_to_screen_name'], row['lang'], location, row['quote_count'],
                row['reply_count'], row['retweet_count'], row['tweet_url'], row['user_id_str'], row['username']
            )

            cur = mysql.connection.cursor()
            cur.execute(sql, values)
            mysql.connection.commit()
            cur.close()

    except Exception as e:
        print("Error parsing and inserting CSV:", str(e))

def deleteNonAsciiCharacters(text):
    if isinstance(text, float) and pd.isna(text):
        return 
    else:
        return ''.join(char for char in text if ord(char) < 128)

# Route menampilkan semua data guru
@main.route('/show-guru', methods=['GET'])
def showGuru():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM guru")
    data = cur.fetchall()
    cur.close()

    username = session['username']
    return render_template('tweetGuru.html', data=data, current_url=request.path, username=username)

# Route upload Preprocessing CSV dan simpan ke database mysql
# @main.route('/upload-preprocessing', methods=['GET', 'POST'])
# def uploadPreprocessing():
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
#         df = df.drop_duplicates(subset=['full_text']).dropna(subset=['full_text'])
        # df = df.dropna(subset=['full_text'])
        # df = df[['full_text', 'username', 'created_at', 'tweet_url']]
        # df['full_text'] = df['full_text'].apply(clear_twitter_text)
        # df['full_text'] = df['full_text'].apply(normalisasi)
        # df['full_text'] = df['full_text'].apply(stopword)
        # df['full_text'] = df['full_text'].apply(tokenized)

        # reset index dataframe
        # df.reset_index(drop=True, inplace=True)

        # cur = mysql.connection.cursor()
        # cur.execute("CREATE TABLE IF NOT EXISTS preprocess_guru (id INT PRIMARY KEY AUTO_INCREMENT, full_text TEXT, username TEXT, created_at TEXT, tweet_url TEXT)")
        # mysql.connection.commit()
        # cur.close()

        # for index, row in df.iterrows():
        #     cur = mysql.connection.cursor()
        #     cur.execute("INSERT INTO preprocess_guru (full_text, username, created_at, tweet_url) VALUES (%s, %s, %s, %s)", (row['full_text'], row['username'], row['created_at'], row['tweet_url']))
        #     mysql.connection.commit()
        #     cur.close()
        
        # return render_template('preprocessing.html')

# Route upload Preprocessing CSV dan simpan ke database mysql
@main.route('/upload-preprocessing', methods=['GET', 'POST'])
def uploadPreprocessing():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        # Cek full_text ada di dataframe
        if 'full_text' not in df.columns:
            return "Column 'full_text' not found in the CSV file", 400

        # Drop duplikasi dan nilai kosong
        df = df.drop_duplicates(subset=['full_text'])
        df = df.dropna(subset=['full_text'])

        df = df[['full_text', 'username', 'created_at', 'tweet_url']]
        
        # Preprocessing
        df['full_text'] = df['full_text'].apply(preprocess_text)

        # reset index dataframe
        df.reset_index(drop=True, inplace=True)

        # Mengubah format created_at menjadi datetime
        df['created_at'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S %z %Y').dt.strftime('%Y-%m-%d %H:%M:%S')

        # Insert data to database
        try:
            cur = mysql.connection.cursor()

            # Editor: Nabil (17/05/2024)
            # cur.execute("CREATE TABLE IF NOT EXISTS preprocess_guru (id INT PRIMARY KEY AUTO_INCREMENT, full_text TEXT, username TEXT, created_at TEXT, tweet_url TEXT)")
            cur.execute("CREATE TABLE IF NOT EXISTS preprocess_guru (id INT PRIMARY KEY AUTO_INCREMENT, full_text TEXT, username VARCHAR(255), created_at DATETIME , tweet_url VARCHAR(255))")

            mysql.connection.commit()

            for index, row in df.iterrows():
                cur.execute("INSERT INTO preprocess_guru (full_text, username, created_at, tweet_url) VALUES (%s, %s, %s, %s)", (row['full_text'], row['username'], row['created_at'], row['tweet_url']))
                mysql.connection.commit()
            cur.close()

            # Pesan berhasil preprocessing
            flash('File berhasil di preprocessing', 'success')
            return redirect(url_for('main.AllPreprocessing'))
        
        
        except Exception as e:
            print("Error:", str(e))
            flash('Terjadi kesalahan saat preprocessing', 'danger')
            return redirect(url_for('main.uploadPreprocessing'))

def preprocess_text(text):
    # Clear Twitter text
    text = clear_twitter_text(text)

    # Normalisasi
    text = normalisasi(text)

    # Stopword
    text = stopword(text)

    # Tokenized
    # tokens = tokenized(text)
    # text = " ".join(tokenized(text))
    text_cleaning = tokenized(text)

    # Stemming
    # text = stemming(tokens)
    # return text
    stemming_text = stemming(text_cleaning)
    return stemming_text

# Route Menampilkan hasil dari preprocessing
@main.route('/show-preprocessing', methods=['GET'])
def AllPreprocessing():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM preprocess_guru")
    data = cur.fetchall()
    cur.close()

    username = session['username']
    return render_template('preprocessing.html', data=data, current_url=request.path, username=username)

# Route menampilkan semua tweet
# @main.route('/all-tweet', methods=['GET'])
# def allTweet():
#     if 'username' not in session:
#         return redirect(url_for('auth.login'))
    
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM tweet_guru")
#     data = cur.fetchall()
#     cur.close()

#     username = session['username']
#     return render_template('tweetGuru.html', data=data, current_url=request.path, username=username)

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
# @main.route('/show-preprocessing', methods=['GET'])
# def AllPreprocessing():
#     if 'username' not in session:
#         return redirect(url_for('auth.login'))
    
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM preprocessing")
#     data = cur.fetchall()
#     cur.close()
#     username = session['username']
#     return render_template('preprocessing.html', data=data, current_url=request.path, username=username)

# Route membuat tabel data training
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

# Route data training menyimpan file CSV ke database
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

# Route training model
@main.route('/training-model', methods=['GET','POST'])
def trainModel():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM data_training")
    training_data = cur.fetchall()

    # Mengubah tuple menjadi dictionary
    column_names = [column[0] for column in cur.description]
    training_data = [dict(zip(column_names, row)) for row in training_data]

    # Mengambil full_text dan category dari data training 
    texts = [data['full_text'] for data in training_data]
    labels = [data['category'] for data in training_data]

    # Preprocessing data
    vectorizer = CountVectorizer()
    X_train = vectorizer.fit_transform(texts)
    encoder = LabelEncoder()
    y_train = encoder.fit_transform(labels)

    # Inisialisasi dan latih model
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Simpan model ke joblib
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    joblib.dump(encoder, 'encoder.pkl')

    username = session['username']

    cur.close()
    # return jsonify({'message': 'Model berhasil dilatih'})
    return render_template('train-test.html', current_url=request.path ,username=username)

# Route membuat tabel data testing
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

# Route data testing menyimpan file CSV ke database
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

# Route testing model
@main.route('/testing-model', methods=['GET','POST'])
def testingModel():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM data_testing")
    testing_data = cur.fetchall()

    # Mengubah tuple menjadi dictionary
    column_names = [column[0] for column in cur.description]
    testing_data = [dict(zip(column_names, row)) for row in testing_data]

    # Mengambil full_text dan category dari data training 
    texts = [data['full_text'] for data in testing_data]
    labels = [data['categories'] for data in testing_data]

    # Preprocessing data
    vectorizer = joblib.load('vectorizer.pkl')
    X_test = vectorizer.transform(texts)
    encoder = joblib.load('encoder.pkl')
    y_test = encoder.transform(labels)

    # testing model
    model = joblib.load('model.pkl')

    # Prediksi
    y_pred = model.predict(X_test)

    # Evaluasi model
    accuracy = accuracy_score(y_test, y_pred)

    cur.close()
    # return render_template('train-model.html', accuracy=accuracy)
    return jsonify({'accuracy': accuracy})


# Labeling menggunakan kamus
data = pd.read_csv('dataset/training_data_belum_dilabeling.csv')

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
    
@main.route('/kamus-training', methods=['GET', 'POST'])
def labeling_kamus():
    if request.method == 'POST':
        sentence = request.form['sentence']
        category = categorize_sentence(sentence)  # Call the function
        return render_template('kamus-training.html', sentence=sentence, category=category)
    else:
        return render_template('kamus-training.html')

