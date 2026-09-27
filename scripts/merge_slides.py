import glob
import os
import re

def build_combined():
    slides = sorted(glob.glob("archetypes/[0-9][0-9]-Slide-*.html"))
    
    combined_styles = []
    combined_body = []
    scripts_set = set()
    scripts_order = []
    
    for slide_path in slides:
        with open(slide_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract styles
        style_matches = re.finditer(r'<style[^>]*>(.*?)</style>', content, re.IGNORECASE | re.DOTALL)
        for match in style_matches:
            combined_styles.append(f"/* --- {os.path.basename(slide_path)} --- */\n{match.group(1)}")
                
        # Extract scripts
        script_matches = re.finditer(r'<script[^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL)
        for match in script_matches:
            script_tag = match.group(0)
            if script_tag not in scripts_set:
                scripts_set.add(script_tag)
                scripts_order.append(script_tag)
                
        # Extract body content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.IGNORECASE | re.DOTALL)
        if body_match:
            combined_body.append(f"<!-- --- {os.path.basename(slide_path)} --- -->\n{body_match.group(1)}")

    # Base HTML template
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ACME - Full Penetration Testing Report</title>
    {chr(10).join(scripts_order)}
    <style>
{chr(10).join(combined_styles)}

        /* --- GLOBAL SCROLL AND LAYOUT FIX FOR COMBINED VIEW --- */
        html, body {{
            height: auto !important;
            overflow: auto !important;
            overflow-x: hidden !important;
        }}
        @media screen {{
            body {{
                padding: 2rem 0 !important;
                background-color: #64748B !important;
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                gap: 2rem !important;
            }}
            .slide {{
                margin: 0 !important; /* Managed by body gap */
                box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
            }}
        }}
    </style>
</head>
<body>
{chr(10).join(combined_body)}
</body>
</html>
"""

    os.makedirs('reports', exist_ok=True)
    with open('reports/combined_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    with open('reports/merged_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Generated reports/combined_report.html and reports/merged_report.html from {len(slides)} slides.")

if __name__ == "__main__":
    build_combined()
