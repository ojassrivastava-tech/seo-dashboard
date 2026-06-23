import streamlit as st
import pandas as pd
import os
import requests
import plotly.express as px
from datetime import datetime

# 1. Page Configuration - Strict Mobile Responsive Layout
st.set_page_config(
    page_title="SEO & Web Audit Portal", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.title("🚀 Google PageSpeed Insights Audit Portal")
st.caption("Enterprise Web Optimization Engine - Ditto Google Pro Specs")

excel_file = "seo_speed_report.xlsx"

# ⚡ FAST LOADING FUNCTION FOR HISTORICAL DATA
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

# Helper function for Traffic Light Color Coding (PageSpeed Rules)
def get_status_indicator(score):
    if score >= 90:
        return "🟢 Good", "green"
    elif score >= 50:
        return "🟠 Needs Improvement", "orange"
    else:
        return "🔴 Poor", "red"

# Helper function to convert dynamic multi-metric data to downloadable CSV
def convert_advanced_df(url, strategy, perf, seo, access, best_prac, fcp, tti, cls):
    report_data = pd.DataFrame([{
        'Audit Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Target URL': url,
        'Device Strategy': strategy.upper(),
        'Performance Score': f"{perf}%",
        'SEO Score': f"{seo}%",
        'Accessibility Score': f"{access}%",
        'Best Practices Score': f"{best_prac}%",
        'First Contentful Paint (FCP)': fcp,
        'Time to Interactive (TTI)': tti,
        'Cumulative Layout Shift (CLS)': cls
    }])
    return report_data.to_csv(index=False).encode('utf-8')

# ==========================================
# 🔍 GOOGLE ENTERPRISE LIVE URL AUDIT 
# ==========================================
st.markdown("---")
st.markdown("### 🌐 Real-Time Full Website Audit")
st.write("Enter any URL below to perform a standard Google Lighthouse audit suite:")

user_url = st.text_input("Enter Website URL", placeholder="https://example.com")

# 📱/💻 GOOGLE DITTO UPGRADE 1: Mobile vs Desktop Toggle Switch
strategy = st.radio("Select Target Device Environment:", ["Mobile", "Desktop"], horizontal=True)

# Dedicated Personal Google API Key
API_KEY = "AIzaSyCxic-4hCaYk4rNUaLD8yExJKOlyqoy1WE"

if st.button("⚡ Run Full Core Audit"):
    if user_url:
        if not user_url.startswith("http://") and not user_url.startswith("https://"):
            user_url = "https://" + user_url
            
        with st.spinner(f"Connecting to Google Servers... Running full {strategy} analysis..."):
            try:
                # Dynamic strategy injection (mobile/desktop) inside official Google API request
                api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={user_url}&category=performance&category=seo&category=accessibility&category=best-practices&strategy={strategy.lower()}&key={API_KEY}"
                response = requests.get(api_url, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    if "lighthouseResult" in data:
                        lighthouse = data["lighthouseResult"]
                        cats = lighthouse["categories"]
                        audits = lighthouse["audits"]
                        
                        # Extracting Google Core Pillars Scores
                        perf_score = int(cats["performance"]["score"] * 100)
                        seo_score = int(cats["seo"]["score"] * 100)
                        access_score = int(cats["accessibility"]["score"] * 100)
                        best_prac_score = int(cats["best-practices"]["score"] * 100)
                        
                        # Extracting Speed Performance Metrics
                        fcp_disp = audits["first-contentful-paint"]["displayValue"]
                        tti_disp = audits["interactive"]["displayValue"]
                        cls_val = float(audits["cumulative-layout-shift"]["numericValue"])
                        
                        st.success(f"Full {strategy} Audit Completed Successfully!")
                        
                        # 📊 GOOGLE PAGESPEED DISPLAY (With Status Badges)
                        st.markdown(f"#### 🎯 Core Optimization Scores ({strategy})")
                        
                        p_label, p_color = get_status_indicator(perf_score)
                        s_label, s_color = get_status_indicator(seo_score)
                        a_label, a_color = get_status_indicator(access_score)
                        b_label, b_color = get_status_indicator(best_prac_score)
                        
                        m1, m2 = st.columns(2)
                        with m1:
                            st.metric(label="📈 Performance Score", value=f"{perf_score}%", delta=p_label, delta_color="normal")
                            st.metric(label="Accessibility Score", value=f"{access_score}%", delta=a_label, delta_color="normal")
                        with m2:
                            st.metric(label="🔍 SEO Score", value=f"{seo_score}%", delta=s_label, delta_color="normal")
                            st.metric(label="🛡️ Best Practices Score", value=f"{best_prac_score}%", delta=b_label, delta_color="normal")
                            
                        # ⏱️ Speed Pillars
                        st.markdown("#### ⏱️ User Experience & Core Web Vitals")
                        s1, s2, s3 = st.columns(3)
                        with s1:
                            st.metric(label="⏱️ FCP", value=fcp_disp)
                        with s2:
                            st.metric(label="⚡ TTI", value=tti_disp)
                        with s3:
                            st.metric(label="📉 CLS", value=f"{cls_val:.2f}")

                        # 📥 Report Download Button (CSV Format)
                        csv_data = convert_advanced_df(user_url, strategy, perf_score, seo_score, access_score, best_prac_score, fcp_disp, tti_disp, cls_val)
                        st.download_button(
                            label="📥 Download Full Executive Report (CSV)",
                            data=csv_data,
                            file_name=f"pagespeed_{strategy.lower()}_audit_{user_url.replace('https://', '').replace('/', '_')}.csv",
                            mime='text/csv',
                            use_container_width=True
                        )
                        
                        # 📈 DYNAMIC HORIZONTAL GRAPH BREAKDOWN (MOBILE STABLE)
                        st.markdown("#### 📊 Metric Analysis Chart")
                        chart_df = pd.DataFrame({
                            'Metric Category': ['Performance', 'SEO', 'Accessibility', 'Best Practices'],
                            'Score (%)': [perf_score, seo_score, access_score, best_prac_score]
                        })
                        
                        fig_live = px.bar(
                            chart_df,
                            x='Score (%)',
                            y='Metric Category',
                            color='Score (%)',
                            text='Score (%)',
                            orientation='h',
                            template='plotly_dark',
                            color_continuous_scale=px.colors.sequential.Plotly3
                        )
                        fig_live.update_traces(texttemplate=' %{text}%', textposition='outside')
                        fig_live.update_layout(
                            height=240, 
                            coloraxis_showscale=False,
                            margin=dict(l=100, r=40, t=10, b=10),
                            xaxis_title=None, yaxis_title=None, dragmode=False
                        )
                        fig_live.update_xaxes(fixedrange=True, range=[0, 115], showgrid=False)
                        fig_live.update_yaxes(fixedrange=True)
                        st.plotly_chart(fig_live, use_container_width=True, config={'displayModeBar': False})
                        
                        # 🛠️ GOOGLE DITTO UPGRADE 2: Opportunities & Diagnostics (Real Engine Suggestions)
                        st.markdown("---")
                        st.markdown("### 🛠️ Optimization Opportunities & Diagnostics")
                        st.write("Fix these technical issues to instantly uplift this score:")
                        
                        opp_count = 0
                        for audit_name, audit_data in audits.items():
                            # Filter audits that have actionable savings guidelines from Google
                            if 'details' in audit_data and audit_data['details'].get('type') == 'opportunity':
                                title = audit_data.get('title')
                                description = audit_data.get('description', '')
                                overall_savings = audit_data['details'].get('overallSavingsMs', 0)
                                
                                if overall_savings > 0:
                                    opp_count += 1
                                    savings_sec = overall_savings / 1000.0
                                    with st.expander(f"⚠️ {title} (Potential Savings: {savings_sec:.2f}s)"):
                                        st.write(description)
                        
                        if opp_count == 0:
                            st.success("🎉 Excellent! Google found no major optimization layout opportunities for this strategy.")
                        
                    else:
                        st.error("Google Lighthouse structure parsing failed. Please try again.")
                else:
                    st.error(f"Google Engine API Error. (Status Code: {response.status_code})")
            except Exception as e:
                st.error("Audit Timeout. Google servers took too long to analyze this website.")
    else:
        st.warning("Please enter a valid website URL first!")

# ==========================================
# 📊 PRE-SAVED HISTORICAL REPORTS SECTION
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
    
    # Historical Graph
    st.markdown("### 📈 Historical Metric Comparison Graph")
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("Select metric for historical graph:", metrics_to_chart)
    
    chart_data = filtered_df.groupby('URL', as_index=False)[selected_metric].mean().dropna()
    
    if not chart_data.empty:
        chart_data['Clean_URL'] = chart_data['URL'].str.replace('https://www.', '').str.replace('https://', '').str.replace('http://', '')
        fig = px.bar(
            chart_data, 
            x=selected_metric, 
            y='Clean_URL', 
            color=selected_metric,
            text=selected_metric,
            orientation='h',
            color_continuous_scale=px.colors.sequential.Viridis,
            template="plotly_dark"
        )
        fig.update_traces(texttemplate=' %{text:.1f}', textposition='outside')
        fig.update_layout(
            margin=dict(l=110, r=40, t=10, b=10), 
            height=280, coloraxis_showscale=False, 
            xaxis_title=selected_metric, yaxis_title=None, dragmode=False
        )
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True, tickfont=dict(size=11))
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

else:
    st.warning(f"Historical report file '{excel_file}' not found or empty.")
