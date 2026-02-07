import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard UMKM Jawa Barat",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 32px; }

.main-title {
    font-size: 56px;
    font-weight: 800;
    margin-bottom: 0;
}

.sub-title {
    color: gray;
    font-size: 18px;
    margin-top: 0;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="main-title">Dashboard UMKM Provinsi Jawa Barat</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="sub-title">Analisis data UMKM periode 2016–2023</p>',
    unsafe_allow_html=True
)


@st.cache_data
def load_data():
    df = pd.read_csv("UMKM_JABAR_2016_2023.csv")
    coord = pd.read_csv("KOORDINAT_KAB_KOTA_JABAR.csv")
    
    
    df["nama_kabupaten_kota"] = df["nama_kabupaten_kota"].astype(str).str.upper().str.strip()
    df["jenis_usaha"] = df["jenis_usaha"].astype(str).str.upper().str.strip()
    df["tahun"] = df["tahun"].astype(int)
    coord["nama_kabupaten_kota"] = coord["nama_kabupaten_kota"].astype(str).str.upper().str.strip()
    
    return df, coord

df, coord = load_data()

st.sidebar.header("Filter Data")
JENIS_USAHA_LIST = sorted(["AGRIBISNIS", "AKSESORIS", "FASHION", "INDUSTRI", "MAKANAN", "MINUMAN", "KERAJINAN", "JASA", "KULINER", "OBAT-OBATAN"])

tahun_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df["tahun"].unique()),
    default=[2023]
)

jenis_filter = st.sidebar.multiselect(
    "Pilih Jenis Usaha",
    options=JENIS_USAHA_LIST,
    default=JENIS_USAHA_LIST[:3]
)

tahun_pie = st.sidebar.selectbox(
    "Tahun untuk Pie Chart",
    sorted(df["tahun"].unique()),
    index=len(df["tahun"].unique()) - 1
)

if not tahun_filter or not jenis_filter:
    st.warning("⚠️ Silakan pilih minimal satu Tahun dan satu Jenis Usaha di sidebar.")
    st.stop()

df_f = df[(df["tahun"].isin(tahun_filter)) & (df["jenis_usaha"].isin(jenis_filter))]

col_main, col_side = st.columns([0.7, 0.3])

with col_main:
    st.markdown("### 🗺️ Peta Persebaran UMKM")
    map_df = (
        df_f.groupby("nama_kabupaten_kota", as_index=False)["jumlah_umkm"].sum()
        .merge(coord, on="nama_kabupaten_kota", how="left")
        .dropna(subset=["latitude", "longitude"])
    )

    m = folium.Map(location=[-6.9, 107.6], zoom_start=8)
    cluster = MarkerCluster().add_to(m)

    for _, r in map_df.iterrows():
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=8,
            popup=f"<b>{r['nama_kabupaten_kota']}</b><br>Total: {int(r['jumlah_umkm']):,}",
            color="#1f77b4",
            fill=True,
            fill_opacity=0.7
        ).add_to(cluster)

    st_folium(m, width="100%", height=450)
    
    st.markdown("### 📋 Detail Data")
    st.dataframe(df_f, use_container_width=True, height=300)

with col_side:
    st.markdown("### 📊 Ringkasan")
    st.metric("Total UMKM", f"{int(df_f['jumlah_umkm'].sum()):,}")
    st.metric("Wilayah", f"{df_f['nama_kabupaten_kota'].nunique()} Kab/Kota")
    st.metric("Kategori", f"{df_f['jenis_usaha'].nunique()} Jenis")
    
    st.markdown("---")
    
    st.markdown("### 📈 Tren Tahunan")
    line_df = df_f.groupby("tahun")["jumlah_umkm"].sum().reset_index()
    st.line_chart(line_df.set_index("tahun"), height=200)
    
    st.markdown("---")
    
    st.markdown(f"### 🍰 Komposisi {tahun_pie}")
    pie_data = (
        df[(df["tahun"] == tahun_pie) & (df["jenis_usaha"].isin(jenis_filter))]
        .groupby("jenis_usaha")["jumlah_umkm"].sum()
    )
    
    if not pie_data.empty:
        fig, ax = plt.subplots(figsize=(4, 4))
        colors = plt.cm.Paired(range(len(pie_data)))
        ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'fontsize': 8})
        ax.axis('equal')
        fig.patch.set_facecolor('none') 
        st.pyplot(fig)
    else:
        st.info("Pilih data untuk melihat komposisi")



