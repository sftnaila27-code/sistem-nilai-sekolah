import streamlit as st
import pandas as pd
from io import BytesIO

# KONFIGURASI
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# PENGOLAHAN DATA
def proses_data(unggah):
    data = []
    if not unggah:
        return None

    for berkas in unggah:
        try:
            # Ambil nama kelas dari nama file
            nama_kelas = berkas.name.split('.')[0].upper()
            # Baca file excel
            df = pd.read_excel(berkas)
            # Samakan nama kolom
            df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
            # Tambah kolom kelas
            df['KELAS'] = nama_kelas
            # Ubah ke angka
            for kolom in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
                df[kolom] = pd.to_numeric(df[kolom], errors='coerce')
            data.append(df)
        except Exception as e:
            st.error(f"❌ Salah format file: {berkas.name}")
            return None

    if not data:
        return None

    # Gabungkan semua
    gabung = pd.concat(data, ignore_index=True)

    # 1. Rekap Rata-rata Kelas
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={
        'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','Rata-Rata':'Rata-Rata Kelas'
    })

    # 2. Peringkat Sekolah
    peringkat_sekolah = gabung.sort_values('Rata-Rata', ascending=False).reset_index(drop=True)
    peringkat_sekolah.insert(0, 'PERINGKAT', peringkat_sekolah.index + 1)

    # 3. Peringkat Kelas
    gabung['PERINGKAT_KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense')
    peringkat_kelas = gabung.sort_values(['KELAS', 'PERINGKAT_KELAS'])

    # Simpan ke Excel
    def unduh_excel():
        keluaran = BytesIO()
        with pd.ExcelWriter(keluaran, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
            peringkat_sekolah.to_excel(w, 'Peringkat Sekolah', False)
            peringkat_kelas.to_excel(w, 'Peringkat Kelas', False)
        return keluaran.getvalue()

    return {
        'rekap_kelas': rekap_kelas,
        'peringkat_sekolah': peringkat_sekolah,
        'peringkat_kelas': peringkat_kelas,
        'berkas_hasil': unduh_excel()
    }

# TAMPILAN UTAMA
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")

# MENU SAMPING
with st.sidebar:
    st.header("📝 Cara Pakai")
    st.info("""
    1. Siapkan file Excel (.xlsx)
    2. Nama kolom: No | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata
    3. Nama file: `7a.xlsx`, `7b.xlsx`, dst
    4. Unggah file → Lihat hasil → Unduh
    """)
    st.header("📤 Unggah File")
    unggahan = st.file_uploader("Pilih File", type="xlsx", accept_multiple_files=True)

# PROSES
hasil = proses_data(unggahan)

if not hasil:
    st.warning("⬅️ Silakan unggah file nilai terlebih dahulu")
    st.code("Contoh format isi file:\nNo | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata")
    st.stop()

# TAMPILAN HASIL
tab1, tab2, tab3 = st.tabs(["🏫 Rekap Nilai Kelas", "🏆 Peringkat Seluruh Sekolah", "📋 Peringkat Per Kelas"])

with tab1:
    st.subheader("Tabel Rekapitulasi Nilai")
    st.dataframe(hasil['rekap_kelas'], use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Daftar Peringkat Siswa Sekolah")
    st.dataframe(hasil['peringkat_sekolah'], use_container_width=True, hide_index=True)

with tab3:
    pilih_kelas = st.selectbox("Pilih Kelas", sorted(hasil['peringkat_kelas']['KELAS'].unique()))
    tampil = hasil['peringkat_kelas'][hasil['peringkat_kelas']['KELAS'] == pilih_kelas]
    st.dataframe(tampil, use_container_width=True, hide_index=True)

# TOMBOL UNDUH
st.download_button(
    label="📥 Unduh Semua Hasil (Excel)",
    data=hasil['berkas_hasil'],
    file_name="HASIL_NILAI_SEKOLAH.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
    use_container_width=True
)