import streamlit as st
import pandas as pd
from io import BytesIO

# ======================================
# KONFIGURASI
# ======================================
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# ======================================
# FUNGSI BACA FILE (KHUSUS FORMAT ANDA)
# ======================================
def baca_file(berkas):
    try:
        # Baca sebagai teks biasa
        isi = berkas.read().decode('utf-8', errors='ignore')
        baris = isi.strip().split('\n')
        
        data = []
        header = None

        for b in baris:
            b = b.strip()
            if not b: continue
            if '|' not in b: continue
            if '---' in b: continue

            kolom = [x.strip() for x in b.split('|') if x.strip()]
            
            if len(kolom) >= 8:
                if header is None:
                    header = kolom
                else:
                    data.append(kolom)

        if not header or not data:
            st.error("❌ Isi file kosong atau format salah!")
            return None

        # Buat tabel
        df = pd.DataFrame(data, columns=header)

        # Samakan nama kolom PERSIS
        df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']

        # Ubah ke angka
        for kol in ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']:
            df[kol] = pd.to_numeric(df[kol], errors='coerce')

        # Tambah Kelas
        nama_kelas = berkas.name.split('.')[0].upper()
        df['KELAS'] = nama_kelas

        return df

    except Exception as e:
        st.error(f"❌ Gagal baca: {berkas.name} | Error: {str(e)}")
        return None

# ======================================
# PENGOLAHAN UTAMA
# ======================================
def proses_semua(daftar_file):
    semua = []
    if not daftar_file:
        return None

    st.info("⏳ Sedang membaca file... Mohon tunggu")
    
    for f in daftar_file:
        st.write(f"🔄 Memproses: {f.name}")
        hasil = baca_file(f)
        if hasil is None:
            return None
        semua.append(hasil)

    if not semua:
        return None

    # Gabungkan
    gabung = pd.concat(semua, ignore_index=True)
    st.success("✅ Semua file berhasil dibaca!")

    # ANALISIS
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata', ascending=False)
    rekap_kelas = rekap_kelas.rename(columns={
        'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','Rata-Rata':'Rata-Rata Kelas'
    })

    peringkat_sekolah = gabung.sort_values('Rata-Rata', ascending=False).reset_index(drop=True)
    peringkat_sekolah.insert(0, 'PERINGKAT', peringkat_sekolah.index + 1)

    gabung['PERINGKAT_KELAS'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense')
    peringkat_kelas = gabung.sort_values(['KELAS', 'PERINGKAT_KELAS'])

    # Simpan Excel
    def simpan_excel():
        o = BytesIO()
        with pd.ExcelWriter(o, engine='xlsxwriter') as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
            peringkat_sekolah.to_excel(w, 'Peringkat Sekolah', False)
            peringkat_kelas.to_excel(w, 'Peringkat Kelas', False)
        return o.getvalue()

    return {
        'rekap': rekap_kelas,
        'peringkat_s': peringkat_sekolah,
        'peringkat_k': peringkat_kelas,
        'file_hasil': simpan_excel()
    }

# ======================================
# TAMPILAN UTAMA
# ======================================
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
st.markdown("---")

# MENU SAMPING
with st.sidebar:
    st.header("📝 CARA PAKAI")
    st.code("Format: |No|Nama Siswa|No Induk|MTK|B.Indo|B.Inggris|IPA|Rata-Rata|")
    st.header("📤 UNGGAH FILE")
    berkas = st.file_uploader("Pilih File", type=["xlsx", "txt"], accept_multiple_files=True)

# JALANKAN PROSES
hasil = proses_semua(berkas)

# TAMPILKAN HASIL (DIPAKSA MUNCUL)
if hasil:
    st.success("✅ PROSES SELESAI! HASIL DI BAWAH INI:")
    tab1, tab2, tab3 = st.tabs(["🏫 Rekap Kelas", "🏆 Peringkat Sekolah", "👥 Peringkat Kelas"])

    with tab1:
        st.subheader("Tabel Rekapitulasi Nilai")
        st.dataframe(hasil['rekap'], use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Daftar Peringkat Sekolah")
        st.dataframe(hasil['peringkat_s'], use_container_width=True, hide_index=True)

    with tab3:
        pilih = st.selectbox("Pilih Kelas", sorted(hasil['peringkat_k']['KELAS'].unique()))
        st.dataframe(hasil['peringkat_k'][hasil['peringkat_k']['KELAS'] == pilih], use_container_width=True, hide_index=True)

    # Tombol Unduh
    st.markdown("---")
    st.download_button(
        label="📥 UNDUH HASIL EXCEL",
        data=hasil['file_hasil'],
        file_name="HASIL_NILAI_SEKOLAH.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

else:
    st.warning("⚠️ Belum ada file atau file gagal dibaca.")
    st.info("Pastikan isi file ada tanda garis pemisah | dan ada 8 kolom data.")