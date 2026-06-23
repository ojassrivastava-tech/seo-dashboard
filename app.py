import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Page Configuration & Styling for Mobile Responsiveness
st.set_page_config(page_title="Enterprise SEO & Performance Suite", layout="wide")

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
""", unsafe_with_html=True)

st.title("🚀 Enterprise Performance & SEO Suite")
st.caption("Compare your website directly against competitors or run standard single audits.")

# --- API HELPER FUNCTION ---
def fetch_psi_data(url, strategy, api_key=None):
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}"
    for category in ["performance", "seo", "accessibility", "best-practices"]:
        api_url += f"&category={category}"
    if api_key:
        api_url += f"&key={api_key}"
        
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: Status {response.status_code}"}
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

def extract_metrics(json_data):
    if "error" in json_data:
        return None
    
    categories = json_data.get("lighthouseResult", {}).get("categories", {})
    audits = json_data.get("lighthouseResult", {}).get("audits", {})
    
    # Extract Scores (0-100 format)
    scores = {
        "Performance": int((categories.get("performance", {}).get("score", 0)) * 100),
        "SEO": int((categories.get("seo", {}).get("score", 0)) * 100),
        "Accessibility": int((categories.get("accessibility", {}).get("score", 0)) * 100),
        "Best Practices": int((categories.get("best-practices", {}).get("score", 0)) * 100)
    }
    
    # Extract Web Vitals & Speeds
    fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
    lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
    cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
    tbt = audits.get("total-blocking-time", {}).get("displayValue", "N/A")
    speed_index = audits.get("speed-index", {}).get("displayValue", "N/A")
    
    # Extract Opportunities
    opps = []
    for audit_name, audit_data in audits.items():
        if audit_data.get("details", {}).get("type") == "opportunity":
            title = audit_data.get("title")
            description = audit_data.get("description")
            wasted_ms = audit_data.get("details", {}).get("overallSavingsMs", 0)
            if wasted_ms > 0:
                opps.append({"Opportunity": title, "Estimated Savings": f"{wasted_ms} ms", "Description": description})
                
    return {"scores": scores, "vitals": {"FCP": fcp, "LCP": lcp, "CLS": cls, "TBT": tbt, "Speed Index": speed_index}, "opportunities": opps}

def get_badge_html(score):
    if score >= 90: return f'<span class="badge good">{score} (Good)</span>'
    elif score >= 50: return f'<span class="badge needs-improvement">{score} (Needs Imp.)</span>'
    else: return f'<span class="badge poor">{score} (Poor)</span>'

# --- RENDER COMPARISON CHART (Mobile Friendly) ---
def render_comparison_chart(my_scores, comp_scores):
    categories = list(my_scores.keys())
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=list(my_scores.values()),
        name='Your Website',
        marker_color='#0066cc'
    ))
    fig.add_trace(go.Bar(
        x=categories,
        y=list(comp_scores.values()),
        name='Competitor',
        marker_color='#ff4e42'
    ))
    
    fig.update_layout(
        barmode='group',
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        dragmode=False, # Disable zooming for smooth mobile scrolling
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True, range=[0, 100])
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- USER CONTROL INTERFACE ---
st.sidebar.header("⚙️ Configuration")
mode = st.sidebar.radio("Select Mode", ["Single Audit", "Competitor Comparison ⚔️"])
strategy = st.sidebar.radio("Device Strategy", ["mobile", "desktop"], index=0)
api_key = st.sidebar.text_input("Google API Key (Optional)", type="password")

# --- EXECUTION LOGIC ---
if mode == "Single Audit":
    url = st.text_input("Enter Website URL:", placeholder="https://example.com")
    if st.button("Run Audit", type="primary"):
        if not url:
            st.error("Please enter a valid URL.")
        else:
            with st.spinner("Fetching data from Google..."):
                raw_data = fetch_psi_data(url, strategy, api_key)
                metrics = extract_metrics(raw_data)
                
                if metrics is None:
                    st.error("Could not fetch data. Check the URL or API Key.")
                else:
                    st.success("Audit Completed!")
                    
                    # Core Pillars Metrics Rows
                    cols = st.columns(4)
                    for i, (pillar, val) in enumerate(metrics["scores"].items()):
                        with cols[i]:
                            st.markdown(f"**{pillar}**")
                            st.markdown(get_badge_html(val), unsafe_with_html=True)
                    
                    st.markdown("---")
                    
                    # Web Vitals Metrics
                    v_cols = st.columns(5)
                    for i, (k, v) in enumerate(metrics["vitals"].items()):
                        with v_cols[i]:
                            st.metric(label=k, value=v)
                            
                    # Opportunities
                    if metrics["opportunities"]:
                        st.markdown("### 🛠️ Optimization Opportunities")
                        for op in metrics["opportunities"]:
                            with st.expander(f"{op['Opportunity']} — {op['Estimated Savings']}"):
                                st.write(op["Description"])

else:
    # COMPETITOR COMPARISON MODE
    # CSS grid structure ensures stacked format on smaller mobile displays automatically via Streamlit columns
    c1, c2 = st.columns(2)
    with c1:
        my_url = st.text_input("Your Website URL:", placeholder="https://mywebsite.com")
    with c2:
        comp_url = st.text_input("Competitor's Website URL:", placeholder="https://competitor.com")
        
    if st.button("Compare Performance ⚔️", type="primary"):
        if not my_url or not comp_url:
            st.error("Please enter both URLs to run the comparison.")
        else:
            with st.spinner("Analyzing both domains in parallel..."):
                # Fetching both URLs
                my_raw = fetch_psi_data(my_url, strategy, api_key)
                comp_raw = fetch_psi_data(comp_url, strategy, api_key)
                
                my_metrics = extract_metrics(my_raw)
                comp_metrics = extract_metrics(comp_raw)
                
                if not my_metrics or not comp_metrics:
                    st.error("Error processing data for one or both URLs.")
                else:
                    st.success("Comparison Battle Complete!")
                    
                    # 1. Graphical Chart comparison
                    st.markdown("### 📊 Side-by-Side Pillar Comparison")
                    render_comparison_chart(my_metrics["scores"], comp_metrics["scores"])
                    
                    st.markdown("---")
                    
                    # 2. Detailed Breakdown Grid (Automatically stacks on mobile)
                    col_left, col_right = st.columns(2)
                    
                    with col_left:
                        st.markdown(f"#### 🏠 Your Site: `{my_url.replace('https://', '').replace('www.', '')[:20]}...`")
                        for pillar, val in my_metrics["scores"].items():
                            st.markdown(f"**{pillar}**: {get_badge_html(val)}", unsafe_with_html=True)
                        st.markdown("**Core Web Vitals:**")
                        st.json(my_metrics["vitals"])
                        
                    with col_right:
                        st.markdown(f"#### 👺 Competitor: `{comp_url.replace('https://', '').replace('www.', '')[:20]}...`")
                        for pillar, val in comp_metrics["scores"].items():
                            st.markdown(f"**{pillar}**: {get_badge_html(val)}", unsafe_with_html=True)
                        st.markdown("**Core Web Vitals:**")
                        st.json(comp_metrics["vitals"])
