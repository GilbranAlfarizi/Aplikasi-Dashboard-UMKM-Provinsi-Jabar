import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from streamlit_echarts import st_echarts


st.set_page_config(
    page_title="Dashboard UMKM Jawa Barat",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
html, body { font-family: "Inter", sans-serif; }

p.main-title {
    font-size: 52px;
    font-weight: 900;
    margin-bottom: 4px;
    color: #e5e7eb;
}

p.sub-title {
    color: #9ca3af;
    font-size: 18px;
    margin-bottom: 24px;
}

h3 { color: #e5e7eb; font-weight: 700; }

div[data-testid="stMetric"] {
    background-color: #020617;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid rgba(34,197,94,0.35);
}

div[data-testid="stMetricValue"] {
    color: #22c55e;
    font-size: 28px;
    font-weight: 800;
}

div[data-testid="stDataFrame"],
div[data-testid="stLineChart"],
div[data-testid="stPyplotChart"] {
    background-color: #020617;
    border-radius: 14px;
    border: 1px solid #1e293b;
    padding: 12px;
}

iframe {
    border-radius: 14px !important;
    border: 1px solid #1e293b;
}

hr {
    border-top: 1px solid #1e293b;
    margin: 28px 0;
}
</style>

<p class="main-title">Dashboard UMKM Provinsi Jawa Barat</p>
<p class="sub-title">Analisis data UMKM periode 2016–2023</p>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv("UMKM_JABAR_2016_2023.csv")
    coord = pd.read_csv("KOORDINAT_KAB_KOTA_JABAR.csv")

    df["nama_kabupaten_kota"] = df["nama_kabupaten_kota"].str.upper().str.strip()
    df["jenis_usaha"] = df["jenis_usaha"].str.upper().str.strip()
    df["tahun"] = df["tahun"].astype(int)

    coord["nama_kabupaten_kota"] = coord["nama_kabupaten_kota"].str.upper().str.strip()
    return df, coord

df, coord = load_data()


st.sidebar.header("Filter Data")

JENIS_USAHA_LIST = sorted(df["jenis_usaha"].unique())

tahun_filter = st.sidebar.multiselect(
    "Pilih Tahun",
    sorted(df["tahun"].unique())
)

jenis_filter = st.sidebar.multiselect(
    "Pilih Jenis Usaha",
    JENIS_USAHA_LIST
)

tahun_pie = st.sidebar.selectbox(
    "Tahun untuk Pie Chart",
    [None] + sorted(df["tahun"].unique()),
    format_func=lambda x: "— Pilih Tahun —" if x is None else str(x)
)

if not tahun_filter or not jenis_filter:
    st.warning("⚠️ Silakan pilih minimal satu Tahun dan satu Jenis Usaha di sidebar.")
    st.stop()

df_f = df[df["tahun"].isin(tahun_filter) & df["jenis_usaha"].isin(jenis_filter)]


col_map, col_kpi = st.columns([0.7, 0.3])

with col_map:
    st.markdown("### 🗺️ Peta Persebaran UMKM")

    map_df = (
        df_f.groupby("nama_kabupaten_kota", as_index=False)["jumlah_umkm"].sum()
        .merge(coord, on="nama_kabupaten_kota")
    )

    m = folium.Map(location=[-6.9, 107.6], zoom_start=6)
    cluster = MarkerCluster().add_to(m)

    for _, r in map_df.iterrows():
        folium.CircleMarker(
            [r["latitude"], r["longitude"]],
            radius=8,
            popup=f"<b>{r['nama_kabupaten_kota']}</b><br>{int(r['jumlah_umkm']):,}",
            color="#22c55e",
            fill=True,
            fill_opacity=0.7
        ).add_to(cluster)

    st_folium(m, height=450, width="100%")

with col_kpi:
    st.markdown("### 📊 Ringkasan")
    st.metric("Total UMKM", f"{int(df_f['jumlah_umkm'].sum()):,}")
    st.metric("Wilayah", f"{df_f['nama_kabupaten_kota'].nunique()} Kab/Kota")
    st.metric("Kategori", f"{df_f['jenis_usaha'].nunique()} Jenis")


st.markdown("---")

st.markdown("## 📋 Detail Data UMKM")

tabel_df = df_f[[
    "id",
    "nama_kabupaten_kota",
    "jenis_usaha",
    "jumlah_umkm",
    "tahun"
]].copy()

tabel_df.columns = ["ID", "Kabupaten / Kota", "Jenis Usaha", "Jumlah UMKM", "Tahun"]

st.dataframe(
    tabel_df,
    use_container_width=True,
    height=420,  
    hide_index=True
)

st.markdown("---")

col_trend, col_comp = st.columns([0.4, 0.8])

with col_trend:
    st.markdown("### 📈 Tren Tahunan")
    line_df = df_f.groupby("tahun")["jumlah_umkm"].sum()
    st.line_chart(line_df, height=300)

with col_comp:
    st.markdown(f"### 📊 Proporsi UMKM Tahun {tahun_pie}")

    if tahun_pie:
        bar_df = (
            df[
                (df["tahun"] == tahun_pie) &
                (df["jenis_usaha"].isin(jenis_filter))
            ]
            .groupby("jenis_usaha")["jumlah_umkm"]
            .sum()
            .reset_index()
        )

        option = {
            "backgroundColor": "transparent",
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": bar_df["jenis_usaha"].tolist(),
                "axisLabel": {"rotate": 30, "color": "#e5e7eb"}
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "#e5e7eb"},
                "splitLine": {"lineStyle": {"color": "#1e293b"}}
            },
            "series": [{
                "type": "bar",
                "data": bar_df["jumlah_umkm"].tolist(),
                "itemStyle": {"color": "#22c55e"}
            }]
        }

        st_echarts(option, height="300px")


