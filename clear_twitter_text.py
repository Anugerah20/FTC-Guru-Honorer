import re

def clear_twitter_text(text):

     # Hapus @mentions
     text = re.sub(r'@[A-Za-z0-9_]+', '', text)

     # Hapus #hashtags
     text = re.sub(r'#', '', text)

     # Hapus URL
     text = re.sub(r'https?://[^\s]+', '', text)
     text = re.sub(r'www\.[^\s]+', '', text)

     # Menghapus titik, titik dua, dan titik koma
     text = re.sub(r'[:,;.]', '', text)


     # Menghapus karakter !, ? dan -
     text = re.sub(r'[!?\-]', '', text)

    # Menghapus angka
    # text = re.sub(r'\d+', '', text)

     return text