# KODINGAN LAMA
# EDITOR: Nabil 02/06/2024
# from flask import Blueprint, render_template
# import pandas as pd
# import re
# import numpy as np
# import nltk # untuk melakukan proses preprocessing
# import matplotlib.pyplot as plt
# plt.switch_backend('agg') # untuk menghindari error ketika menjalankan di server tanpa GUI
# from sklearn.feature_extraction.text import TfidfVectorizer # TfidfVectorizer digunakan untuk mengubah teks menjadi vektor
# from sklearn.cluster import KMeans # KMeans digunakan untuk melakukan clustering
# from sklearn.manifold import MDS # MDS untuk mengurangi dimensi data
# from collections import Counter # collections digunakan untuk menghitung frekuensi kata

# nltk.download('stopwords')

# clustering = Blueprint('clustering', __name__)

# # Fungsi untuk membaca dataset dari file CSV
# def load_dataset(filename):
#     df = pd.read_csv(filename)
#     acc_names = df['username'].tolist()
#     tweets = df['full_text'].tolist()
#     return acc_names, tweets

# # definisikan beberapa fungsi untuk kebutuhkan pre-processing, pre-processing yang dilakukan adalah
# # A. lowercasing
# # B. stopword removal
# # C. stemming

# stopwords = set(nltk.corpus.stopwords.words('indonesian'))

# def preprocess(text):
#     # tokenizing and lowercasing
#     tokens = [word.lower() for word in text.split()]
#     filtered_tokens = []
#     # buat yang bukan terdiri dari alfabet, dan bukan stopword
#     for token in tokens:
#         if re.search('[a-zA-Z]', token) and (token not in stopwords):
#             filtered_tokens.append(token)
#     return " ".join(filtered_tokens)


# # Fungsi untuk proses melakukan clustering
# def perform_clustering():
#     # memuat dataset
#     acc_names, tweets = load_dataset("./dataset/gabungan_training.csv")

#     # Preprocess tweets
#     preprocessed_tweets = [preprocess(tweet) for tweet in tweets]

#     # TF-IDF Vectorizer
#     vectorizer = TfidfVectorizer(max_features=5000)
#     X = vectorizer.fit_transform(preprocessed_tweets)

#     # Menggunakan KMeans untuk clustering
#     num_topics = 4
#     km = KMeans(n_clusters=num_topics)
#     km.fit(X)
#     clusters = km.labels_.tolist()

#     # MDS untuk reduksi dimensi ke 2D
#     mds = MDS(n_components=2)
#     pos = mds.fit_transform(X.toarray())
#     xs, ys = pos[:, 0], pos[:, 1]

#     # Menghitung frekuensi kata untuk setiap cluster
#     cluster_word_counts = [Counter() for _ in range(num_topics)]

#     # Hitung frekuensi kata untuk setiap cluster-nya
#     for i, cluster in enumerate(clusters):
#         words = preprocessed_tweets[i].split()
#         cluster_word_counts[cluster].update(words)

#     # Buat plot clustering
#     plt.figure(figsize=(10, 10))
#     for x, y, username, cluster in zip(xs, ys, acc_names, clusters):
#         # plt.text(x, y, username, fontsize=9)
#         # plt.text(x, y, f'{username}\n{tweet}\n{cluster}', fontsize=9)
#         plt.text(x, y, f'{username}', fontsize=9, ha='right', va='top', color='blue')

#         # Tambahkan kata yang sering muncul pada pojok kanan atas
#     for i, (cluster_word_count, cluster) in enumerate(zip(cluster_word_counts, clusters)):
#         top_words = cluster_word_count.most_common(4)  # Ambil 10 kata teratas
#         # top_words_text = '\n'.join([f'{word}: {count}' for word, count in top_words])
#         top_word = top_words[0][0]
#         plt.text(xs[i], ys[i], top_word, fontsize=9, ha='right', va='top', color='red')

#     plt.scatter(xs, ys, c=clusters, cmap='viridis', alpha=0.6)
#     plt.title('Clustering of Tweets')
#     image_path = './static/images/clustering_guru.png'
#     plt.savefig(image_path)
#     plt.close()

#     return image_path, clusters, tweets

# # Fungsi untuk membuat plot distribusi kata-kata
# def generate_word_distribution_plot(tweets, clusters, num_topics=4):
#     vectorizer = TfidfVectorizer(max_features=5000)
#     X = vectorizer.fit_transform(tweets)
#     terms = vectorizer.get_feature_names_out()
#     X = X.toarray()
#     terms = np.array(terms)
#     image_paths = []  # List untuk menyimpan path gambar

#     for topic in range(num_topics):
#         cluster_tweets = [tweets[i] for i in range(len(tweets)) if clusters[i] == topic]
#         all_words = ' '.join(cluster_tweets).split()
#         word_counts = Counter(all_words)
#         common_words = word_counts.most_common(10)
#         words, counts = zip(*common_words)

#         plt.figure()
#         plt.bar(words, counts)
#         plt.xticks(rotation='vertical')
#         plt.title(f'Word Distribution of Topic {topic}')
#         image_path = f'./static/images/word_distribution_topic_{topic}.png'
#         plt.savefig(image_path)
#         plt.close()
#         image_paths.append(image_path)  # Tambahkan path gambar ke list
#     return image_paths

# # Router untuk melakukan clustering menampilkan username dan tweet full_text
# @clustering.route('/clustering', methods=['GET'])
# def clustering_tweet():
#     image_path, clusters, tweets = perform_clustering()
#     image_paths = generate_word_distribution_plot(tweets, clusters)
#     return render_template('klustering.html', image_path=image_path, world_distribution=image_paths)


from flask import Blueprint, render_template, redirect, session, request, url_for
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
import os # Untuk membuat folder dan menyimpan gambar
from sklearn.metrics import silhouette_score, davies_bouldin_score # Menggunakan silhouette score dan davies bouldin score untuk evaluasi clustering

nltk.download('stopwords')

clustering = Blueprint('clustering', __name__)

# Fungsi untuk membaca dataset dari file CSV
# List acc_names berisikan username kemudian list tweets berisikan full_text
def read_dataset(filename):
    df = pd.read_csv(filename)
    acc_names = df['username'].tolist()
    tweets = df['full_text'].tolist()
    return acc_names, tweets

# Menggunakan beberapa fungsi untuk kebutuhkan pre-processing, ini tahapan pre-processing sebagai berikut:
# A. lowercasing
# B. stopword removal
# C. stemming

# corpus yang digunakan adalah corpus bahasa indonesia
stopwords = set(nltk.corpus.stopwords.words('indonesian'))

# Fungsi ini digunakan melakukan pre-processing pada teks
def preprocess(text):
    # tokenizing and lowercasing
    tokens = [word.lower() for word in text.split()]
    filtered_tokens = []
    # buat yang bukan terdiri dari alfabet, dan bukan stopword
    for token in tokens:
        if re.search('[a-zA-Z]', token) and (token not in stopwords):
            filtered_tokens.append(token)
    return " ".join(filtered_tokens)

# Fungsi untuk membuat plot clustering dokumen
# Menggunakan MDS untuk mereduksi dimensi ke 2D
# Kemudian plot dengan matplotlib unutk menampilkan cluster yang bersisikan username dan label cluster
def plot_doc_cluster(xs, ys, clusters, acc_names, cluster_names):
    cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e'}
    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, acc_names=acc_names))
    groups = df.groupby('label')
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.margins(0.05)

    # Proses perulangan cluster
    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=12, label=cluster_names[name], color=cluster_colors[name], mec='none')
        ax.set_aspect('auto')
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax.tick_params(axis='y', which='both', left=False, top=False, labelleft=False)

    ax.legend(numpoints=1)

    # Perulangan untuk menampilkan username
    for i in range(len(df)):
        ax.text(df.loc[i]['x'], df.loc[i]['y'], df.loc[i]['acc_names'], size=8)

    # Kalau tidak ada folder static/images, maka buat folder baru
    if not os.path.exists('./static/images'):
        os.makedirs('./static/images')

    # Menyimpan gambar ke dalam folder static/images
    image_cluster = './static/images/clustering_guru.png'
    plt.savefig(image_cluster)
    plt.close()

    return image_cluster

# Fungsi untuk proses melakukan clustering
def perform_clustering():
    # memuat dataset
    acc_names, tweets = read_dataset("./dataset/data_cluster.csv")

    # Preprocess tweets menggunakan fungsi preprocess
    preprocessed_tweets = [preprocess(tweet) for tweet in tweets]

    # TF-IDF Vectorizer digunakan untuk mengubah teks menjadi vektor
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(preprocessed_tweets)

    # DEBUGGING: Menampilkan shape dari X
    # print(f'shape of x: {X.shape}')

     # Check for NaN or Inf values
    if np.isnan(X.toarray()).any() or np.isinf(X.toarray()).any():
        raise ValueError("Data contains NaN or Inf values.")

    # Menggunakan KMeans untuk clustering
    num_topics = 4
    # km = KMeans(n_clusters=num_topics, random_state=42)
    # Menggunakan KMeans untuk clustering dengan inisialisasi k-means++
    km = KMeans(n_clusters=num_topics, random_state=42, init='k-means++')
    km.fit(X)
    clusters = km.labels_.tolist()

    # DEBUGGING: Menampilkan cluster labels dan unique cluster labels
    # print(f"Cluster labels: {clusters}")
    # print(f"Unique cluster labels: {set(clusters)}")

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

    # Tentukan nama cluster berdasarkan kata yang sering muncul
    cluster_names = {}
    for i, word_count in enumerate(cluster_word_counts):
        common_words = word_count.most_common(3)
        cluster_names[i] = ', '.join([word for word, count in common_words])

    # Buat plot clustering
    plot_url = plot_doc_cluster(xs, ys, clusters, acc_names, cluster_names)

    # Proses evaluasi clustering menggunakan silhouette score dan davies bouldin score
    # Inertia merupakan jarak kuadrat antara setiap sampel cluster terdekat, semakin kecil nilai inertia semakin baik
    inertia = km.inertia_

    # Silhouette Score Mengukur seberapa mirip antara cluster sendiri dibandingkan dengan cluster yang lain
    # -1 nilai buruk sedangkan 1 nilai baik
    # Jika jumlah cluster lebih dari 1, maka hitung silhouette score
    if len(set(km.labels_)) > 1:
        silhoutte_avg = silhouette_score(X, km.labels_)
    else:
        silhoutte_avg = None

    # Davies Bouldin mengukur rata-rata jarak antara setiap cluster, semakin kecil nilai semakin baik
    davies_bouldin = davies_bouldin_score(X.toarray(), km.labels_)

    # DEBUGGING: menampilkan nilai inertia, silhouette score, dan davies bouldin index
    # print(f"Inertia: {inertia}")
    # print(f"Silhouette Score: {silhoutte_avg}")
    # print(f"Davies-Bouldin Index: {davies_bouldin}")

    return plot_url, clusters, preprocessed_tweets, inertia, silhoutte_avg, davies_bouldin

# Fungsi untuk membuat plot distribusi kata-kata
def generate_word_distribution_plot(tweets, clusters, num_topics=4):
    vectorizer = TfidfVectorizer(max_features=5000)
    X = vectorizer.fit_transform(tweets)
    terms = vectorizer.get_feature_names_out()
    X = X.toarray()
    terms = np.array(terms)
    image_paths = []  # List untuk menyimpan path gambar

    # Proses perulangan buat distribusi kata per-topik yang ditemukan
    for topic in range(num_topics):
        cluster_tweets = [tweets[i] for i in range(len(tweets)) if clusters[i] == topic]
        all_words = ' '.join(cluster_tweets).split()
        word_counts = Counter(all_words)
        # Mengambil 10 kata teratas
        common_words = word_counts.most_common(10)
        words, counts = zip(*common_words)

        plt.figure(figsize=(7, 7))
        plt.bar(words, counts)
        plt.xticks(rotation='vertical')
        plt.title(f'Word Distribution of Topic {topic}')

        # Menyimpan ganmbar ke dalam folder static/images
        image_path = f'./static/images/word_distribution_topic_{topic}.png'
        plt.savefig(image_path)
        plt.close()
        image_paths.append(image_path)  # Tambahkan path gambar ke list
    return image_paths

# Router untuk melakukan clustering menampilkan username dan tweet full_text
@clustering.route('/clustering', methods=['GET'])
def clustering_tweet():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    plot_url, clusters, tweets, inertia, silhoutte_avg, davies_bouldin = perform_clustering()
    # Memanggil fungsi generate_word_distribution_plot untuk membuat plot distribusi kata-kata
    image_paths = generate_word_distribution_plot(tweets, clusters)
    # Tampung hasil clustering dan plot distribusi kata-kata ke dalam render_template html

    # Tampung username yang sedang login
    username = session['username']
    return render_template(
        'clustering.html',
        current_url=request.path,
        username=username,
        image_cluster=plot_url,
        image_paths=image_paths,
        inertia=inertia,
        silhoutte_avg=silhoutte_avg,
        davies_bouldin=davies_bouldin
    )

# fungsi untuk melakukan data testing
# @clustering.route('/data-training', methods=['GET'])
# def data_training():
#     if 'username' not in session:
#         return redirect(url_for('auth.login'))

#     # Tampung username yang sedang login
#     username = session['username']
#     return render_template(
#         current_url=request.path,
#         username=username,
#     )