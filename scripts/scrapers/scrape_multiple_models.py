#!/usr/bin/env python3
"""
Scrape multiple model detail pages and update the CSV.
Uses the model_links.json file to know which models to scrape.
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from datetime import datetime
import re

def get_headers():
    """Return headers for requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def scrape_model_page(url):
    """Scrape a single model detail page"""
    try:
        print(f"  Fetching {url}...")
        response = requests.get(url, headers=get_headers(), timeout=30)
        
        if response.status_code != 200:
            print(f"  ⚠ HTTP {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {
            'context_window': None,
            'max_output_tokens': None,
            'knowledge_cutoff': None,
            'rate_limits': [],
        }
        
        # Extract context window
        text = soup.get_text()
        context_match = re.search(r'([\d,]+)\s+context window', text, re.IGNORECASE)
        if context_match:
            details['context_window'] = context_match.group(1).replace(',', '')
        
        # Extract max output tokens
        output_match = re.search(r'([\d,]+)\s+max output tokens', text, re.IGNORECASE)
        if output_match:
            details['max_output_tokens'] = output_match.group(1).replace(',', '')
        
        # Extract knowledge cutoff
        cutoff_match = re.search(r'(\w+\s+\d+,\s+\d{4})\s+knowledge cutoff', text, re.IGNORECASE)
        if cutoff_match:
            details['knowledge_cutoff'] = cutoff_match.group(1)
        
        # Extract rate limits from table
        rate_table = soup.find('table')
        if rate_table:
            tbody = rate_table.find('tbody')
            if tbody:
                for row in tbody.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                    if len(cells) >= 3:  # Tier, RPM, TPM columns
                        details['rate_limits'].append({
                            'tier': cells[0],
                            'rpm': cells[1] if len(cells) > 1 else None,
                            'tpm': cells[2] if len(cells) > 2 else None,
                        })
        
        return details
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def get_models_from_csv(csv_file):
    """Get unique model names from CSV that need details"""
    models = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row['Model'].strip().lower()
            # Only include actual models, not tools/services
            if model and not any(skip in model for skip in ['storage', 'tool call', 'search', 'interpreter']):
                models.add(model)
    return sorted(models)

def main():
    csv_file = 'openai-pricing.csv'
    links_file = 'model_links.json'
    
    # Load model links
    with open(links_file, 'r') as f:
        model_links = json.load(f)
    
    # Get models that need details from CSV
    csv_models = get_models_from_csv(csv_file)
    
    # Priority models to scrape first (most commonly used)
    priority_models = [
        'gpt-5.1', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro', 
        'gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-4o-mini',
        'o1', 'o1-mini', 'o3', 'o3-mini', 'o4-mini'
    ]
    
    # Filter to only scrape models we have in CSV
    models_to_scrape = []
    for model in priority_models:
        if model in model_links and model in csv_models:
            models_to_scrape.append(model)
    
    print(f"Found {len(models_to_scrape)} priority models to scrape")
    print(f"Models: {', '.join(models_to_scrape)}\n")
    
    # Scrape with delay
    scraped_data = {}
    for i, model_name in enumerate(models_to_scrape, 1):
        url = model_links[model_name]['url']
        print(f"[{i}/{len(models_to_scrape)}] {model_name}")
        
        details = scrape_model_page(url)
        
        if details:
            scraped_data[model_name] = details
            rpm_info = f", RPM tiers: {len(details.get('rate_limits', []))}" if details.get('rate_limits') else ""
            print(f"  ✓ Context: {details['context_window']}, Max output: {details['max_output_tokens']}{rpm_info}")
        
        # Delay between requests to avoid rate limiting
        if i < len(models_to_scrape):
            delay = 3
            print(f"  Waiting {delay}s...\n")
            time.sleep(delay)
    
    # Save scraped data
    output_file = 'scraped_model_details.json'
    with open(output_file, 'w') as f:
        json.dump(scraped_data, f, indent=2)
    
    print(f"\n✓ Scraped {len(scraped_data)} models")
    print(f"✓ Saved to {output_file}")
    
    # Update CSV
    update_csv(csv_file, scraped_data)

def update_csv(csv_file, scraped_data):
    """Update CSV with scraped data"""
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    updated_count = 0
    for row in rows:
        model = row['Model'].strip().lower()
        
        if model in scraped_data:
            details = scraped_data[model]
            
            if details.get('context_window'):
                row['Context Window (Tokens)'] = details['context_window']
            
            if details.get('max_output_tokens'):
                row['Max Tokens'] = details['max_output_tokens']
            # Add rate limit from Tier 1 if available
            if details.get('rate_limits'):
                tier1 = details['rate_limits'][0] if details['rate_limits'] else None
                if tier1 and tier1.get('rpm'):
                    row['Rate Limit (Requests/sec)'] = f"{tier1['rpm']} RPM"
            
            
            row['Last Updated'] = datetime.now().strftime('%Y-%m-%d')
            updated_count += 1
    
    # Write back
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Updated {updated_count} rows in CSV")

if __name__ == '__main__':
    main()
