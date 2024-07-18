import re

def remove_url(text):
    # Menghapus URL, yang diawali dengan http, https, atau www
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_emoticons(text):
    # Delete emoticons
    emoticon_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"
                                  u"\U0001F300-\U0001F5FF"
                                  u"\U0001F680-\U0001F6FF"
                                  u"\U0001F1E0-\U0001F1FF"
                                  "]+", flags=re.UNICODE)
    return emoticon_pattern.sub(r'', text)

def remove_emoticons_other(text):
    # Menghapus emoticon yang tidak terdeteksi oleh emoticon_pattern
    emoticon_pattern = re.compile(r'[:;][-~]?[)Dd\]]+|[\[(][-~]?[:;]', flags=re.UNICODE)
    return emoticon_pattern.sub(r'', text)

def clear_twitter_text(text):
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = remove_url(text)
    text = re.sub(r'[:,;.]', '', text)
    text = re.sub(r'[!?]', '', text)
    text = re.sub(r'[+()]+|[%x=]+|&amp|&gt|&lt', '', text)
    text = re.sub(r'[\\\\\'\\"]', '', text)
    text = remove_emoticons(text)
    text = remove_emoticons_other(text)
    # Menghapus spasi di awal dan di akhir kalimat
    text = text.strip()
    # Mengubah teks menjadi huruf kecil
    text = text.lower()
    return text
