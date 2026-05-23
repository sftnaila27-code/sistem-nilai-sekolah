# ==================================================
#       APLIKASI PENGOLAHAN NILAI SISWA
#   Dibuat untuk Sekolah - Tanpa Perlu Coding
# ==================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# ----------------------
# KONFIGURASI AWAL
# ----------------------
st.set_page_config(
    page_title="Sistem Nilai Sekolah",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Menyembunyikan pesan peringatan dan menu bawaan streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-18e3th9 {padding-top: 1rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----------------------
# FUNGSI UTAMA PENGOLAHAN
# ----------------------
def proses_data(uploaded_files):
    semua_data = []
    nama_file_list = []

    if not uploaded_files:
        return None, None

    # Membaca setiap file yang diunggah
    for file in uploaded_files:
        try:
            # Ambil nama kelas dari nama file (contoh: 7a.xlsx -> 7A)
            nama_kelas = file.name.split('.')[0].upper()
            nama_file_list.append(nama_kelas)

            # Baca isi file excel
            df = pd.read_excel(file, engine='openpyxl')
            
            # Menyesuaikan nama kolom agar seragam (sesuai format data Anda)
            df.columns = ['No', 'Nama Siswa', 'No Induk', 'MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
            
            # Tambahkan kolom identitas kelas
            df['KELAS'] = nama_kelas
            
            # Ubah tipe data nilai ke angka
            kolom_nilai = ['MTK', 'B.Indo', 'B.Inggris', 'IPA', 'Rata-Rata']
            for col in kolom_nilai:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            semua_data.append(df)

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {file.name}. Pastikan format sesuai contoh.")
            return None, None

    # Gabungkan semua data jadi satu
    if semua_data:
        data_utama = pd.concat(semua_data, ignore_index=True)
        
        # --- ANALISIS DATA ---
        
        # 1. Rekap Nilai Rata-rata Per Kelas
        rekap_kelas = data_utama.groupby('KELAS')[kolom_nilai].mean().round(2).reset_index()
        rekap_kelas = rekap_kelas.sort_values(by='Rata-Rata', ascending=False)
        rekap_kelas = rekap_kelas.rename(columns={
            'MTK': 'Matematika', 
            'B.Indo': 'Bahasa Indonesia', 
            'B.Inggris': 'Bahasa Inggris', 
            'IPA': 'IPA', 
            'Rata-Rata': 'Rata-Rata Kelas'
        })

        # 2. Peringkat Siswa Seluruh Sekolah
        peringkat_sekolah = data_utama.sort_values(by='Rata-Rata', ascending=False).reset_index(drop=True)
        peringkat_sekolah['PERINGKAT'] = peringkat_sekolah.index + 1

        # 3. Peringkat Siswa Per Kelas
        data_utama['PERINGKAT_KELAS'] = data_utama.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense')
        peringkat_kelas = data_utama.sort_values(by=['KELAS', 'PERINGKAT_KELAS'])

        # 4. Rata-rata Mata Pelajaran Sekolah
        rata_mapel = data_utama[kolom_nilai[:-1]].mean().round(2).reset_index()
        rata_mapel.columns = ['Mata Pelajaran', 'Nilai Rata-Rata']
        rata_mapel['Mata Pelajaran'] = rata_mapel['Mata Pelajaran'].map({
            'MTK': 'Matematika', 'B.Indo':'Bahasa Indonesia', 'B.Inggris':'Bahasa Inggris', 'IPA':'IPA'
        })

        hasil_analisis = {
            'data_lengkap': data_utama,
            'rekap_kelas': rekap_kelas,
            'peringkat_sekolah': peringkat_sekolah[['PERINGKAT','KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']],
            'peringkat_kelas': peringkat_kelas[['PERINGKAT_KELAS','KELAS','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']],
            'rata_mapel': rata_mapel
        }
        return hasil_analisis, nama_file_list

    return None, None

# Fungsi untuk mengunduh hasil ke Excel
def unduh_excel(hasil):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hasil['data_lengkap'].to_excel(writer, sheet_name='Data Lengkap', index=False)
        hasil['rekap_kelas'].to_excel(writer, sheet_name='Rekap Per Kelas', index=False)
        hasil['peringkat_sekolah'].to_excel(writer, sheet_name='Peringkat Sekolah', index=False)
        hasil['peringkat_kelas'].to_excel(writer, sheet_name='Peringkat Per Kelas', index=False)
    processed_data = output.getvalue()
    return processed_data

# ----------------------
# TAMPILAN APLIKASI
# ----------------------

def main():
    st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")
    st.markdown("---")

    # SIDEBAR - Panduan & Unggah File
    with st.sidebar:
        st.header("📝 Cara Penggunaan")
        st.info("""
        1. **Siapkan File:** Pastikan format file Excel sama persis dengan contoh (Nama kolom & urutan tidak diubah). Nama file gunakan kode kelas (contoh: `7a.xlsx`, `9b.xlsx`).
        2. **Unggah File:** Klik tombol di bawah ini, pilih SEMUA file nilai sekaligus.
        3. **Lihat Hasil:** Data akan diproses otomatis dan muncul grafik serta tabel.
        4. **Unduh:** Simpan hasil pengolahan ke komputer.
        """)

        st.header("📤 Unggah File Nilai")
        uploaded_files = st.file_uploader(
            "Pilih File Excel (.xlsx)", 
            type=["xlsx"], 
            accept_multiple_files=True,
            help="Bisa pilih lebih dari satu file sekaligus"
        )

    # JIKA BELUM ADA FILE DIUNGGAH
    if not uploaded_files:
        st.warning("⚠️ Silakan unggah file nilai terlebih dahulu melalui menu di samping.")
        
        # Tampilan Awal
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Format File yang Diterima")
            st.code("""
            | No | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata |
            |----|------------|----------|-----|--------|-----------|-----|-----------|
            """, language="markdown")
        with col2:
            st.subheader("✅ Keunggulan Sistem")
            st.markdown("""
            - Hitungan otomatis & akurat
            - Menampilkan peringkat kelas & sekolah
            - Grafik perbandingan otomatis
            - Hasil bisa disimpan ke Excel
            - **Tanpa perlu keahlian pemrograman**
            """)
        return

    # PROSES DATA JIKA SUDAH ADA FILE
    with st.spinner("🔄 Sedang memproses data... Mohon tunggu sebentar"):
        hasil, daftar_kelas = proses_data(uploaded_files)

    if hasil is None:
        st.error("Terjadi kesalahan dalam memproses data. Periksa kembali format file Anda.")
        return

    # ----------------------
    # MENU UTAMA HASIL
    # ----------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Ikhtisar & Grafik", 
        "🏫 Rekap Nilai Per Kelas", 
        "🏆 Peringkat Siswa", 
        "📄 Data Lengkap"
    ])

    # --- TAB 1: IKHTISAR & GRAFIK ---
    with tab1:
        st.subheader("📈 Analisis Grafik Sekolah")
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("**Perbandingan Rata-Rata Nilai Antar Kelas**")
            fig1 = px.bar(
                hasil['rekap_kelas'], 
                x='KELAS', 
                y='Rata-Rata Kelas',
                color='KELAS',
                text_auto='.2f',
                height=400
            )
            fig1.update_layout(showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)

        with col_graf2:
            st.markdown("**Rata-Rata Nilai Setiap Mata Pelajaran**")
            fig2 = px.pie(
                hasil['rata_mapel'], 
                values='Nilai Rata-Rata', 
                names='Mata Pelajaran',
                color_discrete_sequence=px.colors.sequential.RdBu,
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("📊 Detail Nilai Mata Pelajaran per Kelas")
        fig3 = px.line(
            hasil['rekap_kelas'].melt(id_vars='KELAS', value_vars=['Matematika', 'Bahasa Indonesia', 'Bahasa Inggris', 'IPA']),
            x='KELAS',
            y='value',
            color='variable',
            markers=True,
            labels={'value':'Nilai', 'variable':'Mata Pelajaran'},
            title="Perkembangan Nilai Mata Pelajaran Setiap Kelas"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --- TAB 2: REKAP PER KELAS ---
    with tab2:
        st.subheader("📋 Tabel Rekapitulasi Nilai Kelas")
        st.dataframe(hasil['rekap_kelas'], use_container_width=True, hide_index=True)

    # --- TAB 3: PERINGKAT ---
    with tab3:
        menu_peringkat = st.radio("Pilih Jenis Peringkat:", ["Peringkat Seluruh Sekolah", "Peringkat Per Kelas"], horizontal=True)
        
        if menu_peringkat == "Peringkat Seluruh Sekolah":
            st.dataframe(hasil['peringkat_sekolah'], use_container_width=True, hide_index=True)
        else:
            kelas_pilih = st.selectbox("Pilih Kelas", sorted(hasil['data_lengkap']['KELAS'].unique()))
            df_kelas = hasil['peringkat_kelas'][hasil['peringkat_kelas']['KELAS'] == kelas_pilih]
            st.dataframe(df_kelas, use_container_width=True, hide_index=True)

    # --- TAB 4: DATA LENGKAP ---
    with tab4:
        st.dataframe(hasil['data_lengkap'], use_container_width=True, hide_index=True)

    # ----------------------
    # TOMBOL UNDUH HASIL
    # ----------------------
    st.markdown("---")
    st.success("✅ Proses pengolahan selesai! Silakan unduh hasil di bawah ini.")
    
    excel_data = unduh_excel(hasil)
    st.download_button(
        label="📥 Unduh Semua Hasil (File Excel)",
        data=excel_data,
        file_name="HASIL_PENGOLAHAN_NILAI_SEKOLAH.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

if __name__ == "__main__":
    main()