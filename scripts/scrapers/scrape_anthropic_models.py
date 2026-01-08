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
            
            # Get headers to identify model names
            thead = table.find('thead')
            tbody = table.find('tbody')
            
            if not thead or not tbody:
                continue
            
            # Extract headers (model names are in the header row)
            header_cells = thead.find_all('th')
            headers = [th.get_text(strip=True) for th in header_cells]
            print(f"  Headers: {headers}")
            
            # Extract rows with features
            rows = tbody.find_all('tr')
            
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                
                if not cells or len(cells) < 2:
                    continue
                
                feature = cells[0]  # First cell is feature name
                
                # Look for specific features we care about
                is_relevant = any(keyword in feature.lower() for keyword in [
                    'context window', 'max output', 'knowledge cutoff', 
                    'training data cutoff', 'api id'
                ])
                
                if not is_relevant:
                    continue
                
                print(f"  Processing: {feature}")
                
                # Parse the model columns (skip first column which is feature name)
                for i, cell in enumerate(cells[1:], 1):
                    # Get model name from header
                    if i < len(headers):
                        model_name = headers[i]
                    else:
                        continue
                    
                    if not cell or cell in ['-', '—', 'N/A']:
                        continue
                    
                    if model_name not in model_data:
                        model_data[model_name] = {
                            'model': model_name,
                            'context_window': None,
                            'max_output_tokens': None,
                            'knowledge_cutoff': None,
                            'training_data_cutoff': None,
                        }
                    
                    # Parse based on feature type
                    if 'context window' in feature.lower():
                        tokens_match = re.search(r'([\d,]+)K?\s+tokens?', cell, re.IGNORECASE)
                        if tokens_match:
                            tokens = tokens_match.group(1).replace(',', '')
                            if 'K' in cell.upper():
                                tokens = str(int(tokens) * 1000)
                            model_data[model_name]['context_window'] = tokens
                    
                    elif 'max output' in feature.lower():
                        tokens_match = re.search(r'([\d,]+)K?\s+tokens?', cell, re.IGNORECASE)
                        if tokens_match:
                            tokens = tokens_match.group(1).replace(',', '')
                            if 'K' in cell.upper():
                                tokens = str(int(tokens) * 1000)
                            model_data[model_name]['max_output_tokens'] = tokens
                    
                    elif 'knowledge cutoff' in feature.lower():
                        date_match = re.search(r'([\w]+\s+\d{1,2},?\s+\d{4})', cell)
                        if date_match:
                            model_data[model_name]['knowledge_cutoff'] = date_match.group(1)
                    
                    elif 'training data cutoff' in feature.lower():
                        date_match = re.search(r'([\w]+\s+\d{1,2},?\s+\d{4})', cell)
                        if date_match:
                            model_data[model_name]['training_data_cutoff'] = date_match.group(1)
        
        return model_data
        
    except Exception as e:
        print(f"✗ Error scraping models: {e}")
        import traceback
        traceback.print_exc()
        return {}

def main():
    print("=" * 60)
    print("Anthropic Model Details Scraper")
    print("=" * 60)
    
    # Scrape model comparison page
    model_data = scrape_model_comparison()
    
    if model_data:
        print(f"\n✓ Found {len(model_data)} models")
        
        # Save to JSON
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_file = os.path.join(base_dir, 'data', 'anthropic', 'scraped_model_details.json')
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
