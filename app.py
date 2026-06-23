import streamlit as st
import pandas as pd
import os

# 1. Page Config - Fast Mobile Loading
st.set_page_config(
    page_title="SEO Dashboard", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.title("🚀 Fast SEO Dashboard")

excel_file = "seo_speed_report.xlsx"

# ⚡ FAST LOADING FUNCTION (Cache memory use karega taaki phone lag na kare)
@st.cache_data(ttl=60)  # 60 seconds tak data memory mein rahega, baar-baar load nahi hoga
def load_and_clean_data(file_path):
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_excel(file_path)
    
    # Fast regex replacement & numeric conversion[cite: 1]
    for col in ['First Contentful Paint (FCP)', 'Time to Interactive (TTI)']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Performance Score (%)' in df.columns:
        df['Performance Score (%)'] = pd.to_numeric(df['Performance Score (%)'], errors='coerce')
        
    return df

# Data load karo ek jhatke mein
df = load_and_clean_data(excel_file)

if df is not None:
    # 🔍 Mobile Filter
    st.markdown("### 🔍 Select Website")
    all_sites = ["All Websites"] + list(df['URL'].unique())
    selected_site = st.selectbox("Choose a site:", all_sites, label_visibility="collapsed")
    
    filtered_df = df if selected_site == "All Websites" else df[df['URL'] == selected_site]

    # 📊 Metrics Cards (Lag-free)
    st.markdown("### 📊 Performance Metrics")
    
    if selected_site != "All Websites" and len(filtered_df) > 0:
        row = filtered_df.iloc[0]
        st.metric(label="🎯 Performance Score", value=f"{int(row['Performance Score (%)'])}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="⏱️ FCP Speed", value=f"{row['First Contentful Paint (FCP)']} s")
        with col2:
            st.metric(label="⚡ TTI Speed", value=f"{row['Time to Interactive (TTI)']} s")
    else:
        # Sleek fast table[cite: 1]
        expected_cols = ['URL', 'Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)']
        available_cols = [col for col in expected_cols if col in df.columns]
        
        display_df = filtered_df[available_cols].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 📈 Light-weight Mobile Chart
    st.markdown("### 📈 Metric Comparison Graph")
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("Select metric:", metrics_to_chart)
    
    chart_data = filtered_df.pivot_table(index='URL', values=selected_metric, aggfunc='mean')
    st.bar_chart(chart_data, use_container_width=True)

else:
    st.warning(f"Data file '{excel_file}' not found.")
