import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import squarify
import textwrap

# Membaca data dari CSV
data_path = "RFM_revised_sby.csv"
df = pd.read_csv(data_path)

# Filter untuk cabang (Branch_Name)
st.sidebar.subheader("Filter Data")
branch_options = ["All"] + list(df["Branch_Name"].unique())
selected_branch = st.sidebar.selectbox("Pilih Cabang", branch_options)

# Filter untuk jenis member
member_options = ["All Member", "Member Aktif"]
selected_member_filter = st.sidebar.radio("Pilih Jenis Member", member_options)

# Filter cheating member
cheating_options = ["Include Cheating Member", "Exclude Cheating Member"]
selected_cheating_filter = st.sidebar.radio("Pilih Filter Cheating Member", cheating_options)

# Terapkan filter cabang
if selected_branch != "All":
    filtered_df = df[df["Branch_Name"] == selected_branch].copy()
else:
    filtered_df = df.copy()

# Terapkan filter jenis member: Member Aktif jika recency <= 365
if selected_member_filter == "Member Aktif":
    filtered_df = filtered_df[filtered_df["Recency"] <= 365].copy()
    
# Terapkan filter cheating member
if selected_cheating_filter == "Exclude Cheating Member":
    filtered_df = filtered_df[filtered_df["isCheating"] == 0].copy()

# Pastikan kembali kolom memberPhone di filtered_df dalam bentuk string
if 'memberPhone' in filtered_df.columns:
    filtered_df.loc[:, 'memberPhone'] = filtered_df.loc[:, 'memberPhone'].astype(str)

# st.write(f"Menampilkan data untuk Cabang: **{selected_branch}**")
# st.write(f"Jenis Member: **{selected_member_filter}**")
# st.write(f"Filter Cheating Member: **{selected_cheating_filter}**")
st.write(f"Total = **{len(filtered_df)}** members")


st.header('Member Segmentation')

# Hitung jumlah customer per segmen
segment_counts = filtered_df['Segmentation'].value_counts()

# Buat label yang mencakup nama segmen, jumlah, dan persentase
labels = [
    f"{seg}\n({cnt} - {cnt / len(filtered_df) * 100:.1f}%)"
    for seg, cnt in zip(segment_counts.index, segment_counts.values)
]

# Lakukan text wrapping agar label tidak meluber
labels_wrapped = [textwrap.fill(label, width=10) for label in labels]

# Buat treemap chart menggunakan squarify dan matplotlib
fig, ax = plt.subplots(figsize=(20, 14))
squarify.plot(
    sizes=segment_counts.values, 
    label=labels_wrapped,
    alpha=0.8, 
    color=["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", 
           "#e5c494", "#b3b3b3", "#ff7f00", "#1f78b4", "#33a02c"],
    text_kwargs={'fontsize': 10},
    ax=ax
)
ax.axis('off')
ax.set_title("Jumlah Customer per Segmen")
st.pyplot(fig)


# Tambahkan visualisasi distribusi umur
st.subheader("Distribusi Umur Member")

# Pastikan kolom Age ada dan dalam rentang valid
if 'Age' in filtered_df.columns and filtered_df['Age'].notna().any():
    # Filter umur yang valid (0-80 tahun)
    valid_age_mask = (filtered_df['Age'] >= 0) & (filtered_df['Age'] <= 80)
    valid_age_df = filtered_df[valid_age_mask].copy()
    
    if len(valid_age_df) > 0:
        fig_age = px.histogram(
            valid_age_df,
            x='Age',
            nbins=20,
            title="Distribusi Umur (0-80 tahun)",
            color_discrete_sequence=['#3366CC']
        )
        
        fig_age.update_layout(
            showlegend=False,
            xaxis_title="Umur",
            yaxis_title="Jumlah Member",
            xaxis_range=[0, 80]  # Set range umur 0-80
        )
        
        st.plotly_chart(fig_age, use_container_width=True)
        
        # Tampilkan statistik dalam format metric
        age_stats = valid_age_df['Age'].describe()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Rata-rata Umur", f"{age_stats['mean']:.1f}")
        with col2:
            st.metric("Median Umur", f"{age_stats['50%']:.1f}")
        with col3:
            st.metric("Umur Minimum", f"{age_stats['min']:.0f}")
        with col4:
            st.metric("Umur Maximum", f"{age_stats['max']:.0f}")
        with col5:
            st.metric("Total Member Valid", f"{len(valid_age_df):,}")
        
        # Tampilkan informasi tentang data yang difilter
        invalid_age_count = len(filtered_df) - len(valid_age_df)
        if invalid_age_count > 0:
            st.warning(f"Terdapat {invalid_age_count:,} member dengan umur tidak valid (di luar rentang 0-80 tahun)")
    else:
        st.info("Tidak ada data umur yang valid dalam rentang 0-80 tahun")
else:
    st.info("Data umur tidak tersedia")


# Tampilkan DataFrame yang sudah dipastikan kolom memberPhone-nya bertipe string
st.dataframe(filtered_df)
