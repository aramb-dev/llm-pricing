#!/usr/bin/env python3
"""
Parse model details from a cleaned model detail page HTML.
Extracts: context window, max output tokens, knowledge cutoff, rate limits.
"""

from bs4 import BeautifulSoup
import re
import csv
import json
from datetime import datetime

def parse_model_detail_html(html_file):
    """Extract model specifications from the model detail page HTML."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    details = {
        'model_name': None,
        'context_window': None,
        'max_output_tokens': None,
        'knowledge_cutoff': None,
        'rate_limits': []
    }
    
    # Extract model name from the page title or heading
    title_div = soup.find('div', string=lambda text: text and 'GPT' in text if isinstance(text, str) else False)
    if title_div:
        details['model_name'] = title_div.get_text(strip=True)
    
    # Extract context window (e.g., "400,000 context window")
    context_text = soup.find(string=re.compile(r'[\d,]+\s+context window', re.IGNORECASE))
    if context_text:
        match = re.search(r'([\d,]+)\s+context window', context_text, re.IGNORECASE)
        if match:
            details['context_window'] = match.group(1).replace(',', '')
    
    # Extract max output tokens (e.g., "128,000 max output tokens")
    output_text = soup.find(string=re.compile(r'[\d,]+\s+max output tokens', re.IGNORECASE))
    if output_text:
        match = re.search(r'([\d,]+)\s+max output tokens', output_text, re.IGNORECASE)
        if match:
            details['max_output_tokens'] = match.group(1).replace(',', '')
    
    # Extract knowledge cutoff (e.g., "Aug 31, 2025 knowledge cutoff")
    cutoff_text = soup.find(string=re.compile(r'\w+\s+\d+,\s+\d{4}\s+knowledge cutoff', re.IGNORECASE))
    if cutoff_text:
        match = re.search(r'(\w+\s+\d+,\s+\d{4})\s+knowledge cutoff', cutoff_text, re.IGNORECASE)
        if match:
            details['knowledge_cutoff'] = match.group(1)
    
    # Extract rate limits from table
    rate_table = soup.find('table')
    if rate_table:
        headers = []
        header_row = rate_table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        tbody = rate_table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if cells and len(cells) == len(headers):
                    rate_limit = dict(zip(headers, cells))
                    details['rate_limits'].append(rate_limit)
    
    return details

def normalize_model_name(name):
    """Normalize model name for matching with CSV."""
    if not name:
        return None
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    # Common variations
    name = name.replace('gpt-', 'gpt-')
    name = name.replace(' ', '-')
    
    return name

def update_csv_with_details(csv_file, details, dry_run=True):
    """Update the CSV file with extracted model details."""
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    model_name = normalize_model_name(details.get('model_name'))
    
    if not model_name:
        print("⚠ Could not determine model name from HTML")
        return
    
    print(f"\n📄 Parsed model: {details.get('model_name')}")
    print(f"   Normalized: {model_name}")
    print(f"   Context window: {details.get('context_window')}")
    print(f"   Max output tokens: {details.get('max_output_tokens')}")
    print(f"   Knowledge cutoff: {details.get('knowledge_cutoff')}")
    print(f"   Rate limits: {len(details.get('rate_limits', []))} tiers")
    
    # Update matching rows
    updated_count = 0
    for row in rows:
        csv_model = normalize_model_name(row['Model'])
        
        if model_name in csv_model or csv_model in model_name:
            # Update context window
            if details.get('context_window'):
                row['Context Window (Tokens)'] = details['context_window']
            
            # Update max tokens
            if details.get('max_output_tokens'):
                row['Max Tokens'] = details['max_output_tokens']
            
            # Format rate limits (use Tier 1 or average)
            if details.get('rate_limits'):
                # Try to find Tier 1 or use first tier
                tier_data = details['rate_limits'][0] if details['rate_limits'] else {}
                
                # Extract RPM if available
                rpm = tier_data.get('RPM', tier_data.get('Requests per minute', ''))
                if rpm:
                    row['Rate Limit (Requests/sec)'] = f"{rpm} RPM"
            
            # Update last updated date
            row['Last Updated'] = datetime.now().strftime('%Y-%m-%d')
            
            updated_count += 1
            
            if dry_run:
                print(f"   ✓ Would update: {row['Model']} ({row['Source Type']})")
    
    if dry_run:
        print(f"\n🔍 DRY RUN: Would update {updated_count} rows")
        print("   Set dry_run=False to apply changes")
    else:
        # Write updated CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\n✓ Updated {updated_count} rows in {csv_file}")

def main():
    html_file = 'models_page_clean.html'
    csv_file = 'openai-pricing.csv'
    
    print(f"Parsing {html_file}...")
    details = parse_model_detail_html(html_file)
    
    # Save to JSON for reference
    output_file = 'model_details_parsed.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2)
    
    print(f"✓ Saved parsed details to {output_file}")
    
    # Update CSV
    update_csv_with_details(csv_file, details, dry_run=False)
    
    print("\n" + "="*80)
    print("✓ Changes applied to CSV")

if __name__ == '__main__':
    main()
