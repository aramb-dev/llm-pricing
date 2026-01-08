#!/usr/bin/env python3
"""
Extract model links from the models overview page HTML.
This gets the list of all models that we can then scrape individually.
"""

from bs4 import BeautifulSoup
import re
import json

def extract_model_links(html_file):
    """Extract all unique model page links from the models overview HTML."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all links that point to /docs/models/[model-name]
    model_links = {}
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        
        # Match pattern: /docs/models/[model-name]
        if href.startswith('/docs/models/') and href != '/docs/models':
            # Extract model name from URL
            model_name = href.replace('/docs/models/', '')
            
            # Get model display name from link text or child elements
            display_name = link.get_text(strip=True)
            if not display_name or display_name in ['New', '']:
                # Try to find image alt text
                img = link.find('img')
                if img and img.get('alt'):
                    display_name = img.get('alt')
            
            if model_name and model_name not in model_links:
                model_links[model_name] = {
                    'url': f'https://platform.openai.com{href}',
                    'display_name': display_name or model_name
                }
    
    return model_links

def main():
    html_file = 'models_page_clean.html'
    
    print(f"Parsing {html_file}...")
    model_links = extract_model_links(html_file)
    
    print(f"\nFound {len(model_links)} unique models:")
    print("-" * 80)
    
    for model_name, info in sorted(model_links.items()):
        print(f"{model_name:30} → {info['url']}")
    
    # Save to JSON file for the scraper to use
    output_file = 'model_links.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(model_links, f, indent=2)
    
    print(f"\n✓ Saved {len(model_links)} model links to {output_file}")
    print("\nNext steps:")
    print("1. Use scrape_openai_details.py to scrape individual model pages")
    print("2. The scraper will need to be updated to use model_links.json")

if __name__ == '__main__':
    main()
