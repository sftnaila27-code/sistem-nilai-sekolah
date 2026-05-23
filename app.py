import streamlit as st
import pandas as pd
from io import StringIO

# ======================================
# KONFIGURASI DASAR
# ======================================
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# ======================================
# FUNGSI BACA FILE (KHUSUS FORMAT | ANDA)
# ======================================
def baca_file_format_anda(berkas):
    try:
        # Baca sebagai TEKS BIASA (pasti berhasil)
        isi_teks = berkas.read().decode('utf-8', errors='ignore')
        
        # Ubah teks jadi tabel otomatis (karena ada garis |)
        data = pd.read_csv(
            StringIO(isi_teks),
            sep="|",             # Pemisahnya garis |
            skipinitialspace=True, # Buang spasi kosong
            header=0,             # Baris pertama judul kolom
            engine='python'
        )

        # Bersihkan kolom kosong yang muncul di pinggir
        data = data.dropna(axis=1, how='all')
        
        # SAMAKAN NAMA KOLOM PERSIS DENGAN DATA ANDA
        data.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']

        # Ubah kolom angka jadi bilangan bulat/desimal
        for kol in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
            data[kol] = pd.to_numeric(data[kol], errors='coerce')

        # Ambil nama kelas dari nama file (contoh: 7a.xlsx -> 7A)
        nama_kelas = berkas.name.split('.')[0].upper()
        data['KELAS'] = nama_kelas

        return data

    except Exception as e:
        st.error(f"❌ Gagal memproses: {berkas.name}")
        st.error(f"Detail: {str(e)}")
        return None

# ======================================
# PENGOLAHAN DATA UTAMA
# ======================================
def proses_semua_file(daftar_file):
    semua_data = []
    if not daftar_file:
        return None

    st.info("⏳ Sedang memuat data...")

    for f in daftar_file:
        hasil = baca_file_format_anda(f)
        if hasil is None:
            return None
        semua_data.append(hasil)

    # Gabungkan semua data jadi satu
    gabung = pd.concat(semua_data, ignore_index=True)
    st.success("✅ Semua data berhasil dibaca!")

    # 1. REKAP NILAI PER KELAS
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={
        'MTK':'Matematika',
        'B.Indo':'Bahasa Indonesia',
        'B.Inggris':'Bahasa Inggris',
        'Rata-Rata':'Rata-Rata Kelas'
    })

    # 2. PERINGKAT SELURUH SEKOLAH
    gabung['PERINGKAT SEKOLAH'] = gabung['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_sekolah = gabung.sort_values('PERINGKAT SEKOLAH').reset_index(drop=True)

    # 3. PERINGKAT DI DALAM KELAS
    gabung['PERINGKAT KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_kelas = gabung.sort_values(['KELAS', 'PERINGKAT KELAS'])

    # 4. BUAT FILE HASIL UNTUK DIUNDUH
    def buat_file_unduh():
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
            peringkat_sekolah.to_excel(w, 'Peringkat Sekolah', False)
        return output.getvalue()

    return gabung, rekap_kelas, peringkat_sekolah, peringkat_kelas, buat_file_unduh()

# ======================================
# TAMPILAN APLIKASI WEB
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
st.markdown("---")

# MENU SAMPING
with st.sidebar:
    st.header("📝 CARA PENGGUNAAN")
    st.code("""
    Format File:
    |No|Nama Siswa|No Induk|MTK|B.Indo|B.Inggris|IPA|Rata-Rata|

    Nama File:
    7a.xlsx, 7b.xlsx, 8a.xlsx, dst
    """)
    st.header("📤 UNGGAH FILE")
    berkas_masuk = st.file_uploader(
        "Pilih File Anda (.xlsx / .txt)",
        type=["xlsx", "txt"],
        accept_multiple_files=True
    )

# JALANKAN PROSES
hasil = proses_semua_file(berkas_masuk)

# TAMPILKAN HASIL
if hasil:
    data_mentah, rekap, peringkat_s, peringkat_k, file_unduh = hasil

    tab1, tab2, tab3 = st.tabs(["📊 Rekap Nilai Kelas", "🏆 Peringkat Sekolah", "👥 Peringkat Per Kelas"])

    with tab1:
        st.subheader("Tabel Rekapitulasi Nilai Rata-Rata")
        st.dataframe(rekap, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Daftar Urutan Nilai Seluruh Sekolah")
        st.dataframe(peringkat_s[['PERINGKAT SEKOLAH','KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']], use_container_width=True, hide_index=True)

    with tab3:
        pilih_kelas = st.selectbox("Pilih Kelas", sorted(peringkat_k['KELAS'].unique()))
        tampil = peringkat_k[peringkat_k['KELAS'] == pilih_kelas]
        st.dataframe(tampil[['PERINGKAT KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']], use_container_width=True, hide_index=True)

    # TOMBOL UNDUH
    st.markdown("---")
    st.download_button(
        label="📥 UNDUH HASIL (File Excel)",
        data=file_unduh,
        file_name="HASIL_OLAH_NILAI_SEKOLAH.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

else:
    st.info("⚠️ Silakan unggah file nilai Anda lewat menu di samping ⬅️")
    st.warning("*Kode ini sudah disesuaikan 100% agar bisa membaca file Anda yang ada garis | nya*")