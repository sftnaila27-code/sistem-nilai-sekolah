import streamlit as st
import pandas as pd
from io import BytesIO

# KONFIGURASI
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")

# FUNGSI UTAMA
def baca_dan_proses(file_terpilih):
    if not file_terpilih:
        return None

    semua_data = []
    with st.spinner("🔄 Memproses Data..."):
        for f in file_terpilih:
            try:
                # BACA FILE EXCEL ASLI
                df = pd.read_excel(f, engine='openpyxl')
                
                # PAKSA UBAH NAMA KOLOM SESUAI URUTAN
                df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
                
                # UBAH ANGKA
                for kol in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
                    df[kol] = pd.to_numeric(df[kol], errors='coerce')
                
                # TAMBAH KELAS
                df['KELAS'] = f.name.split('.')[0].upper()
                semua_data.append(df)

            except Exception as e:
                st.error(f"❌ GAGAL: {f.name} -> {str(e)}")
                st.info("⚠️ Pastikan ini File Excel Asli, bukan teks biasa!")
                return None

    # GABUNGKAN
    gabung = pd.concat(semua_data, ignore_index=True)

    # HITUNG REKAP KELAS
    rekap = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap = rekap.sort_values('Rata-Rata', ascending=False)
    rekap = rekap.rename(columns={'Rata-Rata':'RATA-RATA KELAS'})

    # HITUNG PERINGKAT SEKOLAH
    gabung['PERINGKAT SEKOLAH'] = gabung['Rata-Rata'].rank(ascending=False, method='min').astype(int)
    gabung = gabung.sort_values('PERINGKAT SEKOLAH').reset_index(drop=True)

    # HITUNG PERINGKAT KELAS
    gabung['PERINGKAT KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='min').astype(int)

    # BUAT FILE EXCEL HASIL
    def simpan():
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'DATA LENGKAP', False)
            rekap.to_excel(w, 'REKAP KELAS', False)
        return output.getvalue()

    return gabung, rekap, simpan()

# ======================================
# TAMPILAN WEB
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SEKOLAH")

# MENU SAMPING
with st.sidebar:
    st.header("📝 CARA PAKAI")
    st.code("""
    1. Buka file Anda di Excel
    2. Pastikan Kolom: No | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata
    3. Simpan sebagai .xlsx (File Excel Asli)
    4. Nama: 7a.xlsx, 7b.xlsx, dst
    """)
    st.header("📤 UNGGAH FILE EXCEL")
    file_masuk = st.file_uploader("Pilih File", type="xlsx", accept_multiple_files=True)

# PROSES
hasil = baca_dan_proses(file_masuk)

if hasil:
    df_data, df_rekap, file_unduh = hasil
    st.success("✅ BERHASIL DIPROSES!")

    tab1, tab2, tab3 = st.tabs(["📊 Rekap Kelas", "🏆 Peringkat Sekolah", "📋 Data Lengkap"])

    with tab1:
        st.subheader("Rekapitulasi Nilai Rata-Rata")
        st.dataframe(df_rekap, use_container_width=True)

    with tab2:
        st.subheader("Daftar Urutan Nilai Siswa")
        st.dataframe(df_data[['PERINGKAT SEKOLAH','KELAS','PERINGKAT KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']], use_container_width=True)

    with tab3:
        st.subheader("Seluruh Data Siswa")
        st.dataframe(df_data, use_container_width=True)

    # TOMBOL UNDUH
    st.download_button(
        label="📥 Unduh Semua Hasil (.xlsx)",
        data=file_unduh,
        file_name="HASIL_OLAH_NILAI.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

else:
    st.warning("⬅️ Silakan unggah File Excel (.xlsx) yang BENAR terlebih dahulu.")
    st.info("⚠️ **PENTING:** File harus disimpan dari Microsoft Excel, bukan file teks biasa yang diganti nama jadi .xlsx.")