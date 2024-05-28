from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import DataTraining, DataTesting
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np

labeling = Blueprint('labeling', __name__)
app = None

# Fungsi membaca file kamus
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]

# Inisiasi kamus positif dan negatif
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
kamus_positif_path = os.path.join(root_dir, 'dataset', 'kamus_positif.txt')
kamus_negatif_path = os.path.join(root_dir, 'dataset', 'kamus_negatif.txt')

# print(f"Loading positive words from: {kamus_positif_path}")
# print(f"Loading negative words from: {kamus_negatif_path}")

kalimat_positif = read_file(kamus_positif_path)
kalimat_negatif = read_file(kamus_negatif_path)

# Fungsi untuk melakukan labeling berdasarkan kamus
def labeling_manual(full_text):
    count_positif = sum(full_text.lower().count(kalimat) for kalimat in kalimat_positif)
    count_negatif = sum(full_text.lower().count(kalimat) for kalimat in kalimat_negatif)

    if count_positif > count_negatif:
        return 'positif'
    elif count_negatif > count_positif:
        return 'negatif'
    else:
        return 'netral'

# Route Data Training and process category
@labeling.route('/train-label', methods=['GET', 'POST'])
def training_labeling():
    if request.method == 'POST':
        file = request.files['csvFile']

        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(root_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            print(f"File saved to: {file_path}")

            try:
                df = pd.read_csv(file_path)
                print(f"DataFrame loaded with columns: {df.columns}")
            except Exception as e:
                flash(f"Error reading CSV file: {e}", 'danger')
                return redirect(request.url)

            if 'full_text' not in df.columns:
                flash('Kolom full_text tidak ditemukan', 'danger')
                return redirect(request.url)

            labeled_data = []
            for _, row in df.iterrows():
                text = row['full_text']
                label = labeling_manual(text)
                labeled_data.append({
                    'full_text': text,
                    'category': label
                })

                labeled_text = DataTraining(full_text=text, category=label)
                db.session.add(labeled_text)
            db.session.commit()

            flash('Data berhasil disimpan', 'success')
            # Ambil data dari database saat redirect
            # labeled_texts = DataTraining.query.all()
            # labeled_data = [{'full_text': text.full_text, 'category': text.category} for text in labeled_texts]
            return redirect(url_for('labeling.get_data_training'))
            # return render_template('data-training.html', labeled_data=labeled_data)
        else:
            flash('File tidak valid', 'danger')
            return redirect(request.url)

    # Ambil data dari database saat metode adalah GET
    labeled_texts = DataTraining.query.all()
    labeled_data = [{'full_text': text.full_text, 'category': text.category} for text in labeled_texts]
    return render_template('data-training.html', labeled_data=labeled_data)

# Route Data Training get all data
@labeling.route('/show-data-training', methods=['GET'])
def get_data_training():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Membuat pagination untuk data training
    page = request.args.get('page', 1, type=int)
    per_page = 20
    labeled_texts = DataTraining.query.paginate(page=page, per_page=per_page)

    # Hitung total positif, negatif, dan netral
    total_positif = DataTraining.query.filter_by(category='positif').count()
    total_negatif = DataTraining.query.filter_by(category='negatif').count()
    total_netral = DataTraining.query.filter_by(category='netral').count()

    result = []
    for text in labeled_texts:
        result.append({'full_text': text.full_text, 'category': text.category})

    total_pages = labeled_texts.pages
    current_page = labeled_texts.page

    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2) + 1
    pagination_range = range(start_page, end_page)

    # Menghitung Total Data
    total_data = DataTraining.query.count()
    username = session['username']

    return render_template(
        'data-training.html',
        labeled_data=result,
        current_url=request.path,
        username=username,
        current_page=current_page,
        total_pages=total_pages,
        pagination_range=pagination_range,
        total_positif=total_positif,
        total_negatif=total_negatif,
        total_netral=total_netral,
        total_data=total_data
    )

# Process Testing Data
# Load training data
training_data = pd.read_csv('dataset/data_training_guru_honorer.csv')

# Calculate total words in each category
word_counts = training_data.groupby('category')['full_text'].apply(lambda x: ' '.join(x).lower().split()).apply(pd.Series).stack().value_counts()

# Calculate total words in training data
total_words = word_counts.sum()

# Calculate probabilities for each word in each category
probabilities = {}
for category in training_data['category'].unique():
    category_data = training_data[training_data['category'] == category]
    word_counts_category = category_data['full_text'].apply(lambda x: x.lower().split()).apply(pd.Series).stack().value_counts()
    probabilities[category] = (word_counts_category + 1) / (len(word_counts) + total_words)

# Calculate prior probabilities for each category
prior_probabilities = training_data['category'].value_counts(normalize=True)

# Function to classify a document
def classify_document(document):
    document_words = document.lower().split()
    scores = {}
    for category in training_data['category'].unique():
        score = np.log(prior_probabilities[category])
        for word in document_words:
            if word in probabilities[category]:
                score += np.log(probabilities[category][word])
            else:
                score += np.log(1 / (len(word_counts) + total_words))
        scores[category] = score
    return max(scores, key=scores.get)

@labeling.route('/test-label', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join(root_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

        # Process testing data and add labels
        testing_data = pd.read_csv(file_path)
        if 'full_text' not in testing_data.columns:
            flash('CSV file does not contain "full_text" column.', 'error')
            return redirect(request.url)

        labeled_data = []
        for _, row in testing_data.iterrows():
            text = row['full_text']
            label = classify_document(text)
            labeled_data.append({
                'full_text': text,
                'categories': label
            })
            # Simpan data testing ke database
            labeled_text = DataTesting(full_text=text, categories=label)
            db.session.add(labeled_text)
        db.session.commit()
        flash('Data berhasil disimpan', 'success')

        # Ambil data dari database saat metode adalah GET
        labeled_texts = DataTesting.query.all()
        labeled_data = [{'full_text': text.full_text, 'categories': text.categories} for text in labeled_texts]

        # Render HTML with classification results
        return render_template('data-testing.html', labeled_data=labeled_data)
        # return redirect(url_for('labeling.get_data_testing'))

    return render_template('data-testing.html')

# Route Data Testing get all data
@labeling.route('/show-data-testing', methods=['GET'])
def get_data_testing():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    # Membuat pagination untuk data testing
    page = request.args.get('page', 1, type=int)
    per_page = 20
    labeled_texts = DataTesting.query.paginate(page=page, per_page=per_page)

    # Hitung total positif, negatif, dan netral
    total_positif = DataTesting.query.filter_by(categories='positif').count()
    total_negatif = DataTesting.query.filter_by(categories='negatif').count()
    total_netral = DataTesting.query.filter_by(categories='netral').count()

    result = []
    for text in labeled_texts:
        result.append({'full_text': text.full_text, 'categories': text.categories})

    total_pages = labeled_texts.pages
    current_page = labeled_texts.page

    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2) + 1
    pagination_range = range(start_page, end_page)

    # Menghitung Total Data
    total_data = DataTesting.query.count()
    username = session['username']

    return render_template(
        'data-testing.html',
        labeled_data=result,
        current_url=request.path,
        username=username,
        current_page=current_page,
        total_pages=total_pages,
        pagination_range=pagination_range,
        total_positif=total_positif,
        total_negatif=total_negatif,
        total_netral=total_netral,
        total_data=total_data
    )

    # labeled_texts = DataTesting.query.all()
    # result = []
    # for text in labeled_texts:
    #     result.append({'full_text': text.full_text, 'categories': text.categories})
    #     username = session['username']
    # return render_template('data-testing.html', labeled_data=result, current_url=request.path, username=username)