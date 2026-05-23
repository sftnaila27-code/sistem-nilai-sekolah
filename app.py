import streamlit as st
import pandas as pd
from io import BytesIO

# KONFIGURASI
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# FUNGSI BACA FILE
def proses_file(berkas):
    try:
        # CARA BACA YANG DIPERBAIKI
        df = pd.read_excel(
            berkas,
            engine='openpyxl',
            header=0
        )

        # SAMAKAN NAMA KOLOM
        df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']

        # UBAH KE ANGKA
        kolom_angka = ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
        for kol in kolom_angka:
            df[kol] = pd.to_numeric(df[kol], errors='coerce')

        # TAMBAH KELAS
        nama_kelas = berkas.name.split('.')[0].upper()
        df['KELAS'] = nama_kelas

        return df

    except Exception as e:
        st.error(f"❌ GAGAL BACA: {berkas.name}")
        st.error(f"Pesan: {str(e)}")
        return None

# PENGOLAHAN UTAMA
def olah_data(daftar_file):
    semua = []
    if not daftar_file:
        return None

    for f in daftar_file:
        hasil = proses_file(f)
        if hasil is None:
            return None
        semua.append(hasil)

    if not semua:
        return None

    # GABUNGKAN
    gabung = pd.concat(semua, ignore_index=True)

    # 1. REKAP KELAS
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={
        'MTK':'Matematika', 'B.Indo':'Bahasa Indonesia', 'B.Inggris':'Bahasa Inggris', 'Rata-Rata':'Rata-Rata Kelas'
    })

    # 2. PERINGKAT SEKOLAH
    gabung['PERINGKAT'] = gabung['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_sekolah = gabung.sort_values('PERINGKAT').reset_index(drop=True)

    # 3. PERINGKAT KELAS
    gabung['PERINGKAT_KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense').astype(int)
    peringkat_kelas = gabung.sort_values(['KELAS','PERINGKAT_KELAS'])

    # 4. BUAT FILE HASIL
    def unduh_excel():
        keluaran = BytesIO()
        with pd.ExcelWriter(keluaran, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
            peringkat_sekolah.to_excel(w, 'Peringkat Sekolah', False)
        return keluaran.getvalue()

    return gabung, rekap_kelas, peringkat_sekolah, unduh_excel()

# ======================================
# TAMPILAN WEB
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
st.markdown("---")

# MENU SAMPING
with st.sidebar:
    st.header("📝 CARA PAKAI")
    st.success("""
    ✅ Pastikan File **Excel Asli** (.xlsx)
    ✅ Urutan Kolom:
    `No | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata`
    ✅ Nama File: `7a.xlsx`, `7b.xlsx`, dst
    """)
    st.header("📤 UNGGAH FILE")
    masuk = st.file_uploader("Pilih File Excel", type="xlsx", accept_multiple_files=True)

# PROSES
hasil = olah_data(masuk)

if hasil:
    data, rekap, peringkat, berkas = hasil
    st.success("✅ FILE BERHASIL DIBACA & DIPROSES!")

    tab1, tab2, tab3 = st.tabs(["🏫 Rekap Kelas", "🏆 Peringkat Sekolah", "📋 Data Lengkap"])

    with tab1:
        st.subheader("Tabel Rekapitulasi Nilai")
        st.dataframe(rekap, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Daftar Urutan Nilai Siswa")
        st.dataframe(peringkat[['PERINGKAT','KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']], use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Seluruh Data Siswa")
        st.dataframe(data, use_container_width=True, hide_index=True)

    # TOMBOL UNDUH
    st.download_button(
        label="📥 Unduh Semua Hasil (.xlsx)",
        data=berkas,
        file_name="HASIL_OLAH_NILAI_SEKOLAH.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

else:
    st.warning("⬅️ Silakan unggah file Excel yang BENAR di menu samping.")
    st.info("⚠️ **Wajib:** File harus disimpan dari Microsoft Excel, bukan file teks biasa.")