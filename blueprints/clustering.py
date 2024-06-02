from flask import Blueprint, render_template
import pandas as pd
import re
import numpy as np
import nltk # untuk melakukan proses preprocessing
import matplotlib.pyplot as plt
plt.switch_backend('agg') # untuk menghindari error ketika menjalankan di server tanpa GUI
from sklearn.feature_extraction.text import TfidfVectorizer # TfidfVectorizer digunakan untuk mengubah teks menjadi vektor
from sklearn.cluster import KMeans # KMeans digunakan untuk melakukan clustering
from sklearn.manifold import MDS # MDS untuk mengurangi dimensi data
from collections import Counter # collections digunakan untuk menghitung frekuensi kata

nltk.download('stopwords')

clustering = Blueprint('clustering', __name__)

# Fungsi untuk membaca dataset dari file CSV
def load_dataset(filename):
    df = pd.read_csv(filename)
    acc_names = df['username'].tolist()
    tweets = df['full_text'].tolist()
    return acc_names, tweets

# definisikan beberapa fungsi untuk kebutuhkan pre-processing, pre-processing yang dilakukan adalah
# A. lowercasing
# B. stopword removal
# C. stemming

stopwords = set(nltk.corpus.stopwords.words('indonesian'))

def preprocess(text):
    # tokenizing and lowercasing
    tokens = [word.lower() for word in text.split()]
    filtered_tokens = []
    # buat yang bukan terdiri dari alfabet, dan bukan stopword
    for token in tokens:
        if re.search('[a-zA-Z]', token) and (token not in stopwords):
            filtered_tokens.append(token)
    return " ".join(filtered_tokens)


# Fungsi untuk proses melakukan clustering
def perform_clustering():
    # memuat dataset
    acc_names, tweets = load_dataset("./dataset/gabungan_training.csv")

    # Preprocess tweets
    preprocessed_tweets = [preprocess(tweet) for tweet in tweets]

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(preprocessed_tweets)

    # Menggunakan KMeans untuk clustering
    num_topics = 4
    km = KMeans(n_clusters=num_topics)
    km.fit(X)
    clusters = km.labels_.tolist()

    # MDS untuk reduksi dimensi ke 2D
    mds = MDS(n_components=2)
    pos = mds.fit_transform(X.toarray())
    xs, ys = pos[:, 0], pos[:, 1]

    # Menghitung frekuensi kata untuk setiap cluster
    cluster_word_counts = [Counter() for _ in range(num_topics)]

    # Hitung frekuensi kata untuk setiap cluster-nya
    for i, cluster in enumerate(clusters):
        words = preprocessed_tweets[i].split()
        cluster_word_counts[cluster].update(words)

    # Buat plot clustering
    plt.figure(figsize=(15, 10))
    for x, y, username, cluster in zip(xs, ys, acc_names, clusters):
        # plt.text(x, y, username, fontsize=9)
        # plt.text(x, y, f'{username}\n{tweet}\n{cluster}', fontsize=9)
        plt.text(x, y, f'{username}', fontsize=9, ha='right', va='top', color='blue')

        # Tambahkan kata yang sering muncul pada pojok kanan atas
    for i, (cluster_word_count, cluster) in enumerate(zip(cluster_word_counts, clusters)):
        top_words = cluster_word_count.most_common(4)  # Ambil 10 kata teratas
        # top_words_text = '\n'.join([f'{word}: {count}' for word, count in top_words])
        top_word = top_words[0][0]
        plt.text(xs[i], ys[i], top_word, fontsize=9, ha='right', va='top', color='red')

    plt.scatter(xs, ys, c=clusters, cmap='viridis', alpha=0.6)
    plt.title('Clustering of Tweets')
    # plt.xlabel('MDS Component 1')
    # plt.ylabel('MDS Component 2')
    # plt.colorbar(label='Cluster')
    image_path = './static/images/clustering_guru.png'
    plt.savefig(image_path)
    plt.close()

    return image_path, clusters, tweets

# Fungsi untuk membuat plot distribusi kata-kata
def generate_word_distribution_plot(tweets, clusters, num_topics=4):
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(tweets)
    terms = vectorizer.get_feature_names_out()
    X = X.toarray()
    terms = np.array(terms)
    image_paths = []  # List untuk menyimpan path gambar

    for topic in range(num_topics):
        cluster_tweets = [tweets[i] for i in range(len(tweets)) if clusters[i] == topic]
        all_words = ' '.join(cluster_tweets).split()
        word_counts = Counter(all_words)
        common_words = word_counts.most_common(10)
        words, counts = zip(*common_words)

        plt.figure()
        plt.bar(words, counts)
        plt.xticks(rotation='vertical')
        plt.title(f'Word Distribution of Topic {topic}')
        image_path = f'./static/images/word_distribution_topic_{topic}.png'
        plt.savefig(image_path)
        plt.close()
        image_paths.append(image_path)  # Tambahkan path gambar ke list
    return image_paths

# Router untuk melakukan clustering menampilkan username dan tweet full_text
@clustering.route('/clustering', methods=['GET'])
def clustering_tweet():
    image_path, clusters, tweets = perform_clustering()
    image_paths = generate_word_distribution_plot(tweets, clusters)
    # world_distribution = [f'./static/images/word_distribution_topic_{topic}.png' for topic in range(4)]
    return render_template('klustering.html', image_path=image_path, world_distribution=image_paths)

# Router menampilkan kata-kata yang sering muncul
# @clustering.route('/word-distribution/<int:topic_no>', methods=['GET'])
# def word_distribution(topic_no):
#     image_path = generate_word_distribution_plot(topic_no)
#     return send_file(image_path, mimetype='image/png')

# @clustering.route('/clustering', methods=['GET'])
# def clustering_tweet():
#     # Kita load dokumen twitter, dan lakukan preprocessing terhadap tweet yang sudah di-load
#     acc_names, tweets = load_dataset("./dataset/gabungan_training.csv")

#     # Lakukan pre-process untuk setiap tweet pada koleksi "tweets" kita
#     # Gunakan List Comprehension untuk mempermudah hidup kita
#     preprocessed_tweets = [preprocess(tweet) for tweet in tweets]

#     # Buat TF-IDF Vectorizer
#     vectorizer = TfidfVectorizer(max_features=5000)
#     X = vectorizer.fit_transform(preprocessed_tweets)

#     # Lakukan k-means clustering
#     num_topics = 4
#     km = KMeans(n_clusters=num_topics)
#     km.fit(X)

#     # Lihat indeks cluster untuk setiap tweet/dokumen
#     clusters = km.labels_.tolist()

#     # plot hasil clustering
#     # reduksi dimensi dengan multidimensional scaling
#     mds = MDS(n_components=2)
#     pos = mds.fit_transform(X.toarray())  # shape (n_components, n_samples)

#     # ambil hasil reduksi ke 2D untuk posisi x dan y --> agar bisa di-plot di bidang kartesius
#     xs, ys = pos[:, 0], pos[:, 1]

#     # plot dokumen/tweet
#     plt.figure(figsize=(10, 8))
#     plt.scatter(xs, ys, c=clusters, cmap='viridis')
#     plt.title('Clustering of Tweets')
#     plt.xlabel('MDS Component 1')
#     plt.ylabel('MDS Component 2')
#     plt.colorbar(label='Cluster')

#     # Simpan gambar ke dalam file
#     plt.savefig('./static/images/clustering_guru.png')
#     plt.close()

#     # Kembalikan path gambar untuk ditampilkan di halaman web
#     image_path = './static/images/clustering_guru.png'
#     return render_template('klustering.html', image_path=image_path)
