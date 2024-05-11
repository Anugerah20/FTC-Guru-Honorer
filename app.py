from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for
from flask_cors import CORS
import pandas as pd
import os
from flask_mysqldb import MySQL
from sqlalchemy import create_engine

# import matplotlib.pyplot as plt

# from clear_twitter_text import clear_twitter_text
# from normalisasi import normalisasi
# from stopword import stopword
# from stemming import stemming

# from translate import convert_eng
# from labeling_text_blob import labeling_text
# from generate_wordcloud import generate_wordcloud
# from show_bar_chart import show_bar_chart

app = Flask(__name__)

# Koneksi ke database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'guru_honorer'

mysql = MySQL(app)

# Enable CORS
CORS(app, origins='*')

# Debug mode
app.config['DEBUG'] = True

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route utama
@app.route('/')
def index():
     return 'API Guru Honorer'

# Route untuk menyimpan data csv ke dalam database
@app.route('/save-csv-to-database')
def saveCSVToDatabase():
     df = pd.read_csv('data/guru_honorer.csv')

     # Membuat koneksi engine untuk Pandas to_sql
     engine = create_engine(f"mysql://{app.config['MYSQL_USER']}:{app.config['MYSQL_PASSWORD']}@{app.config['MYSQL_HOST']}/{app.config['MYSQL_DB']}")

     # Menyimpan DataFrame ke tabel MySQL
     df.to_sql('tweet_guru', con=engine, if_exists='replace', index=False)

     return 'File CSV berhasil disimpan ke database'

# Route untuk menampilkan semua data dari database
@app.route('/all-tweet', methods=['GET'])
def allTweet():
     cur = mysql.connection.cursor()
     # Tampilkan semua data
     cur.execute("SELECT * FROM tweet_guru")
     data = cur.fetchall()
     cur.close()

     return render_template('tweetGuru.html', data=data)

# Route Beranda
# @app.route('/')
# def home():
#      return render_template('home.html')

# @app.route('/',methods=['POST'])
# def uploadFiles():

#      uploaded_file = request.files['file']

#      if uploaded_file.filename != '':
#           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
#           uploaded_file.save(file_path)
#           parseCSV(file_path)

#           return redirect(url_for('home'))
     
# def parseCSV(file_path):
#      col_names = [
#      'conversation_id_str', 'created_at', 'favorite_count', 'full_text', 'id_str',
#      'image_url', 'in_reply_to_screen_name', 'lang', 'location', 'quote_count',
#      'reply_count', 'retweet_count', 'tweet_url', 'user_id_str', 'username'
#      ]

#      csvData = pd.read_csv(file_path,names=col_names,header=None)

#      for i,row in csvData.iterrows():
#           sql = """INSERT INTO tweet_guru (
#                          conversation_id_str, created_at, favorite_count, full_text, id_str,
#                          image_url, in_reply_to_screen_name, lang, location, quote_count,
#                          reply_count, retweet_count, tweet_url, user_id_str, username
#                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
#           value = (
#                row['conversation_id_str'], row['created_at'], row['favorite_count'], row['full_text'], row['id_str'],
#                row['image_url'], row['in_reply_to_screen_name'], row['lang'], row['location'], row['quote_count'],
#                row['reply_count'], row['retweet_count'], row['tweet_url'], row['user_id_str'], row['username']
#           )

#      mycursor.execute(sql,value)
#      mydb.commit()

# Route untuk menampilkan semua data dari database
# @app.route('/tweet-guru', methods=['GET'])
# def tweetGuru():
#           # Query untuk mendapatkan data dari database
#           mycursor.execute("SELECT * FROM tweet_guru")
#           data = mycursor.fetchall()

#           if data:
#                return render_template('tweetGuru.html', data=data)
#           else:
#                return jsonify({'message': 'Data tidak ditemukan'})

# Route untuk mendapatkan data dari file CSV
# @app.route('/data-guru-honorer', methods=['GET'])
# def dataGuruHonorer():
#      try:
#           # Memuat data dari file CSV
#           df = pd.read_csv('data/guru.csv')
          
#           # Mengonversi data ke format JSON
#           return df.to_json(orient='records')
     
#      except Exception as e:
#           return jsonify({'error': str(e)})
     
# Route memproses data yang dibersihkan
# @app.route('/preprocessing-data')
# def preprocessingData():
#           # Memuat data dari file CSV
#           df = pd.read_csv('data/guru.csv')

#           # Drop data duplikat dan data kosong
#           df = df.drop_duplicates(subset=['full_text'])
#           df = df.dropna(subset=['full_text'])

#           # Konversi teks menjadi lowercase
#           df['full_text'] = df['full_text'].str.lower()

#           # Bersihkan teks dari karakter-karakter yang tidak diperlukan
#           df['full_text'] = df['full_text'].apply(clear_twitter_text)

#           df['full_text'] = df['full_text'].apply(normalisasi)

#           # Proses Stopword
#           df['full_text'] = df['full_text'].apply(stopword)

#           # Proses tokenisasi
#           df['full_text'] = df['full_text'].apply(lambda x: x.split())

#           # Proses stemming
#           df['full_text'] = df['full_text'].apply(stemming)

#           # Mengonversi data ke format JSON
#           df.to_csv('data/preprocesingGuruHonorerBaru.csv', index=False)

# Route untuk Menampilkan preprocessing
# @app.route('/show-preprocessing-data', methods=['GET'])
# def showPreprocessingData():
#      try:
#           df = pd.read_csv('data/preprocesingGuruHonorer.csv')

#           return df.to_json(orient='records')
#      except Exception as e:
#           return jsonify({'error': str(e)})
     
# Route proses translate
# @app.route('/translate-guru-honorer')
# def translateGuruHonorer():
#      try:
#           # Memuat data dari file CSV
#           data = pd.read_csv('data/preprocesingGuruHonorerBaru.csv')

#           # Proses melakukan translate bahasa indonesia ke bahasa inggris
#           data['tweet_eng'] = data['full_text'].apply(convert_eng)
#           data.to_csv("data/translateGuruHonorer.csv", index=False)
          
#           return jsonify({'message': 'Data berhasil diterjemahkan'})
     
#      except Exception as e:
#           return jsonify({'error': str(e)})

# Route Labeling TextBlob
# @app.route('/labeling-textblob', methods=['GET'])
# def labelingTextBlob():
#      try:
#           hasil_analisis = labeling_text()

#           return jsonify(hasil_analisis)
     
#      except Exception as e:
#           return jsonify({'error': str(e)})
     
# Route untuk mendapatkan labeling TextBlob``
# @app.route('/data-textblob', methods=['GET'])
# def dataTextBlob():
#      # Membaca file dari file CSV
#      df = pd.read_csv('data/labelingTextBlob.csv')

#      # Konversi data ke format JSON
#      return df.to_json(orient='records')

# Route untuk proses wordcloud
# @app.route('/wordcloud', methods=['GET'])
# def worldcloud():
#      # Membaca data dari file CSV
#      generate_wordcloud('data/translateGuruHonorer.csv')

#      # Peletakan bar chart disimpan ke dalam folder static
#      return send_from_directory('static', 'wordcloud.png')

# Route untuk proses Bar Chart
# @app.route('/bar-chart')
# def bar_chart():
#      # Data bar chart guru honorer
#      labels = ['Setuju', 'Tidak Setuju', 'Netral']
#      total_setuju = 138
#      total_tidak_setuju = 138
#      total_netral = 229
#      counts = [total_setuju, total_tidak_setuju, total_netral]
#      title = 'Guru Honorer'

#      # Menampilkan bar chart
#      show_bar_chart(labels=labels, counts=counts, title=title)
#      # Peletaan bar chart disimpan ke dalam folder static
#      return send_from_directory('static', 'bar_chart.png')

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=True)