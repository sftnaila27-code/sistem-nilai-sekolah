import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import plotly.express as px
import plotly.graph_objects as go

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
</style>
""", unsafe_allow_html=True)

# ======================================
# FUNGSI PENGOLAHAN DATA (ALUR SESUAI DIAGRAM)
# ======================================

# 1. Upload & Load Data
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
        
        # Ubah ke numerik
        for kol in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
            data[kol] = pd.to_numeric(data[kol], errors='coerce')
        
        nama_kelas = berkas.name.split('.')[0].upper()
        data['KELAS'] = nama_kelas
        return data
    except Exception as e:
        st.error(f"❌ Gagal baca file: {berkas.name}")
        return None

# 2. Data Cleaning & Preprocessing
def bersihkan_data(df):
    # Hapus baris kosong
    df = df.dropna(subset=['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata'])
    # Hapus duplikat
    df = df.drop_duplicates(subset=['No Induk', 'Nama Siswa'])
    # Reset index
    df = df.reset_index(drop=True)
    return df

# 3. Metode K-Means Clustering
def proses_kmeans(df, fitur=['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata'], n_cluster=3):
    # Ambil data fitur
    X = df[fitur].values
    
    # Standarisasi Data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Model K-Means
    kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init='auto')
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analisis Karakteristik Cluster
    rata_cluster = df.groupby('Cluster')[fitur].mean().round(2)
    rata_cluster['Jumlah Siswa'] = df['Cluster'].value_counts()
    
    # Label Cluster Berdasarkan Nilai Rata-rata
    urutan = rata_cluster.sort_values('Rata-Rata', ascending=False).index.tolist()
    label_map = {
        urutan[0]: '✅ Berprestasi',
        urutan[1]: '⚖️ Rata-rata',
        urutan[2]: '⚠️ Perlu Perhatian'
    }
    df['Kategori'] = df['Cluster'].map(label_map)
    
    return df, kmeans, X_scaled, rata_cluster

# 4. Evaluasi Model: Elbow Method
def evaluasi_elbow(X_scaled):
    wcss = []
    for i in range(1, 11):
        kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=42)
        kmeans.fit(X_scaled)
        wcss.append(kmeans.inertia_)
    return wcss

# 5. Evaluasi Model: Silhouette Score
def evaluasi_silhouette(X_scaled):
    skor = []
    rentang_k = range(2, 11)
    for k in rentang_k:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(X_scaled)
        skor.append(silhouette_score(X_scaled, labels, metric='euclidean'))
    return rentang_k, skor

# 6. Perangkingan Siswa
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
if 'hasil_evaluasi' not in st.session_state:
    st.session_state.hasil_evaluasi = None

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
    st.markdown('<p style="color:white; font-weight:600; margin-bottom:8px;">📤 Unggah Dataset</p>', unsafe_allow_html=True)
    berkas_masuk = st.file_uploader("", type=["xlsx", "txt"], accept_multiple_files=True, label_visibility="collapsed")
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

    # Grafik Distribusi Nilai & Ringkasan
    col_kiri, col_kanan = st.columns([2,1])
    with col_kiri:
        st.markdown('<div class="kartu"><h4>📊 Statistik Nilai Mata Pelajaran</h4>', unsafe_allow_html=True)
        if st.session_state.data_olah is not None:
            data_rata = st.session_state.data_olah[['MTK','B.Indo','B.Inggris','IPA']].mean()
            fig = px.bar(x=data_rata.index, y=data_rata.values, labels={'x':'Mata Pelajaran', 'y':'Rata-Rata Nilai'}, color_discrete_sequence=['#16A085'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("⚠️ Unggah data terlebih dahulu untuk melihat grafik.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_kanan:
        st.markdown('<div class="kartu"><h4>📌 Keterangan Proses</h4>', unsafe_allow_html=True)
        st.markdown("""
        ✅ **Data Cleaning**: Menghapus data kosong/duplikat  
        ✅ **Preprocessing**: Standarisasi nilai  
        ✅ **Clustering**: K-Means (3 Kelompok)  
        ✅ **Evaluasi**: Elbow Method & Silhouette Score  
        ✅ **Identifikasi**: Label Berprestasi / Rata-rata / Perlu Perhatian
        """)
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
                st.session_state.data_olah, model, X_scaled, karakteristik = proses_kmeans(st.session_state.data_olah)
                st.session_state.data_olah = peringkat_siswa(st.session_state.data_olah)
                st.session_state.hasil_evaluasi = {'X': X_scaled}
            st.success("✅ Pengelompokan selesai!")

            st.subheader("📌 Karakteristik Setiap Kelompok")
            st.dataframe(karakteristik, use_container_width=True)

            st.subheader("📊 Visualisasi Hasil Kelompok")
            fig = px.scatter(st.session_state.data_olah, x='Rata-Rata', y='MTK', color='Kategori',
                             hover_data=['Nama Siswa', 'No Induk', 'KELAS'],
                             color_discrete_map={'✅ Berprestasi':'#27AE60', '⚖️ Rata-rata':'#F39C12', '⚠️ Perlu Perhatian':'#E74C3C'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ Silakan unggah dan bersihkan data terlebih dahulu.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Evaluasi Model":
    st.markdown('<div class="kartu"><h4>📈 Evaluasi Kualitas Model Clustering</h4>', unsafe_allow_html=True)
    if st.session_state.hasil_evaluasi is not None:
        tab1, tab2 = st.tabs(["📐 Elbow Method", "✨ Silhouette Score"])
        
        with tab1:
            wcss = evaluasi_elbow(st.session_state.hasil_evaluasi['X'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(range(1,11)), y=wcss, mode='lines+markers', line=dict(color='#2980B9', width=3)))
            fig.update_layout(title='Penentuan Jumlah Cluster Optimal (Metode Siku)',
                              xaxis_title='Jumlah Cluster (K)',
                              yaxis_title='WCSS (Within-Cluster Sum of Squares)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**📌 Interpretasi:** Titik lengkung/penurunan drastis menunjukkan jumlah kelompok terbaik.")

        with tab2:
            k_range, skor_sil = evaluasi_silhouette(st.session_state.hasil_evaluasi['X'])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=k_range, y=skor_sil, mode='lines+markers', line=dict(color='#8E44AD', width=3)))
            fig.update_layout(title='Nilai Silhouette Score',
                              xaxis_title='Jumlah Cluster (K)',
                              yaxis_title='Nilai Skor (-1 s.d 1)',
                              yaxis=dict(range=[0,1]))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**📌 Interpretasi:** Semakin mendekati nilai **1**, semakin baik pemisahan antar kelompok.")
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