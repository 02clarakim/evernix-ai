import os
from datetime import date
import matplotlib.pyplot as plt
import markdown

# ----------------------
# Convert Markdown to HTML
# ----------------------
def markdown_to_html(md_text):
    # Use Python Markdown library with table extension
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'attr_list'])
    return html

# ----------------------
# Generate a chart image (optional)
# ----------------------
def generate_price_chart(dates, prices, chart_file="price_chart.png"):
    plt.figure(figsize=(8,4))
    plt.plot(dates, prices, marker='o', color='#003366')
    plt.title("12-Month Price Chart")
    plt.xlabel("Month")
    plt.ylabel("Price (USD)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(chart_file, bbox_inches='tight')
    plt.close()
    return chart_file

# ----------------------
# Wrap HTML content in full page
# ----------------------
from datetime import date

def wrap_html(content_html, charts=None, company_name="Report", ticker="TICKER"):
    """
    Wrap HTML content in a full page with CSS and optional charts.
    Download button uses SVG only and triggers OS 'Save As...' popup.
    """
    charts = charts or []

    # Build chart HTML blocks
    chart_html = "".join([
        f'<div class="chart"><img src="cid:{c}" style="width:800px;height:auto"></div>'
        for c in charts
    ])

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{company_name} ({ticker}) — Full Report</title>

<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                 Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    line-height: 1.6;
    margin: 40px auto;
    max-width: 900px;
    color: #222;
}}

.header-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}}

.report-title {{
    font-size: 30px;
    font-weight: 700;
    margin: 0;
}}

.download-btn {{
    text-decoration: none;
    padding: 6px;
    border-radius: 6px;
    color: #333;
    transition: background 0.2s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
}}

.download-btn:hover {{
    background-color: #f0f0f0;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 25px 0;
    font-size: 14px;
}}

table, th, td {{
    border: 1px solid #aaa;
    padding: 8px;
    text-align: left;
}}

th {{
    background-color: #003366;
    color: white;
}}

tbody tr:nth-child(even) {{
    background-color: #f7f7f7;
}}

.chart {{
    margin: 25px 0;
    text-align: center;
}}
</style>
</head>

<body>

<div class="header-container">
    <div class="report-title">{company_name} ({ticker})</div>

    <!-- Download button: SVG only -->
    <div class="download-btn" onclick="downloadReport()">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
    </div>
</div>

<div class="content">
    {content_html}
</div>

{chart_html}

<script>
function downloadReport() {{
    const blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = '{company_name}_report.html';  // default filename
    a.click();
    URL.revokeObjectURL(url);
}}
</script>

</body>
</html>
"""
    return html_content

