Aplikasi SPK Pemilihan Laptop - Toko Elfanos
Aplikasi ini adalah Sistem Pendukung Keputusan (SPK) berbasis web yang dibangun menggunakan Streamlit untuk membantu pelanggan Toko Elfanos Computer dalam memilih laptop yang paling sesuai dengan kebutuhan mereka. Sistem ini mengimplementasikan metode Analytical Hierarchy Process (AHP) untuk melakukan perangkingan alternatif laptop berdasarkan kriteria yang telah ditentukan.

Aplikasi ini memiliki dua peran pengguna: Admin dan Karyawan. Admin memiliki kontrol penuh atas data produk, kriteria, dan manajemen pengguna, sedangkan Karyawan hanya dapat melihat data produk dan melakukan proses seleksi.

Fitur Utama
Manajemen Pengguna:

Sistem login dengan dua peran (Admin dan Karyawan).

Admin dapat menambah dan menghapus akun pengguna.

Fitur reset password untuk semua pengguna.

CRUD Data Produk (Laptop):

Admin dapat menambah, melihat, mengedit, dan menghapus data laptop yang tersedia di toko.

Tampilan data produk dalam bentuk tabel yang informatif.

CRUD Kriteria AHP:

Admin dapat mengelola kriteria yang digunakan dalam perhitungan AHP (misalnya: Harga, RAM, Prosesor, dll).

Setiap kriteria memiliki bobot yang dapat disesuaikan.

Perhitungan AHP:

Perbandingan Berpasangan: Admin dapat mengisi matriks perbandingan berpasangan antar kriteria.

Rasio Konsistensi (CR): Sistem secara otomatis menghitung Consistency Ratio (CR) untuk memastikan validitas perbandingan. Jika CR ≥ 0.10, sistem akan memberikan peringatan.

Penerapan Bobot Eigenvector: Bobot yang dihasilkan dari matriks perbandingan dapat diterapkan secara otomatis untuk perhitungan.

Proses Seleksi (Ranking):

Pengguna dapat memilih beberapa laptop yang ingin dibandingkan.

Sistem akan menghitung skor akhir untuk setiap laptop berdasarkan kriteria dan bobot yang ada.

Hasil ditampilkan dalam bentuk tabel peringkat yang sudah diurutkan.

Cetak Laporan PDF:

Kemampuan untuk mencetak dan mengunduh laporan dalam format PDF untuk:

Daftar Data Produk

Daftar Kriteria dan Bobotnya

Hasil Akhir Seleksi Laptop

Teknologi yang Digunakan

Framework: Streamlit 


Manajemen Data: Pandas, NumPy 


Database: SQLite 


Pembuatan PDF: FPDF 


Navigasi Menu: streamlit-option-menu 

Instalasi dan Cara Menjalankan
Clone Repositori

Bash

git clone https://github.com/nama-anda/repositori-ini.git
cd repositori-ini
Buat Virtual Environment (Direkomendasikan)

Bash

python -m venv venv
Windows:

Bash

venv\Scripts\activate
macOS/Linux:

Bash

source venv/bin/activate
Instal Dependensi
Pastikan Anda memiliki file requirements.txt di direktori proyek.

Bash

pip install -r requirements.txt
Jalankan Aplikasi

Bash

streamlit run main-app.py
Aplikasi akan terbuka secara otomatis di browser Anda.

Cara Penggunaan
Login sebagai Admin:

Username: admin

Password: admin

Gunakan menu di sidebar untuk bernavigasi antara halaman Data Produk, Kriteria, Seleksi, dan manajemen pengguna lainnya.

Untuk pengguna baru, Anda dapat mendaftar melalui menu Tambah Akun di halaman login. Pengguna baru akan otomatis mendapatkan peran "karyawan".
