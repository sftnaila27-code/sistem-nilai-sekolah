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

# CSS KUSTOM - BERSIH, RAPI, TANPA TEKS ANEH
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

/* ===== MENU SAMPING ===== */
[data-testid="stSidebar"] {
    background-color: var(--putih);
    background: linear-gradient(180deg, #ffffff 0%, #f8f0fc 100%);
    border-right: 1px solid #f0f0f0;
    padding: 20px 12px !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.03);
}

.sidebar-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--ungu-lembut);
    text-align: left;
    margin-bottom: 25px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(107, 114, 225, 0.05);
    border-radius: 12px;
}

/* Tombol Navigasi */
div.stButton > button {
    width: 100% !important;
    padding: 12px 15px !important;
    margin: 6px 0 !important;
    border-radius: 12px !important;
    border: none !important;
    background: transparent !important;
    color: var(--teks) !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 10px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    background-color: rgba(107, 114, 225, 0.1) !important;
    color: var(--ungu-lembut) !important;
}
.active {
    background: linear-gradient(90deg, var(--ungu-lembut) 0%, #8B5CF6 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(107, 114, 225, 0.2) !important;
}

.divider {
    height: 1px;
    background-color: var(--abu-garis);
    margin: 18px 0 !important;
}

/* Kotak Kartu Samping */
.sidebar-card {
    background: var(--putih);
    padding: 15px !important;
    border-radius: 12px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    margin: 12px 0 !important;
    border: 1px solid #f3f4f6 !important;
}
.sidebar-card h4 {
    margin: 0 0 8px 0 !important;
    color: var(--ungu-lembut);
    font-size: 15px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

/* ====================================== */
/* BAGIAN UTAMA: HAPUS TEKS BERANTAKAN */
/* ====================================== */
div[data-testid="stMarkdownContainer"] > p,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] label,
div.uploadedFile > div:first-child,
div[data-testid="stMarkdown"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
    overflow: hidden !important;
}

/* Tampilkan HANYA tombol upload */
div[data-testid="stFileUploader"] {
    display: block !important;
    visibility: visible !important;
    background: #f9fafb !important;
    border: 1px dashed #ccc !important;
    border-radius: 8px !important;
    padding: 8px !important;
    margin: 0 !important;
    min-height: auto !important;
}
div[data-testid="stFileUploader"] > div:first-child {
    display: block !important;
    visibility: visible !important;
    height: auto !important;
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
#MainMenu, footer, header, .stDeployButton {
    visibility: hidden !important;
    display: none !important;
}
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
        st.error(f"❌ Gagal: {berkas.name}")
        return None

def proses_semua_file(daftar_file):
    semua_data = []
    if not daftar_file: return None
    
    for f in daftar_file:
        hasil = baca_file_format_anda(f)
        if hasil is None: return None
        semua_data.append(hasil)
    
    gabung = pd.concat(semua_data, ignore_index=True)
    
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','Rata-Rata':'Rata-Rata Kelas'})

    gabung['PERINGKAT SEKOLAH'] = gabung['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_sekolah = gabung.sort_values('PERINGKAT SEKOLAH').reset_index(drop=True)

    gabung['PERINGKAT KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_kelas = gabung.sort_values(['KELAS','PERINGKAT KELAS'])

    def buat_unduh():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
        return output.getvalue()

    return gabung, rekap_kelas, peringkat_sekolah, peringkat_kelas, buat_unduh()

# ======================================
# INISIALISASI MENU
# ======================================
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Beranda"

# ======================================
# TAMPILAN UTAMA
# ======================================

# ==== MENU SAMPING ====
with st.sidebar:
    st.markdown('<div class="sidebar-title">🏫 Nilai Sekolah</div>', unsafe_allow_html=True)
    
    # TOMBOL NAVIGASI (DIPERBAIKI, TANPA EROR)
    if st.button("📊 Beranda", key="m1"):
        st.session_state.menu_aktif = "Beranda"
    if st.button("📋 Data Nilai", key="m2"):
        st.session_state.menu_aktif = "Data Nilai"
    if st.button("🏆 Peringkat", key="m3"):
        st.session_state.menu_aktif = "Peringkat"
    if st.button("⚙️ Pengaturan", key="m4"):
        st.session_state.menu_aktif = "Pengaturan"

    # Garis
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Panduan
    st.markdown('<div class="sidebar-card"><h4>📝 Panduan</h4><span>Format: |No|Nama|...|<br>Nama: 7a.xlsx</span></div>', unsafe_allow_html=True)

    # UPLOAD BERKAS - TETAP ADA, BERSIH
    st.markdown('<div class="sidebar-card"><h4>📤 Unggah Berkas</h4>', unsafe_allow_html=True)
    berkas_masuk = st.file_uploader(
        "", 
        type=["xlsx", "txt"], 
        accept_multiple_files=True,
        label_visibility="hidden"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Info
    st.markdown('<div class="sidebar-card"><h4>ℹ️ Info</h4><span>Otomatis hitung rata-rata & peringkat.</span></div>', unsafe_allow_html=True)

# ==== KONTEN UTAMA ====
hasil = proses_semua_file(berkas_masuk)

if st.session_state.menu_aktif == "Beranda":
    st.markdown("""
    <div class="header-banner">
        <h1 style="margin:0; font-size:28px;">📊 Sistem Pengolahan Nilai Siswa</h1>
        <p style="margin:5px 0 0 0; opacity:0.9;">Kelola, hitung, dan rangking nilai sekolah</p>
    </div>
    """, unsafe_allow_html=True)

    if hasil:
        data_mentah, rekap, _, _, _ = hasil
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="card"><div style="color:#6B72E1;">👥 Total Siswa</div><h2>{}</h2></div>'.format(len(data_mentah)), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card"><div style="color:#36C5F0;">🏫 Jumlah Kelas</div><h2>{}</h2></div>'.format(data_mentah['KELAS'].nunique()), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="card"><div style="color:#2ECC71;">📈 Rata-Rata</div><h2>{}</h2></div>'.format(round(data_mentah['Rata-Rata'].mean(),2)), unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="card"><div style="color:#F06292;">🏆 Nilai Tertinggi</div><h2>{}</h2></div>'.format(data_mentah['Rata-Rata'].max()), unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📋 Rekapitulasi Nilai Per Kelas")
        st.dataframe(rekap, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="card" style="text-align:center; padding:50px 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/3201/3201355.png" width="150">
            <h2 style="color:#6B72E1; margin-top:20px;">Selamat Datang</h2>
            <p>Unggah file nilai Anda lewat tombol di samping kiri.</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Data Nilai":
    st.markdown('<div class="header-banner"><h1>📋 Data Lengkap Siswa</h1></div>', unsafe_allow_html=True)
    if hasil:
        data_mentah, _, _, _, _ = hasil
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(data_mentah, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⚠️ Silakan unggah file terlebih dahulu.")

elif st.session_state.menu_aktif == "Peringkat":
    st.markdown('<div class="header-banner"><h1>🏆 Daftar Peringkat Nilai</h1></div>', unsafe_allow_html=True)
    if hasil:
        _, _, peringkat_s, peringkat_k, file_unduh = hasil
        
        tab1, tab2 = st.tabs(["🏆 Peringkat Sekolah", "👥 Peringkat Per Kelas"])
        with tab1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.dataframe(peringkat_s[['PERINGKAT SEKOLAH','KELAS','Nama Siswa','No Induk','Rata-Rata']], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            pilih_kelas = st.selectbox("", sorted(peringkat_k['KELAS'].unique()))
            tampil = peringkat_k[peringkat_k['KELAS'] == pilih_kelas]
            st.dataframe(tampil[['PERINGKAT KELAS','Nama Siswa','No Induk','Rata-Rata']], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.download_button(
            label="📥 Unduh Hasil Excel",
            data=file_unduh,
            file_name="HASIL_OLAH_NILAI_SEKOLAH.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⚠️ Silakan unggah file terlebih dahulu.")

elif st.session_state.menu_aktif == "Pengaturan":
    st.markdown('<div class="header-banner"><h1>⚙️ Pengaturan Aplikasi</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><p>Pengaturan sistem tampilan.</p></div>', unsafe_allow_html=True)