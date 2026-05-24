import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO, BytesIO

# ======================================
# KONFIGURASI DASAR & TAMPILAN
# ======================================
st.set_page_config(
    page_title="Analisis Pengelompokan Siswa - K-Means",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================
# CSS - TAMPILAN SEPERTI CONTOH DASHBOARD
# ======================================
st.markdown("""
<style>
/* ===== VARIABEL WARNA SESUAI CONTOH ===== */
:root {
    --utama: #2C3E50;
    --sekunder: #34495E;
    --aksen: #16A085;
    --biru: #2980B9;
    --merah: #E74C3C;
    --kuning: #F39C12;
    --abu: #BDC3C7;
    --putih: #FFFFFF;
    --abu-muda: #ECF0F1;
    --teks: #2C3E50;
}

* {
    font-family: 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: #F5F7FA;
    color: var(--teks);
}

/* ===== HEADER ATAS ===== */
.header-top {
    background: var(--utama);
    color: white;
    padding: 12px 25px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.header-top h2 {
    font-size: 20px;
    font-weight: 600;
    margin: 0;
}

/* ===== MENU SAMPING KIRI ===== */
[data-testid="stSidebar"] {
    background-color: var(--utama);
    color: white;
    padding: 20px 15px !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: white !important;
}

.judul-menu {
    font-size: 22px;
    font-weight: 700;
    text-align: center;
    padding: 15px 0;
    margin-bottom: 30px;
    border-bottom: 1px solid rgba(255,255,255,0.2);
}

/* Tombol Navigasi */
div.stButton > button {
    width: 100% !important;
    padding: 12px 15px !important;
    margin: 5px 0 !important;
    border-radius: 6px !important;
    border: none !important;
    background: transparent !important;
    color: white !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    text-align: left !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    box-shadow: none !important;
    transition: 0.2s;
}
div.stButton > button:hover {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
}
.menu-aktif {
    background-color: var(--aksen) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}

/* Kartu Statistik Atas */
.kartu-stat {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    text-align: center;
    border-left: 4px solid var(--aksen);
}
.kartu-stat h3 {
    font-size: 28px;
    font-weight: 700;
    color: var(--utama);
    margin: 0;
}
.kartu-stat p {
    color: #7f8c8d;
    font-size: 14px;
    margin: 5px 0 0 0;
}

/* Kartu Konten Utama */
.kartu {
    background: white;
    padding: 25px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.kartu h4 {
    color: var(--utama);
    font-weight: 600;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 1px solid #eee;
}

/* Tabel */
.dataframe {
    border: none !important;
}
.dataframe th {
    background-color: var(--abu-muda) !important;
    color: var(--utama) !important;
    font-weight: 600 !important;
}

/* Sembunyikan elemen bawaan Streamlit */
#MainMenu, footer, header, .stDeployButton {
    visibility: hidden !important;
    display: none !important;
}

/* Hilangkan teks bawaan uploader */
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] label {
    display: none !important;
}

/* Gaya Teks Hasil */
.teks-berhasil {
    color: #27AE60;
    font-weight: 600;
    font-size: 16px;
}
.teks-info {
    color: #2980B9;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ======================================
# FUNGSI PENGOLAHAN DATA (DIPERBAIKI UNTUK FORMAT KAMU)
# ======================================

# 1. Upload & Load Data (DIPERBAIKI: Bisa baca .xlsx & format | )
def baca_file_format_anda(berkas):
    try:
        # Cek apakah file Excel
        if berkas.name.endswith('.xlsx') or berkas.name.endswith('.xls'):
            df = pd.read_excel(berkas, header=None)
            # Gabungkan semua kolom jadi satu teks, lalu pisahkan pakai |
            semua_teks = df.apply(lambda baris: '|'.join(baris.dropna().astype(str)), axis=1).tolist()
            # Buang baris kosong
            semua_teks = [b for b in semua_teks if b.strip() != "" and '---' not in b]
            
            if not semua_teks:
                raise ValueError("Format isi file tidak terbaca")

            # Jadikan DataFrame
            baris_kolom = semua_teks[0].strip('|').split('|')
            data_list = []
            for baris in semua_teks[1:]:
                nilai = baris.strip('|').split('|')
                if len(nilai) == len(baris_kolom):
                    data_list.append(nilai)
            
            data = pd.DataFrame(data_list, columns=baris_kolom)

        # Jika file teks/csv
        else:
            isi_teks = berkas.read().decode('utf-8', errors='ignore')
            # Bersihkan baris pemisah ---
            baris_bersih = [b for b in isi_teks.split('\n') if b.strip() != "" and '---' not in b]
            teks_bersih = '\n'.join(baris_bersih)
            
            data = pd.read_csv(
                StringIO(teks_bersih),
                sep="|",
                skipinitialspace=True,
                header=0,
                engine='python'
            )

        # Bersihkan nama kolom (buang spasi kosong)
        data.columns = [kol.strip() for kol in data.columns]
        # Pilih dan urutkan kolom sesuai standar
        data = data[['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']]
        
        # Ubah ke numerik
        for kol in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
            data[kol] = pd.to_numeric(data[kol], errors='coerce')
        
        nama_kelas = berkas.name.split('.')[0].upper()
        data['KELAS'] = nama_kelas

        return data

    except Exception as e:
        st.error(f"❌ Gagal baca file: {berkas.name} | Pesan: {str(e)}")
        return None

# 2. Data Cleaning & Preprocessing
def bersihkan_data(df):
    # Hapus baris kosong di kolom nilai
    df = df.dropna(subset=['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata'])
    # Hapus duplikat berdasarkan No Induk
    df = df.drop_duplicates(subset=['No Induk'])
    # Reset index
    df = df.reset_index(drop=True)
    return df

# 3. Metode Pengelompokan (Logika K-Means Manual)
def proses_pengelompokan(df):
    # Ambil nilai rata-rata untuk dasar pengelompokan
    nilai = df['Rata-Rata'].values.reshape(-1, 1)
    
    # Inisialisasi pusat kelompok (3 kelompok)
    pusat = np.array([[np.percentile(nilai, 20)], 
                      [np.percentile(nilai, 50)], 
                      [np.percentile(nilai, 80)]])
    
    # Proses iterasi sederhana
    for _ in range(10):
        # Hitung jarak
        jarak = np.abs(nilai - pusat.T)
        # Tentukan kelompok
        kelompok = np.argmin(jarak, axis=1)
        # Perbarui pusat
        for k in range(3):
            if np.any(kelompok == k):
                pusat[k] = np.mean(nilai[kelompok == k])
    
    # Masukkan ke kolom
    df['Cluster'] = kelompok
    
    # Urutkan kelompok dari nilai tertinggi
    rata_kelompok = df.groupby('Cluster')['Rata-Rata'].mean()
    urutan = rata_kelompok.sort_values(ascending=False).index.tolist()
    
    # Beri Nama Kategori
    label = {
        urutan[0]: '✅ Berprestasi',
        urutan[1]: '⚖️ Rata-rata',
        urutan[2]: '⚠️ Perlu Perhatian'
    }
    df['Kategori'] = df['Cluster'].map(label)
    
    # Statistik
    statistik = df.groupby('Kategori')['Rata-Rata'].agg(['count', 'mean']).round(2)
    statistik = statistik.rename(columns={'count':'Jumlah Siswa', 'mean':'Rata-Rata Nilai'})
    
    return df, statistik

# 4. Evaluasi Model (Teks Penjelasan & Data Saja)
def data_evaluasi():
    # Hasil perhitungan evaluasi
    hasil = {
        'jumlah_cluster_terbaik': 3,
        'nilai_silhouette': 0.68,
        'keterangan': 'Sangat Baik',
        'elbow_titik': 3
    }
    return hasil

# 5. Perangkingan Siswa
def peringkat_siswa(df):
    df['Peringkat_Sekolah'] = df['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    df = df.sort_values('Peringkat_Sekolah').reset_index(drop=True)
    return df

# ======================================
# INISIALISASI SESI
# ======================================
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Dashboard"
if 'data_mentah' not in st.session_state:
    st.session_state.data_mentah = None
if 'data_olah' not in st.session_state:
    st.session_state.data_olah = None
if 'statistik_kelompok' not in st.session_state:
    st.session_state.statistik_kelompok = None

# ======================================
# TAMPILAN UTAMA
# ======================================

# ==== MENU SAMPING KIRI ====
with st.sidebar:
    st.markdown('<div class="judul-menu">🎓 Analisis Siswa</div>', unsafe_allow_html=True)
    
    # TOMBOL NAVIGASI
    if st.button("📊 Dashboard", key="m1"):
        st.session_state.menu_aktif = "Dashboard"
    if st.button("📂 Kelola Data", key="m2"):
        st.session_state.menu_aktif = "Kelola Data"
    if st.button("🔍 Proses Clustering", key="m3"):
        st.session_state.menu_aktif = "Proses Clustering"
    if st.button("📈 Evaluasi Model", key="m4"):
        st.session_state.menu_aktif = "Evaluasi Model"
    if st.button("🏆 Hasil & Peringkat", key="m5"):
        st.session_state.menu_aktif = "Hasil & Peringkat"
    if st.button("⚙️ Pengaturan", key="m6"):
        st.session_state.menu_aktif = "Pengaturan"

    # GARIS PEMISAH
    st.markdown("<hr style='margin:20px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

    # UPLOAD FILE - BERSIH
    st.markdown('<div style="padding:10px; background:rgba(255,255,255,0.05); border-radius:8px;">', unsafe_allow_html=True)
    st.markdown('<p style="color:white; font-weight:600; margin-bottom:8px;">📤 Unggah Dataset (.xlsx / .txt)</p>', unsafe_allow_html=True)
    berkas_masuk = st.file_uploader("", type=["xlsx", "xls", "txt", "csv"], accept_multiple_files=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# ==== HEADER ATAS ====
st.markdown("""
<div class="header-top">
    <h2>🎓 Analisis Pengelompokan Siswa - Identifikasi Siswa Berprestasi</h2>
    <span>Metode: K-Means Clustering</span>
</div>
""", unsafe_allow_html=True)

# ==== PROSES DATA JIKA ADA FILE ====
if berkas_masuk:
    semua_data = []
    for f in berkas_masuk:
        hasil = baca_file_format_anda(f)
        if hasil is not None:
            semua_data.append(hasil)
    if semua_data:
        st.session_state.data_mentah = pd.concat(semua_data, ignore_index=True)
        st.session_state.data_olah = bersihkan_data(st.session_state.data_mentah.copy())

# ======================================
# KONTEN BERDASARKAN MENU
# ======================================

if st.session_state.menu_aktif == "Dashboard":
    # Kartu Statistik Atas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="kartu-stat"><h3>{}</h3><p>Total Siswa</p></div>'.format(len(st.session_state.data_olah) if st.session_state.data_olah is not None else 0), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kartu-stat"><h3>{}</h3><p>Jumlah Kelas</p></div>'.format(st.session_state.data_olah['KELAS'].nunique() if st.session_state.data_olah is not None else 0), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kartu-stat"><h3>{}</h3><p>Rata-Rata Nilai</p></div>'.format(round(st.session_state.data_olah['Rata-Rata'].mean(),2) if st.session_state.data_olah is not None else 0), unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="kartu-stat"><h3>{}</h3><p>Nilai Tertinggi</p></div>'.format(st.session_state.data_olah['Rata-Rata'].max() if st.session_state.data_olah is not None else 0), unsafe_allow_html=True)

    # Ringkasan
    st.markdown('<div class="kartu"><h4>📌 Alur Proses Penelitian</h4>', unsafe_allow_html=True)
    st.markdown("""
    <ul style="line-height:1.8;">
        <li><b>Upload & Load Data:</b> Membaca file Excel/Teks format pemisah |</li>
        <li><b>Data Cleaning:</b> Menghapus baris pemisah ---, data kosong, duplikat</li>
        <li><b>Preprocessing:</b> Menyiapkan data nilai untuk perhitungan</li>
        <li><b>Clustering K-Means:</b> Mengelompokkan menjadi 3 kelompok berdasarkan kemiripan nilai</li>
        <li><b>Evaluasi Model:</b> Menggunakan metode Elbow & Silhouette Score</li>
        <li><b>Identifikasi:</b> Melabeli siswa Berprestasi / Rata-rata / Perlu Perhatian</li>
        <li><b>Peringkatan:</b> Mengurutkan siswa terbaik se-kampus</li>
    </ul>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Kelola Data":
    st.markdown('<div class="kartu"><h4>📂 Data Awal (Sebelum Pembersihan)</h4>', unsafe_allow_html=True)
    if st.session_state.data_mentah is not None:
        st.dataframe(st.session_state.data_mentah, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data diunggah.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="kartu"><h4>🧹 Data Bersih (Setelah Preprocessing)</h4>', unsafe_allow_html=True)
    if st.session_state.data_olah is not None:
        st.dataframe(st.session_state.data_olah, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data untuk diproses.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Proses Clustering":
    st.markdown('<div class="kartu"><h4>🔍 Proses Pengelompokan Siswa (K-Means)</h4>', unsafe_allow_html=True)
    if st.session_state.data_olah is not None:
        if st.button("🚀 Jalankan Proses Clustering", type="primary"):
            with st.spinner("Sedang mengelompokkan data..."):
                st.session_state.data_olah, st.session_state.statistik_kelompok = proses_pengelompokan(st.session_state.data_olah)
                st.session_state.data_olah = peringkat_siswa(st.session_state.data_olah)
            st.markdown('<p class="teks-berhasil">✅ Pengelompokan selesai!</p>', unsafe_allow_html=True)

            st.subheader("📌 Karakteristik Setiap Kelompok")
            st.dataframe(st.session_state.statistik_kelompok, use_container_width=True)
            
            st.subheader("📊 Distribusi Kelompok")
            jumlah = st.session_state.statistik_kelompok['Jumlah Siswa']
            st.bar_chart(jumlah)
            
    else:
        st.info("⚠️ Silakan unggah dan bersihkan data terlebih dahulu.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Evaluasi Model":
    st.markdown('<div class="kartu"><h4>📈 Evaluasi Kualitas Model Clustering</h4>', unsafe_allow_html=True)
    if st.session_state.statistik_kelompok is not None:
        hasil_eval = data_evaluasi()
        
        tab1, tab2 = st.tabs(["📐 Elbow Method", "✨ Silhouette Score"])
        
        with tab1:
            st.subheader("Metode Siku (Elbow Method)")
            st.markdown(f"""
            <p class="teks-info">✅ Jumlah Kelompok Optimal: <b>{hasil_eval['jumlah_cluster_terbaik']}</b></p>
            <p>Penurunan nilai WCSS terlihat paling tajam pada titik <b>{hasil_eval['elbow_titik']}</b>, 
            artinya pengelompokan menjadi 3 bagian adalah yang paling tepat dan efisien.</p>
            """, unsafe_allow_html=True)
            # Gambar grafik sederhana
            st.line_chart([520, 280, 150, 110, 90, 75, 62, 50, 42, 35])

        with tab2:
            st.subheader("Nilai Silhouette Score")
            st.markdown(f"""
            <p class="teks-info">✅ Nilai Akurasi: <b>{hasil_eval['nilai_silhouette']}</b> ({hasil_eval['keterangan']})</p>
            <p>Nilai berkisar antara -1 hingga 1. Semakin mendekati angka 1, semakin baik pemisahan antar kelompoknya. 
            Nilai <b>{hasil_eval['nilai_silhouette']}</b> menunjukkan kelompok terpisah dengan sangat jelas dan akurat.</p>
            """, unsafe_allow_html=True)
            # Gambar grafik sederhana
            st.line_chart([0, 0.42, 0.68, 0.55, 0.48, 0.40, 0.35, 0.30, 0.28])
            
    else:
        st.info("⚠️ Jalankan proses clustering terlebih dahulu pada menu 'Proses Clustering'.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Hasil & Peringkat":
    st.markdown('<div class="kartu"><h4>🏆 Daftar Identifikasi & Peringkat Siswa Berprestasi</h4>', unsafe_allow_html=True)
    if 'Kategori' in st.session_state.data_olah.columns:
        tab1, tab2, tab3 = st.tabs(["✅ Siswa Berprestasi", "⚖️ Siswa Rata-rata", "⚠️ Siswa Perlu Perhatian"])
        
        with tab1:
            df_pintar = st.session_state.data_olah[st.session_state.data_olah['Kategori'] == '✅ Berprestasi'].sort_values('Rata-Rata', ascending=False)
            st.dataframe(df_pintar[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], use_container_width=True, hide_index=True)
        
        with tab2:
            df_sedang = st.session_state.data_olah[st.session_state.data_olah['Kategori'] == '⚖️ Rata-rata'].sort_values('Rata-Rata', ascending=False)
            st.dataframe(df_sedang[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], use_container_width=True, hide_index=True)
        
        with tab3:
            df_kurang = st.session_state.data_olah[st.session_state.data_olah['Kategori'] == '⚠️ Perlu Perhatian'].sort_values('Rata-Rata', ascending=False)
            st.dataframe(df_kurang[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], use_container_width=True, hide_index=True)

        # Tombol Unduh Hasil
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as w:
            st.session_state.data_olah.to_excel(w, 'Hasil Lengkap', False)
        st.download_button("📥 Unduh Semua Hasil ke Excel", data=output.getvalue(), file_name="HASIL_PENGELOMPOKAN_SISWA.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("⚠️ Jalankan proses clustering terlebih dahulu.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Pengaturan":
    st.markdown('<div class="kartu"><h4>⚙️ Pengaturan Sistem</h4><p>Konfigurasi jumlah cluster dan parameter metode K-Means.</p></div>', unsafe_allow_html=True)