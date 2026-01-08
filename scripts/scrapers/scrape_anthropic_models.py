#!/usr/bin/env python3
"""
Scrape detailed model specifications from Anthropic documentation.
This includes context windows, max output tokens, rate limits, and knowledge cutoffs.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def get_headers():
    """Return headers for requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def scrape_model_comparison():
    """Scrape the model comparison page for specifications"""
    url = "https://platform.claude.com/docs/en/about-claude/models"
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=get_headers(), timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        model_data = {}
        
        # Look for tables with model information
        tables = soup.find_all('table')
        print(f"Found {len(tables)} table(s)")
        
        for idx, table in enumerate(tables):
            print(f"\nProcessing table {idx + 1}...")
            
            # Get headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
                print(f"  Headers: {headers}")
            
            # Get rows
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                    
                    if not cells:
                        continue
                    
                    # First cell is usually the model name
                    model_name = cells[0]
                    
                    if model_name not in model_data:
                        model_data[model_name] = {
                            'model': model_name,
                            'context_window': None,
                            'max_output_tokens': None,
                            'knowledge_cutoff': None,
                            'rate_limits': {},
                            'features': []
                        }
                    
                    # Parse other cells based on headers or content
                    for i, cell in enumerate(cells[1:], 1):
                        header = headers[i] if i < len(headers) else f"Column {i}"
                        
                        # Look for context window
                        if re.search(r'context|input', header, re.IGNORECASE):
                            tokens_match = re.search(r'([\d,]+)K?\s+tokens?', cell, re.IGNORECASE)
                            if tokens_match:
                                tokens = tokens_match.group(1).replace(',', '')
                                if 'K' in cell.upper():
                                    tokens = str(int(tokens) * 1000)
                                model_data[model_name]['context_window'] = tokens
                        
                        # Look for max output tokens
                        if re.search(r'output|max', header, re.IGNORECASE):
                            tokens_match = re.search(r'([\d,]+)K?\s+tokens?', cell, re.IGNORECASE)
                            if tokens_match:
                                tokens = tokens_match.group(1).replace(',', '')
                                if 'K' in cell.upper():
                                    tokens = str(int(tokens) * 1000)
                                model_data[model_name]['max_output_tokens'] = tokens
                        
                        # Look for knowledge cutoff
                        if re.search(r'knowledge|cutoff|training', header, re.IGNORECASE):
                            date_match = re.search(r'([\w]+\s+\d{4})', cell)
                            if date_match:
                                model_data[model_name]['knowledge_cutoff'] = date_match.group(1)
                        
                        # Collect other features
                        if cell and cell not in [model_name, '-', '—', '']:
                            if header not in ['Model', 'Pricing']:
                                model_data[model_name]['features'].append(f"{header}: {cell}")
                    
                    print(f"  ✓ {model_name}")
        
        # Also scrape text content for additional details
        text_content = soup.get_text()
        
        # Look for rate limits in text
        rpm_matches = re.findall(r'([\d,]+)\s+(?:requests?|RPM)\s+per\s+minute', text_content, re.IGNORECASE)
        tpm_matches = re.findall(r'([\d,]+)\s+(?:tokens?|TPM)\s+per\s+minute', text_content, re.IGNORECASE)
        
        return model_data
        
    except Exception as e:
        print(f"✗ Error scraping models: {e}")
        return {}

def scrape_individual_model_pages(model_data):
    """Try to scrape individual model pages for more details"""
    base_url = "https://platform.claude.com/docs/en/about-claude/models/"
    
    # Common model page slugs
    model_slugs = {
        'opus': ['claude-opus-4.5', 'claude-opus-4.1', 'claude-opus-4', 'claude-opus-3'],
        'sonnet': ['claude-sonnet-4.5', 'claude-sonnet-4', 'claude-sonnet-3.7'],
        'haiku': ['claude-haiku-4.5', 'claude-haiku-3.5', 'claude-haiku-3']
    }
    
    for category, slugs in model_slugs.items():
        for slug in slugs:
            url = f"{base_url}{slug}"
            print(f"\nTrying {url}...")
            
            try:
                response = requests.get(url, headers=get_headers(), timeout=30, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    # Extract context window
                    context_match = re.search(r'([\d,]+)K?\s+(?:token\s+)?context\s+window', text, re.IGNORECASE)
                    if context_match:
                        tokens = context_match.group(1).replace(',', '')
                        if 'K' in text[context_match.start():context_match.end()].upper():
                            tokens = str(int(tokens) * 1000)
                        
                        # Update model data
                        for model_name in model_data:
                            if slug.replace('-', ' ').lower() in model_name.lower():
                                model_data[model_name]['context_window'] = tokens
                                print(f"  ✓ Updated {model_name} context window: {tokens}")
                    
                    # Extract max output
                    output_match = re.search(r'([\d,]+)K?\s+(?:max\s+)?output\s+tokens?', text, re.IGNORECASE)
                    if output_match:
                        tokens = output_match.group(1).replace(',', '')
                        if 'K' in text[output_match.start():output_match.end()].upper():
                            tokens = str(int(tokens) * 1000)
                        
                        for model_name in model_data:
                            if slug.replace('-', ' ').lower() in model_name.lower():
                                model_data[model_name]['max_output_tokens'] = tokens
                                print(f"  ✓ Updated {model_name} max output: {tokens}")
                
            except Exception as e:
                print(f"  ⚠ {e}")
                continue
    
    return model_data

def main():
    print("=" * 60)
    print("Anthropic Model Details Scraper")
    print("=" * 60)
    
    # Scrape model comparison page
    model_data = scrape_model_comparison()
    
    if model_data:
        print(f"\n✓ Found {len(model_data)} models")
        
        # Try to get more details from individual pages
        model_data = scrape_individual_model_pages(model_data)
        
        # Save to JSON
        output_file = '../../data/anthropic/scraped_model_details.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'models': model_data,
                'scraped_at': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n✓ Saved to {output_file}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Summary:")
        print("=" * 60)
        for model_name, data in model_data.items():
            print(f"\n{model_name}:")
            print(f"  Context Window: {data['context_window'] or 'N/A'}")
            print(f"  Max Output: {data['max_output_tokens'] or 'N/A'}")
            print(f"  Knowledge Cutoff: {data['knowledge_cutoff'] or 'N/A'}")
    else:
        print("\n✗ No model data scraped")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
