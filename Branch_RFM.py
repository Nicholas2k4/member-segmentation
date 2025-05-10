import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

import calendar
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(
    page_title="My Dashboard",
    layout="wide",        # ← makes the page use the full width
    initial_sidebar_state="expanded"
)



st.title("Branch RFM")

col1, col2 = st.columns(2)

# Year selection
years = range(2018, 2026)
with col1:
    year_selected = st.selectbox("Select Year", years, index=years.index(2025))

# Month selection
months = range(1, 13)
with col2:
    month_selected = st.selectbox("Select Month", months, index=months.index(2))

# Fetch Data
branch_rfm = pd.read_csv("branch_rfm.csv")
with st.spinner("Loading data..."):
    # If less than 2017 month 11, show alert
    if (year_selected == 2025 and month_selected > 3) or (
        year_selected == 2018 and month_selected < 6
    ):
        st.warning("Data not available for the selected date.")
    else:
        branch_rfm_filtered = branch_rfm[
            (branch_rfm["Year"] == year_selected)
            & (branch_rfm["Month"] == month_selected)
        ].copy()

# Branch Information
branches = branch_rfm_filtered["Branch_Name"].unique().tolist()

branch_info = {
    "Citraland (9GO)": {"cut_target": 900, "chair": 5},
    "Graha Family": {"cut_target": 1575, "chair": 7},
    "Intro": {"cut_target": 900, "chair": 4},
    "Klampis": {"cut_target": 1575, "chair": 7},
    "Margorejo": {"cut_target": 1575, "chair": 7},
    "Sukomanunggal": {"cut_target": 1125, "chair": 5},
    "Bukit Darmo Golf": {"cut_target": 1125, "chair": 5},
}

# --- Inject sedikit CSS untuk styling box ---
st.markdown(
    """
    <style>
        .kpi-box {
          border: 3px solid #000;
          border-radius: 12px;
          padding: 16px;
          margin-bottom: 16px;
        }
        .kpi-header {
          font-weight: bold;
          margin-bottom: 8px;
          color: #555;
        }
        .kpi-value {
          font-size: 2.5rem;
          margin: 0;
          color: #555;
        }
        .kpi-sub {
          font-size: 0.9rem;
          color: #555;
        }
        .bg-red   { background-color: #ff5f5f; }
        .bg-orange{ background-color: #ffb74d; }
        .bg-yellow{ background-color: #ffde59; }
        .bg-green { background-color: #b8ff96; }
        .bg-white { background-color: #fff; }
        .text-white{ color: #fff; }
    </style>
""",
    unsafe_allow_html=True,
)

metrics = []

for branch in branches:
    if branch == "Goodfellas Home":
        continue
    
    st.title(f"{branch} - {calendar.month_name[month_selected]} {year_selected}")

    rfm_branch_now = branch_rfm_filtered[branch_rfm_filtered["Branch_Name"] == branch]

    # Total Customer & Member
    st.subheader(f"Total Customer yang datang: {rfm_branch_now.iloc[0]['TotalCut']}")
    st.write(f"Total Member: **{rfm_branch_now.iloc[0]['TotalMember']}**\n---")

    # compute raw counts
    orang_hilang = rfm_branch_now.iloc[0]["OrangHilang"]
    orang_semi_hilang = rfm_branch_now.iloc[0]["OrangSemiHilang"]
    orang_baru = rfm_branch_now.iloc[0]["OrangBaru"]
    orang_langganan = rfm_branch_now.iloc[0]["OrangLangganan"]
    total_members = rfm_branch_now.iloc[0]["TotalMember"]

    member_cut = rfm_branch_now.iloc[0]["MemberCut"]
    non_member_cut = rfm_branch_now.iloc[0]["NonMemberCut"]
    total_cut = rfm_branch_now.iloc[0]["TotalCut"]
    new_member = rfm_branch_now.iloc[0]["NewMember"]
    cut_per_chair = rfm_branch_now.iloc[0]["CutPerChair"]
    
    # compute percentages
    pct_hilang = orang_hilang / total_members * 100 if total_members else 0
    pct_semi_hilang = orang_semi_hilang / total_members * 100 if total_members else 0
    pct_baru = orang_baru / total_members * 100 if total_members else 0
    pct_langganan = orang_langganan / total_members * 100 if total_members else 0
    pct_member = member_cut / total_cut * 100 if total_cut else 0
    pct_non_member = non_member_cut / total_cut * 100 if total_cut else 0
    pct_acquisition = new_member / non_member_cut * 100 if non_member_cut else 0
    pct_target = total_cut / branch_info[branch]["cut_target"] * 100 if total_cut else 0
    member_ratio = round(pct_member / 100 * 10)
    non_member_ratio = 10 - member_ratio
    
    metrics.append({
        "Branch_Name": branch,
        "TargetPercentage": pct_target,
    })

    # Member RFM Activity
    cols = st.columns([1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown(
            f'<div class="kpi-box bg-red" style="text-align:center;">'
            f'  <div class="kpi-header">Orang Hilang</div>'
            f'  <p class="kpi-value">{pct_hilang:.2f}%</p>'
            f'  <p class="kpi-sub">{orang_hilang} Member</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            f'<div class="kpi-box bg-orange" style="text-align:center;">'
            f'  <div class="kpi-header">Orang Semi Hilang</div>'
            f'  <p class="kpi-value">{pct_semi_hilang:.2f}%</p>'
            f'  <p class="kpi-sub">{orang_semi_hilang} Member</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            f'<div class="kpi-box bg-yellow" style="text-align:center;">'
            f'  <div class="kpi-header">Orang Baru</div>'
            f'  <p class="kpi-value">{pct_baru:.2f}%</p>'
            f'  <p class="kpi-sub">{orang_baru} Member</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cols[3]:
        st.markdown(
            f'<div class="kpi-box bg-green" style="text-align:center;">'
            f'  <div class="kpi-header">Orang Langganan</div>'
            f'  <p class="kpi-value">{pct_langganan:.2f}%</p>'
            f'  <p class="kpi-sub">{orang_langganan} Member</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cols[4]:
        st.markdown(
            f'<div class="kpi-box bg-white" style="text-align:center;">'
            f'<div class="kpi-header">Member Cut</div>'
            f'<p class="kpi-value">{pct_member:.2f}%</p>'
            f'<p class="kpi-sub">{member_cut} Kepala</p>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.write("---")

    # Non Member Activity
    cols2 = st.columns([4, 1])
    with cols2[0]:
        st.markdown(
            f'<div class="kpi-box bg-yellow" style="text-align:center;">'
            f'<div class="kpi-header">Acquisition to Member</div>'
            f'<p class="kpi-value">{pct_acquisition:.2f}%</p>'
            f'<p class="kpi-sub">{new_member} Kepala</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
    with cols2[1]:
        st.markdown(
            f'<div class="kpi-box bg-white" style="text-align:center;">'
            f'<div class="kpi-header text-black">Non-Member Cut</div>'
            f'<p class="kpi-value">{pct_non_member:.2f}%</p>'
            f'<p class="kpi-sub">{non_member_cut} Kepala</p>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.write("---")

    def colored_progress(value: float, max_value: float = 100.0, width: int = 220, height: int = 10):
        """
        Render a rounded progress bar with dynamic fill color:
        fraction: 0.0–1.0
        """
        
        fraction = value / max_value
        pct = max(0, min(1, fraction)) * 100
        # choose fill color by threshold
        if pct < 60:
            fill = "#ff5f5f"  # red
        elif pct < 80:
            fill = "#ffde59"  # yellow
        else:
            fill = "#b8ff96"  # green
        track = "#eee"  # light grey track
        radius = height // 2

        bar = f"""
            <div style="
                width:{width}px; height:{height}px;
                background:{track};
                border-radius:{radius}px;
                overflow:hidden;
                margin:4px auto;
            ">
              <div style="
                width:{pct:.1f}%; height:100%;
                background:{fill};
                transition: width 0.3s ease;
              "></div>
            </div>
        """
        st.markdown(bar, unsafe_allow_html=True)

    # Branch Activity
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown(
            f'<div class="kpi-box" style="text-align:center;"><div class="kpi-header text-white">Cut vs Target</div>'
            f'<p class="kpi-value text-white">{pct_target:.1f}%</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # render our custom, colored bar
        colored_progress(pct_target)
    
    with b2:
        st.markdown(
            f'<div class="kpi-box" style="text-align:center;"><div class="kpi-header text-white">Cut per Chair</div>'
            f'<p class="kpi-value text-white">{cut_per_chair:.1f}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
    # member active ratio
    with b3:
        st.markdown(
            f'<div class="kpi-box" style="text-align:center;"><div class="kpi-header text-white">Member Active Ratio</div>'
            f'<p class="kpi-value text-white">{member_ratio} : {non_member_ratio}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        
    # active member pct
    with b4:
        st.markdown(
            f'<div class="kpi-box" style="text-align:center;"><div class="kpi-header text-white">Active Member Percentage</div>'
            f'<p class="kpi-value text-white">{(pct_langganan + pct_baru):.1f}%</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        colored_progress(pct_langganan + pct_baru, 40)
        
   
    st.write("<br><br>", unsafe_allow_html=True)

# selesai loop, ubah metrics list menjadi DataFrame
metrics_df = pd.DataFrame(metrics)

# merge ke branch_rfm_filtered
summary_df = branch_rfm_filtered.merge(metrics_df, on="Branch_Name", how="left")

# tampilkan di Streamlit
st.subheader("📊 Ringkasan RFM per Cabang")
st.dataframe(summary_df)