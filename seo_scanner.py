import requests
import pandas as pd
from datetime import datetime

# =====================================================================
# CONFIGURATION
# =====================================================================
# Google Cloud Console API key configured directly:
API_KEY = "AIzaSyAKDEUUJjx9VubkTR5cHxs6vytpzTFux_A"  

# List of target websites to scan (Your site + Competitors)
URLS_TO_SCAN = [
    "https://www.building10x.com",
    "https://www.amazon.in",
    "https://www.flipkart.com",
    "https://www.myntra.com"
]
# =====================================================================

def check_page_speed(target_url, api_key):
    print(f"\nScanning: {target_url} ... Please wait...")
    
    # PageSpeed Insights API endpoint (Performance Category)
    endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&key={api_key}&category=PERFORMANCE"
    
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            
            # Extract Core Metrics from Lighthouse results
            lighthouse_result = data.get('lighthouseResult', {})
            audits = lighthouse_result.get('audits', {})
            
            # Extract scores and convert performance to percentage
            performance_score = lighthouse_result.get('categories', {}).get('performance', {}).get('score', 0) * 100
            fcp = audits.get('first-contentful-paint', {}).get('displayValue', 'N/A')
            speed_index = audits.get('speed-index', {}).get('displayValue', 'N/A')
            tti = audits.get('interactive', {}).get('displayValue', 'N/A')
            
            return {
                "URL": target_url,
                "Performance Score (%)": round(performance_score, 2),
                "First Contentful Paint (FCP)": fcp,
                "Speed Index": speed_index,
                "Time to Interactive (TTI)": tti,
                "Scan Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"❌ Error fetching data for {target_url}: Status Code {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ An error occurred for {target_url}: {e}")
        return None

# --- Main Execution Loop ---
if __name__ == "__main__":
    print("🚀 Bulk SEO Scanner Started...")
    all_results = []
    
    # Loop through each URL in the list
    for url in URLS_TO_SCAN:
        result = check_page_speed(url, API_KEY)
        if result:
            all_results.append(result)
            print(f"✅ Success! Score: {result['Performance Score (%)']}%")
    
    # Export results to an Excel sheet if data is collected
    if all_results:
        df = pd.DataFrame(all_results)
        output_file = "seo_speed_report.xlsx"
        
        df.to_excel(output_file, index=False)
        print(f"\n🎉 Task Completed! Data saved to '{output_file}'. 🔥")
    else:
        print("\n❌ Failed to fetch data. Please verify your API Key.")