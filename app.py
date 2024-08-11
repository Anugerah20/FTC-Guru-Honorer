from flask import Flask
from config import Config
from extensions import mysql, cors, db
from blueprints.auth import auth
from blueprints.main import main
from blueprints.clustering import clustering

# TESTING
from flask import Flask, app, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
from ftc import ftc
import json
# END TESTING

import os
from flask_migrate import Migrate
from flask import Flask
from config import Config
from extensions import mysql, cors, db
from blueprints.auth import auth
from blueprints.main import main

app = Flask(__name__)

app.config.from_object(Config)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql.init_app(app)
cors.init_app(app)
db.init_app(app)

# Flask Migrate SQLAlchemy
migrate = Migrate(app, db, compare_type=True)

# daftar blueprint agar lebih mudah dibaca
app.register_blueprint(auth)
app.register_blueprint(main)
app.register_blueprint(clustering)

# Fungsi untuk mengonversi set menjadi list dan tuple keys menjadi string (jika diperlukan)
def convert_to_string(data):
    if isinstance(data, dict):
        return {str(k): convert_to_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_string(i) for i in data]
    elif isinstance(data, set):
        return list(data)
    elif isinstance(data, tuple):

        if len(data) == 1:
            return str(data[0])
        else:
            return tuple(convert_to_string(i) for i in data)

        # return ', '.join([str(i) for i in data])
    else:
        return data

'''

# FTC
@app.route('/cluster', methods=['GET', 'POST'])
def cluster_view():
    # Cek auth
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Default minimum support
    # Minimum support 0.4

    # min_support = 0.1
    # min_support = 0.2
    # min_support = 0.3
    # min_support = 0.4
    # min_support = 0.5

    if request.method == 'POST':

        # Mengambil nilai minimum support dari form
        min_support = float(request.form['min_support'])

        # Ambil file dari form
        file = request.files['file']
        if file:
            # Membaca file csv
            df = pd.read_csv(file)

            # Ambil data berisi full_text
            data = df['full_text'].tolist()
        else:
            return "No file uploaded", 400
    else:
        # Data default jika tidak ada file yang diupload
        data = [
            # "honorer jokowi sd tes",
            # "owi jokowi",
            # "guru honorer sd tes",
            # "honorer jokowi sd tes",
            # "guru gaji wowo",
            # "wowo gaji guru"
        ]

    username = session.get('username')

    # Run FTC
    iterations = ftc(data, min_support)

    # Konversi hasil FTC jika ada kunci yang menggunakan tuple menjadi string
    iterations = convert_to_string(iterations)


    # Simpan hasil FTC ke dalam file JSON
    result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'ftc.json')
    with open(result_filepath, 'w') as f:
        json.dump(iterations, f, indent=4)  # `indent=4` untuk membuat format JSON lebih terbaca

    print(" ")

    # print(iterations)
    print(f"Klaster yang dihasilkan: {iterations}")

    return render_template('ftc.html', iterations=iterations, username=username)
'''

@app.route('/cluster', methods=['GET', 'POST'])
def cluster_view():
    # Cek auth
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Mengambil nilai minimum support dari form
        min_support = float(request.form['min_support'])

        # Ambil file dari form
        file = request.files['file']
        if file:
            # Membaca file CSV
            df = pd.read_csv(file)

            # Ambil data berisi full_text
            data = df['full_text'].tolist()
        else:
            return "No file uploaded", 400

        # Jalankan FTC
        iterations = ftc(data, min_support)

        # Konversi hasil FTC jika ada kunci yang menggunakan tuple menjadi string
        iterations = convert_to_string(iterations)

        # Simpan hasil FTC ke dalam file JSON
        result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'ftc.json')
        with open(result_filepath, 'w') as f:
            json.dump(iterations, f, indent=4)

        print(f"Klaster yang dihasilkan: {iterations}")

        # Tampilkan hasil klasterisasi
        return render_template('ftc.html', iterations=iterations, username=session.get('username'))

    else:
        # Jika request adalah GET, tampilkan halaman upload
        return render_template('ftc.html')

# ! Tinggal menampilkan kandidat klaster yang nilai Entropy Overlap terkecil

# Route untuk menampilkan hasil cluster formatted json
@app.route('/view-cluster', methods=['GET'])
def view_cluster():
    # Cek auth
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    result_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'ftc.json')
    if os.path.exists(result_filepath):
        with open(result_filepath, 'r') as f:
            iterations = json.load(f)

        username = session.get('username')

        # Pass data to the template
        return render_template('view_cluster.html', iterations=iterations, username=username)
    else:
        return jsonify({"error": "No clustering results found"}), 404



if __name__ == '__main__':
     # Buat folder 'uploads' jika belum ada
     if not os.path.exists(app.config['UPLOAD_FOLDER']):
          os.makedirs(app.config['UPLOAD_FOLDER'])

     app.run(debug=True)
