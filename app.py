import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="SEO Automation Dashboard", layout="wide")
st.title("🚀 SEO & Web Performance Automation Dashboard")
st.write("Welcome! This automated system tracks real-time website performance and SEO metrics.")

excel_file = "seo_speed_report.xlsx"

if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    st.success("Backend Python automation engine data loaded successfully!")
    
    # Strictly extract only numeric values (removes 's', spaces, or any letters)
    for col in ['First Contentful Paint (FCP)', 'Time to Interactive (TTI)']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Performance Score (%)' in df.columns:
        df['Performance Score (%)'] = pd.to_numeric(df['Performance Score (%)'], errors='coerce')

    st.sidebar.header("Filter Options")
    all_sites = ["All Websites"] + list(df['URL'].unique())
    selected_site = st.sidebar.selectbox("Select Website to Analyze", all_sites)
    
    if selected_site != "All Websites":
        filtered_df = df[df['URL'] == selected_site]
    else:
        filtered_df = df

    st.subheader("📊 Monitored Websites Performance Matrix")
    
    expected_cols = [
        'URL', 
        'Performance Score (%)', 
        'First Contentful Paint (FCP)', 
        'Time to Interactive (TTI)'
    ]
    
    date_col = next((c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()), None)
    if date_col and date_col not in expected_cols:
        expected_cols.append(date_col)
        
    available_cols = [col for col in expected_cols if col in df.columns]
    
    display_df = filtered_df[available_cols].copy()
    if 'First Contentful Paint (FCP)' in display_df.columns:
        display_df['First Contentful Paint (FCP)'] = display_df['First Contentful Paint (FCP)'].apply(lambda x: f"{x} s" if pd.notnull(x) else "")
    if 'Time to Interactive (TTI)' in display_df.columns:
        display_df['Time to Interactive (TTI)'] = display_df['Time to Interactive (TTI)'].apply(lambda x: f"{x} s" if pd.notnull(x) else "")
        
    st.dataframe(display_df)
    
    st.subheader("📈 Website Metrics Comparison Graph")
    
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("🎯 Choose Metric to Visualize on Graph:", metrics_to_chart)
    
    chart_data = filtered_df.pivot_table(index='URL', values=selected_metric, aggfunc='mean')
    st.bar_chart(chart_data)

else:
    st.warning(f"Backend file '{excel_file}' not found.")