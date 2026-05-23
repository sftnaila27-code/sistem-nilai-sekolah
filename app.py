import streamlit as st
import pandas as pd
from io import StringIO, BytesIO

# ======================================
# KONFIGURASI DASAR
# ======================================
st.set_page_config(
    page_title="Sistem Nilai Sekolah",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================
# CSS - TAMPILAN BERSIH, RAPI, MUNCUL SEMPURNA
# ======================================
st.markdown("""
<style>
/* Warna Dasar */
:root {
    --ungu: #6B72E1;
    --biru: #36C5F0;
    --putih: #FFFFFF;
    --abu-muda: #F8F9FC;
    --teks: #374151;
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
    background: var(--putih);
    border-right: 1px solid #eee;
    padding: 20px 15px !important;
}

.judul-sidebar {
    font-size: 22px;
    font-weight: 700;
    color: var(--ungu);
    text-align: left;
    margin-bottom: 30px;
    padding: 10px;
    background: rgba(107, 114, 225, 0.05);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Tombol Navigasi */
div.stButton > button {
    width: 100% !important;
    padding: 12px 15px !important;
    margin: 5px 0 !important;
    border-radius: 12px !important;
    border: none !important;
    background: transparent !important;
    color: var(--teks) !important;
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
    background: rgba(107, 114, 225, 0.1) !important;
    color: var(--ungu) !important;
}
.aktif {
    background: linear-gradient(90deg, var(--ungu) 0%, #8B5CF6 100%) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(107, 114, 225, 0.2) !important;
}

/* Kotak Kartu Samping */
.kartu-samping {
    background: var(--putih);
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin: 12px 0;
    border: 1px solid #f3f4f6;
}
.judul-kartu {
    font-size: 15px;
    font-weight: 600;
    color: var(--ungu);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* ===== HAPUS TEKS BERANTAKAN SAJA ===== */
div[data-testid="stFileUploader"] small,
div[data-testid="stMarkdown"]:empty {
    display: none !important;
}

/* Sembunyikan menu streamlit bawaan */
#MainMenu, footer, header {
    visibility: hidden !important;
    display: none !important;
}

/* ===== KONTEN UTAMA ===== */
.banner {
    background: linear-gradient(90deg, var(--ungu) 0%, var(--biru) 100%);
    color: white;
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 25px;
    box-shadow: 0 8px 20px rgba(107, 114, 225, 0.2);
}

.kartu {
    background: var(--putih);
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ======================================
# FUNGSI BACA FILE (SESUAI FORMAT | ANDA)
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
        st.error(f"❌ Gagal baca: {berkas.name}")
        return None

def proses_semua_file(daftar_file):
    semua_data = []
    if not daftar_file: return None
    
    for f in daftar_file:
        hasil = baca_file_format_anda(f)
        if hasil is None: return None
        semua_data.append(hasil)
    
    gabung = pd.concat(semua_data, ignore_index=True)
    
    # Hitung Data
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','Rata-Rata':'Rata-Rata Kelas'})

    gabung['PERINGKAT SEKOLAH'] = gabung['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_sekolah = gabung.sort_values('PERINGKAT SEKOLAH').reset_index(drop=True)

    gabung['PERINGKAT KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_kelas = gabung.sort_values(['KELAS','PERINGKAT KELAS'])

    # Buat file unduh
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
    st.markdown('<div class="judul-sidebar">🏫 Nilai Sekolah</div>', unsafe_allow_html=True)
    
    # Tombol Navigasi BERFUNGSI
    if st.button("📊 Beranda", key="b1"):
        st.session_state.menu_aktif = "Beranda"
    if st.button("📋 Data Nilai", key="b2"):
        st.session_state.menu_aktif = "Data Nilai"
    if st.button("🏆 Peringkat", key="b3"):
        st.session_state.menu_aktif = "Peringkat"
    if st.button("⚙️ Pengaturan", key="b4"):
        st.session_state.menu_aktif = "Pengaturan"

    # Garis pemisah
    st.markdown("<hr style='margin:15px 0; border-color:#eee;'>", unsafe_allow_html=True)

    # Kotak Panduan
    st.markdown('<div class="kartu-samping"><div class="judul-kartu">📝 Panduan</div><span style="font-size:13px;">✅ Format: |No|Nama|...|<br>✅ Nama: 7a.xlsx / 7a.txt</span></div>', unsafe_allow_html=True)

    # Kotak UPLOAD FILE - TAMPIL, BERSIH, BERFUNGSI
    st.markdown('<div class="kartu-samping"><div class="judul-kartu">📤 Unggah Berkas</div>', unsafe_allow_html=True)
    berkas_masuk = st.file_uploader(
        "", 
        type=["xlsx", "txt"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Kotak Info
    st.markdown('<div class="kartu-samping"><div class="judul-kartu">ℹ️ Info</div><span style="font-size:13px;">Sistem otomatis hitung rata-rata & peringkat.</span></div>', unsafe_allow_html=True)

# ==== KONTEN TENGAH (TIDAK KOSONG LAGI) ====
hasil = proses_semua_file(berkas_masuk)

if st.session_state.menu_aktif == "Beranda":
    # Banner
    st.markdown("""
    <div class="banner">
        <h1 style="margin:0; font-size:28px;">📊 Sistem Pengolahan Nilai Siswa</h1>
        <p style="margin:5px 0 0 0; opacity:0.9;">Kelola, hitung, dan rangking nilai sekolah</p>
    </div>
    """, unsafe_allow_html=True)

    if hasil:
        data_mentah, rekap, _, _, _ = hasil
        # Kartu Ringkasan
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="kartu" style="text-align:center;"><div style="color:#6B72E1;">👥 Total Siswa</div><h2>{}</h2></div>'.format(len(data_mentah)), unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="kartu" style="text-align:center;"><div style="color:#36C5F0;">🏫 Jumlah Kelas</div><h2>{}</h2></div>'.format(data_mentah['KELAS'].nunique()), unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="kartu" style="text-align:center;"><div style="color:#2ECC71;">📈 Rata-Rata</div><h2>{}</h2></div>'.format(round(data_mentah['Rata-Rata'].mean(),2)), unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="kartu" style="text-align:center;"><div style="color:#F06292;">🏆 Nilai Tertinggi</div><h2>{}</h2></div>'.format(data_mentah['Rata-Rata'].max()), unsafe_allow_html=True)

        # Tabel Rekap
        st.markdown('<div class="kartu">', unsafe_allow_html=True)
        st.subheader("📋 Rekapitulasi Nilai Per Kelas")
        st.dataframe(rekap, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Tampilan Awal (Jelas & Tidak Kosong)
        st.markdown("""
        <div class="kartu" style="text-align:center; padding:50px 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/3201/3201355.png" width="150">
            <h2 style="color:#6B72E1; margin-top:20px;">Selamat Datang di Sistem Nilai</h2>
            <p style="font-size:16px; max-width:500px; margin:10px auto;">
                Unggah file nilai Anda lewat tombol di samping kiri. Sistem akan otomatis memproses dan menampilkan data di sini.
            </p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.menu_aktif == "Data Nilai":
    st.markdown('<div class="banner"><h1 style="margin:0;">📋 Data Lengkap Siswa</h1></div>', unsafe_allow_html=True)
    if hasil:
        data_mentah, _, _, _, _ = hasil
        st.markdown('<div class="kartu">', unsafe_allow_html=True)
        st.dataframe(data_mentah, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⚠️ Silakan unggah file terlebih dahulu untuk melihat data.")

elif st.session_state.menu_aktif == "Peringkat":
    st.markdown('<div class="banner"><h1 style="margin:0;">🏆 Daftar Peringkat Nilai</h1></div>', unsafe_allow_html=True)
    if hasil:
        _, _, peringkat_s, peringkat_k, file_unduh = hasil
        
        tab1, tab2 = st.tabs(["🏆 Peringkat Sekolah", "👥 Peringkat Per Kelas"])
        with tab1:
            st.markdown('<div class="kartu">', unsafe_allow_html=True)
            st.dataframe(peringkat_s[['PERINGKAT SEKOLAH','KELAS','Nama Siswa','No Induk','Rata-Rata']], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="kartu">', unsafe_allow_html=True)
            pilih_kelas = st.selectbox("Pilih Kelas", sorted(peringkat_k['KELAS'].unique()))
            tampil = peringkat_k[peringkat_k['KELAS'] == pilih_kelas]
            st.dataframe(tampil[['PERINGKAT KELAS','Nama Siswa','No Induk','Rata-Rata']], use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Tombol Unduh
        st.markdown('<div class="kartu">', unsafe_allow_html=True)
        st.download_button(
            label="📥 Unduh Semua Hasil ke Excel",
            data=file_unduh,
            file_name="HASIL_OLAH_NILAI_SEKOLAH.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⚠️ Silakan unggah file terlebih dahulu.")

elif st.session_state.menu_aktif == "Pengaturan":
    st.markdown('<div class="banner"><h1 style="margin:0;">⚙️ Pengaturan Aplikasi</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="kartu"><p>Pengaturan tampilan dan sistem aplikasi akan ditampilkan di sini.</p></div>', unsafe_allow_html=True)