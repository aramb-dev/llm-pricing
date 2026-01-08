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
            
            # Get rows - the table structure has Feature in first column, then model names as headers
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                
                # If first row contains model names (headers), parse accordingly
                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                    
                    if not cells:
                        continue
                    
                    feature = cells[0]  # First cell is the feature name
                    
                    # Skip non-spec rows
                    if feature.lower() not in ['context window', 'max output', 'knowledge cutoff', 'training data cutoff']:
                        continue
                    
                    print(f"  Processing: {feature}")
                    
                    # Parse the rest of the cells as model data
                    for i, cell in enumerate(cells[1:], 1):
                        # Try to get model name from header
                        model_name = headers[i] if i < len(headers) else f"Model {i}"
                        
                        if not cell or cell == '-' or cell == '—':
                            continue
                        
                        if model_name not in model_data:
                            model_data[model_name] = {
                                'model': model_name,
                                'context_window': None,
                                'max_output_tokens': None,
                                'knowledge_cutoff': None,
                                'training_data_cutoff': None,
                                'features': []
                            }
                        
                        # Parse based on feature type
                        if feature.lower() == 'context window':
                            tokens_match = re.search(r'([\d,]+)K?\s+tokens?', cell, re.IGNORECASE)
                            if tokens_match:
                                tokens = tokens_match.group(1).replace(',', '')
                                if 'K' in cell.upper():
                                    tokens = str(int(tokens) * 1000)
                                model_data[model_name]['context_window'] = tokens
                        
                        elif feature.lower() == 'max output':
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
