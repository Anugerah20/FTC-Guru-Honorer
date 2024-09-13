# Menjalankan Aplikasi Website
- .\venv\Scripts\activate
- flask run
- Atau python app.py
# Berhenti Menjalankan Aplikasi Website
- CTR+C
- deactivate

# INFO!
-  Di branch dev-nabil Mysql + SQLAlchemy + ORM (Tidak ada perintah kode SQL dikodingannya)
-  Pada branch mysql-dev (Ada perinth kode SQL dikodingannya)
  
## API
1. Proses crawling dataset csv
   - http://127.0.0.1:5000/upload-file
2. Menampilkan hasil crawling
   - http://127.0.0.1:5000/show-guru
3. Proses preprocessing dataset csv
   - http://127.0.0.1:5000/upload-preprocessing
4. Menampilkan hasil preprocessing
   - http://127.0.0.1:5000/show-preprocessing
5. Proses klasterisasi Frequent Term Based Clustering (FTC)
   - http://127.0.0.1:5000/ftc
6. Menampilkan hasil klasterisasi FTC
   - http://127.0.0.1:5000/ftc/results
7. Menghapus database klasterisasi FTC, dataset preprocessing, dan file JSON FTC
   - http://127.0.0.1:5000/delete-clustering-ftc
8. Memproses dan menampilkan pengujian menggunakan purity
   - http://127.0.0.1:5000/purity
