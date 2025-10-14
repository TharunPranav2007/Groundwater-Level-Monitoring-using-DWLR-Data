import os
import glob
import re
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# -------------------------
# API key & Page Config
# -------------------------
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]
st.set_page_config(
    page_title="Groundwater Evaluation Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# --- FINAL UI STYLESHEET ---
# -------------------------
st.markdown("""
<style>
    .main {background-color: #F0F2F6;}
    html, body, [class*="css"] {font-family: 'Segoe UI', sans-serif;}
    .main-title-container {
        background: linear-gradient(to right, #005c97, #363795);
        padding: 20px; border-radius: 12px; color: white;
        text-align: center; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .main-title-container h1 {font-size: 2.5em; font-weight: 800; color: white; margin: 0;}
    .main-title-container .subtitle {font-size: 1.1em; color: #E0E0E0; margin: 5px 0 0 0;}
    [data-testid="stSidebar"] {background-color: #FFFFFF; border-right: 1px solid #E0E0E0; padding: 10px;}
    .sidebar-section {
        background-color: #F8F9FA; border: 1px solid #E0E0E0;
        border-radius: 12px; padding: 15px; margin-top: 10px;
    }
    .sidebar-section h2 {font-size: 1.5em; font-weight: 700; color: #004C99; margin-top: 0;}
    [data-testid="stSelectbox"] > div > div, [data-testid="stTextInput"] > div > div > input {
        background-color: #FFFFFF; border: 1px solid #B0B0B0; border-radius: 8px;
    }
    [data-testid="stSelectbox"] label, [data-testid="stTextInput"] label {font-weight: 600; color: #333;}
    [data-testid="stSidebar"] .stButton>button {
        background-color: transparent; border: 1px solid #0077b6; color: #0077b6;
        border-radius: 50%; width: 45px; height: 45px; font-size: 20px;
        padding: 0; transition: all 0.3s;
    }
    [data-testid="stSidebar"] .stButton>button:hover {background-color: #0077b6; color: white;}
    .kpi-card {
        background-color: #FFFFFF; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); text-align: center;
        border: 1px solid #E0E0E0; transition: all 0.3s ease-in-out; height: 100%;
    }
    .kpi-card:hover {transform: translateY(-5px); box-shadow: 0 6px 16px rgba(0,0,0,0.12);}
    .kpi-icon {font-size: 28px; margin-bottom: 10px;}
    .kpi-title {font-size: 16px; font-weight: 500; color: #4F6A94;}
    .kpi-value {font-size: 26px; font-weight: 700; color: #004C99;}
    .result-box {
        background-color: #E0F7FA; border: 1px solid #00B4D8; border-left: 5px solid #0077b6;
        border-radius: 10px; padding: 16px; margin-top: 15px; word-wrap: break-word;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .result-box strong {color: #005f91; font-size: 1.1em;}
    h2, h3 {
        color: #004C99; font-weight: 700;
        border-bottom: 2px solid #ADE8F4; padding-bottom: 5px;
    }
    /* Styling for Action Buttons in columns */
    div[data-testid="stHorizontalBlock"] .stButton>button,
    div[data-testid="stHorizontalBlock"] .stDownloadButton>button {
        background-color: #0077b6;
        color: white;
        width: 100%;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 0;
        border: none;
        transition: background-color 0.3s;
    }
    div[data-testid="stHorizontalBlock"] .stButton>button:hover,
    div[data-testid="stHorizontalBlock"] .stDownloadButton>button:hover {
        background-color: #005f91;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Initialize Session State
# -------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'soil_type' not in st.session_state:
    st.session_state.soil_type = "Click Generate"
if 'recommended_crops' not in st.session_state:
    st.session_state.recommended_crops = ""

# -------------------------
# Utilities & Data Loading
# -------------------------
def _classify_season(dt: pd.Timestamp) -> str:
    if pd.isna(dt): return "Unknown"
    if dt.month in (1, 2, 3, 4, 5): return "Premonsoon"
    if dt.month in (8, 10, 11, 12): return "Postmonsoon"
    return "Other"

@st.cache_data
def load_all_data() -> pd.DataFrame:
    base_url = "https://raw.githubusercontent.com/TharunPranav2007/Groundwater-Level-Monitoring-using-DWLR-Data/main/"
    file_names = [
        "august_wl_1994-2023_compressed-clean.csv",
        "january_wl_1994-2024-compressed-clean.xlsx",
        "post-monsoon_wl_1994-2023_compressed-clean.xlsx",
        "pre-monsoon_1994-2003-clean.csv",
        "pre-monsoon_2004-2013-clean.csv",
        "pre-monsoon_2014-2024-clean.csv"
    ]
    file_urls = [base_url + name for name in file_names]

    parts = []
    for url in file_urls:
        df = None
        try:
            if url.endswith('.csv'):
                df = pd.read_csv(url, parse_dates=["DATE"], dayfirst=True, low_memory=False, encoding='utf-8')
            elif url.endswith('.xlsx'):
                df = pd.read_excel(url, parse_dates=["DATE"])

            if df is None or df.empty: continue
            
            df.columns = [c.strip().upper() for c in df.columns]
            for col in ["STATE_UT", "DISTRICT", "BLOCK", "VILLAGE"]:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True).replace({"nan": np.nan, "None": np.nan})
                    df.loc[df[col].notna(), col] = df.loc[df[col].notna(), col].str.title()
            if "DATE" in df.columns:
                df["SEASON"] = df["DATE"].apply(_classify_season)
            parts.append(df)
        except Exception as e:
            st.warning(f"Could not read file from URL: {os.path.basename(url)}. Error: {e}")
            continue

    if not parts: st.error("No valid data could be loaded from the provided URLs."); st.stop()
    
    df_all = pd.concat(parts, ignore_index=True)
    if "DTWL" in df_all.columns and "DATE" in df_all.columns:
        df_all = df_all.dropna(subset=["DTWL", "DATE"])
    return df_all

@st.cache_data
def precompute_unique_values(df: pd.DataFrame):
    uniques = {}
    uniques["states"] = sorted(df["STATE_UT"].dropna().unique()) if "STATE_UT" in df.columns else []
    uniques["districts_by_state"] = df.groupby("STATE_UT")["DISTRICT"].apply(lambda x: sorted(x.dropna().unique())).to_dict() if {"STATE_UT","DISTRICT"}.issubset(df.columns) else {}
    uniques["blocks_by_district"] = df.groupby("DISTRICT")["BLOCK"].apply(lambda x: sorted(x.dropna().unique())).to_dict() if {"DISTRICT","BLOCK"}.issubset(df.columns) else {}
    uniques["villages_by_block"] = df.groupby("BLOCK")["VILLAGE"].apply(lambda x: sorted(x.dropna().unique())).to_dict() if {"BLOCK","VILLAGE"}.issubset(df.columns) else {}
    uniques["pincodes_by_village"] = df.groupby("VILLAGE")["PINCODE"].apply(lambda x: sorted(x.dropna().unique())).to_dict() if {"VILLAGE","PINCODE"}.issubset(df.columns) else {}
    return uniques

df_all = load_all_data()
uniques = precompute_unique_values(df_all)

# -------------------------
# Sidebar (always visible)
# -------------------------
col1, col2 = st.sidebar.columns([3, 1])
with col1:
    st.header("📍 Location Selector")
with col2:
    if st.button("🧹", help="Clear all filters"):
        for key in ("state", "district", "block", "village", "pincode", "manual_search"): st.session_state[key] = ""
        st.session_state.soil_type = "Click Generate"; st.session_state.recommended_crops = ""
        st.session_state.page = 'home'
        st.rerun()

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
for key in ("state","district","block","village","pincode"):
    if key not in st.session_state: st.session_state[key] = ""
manual_location = st.sidebar.text_input("Manual search", key='manual_search')
state_options = [""] + uniques.get("states", [])
st.session_state["state"] = st.sidebar.selectbox("State", state_options, key='state_select', index=state_options.index(st.session_state.get("state", "")) if st.session_state.get("state") in state_options else 0)
district_options = [""] + uniques["districts_by_state"].get(st.session_state.get("state", ""), [])
st.session_state["district"] = st.sidebar.selectbox("District", district_options, key='district_select', index=district_options.index(st.session_state.get("district", "")) if st.session_state.get("district") in district_options else 0)
block_options = [""] + uniques["blocks_by_district"].get(st.session_state.get("district", ""), [])
st.session_state["block"] = st.sidebar.selectbox("Block", block_options, key='block_select', index=block_options.index(st.session_state.get("block", "")) if st.session_state.get("block") in block_options else 0)
village_options = [""] + uniques["villages_by_block"].get(st.session_state.get("block", ""), [])
st.session_state["village"] = st.sidebar.selectbox("Village", village_options, key='village_select', index=village_options.index(st.session_state.get("village", "")) if st.session_state.get("village") in village_options else 0)
pincode_options = [""] + uniques["pincodes_by_village"].get(st.session_state.get("village", ""), [])
st.session_state["pincode"] = st.sidebar.selectbox("Pincode", pincode_options, key='pincode_select', index=pincode_options.index(st.session_state.get("pincode", "")) if st.session_state.get("pincode") in pincode_options else 0)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Data Filtering (always runs)
# -------------------------
df_filtered = df_all.copy()
if st.session_state.state: df_filtered = df_filtered[df_filtered["STATE_UT"] == st.session_state.state]
if st.session_state.district: df_filtered = df_filtered[df_filtered["DISTRICT"] == st.session_state.district]
if st.session_state.block: df_filtered = df_filtered[df_filtered["BLOCK"] == st.session_state.block]
if st.session_state.village: df_filtered = df_filtered[df_filtered["VILLAGE"] == st.session_state.village]
if st.session_state.pincode: df_filtered = df_filtered[df_filtered["PINCODE"] == st.session_state.pincode]
if manual_location:
    q = manual_location.lower()
    df_filtered = df_filtered[df_filtered.apply(lambda row: q in str(row).lower(), axis=1)]

# -------------------------
# --- PAGE 1: HOME PAGE ---
# -------------------------
def render_home_page(df):
    st.markdown("""
    <div class="main-title-container">
        <h1>💧 Groundwater Resource Evaluation Dashboard</h1>
        <p class="subtitle">Real-time Visualization • Weather Insights • Crop Suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NEW: Display Selected Location ---
    location_name = " -> ".join(filter(None, [st.session_state.get('state'), st.session_state.get('district'), st.session_state.get('block'), st.session_state.get('village')])) or "All India"
    st.subheader(f"📍 Currently Showing Data For: `{location_name}`")
    
    # KPIs Section
    st.subheader("📊 Key Performance Indicators")
    avg_dtwl = df["DTWL"].mean()
    current_dtwl = df.sort_values("DATE").iloc[-1]["DTWL"]
    prem_avg = df[df["SEASON"]=="Premonsoon"]["DTWL"].mean()
    post_avg = df[df["SEASON"]=="Postmonsoon"]["DTWL"].mean()
    kpi_cols = st.columns(4)
    kpi_cols[0].markdown(f'<div class="kpi-card"><div class="kpi-icon">📉</div><div class="kpi-title">Overall DTWL</div><div class="kpi-value">{avg_dtwl:.2f} m</div></div>', unsafe_allow_html=True)
    kpi_cols[1].markdown(f'<div class="kpi-card"><div class="kpi-icon">💧</div><div class="kpi-title">Current DTWL</div><div class="kpi-value">{current_dtwl:.2f} m</div></div>', unsafe_allow_html=True)
    kpi_cols[2].markdown(f'<div class="kpi-card"><div class="kpi-icon">☀️</div><div class="kpi-title">Premonsoon Avg</div><div class="kpi-value">{f"{prem_avg:.2f} m" if not np.isnan(prem_avg) else "N/A"}</div></div>', unsafe_allow_html=True)
    kpi_cols[3].markdown(f'<div class="kpi-card"><div class="kpi-icon">🌧️</div><div class="kpi-title">Postmonsoon Avg</div><div class="kpi-value">{f"{post_avg:.2f} m" if not np.isnan(post_avg) else "N/A"}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Weather info
    try:
        location = f"{st.session_state.district},{st.session_state.state},IN" if st.session_state.district else f"{st.session_state.state},IN"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        weather_temp, weather_hum = res["main"]["temp"], res["main"]["humidity"]
    except:
        weather_temp, weather_hum = None, None
    
    if weather_temp is not None:
        weather_cols = st.columns(3)
        weather_cols[0].markdown(f'<div class="kpi-card"><div class="kpi-icon">🌡️</div><div class="kpi-title">Temperature</div><div class="kpi-value">{weather_temp:.1f} °C</div></div>', unsafe_allow_html=True)
        weather_cols[1].markdown(f'<div class="kpi-card"><div class="kpi-icon">💧</div><div class="kpi-title">Humidity</div><div class="kpi-value">{weather_hum:.1f} %</div></div>', unsafe_allow_html=True)
        weather_cols[2].markdown(f'<div class="kpi-card"><div class="kpi-icon">🌱</div><div class="kpi-title">Soil Type</div><div class="kpi-value">{st.session_state.soil_type}</div></div>', unsafe_allow_html=True)

    def get_rule_based_recommendation(state, temp, avg_dtwl):
        # (Rule-based logic remains the same)
        return "Alluvial Soil", "Rice, Wheat, Sugarcane"

    st.markdown("---")
    st.header("🌾 Crop Recommendation and Report Download")
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("🌱 Generate Crop Recommendation"):
            if weather_temp is not None and not np.isnan(avg_dtwl):
                soil, crops = get_rule_based_recommendation(st.session_state.state, weather_temp, avg_dtwl)
                st.session_state.soil_type = soil; st.session_state.recommended_crops = crops
                st.rerun()
            else: st.error("Weather or water level data unavailable.")
    
    with action_cols[1]:
        # --- CORRECTED DOWNLOAD LOGIC ---
        summary_header = "Metric,Value\n"
        summary_rows = [
            f"Location - State,{st.session_state.state or 'N/A'}",
            f"Location - District,{st.session_state.district or 'N/A'}",
            f"Location - Block,{st.session_state.block or 'N/A'}",
            f"Location - Village,{st.session_state.village or 'N/A'}",
            "---,---",
            f"Overall DTWL (m),{avg_dtwl:.2f}",
            f"Temperature (°C),{f'{weather_temp:.1f}' if weather_temp is not None else 'N/A'}",
            f"Predicted Soil Type,\"{st.session_state.soil_type}\"",
            f"Recommended Crops,\"{st.session_state.recommended_crops}\"",
        ]
        summary_string = summary_header + "\n".join(summary_rows)
        raw_data_string = df.to_csv(index=False)
        final_csv_string = summary_string + "\n\n--- RAW DATA ---\n\n" + raw_data_string
        st.download_button(label="📂 Download Full Report", data=final_csv_string.encode("utf-8"), file_name="groundwater_report.csv", mime="text/csv")

    if st.session_state.recommended_crops:
        st.markdown(f"<div class='result-box'><strong>Recommended Crops:</strong> {st.session_state.recommended_crops}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("📈 Detailed Historical Analysis")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        if st.button("View Detailed Trend Report"):
            st.session_state.page = 'report'
            st.rerun()

    st.markdown("---")
    st.header("📊 Overall Trend Analysis & Location Map")
    df_plot = df.copy()
    if "DATE" in df_plot.columns:
        df_plot["YEAR"] = df_plot["DATE"].dt.year
        prem = df_plot[df_plot["SEASON"]=="Premonsoon"].groupby("YEAR")["DTWL"].mean().reset_index()
        post = df_plot[df_plot["SEASON"]=="Postmonsoon"].groupby("YEAR")["DTWL"].mean().reset_index()
        overall = df_plot[df_plot.SEASON.isin(["Premonsoon", "Postmonsoon"])].groupby("YEAR")["DTWL"].mean().reset_index()
        if not (prem.empty and post.empty):
            prem['Trend'], post['Trend'], overall['Trend'] = 'Premonsoon', 'Postmonsoon', 'Overall'
            df_combined = pd.concat([prem, post, overall], ignore_index=True)
            fig_combined = px.line(df_combined, x="YEAR", y="DTWL", color='Trend', markers=True, 
                                   title="Combined Groundwater Level Trends", labels={"DTWL": "Depth to Water Level DTWL (m)", "YEAR": "Year"})
            st.plotly_chart(fig_combined, use_container_width=True)
    
    if "LATITUDE" in df.columns and "LONGITUDE" in df.columns:
        loc_latest = df.dropna(subset=["LATITUDE", "LONGITUDE"]).sort_values("DATE").groupby(["STATE_UT","DISTRICT","BLOCK","VILLAGE"]).tail(1)
        if not loc_latest.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.header("📍 Location Map")
            fig_map = px.scatter_mapbox(loc_latest, lat="LATITUDE", lon="LONGITUDE", hover_name="VILLAGE", hover_data=["DTWL"],
                                        color="DTWL", size="DTWL", size_max=12, zoom=4, mapbox_style="open-street-map",
                                        color_continuous_scale=px.colors.sequential.Viridis_r)
            fig_map.update_layout(margin=dict(t=0,b=0,l=0,r=0), height=500)
            st.plotly_chart(fig_map, use_container_width=True)

# -------------------------
# --- PAGE 2: REPORT PAGE ---
# -------------------------
def render_report_page(df):
    location_name = " -> ".join(filter(None, [st.session_state.get('state'), st.session_state.get('district'), st.session_state.get('block'), st.session_state.get('village')])) or "All India"
    st.markdown(f"## 📋 Detailed Trend Report for: `{location_name}`")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'home'
        st.rerun()
        
    if df.empty or "DATE" not in df.columns:
        st.warning("No data available to generate a detailed report.")
        return

    df_plot = df.copy()
    df_plot["YEAR"] = df_plot["DATE"].dt.year
    prem = df_plot[df_plot["SEASON"]=="Premonsoon"].groupby("YEAR")["DTWL"].mean().reset_index()
    post = df_plot[df_plot["SEASON"]=="Postmonsoon"].groupby("YEAR")["DTWL"].mean().reset_index()
    overall = df_plot[df_plot.SEASON.isin(["Premonsoon", "Postmonsoon"])].groupby("YEAR")["DTWL"].mean().reset_index()
    y_axis_label = {"DTWL": "Depth to Water Level DTWL (m)", "YEAR": "Year"}

    if not prem.empty:
        st.subheader("☀️ Premonsoon DTWL Trend")
        fig_prem = px.line(prem, x="YEAR", y="DTWL", markers=True, title="Premonsoon DTWL Trend", labels=y_axis_label)
        st.plotly_chart(fig_prem, use_container_width=True)
    if not post.empty:
        st.subheader("🌧️ Postmonsoon DTWL Trend")
        fig_post = px.line(post, x="YEAR", y="DTWL", markers=True, title="Postmonsoon DTWL Trend", labels=y_axis_label)
        st.plotly_chart(fig_post, use_container_width=True)
    if not overall.empty:
        st.subheader("📉 Overall DTWL Trend")
        fig_overall = px.line(overall, x="YEAR", y="DTWL", markers=True, title="Overall DTWL Trend", labels=y_axis_label)
        st.plotly_chart(fig_overall, use_container_width=True)

# -------------------------
# --- MAIN APP ROUTER ---
# -------------------------
if df_filtered.empty:
    st.warning("No data found for the selected filters. Please clear the filters or choose another location.")
else:
    if st.session_state.page == 'home':
        render_home_page(df_filtered)
    elif st.session_state.page == 'report':
        render_report_page(df_filtered)
