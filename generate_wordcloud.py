# wordcloud_generator.py
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

def generate_wordcloud(csv_file_path):
    # Baca data dari CSV
    data = pd.read_csv(csv_file_path)

    # Pastikan kolom 'full_text' ada di dalam data
    if 'full_text' in data.columns:
        all_words = ' '.join([tweet for tweet in data['full_text']])
    else:
        raise ValueError("Kolom 'full_text' tidak ditemukan dalam data.")
    
    # Generate WordCloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        random_state=3,
        background_color='black',
        colormap='RdPu',
        collocations=False,
        stopwords=STOPWORDS
    ).generate(all_words)

    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('static/wordcloud.png')