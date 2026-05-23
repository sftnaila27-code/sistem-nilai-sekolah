import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# Konfigurasi Dasar
st.set_page_config(page_title="Nilai Sekolah", page_icon="🏫", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# Fungsi Pengolahan
def proses_data(unggah):
    data = []
    if not unggah: return None
    
    for f in unggah:
        kelas = f.name.split('.')[0].upper()
        try:
            df = pd.read_excel(f)
            df.columns = ['No','Nama Siswa','No Induk','MTK','B.Indo','B.Inggris','IPA','Rata-Rata']
            df['KELAS'] = kelas
            for c in ['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            data.append(df)
        except:
            st.error(f"File {f.name} salah format!")
            return None

    if not data: return None
    gabung = pd.concat(data, ignore_index=True)

    # Analisis
    rekap_kelas = gabung.groupby('KELAS')[['MTK','B.Indo','B.Inggris','IPA','Rata-Rata']].mean().round(2).reset_index()
    rekap_kelas = rekap_kelas.rename(columns={'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','Rata-Rata':'Rata-Rata Kelas'})
    rekap_kelas = rekap_kelas.sort_values('Rata-Rata Kelas', ascending=False)

    peringkat_sekolah = gabung.sort_values('Rata-Rata', ascending=False).reset_index(drop=True)
    peringkat_sekolah.insert(0, 'Peringkat', peringkat_sekolah.index+1)

    gabung['Peringkat Kelas'] = gabung.groupby('KELAS')['Rata-Rata'].rank(ascending=False, method='dense')
    peringkat_kelas = gabung.sort_values(['KELAS','Peringkat Kelas'])

    rata_mapel = gabung[['MTK','B.Indo','B.Inggris','IPA']].mean().round(2).reset_index()
    rata_mapel.columns = ['Mapel','Nilai']
    rata_mapel['Mapel'] = rata_mapel['Mapel'].map({'MTK':'Matematika','B.Indo':'Bahasa Indonesia','B.Inggris':'Bahasa Inggris','IPA':'IPA'})

    # Simpan ke Excel
    def simpan_excel():
        o = BytesIO()
        with pd.ExcelWriter(o) as w:
            gabung.to_excel(w, 'Data Lengkap', False)
            rekap_kelas.to_excel(w, 'Rekap Kelas', False)
            peringkat_sekolah.to_excel(w, 'Peringkat Sekolah', False)
            peringkat_kelas.to_excel(w, 'Peringkat Kelas', False)
        return o.getvalue()

    return {
        'rekap_kelas':rekap_kelas,
        'peringkat_sekolah':peringkat_sekolah,
        'peringkat_kelas':peringkat_kelas,
        'rata_mapel':rata_mapel,
        'file_excel':simpan_excel()
    }

# TAMPILAN UTAMA
st.title("🏫 SISTEM PENGOLAHAN NILAI SISWA")

with st.sidebar:
    st.info("**Cara Pakai:**\n1. Siapkan file .xlsx\n2. Nama kolom: No, Nama Siswa, No Induk, MTK, B.Indo, B.Inggris, IPA, Rata-Rata\n3. Nama file: 7a.xlsx, 8b.xlsx, dst")
    berkas = st.file_uploader("Unggah File", type='xlsx', accept_multiple_files=True)

hasil = proses_data(berkas)

if not hasil:
    st.warning("⬅️ Silakan unggah file nilai di menu samping")
    st.code("Contoh format:\n| No | Nama Siswa | No Induk | MTK | B.Indo | B.Inggris | IPA | Rata-Rata |")
    st.stop()

# Tabs
t1,t2,t3 = st.tabs(["📊 Grafik","🏫 Rekap Kelas","🏆 Peringkat"])

with t1:
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Rata-Rata Kelas")
        st.plotly_chart(px.bar(hasil['rekap_kelas'], x='KELAS', y='Rata-Rata Kelas', color='KELAS', text_auto='.1f'), use_container_width=True)
    with c2:
        st.subheader("Rata-Rata Mata Pelajaran")
        st.plotly_chart(px.pie(hasil['rata_mapel'], values='Nilai', names='Mapel'), use_container_width=True)

with t2:
    st.subheader("Tabel Rekapitulasi")
    st.dataframe(hasil['rekap_kelas'], use_container_width=True, hide_index=True)

with t3:
    pilih = st.radio("Lihat:", ["Seluruh Sekolah","Per Kelas"], horizontal=True)
    if pilih == "Seluruh Sekolah":
        st.dataframe(hasil['peringkat_sekolah'], use_container_width=True, hide_index=True)
    else:
        kls = st.selectbox("Pilih Kelas", sorted(hasil['peringkat_kelas']['KELAS'].unique()))
        st.dataframe(hasil['peringkat_kelas'][hasil['peringkat_kelas']['KELAS']==kls], use_container_width=True, hide_index=True)

# Unduh
st.download_button("📥 Unduh Semua Hasil (.xlsx)", hasil['file_excel'], "Hasil_Nilai_Sekolah.xlsx", use_container_width=True, type='primary')