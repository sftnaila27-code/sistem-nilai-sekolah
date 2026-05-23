import streamlit as st
import pandas as pd
import re
from io import BytesIO

# KONFIGURASI
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# FUNGSI UBAH TEKS MARKDOWN KE TABEL
def baca_file_format_kamu(berkas):
    try:
        # Baca isi file sebagai teks
        isi = berkas.read().decode('utf-8')
        baris = isi.strip().split('\n')
        
        # Cari baris header dan data
        data_bersih = []
        header = None
        
        for b in baris:
            b = b.strip()
            if not b or '---' in b or '===' in b:
                continue
            # Ambil bagian dalam tanda |
            potong = [kolom.strip() for kolom in b.split('|') if kolom.strip()]
            
            if len(potong) >= 8: # Pastikan ada 8 kolom
                if header is None:
                    header = potong
                else:
                    data_bersih.append(potong)
        
        if not header or not data_bersih:
            return None
        
        # Buat DataFrame
        df = pd.DataFrame(data_bersih, columns=header)
        
        # Ubah nama kolom agar seragam
        df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
        
        # Ubah ke angka
        kolom_angka = ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
        for kolom in kolom_angka:
            df[kolom] = pd.to_numeric(df[kolom], errors='coerce')
        
        # Tambah kolom kelas dari nama file
        nama_kelas = berkas.name.split('.')[0].upper()
        df['KELAS'] = nama_kelas
        
        return df

    except Exception as e:
        st.error(f"❌ Gagal baca: {berkas.name} | Pesan: {str(e)}")
        return None

# FUNGSI PENGOLAHAN UTAMA
def proses_data(unggah):
    semua_data = []
    if not unggah:
        return None

    for berkas in unggah:
        df = baca_file_format_kamu(berkas)
        if df is None:
            return None
        semua_data.append(df)

    if not semua_data:
        return None

    # Gabungkan semua
    gabung = pd.concat(semua_data, ignore_index=True)

    # 1. Rekap Kelas
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

# ======================================
# TAMPILAN APLIKASI
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
st.markdown("---")

# MENU SAMPING
with st.sidebar:
    st.header("📝 CARA PAKAI")
    st.success("""
    ✅ Format file yang diterima:
    File berisi teks/tabel seperti ini:
    |No|Nama Siswa|No Induk|MTK|B.Indo|B.Inggris|IPA|Rata-Rata|
    
    ✅ Nama File: `7a.xlsx`, `7b.xlsx`, dst
    """)
    st.header("📤 UNGGAH FILE")
    unggahan = st.file_uploader("Pilih File", type=["xlsx","txt"], accept_multiple_files=True)

# PROSES
hasil = proses_data(unggahan)

if not hasil:
    st.warning("⬅️ Silakan unggah file nilai di menu samping")
    st.info("Kode ini sudah disesuaikan dengan format file kamu yang asli.")
    st.stop()

# TAMPILKAN HASIL
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