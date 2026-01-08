#!/usr/bin/env python3
"""Remove all class attributes from HTML to reduce size"""

from bs4 import BeautifulSoup
import sys

def clean_html(input_file, output_file):
    """Remove scripts, styles, and class/style attributes from HTML"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove all script tags
    for script in soup.find_all('script'):
        script.decompose()
    
    # Remove all style tags
    for style in soup.find_all('style'):
        style.decompose()
    
    # Remove all class and style attributes
    for tag in soup.find_all(True):
        if tag.has_attr('class'):
            del tag['class']
        if tag.has_attr('style'):
            del tag['style']
    
    # Write cleaned HTML
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Cleaned HTML written to {output_file}")
    print(f"Original size: {len(html)} bytes")
    print(f"Cleaned size: {len(str(soup))} bytes")
    print(f"Reduction: {len(html) - len(str(soup))} bytes ({(1 - len(str(soup))/len(html))*100:.1f}%)")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "models_page_raw.html"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "models_page_clean.html"
    clean_html(input_file, output_file)
