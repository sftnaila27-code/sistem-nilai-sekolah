import streamlit as st
import pandas as pd
from io import BytesIO

# KONFIGURASI DASAR
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# FUNGSI PENGOLAHAN DATA
def proses_data(unggah):
    data = []
    if not unggah:
        return None

    for berkas in unggah:
        try:
            # Ambil nama kelas dari nama file (contoh: 7a.xlsx -> 7A)
            nama_kelas = berkas.name.split('.')[0].upper()
            
            # Baca file Excel - DISESUAIKAN DENGAN FORMAT ASLI KAMU
            df = pd.read_excel(berkas)
            
            # BAGIAN PENTING: Menyesuaikan nama kolom persis seperti data kamu
            # Format asli kamu: |No|Nama Siswa|No Induk|MTK|B.Indo|B.Inggris|IPA|Rata-Rata|
            df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
            
            # Tambah kolom identitas kelas
            df['KELAS'] = nama_kelas
            
            # Ubah kolom nilai menjadi angka
            kolom_angka = ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
            for kolom in kolom_angka:
                df[kolom] = pd.to_numeric(df[kolom], errors='coerce')
            
            data.append(df)

        except Exception as e:
            st.error(f"❌ Gagal membaca: {berkas.name}")
            return None

    if not data:
        return None

    # Gabungkan semua data jadi satu
    gabung = pd.concat(data, ignore_index=True)

    # 1. REKAP NILAI PER KELAS
    rekap_kelas = gabung.groupby('KELAS')[kolom_angka].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={
        'MTK':'Matematika',
        'B.Indo':'Bahasa Indonesia',
        'B.Inggris':'Bahasa Inggris',
        'Rata-Rata':'Rata-Rata Kelas'
    })

    # 2. PERINGKAT SELURUH SEKOLAH
    peringkat_sekolah = gabung.sort_values('Rata-Rata', ascending=False).reset_index(drop=True)
    peringkat_sekolah.insert(0, 'PERINGKAT', peringkat_sekolah.index + 1)

    # 3. PERINGKAT DI DALAM KELAS
    gabung['PERINGKAT_KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense')
    peringkat_kelas = gabung.sort_values(['KELAS', 'PERINGKAT_KELAS'])

    # 4. BUAT FILE HASIL UNTUK DIUNDUH
    def buat_file_excel():
        keluaran = BytesIO()
        with pd.ExcelWriter(keluaran, engine='xlsxwriter') as penulis:
            gabung.to_excel(penulis, sheet_name='Data Lengkap', index=False)
            rekap_kelas.to_excel(penulis, sheet_name='Rekap Per Kelas', index=False)
            peringkat_sekolah.to_excel(penulis, sheet_name='Peringkat Sekolah', index=False)
            peringkat_kelas.to_excel(penulis, sheet_name='Peringkat Per Kelas', index=False)
        return keluaran.getvalue()

    return {
        'rekap_kelas': rekap_kelas,
        'peringkat_sekolah': peringkat_sekolah,
        'peringkat_kelas': peringkat_kelas,
        'file_hasil': buat_file_excel()
    }

# ======================================
# TAMPILAN UTAMA APLIKASI
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
st.markdown("---")

# MENU SAMPING
with st.sidebar:
    st.header("📝 PANDUAN PENGGUNAAN")
    st.success("""
    ✅ **Format File yang DITERIMA:**
    | No | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata |
    
    ✅ **Nama File:**
    `7a.xlsx`, `7b.xlsx`, `8a.xlsx`, dst
    """)
    st.header("📤 UNGGAH FILE")
    berkas_masuk = st.file_uploader("Pilih File Excel", type="xlsx", accept_multiple_files=True)

# PROSES DATA
hasil = proses_data(berkas_masuk)

if not hasil:
    st.warning("⚠️ Silakan unggah file nilai terlebih dahulu lewat menu di samping ⬅️")
    st.info("Pastikan urutan kolom **sama persis** seperti contoh di panduan.")
    st.stop()

# TAMPILKAN HASIL
tab1, tab2, tab3 = st.tabs(["📊 Rekap Kelas", "🏆 Peringkat Sekolah", "👥 Peringkat Per Kelas"])

with tab1:
    st.subheader("Rekapitulasi Nilai Rata-Rata Setiap Kelas")
    st.dataframe(hasil['rekap_kelas'], use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Daftar Urutan Nilai Siswa Seluruh Sekolah")
    st.dataframe(hasil['peringkat_sekolah'], use_container_width=True, hide_index=True)

with tab3:
    pilih_kelas = st.selectbox("Pilih Kelas", sorted(hasil['peringkat_kelas']['KELAS'].unique()))
    tampil_kelas = hasil['peringkat_kelas'][hasil['peringkat_kelas']['KELAS'] == pilih_kelas]
    st.dataframe(tampil_kelas, use_container_width=True, hide_index=True)

# TOMBOL UNDUH
st.markdown("---")
st.download_button(
    label="📥 UNDUH SEMUA HASIL (File Excel)",
    data=hasil['file_hasil'],
    file_name="HASIL_PENGOLAHAN_NILAI_SEKOLAH.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary",
    use_container_width=True
)