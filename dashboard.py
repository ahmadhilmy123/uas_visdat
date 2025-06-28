import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Dashboard Pendidikan Indonesia",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .kpi-container {
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 2rem;
    }
    .insight-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Data_Visdat.csv")
        df['tahun'] = df['tahun'].astype(str)
        df['nilai'] = pd.to_numeric(df['nilai'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("File 'Data_Visdat.csv' tidak ditemukan. Pastikan file ada di direktori yang sama!")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# ===== HEADER =====
st.markdown("""
<div class="main-header">
    <h1>📚 Dashboard Visualisasi Data Pendidikan Indonesia</h1>
    <p>Analisis Komprehensif Indikator Pendidikan Nasional</p>
</div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
st.sidebar.markdown("## 🎛️ Kontrol Dashboard")
st.sidebar.markdown("---")

indikator_list = df['indikator'].unique()
tahun_list = sorted(df['tahun'].unique())

indikator = st.sidebar.selectbox(
    "📊 Pilih Indikator",
    indikator_list,
    help="Pilih indikator pendidikan yang ingin dianalisis"
)

tahun = st.sidebar.selectbox(
    "📅 Pilih Tahun",
    tahun_list,
    help="Pilih tahun untuk analisis ranking provinsi"
)

# Filter tambahan
st.sidebar.markdown("### 🔍 Filter Lanjutan")
provinsi_list = ['Semua'] + sorted(df['nama_provinsi'].unique())
provinsi_filter = st.sidebar.multiselect(
    "🏛️ Pilih Provinsi (Opsional)",
    provinsi_list,
    default=['Semua'],
    help="Kosongkan untuk menampilkan semua provinsi"
)

# ===== STATISTIK UTAMA =====
st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏛️ Total Provinsi", df['nama_provinsi'].nunique())
with col2:
    st.metric("📅 Rentang Tahun", f"{min(tahun_list)} - {max(tahun_list)}")
with col3:
    st.metric("📊 Jenis Indikator", len(indikator_list))
with col4:
    st.metric("📋 Total Record", f"{len(df):,}")
st.markdown('</div>', unsafe_allow_html=True)

# ===== FILTER DATA =====
if 'Semua' not in provinsi_filter and provinsi_filter:
    df_filtered = df[df['nama_provinsi'].isin(provinsi_filter)]
else:
    df_filtered = df

# ===== VISUALISASI =====

# 1. LINE CHART - Tren Waktu
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.subheader(f"📈 Tren {indikator} dari Waktu ke Waktu")
line_df = df_filtered[df_filtered['indikator'] == indikator].groupby('tahun')['nilai'].agg(['mean', 'std']).reset_index()
line_df.columns = ['tahun', 'rata_rata', 'std_dev']

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=line_df['tahun'],
    y=line_df['rata_rata'],
    mode='lines+markers',
    name='Rata-rata',
    line=dict(color='#667eea', width=3),
    marker=dict(size=8, color='#667eea')
))
# Area standar deviasi (warna soft)
fig_line.add_trace(go.Scatter(
    x=line_df['tahun'],
    y=line_df['rata_rata'] + line_df['std_dev'],
    mode='lines',
    line=dict(width=0),
    showlegend=False
))
fig_line.add_trace(go.Scatter(
    x=line_df['tahun'],
    y=line_df['rata_rata'] - line_df['std_dev'],
    fill='tonexty',
    mode='lines',
    line=dict(width=0),
    fillcolor='rgba(102, 126, 234, 0.12)',
    name='±1 Std Dev'
))
fig_line.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Nilai",
    hovermode='x unified',
    template='simple_white',
    height=400,
    showlegend=False
)
st.plotly_chart(fig_line, use_container_width=True)
avg_change = line_df['rata_rata'].iloc[-1] - line_df['rata_rata'].iloc[0] if len(line_df) > 1 else 0
st.markdown(f"""
<div class="insight-box">
    <strong>💡 Insight:</strong>
    Perubahan rata-rata {indikator} dari {min(tahun_list)} ke {max(tahun_list)}:
    <strong>{avg_change:+.2f}</strong>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 2. BAR CHART - Ranking Provinsi (Top 10 & Bottom 10)
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader(f"🏆 Top 10 Provinsi - {indikator} ({tahun})")
    bar_df = df_filtered[(df_filtered['indikator'] == indikator) & (df_filtered['tahun'] == tahun)]
    bar_df = bar_df.groupby('nama_provinsi')['nilai'].mean().sort_values(ascending=False).head(10)
    fig_bar = px.bar(
        x=bar_df.values,
        y=bar_df.index,
        orientation='h',
        color_discrete_sequence=['#667eea'],
        labels={'x': 'Nilai', 'y': 'Provinsi'}
    )
    fig_bar.update_layout(
        xaxis_title="Nilai",
        yaxis_title="Provinsi",
        height=350,
        template='simple_white'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader(f"📉 Bottom 10 Provinsi - {indikator} ({tahun})")
    bottom_df = df_filtered[(df_filtered['indikator'] == indikator) & (df_filtered['tahun'] == tahun)]
    bottom_df = bottom_df.groupby('nama_provinsi')['nilai'].mean().sort_values(ascending=True).head(10)
    fig_bottom = px.bar(
        x=bottom_df.values,
        y=bottom_df.index,
        orientation='h',
        color_discrete_sequence=['#a5b4fc'],
        labels={'x': 'Nilai', 'y': 'Provinsi'}
    )
    fig_bottom.update_layout(
        xaxis_title="Nilai",
        yaxis_title="Provinsi",
        height=350,
        template='simple_white'
    )
    st.plotly_chart(fig_bottom, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. HEATMAP - Distribusi
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.subheader(f"🗺️ Heatmap Distribusi {indikator} Antar Provinsi & Tahun")
heatmap_df = df_filtered[df_filtered['indikator'] == indikator].pivot_table(
    index='nama_provinsi',
    columns='tahun',
    values='nilai',
    aggfunc='mean'
)
if len(heatmap_df) > 20:
    provinsi_top = heatmap_df.mean(axis=1).sort_values(ascending=False).head(20).index
    heatmap_df = heatmap_df.loc[provinsi_top]
fig_heatmap = px.imshow(
    heatmap_df.values,
    x=heatmap_df.columns,
    y=heatmap_df.index,
    color_continuous_scale='Blues',
    aspect='auto'
)
fig_heatmap.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Provinsi",
    height=500,
    template='simple_white',
    coloraxis_showscale=True
)
st.plotly_chart(fig_heatmap, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 4. SCATTER PLOT - Korelasi
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.subheader("📊 Analisis Korelasi: Harapan vs Rata-rata Lama Sekolah")
pivot = df_filtered.pivot_table(
    index=['nama_provinsi', 'tahun'],
    columns='indikator',
    values='nilai'
).reset_index()
if {'Harapan Lama Sekolah', 'Rata-rata Lama Sekolah'}.issubset(df['indikator'].unique()):
    pivot_clean = pivot.dropna(subset=['Harapan Lama Sekolah', 'Rata-rata Lama Sekolah'])
    fig_scatter = px.scatter(
        pivot_clean,
        x='Harapan Lama Sekolah',
        y='Rata-rata Lama Sekolah',
        color='tahun',
        color_discrete_sequence=px.colors.sequential.Blues,
        hover_data=['nama_provinsi'],
        trendline="ols"
    )
    fig_scatter.update_layout(
        height=400,
        template='simple_white',
        showlegend=False
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    corr = pivot_clean['Harapan Lama Sekolah'].corr(pivot_clean['Rata-rata Lama Sekolah'])
    st.markdown(f"""
    <div class="insight-box">
        <strong>📈 Korelasi:</strong> {corr:.3f}
        <br><strong>Interpretasi:</strong>
        {'Korelasi sangat kuat' if abs(corr) > 0.8 else 'Korelasi kuat' if abs(corr) > 0.6 else 'Korelasi sedang' if abs(corr) > 0.4 else 'Korelasi lemah'}
        antara Harapan dan Rata-rata Lama Sekolah
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("⚠️ Indikator 'Harapan Lama Sekolah' dan 'Rata-rata Lama Sekolah' tidak ditemukan dalam data.")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BOX PLOT - Distribusi & Outlier
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.subheader(f"📦 Box Plot - {indikator}")
box_data = df_filtered[df_filtered['indikator'] == indikator]
if not box_data.empty:
    fig_box = px.box(
        box_data,
        y='nilai',
        points='outliers',
        color_discrete_sequence=['#667eea']
    )
    fig_box.update_layout(
        height=300,
        template='simple_white',
        showlegend=False
    )
    st.plotly_chart(fig_box, use_container_width=True)
else:
    st.info("Data tidak tersedia untuk box plot.")
st.markdown('</div>', unsafe_allow_html=True)

# ===== ANALISIS STATISTIK LANJUTAN =====
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.subheader("📊 Analisis Statistik Lanjutan")
analisis_data = df_filtered[df_filtered['indikator'] == indikator]['nilai']
if analisis_data.empty or analisis_data.isnull().all():
    st.warning("Data tidak tersedia untuk indikator ini.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "📏 Rata-rata",
            f"{analisis_data.mean():.2f}",
            delta=f"±{analisis_data.std():.2f}",
            help="Nilai rata-rata dengan standar deviasi"
        )
    with col2:
        st.metric(
            "📐 Median",
            f"{analisis_data.median():.2f}",
            help="Nilai tengah distribusi"
        )
    with col3:
        st.metric(
            "📊 Min - Max",
            f"{analisis_data.min():.2f} - {analisis_data.max():.2f}",
            help="Rentang nilai minimum dan maksimum"
        )
    with col4:
        mean_val = analisis_data.mean()
        cv = (analisis_data.std() / mean_val) * 100 if mean_val != 0 else 0
        st.metric(
            "📈 Koef. Variasi",
            f"{cv:.1f}%",
            help="Coefficient of Variation (Standar Deviasi / Rata-rata)"
        )
st.markdown('</div>', unsafe_allow_html=True)

# ===== FOOTER =====
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>📚 <strong>Dashboard Pendidikan Indonesia</strong> |
    Dibuat dengan ❤️ Kelompok 7</p>
    <p><small>Data diperbarui secara berkala untuk memberikan insights terkini</small></p>
</div>
""", unsafe_allow_html=True)