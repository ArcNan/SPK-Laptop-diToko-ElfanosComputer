# ========== IMPORTS ==========
import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_option_menu import option_menu
from fpdf import FPDF          
from datetime import datetime
import numpy as np
import base64
import streamlit.components.v1 as components
import sqlite3 

# ========== CONFIG ==========
st.set_page_config(page_title="Aplikasi SPK Laptop", page_icon="💻", layout="centered")

# ========== KELAS PDF (GLOBAL) ===============
class PDF(FPDF):
    def __init__(self,
                 orientation="P", unit="mm", format="A4",
                 title="Hasil Perhitungan Skor"):
        super().__init__(orientation, unit, format)
        self.title_text  = title    
        self._first_page = True     

    # ───────────────────────────────── HEADER ─────────────────────────────────
    def header(self):
        # ── logo & identitas toko 
        self.image("ElfanosLogo.png", x=12, y=8, w=26)

        self.set_font("Arial", "B", 14)
        self.set_x(40)
        self.cell(0, 10, "Toko Elfanos Computer", ln=True, align="L")

        self.set_font("Arial", "", 10)
        self.set_x(40)
        self.cell(
            0, 5,
            "Komp. Al, Jl. Raya Panggung No.62, Jatibening, Kec. Pd. Gede, "
            "Kota Bks, Jawa Barat 17412",
            ln=True, align="L",
        )
        self.set_x(40)
        self.cell(
            0, 5,
            "Telp: (+62) 81311567575 | Email: info@elfanoscomputer.com",
            ln=True, align="L",
        )

        # ── garis horizontal menyesuaikan orientasi ──────────────────────────
        self._draw_header_line()

        # ── judul tabel : tampil hanya di halaman pertama ────────────────────
        if self._first_page:
            self.set_font("Arial", "B", 14)
            self.cell(0, 8, self.title_text, ln=True, align="C")
            self.ln(2)
            self._first_page = False
        else:
            self.ln(10)   # supaya tabel di halaman berikutnya turun konsisten

    def _draw_header_line(self):
        
        self.ln(4)
        self.set_line_width(0.5)
        x1 = self.l_margin
        x2 = self.w - self.r_margin   # self.w = lebar halaman saat ini
        y  = self.get_y()
        self.line(x1, y, x2, y)
        self.ln(5)

    # ---------- FOOTER : HANYA NOMOR HALAMAN ----------
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Halaman {self.page_no()}", align="C")

    # ---------- BLOK TANDA‑TANGAN (dipanggil manual) ----------
    def add_signature_block(self):
        # jika sisa ruang < 45 mm, buat halaman baru
        if self.get_y() > self.h - 60:
            self.add_page()

        self.ln(10)                                    # sedikit jarak
        self.set_font("Arial", "", 10)
        tanggal = datetime.now().strftime("%d %B %Y")
        self.cell(0, 5, f"Bekasi, {tanggal}", ln=True, align="R")

        self.ln(25)                                     
        self.set_font("Arial", "U", 10)                 
        self.cell(0, 5, "Nanda Budi S.", ln=True, align="R")

        self.ln(2)                                    # ruang ttd
        self.set_font("Arial", "I", 8)
        self.cell(0, 5, "Owner Elfanos Computer", ln=True, align="R")

# ========== TABEL HASIL SELEKSI ===============
   
    def make_table(self, df):
        col_w = [15, 20, 45, 80, 30]  
        headers = ["ID", "Rank", "Merk", "Tipe", "Skor"]
        start_x = (self.w - sum(col_w)) / 2

        self.set_font("Arial", "B", 11); self.set_x(start_x)
        for w, h in zip(col_w, headers):
            self.cell(w, 8, h, 1, 0, "C")
        self.ln()

        self.set_font("Arial", "", 10)
        for _, r in df.iterrows():
            self.set_x(start_x)
            self.cell(col_w[0], 8, str(r["Id"]),   1, 0, "C")
            self.cell(col_w[1], 8, str(r["Rank"]), 1, 0, "C")
            self.cell(col_w[2], 8, r["Merk"],      1)
            self.cell(col_w[3], 8, r["Tipe"],      1)
            self.cell(col_w[4], 8, f"{r['Skor']:.3f}", 1, 1, "C")

# ========== TABEL DATA PRODUK ===============

    def make_table_produk(self, df):
        df = df[["Id", "Merk", "Tipe", "Prosesor", "Ram", "Penyimpanan",
                 "Vga", "Layar", "Baterai", "Sistem Operasi", "Harga"]]

        headers = df.columns.tolist()
        col_w = [12, 28, 38, 38, 15, 38, 30, 15, 20, 38, 21]  # total ≈ 293 mm
        start_x = (self.w - sum(col_w)) / 2

        self.set_font("Arial", "B", 8); self.set_x(start_x)
        for w, h in zip(col_w, headers):
            self.cell(w, 7, h, 1, 0, "C")
        self.ln()

        self.set_font("Arial", "", 7)
        for _, r in df.iterrows():
            self.set_x(start_x)
            for w, c in zip(col_w, headers):
                self.cell(w, 6, str(r[c]), 1, 0, "C")
            self.ln()

# ========== TABEL KRITERIA ===============            

    def make_table_kriteria(self, df):
        df = df[["Id", "Nama", "Bobot"]]
        headers = ["Id", "Nama Kriteria", "Bobot"]
        col_w   = [15, 100, 30]                     # total 145 mm → potret

        start_x = (self.w - sum(col_w)) / 2
        self.set_font("Arial", "B", 11); self.set_x(start_x)
        for w, h in zip(col_w, headers):
            self.cell(w, 8, str(h), 1, 0, "C")
        self.ln()

        self.set_font("Arial", "", 10)
        for _, r in df.iterrows():
            self.set_x(start_x)
            self.cell(col_w[0], 8, str(r["Id"]),   1, 0, "C")
            self.cell(col_w[1], 8, r["Nama"],      1)
            self.cell(col_w[2], 8, f"{r['Bobot']:.4f}", 1, 1, "C")

# ========== TABEL PAIR‑WISE (CR)  ===============  
            
    def make_table_cr(self, df):
        """
        df : DataFrame matriks perbandingan dengan index & columns = nama kriteria
        """
        headers = [""] + df.columns.tolist()
        col_w   = [30] + [25]*len(df.columns)      
        start_x = (self.w - sum(col_w)) / 2

        # header
        self.set_font("Arial", "B", 9); self.set_x(start_x)
        for w, h in zip(col_w, headers):
            self.cell(w, 7, str(h), 1, 0, "C")
        self.ln()

        # isi
        self.set_font("Arial", "", 9)
        for idx, row in df.iterrows():
            self.set_x(start_x)
            self.cell(col_w[0], 7, str(idx), 1, 0, "C")
            for w, val in zip(col_w[1:], row):
                self.cell(w, 7, f"{val:.4g}", 1, 0, "C")
            self.ln()

# ========== TABEL ALTERNATIF (SCALE 1‑9)  =============== 

    def make_table_alt(self, df):
        df = df[["Id", "Nama", "Skala (1-9)"]]
        headers = ["Id", "Kriteria", "Skala 1-9"]
        col_w   = [15, 100, 30]

        start_x = (self.w - sum(col_w)) / 2
        self.set_font("Arial", "B", 11); self.set_x(start_x)
        for w, h in zip(col_w, headers):
            self.cell(w, 8, str(h), 1, 0, "C")
        self.ln()

        self.set_font("Arial", "", 10)
        for _, r in df.iterrows():
            self.set_x(start_x)
            self.cell(col_w[0], 8, str(r["Id"]), 1, 0, "C")
            self.cell(col_w[1], 8, r["Nama"],    1)
            self.cell(col_w[2], 8, str(r["Skala (1-9)"]), 1, 1, "C")

# ========== KELAS CETAK PDF (GLOBAL)  =============== 

def cetak_pdf_button(pdf_bytes: bytes, height=46, label="🖨️ Cetak PDF", width="120px"):
    if not pdf_bytes:
        return
    b64 = base64.b64encode(pdf_bytes).decode()
    components.html(f"""
        <button id="print-btn"
                style="
                background-color: transparent;
                color:#4CAF50;
                padding:8px 6px;
                border:2px solid #4CAF50;
                border-radius:8px;
                cursor:pointer;
                width: {width};
                font-weight: 600;
                font-size: 14px;
                font-family: 'arial', sans-serif;
                margin-top: 0px;
                ">
        {label}
        </button>

        <script>
        function b64toBlob(b64Data, contentType) {{
            const byteChars = atob(b64Data);
            const byteArrays = [];
            for (let offset = 0; offset < byteChars.length; offset += 512) {{
                const slice = byteChars.slice(offset, offset + 512);
                const byteNumbers = Array.from(slice).map(ch => ch.charCodeAt(0));
                byteArrays.push(new Uint8Array(byteNumbers));
            }}
            return new Blob(byteArrays, {{ type: contentType }});
        }}

        document.getElementById("print-btn").addEventListener("click", function() {{
            const blob = b64toBlob("{b64}", "application/pdf");
            const url  = URL.createObjectURL(blob);
            const w    = window.open(url, "_blank", "width=1200,height=800");
            w.focus();
            setTimeout(() => w.print(), 2000);
        }});
        </script>
    """, height=height)

# ========== PATH untuk SQLite =============== 

DB_PATH = "database/spk_laptop.db"

# Pastikan direktori database ada
Path("database").mkdir(parents=True, exist_ok=True)

# Fungsi untuk inisialisasi database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Buat tabel users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            nama TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Buat tabel laptops
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laptops (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Merk TEXT,
            Tipe TEXT,
            Prosesor TEXT,
            Ram INTEGER,
            Penyimpanan TEXT,
            Vga TEXT,
            Layar TEXT,
            Baterai TEXT,
            "Sistem Operasi" TEXT, -- Kolom dengan spasi perlu diapit kutip ganda
            Harga INTEGER
        )
    """)

    # Buat tabel kriteria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kriteria (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Nama TEXT UNIQUE,
            Bobot REAL
        )
    """)

    # Tambahkan admin jika belum ada
    cursor.execute("SELECT COUNT(*) FROM users WHERE nama = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (nama, password, role) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))
    
    conn.commit()
    conn.close()
init_db()

# ========== DATABASE CONNECTION (GLOBAL) =============== 

def get_db_connection():
 
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

# ========== USER MANAGEMENT =============== 

def load_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM users", conn)
    conn.close()
    return df

def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE nama = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    if result:
        return True, result[0]
    return False, None

def add_user(username, password, role="karyawan"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (nama, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True, f"✅ Pengguna '{username}' berhasil ditambahkan!"
    except sqlite3.IntegrityError:
        return False, "Username sudah digunakan."
    finally:
        conn.close()

def delete_user(username):
    if username.lower() == "admin":
        return False, "⚠️ Admin tidak bisa dihapus!"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE nama = ?", (username,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    if rows_affected > 0:
        return True, f"✅ User '{username}' berhasil dihapus!"
    return False, "⚠️ User tidak ditemukan."

def reset_password(username, new_password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE nama = ?", (new_password, username))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    if rows_affected > 0:
        return True, "✅ Password berhasil direset!"
    return False, "⚠️ Username tidak ditemukan."

# ========== LAPTOP DATA MANAGEMENT =============== 

def load_laptop_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM laptops", conn)
    conn.close()
    return df

def save_laptop_data(df):
    pass 

def add_laptop_row(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    
    if "Id" in data:
        del data["Id"]

    # apit nama kolom yang punya spasi
    columns = ', '.join([f'"{col}"' if ' ' in col else col for col in data.keys()])
    placeholders = ', '.join(['?'] * len(data))

    query = f"INSERT INTO laptops ({columns}) VALUES ({placeholders})"
    cursor.execute(query, tuple(data.values()))
    conn.commit()
    conn.close()

def migrate_laptops_schema_if_needed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Cek skema saat ini
    cur.execute("PRAGMA table_info(laptops)")
    cols = cur.fetchall()  

    id_col = next((c for c in cols if c[1].lower() == "id"), None)
    need_migration = (
        not id_col or id_col[2].upper() != "INTEGER" or id_col[5] != 1
    )

    if need_migration:
        
        cur.execute("ALTER TABLE laptops RENAME TO laptops_old")

     
        cur.execute("""
            CREATE TABLE laptops (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                Merk TEXT,
                Tipe TEXT,
                Prosesor TEXT,
                Ram INTEGER,
                Penyimpanan TEXT,
                Vga TEXT,
                Layar TEXT,
                Baterai TEXT,
                "Sistem Operasi" TEXT,
                Harga INTEGER
            )
        """)

        
        cur.execute("""
            INSERT INTO laptops (Merk, Tipe, Prosesor, Ram, Penyimpanan, Vga, Layar, Baterai, "Sistem Operasi", Harga)
            SELECT Merk, Tipe, Prosesor, Ram, Penyimpanan, Vga, Layar, Baterai, "Sistem Operasi", Harga
            FROM laptops_old
        """)

        cur.execute("DROP TABLE laptops_old")
        conn.commit()

 
    cur.execute("DELETE FROM laptops WHERE Id IS NULL")
    conn.commit()
    conn.close()

# Panggil setelah init_db()
init_db()
migrate_laptops_schema_if_needed()

def reorder_laptop_ids():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ambil semua data kecuali Id, urutkan berdasarkan Id lama
    cur.execute('''
        SELECT Merk, Tipe, Prosesor, Ram, Penyimpanan, Vga, Layar, 
               Baterai, "Sistem Operasi", Harga
        FROM laptops
        ORDER BY Id
    ''')
    rows = cur.fetchall()

    # Hapus semua data & reset sequence AUTOINCREMENT
    cur.execute("DELETE FROM laptops")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='laptops'")

    # Masukkan kembali data dengan ID baru berurutan
    cur.executemany('''
        INSERT INTO laptops (Merk, Tipe, Prosesor, Ram, Penyimpanan, Vga, 
                              Layar, Baterai, "Sistem Operasi", Harga)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', rows)

    conn.commit()
    conn.close()

# Jalankan langsung setelah inisialisasi DB
init_db()
reorder_laptop_ids()


def update_laptop_row(laptop_id, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Apit kolom yang ada spasi
    set_clause = ', '.join([f'"{col}" = ?' if ' ' in col else f"{col} = ?" for col in data.keys()])

    query = f"UPDATE laptops SET {set_clause} WHERE Id = ?"
    cursor.execute(query, tuple(data.values()) + (laptop_id,))
    conn.commit()
    conn.close()


def delete_laptop_row(row_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if row_id is None or (isinstance(row_id, float) and pd.isna(row_id)):
            cursor.execute("DELETE FROM laptops WHERE Id IS NULL")
        else:
            cursor.execute("DELETE FROM laptops WHERE Id = ?", (int(row_id),))
        conn.commit()
    finally:
        conn.close()

# ========== KRITERIA MANAGEMENT =============== 

def load_kriteria():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM kriteria", conn)
    conn.close()
    return df
    

def save_kriteria(df):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for index, row in df.iterrows():
        cursor.execute("INSERT OR REPLACE INTO kriteria (Id, Nama, Bobot) VALUES (?, ?, ?)",
                       (row['Id'], row['Nama'], row['Bobot']))
    conn.commit()
    conn.close()

def add_kriteria_row(nama, bobot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kriteria (Nama, Bobot) VALUES (?, ?)", (nama, bobot))
        conn.commit()
        return True, f"✅ Kriteria '{nama}' ditambahkan."
    except sqlite3.IntegrityError:
        return False, "Nama kriteria sudah ada."
    finally:
        conn.close()

def update_kriteria_row(kriteria_id, nama, bobot):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE kriteria SET Nama = ?, Bobot = ? WHERE Id = ?", (nama, bobot, kriteria_id))
        conn.commit()
        return True, "✅ Diperbarui."
    except sqlite3.IntegrityError:
        return False, "Nama kriteria sudah ada."
    finally:
        conn.close()

def delete_kriteria_by_id(kriteria_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kriteria WHERE Id = ?", (kriteria_id,))
    conn.commit()
    conn.close()


# ---------- HELPER ----------
def scale_saaty_from_bobot(b):      # bobot 0‑1 → 1‑9
    return max(1,min(9,round(1+b*8)))

# ---------- AHP Consistency Helper ----------
def compute_cr(matrix: np.ndarray):
    """
    Hitung λ_max, CI, CR serta eigen‑vector prioritas (bobot).
    matrix: matriks pairwise (n×n, positif, reciprocal)

    Return: lam_max, CI, CR, priority_vector
    """
    n = matrix.shape[0]

    # Validasi dasar
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matriks harus persegi (n×n).")
    if (matrix <= 0).any():
        raise ValueError("Semua elemen matriks harus positif (> 0).")

    # Hitung eigenvalue dan eigenvector
    eigvals, eigvecs = np.linalg.eig(matrix)
    max_idx = np.argmax(eigvals.real)
    lam_max = eigvals.real[max_idx]

    # Ambil eigenvector utama dan normalisasi
    w = eigvecs[:, max_idx].real
    w = np.abs(w)  
    w = w / w.sum()

    # Hitung CI dan CR
    CI = (lam_max - n) / (n - 1) if n > 1 else 0

    RI_table = {
        1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
    }
    RI = RI_table.get(n, 1.49)  # fallback untuk n > 10
    CR = CI / RI if RI else 0

    return lam_max, CI, CR, w

def default_pairwise(weights, index):
    if len(weights) == 0:
        raise ValueError("Daftar bobot kosong.")
    if any(w <= 0 for w in weights):
        raise ValueError("Semua bobot harus lebih dari 0.")

    return pd.DataFrame(
        [[wi / wj for wj in weights] for wi in weights],
        index=index, columns=index
    )


# ========== INISIALISASI ==========
if "login_user" not in st.session_state:
    st.session_state["menu"] = "Login"
else:
    st.session_state["menu"] = "Beranda"

# ========== SIDEBAR =============== 

with st.sidebar:
    # tentukan daftar opsi + ikon seperti semula …
    if "login_user" not in st.session_state:
        unauth_opts  = ["Login", "Tambah Akun"]
        unauth_icons = ["door-open", "person-plus"]
        default_name = st.session_state.get("menu", "Login")
        default_idx  = unauth_opts.index(default_name) if default_name in unauth_opts else 0

        menu = option_menu(
            "Elfanos Computer",
            unauth_opts,
            icons=unauth_icons,
            default_index=default_idx,      
            menu_icon="pc-display",
        )

    else:
        role = st.session_state.get("user_role", "")
        sidebar_options = ["Beranda", "Data Produk", "Seleksi", "Logout"]
        sidebar_icons = ["house", "database", "check2-circle", "box-arrow-right"]

        if role == "admin":
            sidebar_options.insert(2, "Kriteria")
            sidebar_icons.insert(2, "filter")
            sidebar_options.insert(3,"Alternatif")
            sidebar_icons.insert(3,"bi bi-sort-up-alt")
            sidebar_options.append("Hapus User")
            sidebar_icons.append("trash")

        default_name = st.session_state.get("menu", sidebar_options[0])
        default_idx  = sidebar_options.index(default_name)

        menu = option_menu(
            "Elfanos Computer",
            sidebar_options,
            icons=sidebar_icons,
            default_index=default_idx,       
            menu_icon="pc-display",
        )
st.session_state["menu"] = menu

# =========== HEADER UI =============== 
col1, col2 = st.columns([1, 3])
with col1:
    st.image("ElfanosLogo.png", width=220)
with col2:
    st.markdown("<h2 style='text-align: center; margin-top: 20px'>Sistem Pendukung Keputusan Pemilihan Laptop</h2>", unsafe_allow_html=True)

st.markdown("---")

# ========== NOTIFIKASI ==========
for key in ["tambah_sukses", "hapus_sukses"]:
    if key in st.session_state:
        st.success(st.session_state[key])
        del st.session_state[key]

# ========== LOGIKA UTAMA ==========
if menu == "Login" and "login_user" not in st.session_state:
    from_login = st.tabs(["🔑 Login", "🔄 Lupa Password"])

    with from_login[0]:
        with st.form("login_form"):
            username = st.text_input("Nama Pengguna")
            password = st.text_input("Kata Sandi", type="password")
            login_button = st.form_submit_button("Login")

        if login_button:
            success, role = login(username, password)
            if success:
                st.session_state["login_user"] = username
                st.session_state["user_role"] = role
                st.session_state["menu"] = "Beranda"
                st.rerun()
            else:
                st.error("⚠️ Nama pengguna atau kata sandi salah.")

    with from_login[1]:
        st.info("Masukkan nama pengguna dan sandi baru.")
        with st.form("reset_form"):
            reset_user = st.text_input("Nama Pengguna")
            new_pass = st.text_input("Kata Sandi Baru", type="password")
            reset_button = st.form_submit_button("Reset Password")

        if reset_button:
            success, msg = reset_password(reset_user, new_pass)
            if success:
                st.success(msg)
            else:
                st.warning(msg)


elif menu == "Tambah Akun" and "login_user" not in st.session_state:
    with st.form("add_user_form"):
        new_user = st.text_input("Nama Pengguna Baru")
        new_pass = st.text_input("Kata Sandi Baru", type="password")
        new_role = st.selectbox("Peran Pengguna", ["karyawan"])
        submit_add = st.form_submit_button("Daftar")

    if submit_add:
        success, msg = add_user(new_user, new_pass, new_role)
        if success:
            st.success(msg)
        else:
            st.warning(msg)


elif "login_user" in st.session_state:
    role = st.session_state.get("user_role", "")

# ========== BERANDA ==========
    if menu == "Beranda":
        st.info("Selamat datang di Beranda Elfanos Computer, tempat Anda memulai perjalanan pengambilan keputusan dengan AHP. Di halaman ini Anda akan menemukan ringkasan sistem, petunjuk cepat cara menambahkan kriteria & alternatif, serta akses mudah ke perhitungan konsistensi dan laporan PDF—semuanya dirancang untuk membantu Anda memilih laptop terbaik secara transparan dan terukur.")

    elif menu == "Hapus User" and role == "admin":
        df_users = load_users()
        user_list = [u for u in df_users["nama"].values if u.lower() != "admin"]
        selected_user = st.selectbox("Pilih Pengguna", user_list) if user_list else None
        if selected_user and st.button("🗑️ Hapus User"):
            success, msg = delete_user(selected_user)
            if success:
                st.session_state["hapus_sukses"] = msg
            else:
                st.error(msg)
            st.rerun()

# ========== LOGOUT ==========
    elif menu == "Logout":
        for key in ["login_user", "user_role"]:
            if key in st.session_state: del st.session_state[key]
        st.success("Anda telah logout.")
        st.session_state["menu"] = "Login"
        st.rerun()


# =========== HEADER UI ===============


    elif menu == "Data Produk":
        df_laptop = load_laptop_data()
        st.dataframe(df_laptop.set_index("Id"), use_container_width=True)
        
        # Inisialisasi key jika belum ada
        if "pdf_bytes_produk" not in st.session_state:
            st.session_state["pdf_bytes_produk"] = None
        # ---------- CETAK / DOWNLOAD ----------
        st.markdown("### 📄 Cetak / Download Data Produk")
        col_pdf, col_csv = st.columns(2)

        with col_pdf:
            if st.button("📄 Buat PDF Data Produk"):
                    pdf_p = PDF(orientation="L", title="Daftar Data Produk Laptop")
                    pdf_p.set_auto_page_break(auto=True, margin=15)
                    pdf_p.add_page()
                    pdf_p.make_table_produk(df_laptop.copy())
                    pdf_p.add_signature_block()
                    st.session_state["pdf_bytes_produk"] = pdf_p.output(dest="S").encode("latin-1", "replace")
                    st.success("✅ PDF Data Produk berhasil dibuat!")

            if st.session_state.get("pdf_bytes_produk"):
                cetak_pdf_button(st.session_state["pdf_bytes_produk"])

        with col_csv:
            csv_produk_bytes = df_laptop.to_csv(index=False).encode()
            st.download_button(
                "⬇️ Download CSV Data Produk",
                data=csv_produk_bytes,
                file_name="data_produk.csv",
                mime="text/csv",
            )
        
            if st.session_state.get("pdf_bytes_produk"):
                    st.download_button(
                        "⬇️ Download PDF Data Produk",
                        data=st.session_state["pdf_bytes_produk"],
                        file_name="data_produk.pdf",
                        mime="application/pdf",
                    )
        
        role = st.session_state.get("user_role", "").lower()

        if role == "karyawan":
            st.caption(
                "Login sebagai Karyawan hanya memberikan akses untuk melihat Data Produk. Fitur tambah dan edit data tersedia hanya untuk Owner.",
                unsafe_allow_html=True
            )


        if role == "admin":
            st.markdown("---")
            st.subheader("➕ Tambah Data Laptop")
            with st.form("form_tambah_laptop"):
                col1, col2 = st.columns(2)
                with col1:
                    merk = st.text_input("Merk", key="add_merk")
                    tipe = st.text_input("Tipe", key="add_tipe")
                    prosesor = st.text_input("Prosesor", key="add_prosesor")
                    ram = st.number_input("RAM (GB)", min_value=1, step=1, key="add_ram")
                    penyimpanan_gb = st.number_input("Penyimpanan (GB)", min_value=64, step=64, key="add_penyimpanan_gb")
                    penyimpanan_tipe = st.selectbox("Jenis Penyimpanan", ["SSD", "HDD", "eMMC"], key="add_penyimpanan_tipe")
                    penyimpanan = f"{int(penyimpanan_gb)} GB {penyimpanan_tipe}"
                with col2:
                    vga = st.text_input("VGA", key="add_vga")
                    layars = st.number_input("Ukuran Layar", min_value=10.0, step=0.1, format="%.1f", key="add_layar_float")
                    layar = f'{layars}"'
                    baterai_wh = st.number_input("Baterai (Wh)", min_value=10, step=1, key="add_baterai_wh")
                    baterai = f"{int(baterai_wh)} Wh"
                    os_tipe = st.selectbox("Sistem Operasi", ["Windows", "MacOS", "ChromeOS"], key="add_os_tipe")
                    Os = os_tipe
                    harga = st.number_input("Harga (Rp)", min_value=800000, step=100000, key="add_harga")
                    submit_laptop = st.form_submit_button("Simpan Laptop")

            if submit_laptop:
                
                if not merk or not tipe or not prosesor or not vga or not Os:
                    st.error("⚠️ Merk, Tipe, Prosesor, VGA, dan Sistem Operasi tidak boleh kosong.")
                elif ram <= 0 or penyimpanan_gb <= 0 or layars <= 0 or baterai_wh <= 0 or harga <= 0:
                    st.error("⚠️ RAM, Penyimpanan, Layar, Baterai, dan Harga harus lebih dari nol.")
                else:
                    new_laptop_data = {
                        "Merk": merk, "Tipe": tipe, "Prosesor": prosesor, "Ram": ram,
                        "Penyimpanan": penyimpanan, "Vga": vga, "Layar": layar,
                        "Baterai": baterai, "Sistem Operasi": Os, "Harga": harga
                    }
                    add_laptop_row(new_laptop_data)
                    st.session_state["tambah_sukses"] = f"✅ Data laptop '{merk} {tipe}' berhasil ditambahkan!"
                    st.rerun()             
            st.markdown("---")

            df_laptop = load_laptop_data() 
            st.subheader("📝 Edit Data Laptop")

            if not df_laptop.empty:
                id_to_edit = st.selectbox("Pilih ID untuk Diedit", df_laptop["Id"], key="edit_id_select")
                row_to_edit = df_laptop[df_laptop["Id"] == id_to_edit].iloc[0]

                with st.form("form_edit_laptop"):
                    col1, col2 = st.columns(2)

                    with col1:
                        merk = st.text_input("Merk", value=row_to_edit["Merk"], key="edit_merk")
                        tipe = st.text_input("Tipe", value=row_to_edit["Tipe"], key="edit_tipe")
                        prosesor = st.text_input("Prosesor", value=row_to_edit["Prosesor"], key="edit_prosesor")
                        ram = st.number_input("RAM (GB)", min_value=1, step=1, value=int(row_to_edit["Ram"]), key="edit_ram")

                        # Penyimpanan
                        penyimpanan_parts = row_to_edit["Penyimpanan"].split()
                       
                        try:
                            penyimpanan_gb_val = int(penyimpanan_parts[0])
                        except (ValueError, IndexError):
                            penyimpanan_gb_val = 0
                        
                        penyimpanan_tipe_val = "SSD" 
                        if len(penyimpanan_parts) > 2:
                            penyimpanan_tipe_val = penyimpanan_parts[2]

                        penyimpanan_gb = st.number_input("Penyimpanan (GB)", min_value=64, step=64, value=penyimpanan_gb_val, key="edit_penyimpanan_gb")
                        penyimpanan_tipe_options = ["SSD", "HDD", "eMMC"]
                        penyimpanan_tipe_idx = penyimpanan_tipe_options.index(penyimpanan_tipe_val) if penyimpanan_tipe_val in penyimpanan_tipe_options else 0
                        penyimpanan_tipe = st.selectbox("Jenis Penyimpanan", penyimpanan_tipe_options, index=penyimpanan_tipe_idx, key="edit_penyimpanan_tipe")

                    with col2:
                        vga = st.text_input("VGA", value=row_to_edit["Vga"], key="edit_vga")

                        # Layar
                        try:
                            layar_inch_val = float(str(row_to_edit["Layar"]).replace('"', ''))
                        except ValueError:
                            layar_inch_val = 10.0 # Default or handle error
                        layar_inch = st.number_input("Ukuran Layar (Inch)", min_value=10.0, max_value=20.0, step=0.1, format="%.1f", value=layar_inch_val, key="edit_layar_float")

                        # Baterai
                        try:
                            baterai_wh_val = int(str(row_to_edit["Baterai"]).replace(" Wh", ""))
                        except ValueError:
                            baterai_wh_val = 10 # Default or handle error
                        baterai_wh = st.number_input("Baterai (Wh)", min_value=10, step=1, value=baterai_wh_val, key="edit_baterai_wh")

                        # OS dan Harga
                        os_tipe_options = ["Windows", "MacOS", "ChromeOS"]
                        os_tipe_idx = os_tipe_options.index(row_to_edit["Sistem Operasi"]) if row_to_edit["Sistem Operasi"] in os_tipe_options else 0
                        os_tipe = st.selectbox("Sistem Operasi", os_tipe_options, index=os_tipe_idx, key="edit_os_tipe")
                        harga = st.number_input("Harga (Rp)", min_value=800_000, step=100_000, value=int(row_to_edit["Harga"]), key="edit_harga")

                        submit_edit = st.form_submit_button("Update Data Laptop")

                    if submit_edit:
                        if not merk or not tipe or not prosesor or not vga or not os_tipe:
                            st.error("⚠️ Merk, Tipe, Prosesor, VGA, dan Sistem Operasi tidak boleh kosong.")
                        elif ram <= 0 or penyimpanan_gb <= 0 or layar_inch <= 0 or baterai_wh <= 0 or harga <= 0:
                            st.error("⚠️ RAM, Penyimpanan, Layar, Baterai, dan Harga harus lebih dari nol.")
                        else:
                            updated_laptop_data = {
                                "Merk": merk, "Tipe": tipe, "Prosesor": prosesor, "Ram": ram,
                                "Penyimpanan": f"{penyimpanan_gb} GB {penyimpanan_tipe}",
                                "Vga": vga, "Layar": f'{layar_inch}"', "Baterai": f"{baterai_wh} Wh",
                                "Sistem Operasi": os_tipe, "Harga": harga
                            }
                            update_laptop_row(id_to_edit, updated_laptop_data)
                            st.session_state["tambah_sukses"] = f"✅ Data laptop ID {id_to_edit} berhasil diperbarui."
                            st.rerun()
            else:
                st.warning("❗ Belum ada data laptop untuk diedit.")

            st.markdown("---")
            if not df_laptop.empty:
                id_to_delete = st.selectbox("Pilih ID untuk Hapus", df_laptop["Id"], key="delete_id_select")
                if st.button("🗑️ Hapus Data Laptop"):
                    delete_laptop_row(id_to_delete)
                    st.session_state["hapus_sukses"] = f"✅ Data laptop dengan ID {id_to_delete} berhasil dihapus."
                    st.rerun()

# =========== MENU : KRITERIA ===============
    elif menu == "Kriteria":
        df_kriteria = load_kriteria()

        # Reset pairwise_df jika jumlah atau nama kriteria berubah
        if "pairwise_df" in st.session_state:
            current_names = df_kriteria["Nama"].tolist()
            if set(st.session_state["pairwise_df"].index) != set(current_names):
                st.session_state.pop("pairwise_df")

        # ---------- HEADER + TABEL ----------
        st.subheader("📋 Daftar Kriteria Seleksi")
        st.dataframe(df_kriteria.set_index("Id"),
                    use_container_width=True, hide_index=False)

        # ---------- PDF Kriteria ----------
        st.markdown("### 📄 Cetak / Download Kriteria")
        if st.button("📄 Buat PDF Kriteria"):
            pdf_k = PDF(title="Daftar Bobot Kriteria")
            pdf_k.set_auto_page_break(auto=True, margin=15)
            pdf_k.add_page()
            pdf_k.make_table_kriteria(df_kriteria.copy())
            pdf_k.add_signature_block()
            st.session_state["pdf_bytes_kriteria"] = (
                pdf_k.output(dest="S").encode("latin-1", "replace")
            )
            st.success("✅ PDF Kriteria berhasil dibuat!")

        if st.session_state.get("pdf_bytes_kriteria"):
            st.download_button("⬇️ Download PDF Kriteria",
                            st.session_state["pdf_bytes_kriteria"],
                            file_name="kriteria.pdf",
                            mime="application/pdf")
            
        if st.session_state.get("pdf_bytes_kriteria"):
            cetak_pdf_button(st.session_state["pdf_bytes_kriteria"])

        # -----------------------------------------------------------
        # 📊 PAIR‑WISE & CONSISTENCY RATIO
        # -----------------------------------------------------------
        with st.expander("📊 Perbandingan Berpasangan & Konsistensi (CR)"):
            if df_kriteria.empty:
                st.info("Tambahkan kriteria terlebih dahulu.")
                
            elif (df_kriteria["Bobot"] <= 0).any():
                st.warning("Semua bobot harus > 0 sebelum menghitung CR.")
            else:
                # Inisialisasi default pairwise jika belum ada
                k_list = df_kriteria["Nama"].tolist()
                if "pairwise_df" not in st.session_state:
                    st.session_state["pairwise_df"] = default_pairwise(
                        df_kriteria["Bobot"].values, k_list
                    )

                pair_df = st.session_state["pairwise_df"]
                with st.form("form_cr"):
                    edit_df = st.data_editor(
                        pair_df.copy(),
                        num_rows="fixed",
                        use_container_width=True
                    )
                    col1, col2, col3, col4, col5 = st.columns(5)
                    do_hitung = col1.form_submit_button("Hitung CR", type="primary")
                    do_reset  = col5.form_submit_button("Reset Matriks")

                # RESET
                if do_reset:
                    st.session_state["pairwise_df"] = default_pairwise(
                        df_kriteria["Bobot"].values, k_list
                    )
                    st.session_state.pop("cr_pdf_data", None)
                    st.success("Matriks di-reset.")
                    st.rerun()

                # HITUNG
                if do_hitung:
                    if (edit_df.values <= 0).any():
                        st.error("Semua elemen matriks harus positif (> 0).")
                    else:
                    
                        original = pair_df.copy()

                        # Simetrisasi reciprocal
                        n = len(k_list)
                        for i in range(n):
                            for j in range(i+1, n):
                                
                                if edit_df.iat[i, j] != 0:
                                    edit_df.iat[j, i] = round(1.0 / edit_df.iat[i, j], 4)
                                else:
                                    edit_df.iat[j, i] = 0 

                        # Simpan ke session
                        st.session_state["pairwise_df"] = edit_df.copy()

                        # Cek perubahan dan tampilkan sesuai kondisi
                        if edit_df.equals(original):
                            st.info("Belum ada perubahan manual—tabel tetap simetris.")
                        else:
                            st.success("Matriks disimetrisasi dan diperbarui:")
                            st.markdown("#### Matriks Setelah Simetrisasi")
                            st.dataframe(edit_df, use_container_width=True)

                        # Hitung CR
                        try:
                            M = edit_df.values.astype(float)
                            lam, ci, cr, w_eig = compute_cr(M)
                            ci, cr = abs(ci), abs(cr)

                            st.session_state["cr_pdf_data"] = {
                                "matrix": edit_df.copy(),
                                "lam": lam, "ci": ci, "cr": cr,
                                "w_eig": w_eig
                            }
                        except Exception as e:
                            st.error(f"Error perhitungan: {e}")

                # TAMPILKAN HASIL CR & PDF (jika sudah dihitung)
                if st.session_state.get("cr_pdf_data"):
                    data = st.session_state["cr_pdf_data"]

                    st.markdown("#### Hasil Konsistensi")
                    st.markdown(f"""
                    • \$ \lambda_{max} \$ = **{data['lam']:.3f}**  
                    • CI     = **{data['ci']:.3f}**  
                    • CR     = **{data['cr']:.3f}**
                    """, unsafe_allow_html=True)

                    if data["cr"] < 0.10:
                        st.success("✅ Konsisten (CR < 0,10).")
                    else :
                        st.error("CR ≥ 0,10 — perbaiki matriks.")

                    if st.button("❇️ Terapkan Bobot Eigenvector", key="apply_eigen_button"):
                        if st.session_state.get("cr_pdf_data"): 
                            try:
                                data = st.session_state["cr_pdf_data"]
                                for i, nama_kriteria in enumerate(k_list):
                                    df_kriteria.loc[df_kriteria["Nama"] == nama_kriteria, "Bobot"] = data["w_eig"][i].round(4)
                                
                                save_kriteria(df_kriteria)
                                st.success("✅ Bobot berhasil diterapkan dan disimpan.")
                                st.rerun() 
                            except Exception as e:
                                st.error(f"⚠️ Terjadi kesalahan saat menerapkan atau menyimpan bobot: {e}")
                        else:
                            st.warning("⚠️ Harap hitung konsistensi terlebih dahulu sebelum menerapkan bobot.")


            # ---------- PDF CR ----------
            st.markdown("### 📄 Cetak / Download Tabel Pair-Wise & CR")
            if st.session_state.get("cr_pdf_data"):
                if st.button("📄 Buat PDF CR"):
                    data = st.session_state["cr_pdf_data"]
                    try:
                        pdf_cr = PDF(title="Matriks Pair-Wise & CR")
                        pdf_cr.set_auto_page_break(auto=True, margin=15)
                        pdf_cr.add_page()

                        matrix_clean = data["matrix"].copy()
                        matrix_clean.columns = [str(c).replace("‑", "-") for c in matrix_clean.columns]
                        matrix_clean.index = [str(i).replace("‑", "-") for i in matrix_clean.index]

                        pdf_cr.make_table_cr(matrix_clean)
                        pdf_cr.ln(4)
                        pdf_cr.set_font("Arial", "", 11)

                        # Gunakan teks ASCII-friendly
                        info = f"lambda_max = {data['lam']:.3f}   CI = {data['ci']:.3f}   CR = {data['cr']:.3f}"
                        pdf_cr.cell(0, 6, info, ln=True, align="C")
                        pdf_cr.add_signature_block()

                        # Encode dengan aman
                        pdf_bytes = pdf_cr.output(dest="S").encode("latin-1", "replace")
                        st.session_state["pdf_bytes_cr"] = pdf_bytes
                        st.success("✅ PDF Tabel CR berhasil dibuat !")

                    except Exception as e:
                        st.error(f"Gagal membuat PDF CR: {e}")

                if st.session_state.get("pdf_bytes_cr"):
                    st.download_button("⬇️ Download PDF CR",
                                    st.session_state["pdf_bytes_cr"],
                                    file_name="tabel_cr.pdf",
                                    mime="application/pdf")
                    
                    if st.session_state.get("pdf_bytes_cr"):
                        cetak_pdf_button(st.session_state["pdf_bytes_cr"])
            else:
                st.warning("❗ Belum ada data CR. Silakan hitung CR terlebih dahulu.")
                
        st.markdown("---")

        col1, col2 = st.columns(2)

# =========== K O L O M 1 : Tambah Kriteria ===============
        with col1:
            st.subheader("➕ Tambah Kriteria")
            kriteria_master = [
                "Harga", "Ram", "Prosesor", "Penyimpanan",
                "Vga", "Layar", "Baterai", "Sistem Operasi"
            ]
            kriteria_tersedia = [
                k for k in kriteria_master
                if k not in df_kriteria["Nama"].values
            ]

            if kriteria_tersedia:
                with st.form("form_tambah_kriteria"):
                    nama_bar = st.selectbox("Pilih Kriteria", kriteria_tersedia, key="add_kriteria_name")
                    bobot_bar = st.number_input(
                        "Bobot (0 – 1)",
                        min_value=0.0, max_value=1.0, step=0.01, key="add_kriteria_bobot"
                    )
                    simpan_btn = st.form_submit_button("Simpan")

                if simpan_btn:
                    if not nama_bar.strip():
                        st.warning("Nama kriteria tidak boleh kosong.")
                    elif bobot_bar <= 0:
                        st.warning("Bobot harus lebih dari 0.")
                    else:
                        success, msg = add_kriteria_row(nama_bar.title(), bobot_bar)
                        if success:
                            st.success(msg)
                        else:
                            st.warning(msg)
                        st.rerun()
            else:
                st.info("Semua kriteria master sudah ditambahkan.")

# =========== K O L O M 2 : Edit / Hapus Kriteria ===============
        with col2:
            st.subheader("📝 Edit / Hapus Kriteria")
            if df_kriteria.empty:
                st.info("Belum ada kriteria.")
            else:
                pilih = st.selectbox("ID", df_kriteria["Id"], key="edit_kriteria_id")
                baris = df_kriteria[df_kriteria["Id"] == pilih].iloc[0]

                with st.form("form_edit_kriteria"):
                    nama_e = st.text_input("Nama", value=baris["Nama"], key="edit_kriteria_name")
                    bobot_e = st.number_input(
                        "Bobot (0–1)",
                        min_value=0.0,           # batas bawah 0.0
                        max_value=1.0,
                        step=0.01,
                        value=float(baris["Bobot"]), key="edit_kriteria_bobot"
                    )
                    update = st.form_submit_button("Update")

                if update:
                    if not nama_e.strip():
                        st.warning("Nama tidak boleh kosong.")
                    elif bobot_e <= 0:
                        st.warning("Bobot harus lebih dari 0.")
                    else:
                        success, msg = update_kriteria_row(pilih, nama_e.title(), bobot_e)
                        if success:
                            st.success(msg)
                        else:
                            st.warning(msg)
                        st.rerun()

                if st.button("🗑️ Hapus Kriteria", key="delete_kriteria_button"):
                    delete_kriteria_by_id(pilih)
                    st.session_state["hapus_sukses"] = f"✅ Kriteria dengan ID '{pilih}' berhasil dihapus!"       
                    st.rerun()

# =========== ALTERNATIF ===============
    elif menu=="Alternatif":
        dfk=load_kriteria()

        if dfk.empty:
            st.warning("Belum ada kriteria.")
        else:
            st.subheader("📐 Skala Saaty (1-9) - dihitung dari Bobot")
            dfk["Skala (1-9)"]=dfk.Bobot.apply(scale_saaty_from_bobot)
            st.dataframe(dfk.set_index("Id")[["Nama","Bobot","Skala (1-9)"]],
                        use_container_width=True)
            st.caption(
                "Kolom <i>Skala (1-9)</i> dikonversi otomatis dari bobot (0-1). "
                "Nilai inilah yang akan dipakai sebagai skor alternatif "
                "ketika perhitungan AHP (normalisasi otomatis).",
                unsafe_allow_html=True
            )
        
        # ---------- CETAK PDF ALTERNATIF ----------
        st.markdown("### 📄 Cetak / Download Skala Saaty")
        if st.button("📄 Buat PDF Alternatif"):
            pdf_a = PDF(title="Matriks Skala Saaty 1-9")
            pdf_a.set_auto_page_break(auto=True, margin=15)
            pdf_a.add_page()
            pdf_a.make_table_alt(dfk[["Id", "Nama", "Skala (1-9)"]].copy())
            # catatan kecil di tengah
            pdf_a.set_font("Arial", "I", 8)
            pdf_a.ln(4)
            note = (
                "Nilai pada kolom Skala (1-9) dihitung secara otomatis dari bobot 0-1 "
                "berdasarkan skala prioritas. Angka ini berfungsi sebagai representasi "
                "kepentingan relatif setiap kriteria, dan akan digunakan untuk menghitung "
                "skor akhir alternatif secara terstandarisasi dalam metode AHP."
            )

            # lebar teks agar tidak keluar margin
            note_width = 150  # margin kiri+kanan default = 10
            x = (pdf_a.w - note_width) / 2  # posisi X tengah
            pdf_a.set_x(x)
            pdf_a.multi_cell(note_width, 4, note, align="C")

            pdf_a.add_signature_block()
            st.session_state["pdf_bytes_alt"] = (pdf_a.output(dest="S").encode("latin-1", "replace"))
            st.success("✅ PDF Skala Saaty berhasil dibuat !")
                
        if st.session_state.get("pdf_bytes_alt"):
            st.download_button(
                "⬇️ Download PDF Alternatif",
                st.session_state["pdf_bytes_alt"],
                file_name="alternatif_saaty.pdf",
                mime="application/pdf",
            )

            if st.session_state.get("pdf_bytes_alt"):
                cetak_pdf_button(st.session_state["pdf_bytes_alt"])

# =========== LOGIKA MENU SELEKSI ===============
    elif menu == "Seleksi":

        df_laptop = load_laptop_data()
        df_kriteria = load_kriteria()

        if df_laptop.empty or df_kriteria.empty:
            st.warning("❗ Data laptop dan kriteria harus tersedia untuk melakukan seleksi.")
            st.stop()

        st.subheader("🎯 Pilih Brand & Tipe yang Akan Dibandingkan")

        semua_brand = sorted(df_laptop["Merk"].unique())

        # 1) pilih berapa brand
        jml_brand = st.number_input("Berapa brand ingin dibandingkan?", 1, len(semua_brand), 1, key="num_brands_select")

        # 2) pilih brand
        brand_terpilih = st.multiselect(
            "Pilih Brand",
            options=semua_brand,
            default=semua_brand[:min(jml_brand, len(semua_brand))], 
            max_selections=jml_brand,
            key="brand_select",
        )

        # 3) pilih tipe per‑brand
        tipe_dict = {}
        if brand_terpilih:
            with st.form("form_pilih_tipe"):
                for b in brand_terpilih:
                    tipe_opsi = df_laptop[df_laptop["Merk"] == b]["Tipe"].tolist()
                    if not tipe_opsi:
                        st.warning(f"Tidak ada tipe laptop ditemukan untuk brand: {b}")
                        tipe_dict[b] = None # Set to None if no options
                    else:
                        tipe_dict[b] = st.selectbox(f"Pilih tipe untuk {b}", tipe_opsi, key=f"tipe_{b}")
                hitung_btn = st.form_submit_button("Hitung AHP")

            # ---- selesai form; mulai di luar form ----
            if hitung_btn:
                
                selected_laptops_data = []
                for b in brand_terpilih:
                    if tipe_dict[b] is not None:
                        selected_laptops_data.append(df_laptop[(df_laptop["Merk"] == b) & (df_laptop["Tipe"] == tipe_dict[b])])
                
                if not selected_laptops_data:
                    st.warning("Tidak ada laptop yang dipilih untuk perbandingan. Silakan pilih setidaknya satu laptop.")
                    st.stop()

                df_pilih = pd.concat(selected_laptops_data, ignore_index=True)

                # =========== DEFINISI NILAI MAX/MIN dan TIPE KRITERIA  ===============
                max_values = {
                    "Prosesor": 10, "Ram": 10, "Penyimpanan": 10, "Vga": 10,
                    "Layar": 10, "Harga": 38999000, "Baterai": 10, "Sistem Operasi": 10
                }

                min_values = {
                    "Prosesor": 2, "Ram": 3, "Penyimpanan": 2, "Vga": 3,
                    "Layar": 3, "Harga": 2950000, "Baterai": 4, "Sistem Operasi": 4
                }

                kriteria_tipe = {
                    "Prosesor": "benefit", "Ram": "benefit", "Penyimpanan": "benefit", "Vga": "benefit",
                    "Layar": "benefit", "Harga": "cost", "Baterai": "benefit", "Sistem Operasi": "benefit"
                }

                # =========== DICT MAPPING  ===============
                mapping_prosesor = {
                    "AMD A4-9120C": 3, "Apple M1": 7, "Apple M2": 9, "Athlon Silver 3050U": 4,
                    "Celeron N3350": 3, "Celeron N4000": 3, "Celeron N4020": 3, "Celeron N4100": 3,
                    "Celeron N4500": 3, "i3-1115G4": 5, "i3-1125G4": 5, "i3-1215U": 5,
                    "i5-1135G7": 7, "i5-1155G7": 7, "i7-11800H": 9, "i7-1260P": 9,
                    "i7-12700H": 9, "i7-1355U": 9, "i9-11900H": 10, "i9-12900H": 10,
                    "Intel N4000": 3, "Pentium Silver N5030": 4, "Ryzen 5 5500U": 7,
                    "Ryzen 5 5625U": 7, "Ryzen 5 7520U": 7, "Ryzen 7 5800H": 9,
                    "Ryzen 7 6800H": 9
                }

                mapping_ram = {4: 3, 8: 6, 16: 8, 32: 10, 64: 10}

                mapping_penyimpanan = {
                    "128 GB SSD": 5, "256 GB SSD": 5, "512 GB SSD": 7, "1 TB SSD": 9,   
                    "2 TB SSD": 10, "64 GB eMMC": 3, "500 GB HDD": 2, 
                }

                mapping_vga = {
                    "Intel Iris Xe": 4, "Intel UHD": 3, "AMD Radeon": 5, "Radeon R3": 4,
                    "Apple M1 GPU": 6, "Apple M2 GPU": 8, "RTX 3050": 9, "RTX 3060": 9,
                    "RTX 3070": 9, "RTX 3070 Ti": 9, "RTX 3080 ": 10, "RTX A3000": 10,
                    "RTX A5000": 10,
                }

                mapping_layar = {
                    '10.1': 3, '11.6': 3, '13': 3, '13.3': 5, '13.5': 5, '14': 6,
                    '15.6': 8, '16': 9, '16.1': 9, '17': 10,
                }

                # -------- PROSES AHP ----------
               
                bobot_manual = {
                    "Prosesor": 0.1896,
                    "Ram": 0.0701,
                    "Penyimpanan": 0.0701,
                    "Vga": 0.1314,
                    "Layar": 0.1558,
                    "Harga": 0.3831,
                    "Baterai": 0.0, 
                    "Sistem Operasi": 0.0
                }
           
                for kriteria_name, weight_val in bobot_manual.items():
                    if kriteria_name in df_kriteria["Nama"].values:
                        df_kriteria.loc[df_kriteria["Nama"] == kriteria_name, "Bobot"] = weight_val
                    # else:
                    #     st.warning(f"Kriteria '{kriteria_name}' dari bobot manual tidak ditemukan di daftar kriteria. Lewati.")

                df_norm = df_pilih.copy()
               
                # Penanganan Tipe Data dan Ekstraksi Nilai
                for kriteria_nama in df_kriteria["Nama"]:
                    kolom_data = kriteria_nama.title()

                    if kolom_data not in df_norm.columns:
                        st.warning(f"Kolom '{kolom_data}' tidak ditemukan di data laptop yang dipilih. Lewati pra-pemrosesan untuk kriteria ini.")
                        df_norm[kolom_data] = 0 
                        continue
                    
                    # =========== MAPPING IMPLEMENTATION  ===============
                    if kolom_data == "Prosesor":
                        df_norm[kolom_data] = df_norm[kolom_data].astype(str).str.strip().map(mapping_prosesor).fillna(0)
                    elif kolom_data == "Ram":
                        df_norm[kolom_data] = pd.to_numeric(df_norm[kolom_data], errors='coerce').map(mapping_ram).fillna(0)
                    elif kolom_data == "Penyimpanan":
                       
                        df_norm[kolom_data] = df_norm[kolom_data].astype(str).str.replace(' GB ', ' GB ').str.strip().map(mapping_penyimpanan).fillna(0)
                    elif kolom_data == "Vga":
                        df_norm[kolom_data] = df_norm[kolom_data].astype(str).str.strip().map(mapping_vga).fillna(0)
                    elif kolom_data == "Layar":
                        df_norm[kolom_data] = df_norm[kolom_data].astype(str).str.replace('"', '').str.strip().map(mapping_layar).fillna(0)
                    elif kolom_data == "Harga":
                        df_norm[kolom_data] = pd.to_numeric(df_norm[kolom_data], errors='coerce')
                        df_norm[kolom_data].fillna(df_norm[kolom_data].mean() if not df_norm[kolom_data].empty else 0, inplace=True) 
                    elif kolom_data == "Baterai":
              
                        df_norm[kolom_data] = df_norm[kolom_data].astype(str).str.replace(' Wh', '').str.strip()
                        df_norm[kolom_data] = pd.to_numeric(df_norm[kolom_data], errors='coerce').fillna(0)
                    elif kolom_data == "Sistem Operasi":
                        
                        df_norm[kolom_data] = pd.to_numeric(df_norm[kolom_data], errors='coerce').fillna(0)
                    else:
                        
                        df_norm[kolom_data] = pd.to_numeric(df_norm[kolom_data], errors='coerce')
                        df_norm[kolom_data].fillna(df_norm[kolom_data].mean() if not df_norm[kolom_data].empty else 0, inplace=True)

                # Normalisasi berdasarkan tipe kriteria (benefit/cost)
                for kriteria_nama in df_kriteria["Nama"]:
                    kolom_data = kriteria_nama.title()

                    if kolom_data not in df_norm.columns:
                        continue 

                    if kolom_data in kriteria_tipe:
                        if kriteria_tipe[kolom_data] == "benefit":
                            max_global = max_values.get(kolom_data, df_norm[kolom_data].max())
                            if max_global > 0:
                                df_norm[kolom_data] = df_norm[kolom_data] / max_global
                            else:
                                df_norm[kolom_data] = 0
                        elif kriteria_tipe[kolom_data] == "cost":
                            min_global = min_values.get(kolom_data, df_norm[kolom_data].min()) 
                            df_norm[kolom_data] = df_norm[kolom_data].apply(lambda x: min_global / x if x != 0 else 0)
                        else:
                            st.warning(f"Tipe kriteria tidak dikenal untuk '{kolom_data}'. Lewati normalisasi.")
                    else:
                        st.warning(f"Tipe kriteria tidak didefinisikan untuk '{kolom_data}'. Lewati normalisasi.")

                # Calculate final score
                df_pilih["Skor"] = df_norm.apply(
                    lambda r: sum(r[k.title()] * df_kriteria.loc[df_kriteria["Nama"] == k, "Bobot"].iloc[0] 
                                  for k in df_kriteria["Nama"] if k.title() in r and not df_kriteria.loc[df_kriteria["Nama"] == k, "Bobot"].empty),
                    axis=1,
                )
                df_hasil = df_pilih.sort_values("Skor", ascending=False).reset_index(drop=True)

                # simpan di session agar bisa dipakai ulang 
                st.session_state["hasil_seleksi"] = df_hasil

                # ---------- tampil & download ----------

        if "hasil_seleksi" in st.session_state:
            df_hasil = st.session_state["hasil_seleksi"]

            df_hasil["Rank"] = df_hasil["Skor"].rank(ascending=False, method="min").astype(int)
            df_hasil = df_hasil.sort_values("Rank")

            st.subheader("📊 Hasil Seleksi Laptop")
            st.dataframe(df_hasil[["Id", "Merk", "Tipe", "Skor", "Rank"]], use_container_width=True, hide_index=True)
            
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if "pdf_bytes_seleksi" not in st.session_state:
                    st.session_state["pdf_bytes_seleksi"] = None

                if st.button("📄 Buat PDF"):
                    pdf = PDF(title="Hasil Perhitungan Skor")
                    
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    pdf.make_table(df_hasil[["Id", "Merk", "Tipe", "Skor", "Rank"]])
                    pdf.add_signature_block()
                    st.session_state["pdf_bytes_seleksi"] = pdf.output(dest="S").encode("latin-1", "replace")
                    st.success("✅ PDF Hasil Seleksi berhasil dibuat!")

                if st.session_state["pdf_bytes_seleksi"]:
                    st.download_button("⬇️ Download PDF",
                                    st.session_state["pdf_bytes_seleksi"],
                                    file_name="laporan_seleksi.pdf",
                                    mime="application/pdf")
                
                if st.session_state.get("pdf_bytes_seleksi"):
                    cetak_pdf_button(st.session_state["pdf_bytes_seleksi"])
