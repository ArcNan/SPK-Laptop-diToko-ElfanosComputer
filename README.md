

 # Aplikasi SPK Pemilihan Laptop - Toko Elfanos


## --- Deskripsi ---

Aplikasi Sistem Pendukung Keputusan (SPK) berbasis Streamlit untuk
merekomendasikan laptop di Toko Elfanos menggunakan metode Analytical
Hierarchy Process (AHP).

## --- Fitur Utama ---
- Manajemen Pengguna: Login dengan peran Admin & Karyawan.
- CRUD Data Produk: Admin dapat menambah, mengedit, & menghapus data laptop.
- Manajemen Kriteria AHP: Admin bisa mengatur kriteria dan bobotnya.
- Perhitungan Rasio Konsistensi (CR): Untuk validasi matriks AHP.
- Proses Seleksi: Memberikan peringkat laptop berdasarkan perhitungan AHP.
- Cetak Laporan PDF: Mengunduh data produk, kriteria, dan hasil seleksi.


## --- Demo ---

### Tampilan Aplikasi

**Halaman Login**

<img width="480" height="854" alt="image" src="https://github.com/user-attachments/assets/6ad1f206-633d-46fa-88e2-93546ec26aaf" />






**Dashboard Admin**

<img width="480" height="854" alt="Screenshot 2025-10-06 104351" src="https://github.com/user-attachments/assets/765286c4-14f2-4478-8c72-ddd482a11932" />


## --- Teknologi yang Digunakan ---
- Framework: Streamlit
- Manajemen Data: Pandas, NumPy
- Database: SQLite
- Pembuatan PDF: FPDF


## --- Instalasi & Cara Menjalankan ---
1. Clone repositori ini:
   (bash)
   git clone https://github.com/ArcNan/SPK-Laptop-diToko-ElfanosComputer.git

2. Buat dan aktifkan virtual environment (direkomendasikan):
   (bash)
   python -m venv venv
   source venv/bin/activate  # Untuk macOS/Linux
   # venv\Scripts\activate   # Untuk Windows

3. Instal semua dependensi yang dibutuhkan:
   (bash)
   pip install -r requirements.txt

4. Jalankan aplikasi Streamlit:
   (bash)
   streamlit run main-app.py

5. Buka browser dan akses alamat yang muncul di terminal
   (biasanya http://localhost:8501).

**Akun Default:**
- Username: admin
- Password: admin
