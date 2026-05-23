import streamlit as st
import pandas as pd
from io import StringIO, BytesIO

# ======================================
# KONFIGURASI & TEMA TAMPILAN
# ======================================
st.set_page_config(
    page_title="Sistem Nilai Sekolah",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS KUSTOM - Navigasi samping diperbaiki & lebih rapi
st.markdown("""
<style>
/* ===== DASAR & WARNA ===== */
:root {
    --ungu-lembut: #6B72E1;
    --biru-lembut: #36C5F0;
    --pink-lembut: #F06292;
    --hijau-lembut: #2ECC71;
    --kuning-lembut: #F1C40F;
    --abu-muda: #F8F9FC;
    --putih: #FFFFFF;
    --teks: #374151;
    --abu-garis: #E5E7EB;
}

* {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
    color: var(--teks);
}

/* ===== MENU SAMPING - DIPERBAIKI & DIRAPIHKAN ===== */
[data-testid="stSidebar"] {
    background-color: var(--putih);
    background: linear-gradient(180deg, #ffffff 0%, #f8f0fc 100%);
    border-right: 1px solid #f0f0f0;
    padding: 25px 15px !important;
}

/* Judul Utama Sidebar */
.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--ungu-lembut);
    text-align: left;
    margin-bottom: 35px;
    padding-left: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Item Menu Navigasi */
.nav-item {
    padding: 12px 15px;
    margin: 8px 0;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--teks);
    text-decoration: none;
    font-size: 15px;
}
.nav-item:hover {
    background-color: rgba(107, 114, 225, 0.1);
    color: var(--ungu-lembut);
}
.nav-item.active {
    background: linear-gradient(90deg, var(--ungu-lembut) 0%, #8B5CF6 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(107, 114, 225, 0.2);
}

/* Pembatas Garis */
.divider {
    height: 1px;
    background-color: var(--abu-garis);
    margin: 20px 0;
}

/* Kotak Konten di Sidebar */
.sidebar-card {
    background: var(--putih);
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin: 15px 0;
    border: 1px solid #f3f4f6;
}
.sidebar-card h4 {
    margin: 0 0 10px 0;
    color: var(--ungu-lembut);
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ===== KARTU KONTEN UTAMA ===== */
.card {
    background: var(--putih);
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
    border: none;
    margin-bottom: 20px;
}
.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 25px rgba(0,0,0,0.12);
}

.card-header {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
}

/* ===== TOMBOL & KOMPONEN ===== */
.stButton>button {
    background: linear-gradient(90deg, var(--ungu-lembut) 0%, #8B5CF6 100%);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(107, 114, 225, 0.3);
    width: 100%;
}
.stButton>button:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 15px rgba(107, 114, 225, 0.4);
}

.stDownloadButton>button {
    background: linear-gradient(90deg, var(--hijau-lembut) 0%, #10B981 100%);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

/* ===== HEADER UTAMA ===== */
.header-banner {
    background: linear-gradient(90deg, var(--ungu-lembut) 0%, var(--biru-lembut) 100%);
    color: white;
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 30px;
    box-shadow: 0 8px 20px rgba(107, 114, 225, 0.2);
}

/* ===== SEMBUNYIKAN ELEMEN BAWAAAN ===== */
#MainMenu, footer, header {visibility: hidden;}
.css-18e3th9 {padding-top: 1rem;}
.stFileUploader {margin-top: 8px;}
</style>
""", unsafe_allow_html=True)

# ======================================
# FUNGSI PENGOLAHAN DATA (SESUAI FORMAT ANDA)
# ======================================
def baca_file_format_anda(berkas):
    try:
        isi_teks = berkas.read().decode('utf-8', errors='ignore')
        data = pd.read_csv(
            StringIO(isi_teks),
            sep="|",
            skipinitialspace=True,
            header=0,
            engine='python'
        )
        data = data.dropna(axis=1, how='all')
        data.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
        
        for kol in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
            data[kol] = pd.to_numeric(data[kol], errors='coerce')
        
        nama_kelas = berkas.name.split('.')[0].upper()
        data['KELAS'] = nama_kelas
        return data
    except Exception as e:
        st.error(f"❌ Gagal: {berkas.name} | {str(e)}")
        return None

def proses_semua_file(daftar_file):
    semua_data = []
    if not daftar_file: return None
    
    for f in daftar_file:
        hasil = baca_file_format_anda(f)
        if hasil is None: return None
        semua_data.append(hasil)
    
    gabung = pd.concat(semua_data, ignore_index=True)
    
    # Analisis
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','Rata-Rata':'Rata-Rata Kelas'})

    gabung['PERINGKAT SEKOLAH'] = gabung['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_sekolah = gabung.sort_values('PERINGKAT SEKOLAH').reset_index(drop=True)

    gabung['PERINGKAT KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_kelas = gabung.sort_values(['KELAS','PERINGKAT KELAS'])

    # Simpan Excel
    def buat_unduh():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
        return output.getvalue()

    return gabung, rekap_kelas, peringkat_sekolah, peringkat_kelas, buat_unduh()

# ======================================
# TAMPILAN UTAMA
# ======================================

# ==== MENU SAMPING - DIPERBAIKI & DIRAPIHKAN ====
with st.sidebar:
    # Judul
    st.markdown('<div class="sidebar-title">🏫 Nilai Sekolah</div>', unsafe_allow_html=True)
    
    # Menu Navigasi Utama
    st.markdown('<div class="nav-item active">📊 Beranda</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">📋 Data Nilai</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">🏆 Peringkat</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-item">⚙️ Pengaturan</div>', unsafe_allow_html=True)
    
    # Garis Pembatas
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Kotak Panduan
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<h4>📝 Panduan Format</h4>', unsafe_allow_html=True)
    st.markdown("""
    ✅ Gunakan format: `|No|Nama Siswa|...|`
    ✅ Nama file: `7a.xlsx`, `8b.xlsx`
    ✅ Mendukung file `.xlsx` / `.txt`
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Kotak Unggah File - Posisi Rapi
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<h4>📤 Unggah Berkas</h4>', unsafe_allow_html=True)
    berkas_masuk = st.file_uploader(
        "", 
        type=["xlsx", "txt"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Kotak Info Tambahan
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<h4>ℹ️ Informasi</h4>', unsafe_allow_html=True)
    st.markdown("Sistem otomatis menghitung rata-rata & mengurutkan nilai.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==== KONTEN UTAMA ====

# Banner Atas
st.markdown("""
<div class="header-banner">
    <h1 style="margin:0; font-size:28px;">📊 Sistem Pengolahan Nilai Siswa</h1>
    <p style="margin:5px 0 0 0; opacity:0.9;">Kelola, hitung, dan rangking nilai dengan tampilan modern & mudah digunakan</p>
</div>
""", unsafe_allow_html=True)

# Proses Data
hasil = proses_semua_file(berkas_masuk)

if hasil:
    data_mentah, rekap, peringkat_s, peringkat_k, file_unduh = hasil

    # Kartu Ringkasan
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="card"><div class="card-header" style="color:#6B72E1;">👥 Total Siswa</div><h2 style="margin:0;">{}</h2></div>'.format(len(data_mentah)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card"><div class="card-header" style="color:#36C5F0;">🏫 Jumlah Kelas</div><h2 style="margin:0;">{}</h2></div>'.format(data_mentah['KELAS'].nunique()), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card"><div class="card-header" style="color:#2ECC71;">📈 Rata-Rata</div><h2 style="margin:0;">{}</h2></div>'.format(round(data_mentah['Rata-Rata'].mean(),2)), unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="card"><div class="card-header" style="color:#F06292;">🏆 Nilai Tertinggi</div><h2 style="margin:0;">{}</h2></div>'.format(data_mentah['Rata-Rata'].max()), unsafe_allow_html=True)

    # Tab Menu
    tab1, tab2, tab3 = st.tabs(["📊 Rekap Kelas", "🏆 Peringkat Sekolah", "👥 Peringkat Per Kelas"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Tabel Rekapitulasi Nilai")
        st.dataframe(rekap, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏅 Daftar Urutan Nilai Seluruh Sekolah")
        st.dataframe(peringkat_s[['PERINGKAT SEKOLAH','KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        pilih_kelas = st.selectbox("Pilih Kelas", sorted(peringkat_k['KELAS'].unique()))
        tampil = peringkat_k[peringkat_k['KELAS'] == pilih_kelas]
        st.dataframe(tampil[['PERINGKAT KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tombol Unduh
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.download_button(
        label="📥 Unduh Semua Hasil ke Excel",
        data=file_unduh,
        file_name="HASIL_OLAH_NILAI_SEKOLAH.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Tampilan Awal (Kosong tapi indah)
    st.markdown("""
    <div class="card" style="text-align:center; padding:50px 20px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3201/3201355.png" width="150">
        <h2 style="color:#6B72E1; margin-top:20px;">Selamat Datang di Sistem Nilai</h2>
        <p style="font-size:16px; max-width:500px; margin:10px auto;">
            Unggah file nilai Anda lewat menu di samping kiri. 
            Sistem akan otomatis menghitung rata-rata, membuat peringkat, dan menyajikan data dalam tampilan indah.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Kartu Fitur
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <h3 style="color:#6B72E1;">⚡ Cepat & Akurat</h3>
            <p>Hitungan otomatis tanpa salah hitung, langsung diproses sekejap.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <h3 style="color:#36C5F0;">📊 Analisis Lengkap</h3>
            <p>Rekap kelas, peringkat sekolah, dan peringkat di dalam kelas tersedia lengkap.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <h3 style="color:#2ECC71;">📤 Mudah Diunduh</h3>
            <p>Hasil bisa disimpan kembali ke file Excel untuk arsip sekolah.</p>
        </div>
        """, unsafe_allow_html=True)