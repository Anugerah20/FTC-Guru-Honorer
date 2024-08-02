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

# Fungsi untuk menghubungkan ke database
def db_connect(host, user, password, database):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    return conn, cursor


# Fungsi untuk memanggil data dari tabel bersih
def fetch_data():
    conn, cursor = db_connect("localhost", "root", "", "guru_honorer")
    cursor.execute("SELECT full_text FROM bersih")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]


# Fungsi untuk menyimpan data ke tabel bersih
def save_text_to_db(texts):
    conn, cursor = db_connect("localhost", "root", "", "guru_honorer")
    cursor.executemany("INSERT INTO bersih (full_text) VALUES (%s)", [(text,) for text in texts])
    conn.commit()
    cursor.close()
    conn.close()


def extract_terms(documents):
    terms = set()
    for doc in documents:
        terms.update(doc.split())
    return sorted(terms)


def preprocess_documents(documents):
    return [set(doc.split()) for doc in documents]


def generate_candidates(itemset_number, last_frequent_itemsets):
    if itemset_number == 1:
        raise Exception(
            "This function should not be called for the first itemset generation.")
    else:
        temp_candidates = set()
        # Iterate over pairs of last frequent itemsets
        for i in range(len(last_frequent_itemsets)):
            for j in range(i + 1, len(last_frequent_itemsets)):
                # Turn tuples into sets for easy merging
                set1, set2 = set(last_frequent_itemsets[i]), set(
                    last_frequent_itemsets[j])
                # Merge sets only if they share exactly itemset_number - 2 common items
                if len(set1.intersection(set2)) == itemset_number - 2:
                    new_candidate = tuple(sorted(set1.union(set2)))
                    # Ensure new candidate has the correct number of items
                    if len(new_candidate) == itemset_number:
                        temp_candidates.add(new_candidate)
        return list(temp_candidates)


def calculate_frequent_itemsets(documents, candidates, min_sup):
    num_documents = len(documents)
    frequent_itemsets = []
    itemset_counts = [0] * len(candidates)
    itemset_documents = [set() for _ in range(len(candidates))]

    for i, candidate in enumerate(candidates):
        for doc_id, document in enumerate(documents):
            if set(candidate).issubset(document):
                itemset_counts[i] += 1
                itemset_documents[i].add(f"D{doc_id + 1}")

    return [(candidates[i], itemset_documents[i]) for i in range(len(candidates)) if itemset_counts[i] / num_documents >= min_sup]


def apriori(documents, min_sup):
    terms = extract_terms(documents)
    processed_docs = preprocess_documents(documents)
    all_frequent_itemsets = []  # List to store all frequent itemsets

    # Generate initial frequent itemsets directly from terms
    last_frequent_itemsets = calculate_frequent_itemsets(
        processed_docs, [tuple([term]) for term in terms], min_sup)

    # Store initial frequent itemsets
    all_frequent_itemsets.extend(last_frequent_itemsets)

    itemset_number = 1

    while True:
        itemset_number += 1
        candidates = generate_candidates(
            itemset_number, [itemset for itemset, _ in last_frequent_itemsets])

        last_frequent_itemsets = calculate_frequent_itemsets(
            processed_docs, candidates, min_sup)

        if not last_frequent_itemsets:
            break

        # Store all subsequent frequent itemsets
        all_frequent_itemsets.extend(last_frequent_itemsets)

        if itemset_number > 10:  # Safety check to prevent infinite loops
            break

    return all_frequent_itemsets


# Fungsi untuk menghitung klaster
def process_cluster(data):
    min_support = 0.4  # Ubah menjadi persentase 0.4 atau (40%)
    all_frequent_itemsets = apriori(data, min_support)

    clusters = defaultdict(set)
    terms_involved = set()

    for itemset, docs in all_frequent_itemsets:
        terms_involved.update(itemset)
        clusters[', '.join(itemset)] = docs

    # Fungsi untuk menghitung entropy overlap
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

    json_data = []
    # Variabel untuk iterasi klatser
    iteration = 1
    selected_cluster = None

    # Proses iterasi klaster untuk membentuk file JSON yang menyimpan hasil klaster terpilih
    for terms, docs in clusters.items():
        terms_list = terms.split(', ')
        entropy = calculate_entropy_overlap(docs)
        full_text = [data[int(doc[1:]) - 1] for doc in docs]

        # Melihat total documents dan full texts pada per iterasi klaster
        total_documents = len(docs)
        total_full_texts = len(full_text)

        cluster_info = {
            'Iteration': f'Iterasi ke-{iteration}',
            'Terms': terms_list,
            'Documents': list(docs),
            'Full_Text': full_text,
            'EO': entropy,
            'selected': False,  # Default to not selected
            'Total_Documents': total_documents,
            'Total_Full_Texts': total_full_texts
        }

        # Memilih klaster dengan nilai entropy terendah
        # Sebagai klaster terpilih
        if selected_cluster is None or entropy < selected_cluster['EO']:
            selected_cluster = cluster_info

        json_data.append(cluster_info)
        iteration += 1

    if selected_cluster:
        selected_cluster['selected'] = True

    return json_data, list(terms_involved), selected_cluster, total_documents, total_full_texts


# Pilih folder untuk menyimpan file upload
UPLOAD_FOLDER = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Hanya mengizinkan file csv
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


# Route klaster untuk proses upload file csv
@clustering.route('/ftc', methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(request.url)
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
            json_data, terms_involved, selected_cluster, total_documents, total_full_texts = process_cluster(data)

            with open(os.path.join(UPLOAD_FOLDER, 'ftc_cluster4.json'), 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

            save_text_to_db(data)

        username = session.get('username')
        return render_template(
            'upload.html',
            json_data=json_data,
            terms_involved=terms_involved,
            selected_cluster=selected_cluster,
            username=username,
            current_url=request.path,
            total_documents=total_documents,
            total_full_texts=total_full_texts
        )

    username = session.get('username')
    return render_template(
        'upload.html',
        json_data=None,
        terms_involved=None,
        selected_cluster=None,
        username=username,
        current_url=request.path,
        total_documents=0,
        total_full_texts=0
    )

# Route proses untuk menghapus file csv dan json
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

# Route buat hapus data json, csv, dan database
@clustering.route('/delete-clustering-ftc', methods=['GET', 'DELETE'])
def delete_cluster():
    try:
        conn, cursor = db_connect(host="localhost", user="root", password="", database="guru_honorer")

        cursor.execute("UPDATE bersih SET full_text = ''")
        conn.commit()

        cursor.execute("DELETE FROM bersih WHERE full_text = ''")
        conn.commit()

        csv_file_path = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/hasil_preprocesing_guru2.csv'
        delete_file(csv_file_path, 'File CSV')

        # json_file_path = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_clusterrr3.json'
        json_file_path = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_cluster4.json'
        delete_file(json_file_path, 'File JSON')

        flash('Data berhasil dihapus dari database', 'success')
        return redirect(url_for('clustering.upload_file'))

    except Exception as e:
        logging.error(f'Gagal menghapus data dan file JSON: {e}')
        flash(f'Gagal menghapus data dan file JSON', 'danger')
        return redirect(url_for('clustering.upload_file'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Route untuk menampilkan hasil klaster
@clustering.route('/ftc/results', methods=['GET'])
def show_results():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    file_path = os.path.join(UPLOAD_FOLDER, 'ftc_cluster4.json')
    if not os.path.exists(file_path):
        flash('Tidak ada hasil klaster yang tersedia.', 'danger')
        return redirect(url_for('clustering.upload_file'))

    with open(file_path, 'r') as json_file:
        json_data = json.load(json_file)

    username = session.get('username')
    return render_template(
        'upload.html',
        json_data=json_data,
        username=username,
        current_url=request.path
    )

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
    # filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_clusterrr3.json'
    filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_cluster4.json'
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