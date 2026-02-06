import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt


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


st.markdown("##  Peta Persebaran UMKM Jawa Barat")

map_df = (
    df_f
    .groupby("nama_kabupaten_kota", as_index=False)["jumlah_umkm"]
    .sum()
    .merge(coord, on="nama_kabupaten_kota", how="left")
    .dropna(subset=["latitude", "longitude"])
)

m = folium.Map(
    location=[-6.9, 107.6],
    zoom_start=6,
    tiles="OpenStreetMap"
)

cluster = MarkerCluster(disableClusteringAtZoom=10).add_to(m)

for _, r in map_df.iterrows():
    folium.Marker(
        location=[r["latitude"], r["longitude"]],
        popup=f"""
        <b>{r['nama_kabupaten_kota']}</b><br>
        Jumlah UMKM: {int(r['jumlah_umkm']):,}
        """
    ).add_to(cluster)

st_folium(m, width=1200, height=450)

st.caption(
    "Peta menggunakan marker clustering: zoom rendah menampilkan agregasi, "
    "dan akan terurai menjadi detail wilayah saat diperbesar."
)

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

st.markdown(f"##  Komposisi UMKM per Jenis Usaha ({tahun_pie})")

pie_df = (
    df_f[df_f["tahun"] == tahun_pie]      
    .groupby("jenis_usaha")["jumlah_umkm"]
    .sum()
    .reindex(jenis_filter)                 
    .dropna()
)

st.markdown(f"##  Komposisi UMKM per Jenis Usaha ({tahun_pie})")

pie_df = (
    percent_df[
        (percent_df["tahun"] == tahun_pie) &
        (percent_df["jenis_usaha"].isin(jenis_filter))
    ]
    .set_index("jenis_usaha")
    .reindex(jenis_filter)
    .dropna()
)

if pie_df.empty:
    st.warning("Tidak ada data untuk tahun dan jenis usaha yang dipilih.")
else:
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        pie_df["persen"],
        labels=pie_df.index,
        autopct="%1.1f%%",
        startangle=140
    )
    ax.axis("equal")

    st.pyplot(fig)

st.dataframe(
    percent_df[percent_df["tahun"] == tahun_pie]
    .sort_values("persen", ascending=False)
)


