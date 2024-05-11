# Proses melakukan translate bahasa indonesia ke bahasa inggris
import pandas as pd
from googletrans import Translator

# data = pd.read_csv("/content/drive/MyDrive/Skripsi/Hasil Terjemahan/preprocesingGuruHonorerBaru.csv")

def convert_eng(tweet):
    translator = Translator()
    translation = translator.translate(tweet, src='id', dest='en')
    return translation.text

# data['tweet_eng'] = data['tweet'].apply(convert_eng)
# data.to_csv("/data/translateGuruHonorerBaru.csv", index=False)