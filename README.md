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

## METODE KLASTERISASI FTC
1. Branch metode-ftc -> Menerapkan klasterisasi FTC tetapi belum menandai klaster kandidat
2. Branch baru-ftc -> Sudah menerapkan FTC dan terdapat tanda klaster kandidat
3. Branch mysql-dev -> Pembaruan perintah SQL yang sudah menggunakan MySQL
4. dev-nabil -> Belum menerapkan SQL di MySQL
5. main -> Belum di update dari awal
  
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
