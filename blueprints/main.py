# blueprints/main.py
from flask import Blueprint, flash, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from extensions import mysql, db
from flask import current_app as app
from dateutil import parser as date_parser
from datetime import datetime
from flask_paginate import Pagination, get_page_args

# Import fungsi preprocessing
from clear_twitter_text import clear_twitter_text
from normalisasi import normalisasi
from stopword import stopword
from tokenized import tokenized
from stemming import stemming

# Upload file
from werkzeug.utils import secure_filename
import os

main = Blueprint('main', __name__)

# Blueprint adalah memisahkan beberapa bagian seperti route dan fungsi
# main.route yang ada di def index merupakan route untuk menampilkan halaman utama
@main.route('/')
def index():
    # redirect itu akan kehalaman yang dituju
    # url_for akan membuat url showGuru dari main
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

# Route untuk menyimpan file csv yang telah di unggah
def save_uploaded_file(uploaded_file):
    file_path = None
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    except Exception as e:
        print("Error saving uploaded file:", str(e))
    return file_path

# Route buat memproses menyimpan file csv ke database kemudian menapilkan data
def parse_and_insert_csv(file_path):
    try:
        print("File CSV :", file_path)
        # Menampung column name yang akan ditampilkan
        col_names = [
            'conversation_id_str', 'created_at', 'favorite_count', 'full_text', 'id_str',
            'image_url', 'in_reply_to_screen_name', 'lang', 'location', 'quote_count',
            'reply_count', 'retweet_count', 'tweet_url', 'user_id_str', 'username'
        ]
        # Membaca file csv dan menghapus baris yang isinya kosong
        csvData = pd.read_csv(file_path, names=col_names, header=None)
        csvData.replace('nan', None, inplace=True)
        # csvData.dropna(inplace=True)

        # Koneksi ke database mysql
        cursor = mysql.connection.cursor()

        # Melakukan iterasi setiap bari pada csvData
        for _, row in csvData.iterrows():
            location = deleteNonAsciiCharacters(row['location'])
            row = row.fillna('')
            created_at = row['created_at']

            try:
                created_at_obj = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                # print("Tidak dapat mem-parse created_at:", created_at)
                continue

            # Cek apakah data sudah ada berdasarkan id_str
            # existing_guru = Guru.query.filter_by(id_str=row['id_str']).first()
            # if (existing_guru):
            #     continue

            # Perintah SQL untuk memasukkan data hasil dari upload file csv
            sql = """ INSERT INTO guru (conversation_id_str, created_at, favorite_count, full_text,
                id_str, image_url, in_reply_to_screen_name, lang, location, quote_count,
                reply_count, retweet_count, tweet_url, user_id_str, username)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

            values = (
                row['conversation_id_str'], created_at_obj, row['favorite_count'],
                row['full_text'], row['id_str'], row['image_url'],
                row['in_reply_to_screen_name'], row['lang'], location,
                row['quote_count'], row['reply_count'], row['retweet_count'],
                row['tweet_url'], row['user_id_str'], row['username']
            )

            # Menjalankan perintah sql, values
            cursor.execute(sql, values)
            mysql.connection.commit()

    except Exception as e:
        print("Error Mengambil data dan memasukkan file CSV ke database:", str(e))
    finally:
        cursor.close()

# Menghapus simbol-simbol, huruf yang ada di location
def deleteNonAsciiCharacters(text):
    if isinstance(text, float) and pd.isna(text):
        return
    else:
        return ''.join(char for char in text if ord(char) < 128)

# Route untuk menampilkan semua data yang ada di database
@main.route('/show-guru', methods=['GET'])
def showGuru():
    # Kondisi untuk mengecek user sudah login atau belum
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Mengatur nomor halaman pada pagination dan nilai defaultnya 1
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 20
    offset = (page - 1) * per_page

    # Melakukan debugging query mysql
    # Nabil (30/05/2024)
    # print(str(paginated_data.query.statement.compile(dialect=mysql.dialect())), flush=True)

    # Membuat koneksi ke database
    cursor = mysql.connection.cursor()

    # Mengambil semua data dari tabel guru
    cursor.execute("SELECT * FROM guru LIMIT %s OFFSET %s", (per_page, offset))

    # Mengambil semua hasil query
    data = cursor.fetchall()

    # Menghitung total data
    cursor.execute("SELECT COUNT(*) FROM guru")
    total_data = cursor.fetchone()[0]
    # total_data = len(data)

    # Mendapatkan username dari session
    username = session['username']

    # Menghitung jumlah halaman, jumlah data per halaman dan total halaman di pagination
    pagination = Pagination(page=page, per_page=per_page, total=total_data, css_framework='bootstrap5')

    cursor.close()

    return render_template(
        'tweetGuru.html',
        data=data,
        total_data=total_data,
        current_url=request.path,
        username=username,
        current_page=page,
        total_pages=pagination.total_pages,
        per_page=per_page,
        pagination=pagination,
    )

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
            return "Kolom 'full_text' tidak ditemukan pada file CSV", 400

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

        # Menyimpan data ke database tabel preprocess_guru
        try:
            for _, row in df.iterrows():
                cursor = mysql.connection.cursor()
                sql = """ INSERT INTO preprocess_guru (full_text, username, created_at, tweet_url)
                    VALUES (%s, %s, %s, %s) """
                values = (row['full_text'], row['username'], row['created_at'], row['tweet_url'])
                cursor.execute(sql, values)
                mysql.connection.commit()

            # Pesan berhasil preprocessing
            flash('File berhasil di preprocessing', 'success')
            return redirect(url_for('main.AllPreprocessing'))

        # Perintah untuk menampilkan pesan error pada saat melakukan preprocessing
        except Exception as e:
            print("Error:", str(e))
            flash('Terjadi kesalahan saat preprocessing', 'danger')
            return redirect(url_for('main.uploadPreprocessing'))

# Fungsi untuk melakukan preprocessing text
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
    # stemming_text = stemming(text)

    return stemming_text

# # Route Menampilkan hasil dari preprocessing
@main.route('/show-preprocessing', methods=['GET'])
def AllPreprocessing():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Membuat pagination
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 20
    offset = (page - 1) * per_page

    # Membuat koneksi ke database
    cursor = mysql.connection.cursor()

    # Mengambil semua data dari tabel guru
    cursor.execute("SELECT * FROM preprocess_guru LIMIT %s OFFSET %s", (per_page, offset))

    # Mengambil semua hasil query
    data = cursor.fetchall()

    # Menghitung total data
    cursor.execute("SELECT COUNT(*) FROM preprocess_guru")
    total_data = cursor.fetchone()[0]

    # Menghitung jumlah halaman, jumlah data per halaman dan total halaman di pagination
    pagination = Pagination(page=page, per_page=per_page, total=total_data, css_framework='bootstrap5')

    # Mendapatkan username dari session
    username = session['username']

    return render_template(
        'preprocessing.html',
        data=data,
        total_data=total_data,
        current_url=request.path,
        username=username,
        current_page=page,
        per_page=per_page,
        pagination=pagination,
        )