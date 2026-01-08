#!/usr/bin/env python3
"""
Scrape model details from OpenAI's individual model pages.
Extracts: context window, max output tokens, knowledge cutoff, rate limits.
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import json
import time
from datetime import datetime

def get_headers():
    """Return browser-like headers for requests."""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }

def scrape_model_page(url, model_name):
    """Scrape a single model detail page."""
    print(f"\n🔍 Scraping {model_name}...")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        
        if response.status_code == 404:
            print(f"   ⚠ 404 - Page not found")
            return None
        
        if response.status_code == 403:
            print(f"   ⚠ 403 - Access forbidden (rate limited?)")
            return None
        
        if response.status_code != 200:
            print(f"   ⚠ Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        details = {
            'model_name': model_name,
            'context_window': None,
            'max_output_tokens': None,
            'knowledge_cutoff': None,
        }
        
        # Extract context window (e.g., "400,000 context window")
        context_text = soup.find(string=re.compile(r'[\d,]+\s+context window', re.IGNORECASE))
        if context_text:
            match = re.search(r'([\d,]+)\s+context window', context_text, re.IGNORECASE)
            if match:
                details['context_window'] = match.group(1).replace(',', '')
                print(f"   ✓ Context window: {details['context_window']}")
        
        # Extract max output tokens (e.g., "128,000 max output tokens")
        output_text = soup.find(string=re.compile(r'[\d,]+\s+max output tokens', re.IGNORECASE))
        if output_text:
            match = re.search(r'([\d,]+)\s+max output tokens', output_text, re.IGNORECASE)
            if match:
                details['max_output_tokens'] = match.group(1).replace(',', '')
                print(f"   ✓ Max output tokens: {details['max_output_tokens']}")
        
        # Extract knowledge cutoff (e.g., "Aug 31, 2025 knowledge cutoff")
        cutoff_text = soup.find(string=re.compile(r'\w+\s+\d+,\s+\d{4}\s+knowledge cutoff', re.IGNORECASE))
        if cutoff_text:
            match = re.search(r'(\w+\s+\d+,\s+\d{4})\s+knowledge cutoff', cutoff_text, re.IGNORECASE)
            if match:
                details['knowledge_cutoff'] = match.group(1)
                print(f"   ✓ Knowledge cutoff: {details['knowledge_cutoff']}")
        
        return details
        
    except requests.exceptions.Timeout:
        print(f"   ⚠ Timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   ⚠ Error: {e}")
        return None

def get_models_from_csv(csv_file):
    """Get unique model names from the CSV."""
    models = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row['Model'].strip().lower()
            # Normalize model names
            model = re.sub(r'-\d{4}-\d{2}-\d{2}.*', '', model)  # Remove dates
            model = re.sub(r'-\d{3,4}x\d{3,4}.*', '', model)  # Remove resolutions
            models.add(model)
    return sorted(models)

def scrape_models(model_links_file, csv_file, max_models=10, delay=3):
    """Scrape model details for models in the CSV."""
    
    # Load model links
    with open(model_links_file, 'r', encoding='utf-8') as f:
        model_links = json.load(f)
    
    # Get models from CSV
    csv_models = get_models_from_csv(csv_file)
    
    print(f"Found {len(csv_models)} unique models in CSV")
    print(f"Found {len(model_links)} model pages available")
    
    # Find matching models
    to_scrape = []
    for csv_model in csv_models:
        for link_model, info in model_links.items():
            if csv_model in link_model or link_model in csv_model:
                to_scrape.append((link_model, info['url']))
                break
    
    print(f"\nWill scrape {min(len(to_scrape), max_models)} models (limit: {max_models})")
    
    # Scrape models
    all_details = {}
    for i, (model_name, url) in enumerate(to_scrape[:max_models]):
        if i > 0:
            print(f"\n⏳ Waiting {delay} seconds...")
            time.sleep(delay)
        
        details = scrape_model_page(url, model_name)
        if details:
            all_details[model_name] = details
    
    # Save results
    output_file = 'scraped_model_details.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_details, f, indent=2)
    
    print(f"\n✓ Saved {len(all_details)} model details to {output_file}")
    return all_details

def update_csv_with_scraped_data(csv_file, scraped_data):
    """Update CSV with scraped model details."""
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    updated_count = 0
    for row in rows:
        csv_model = row['Model'].strip().lower()
        
        # Try to find matching scraped data
        for scraped_model, details in scraped_data.items():
            if scraped_model in csv_model or csv_model in scraped_model:
                # Update fields
                if details.get('context_window'):
                    row['Context Window (Tokens)'] = details['context_window']
                
                if details.get('max_output_tokens'):
                    row['Max Tokens'] = details['max_output_tokens']
                
                row['Last Updated'] = datetime.now().strftime('%Y-%m-%d')
                updated_count += 1
                break
    
    # Write updated CSV
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Updated {updated_count} rows in {csv_file}")

def main():
    model_links_file = 'model_links.json'
    csv_file = 'openai-pricing.csv'
    
    # Scrape up to 10 models with 3 second delays
    scraped_data = scrape_models(model_links_file, csv_file, max_models=10, delay=3)
    
    if scraped_data:
        print("\n" + "="*80)
        print("Updating CSV with scraped data...")
        update_csv_with_scraped_data(csv_file, scraped_data)

if __name__ == '__main__':
    main()
