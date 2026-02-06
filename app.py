import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import plotly.express as px


st.set_page_config(
    page_title="Dashboard UMKM Jawa Barat",
    layout="wide"
)

st.markdown(
    """
    <h1 style='margin-bottom:0;'>Dashboard UMKM Provinsi Jawa Barat</h1>
    <p style='color:gray;margin-top:4px;'>
    Analisis data UMKM Jawa Barat periode 2016–2023
    </p>
    """,
    unsafe_allow_html=True
)


df = pd.read_csv("UMKM_JABAR_2016_2023.csv")
coord = pd.read_csv("KOORDINAT_KAB_KOTA_JABAR.csv")


df["nama_kabupaten_kota"] = df["nama_kabupaten_kota"].astype(str).str.upper().str.strip()
df["jenis_usaha"] = df["jenis_usaha"].astype(str).str.upper().str.strip()
df["tahun"] = df["tahun"].astype(int)

coord["nama_kabupaten_kota"] = coord["nama_kabupaten_kota"].astype(str).str.upper().str.strip()


JENIS_USAHA_LIST = [
    "AGRIBISNIS",
    "AKSESORIS",
    "FASHION",
    "INDUSTRI",
    "MAKANAN",
    "MINUMAN",
    "KERAJINAN",
    "JASA",
    "KULINER",
    "OBAT-OBATAN"
]

df = df[df["jenis_usaha"].isin(JENIS_USAHA_LIST)]


st.markdown("##  Filter Data")

col_f1, col_f2 = st.columns(2)

with col_f1:
    tahun_filter = st.multiselect(
        "Tahun",
        sorted(df["tahun"].unique()),
        default=sorted(df["tahun"].unique())
    )

with col_f2:
    jenis_filter = st.multiselect(
        "Jenis Usaha",
        JENIS_USAHA_LIST,
        default=JENIS_USAHA_LIST
    )

tahun_pie = st.selectbox(
    "Tahun untuk Pie Chart",
    sorted(df["tahun"].unique()),
    index=len(sorted(df["tahun"].unique())) - 1
)

df_f = df[
    (df["tahun"].isin(tahun_filter)) &
    (df["jenis_usaha"].isin(jenis_filter))
]

st.divider()


m1, m2, m3 = st.columns(3)

m1.metric("Total UMKM", f"{int(df_f['jumlah_umkm'].sum()):,}")
m2.metric("Jumlah Kabupaten/Kota", df_f["nama_kabupaten_kota"].nunique())
m3.metric("Jumlah Jenis Usaha", df_f["jenis_usaha"].nunique())

st.divider()


st.markdown("##  Tabel Data UMKM")

table_df = (
    df_f
    .groupby(["tahun", "nama_kabupaten_kota", "jenis_usaha"])["jumlah_umkm"]
    .sum()
    .reset_index()
)

st.dataframe(
    table_df,
    use_container_width=True,
    height=350
)

st.caption("Tabel menampilkan data agregat UMKM per tahun, wilayah, dan jenis usaha.")

st.divider()


st.markdown("##  Tren Jumlah UMKM per Tahun")

line_df = (
    df_f
    .groupby("tahun")["jumlah_umkm"]
    .sum()
    .reset_index()
    .sort_values("tahun")
)

st.line_chart(line_df, x="tahun", y="jumlah_umkm")

st.caption("Grafik menunjukkan perkembangan total UMKM Jawa Barat dari tahun ke tahun.")

st.divider()

percent_df = (
    df_f
    .groupby(["tahun", "jenis_usaha"])["jumlah_umkm"]
    .sum()
    .reset_index()
)

percent_df["persen"] = (
    percent_df["jumlah_umkm"] /
    percent_df.groupby("tahun")["jumlah_umkm"].transform("sum")
) * 100

st.markdown("##  Komposisi UMKM per Jenis Usaha (Stacked Bar %)")

stack_df = (
    percent_df[percent_df["jenis_usaha"].isin(jenis_filter)]
    .sort_values("tahun")
)

fig = px.bar(
    stack_df,
    x="tahun",
    y="persen",
    color="jenis_usaha",
    title="Komposisi UMKM per Jenis Usaha (%)",
    labels={
        "persen": "Persentase (%)",
        "tahun": "Tahun",
        "jenis_usaha": "Jenis Usaha"
    },
    hover_data={
        "jumlah_umkm": ":,",
        "persen": ".2f"
    }
)

fig.update_layout(
    barmode="stack",
    yaxis_ticksuffix="%",
    legend_title_text="Jenis Usaha"
)

st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Stacked bar chart interaktif menggunakan Plotly. "
    "Hover untuk melihat jumlah dan persentase UMKM per jenis usaha."
)
