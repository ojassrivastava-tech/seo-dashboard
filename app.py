import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px

# 1. Page Configuration - Strict Mobile First Layout
st.set_page_config(
    page_title="SEO Dashboard", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.title("🚀 SEO & Web Performance Dashboard")

excel_file = "seo_speed_report.xlsx"

# ⚡ FAST LOADING FUNCTION (Cache for pre-saved data)
@st.cache_data(ttl=60)
def load_and_clean_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        for col in ['First Contentful Paint (FCP)', 'Time to Interactive (TTI)']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'[^0-9.]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'Performance Score (%)' in df.columns:
            df['Performance Score (%)'] = pd.to_numeric(df['Performance Score (%)'], errors='coerce')
        return df
    except:
        return None

df = load_and_clean_data(excel_file)

# ==========================================
# 🛠️ LIVE CUSTOM URL SCANNER (WITH SMOOTH ERROR HANDLING)
# ==========================================
st.markdown("---")
st.markdown("### 🔍 Live Website SEO Checker")
st.write("Enter any custom URL below to test its live performance via Google PageSpeed Insights:")

user_url = st.text_input("Enter Website URL (e.g., https://example.com)", placeholder="https://...")

if st.button("⚡ Run Live Audit"):
    if user_url:
        if not user_url.startswith("http://") and not user_url.startswith("https://"):
            user_url = "https://" + user_url
            
        with st.spinner("Fetching live data from Google API... Please wait..."):
            try:
                api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={user_url}&category=performance"
                response = requests.get(api_url, timeout=30)
                
                # Handled response status codes professionally
                if response.status_code == 200:
                    data = response.json()
                    if "lighthouseResult" in data:
                        lighthouse = data["lighthouseResult"]
                        
                        # Extract Metrics
                        perf_score = int(lighthouse["categories"]["performance"]["score"] * 100)
                        fcp = lighthouse["audits"]["first-contentful-paint"]["displayValue"]
                        tti = lighthouse["audits"]["interactive"]["displayValue"]
                        
                        # Display Results in Gorgeous Mobile Cards
                        st.success(f"Analysis completed for: {user_url}")
                        
                        st.metric(label="🎯 Live Performance Score", value=f"{perf_score}%")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric(label="⏱️ Live FCP", value=f"{fcp}")
                        with c2:
                            st.metric(label="⚡ Live TTI", value=f"{tti}")
                    else:
                        st.error("Lighthouse data not found in response. Try another URL.")
                elif response.status_code == 429:
                    st.error("🚦 Google API is temporarily busy due to multiple quick requests. Please wait 1-2 minutes and click 'Run Live Audit' again.")
                else:
                    st.error(f"Could not fetch data for this URL. (Status Code: {response.status_code})")
            except Exception as e:
                st.error("Connection timeout. Google API is taking too long or URL is invalid.")
    else:
        st.warning("Please enter a valid URL first!")

# ==========================================
# 📊 PRE-SAVED DATA SECTION (Historical Report)
# ==========================================
st.markdown("---")
st.markdown("### 🗃️ Monitored Sites Matrix (Historical Report)")

if df is not None:
    all_sites = ["All Websites"] + list(df['URL'].unique())
    selected_site = st.selectbox("Choose a pre-saved site to inspect:", all_sites)
    
    filtered_df = df if selected_site == "All Websites" else df[df['URL'] == selected_site]

    if selected_site != "All Websites" and len(filtered_df) > 0:
        row = filtered_df.iloc[0]
        st.metric(label="🎯 Performance Score", value=f"{int(row['Performance Score (%)'])}%")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="⏱️ FCP Speed", value=f"{row['First Contentful Paint (FCP)']} s")
        with col2:
            st.metric(label="⚡ TTI Speed", value=f"{row['Time to Interactive (TTI)']} s")
    else:
        expected_cols = ['URL', 'Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)']
        available_cols = [col for col in expected_cols if col in df.columns]
        display_df = filtered_df[available_cols].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 📈 Premium Interactive Graph via Plotly
    st.markdown("### 📈 Metric Comparison Graph")
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("Select metric for graph:", metrics_to_chart)
    
    chart_data = filtered_df.pivot_table(index='URL', values=selected_metric, aggfunc='mean').reset_index()
    
    fig = px.bar(
        chart_data, 
        x='URL', 
        y=selected_metric, 
        color=selected_metric,
        color_continuous_scale=px.colors.sequential.Viridis,
        template="plotly_dark"
    )
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning(f"Data file '{excel_file}' not found.")
