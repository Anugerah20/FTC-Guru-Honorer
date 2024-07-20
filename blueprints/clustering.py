'''
Metode Frequent Term
Based Clustering (FTC)
'''
import random
from itertools import combinations
from flask import Blueprint, render_template, redirect, session, request, url_for, flash, jsonify, url_for
import numpy as np
from math import log, sqrt
import math
import pandas as pd
from collections import Counter
import json
import os
import re
import mysql.connector
from werkzeug.utils import secure_filename
import logging # digunakan untuk debugging
from collections import defaultdict, Counter
import operator

clustering = Blueprint('clustering', __name__)

'''
FTC Frequent Term Based Clustering
TERBARU
'''
# Fungsi untuk koneksi ke tabel_bersih
def db_connect(host, user, password, database):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    return conn, cursor

# Fungsi untuk memanggil data dari bersih
def fetch_data():
    conn, cursor = db_connect("localhost", "root", "", "guru_honorer")
    cursor.execute("SELECT full_text FROM bersih")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]

# Fungsi untuk menyimpan data ke bersih
def save_text_to_db(texts):
    conn, cursor = db_connect("localhost", "root", "", "guru_honorer")
    cursor.executemany("INSERT INTO bersih (full_text) VALUES (%s)", [(text,) for text in texts])
    conn.commit()
    cursor.close()
    conn.close()

def process_cluster(data):
    # Langkah 2: Menggabungkan teks
    all_text = ' '.join(data)

    # Memproses teks dengan menghapus kata-kata yang tidak penting dan mengganti kata
    all_text = re.sub(r'\baja\b', 'saja', all_text)

    # Menghapus kata yang dan tidak
    all_text = re.sub(r'\b(?:yang|dan|tidak)\b', '', all_text)

    # Menghapus angka
    all_text = re.sub(r'\d+', '', all_text)


    # Langkah 3: Membagi teks menjadi kata-kata
    words = all_text.split()

    # Langkah 4: Menghitung frekuensi kemunculan kata
    word_counts = Counter(words)

    # Langkah 5: Menghitung probabilitas kemunculan kata
    total_words = sum(word_counts.values())
    word_probabilities = {word: count / total_words for word, count in word_counts.items()}

    # Langkah 6: Mengurutkan kata berdasarkan probabilitas dan memilih 10 kata teratas
    sorted_word_probabilities = dict(sorted(word_probabilities.items(), key=lambda item: item[1], reverse=True)[:10])

    # Langkah 7: Membuat klaster berdasarkan kombinasi term teratas dan kata tunggal
    clusters = defaultdict(set)
    top_terms = list(sorted_word_probabilities.keys())
    min_support = 4  # Memberikan minimum support 4

    for index, text in enumerate(data):
        words = text.split()
        doc_id = f'D{index+1}'

        # Tambahkan kata tunggal yang sering muncul
        for word in words:
            if word in top_terms and word:
                clusters[word].add(doc_id)

        # Tambahkan kombinasi dua term
        for term1, term2 in combinations(top_terms, 2):
            if term1 in words and term2 in words:
                clusters[f'{term1}, {term2}'].add(doc_id)

        # Tambahkan kombinasi tiga term
        for term1, term2, term3 in combinations(top_terms, 3):
            if term1 in words and term2 in words and term3 in words:
                clusters[f'{term1}, {term2}, {term3}'].add(doc_id)

    cluster_candidates = [(terms, list(docs)) for terms, docs in clusters.items() if len(docs) >= min_support]

    # Langkah 9: Menghitung nilai entropy overlap untuk setiap klaster
    def calculate_entropy_overlap(docs):
        term_count = Counter()
        total_terms = 0
        total_docs = len(docs)

        for doc in docs:
            text = data[int(doc[1:]) - 1]
            words = text.split()
            term_count.update(words)
            total_terms += len(words)

        entropy = 0
        for term, count in term_count.items():
            probability = count / total_terms
            entropy -= probability * math.log(probability, 2)

        return entropy / total_docs

    # Langkah 10: Menyiapkan data untuk disimpan ke JSON
    json_data = []
    terms_involved = set()

    for terms, docs in cluster_candidates:
        terms_list = terms.split(', ')
        terms_involved.update(terms_list)
        entropy = calculate_entropy_overlap(docs)

        # Menyiapkan dokumen yang terlibat
        documents_to_show = docs[:3]  # Menampilkan maksimal 3 dokumen

        full_text = [data[int(doc[1:]) - 1] for doc in documents_to_show]

        json_data.append({
            'Terms': terms_list,
            'Documents': documents_to_show,
            'Full_Text': full_text,
            'EO': entropy,
        })

    return json_data, terms_involved

# Testing clustering ftc
# data = [
#     "guru honorer rendahin banyak anak baca nulis ngitung kerja mulia kaya gitu bisa nya bina memang gaji guru honorer rendah salah guru salah sistemasi perintah aja kurang apresiasi guru honorer",
#     "kakak honorer semenjak lulus sarjana gaji guru kata cuma isi bensin",
#     "allah padahal banyak guru guru honorer lebih derita guru guru influencer anggar pakai naikin gaji guru honorer acara begini",
#     "semua guru asn semua guru gaji pokok layak tunjang banyak guru gaji bawah rupiah bulan sebut guru honorer",
#     "fakta banyak banget guru honorer sepuh tetep dapat gaji bawah umr padahal guru salah kerja puji coba guru apa dunia malah pandang rendah",
#     "memang rendah dulu sempat honorer ajar bahasa inggris smp jam ribu alhamdulillah bulan ribuan lebih banyak gaji dari ajar prima agama bulan juta sering gantiin guru tidak hadir",
#     "itu tuh emang fakta kirim mama guru honorer gaji bulan paling banyak juta",
#     "hidup bagi dunia mana pengiri memang fakta kaya gitu luar banyak guru honorer gaji kecil guru guru pelosok lebih banyak perlu hadap liat cuman orang untung naik pns"
# ]

# # Menampilkan hasil testing
# json_data, terms_involved = process_cluster(data)
# print(json_data)

# Letakkan file csv disini
UPLOAD_FOLDER = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads'
# Kondisi jika folder tidak ada, akan dibuat folder baru
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Fungsi meriksa hanya file csv yang boleh
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

@clustering.route('/ftc', methods=['GET', 'POST'])
#  Fungsi untuk import file csv
def upload_file():

    # Kondisi jika user belum login
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(show_results)
        file = request.files['file']
        if file.filename == '':
            flash('File belum dipilih', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            full_text = pd.read_csv(file_path)
            data = full_text['full_text'].tolist()
            json_data, terms_involved = process_cluster(data)

            # Simpan hasil klaster FTC ke file JSON
            with open(os.path.join(UPLOAD_FOLDER, 'ftc_clusterrr.json'), 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

            #  Simpan data ke database mysql
            save_text_to_db(data)

        username = session.get('username')
        return render_template(
                'upload.html',
                json_data=json_data,
                terms_involved=terms_involved,
                username=username,
                current_url=request.path,
                )

    username = session.get('username')
    return render_template(
        'upload.html',
        json_data=None,
        terms_involved=None,
        username=username,
        current_url=request.path,
        )

# Melihat hasil klastering FTC
@clustering.route('/ftc/results', methods=['GET'])
def show_results():

    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Menampilkan hasil klasterisasi dari file JSON yang telah disimpan
    with open(os.path.join(UPLOAD_FOLDER, 'ftc_clusterrr.json'), 'r') as json_file:
        json_data = json.load(json_file)
        # Menampilkan term
        terms_involved = set()
        for item in json_data:
            terms_involved.update(item['Terms'])

        # Menampilkan jumlah total klaster
        total_clusters = len(json_data)

        username = session['username']
    return render_template(
        'upload.html',
        json_data=json_data,
        terms_involved=terms_involved,
        total_clusters=total_clusters,
        username=username,
        current_url=request.path,
        )

# Membuat fungsi khusus untuk menghapus file csv dan json
def delete_file(file_path, file_type):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f'File {file_type} berhasil dihapus: {file_path}')
            flash(f'File {file_type} berhasil dihapus','success')
        else:
            logging.warning(f'File {file_type} tidak ditemukan: {file_path}')
            print(f'File {file_type} tidak ditemukan','warning')
    except Exception as e:
        logging.error(f'Gagal menghapus {file_type}: {file_path} - {e}')
        print(f'Gagal menghapus {file_type}','danger')

# Membuat route delete data clustering dari database mysql dan file csv serta json
@clustering.route('/delete-clustering-ftc', methods=['GET', 'DELETE'])
# Fungsi untuk menghapus data clustering ftc dari database mysql
def delete_cluster():
    try:
        conn, cursor = db_connect(host="localhost", user="root", password="", database="guru_honorer")

        cursor.execute("UPDATE bersih SET full_text = ''")
        conn.commit()

        # Hapus baris yang memiliki full_text kosong
        cursor.execute("DELETE FROM bersih WHERE full_text = ''")
        conn.commit()

        # Menghapus file CSV dengan memanggil fungsi delete_file
        csv_file_path = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/hasil_preprocesing_guru2.csv'
        delete_file(csv_file_path, 'File CSV')

        # Menghapus file JSON dengan memanggil fungsi delete_file
        json_file_path = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_clusterrr.json'
        delete_file(json_file_path, 'File JSON')

        cursor.close()
        conn.close()

        flash('Data berhasil dihapus dari database', 'success')
        return redirect(url_for('clustering.upload_file'))

    # Tampilkan pesan error jika database error
    except mysql.connector.Error as err:
        print(f'Database error: {err}')
        return redirect(url_for('clustering.upload_file'))

    # Tampilkan pesan error lainnya jika ada
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})


# Fungsi untuk memuat data JSON dari file
def load_json_data(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file) # berfungsi untuk membaca file JSON
        if not data:  # Cek jika file JSON kosong
            return None, 'File JSON kosong'
        return data, None
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None, str(e)

# Fungsi untuk menghitung purity
def calculate_purity(clustering_result):
    total_documents = sum(len(cluster["Documents"]) for cluster in clustering_result)
    max_labels = 0
    for cluster in clustering_result:
        documents = cluster["Documents"]
        label_count = len(documents)  # Semua dokumen dianggap satu kelas
        max_labels += label_count
    purity = max_labels / total_documents
    return purity

# Route untuk halaman purity
@clustering.route('/purity')
def index():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    username = session['username']
    filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_clusterrr.json'
    clustering_result, error_message = load_json_data(filepath)

    if clustering_result:
        purity = calculate_purity(clustering_result)

        # Menghitung metrik untuk setiap cluster
        # metrik adalah jumlah dokumen dalam cluster, jumlah label maksimum, dan proporsi label maksimum
        cluster_metrics = [] # simpan kedalam
        for cluster_id, cluster in enumerate(clustering_result):
            cluster_size = len(cluster["Documents"])
            label_count = cluster_size  # Semua dokumen dianggap satu kelas
            proportion = label_count / cluster_size
            # cluster_metrics.append berfungsi untuk menambahkan data ke dalam list
            cluster_metrics.append({
                'Cluster ID': cluster_id + 1,
                'Number of Tweets': cluster_size,
                'Maximum Number of Tweets': label_count,
                'Proportion': proportion
            })

    else:
        purity = None
        cluster_metrics = []
        flash('Proses pengujian belum dilakukan atau file JSON tidak ditemukan / kosong.', 'danger')

    return render_template(
        'purity.html',
        clusters=clustering_result,
        purity=purity,
        cluster_metrics=cluster_metrics,
        username=username,
        current_url=request.path
        )