import itertools
import time
from collections import defaultdict
from collections import Counter
from math import log, sqrt
from flask import Blueprint, render_template, redirect, session, request, url_for, flash, jsonify, url_for
import numpy as np
import pandas as pd
import json
import os
import mysql.connector
from werkzeug.utils import secure_filename
import logging

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

# Fungsi untuk ekstraksi terms
def extract_terms(documents):
    terms = set()
    for doc in documents:
        terms.update(doc.split())
    return sorted(terms)

# Preprocessing dokumen
def preprocess_documents(documents):
    return [set(doc.split()) for doc in documents]

# Menghasilkan kandidat itemset
def generate_candidates(itemset_number, last_frequent_itemsets):
    if itemset_number == 1:
        raise Exception("This function should not be called for the first itemset generation.")
    else:
        temp_candidates = set()
        for i in range(len(last_frequent_itemsets)):
            for j in range(i + 1, len(last_frequent_itemsets)):
                set1, set2 = set(last_frequent_itemsets[i]), set(last_frequent_itemsets[j])
                if len(set1.intersection(set2)) == itemset_number - 2:
                    new_candidate = tuple(sorted(set1.union(set2)))
                    if len(new_candidate) == itemset_number:
                        temp_candidates.add(new_candidate)
        return list(temp_candidates)

# Menghitung itemset frekuensi
def calculate_frequent_itemsets(documents, candidates, min_sup):
    num_documents = len(documents)
    frequent_itemsets = []
    itemset_counts = [0] * len(candidates)
    itemset_documents = [set() for _ in range(len(candidates))]

    for i, candidate in enumerate(candidates):
        for doc_id, document in enumerate(documents):
            if set(candidate).issubset(document):
                itemset_counts[i] += 1
                itemset_documents[i].add(f"D{doc_id+1}")

    return [(candidates[i], itemset_documents[i]) for i in range(len(candidates)) if itemset_counts[i] / num_documents >= min_sup]

# Menghasilkan frequent term set
def generate_frequent_term_set(documents, min_sup):
    terms = extract_terms(documents)
    processed_docs = preprocess_documents(documents)
    all_frequent_itemsets = []

    last_frequent_itemsets = calculate_frequent_itemsets(processed_docs, [tuple([term]) for term in terms], min_sup)
    all_frequent_itemsets.extend(last_frequent_itemsets)

    itemset_number = 1
    while True:
        itemset_number += 1
        candidates = generate_candidates(itemset_number, [itemset for itemset, _ in last_frequent_itemsets])
        last_frequent_itemsets = calculate_frequent_itemsets(processed_docs, candidates, min_sup)

        if not last_frequent_itemsets:
            break

        all_frequent_itemsets.extend(last_frequent_itemsets)
        if itemset_number > 10:  # Safety check to prevent infinite loops
            break

    return {tuple(itemset): docs for itemset, docs in all_frequent_itemsets}

# Menghitung entropy overlap
def calculate_entropy_overlap(frequent_term_set, data):
    entropy_overlap_results = {}
    for term_set, documents in frequent_term_set.items():
        entropy_overlap_sum = 0
        for document in documents:
            frequency = sum(document in documents for documents in frequent_term_set.values())
            entropy_overlap = (-1/frequency) * log(1/frequency)
            entropy_overlap_sum += entropy_overlap

        entropy_overlap_results[term_set] = entropy_overlap_sum / len(documents)
    return entropy_overlap_results

# Proses klasterisasi FTC
def process_cluster(data):
    min_support = 0.4
    frequent_term_set = generate_frequent_term_set(data, min_support)
    entropy_overlap_results = calculate_entropy_overlap(frequent_term_set, data)

    json_data = []
    iteration = 1
    selected_cluster = None

    for term_set, docs in frequent_term_set.items():
        full_text = [data[int(doc[1:]) - 1] for doc in docs]
        entropy = entropy_overlap_results[term_set]

        cluster_info = {
            'Cluster_Number': f'Cluster {iteration}',
            'Terms': list(term_set),
            'Documents': list(docs),
            'Full_Text': full_text,
            'EO': entropy,
            'selected': False
        }

        if selected_cluster is None or entropy < selected_cluster['EO']:
            selected_cluster = cluster_info

        json_data.append({
            'Iteration': iteration,
            'Clusters': [cluster_info]
        })

        iteration += 1

    if selected_cluster:
        selected_cluster['selected'] = True

    return json_data, selected_cluster

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
            json_data, selected_cluster = process_cluster(data)

            with open(os.path.join(UPLOAD_FOLDER, 'ftc_cluster.json'), 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

            save_text_to_db(data)

        username = session.get('username')
        return render_template(
            'upload.html',
            json_data=json_data,
            selected_cluster=selected_cluster,
            username=username,
            current_url=request.path
        )

    username = session.get('username')
    return render_template(
        'upload.html',
        json_data=None,
        selected_cluster=None,
        username=username,
        current_url=request.path
    )

# Route proses untuk menghapus file csv dan json
def delete_file(file_path, file_type):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f'File {file_type} berhasil dihapus: {file_path}')
            flash(f'File {file_type} berhasil dihapus', 'success')
        else:
            logging.warning(f'File {file_type} tidak ditemukan: {file_path}')
            flash(f'File {file_type} tidak ditemukan', 'warning')
    except Exception as e:
        logging.error(f'Gagal menghapus {file_type}: {file_path} - {e}')
        flash(f'Gagal menghapus {file_type}', 'danger')

# Route untuk menghapus data json, csv, dan database
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

        json_file_path = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_cluster.json'
        delete_file(json_file_path, 'File JSON')

        flash('Data berhasil dihapus dari database', 'success')
        return redirect(url_for('clustering.upload_file'))

    except Exception as e:
        logging.error(f'Gagal menghapus data dari database: {e}')
        flash('Gagal menghapus data dari database', 'danger')
        return redirect(url_for('clustering.upload_file'))

    finally:
        cursor.close()
        conn.close()

# PURITY TERBARU
def calculate_purity(cluster_data):
    # Total tweets
    total_tweets = sum(cluster['total_tweets'] for cluster in cluster_data)

    # List untuk menyimpan data purity
    purity_data = []
    total_purity_numerator = 0

    # Menghitung total purity
    for cluster in cluster_data:
        n_i = cluster['total_tweets']
        max_tweets = cluster['max_tweets']
        total_purity_numerator += max_tweets

        purity_data.append({
            'Cluster_id': cluster['cluster_id'],
            'Jumlah tweet Setiap klaster': n_i,
            'Jumlah tweet Maksimum di setiap klaster': max_tweets
        })

    # Menghitung total purity
    total_purity = total_purity_numerator / total_tweets

    # Menambahkan baris total
    total_row = {
        'Cluster_id': 'Total keseluruhan tweet',
        'Jumlah tweet Setiap klaster': total_tweets,
        'Jumlah tweet Maksimum di setiap klaster': ''
    }

    total_purity_row = {
        'Cluster_id': 'Total Purity',
        'Jumlah tweet Setiap klaster': '',
        'Jumlah tweet Maksimum di setiap klaster': f"{total_purity:.4f}"
    }

    # Membuat DataFrame dan menambahkan baris total
    df = pd.DataFrame(purity_data)
    df_total = pd.DataFrame([total_row, total_purity_row])
    df = pd.concat([df, df_total], ignore_index=True)

    return df, total_purity

@clustering.route('/purity')
def index():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Data input: list of clusters with 'total_tweets' and 'max_tweets'
    cluster_data = [
        {'cluster_id': 1, 'total_tweets': 419, 'max_tweets': 262},
        {'cluster_id': 2, 'total_tweets': 8, 'max_tweets': 3},
        {'cluster_id': 3, 'total_tweets': 1, 'max_tweets': 1},
        {'cluster_id': 4, 'total_tweets': 2, 'max_tweets': 2},
    ]

    # Calculate purity and get DataFrame
    df, total_purity = calculate_purity(cluster_data)

    # username
    username = session.get('username')

    # Convert DataFrame to HTML
    table_html = df.to_html(index=False, classes='table table-striped')

    return render_template('purity.html', table_html=table_html, total_purity=total_purity, username=username)