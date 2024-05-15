import re

def remove_url(text):
    # Delete URLs
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
    # Delete emoticons other
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
    text = text.strip()
    return text


# ========================================================================================================
# Editor: Nabil 15-05-2024
# def clear_twitter_text(text):

     # Hapus @mentions
     # text = re.sub(r'@[A-Za-z0-9_]+', '', text)

     # Hapus #hashtags
     # text = re.sub(r'#', '', text)

     # Hapus URL
     # text = re.sub(r'https?://[^\s]+', '', text)
     # text = re.sub(r'www\.[^\s]+', '', text)

     # Menghapus titik, titik dua, dan titik koma
     # text = re.sub(r'[:,;.]', '', text)


     # Menghapus karakter !, ? dan -
     # text = re.sub(r'[!?\-]', '', text)

     # Menghapus angka
     # text = re.sub(r'\d+', '', text)

     # return text