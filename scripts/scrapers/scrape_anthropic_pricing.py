#!/usr/bin/env python3
"""
Scrape Anthropic (Claude) pricing from platform.claude.com/docs/en/about-claude/pricing
and save to CSV format matching OpenAI structure.
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import json
from datetime import datetime
import time

def get_headers():
    """Return headers for requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def parse_price(price_str):
    """Parse price string like '$5 / MTok' to float"""
    if not price_str:
        return None
    match = re.search(r'\$?([\d.]+)', price_str.replace(',', ''))
    return float(match.group(1)) if match else None

def scrape_pricing_page():
    """Scrape the Anthropic pricing page"""
    url = "https://platform.claude.com/docs/en/about-claude/pricing"
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=get_headers(), timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the pricing table
        pricing_data = []
        
        # Look for the main pricing table
        tables = soup.find_all('table')
        
        if not tables:
            print("⚠ No tables found on the page")
            return []
        
        print(f"Found {len(tables)} table(s)")
        
        # Parse the first table (main pricing table)
        main_table = tables[0]
        headers = []
        header_row = main_table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            print(f"Table headers: {headers}")
        
        tbody = main_table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 5:  # Model, Base Input, Cache Writes (5m), Cache Writes (1h), Cache Hits, Output
                    model_name = cells[0]
                    base_input = parse_price(cells[1])
                    cache_write_5m = parse_price(cells[2])
                    cache_write_1h = parse_price(cells[3])
                    cache_hits = parse_price(cells[4])
                    output_tokens = parse_price(cells[5]) if len(cells) > 5 else None
                    
                    pricing_data.append({
                        'model': model_name,
                        'base_input': base_input,
                        'cache_write_5m': cache_write_5m,
                        'cache_write_1h': cache_write_1h,
                        'cache_hits': cache_hits,
                        'output': output_tokens
                    })
                    
                    print(f"  ✓ {model_name}: ${base_input}/${output_tokens}")
        
        return pricing_data
        
    except Exception as e:
        print(f"✗ Error scraping pricing: {e}")
        return []

def scrape_model_details():
    """Scrape model details (context window, max output tokens, etc.)"""
    # Try the models overview page
    url = "https://platform.claude.com/docs/en/about-claude/models"
    
    print(f"\nFetching model details from {url}...")
    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for model specifications table
        model_specs = {}
        tables = soup.find_all('table')
        
        for table in tables:
            tbody = table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                    if cells and len(cells) >= 2:
                        # First cell is usually the model name
                        model = cells[0]
                        
                        # Try to find context window info
                        for cell in cells:
                            # Look for token counts
                            context_match = re.search(r'([\d,]+)K?\s+tokens?', cell, re.IGNORECASE)
                            if context_match:
                                tokens = context_match.group(1).replace(',', '')
                                if 'K' in cell:
                                    tokens = str(int(tokens) * 1000)
                                
                                if model not in model_specs:
                                    model_specs[model] = {}
                                model_specs[model]['context_window'] = tokens
        
        return model_specs
        
    except Exception as e:
        print(f"⚠ Error scraping model details: {e}")
        return {}

def generate_csv(pricing_data, model_specs, output_file):
    """Generate CSV file in OpenAI format"""
    
    csv_rows = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for item in pricing_data:
        model = item['model']
        
        # Get model specs if available
        context_window = None
        max_output = None
        
        # Try to match model specs
        for spec_model, specs in model_specs.items():
            if model.lower() in spec_model.lower() or spec_model.lower() in model.lower():
                context_window = specs.get('context_window')
                max_output = specs.get('max_output')
                break
        
        # Standard pricing (Base Input Tokens)
        base_row = {
            'Provider': 'Anthropic',
            'Model': model,
            'Source Type': 'Standard',
            'Context Window (Tokens)': context_window or '',
            'Input Cost per 1M Tokens (USD)': item['base_input'] or '',
            'Output Cost per 1M Tokens (USD)': item['output'] or '',
            'Min Tokens': '',
            'Max Tokens': max_output or '',
            'Rate Limit (Requests/sec)': '',
            'Billing Notes': '',
            'Documentation URL': 'https://platform.claude.com/docs/en/about-claude/pricing',
            'Last Updated': today
        }
        csv_rows.append(base_row)
        
        # Cache Write 5m pricing
        if item['cache_write_5m']:
            cache_5m_row = base_row.copy()
            cache_5m_row['Source Type'] = 'Cache Write (5min)'
            cache_5m_row['Input Cost per 1M Tokens (USD)'] = item['cache_write_5m']
            cache_5m_row['Billing Notes'] = 'Prompt caching - 5 minute duration'
            csv_rows.append(cache_5m_row)
        
        # Cache Write 1h pricing
        if item['cache_write_1h']:
            cache_1h_row = base_row.copy()
            cache_1h_row['Source Type'] = 'Cache Write (1hour)'
            cache_1h_row['Input Cost per 1M Tokens (USD)'] = item['cache_write_1h']
            cache_1h_row['Billing Notes'] = 'Prompt caching - 1 hour duration'
            csv_rows.append(cache_1h_row)
        
        # Cache Hits pricing
        if item['cache_hits']:
            cache_hit_row = base_row.copy()
            cache_hit_row['Source Type'] = 'Cache Hit'
            cache_hit_row['Input Cost per 1M Tokens (USD)'] = item['cache_hits']
            cache_hit_row['Billing Notes'] = 'Prompt caching - cache read tokens'
            csv_rows.append(cache_hit_row)
    
    # Write CSV
    if csv_rows:
        fieldnames = [
            'Provider', 'Model', 'Source Type', 'Context Window (Tokens)',
            'Input Cost per 1M Tokens (USD)', 'Output Cost per 1M Tokens (USD)',
            'Min Tokens', 'Max Tokens', 'Rate Limit (Requests/sec)',
            'Billing Notes', 'Documentation URL', 'Last Updated'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        print(f"\n✓ Saved {len(csv_rows)} rows to {output_file}")
    else:
        print("\n⚠ No data to write")

def main():
    print("=" * 60)
    print("Anthropic (Claude) Pricing Scraper")
    print("=" * 60)
    
    # Scrape pricing data
    pricing_data = scrape_pricing_page()
    
    if not pricing_data:
        print("\n✗ Failed to scrape pricing data")
        return
    
    # Scrape model details
    model_specs = scrape_model_details()
    
    # Save raw data
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_file = os.path.join(base_dir, 'data', 'anthropic', 'scraped_pricing_raw.json')
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump({
            'pricing': pricing_data,
            'model_specs': model_specs,
            'scraped_at': datetime.now().isoformat()
        }, f, indent=2)
    print(f"\n✓ Saved raw data to {raw_file}")
    
    # Generate CSV
    output_file = os.path.join(base_dir, 'data', 'anthropic', 'anthropic-pricing.csv')
    generate_csv(pricing_data, model_specs, output_file)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
