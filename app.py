import streamlit as st
import pandas as pd
import os
import re

# 1. Page Configuration - Strict Mobile First Layout
st.set_page_config(
    page_title="SEO Dashboard", 
    layout="centered", # Mobile ke liye 'centered' sabse best hota hai taaki content bhatke na
    initial_sidebar_state="collapsed"
)

st.title("🚀 SEO & Web Performance Dashboard")
st.write("Real-time automated website tracking matrix.")

excel_file = "seo_speed_report.xlsx"

if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    
    # Clean and convert data types
    for col in ['First Contentful Paint (FCP)', 'Time to Interactive (TTI)']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Performance Score (%)' in df.columns:
        df['Performance Score (%)'] = pd.to_numeric(df['Performance Score (%)'], errors='coerce')

    # 🔍 Mobile UI Filter - Big drop-down on top
    st.markdown("### 🔍 Select Website")
    all_sites = ["All Websites"] + list(df['URL'].unique())
    selected_site = st.selectbox("Choose a site to inspect:", all_sites, label_visibility="collapsed")
    
    if selected_site != "All Websites":
        filtered_df = df[df['URL'] == selected_site]
    else:
        filtered_df = df

    # 📊 Mobile Responsive Display (Cards + Table)
    st.markdown("### 📊 Performance Metrics")
    
    # Agar user ne koi ek website select ki hai, toh mobile par use cards ke roop mein sundar dikhao
    if selected_site != "All Websites" and len(filtered_df) > 0:
        row = filtered_df.iloc[0]
        
        # Mobile-friendly large font metrics
        st.metric(label="🎯 Performance Score", value=f"{int(row['Performance Score (%)'])}%")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="⏱️ FCP Speed", value=f"{row['First Contentful Paint (FCP)']} s")
        with col2:
            st.metric(label="⚡ TTI Speed", value=f"{row['Time to Interactive (TTI)']} s")
            
    else:
        # Agar saari websites dekhni hain, toh ek sleek table dikhao jo mobile responsive ho
        expected_cols = ['URL', 'Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)']
        available_cols = [col for col in expected_cols if col in df.columns]
        
        display_df = filtered_df[available_cols].copy()
        
        # Formatting for clear display
        if 'First Contentful Paint (FCP)' in display_df.columns:
            display_df['First Contentful Paint (FCP)'] = display_df['First Contentful Paint (FCP)'].apply(lambda x: f"{x} s" if pd.notnull(x) else "")
        if 'Time to Interactive (TTI)' in display_df.columns:
            display_df['Time to Interactive (TTI)'] = display_df['Time to Interactive (TTI)'].apply(lambda x: f"{x} s" if pd.notnull(x) else "")
            
        # use_container_width automatic ensures no ugly horizontal scroll on phone screens
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 📈 Chart Section - Scaled perfectly for mobile screens
    st.markdown("### 📈 Metric Comparison Graph")
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("Select metric for graph visualization:", metrics_to_chart)
    
    chart_data = filtered_df.pivot_table(index='URL', values=selected_metric, aggfunc='mean')
    st.bar_chart(chart_data, use_container_width=True)

else:
    st.warning(f"Data file '{excel_file}' not found.")
