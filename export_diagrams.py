"""
Export Mermaid Diagrams to Images using Playwright

This script reads the DIAGRAMS.md file and exports each Mermaid diagram as PNG images
using the Mermaid CLI or web-based rendering.
"""

import os
import re
import base64
import requests
from pathlib import Path


def extract_mermaid_diagrams(md_file):
    """Extract all Mermaid diagrams from markdown file"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all mermaid code blocks
    pattern = r'```mermaid\n(.*?)```'
    diagrams = re.findall(pattern, content, re.DOTALL)
    
    # Extract titles from headers
    titles = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## ') and 'mermaid' in '\n'.join(lines[i:i+10]).lower():
            title = line.replace('## ', '').strip()
            # Clean title for filename
            title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            titles.append(title)
    
    return list(zip(titles[:len(diagrams)], diagrams))


def export_via_mermaid_ink(diagram_code, output_file):
    """Export diagram using mermaid.ink service"""
    try:
        # Encode diagram for URL
        encoded = base64.b64encode(diagram_code.encode('utf-8')).decode('utf-8')
        
        # Use mermaid.ink API
        url = f"https://mermaid.ink/img/{encoded}"
        
        print(f"  Fetching from mermaid.ink...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Saved: {output_file}")
            return True
        else:
            print(f"  ✗ Error: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def export_diagrams():
    """Main export function"""
    md_file = 'DIAGRAMS.md'
    output_dir = Path('diagrams')
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    print("Extracting Mermaid diagrams from DIAGRAMS.md...")
    diagrams = extract_mermaid_diagrams(md_file)
    
    if not diagrams:
        print("No diagrams found!")
        return
    
    print(f"\nFound {len(diagrams)} diagrams. Exporting to PNG...\n")
    
    success_count = 0
    for i, (title, code) in enumerate(diagrams, 1):
        filename = f"{i:02d}_{title}.png"
        output_file = output_dir / filename
        
        print(f"[{i}/{len(diagrams)}] Exporting: {title}")
        
        if export_via_mermaid_ink(code, output_file):
            success_count += 1
        
        print()
    
    print(f"✅ Export complete: {success_count}/{len(diagrams)} diagrams exported successfully")
    print(f"📁 Diagrams saved in: {output_dir.absolute()}")
    
    # Create index file
    create_index(diagrams, output_dir)


def create_index(diagrams, output_dir):
    """Create an index HTML file to view all diagrams"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>ABS Platform - Architecture Diagrams</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 10px;
        }
        .diagram {
            background: white;
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .diagram h2 {
            color: #1f77b4;
            margin-top: 0;
        }
        .diagram img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <h1>🏗️ ABS Data Analytics Platform - Architecture Diagrams</h1>
    <p style="text-align: center; color: #666;">
        Generated on """ + str(Path.cwd()) + """
    </p>
"""
    
    for i, (title, _) in enumerate(diagrams, 1):
        filename = f"{i:02d}_{title}.png"
        display_title = title.replace('_', ' ').title()
        
        html_content += f"""
    <div class="diagram">
        <h2>{i}. {display_title}</h2>
        <img src="{filename}" alt="{display_title}">
    </div>
"""
    
    html_content += """
    <div class="footer">
        <p><strong>ABS Data Analytics Platform</strong></p>
        <p>Repository: ABSHackGMF | Branch: David</p>
    </div>
</body>
</html>
"""
    
    index_file = output_dir / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📄 Created index.html for viewing all diagrams")
    print(f"   Open: {index_file.absolute()}")


if __name__ == "__main__":
    print("="*70)
    print("  MERMAID DIAGRAM EXPORTER")
    print("="*70)
    print()
    
    try:
        export_diagrams()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
