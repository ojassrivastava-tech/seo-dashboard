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
""", unsafe_allow_html=True)  # <-- Yahan 'unsafe_allow_html' kar diya hai
