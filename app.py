import streamlit as st
import pandas as pd
import re
from io import BytesIO

# ======================================
# KONFIGURASI DASAR
# ======================================
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# ======================================
# FUNGSI PEMBACA FILE (KHUSUS FORMAT ANDA)
# ======================================
def proses_file(berkas):
    try:
        # Baca isi file sebagai teks murni
        isi_teks = berkas.read().decode('utf-8', errors='ignore')
        barisan = isi_teks.strip().split('\n')
        
        data_list = []
        header = None

        for baris in barisan:
            baris = baris.strip()
            if not baris:
                continue
            
            # Hanya ambil baris yang ada tanda | pemisah
            if baris.startswith('|') and baris.endswith('|'):
                # Bersihkan dan potong per kolom
                kolom = [x.strip() for x in baris.split('|') if x.strip()]
                
                # Abaikan baris pemisah ---
                if '---' in baris or len(kolom) < 7:
                    continue

                if header is None:
                    header = kolom # Ambil judul kolom
                else:
                    data_list.append(kolom) # Ambil data

        if not header or not data_list:
            return None

        # Buat Tabel
        df = pd.DataFrame(data_list, columns=header)

        # SAMAKAN NAMA KOLOM PERSIS DENGAN DATA KAMU
        df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']

        # Ubah ke Angka
        kolom_angka = ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
        for k in kolom_angka:
            df[k] = pd.to_numeric(df[k], errors='coerce')

        # Tambah Nama Kelas dari Nama File
        nama_kelas = berkas.name.split('.')[0].upper()
        df['KELAS'] = nama_kelas

        return df

    except Exception as e:
        st.error(f"❌ Gagal baca: {berkas.name}")
        return None

# ======================================
# PENGOLAHAN UTAMA
# ======================================
def olah_semua(unggahan):
    semua_dataframe = []
    if not unggahan:
        return None

    for f in unggahan:
        hasil_baca = proses_file(f)
        if hasil_baca is None:
            return None
        semua_dataframe.append(hasil_baca)

    if not semua_dataframe:
        return None

    # Gabungkan Semua
    gabung = pd.concat(semua_dataframe, ignore_index=True)

    # 1. Rekap Rata-Rata Kelas
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={
        'MTK':'Matematika', 'B.Indo':'Bahasa Indonesia', 'B.Inggris':'Bahasa Inggris', 'Rata-Rata':'Rata-Rata Kelas'
    })

    # 2. Peringkat Sekolah
    peringkat_sekolah = gabung.sort_values('Rata-Rata', ascending=False).reset_index(drop=True)
    peringkat_sekolah.insert(0, 'PERINGKAT', peringkat_sekolah.index + 1)

    # 3. Peringkat Kelas
    gabung['PERINGKAT_KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense')
    peringkat_kelas = gabung.sort_values(['KELAS', 'PERINGKAT_KELAS'])

    # 4. Simpan ke Excel
    def simpan():
        out = BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
            peringkat_sekolah.to_excel(w, 'Peringkat Sekolah', False)
            peringkat_kelas.to_excel(w, 'Peringkat Kelas', False)
        return out.getvalue()

    return {
        'rekap': rekap_kelas,
        'peringkat_s': peringkat_sekolah,
        'peringkat_k': peringkat_kelas,
        'file_hasil': simpan()
    }

# ======================================
# TAMPILAN WEB
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
st.markdown("---")

# MENU SAMPING
with st.sidebar:
    st.header("📝 CARA PAKAI")
    st.success("""
    ✅ **Format File DITERIMA:**
    File berisi tabel dengan garis | seperti ini:
    |No|Nama Siswa|No Induk|MTK|B.Indo|B.Inggris|IPA|Rata-Rata|

    ✅ **Nama File:**
    `7a.xlsx`, `7b.xlsx`, `8a.xlsx`, dst
    """)
    st.header("📤 UNGGAH FILE")
    masuk = st.file_uploader("Pilih File", type=["xlsx", "txt"], accept_multiple_files=True)

# PROSES
data_akhir = olah_semua(masuk)

if not data_akhir:
    st.warning("⚠️ Silakan unggah file nilai terlebih dahulu ⬅️")
    st.info("Kode ini sudah disesuaikan khusus agar bisa membaca format file kamu yang asli.")
    st.stop()

# TAMPILKAN HASIL
tab1, tab2, tab3 = st.tabs(["🏫 Rekap Nilai Kelas", "🏆 Peringkat Sekolah", "👥 Peringkat Per Kelas"])

with tab1:
    st.subheader("Tabel Rekapitulasi Nilai Rata-Rata")
    st.dataframe(data_akhir['rekap'], use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Daftar Urutan Nilai Seluruh Sekolah")
    st.dataframe(data_akhir['peringkat_s'], use_container_width=True, hide_index=True)

with tab3:
    pilih = st.selectbox("Pilih Kelas", sorted(data_akhir['peringkat_k']['KELAS'].unique()))
    tampil = data_akhir['peringkat_k'][data_akhir['peringkat_k']['KELAS'] == pilih]
    st.dataframe(tampil, use_container_width=True, hide_index=True)

# TOMBOL UNDUH
st.markdown("---")
st.download_button(
    label="📥 UNDUH SEMUA HASIL (Excel)",
    data=data_akhir['file_hasil'],
    file_name="HASIL_OLAH_NILAI_SEKOLAH.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
    use_container_width=True
)