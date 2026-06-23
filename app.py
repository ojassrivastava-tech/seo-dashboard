import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# 1. Page Configuration & Styling for Mobile Responsiveness
st.set_page_config(
    page_title="Enterprise SEO & Performance Suite", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Global Mobile Adjustments */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 1rem !important;
        }
        h1 { font-size: 1.8rem !important; text-align: center; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.1rem !important; }
        div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    }
    
    /* Status Badges Styling */
    .badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
        display: inline-block;
        text-align: center;
        margin-top: 5px;
    }
    .good { background-color: #0cce6b; }
    .needs-improvement { background-color: #ffa400; }
    .poor { background-color: #ff4e42; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Enterprise Performance & SEO Suite")
st.caption("Enterprise Web Optimization & Core Web Vitals Analytics Engine")

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
    if score >= 90: return "🟢 Good", "good"
    elif score >= 50: return "🟠 Needs Improvement", "needs-improvement"
    else: return "🔴 Poor", "poor"

def get_badge_html(score):
    if score >= 90: return f'<span class="badge good">{score}% (Good)</span>'
    elif score >= 50: return f'<span class="badge needs-improvement">{score}% (Needs Imp.)</span>'
    else: return f'<span class="badge poor">{score}% (Poor)</span>'

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

# --- API HELPER FUNCTION ---
def fetch_psi_data(url, strategy, api_key):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy.lower()}&key={api_key}"
    for category in ["performance", "seo", "accessibility", "best-practices"]:
        api_url += f"&category={category}"
    try:
        response = requests.get(api_url, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: Status {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def extract_metrics(json_data):
    if "error" in json_data or "lighthouseResult" not in json_data:
        return None
    
    lighthouse = json_data["lighthouseResult"]
    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})
    
    scores = {
        "Performance": int((categories.get("performance", {}).get("score", 0)) * 100),
        "SEO": int((categories.get("seo", {}).get("score", 0)) * 100),
        "Accessibility": int((categories.get("accessibility", {}).get("score", 0)) * 100),
        "Best Practices": int((categories.get("best-practices", {}).get("score", 0)) * 100)
    }
    
    fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
    tti = audits.get("interactive", {}).get("displayValue", "N/A")
    cls_val = float(audits.get("cumulative-layout-shift", {}).get("numericValue", 0))
    
    opps = []
    for audit_name, audit_data in audits.items():
        if audit_data.get("details", {}).get("type") == "opportunity":
            title = audit_data.get("title")
            description = audit_data.get("description", "")
            wasted_ms = audit_data.get("details", {}).get("overallSavingsMs", 0)
            if wasted_ms > 0:
                opps.append({"Opportunity": title, "Estimated Savings": f"{wasted_ms / 1000.0:.2f} s", "Description": description})
                
    return {"scores": scores, "vitals": {"FCP": fcp, "TTI": tti, "CLS": f"{cls_val:.2f}"}, "opportunities": opps}

# --- RENDER COMPARISON CHART (Mobile Locked) ---
def render_comparison_chart(my_scores, comp_scores):
    categories = list(my_scores.keys())
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=list(my_scores.values()),
        name='Your Website',
        marker_color='#10B981',
        text=list(my_scores.values()),
        textposition='outside'
    ))
    fig.add_trace(go.Bar(
        x=categories,
        y=list(comp_scores.values()),
        name='Competitor',
        marker_color='#3B82F6',
        text=list(comp_scores.values()),
        textposition='outside'
    ))
    
    fig.update_layout(
        barmode='group',
        height=300,
        template='plotly_dark',
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        dragmode=False,
        xaxis=dict(fixedrange=True, showgrid=False),
        yaxis=dict(fixedrange=True, range=[0, 115], showgrid=False)
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- USER CONTROL INTERFACE ---
mode = st.radio("Select Analysis Mode:", ["Single Audit", "Competitor Comparison ⚔️"], horizontal=True)
strategy = st.radio("Select Target Device Environment:", ["Mobile", "Desktop"], horizontal=True)

API_KEY = "AIzaSyCxic-4hCaYk4rNUaLD8yExJKOlyqoy1WE"

# --- EXECUTION LOGIC ---
if mode == "Single Audit":
    url = st.text_input("Enter Website URL:", placeholder="https://example.com")
    if st.button("Run Full Core Audit", type="primary"):
        if not url:
            st.error("Please enter a valid URL.")
        else:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            with st.spinner(f"Connecting to Google Servers... Running {strategy} analysis..."):
                raw_data = fetch_psi_data(url, strategy, API_KEY)
                metrics = extract_metrics(raw_data)
                
                if metrics is None:
                    st.error("Could not fetch data. Check the URL or connection.")
                else:
                    st.success(f"Full {strategy} Audit Completed Successfully!")
                    
                    st.markdown("#### 🎯 Core Optimization Scores")
                    m1, m2 = st.columns(2)
                    p_label, _ = get_status_indicator(metrics["scores"]["Performance"])
                    s_label, _ = get_status_indicator(metrics["scores"]["SEO"])
                    a_label, _ = get_status_indicator(metrics["scores"]["Accessibility"])
                    b_label, _ = get_status_indicator(metrics["scores"]["Best Practices"])
                    
                    with m1:
                        st.metric(label="📈 Performance Score", value=f"{metrics['scores']['Performance']}%", delta=p_label)
                        st.metric(label="Accessibility Score", value=f"{metrics['scores']['Accessibility']}%", delta=a_label)
                    with m2:
                        st.metric(label="🔍 SEO Score", value=f"{metrics['scores']['SEO']}%", delta=s_label)
                        st.metric(label="🛡️ Best Practices Score", value=f"{metrics['scores']['Best Practices']}%", delta=b_label)
                    
                    st.markdown("#### ⏱️ User Experience & Core Web Vitals")
                    s1, s2, s3 = st.columns(3)
                    with s1: st.metric(label="⏱️ FCP", value=metrics["vitals"]["FCP"])
                    with s2: st.metric(label="⚡ TTI", value=metrics["vitals"]["TTI"])
                    with s3: st.metric(label="📉 CLS", value=metrics["vitals"]["CLS"])
                    
                    csv_data = convert_advanced_df(url, strategy, metrics["scores"]["Performance"], metrics["scores"]["SEO"], metrics["scores"]["Accessibility"], metrics["scores"]["Best Practices"], metrics["vitals"]["FCP"], metrics["vitals"]["TTI"], metrics["vitals"]["CLS"])
                    st.download_button(label="📥 Download Full Executive Report (CSV)", data=csv_data, file_name=f"pagespeed_{strategy.lower()}_audit.csv", mime='text/csv', use_container_width=True)
                    
                    if metrics["opportunities"]:
                        st.markdown("---")
                        st.markdown("### 🛠️ Optimization Opportunities & Diagnostics")
                        for op in metrics["opportunities"]:
                            with st.expander(f"⚠️ {op['Opportunity']} (Potential Savings: {op['Estimated Savings']})"):
                                st.write(op["Description"])

else:
    # COMPETITOR COMPARISON MODE
    c1, c2 = st.columns(2)
    with c1:
        my_url = st.text_input("Your Website URL:", placeholder="https://mywebsite.com")
    with c2:
        comp_url = st.text_input("Competitor's Website URL:", placeholder="https://competitor.com")
        
    if st.button("Compare Performance ⚔️", type="primary"):
        if not my_url or not comp_url:
            st.error("Please enter both URLs to run the comparison.")
        else:
            if not my_url.startswith("http://") and not my_url.startswith("https://"): my_url = "https://" + my_url
            if not comp_url.startswith("http://") and not comp_url.startswith("https://"): comp_url = "https://" + comp_url
            
            with st.spinner("Analyzing both domains parallelly via Google Suite..."):
                my_raw = fetch_psi_data(my_url, strategy, API_KEY)
                comp_raw = fetch_psi_data(comp_url, strategy, API_KEY)
                
                my_metrics = extract_metrics(my_raw)
                comp_metrics = extract_metrics(comp_raw)
                
                if not my_metrics or not comp_metrics:
                    st.error("Error processing data from Google API for one or both URLs.")
                else:
                    st.success("Comparison Battle Complete!")
                    
                    st.markdown("### 📊 Side-by-Side Pillar Comparison")
                    render_comparison_chart(my_metrics["scores"], comp_metrics["scores"])
                    
                    st.markdown("---")
                    
                    # Fixed loop variables below using standard unsafe_allow_html parameters
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown(f"#### 🏠 Your Site: `{my_url.replace('https://', '').replace('www.', '')[:22]}`")
                        for pillar, val in my_metrics["scores"].items():
                            st.markdown(f"**{pillar}**: {get_badge_html(val)}", unsafe_allow_html=True)
                        st.markdown("**Core Web Vitals:**")
                        st.write(f"⏱️ **FCP:** {my_metrics['vitals']['FCP']} | ⚡ **TTI:** {my_metrics['vitals']['TTI']} | 📉 **CLS:** {my_metrics['vitals']['CLS']}")
                        
                    with col_right:
                        st.markdown(f"#### 👺 Competitor: `{comp_url.replace('https://', '').replace('www.', '')[:22]}`")
                        for pillar, val in comp_metrics["scores"].items():
                            st.markdown(f"**{pillar}**: {get_badge_html(val)}", unsafe_allow_html=True)
                        st.markdown("**Core Web Vitals:**")
                        st.write(f"⏱️ **FCP:** {comp_metrics['vitals']['FCP']} | ⚡ **TTI:** {comp_metrics['vitals']['TTI']} | 📉 **CLS:** {comp_metrics['vitals']['CLS']}")

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
        with col1: st.metric(label="⏱️ FCP Speed", value=f"{row['First Contentful Paint (FCP)']} s")
        with col2: st.metric(label="⚡ TTI Speed", value=f"{row['Time to Interactive (TTI)']} s")
    else:
        expected_cols = ['URL', 'Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)']
        available_cols = [col for col in expected_cols if col in df.columns]
        st.dataframe(filtered_df[available_cols].copy(), use_container_width=True, hide_index=True)
    
    st.markdown("### 📈 Historical Metric Comparison Graph")
    metrics_to_chart = [col for col in ['Performance Score (%)', 'First Contentful Paint (FCP)', 'Time to Interactive (TTI)'] if col in df.columns]
    selected_metric = st.selectbox("Select metric for historical graph:", metrics_to_chart)
    chart_data = filtered_df.groupby('URL', as_index=False)[selected_metric].mean().dropna()
    
    if not chart_data.empty:
        chart_data['Clean_URL'] = chart_data['URL'].str.replace('https://www.', '').str.replace('https://', '').str.replace('http://', '')
        fig = px.bar(chart_data, x=selected_metric, y='Clean_URL', color=selected_metric, text=selected_metric, orientation='h', color_continuous_scale=px.colors.sequential.Viridis, template="plotly_dark")
        fig.update_traces(texttemplate=' %{text:.1f}', textposition='outside')
        fig.update_layout(margin=dict(l=110, r=40, t=10, b=10), height=280, coloraxis_showscale=False, xaxis_title=selected_metric, yaxis_title=None, dragmode=False)
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True, tickfont=dict(size=11))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.warning(f"Historical report file '{excel_file}' not found or empty.")
