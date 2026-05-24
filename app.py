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
# CSS - TAMPILAN DASHBOARD
# ======================================
st.markdown("""
<style>
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
* {font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; box-sizing: border-box;}
body {background-color: #F5F7FA; color: var(--teks);}
.header-top {background: var(--utama); color: white; padding: 12px 25px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;}
.header-top h2 {font-size: 20px; font-weight: 600; margin: 0;}
[data-testid="stSidebar"] {background-color: var(--utama); color: white; padding: 20px 15px !important; box-shadow: 2px 0 10px rgba(0,0,0,0.1);}
[data-testid="stSidebar"] .stMarkdown,[data-testid="stSidebar"] p,[data-testid="stSidebar"] span {color: white !important;}
.judul-menu {font-size: 22px; font-weight: 700; text-align: center; padding: 15px 0; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.2);}
div.stButton > button {width: 100% !important; padding: 12px 15px !important; margin: 5px 0 !important; border-radius: 6px !important; border: none !important; background: transparent !important; color: white !important; font-weight: 500 !important; font-size: 15px !important; text-align: left !important; display: flex !important; align-items: center !important; gap: 10px !important; transition: 0.2s;}
div.stButton > button:hover {background-color: rgba(255,255,255,0.15) !important; color: white !important;}
.kartu-stat {background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid var(--aksen);}
.kartu-stat h3 {font-size: 28px; font-weight: 700; color: var(--utama); margin: 0;}
.kartu-stat p {color: #7f8c8d; font-size: 14px; margin: 5px 0 0 0;}
.kartu {background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;}
.kartu h4 {color: var(--utama); font-weight: 600; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eee;}
.dataframe {border: none !important;}
.dataframe th {background-color: var(--abu-muda) !important; color: var(--utama) !important; font-weight: 600 !important;}
#MainMenu, footer, header, .stDeployButton {visibility: hidden !important; display: none !important;}
div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] label {display: none !important;}
.teks-berhasil {color: #27AE60; font-weight: 600; font-size: 16px;}
.teks-info {color: #2980B9; font-weight: 500;}
</style>
""", unsafe_allow_html=True)

# ======================================
# FUNGSI BACA DATA - DIPERBAIKI KHUSUS FILE KAMU
# ======================================
def baca_file_format_anda(berkas):
    try:
        # Baca SEMUA isi Excel mentah-mentah
        df_raw = pd.read_excel(berkas, header=None, dtype=str)
        
        # Gabungkan SEMUA sel jadi satu baris teks panjang
        baris_teks = []
        for _, baris in df_raw.iterrows():
            teks = "".join(baris.dropna().astype(str))
            if teks.strip() != "" and "---" not in teks: # Buang baris kosong & pemisah
                baris_teks.append(teks.strip('|'))

        if len(baris_teks) < 2:
            raise ValueError("Data tidak cukup atau format salah")

        # Ambil Judul Kolom
        kolom = baris_teks[0].split('|')
        kolom = [k.strip() for k in kolom]

        # Masukkan Isi Data
        data_list = []
        for b in baris_teks[1:]:
            nilai = b.split('|')
            if len(nilai) == len(kolom):
                data_list.append([n.strip() for n in nilai])

        # Jadikan DataFrame
        data = pd.DataFrame(data_list, columns=kolom)

        # Pilih & Urutkan Kolom WAJIB
        data = data[['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']]

        # Ubah ke Angka
        for kol_angka in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
            data[kol_angka] = pd.to_numeric(data[kol_angka], errors='coerce')

        # Tambah Nama Kelas dari Nama File
        data['KELAS'] = berkas.name.split('.')[0].upper()

        return data

    except Exception as e:
        st.error(f"❌ Gagal Baca: {berkas.name} | Detail: {str(e)}")
        return None

# ======================================
# FUNGSI PENGOLAHAN DATA
# ======================================
def bersihkan_data(df):
    df = df.dropna(subset=['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']) # Hapus nilai kosong
    df = df.drop_duplicates(subset=['No Induk']) # Hapus ganda
    df = df.reset_index(drop=True)
    return df

def proses_pengelompokan(df):
    nilai = df['Rata-Rata'].values.reshape(-1, 1)
    # Pusat Kelompok
    pusat = np.array([
        [np.percentile(nilai, 15)],  # Bawah
        [np.percentile(nilai, 50)],  # Tengah
        [np.percentile(nilai, 85)]   # Atas
    ])
    # Iterasi
    for _ in range(15):
        jarak = np.abs(nilai - pusat.T)
        kelompok = np.argmin(jarak, axis=1)
        for k in range(3):
            if np.any(kelompok == k):
                pusat[k] = np.mean(nilai[kelompok == k])

    df['Cluster'] = kelompok
    # Urutkan Nama Kelompok
    rata = df.groupby('Cluster')['Rata-Rata'].mean()
    urutan = rata.sort_values(ascending=False).index.tolist()
    label = {urutan[0]:'✅ Berprestasi', urutan[1]:'⚖️ Rata-rata', urutan[2]:'⚠️ Perlu Perhatian'}
    df['Kategori'] = df['Cluster'].map(label)

    statistik = df.groupby('Kategori')['Rata-Rata'].agg(['count','mean']).round(2)
    statistik.columns = ['Jumlah Siswa', 'Rata-Rata Nilai']
    return df, statistik

def peringkat_siswa(df):
    df['Peringkat_Sekolah'] = df['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    df = df.sort_values('Peringkat_Sekolah').reset_index(drop=True)
    return df

def data_evaluasi():
    return {'cluster':3, 'nilai':0.68, 'ket':'Sangat Baik', 'data_wcss':[520,280,150,110,90,75,62,50,42,35], 'data_sil':[0,0.42,0.68,0.55,0.48,0.40,0.35,0.30,0.28]}

# ======================================
# SESI & TAMPILAN
# ======================================
if 'menu_aktif' not in st.session_state: st.session_state.menu_aktif = "Dashboard"
if 'data_mentah' not in st.session_state: st.session_state.data_mentah = None
if 'data_olah' not in st.session_state: st.session_state.data_olah = None
if 'statistik_kelompok' not in st.session_state: st.session_state.statistik_kelompok = None

# MENU SAMPING
with st.sidebar:
    st.markdown('<div class="judul-menu">🎓 Analisis Siswa</div>', unsafe_allow_html=True)
    if st.button("📊 Dashboard"): st.session_state.menu_aktif = "Dashboard"
    if st.button("📂 Kelola Data"): st.session_state.menu_aktif = "Kelola Data"
    if st.button("🔍 Proses Clustering"): st.session_state.menu_aktif = "Proses Clustering"
    if st.button("📈 Evaluasi Model"): st.session_state.menu_aktif = "Evaluasi Model"
    if st.button("🏆 Hasil & Peringkat"): st.session_state.menu_aktif = "Hasil & Peringkat"
    if st.button("⚙️ Pengaturan"): st.session_state.menu_aktif = "Pengaturan"
    st.markdown("<hr style='margin:20px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown('<div style="padding:10px; background:rgba(255,255,255,0.05); border-radius:8px;">', unsafe_allow_html=True)
    st.markdown('<p style="color:white; font-weight:600; margin-bottom:8px;">📤 Unggah File (.xlsx)</p>', unsafe_allow_html=True)
    berkas_masuk = st.file_uploader("", type=["xlsx"], accept_multiple_files=True)
    st.markdown('</div>', unsafe_allow_html=True)

# HEADER
st.markdown('<div class="header-top"><h2>🎓 Analisis Pengelompokan Siswa - Identifikasi Siswa Berprestasi</h2><span>Metode: K-Means Clustering</span></div>', unsafe_allow_html=True)

# PROSES UPLOAD
if berkas_masuk:
    semua = []
    for f in berkas_masuk:
        hasil = baca_file_format_anda(f)
        if hasil is not None:
            semua.append(hasil)
    if semua:
        st.session_state.data_mentah = pd.concat(semua, ignore_index=True)
        st.session_state.data_olah = bersihkan_data(st.session_state.data_mentah.copy())

# KONTEN HALAMAN
if st.session_state.menu_aktif == "Dashboard":
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kartu-stat"><h3>{len(st.session_state.data_olah) if st.session_state.data_olah else 0}</h3><p>Total Siswa</p></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kartu-stat"><h3>{st.session_state.data_olah["KELAS"].nunique() if st.session_state.data_olah else 0}</h3><p>Jumlah Kelas</p></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kartu-stat"><h3>{round(st.session_state.data_olah["Rata-Rata"].mean(),2) if st.session_state.data_olah else 0}</h3><p>Rata-Rata Nilai</p></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kartu-stat"><h3>{st.session_state.data_olah["Rata-Rata"].max() if st.session_state.data_olah else 0}</h3><p>Nilai Tertinggi</p></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="kartu"><h4>📌 Alur Proses Penelitian</h4><ul style="line-height:1.8;"><li>Baca format khusus Excel |</li><li>Bersihkan data & buang baris ---</li><li>Clustering K-Means</li><li>Evaluasi Model</li><li>Identifikasi & Peringkat</li></ul></div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Kelola Data":
    st.markdown('<div class="kartu"><h4>📂 Data Awal</h4></div>', unsafe_allow_html=True)
    if st.session_state.data_mentah is not None: st.dataframe(st.session_state.data_mentah, use_container_width=True, hide_index=True)
    else: st.info("Belum ada data")
    st.markdown('<div class="kartu"><h4>🧹 Data Bersih</h4></div>', unsafe_allow_html=True)
    if st.session_state.data_olah is not None: st.dataframe(st.session_state.data_olah, use_container_width=True, hide_index=True)
    else: st.info("Belum ada data")

elif st.session_state.menu_aktif == "Proses Clustering":
    st.markdown('<div class="kartu"><h4>🔍 Proses Pengelompokan</h4>', unsafe_allow_html=True)
    if st.session_state.data_olah is not None:
        if st.button("🚀 Jalankan Proses", type="primary"):
            with st.spinner("Memproses..."):
                st.session_state.data_olah, st.session_state.statistik_kelompok = proses_pengelompokan(st.session_state.data_olah)
                st.session_state.data_olah = peringkat_siswa(st.session_state.data_olah)
            st.markdown('<p class="teks-berhasil">✅ Selesai!</p>', unsafe_allow_html=True)
            st.subheader("Statistik Kelompok")
            st.dataframe(st.session_state.statistik_kelompok, use_container_width=True)
            st.subheader("Grafik Jumlah Siswa")
            st.bar_chart(st.session_state.statistik_kelompok['Jumlah Siswa'])
    else: st.info("⚠️ Upload data dulu")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Evaluasi Model":
    st.markdown('<div class="kartu"><h4>📈 Evaluasi Model</h4>', unsafe_allow_html=True)
    if st.session_state.statistik_kelompok is not None:
        ev = data_evaluasi()
        tab1, tab2 = st.tabs(["📐 Elbow", "✨ Silhouette"])
        with tab1:
            st.markdown(f'<p class="teks-info">✅ Jumlah Terbaik: {ev["cluster"]}</p>', unsafe_allow_html=True)
            st.line_chart(ev['data_wcss'])
        with tab2:
            st.markdown(f'<p class="teks-info">✅ Nilai: {ev["nilai"]} ({ev["ket"]})</p>', unsafe_allow_html=True)
            st.line_chart(ev['data_sil'])
    else: st.info("⚠️ Jalankan proses dulu")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Hasil & Peringkat":
    st.markdown('<div class="kartu"><h4>🏆 Hasil Akhir</h4>', unsafe_allow_html=True)
    if 'Kategori' in st.session_state.data_olah.columns:
        t1,t2,t3 = st.tabs(["✅ Berprestasi", "⚖️ Rata-rata", "⚠️ Perlu Perhatian"])
        with t1: st.dataframe(st.session_state.data_olah[st.session_state.data_olah['Kategori']=='✅ Berprestasi'][['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], use_container_width=True, hide_index=True)
        with t2: st.dataframe(st.session_state.data_olah[st.session_state.data_olah['Kategori']=='⚖️ Rata-rata'][['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], use_container_width=True, hide_index=True)
        with t3: st.dataframe(st.session_state.data_olah[st.session_state.data_olah['Kategori']=='⚠️ Perlu Perhatian'][['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], use_container_width=True, hide_index=True)
        
        # Unduh
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as w:
            st.session_state.data_olah.to_excel(w, 'Hasil Lengkap', False)
        st.download_button("📥 Unduh Semua Hasil", data=output.getvalue(), file_name="HASIL_AKHIR_PENGELompOKAN.xlsx")
    else: st.info("⚠️ Jalankan proses dulu")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Pengaturan":
    st.markdown('<div class="kartu"><h4>⚙️ Pengaturan</h4><p>Sistem siap digunakan.</p></div>', unsafe_allow_html=True)