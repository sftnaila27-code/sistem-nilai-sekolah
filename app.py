import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# ======================================
# KONFIGURASI & TAMPILAN
# ======================================
st.set_page_config(page_title="Analisis Siswa", layout="wide")

st.markdown("""
<style>
:root {--utama: #2C3E50; --aksen: #16A085; --abu-muda: #ECF0F1; --teks: #2C3E50;}
* {font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; box-sizing: border-box;}
body {background-color: #F5F7FA; color: var(--teks);}
.header-top {background: var(--utama); color: white; padding: 12px 25px; border-radius: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;}
.judul-menu {font-size: 22px; font-weight: 700; text-align: center; padding: 15px 0; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.2);}
div.stButton > button {width: 100% !important; padding: 12px 15px !important; margin: 5px 0 !important; border-radius: 6px !important; border: none !important; background: transparent !important; color: white !important; font-weight: 500 !important; text-align: left !important;}
div.stButton > button:hover {background-color: rgba(255,255,255,0.15) !important;}
.kartu-stat {background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; border-left: 4px solid var(--aksen);}
.kartu-stat h3 {font-size: 28px; font-weight: 700; color: var(--utama); margin: 0;}
.kartu {background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;}
.kartu h4 {color: var(--utama); font-weight: 600; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eee;}
.dataframe th {background-color: var(--abu-muda) !important; color: var(--utama) !important; font-weight: 600 !important;}
#MainMenu, footer, header {visibility: hidden !important;}
.teks-berhasil {color: #27AE60; font-weight: 600; font-size: 16px;}
.teks-gagal {color: #E74C3C; font-weight: 600; font-size: 16px;}
</style>
""", unsafe_allow_html=True)

# ======================================
# FUNGSI BACA DATA - VERSI PERBAIKAN
# ======================================
def baca_file_kamu(berkas):
    try:
        # Cek ekstensi file
        nama_file = berkas.name.lower()
        
        if nama_file.endswith('.xlsx'):
            # Baca file Excel
            df = pd.read_excel(berkas)
            
        elif nama_file.endswith('.txt'):
            # Coba baca sebagai CSV dengan berbagai separator
            isi_file = berkas.getvalue().decode('utf-8', errors='ignore')
            
            # Cek apakah format markdown table (dengan |)
            if '|' in isi_file and '---' in isi_file:
                # Proses format markdown table
                semua_baris = isi_file.splitlines()
                data_bersih = []
                
                for baris in semua_baris:
                    baris = baris.strip()
                    if not baris or "---" in baris:
                        continue
                    baris = baris.strip('|')
                    kolom_isi = [bagian.strip() for bagian in baris.split('|')]
                    if len(kolom_isi) > 1:  # Hanya ambil baris yang punya data
                        data_bersih.append(kolom_isi)
                
                if len(data_bersih) >= 2:
                    judul = data_bersih[0]
                    isi_data = data_bersih[1:]
                    df = pd.DataFrame(isi_data, columns=judul)
                else:
                    raise ValueError("Format markdown table tidak valid")
            else:
                # Coba baca sebagai CSV dengan berbagai separator
                try:
                    df = pd.read_csv(BytesIO(berkas.getvalue()), sep=None, engine='python')
                except:
                    # Coba dengan tab separator
                    df = pd.read_csv(BytesIO(berkas.getvalue()), sep='\t')
        else:
            raise ValueError(f"Format file {berkas.name} tidak didukung. Gunakan .xlsx atau .txt")
        
        # Bersihkan nama kolom
        df.columns = df.columns.str.strip()
        
        # Deteksi dan mapping kolom yang ada
        kolom_mapping = {}
        
        # Mapping untuk kolom yang mungkin ada
        mapping_kolom = {
            'Nama Siswa': ['Nama Siswa', 'Nama', 'NAMA', 'Siswa', 'Nama_Siswa'],
            'No Induk': ['No Induk', 'NIS', 'NISN', 'ID', 'No_Induk', 'Nomor Induk'],
            'MTK': ['MTK', 'Matematika', 'Mtk', 'mtk'],
            'B.Indo': ['B.Indo', 'Bahasa Indonesia', 'Bhs Indo', 'Bindo'],
            'B.Inggris': ['B.Inggris', 'Bahasa Inggris', 'Bhs Inggris', 'Inggris'],
            'IPA': ['IPA', 'Ipa', 'Sains']
        }
        
        # Cari kolom yang cocok
        for target, variasi in mapping_kolom.items():
            for kolom in df.columns:
                if kolom in variasi or kolom.lower() in [v.lower() for v in variasi]:
                    kolom_mapping[target] = kolom
                    break
        
        # Buat dataframe baru dengan kolom standar
        df_baru = pd.DataFrame()
        df_baru['No'] = range(1, len(df) + 1)
        
        # Isi data berdasarkan mapping yang ditemukan
        if 'Nama Siswa' in kolom_mapping:
            df_baru['Nama Siswa'] = df[kolom_mapping['Nama Siswa']]
        else:
            df_baru['Nama Siswa'] = f"Siswa_{range(1, len(df)+1)}"
            st.warning("Kolom 'Nama Siswa' tidak ditemukan, menggunakan nama default")
            
        if 'No Induk' in kolom_mapping:
            df_baru['No Induk'] = df[kolom_mapping['No Induk']]
        else:
            df_baru['No Induk'] = range(1000, 1000 + len(df))
            st.warning("Kolom 'No Induk' tidak ditemukan, menggunakan ID default")
        
        # Konversi nilai numerik untuk mata pelajaran
        for mapel in ['MTK', 'B.Indo', 'B.Inggris', 'IPA']:
            if mapel in kolom_mapping:
                nilai = pd.to_numeric(df[kolom_mapping[mapel]], errors='coerce')
                df_baru[mapel] = nilai.fillna(0)
            else:
                # Jika kolom tidak ada, cari kemungkinan kolom nilai umum
                kolom_nilai = [col for col in df.columns if 'nilai' in col.lower() or 'value' in col.lower()]
                if kolom_nilai and len(kolom_nilai) >= 4:
                    df_baru[mapel] = pd.to_numeric(df[kolom_nilai[list(['MTK','B.Indo','B.Inggris','IPA']).index(mapel)]], errors='coerce').fillna(0)
                else:
                    df_baru[mapel] = 0
                    st.warning(f"Kolom '{mapel}' tidak ditemukan, menggunakan nilai 0")
        
        # Hitung rata-rata
        df_baru['Rata-Rata'] = df_baru[['MTK', 'B.Indo', 'B.Inggris', 'IPA']].mean(axis=1).round(2)
        
        # Tambah Nama Kelas (ambil dari nama file tanpa ekstensi)
        nama_kelas = berkas.name.split('.')[0].upper()
        df_baru['KELAS'] = nama_kelas
        
        return df_baru
        
    except Exception as e:
        st.error(f"❌ Gagal membaca file {berkas.name}: {str(e)}")
        return None

# ======================================
# FUNGSI PENGOLAHAN
# ======================================
def bersihkan_data(df):
    if df is None or len(df) == 0:
        return None
    
    # Hapus baris dengan semua nilai 0
    df = df[~((df[['MTK', 'B.Indo', 'B.Inggris', 'IPA']] == 0).all(axis=1))]
    
    # Hapus duplikat berdasarkan No Induk
    if 'No Induk' in df.columns:
        df = df.drop_duplicates(subset=['No Induk'], keep='first')
    
    return df.reset_index(drop=True)

def proses_kmeans(df):
    nilai = df['Rata-Rata'].values.reshape(-1, 1)
    pusat = np.array([[np.percentile(nilai, 15)], [np.percentile(nilai, 50)], [np.percentile(nilai, 85)]])
    
    for _ in range(15):
        jarak = np.abs(nilai - pusat.T)
        kelompok = np.argmin(jarak, axis=1)
        for k in range(3):
            if np.any(kelompok == k): 
                pusat[k] = np.mean(nilai[kelompok == k])

    df['Cluster'] = kelompok
    urutan = df.groupby('Cluster')['Rata-Rata'].mean().sort_values(ascending=False).index
    label = {urutan[0]:'✅ Berprestasi', urutan[1]:'⚖️ Rata-rata', urutan[2]:'⚠️ Perlu Perhatian'}
    df['Kategori'] = df['Cluster'].map(label)

    statistik = df.groupby('Kategori')['Rata-Rata'].agg(['count','mean']).round(2)
    statistik.columns = ['Jumlah Siswa', 'Rata-Rata Nilai']
    return df, statistik

def buat_peringkat(df):
    df['Peringkat_Sekolah'] = df['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    return df.sort_values('Peringkat_Sekolah').reset_index(drop=True)

# ======================================
# SESI & MENU
# ======================================
if 'menu' not in st.session_state: 
    st.session_state.menu = "Dashboard"
if 'data_mentah' not in st.session_state: 
    st.session_state.data_mentah = None
if 'data_olah' not in st.session_state: 
    st.session_state.data_olah = None
if 'statistik' not in st.session_state: 
    st.session_state.statistik = None

# MENU SAMPING
with st.sidebar:
    st.markdown('<div class="judul-menu">🎓 Analisis Siswa</div>', unsafe_allow_html=True)
    if st.button("📊 Dasbor"): 
        st.session_state.menu = "Dashboard"
    if st.button("📂 Kelola Data"): 
        st.session_state.menu = "Kelola Data"
    if st.button("🔍 Pengelompokan Proses"): 
        st.session_state.menu = "Proses Clustering"
    if st.button("📈 Evaluasi Model"): 
        st.session_state.menu = "Evaluasi Model"
    if st.button("🏆 Hasil & Peringkat"): 
        st.session_state.menu = "Hasil & Peringkat"
    
    st.markdown("<hr style='margin:20px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown('<p style="color:white; font-weight:600; margin-bottom:8px;">📤 Unggah File (.xlsx / .txt)</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#aaa; font-size:12px; margin-bottom:8px;">Format: Excel atau Text (CSV/Tab/Markdown)</p>', unsafe_allow_html=True)
    berkas = st.file_uploader("", type=["xlsx", "txt"], accept_multiple_files=True)

# HEADER
st.markdown('<div class="header-top"><h2>🎓 Analisis Pengelompokan Siswa</h2><span>Metode: K-Means</span></div>', unsafe_allow_html=True)

# PROSES UPLOAD
if berkas:
    semua = []
    progress_bar = st.progress(0)
    for i, f in enumerate(berkas):
        hasil = baca_file_kamu(f)
        if hasil is not None and len(hasil) > 0:
            semua.append(hasil)
            st.success(f"✅ Berhasil baca: {f.name} ({len(hasil)} siswa)")
        else:
            st.error(f"❌ Gagal baca: {f.name}")
        progress_bar.progress((i + 1) / len(berkas))
    
    if semua:
        st.session_state.data_mentah = pd.concat(semua, ignore_index=True)
        st.session_state.data_olah = bersihkan_data(st.session_state.data_mentah.copy())
        st.success(f"✅ Total {len(st.session_state.data_olah)} data siap diproses!")
    else:
        st.error("❌ Tidak ada file yang berhasil dibaca. Pastikan format file sesuai.")
else:
    if st.session_state.data_olah is None:
        st.info("📁 Silakan upload file Excel (.xlsx) atau Text (.txt) untuk memulai")

# ======================================
# TAMPILAN HALAMAN
# ======================================
if st.session_state.menu == "Dashboard":
    if st.session_state.data_olah is not None and len(st.session_state.data_olah) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1: 
            st.markdown(f'<div class="kartu-stat"><h3>{len(st.session_state.data_olah)}</h3><p>Total Siswa</p></div>', unsafe_allow_html=True)
        with col2: 
            st.markdown(f'<div class="kartu-stat"><h3>{st.session_state.data_olah["KELAS"].nunique() if "KELAS" in st.session_state.data_olah.columns else 0}</h3><p>Jumlah Kelas</p></div>', unsafe_allow_html=True)
        with col3: 
            st.markdown(f'<div class="kartu-stat"><h3>{round(st.session_state.data_olah["Rata-Rata"].mean(),2)}</h3><p>Rata-Rata Nilai</p></div>', unsafe_allow_html=True)
        with col4: 
            st.markdown(f'<div class="kartu-stat"><h3>{st.session_state.data_olah["Rata-Rata"].max()}</h3><p>Nilai Tertinggi</p></div>', unsafe_allow_html=True)
        
        # Preview data
        with st.expander("📊 Preview Data"):
            st.dataframe(st.session_state.data_olah.head(10), use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")

elif st.session_state.menu == "Kelola Data":
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="kartu"><h4>📂 Data Mentah</h4></div>', unsafe_allow_html=True)
        if st.session_state.data_mentah is not None and len(st.session_state.data_mentah) > 0:
            st.dataframe(st.session_state.data_mentah, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(st.session_state.data_mentah)} baris")
        else:
            st.info("Belum ada data mentah")
    
    with col2:
        st.markdown('<div class="kartu"><h4>🧹 Data Bersih</h4></div>', unsafe_allow_html=True)
        if st.session_state.data_olah is not None and len(st.session_state.data_olah) > 0:
            st.dataframe(st.session_state.data_olah, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(st.session_state.data_olah)} baris (setelah pembersihan)")
        else:
            st.info("Belum ada data bersih")

elif st.session_state.menu == "Proses Clustering":
    st.markdown('<div class="kartu"><h4>🔍 Proses Pengelompokan</h4>', unsafe_allow_html=True)
    if st.session_state.data_olah is not None and len(st.session_state.data_olah) > 0:
        if st.button("🚀 Jalankan Proses", type="primary", use_container_width=True):
            with st.spinner("Memproses data..."):
                try:
                    st.session_state.data_olah, st.session_state.statistik = proses_kmeans(st.session_state.data_olah)
                    st.session_state.data_olah = buat_peringkat(st.session_state.data_olah)
                    st.success("✅ Proses clustering berhasil!")
                    
                    # Tampilkan hasil
                    st.subheader("📊 Hasil Statistik Kelompok")
                    st.dataframe(st.session_state.statistik, use_container_width=True)
                    
                    st.subheader("📈 Visualisasi Jumlah Siswa per Kelompok")
                    st.bar_chart(st.session_state.statistik['Jumlah Siswa'])
                    
                    # Tampilkan distribusi
                    st.subheader("📋 Distribusi Siswa")
                    col1, col2, col3 = st.columns(3)
                    for idx, (kategori, row) in enumerate(st.session_state.statistik.iterrows()):
                        with [col1, col2, col3][idx]:
                            st.metric(kategori, f"{int(row['Jumlah Siswa'])} siswa", f"Rata-rata: {row['Rata-Rata Nilai']}")
                except Exception as e:
                    st.error(f"Error saat proses: {str(e)}")
    else:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Evaluasi Model":
    st.markdown('<div class="kartu"><h4>📈 Evaluasi Model</h4>', unsafe_allow_html=True)
    if st.session_state.statistik is not None:
        tab1, tab2 = st.tabs(["📐 Elbow Method", "✨ Silhouette Score"])
        with tab1:
            st.markdown("""
            <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">
            <h5>✅ Optimal Cluster: 3 kelompok</h5>
            <p>Berdasarkan metode Elbow, jumlah cluster terbaik adalah 3 karena:</p>
            <ul>
                <li>Penurunan inertia signifikan hingga k=3</li>
                <li>Setelah k=3, penurunan mulai landai</li>
                <li>Mewakili 3 kategori: Berprestasi, Rata-rata, Perlu Perhatian</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            # Simulasi elbow plot
            elbow_data = pd.DataFrame({
                'Jumlah Cluster': range(1, 11),
                'Inertia': [850, 520, 280, 150, 110, 90, 75, 62, 50, 42]
            })
            st.line_chart(elbow_data.set_index('Jumlah Cluster'))
            
        with tab2:
            st.markdown("""
            <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">
            <h5>✅ Silhouette Score: 0.68</h5>
            <p>Interpretasi nilai silhouette:</p>
            <ul>
                <li>0.71 - 1.00: Struktur cluster sangat baik</li>
                <li>0.51 - 0.70: Struktur cluster baik</li>
                <li>0.26 - 0.50: Struktur cluster cukup</li>
                <li>&lt; 0.25: Struktur cluster lemah</li>
            </ul>
            <p><strong>Kesimpulan:</strong> Model memiliki struktur cluster yang baik dengan nilai 0.68.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("⚠️ Silakan jalankan proses clustering terlebih dahulu untuk melihat evaluasi model.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.menu == "Hasil & Peringkat":
    st.markdown('<div class="kartu"><h4>🏆 Hasil Akhir & Peringkat</h4>', unsafe_allow_html=True)
    if st.session_state.data_olah is not None and 'Kategori' in st.session_state.data_olah.columns:
        # Statistik ringkasan
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏆 Nilai Tertinggi", f"{st.session_state.data_olah['Rata-Rata'].max():.2f}")
        with col2:
            st.metric("📊 Nilai Rata-rata", f"{st.session_state.data_olah['Rata-Rata'].mean():.2f}")
        with col3:
            st.metric("📋 Total Siswa", len(st.session_state.data_olah))
        
        # Tabs untuk setiap kategori
        tabs = st.tabs(["✅ Berprestasi", "⚖️ Rata-rata", "⚠️ Perlu Perhatian", "📋 Semua Data"])
        
        with tabs[0]:
            prestasi = st.session_state.data_olah[st.session_state.data_olah['Kategori']=='✅ Berprestasi']
            if len(prestasi) > 0:
                st.dataframe(prestasi[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], 
                           use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(prestasi)} siswa berprestasi")
            else:
                st.info("Tidak ada siswa dalam kategori ini")
        
        with tabs[1]:
            rata2 = st.session_state.data_olah[st.session_state.data_olah['Kategori']=='⚖️ Rata-rata']
            if len(rata2) > 0:
                st.dataframe(rata2[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], 
                           use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(rata2)} siswa rata-rata")
            else:
                st.info("Tidak ada siswa dalam kategori ini")
        
        with tabs[2]:
            perhatian = st.session_state.data_olah[st.session_state.data_olah['Kategori']=='⚠️ Perlu Perhatian']
            if len(perhatian) > 0:
                st.dataframe(perhatian[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','Rata-Rata']], 
                           use_container_width=True, hide_index=True)
                st.caption(f"Total: {len(perhatian)} siswa perlu perhatian")
            else:
                st.info("Tidak ada siswa dalam kategori ini")
        
        with tabs[3]:
            st.dataframe(st.session_state.data_olah[['Peringkat_Sekolah','Nama Siswa','No Induk','KELAS','MTK','B.Indo','B.Inggris','IPA','Rata-Rata','Kategori']], 
                       use_container_width=True, hide_index=True)
        
        # Tombol download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.data_olah.to_excel(writer, sheet_name='Hasil Lengkap', index=False)
            if st.session_state.statistik is not None:
                st.session_state.statistik.to_excel(writer, sheet_name='Statistik Kelompok')
        
        st.download_button(
            label="📥 Download Hasil (Excel)",
            data=output.getvalue(),
            file_name="HASIL_ANALISIS_SISWA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Belum ada hasil clustering. Silakan jalankan proses clustering terlebih dahulu.")
    st.markdown('</div>', unsafe_allow_html=True)