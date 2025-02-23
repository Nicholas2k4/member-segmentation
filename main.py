import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import squarify
import plotly.graph_objects as go
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



# Segment filter
selected_segment = st.selectbox(
    "Select Customer Segment",
    options=sorted(filtered_df['Segmentation'].unique())
)

# Filter data based on selection
filtered_df = filtered_df[filtered_df['Segmentation'] == selected_segment]

# Main dashboard
st.title("Segmentation Analysis")
st.subheader(f"Segment: {selected_segment}")

# KPI Metrics dalam layout 2x2
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Customers", len(filtered_df))
with col2:
    st.metric("Average Monetary", f"Rp{filtered_df['Monetary'].mean():,.2f}")

col3, col4 = st.columns(2)
with col3:
    st.metric("Average Frequency", f"{filtered_df['Frequency'].mean():.1f}")
with col4:
    st.metric("Average AOV", f"Rp{filtered_df['AOV'].mean():,.2f}")

# Create two columns for charts
col1, col2 = st.columns(2)

# Age Distribution (Age sudah tersedia di CSV)
with col1:
    st.subheader("Age Distribution")
    if 'Age' in filtered_df.columns and filtered_df['Age'].notna().any():
        fig_age = px.histogram(
            filtered_df,
            x='Age',
            nbins=20,
            title="Age Distribution",
            color_discrete_sequence=['#3366CC']
        )
        fig_age.update_layout(
            showlegend=False,
            xaxis_title="Age",
            yaxis_title="Count"
        )
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("Age data not available")

# LTV (Monetary) Distribution
with col2:
    st.subheader("Monetary Distribution")
    fig_ltv = px.histogram(
        filtered_df,
        x='MCategory',
        nbins=20,
        title="Customer Monetary Distribution",
        color_discrete_sequence=['#109618']
    )
    fig_ltv.update_layout(
        showlegend=False,
        xaxis_title="Lifetime Value (Rp)",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_ltv, use_container_width=True)

col3, col4 = st.columns(2)
# Visit Frequency Distribution
with col3:
    st.subheader("Visit Frequency Distribution")
    
    # Calculate frequency distribution
    freq_counts = filtered_df['Frequency'].value_counts().reset_index()
    freq_counts.columns = ['Frequency', 'Count']
    freq_counts = freq_counts.sort_values('Frequency')
    
    # Create line chart
    fig_freq = go.Figure()
    
    # Add line trace
    fig_freq.add_trace(
        go.Scatter(
            x=freq_counts['Frequency'],
            y=freq_counts['Count'],
            mode='lines',
            line=dict(
                color='#FF9900',
                width=3,
                shape='spline',  # Membuat garis menjadi smooth
                smoothing=1.3    # Adjust smoothing factor
            ),
            hovertemplate='<b>Visits</b>: %{x}<br>' +
                          '<b>Count</b>: %{y}<br>' +
                          '<extra></extra>'  # Menghilangkan trace name dari hover
        )
    )
    
    # Update layout
    fig_freq.update_layout(
        showlegend=False,
        xaxis_title="Number of Visits",
        yaxis_title="Count",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1,
            dtick=1,  # Menampilkan setiap integer pada sumbu-x
            range=[1, max(freq_counts['Frequency']) + 1]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            gridwidth=1,
            zeroline=False
        ),
        margin=dict(l=0, r=0, t=20, b=0),
        height=400
    )
    
    st.plotly_chart(fig_freq, use_container_width=True)

# Visit Recency Distribution
with col4:
    st.subheader("Visit Recency Distribution")
    fig_recency = px.histogram(
        filtered_df,
        x='Recency',
        nbins=20,
        title="Visit Recency Distribution",
        color_discrete_sequence=['#FF0000']
    )
    fig_recency.update_layout(
        showlegend=False,
        xaxis_title="Days Since Last Visit",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_recency, use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.subheader("RFM Score Distribution")
    fig_rfm = px.box(
        filtered_df,
        y=['RScore', 'FScore', 'MScore'],
        title="RFM Score Distribution",
        color_discrete_sequence=['#DC3912', '#FF9900', '#109618']
    )
    fig_rfm.update_layout(
        yaxis_title="Score",
        xaxis_title="RFM Components"
    )
    st.plotly_chart(fig_rfm, use_container_width=True)

# Detailed Customer Table
st.subheader("Customer Details")
columns_to_display = ['Age', 'Recency', 'Frequency', 'Monetary', 
                     'RFMScore', 'AOV', 'Segmentation', 'Branch_Name']

st.dataframe(
    filtered_df[columns_to_display].style.format({
        'Monetary': '${:,.2f}',
        'AOV': '${:,.2f}',
        'RFMScore': '{:.2f}'
    }),
    hide_index=True
)

# Download button for detailed data
csv = filtered_df[columns_to_display].to_csv(index=False)
st.download_button(
    label="Download Segment Data",
    data=csv,
    file_name=f'rfm_segment_{selected_segment}.csv',
    mime='text/csv'
)