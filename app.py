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

html, body {
    font-family: "Inter", sans-serif;
}

p.main-title {
    font-size: 52px !important;
    font-weight: 900 !important;
    margin-bottom: 4px;
    color: #e5e7eb;
}

p.sub-title {
    color: #9ca3af;
    font-size: 18px;
    margin-top: 0;
    margin-bottom: 24px;
}

h3 {
    color: #e5e7eb;
    font-weight: 700;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #020617, #020617);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid rgba(34,197,94,0.35); /* hijau UMKM */
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}

div[data-testid="stMetricLabel"] {
    color: #9ca3af;
    font-size: 14px;
}

div[data-testid="stMetricValue"] {
    color: #22c55e;
    font-size: 28px;
    font-weight: 800;
}

div[data-testid="stDataFrame"] {
    background-color: #020617;
    border-radius: 14px;
    border: 1px solid #1e293b;
    padding: 10px;
}

div[data-testid="stPlotlyChart"],
div[data-testid="stPyplotChart"],
div[data-testid="stLineChart"] {
    background-color: #020617;
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #1e293b;
}

iframe {
    border-radius: 14px !important;
    border: 1px solid #1e293b;
}

hr {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 22px 0;
}

</style>

<p class="main-title">Dashboard UMKM Provinsi Jawa Barat</p>
<p class="sub-title">Analisis data UMKM periode 2016–2023</p>
""", unsafe_allow_html=True)

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
)

jenis_filter = st.sidebar.multiselect(
    "Pilih Jenis Usaha",
    options=JENIS_USAHA_LIST,
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
    # =====================
    # PETA
    # =====================
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
            color="#22c55e",
            fill=True,
            fill_opacity=0.7
        ).add_to(cluster)

    st_folium(m, width="100%", height=450)

    # =====================
    # TABEL (DI BAWAH PETA)
    # =====================
    st.markdown("### 📋 Detail Data UMKM")

    tabel_df = df_f[[
        "id",
        "nama_kabupaten_kota",
        "jenis_usaha",
        "jumlah_umkm",
        "tahun"
    ]].copy()

    tabel_df.columns = [
        "ID",
        "Kabupaten / Kota",
        "Jenis Usaha",
        "Jumlah UMKM",
        "Tahun"
    ]

    st.dataframe(
        tabel_df,
        use_container_width=True,
        height=400
    )

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
    
    st.markdown(f"###  Komposisi {tahun_pie}")
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




















