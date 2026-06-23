import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px

# 1. Page Configuration - Strict Mobile Responsive Layout
st.set_page_config(
    page_title="SEO Dashboard", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.title("🚀 SEO & Web Performance Dashboard")

excel_file = "seo_speed_report.xlsx"

# ⚡ FAST LOADING FUNCTION
@st.cache_data(ttl=60)
def load_and_clean_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(subset=['URL'])
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
# 🛠️ LIVE CUSTOM URL SCANNER
# ==========================================
st.markdown("---")
st.markdown("### 🔍 Live Website SEO Checker")
st.write("Enter any custom URL below to test its live performance via Google PageSpeed Insights:")

user_url = st.text_input("Enter Website URL (e.g., https://example.com)", placeholder="https://...")

API_KEY = "AIzaSyCxic-4hCaYk4rNUaLD8yExJKOlyqoy1WE"

if st.button("⚡ Run Live Audit"):
    if user_url:
        if not user_url.startswith("http://") and not user_url.startswith("https://"):
            user_url = "https://" + user_url
            
        with st.spinner("Fetching live data from Google API... Please wait..."):
            try:
                api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={user_url}&category=performance&key={API_KEY}"
                response = requests.get(api_url, timeout=45)
                
                if response.status_code == 200:
                    data = response.json()
                    if "lighthouseResult" in data:
                        lighthouse = data["lighthouseResult"]
                        
                        perf_score = int(lighthouse["categories"]["performance"]["score"] * 100)
                        fcp_val = float(lighthouse["audits"]["first-contentful-paint"]["numericValue"]) / 1000.0
                        tti_val = float(lighthouse["audits"]["interactive"]["numericValue"]) / 1000.0
                        
                        fcp_display = lighthouse["audits"]["first-contentful-paint"]["displayValue"]
                        tti_display = lighthouse["audits"]["interactive"]["displayValue"]
                        
                        st.success(f"Analysis completed for: {user_url}")
                        st.metric(label="🎯 Live Performance Score", value=f"{perf_score}%")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric(label="⏱️ Live FCP", value=f"{fcp_display}")
                        with c2:
                            st.metric(label="⚡ Live TTI", value=f"{tti_display}")
                        
                        st.markdown("#### 📊 Live Metric Analysis Chart")
                        
                        live_data = pd.DataFrame({
                            'Metric Name': ['Performance Score (%)', 'First Contentful Paint (s)', 'Time to Interactive (s)'],
                            'Value': [perf_score, fcp_val, tti_val],
                            'Type': ['Score (Higher is Better)', 'Speed (Lower is Better)', 'Speed (Lower is Better)']
                        })
                        
                        fig_live = px.bar(
                            live_data,
                            x='Value',
                            y='Metric Name',
                            color='Type',
                            text='Value',
                            orientation='h',
                            template='plotly_dark',
                            color_discrete_map={
                                'Score (Higher is Better)': '#10B981',
                                'Speed (Lower is Better)': '#3B82F6'
                            }
                        )
                        
                        fig_live.update_traces(texttemplate=' %{text:.1f}', textposition='outside')
                        fig_live.update_layout(
                            height=250, 
                            showlegend=True, 
                            legend_title=None,
                            margin=dict(l=10, r=40, t=10, b=10),
                            xaxis_title=None,
                            yaxis_title=None
                        )
                        fig_live.update_xaxes(matches=None, showgrid=False)
                        st.plotly_chart(fig_live, use_container_width=True)
                        
                    else:
                        st.error("Lighthouse data not found in response. Try another URL.")
                elif response.status_code == 429:
                    st.error("🚦 Quota or rate limit hit. Please wait a moment and try again.")
                else:
                    st.error(f"Google API Error. (Status Code: {response.status_code})")
            except Exception as e:
                st.error("Connection timeout. Google API is taking too long or URL is invalid.")
    else:
        st.warning("Please enter a valid URL first!")

# ==========================================
# 📊 PRE-SAVED DATA SECTION (Historical Report)
# ==========================================
st.markdown("---")
st.markdown("### 🗃️ Monitored Sites Matrix (Historical Report)")

if df is not None and not df.empty:
    all_sites = ["All Websites"] + list(df['URL'].dropna().unique())
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
    
    # 📈 FIX FOR HISTORICAL GRAPH: Horizontal Mobile Optimized Layout
    st.markdown("### 📈 Historical Metric Comparison Graph")
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("Select metric for historical graph:", metrics_to_chart)
    
    chart_data = filtered_df.groupby('URL', as_index=False)[selected_metric].mean().dropna()
    
    if not chart_data.empty:
        # Changed orientation to 'h' (Horizontal) for proper mobile formatting
        fig = px.bar(
            chart_data, 
            x=selected_metric, 
            y='URL', 
            color=selected_metric,
            text=selected_metric,
            orientation='h',
            color_continuous_scale=px.colors.sequential.Viridis,
            template="plotly_dark"
        )
        # Formatting for mobile: removed side legend to give graph maximum width
        fig.update_traces(texttemplate=' %{text:.1f}', textposition='outside')
        fig.update_layout(
            margin=dict(l=10, r=40, t=10, b=10), 
            height=300, 
            coloraxis_showscale=False, # Side color legend bar ko chupa diya space bachane ke liye
            xaxis_title=selected_metric,
            yaxis_title=None
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning(f"Data file '{excel_file}' not found or empty.")
