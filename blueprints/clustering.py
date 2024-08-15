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

# Route untuk menampilkan hasil klaster
@clustering.route('/ftc/results', methods=['GET'])
def show_results():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    file_path = os.path.join(UPLOAD_FOLDER, 'ftc_cluster.json')
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

    # EDITOR: NABIL 08/08/2024
    # total_documents = sum(len(cluster["Documents"]) for cluster in clustering_result)

    total_documents = sum(len(cluster["frequent_term_set"]) for cluster in clustering_result)

    max_labels = 0
    for cluster in clustering_result:

        # EDITOR: NABIL 08/08/2024
        # documents = cluster["Documents"]

        documents = cluster["frequent_term_set"]

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

    # EDITOR: NABIL 08/08/2024
    # filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc_cluster4.json'

    # EDITOR: NABIL 08/08/2024
    filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc.json'

    clustering_result, error_message = load_json_data(filepath)

    if clustering_result:
        purity = calculate_purity(clustering_result)

        # Menghitung metrik untuk setiap cluster
        # metrik adalah jumlah dokumen dalam cluster, jumlah label maksimum, dan proporsi label maksimum
        cluster_metrics = [] # simpan kedalam
        for cluster_id, cluster in enumerate(clustering_result):
            # cluster_size = len(cluster["Documents"])
            cluster_size = len(cluster["frequent_term_set"])
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


# START CODE PURITY
# def calculate_purity(clustering_result):
#     total_documents = 0
#     max_labels = 0

#     for cluster in clustering_result:
#         frequent_term_set = cluster["frequent_term_set"]

#         # Menghitung frekuensi kemunculan dokumen di setiap frequent term set
#         for term, (documents, _) in frequent_term_set.items():
#             total_documents += len(documents)

#             # Mengambil jumlah maksimum dari dokumen yang paling sering muncul
#             label_counts = Counter(documents)
#             max_label_count = max(label_counts.values())

#             # Menambahkan jumlah maksimum dokumen yang paling sering muncul
#             max_labels += max_label_count

#     # Menghitung purity
#     purity = max_labels / total_documents if total_documents > 0 else 0
#     return purity

# def get_lowest_candidates(clustering_result):
#     lowest_candidates = []

#     for iteration in clustering_result:
#         frequent_term_set = iteration["frequent_term_set"]

#         # Hitung jumlah candidate term
#         num_candidates = len(frequent_term_set)

#         # Simpan iterasi dan jumlah candidate
#         lowest_candidates.append({
#             "iteration": iteration.get("iteration", 0),  # Pastikan 'iteration' ada
#             "lowest_candidates": num_candidates
#         })

#     # Sort berdasarkan jumlah candidate terendah
#     lowest_candidates.sort(key=lambda x: x["lowest_candidates"])

#     return lowest_candidates


# @clustering.route('/purity')
# def index():
#     if 'username' not in session:
#         return redirect(url_for('auth.login'))

#     username = session['username']
#     filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc.json'

#     clustering_result, error_message = load_json_data(filepath)

#     if clustering_result:
#         # Dapatkan lowest_candidates
#         lowest_candidates = get_lowest_candidates(clustering_result)

#         if lowest_candidates:
#             # Ambil iterasi dengan lowest_candidates terendah
#             lowest_candidates_iter = lowest_candidates[0]["iteration"]

#             # Filter clustering_result untuk iterasi yang dipilih
#             filtered_clustering_result = next(
#                 (item for item in clustering_result if item["iteration"] == lowest_candidates_iter),
#                 None
#             )

#             if filtered_clustering_result:
#                 purity = calculate_purity([filtered_clustering_result])

#                 cluster_metrics = []
#                 frequent_term_set = filtered_clustering_result["frequent_term_set"]

#                 for term, (documents, _) in frequent_term_set.items():
#                     label_counts = Counter(documents)
#                     max_label_count = max(label_counts.values())
#                     cluster_size = len(documents)
#                     proportion = max_label_count / cluster_size

#                     cluster_metrics.append({
#                         'Cluster ID': filtered_clustering_result["iteration"],
#                         'Term': term,
#                         'Number of Tweets': cluster_size,
#                         'Maximum Number of Tweets': max_label_count,
#                         'Proportion': proportion
#                     })

#             else:
#                 purity = None
#                 cluster_metrics = []
#                 flash('Iterasi dengan lowest_candidates terendah tidak ditemukan atau file JSON tidak valid.', 'danger')

#         else:
#             purity = None
#             cluster_metrics = []
#             flash('Tidak ada data lowest_candidates tersedia.', 'danger')

#     else:
#         purity = None
#         cluster_metrics = []
#         flash('Proses pengujian belum dilakukan atau file JSON tidak ditemukan / kosong.', 'danger')

#     return render_template(
#         'purity.html',
#         clusters=[filtered_clustering_result] if filtered_clustering_result else [],
#         purity=purity,
#         cluster_metrics=cluster_metrics,
#         username=username,
#         current_url=request.path
#     )

# END CODE PURITY



# CODE PURITY NEW VERSION 1
# EDITOR: NABIL 13/08/2024
# Fungsi untuk menghitung purity
# def calculate_purity(clustering_result):
#     total_documents = 0
#     max_labels = 0

#     for cluster in clustering_result:
#         frequent_term_set = cluster["frequent_term_set"]

#         for term, (documents, _) in frequent_term_set.items():
#             # Menghitung frekuensi kemunculan dokumen di setiap frequent term set
#             total_documents += len(documents)

#             print(f'Term: {term}')

#             # Mengambil jumlah maksimum dari dokumen yang paling sering muncul
#             label_counts = Counter(documents)

#             print(f'Total Dokumen: {term}: {len(documents)}')

#             # Mengambil jumlah maksimum dari dokumen yang paling sering muncul
#             max_label_count = max(label_counts.values())
#             print(f'Jumlah Dokumen Terbanyak: {max_label_count}')
#             print(' ')

#             # Menambahkan jumlah maksimum dokumen yang paling sering muncul
#             max_labels += max_label_count

#     # Menghitung purity
#     purity = max_labels / total_documents
#     return purity

# # Route untuk halaman purity
# @clustering.route('/purity')
# def index():
#     if 'username' not in session:
#         return redirect(url_for('auth.login'))

#     username = session['username']
#     filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc.json'

#     clustering_result, error_message = load_json_data(filepath)

#     if clustering_result:
#         purity = calculate_purity(clustering_result)

#         cluster_metrics = []
#         for cluster_id, cluster in enumerate(clustering_result):
#             frequent_term_set = cluster["frequent_term_set"]

#             for term, (documents, _) in frequent_term_set.items():
#                 label_counts = Counter(documents)
#                 max_label_count = max(label_counts.values())
#                 cluster_size = len(documents)
#                 proportion = max_label_count / cluster_size

#                 cluster_metrics.append({
#                     'Cluster ID': cluster_id + 1,
#                     'Term': term,
#                     'Number of Tweets': cluster_size,
#                     'Maximum Number of Tweets': max_label_count,
#                     'Proportion': proportion
#                 })
#     else:
#         purity = None
#         cluster_metrics = []
#         flash('Proses pengujian belum dilakukan atau file JSON tidak ditemukan / kosong.', 'danger')

#     return render_template(
#         'purity.html',
#         clusters=clustering_result,
#         purity=purity,
#         cluster_metrics=cluster_metrics,
#         username=username,
#         current_url=request.path
#     )


# CODE PURITY NEW VERSION 2
# EDITOR: NABIL 13/08/2024
# Fungsi untuk menghitung purity dengan pendekatan frequent term set
# def load_json_data(filepath):
#     try:
#         with open(filepath, 'r') as file:
#             data = json.load(file)
#         return data, None
#     except Exception as e:
#         return None, str(e)

# def load_ground_truth(filepath):
#     try:
#         with open(filepath, 'r') as file:
#             ground_truth = json.load(file)
#         return ground_truth
#     except Exception as e:
#         print(f"Error loading ground truth: {e}")
#         return None

# def calculate_purity(clustering_result, ground_truth):
#     total_documents = 0
#     weighted_purity_sum = 0

#     for cluster_id, cluster in enumerate(clustering_result):
#         frequent_term_set = cluster["frequent_term_set"]

#         for term, (documents, _) in frequent_term_set.items():
#             total_documents += len(documents)
#             label_counts = Counter()

#             for doc_id in documents:
#                 true_label = ground_truth.get(doc_id)
#                 if true_label:
#                     label_counts[true_label] += 1

#             max_label_count = max(label_counts.values()) if label_counts else 0
#             cluster_size = len(documents)
#             proportion = max_label_count / cluster_size if cluster_size > 0 else 0
#             weighted_purity_sum += proportion * (cluster_size / total_documents)

#     purity = weighted_purity_sum
#     return purity

# @clustering.route('/purity')
# def index():
#     if 'username' not in session:
#         return redirect(url_for('auth.login'))

#     username = session['username']
#     clustering_filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ftc.json'
#     ground_truth_filepath = 'C:/Fullstack-guru-honorer/Backend-GuruHonorer/uploads/ground_truth.json'

#     clustering_result, error_message = load_json_data(clustering_filepath)
#     ground_truth = load_ground_truth(ground_truth_filepath)

#     if clustering_result and ground_truth:
#         purity = calculate_purity(clustering_result, ground_truth)
#         cluster_metrics = []

#         # Menampilkan satu term per klaster ketika ada lebih dari satu
#         for cluster_id, cluster in enumerate(clustering_result):
#             frequent_term_set = cluster["frequent_term_set"]
#             displayed_terms = set()

#             for term, (documents, _) in frequent_term_set.items():
#                 if term not in displayed_terms:
#                     displayed_terms.add(term)
#                     label_counts = Counter()

#                     for doc_id in documents:
#                         true_label = ground_truth.get(doc_id)
#                         if true_label:
#                             label_counts[true_label] += 1

#                     max_label_count = max(label_counts.values()) if label_counts else 0
#                     cluster_size = len(documents)
#                     proportion = max_label_count / cluster_size if cluster_size > 0 else 0

#                     cluster_metrics.append({
#                         'Cluster ID': cluster_id + 1,
#                         'Term': term,
#                         'Number of Tweets': cluster_size,
#                         'Maximum Number of Tweets': max_label_count,
#                         'Proportion': proportion
#                     })
#                     break  # Keluar dari loop setelah menambahkan satu perwakilan term

#     else:
#         purity = None
#         cluster_metrics = []
#         flash('Proses pengujian belum dilakukan atau file JSON tidak ditemukan / kosong.', 'danger')

#     return render_template(
#         'purity.html',
#         clusters=clustering_result,
#         purity=purity,
#         cluster_metrics=cluster_metrics,
#         username=username,
#         current_url=request.path
#     )