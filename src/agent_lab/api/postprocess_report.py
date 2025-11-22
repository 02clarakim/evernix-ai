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
def wrap_html(content, charts=None, out_file=None):
    charts = charts or []
    chart_html = "".join([
        f'<div class="chart"><img src="{c}" style="width:800px;height:auto"></div>'
        for c in charts
    ])

    today_str = date.today().isoformat()

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Full Report - {today_str}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 20px;
    max-width: 1000px;
}}
h1, h2, h3 {{ color: #003366; }}
ul, ol {{ margin-left: 20px; }}
table {{
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
    width: 100%;
}}
table, th, td {{
    border: 1px solid #999;
    padding: 8px;
    text-align: left;
}}
th {{
    background-color: #003366;
    color: #fff;
}}
tbody tr:nth-child(even) {{
    background-color: #f3f3f3;
}}
.chart {{
    margin: 20px 0;
    text-align: center;
}}

#download-btn {{
  display:inline-block;
  padding:6px 10px;
  background:#0b5fff;
  color:white;
  border-radius:6px;
  text-decoration:none;
  font-size:13px;
  margin-bottom:20px;
}}
</style>
</head>
<body>

<a id="download-btn" href="#" onclick="downloadHtml()">Download HTML</a>

{content}
{chart_html}

<script>
function downloadHtml() {{
    const html = document.documentElement.outerHTML;
    const blob = new Blob([html], {{ type: "text/html" }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "full_report_{today_str}.html";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
}}
</script>

</body>
</html>
"""

    # --- NEW LOGIC ---
    # If out_file is None, return HTML string directly (do NOT write file)
    if out_file is None:
        return html_content

    # Otherwise, save the file AND return the filename
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return out_file
