import preprocessor as p
from textblob import TextBlob
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import pandas as pd

def labeling_text():
    nltk.download('punkt')
    
    data = pd.read_csv("data/translateGuruHonorer.csv")

    data_tweet = list(data['tweet_eng'])
    polaritas = 0

    status = []
    total_setuju = total_tidak_setuju = total_netral = total = 0

    for i, tweet in enumerate(data_tweet):
        analysis = TextBlob(tweet)
        polaritas += analysis.polarity

        if analysis.sentiment.polarity > 0.0:
            total_setuju += 1
            status.append('setuju')
        elif analysis.sentiment.polarity == 0.0:
            total_netral += 1
            status.append('netral')
        else:
            total_tidak_setuju += 1
            status.append('tidak setuju')

        total += 1

    hasil_analisis = {
        'total_setuju': total_setuju,
        'total_netral': total_netral,
        'total_tidak_setuju': total_tidak_setuju,
        'total_data': total
    }

    data['klasifikasi'] = status
    data['hasil_analisis'] = str(hasil_analisis)

    data.to_csv("data/labelingText.csv", index=False)

    return hasil_analisis

# Contoh penggunaan fungsi
hasil_analisis = labeling_text()
print(hasil_analisis)
