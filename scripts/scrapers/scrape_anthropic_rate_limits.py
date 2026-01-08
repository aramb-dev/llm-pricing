#!/usr/bin/env python3
"""
Scrape Anthropic rate limits from the rate-limits documentation.
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

def parse_rate_limit_table(table):
    """Parse a rate limit table and extract model limits"""
    limits = {}
    
    tbody = table.find('tbody')
    if not tbody:
        return limits
    
    for row in tbody.find_all('tr'):
        cells = [td.get_text(strip=True) for td in row.find_all('td')]
        
        if len(cells) < 4:
            continue
        
        model = cells[0]
        rpm = cells[1]
        itpm = cells[2]
        otpm = cells[3]
        
        limits[model] = {
            'rpm': rpm,
            'itpm': itpm,
            'otpm': otpm
        }
    
    return limits

def scrape_rate_limits_page():
    """Scrape the rate limits page"""
    url = "https://platform.claude.com/docs/en/api/rate-limits"
    
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=get_headers(), timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} table(s)")
        
        # Rate limits are organized by tier
        rate_limits = {
            'tier1': {},
            'tier2': {},
            'tier3': {},
            'tier4': {},
        }
        
        # Parse all tables and identify rate limit tables by content
        tier_tables = []
        
        for idx, table in enumerate(tables):
            # Check if this is a rate limit table by looking at headers
            thead = table.find('thead')
            if thead:
                headers = [th.get_text(strip=True) for th in thead.find_all('th')]
                print(f"\nTable {idx + 1} headers: {headers}")
                
                # Look for rate limit indicators
                has_rpm = any('RPM' in h.upper() or 'requests per minute' in h.lower() for h in headers)
                has_tokens = any('tokens' in h.lower() for h in headers)
                has_model = any('model' in h.lower() for h in headers)
                
                if (has_rpm or has_tokens) and has_model:
                    print(f"  ✓ Found rate limit table")
                    tier_tables.append(table)
                    limits = parse_rate_limit_table(table)
                    for model, data in limits.items():
                        print(f"    {model}: RPM={data['rpm']}, ITPM={data['itpm']}, OTPM={data['otpm']}")
        
        print(f"\nTotal rate limit tables found: {len(tier_tables)}")
        
        # Assign tables to tiers (assuming order: Tier 1, 2, 3, 4)
        tier_names = ['tier1', 'tier2', 'tier3', 'tier4']
        for i, table in enumerate(tier_tables[:4]):
            tier = tier_names[i] if i < len(tier_names) else f'tier{i+1}'
            print(f"\nAssigning to {tier}...")
            limits = parse_rate_limit_table(table)
            rate_limits[tier] = limits
        
        return rate_limits
        
    except Exception as e:
        print(f"✗ Error scraping rate limits: {e}")
        import traceback
        traceback.print_exc()
        return {}

def main():
    print("=" * 60)
    print("Anthropic Rate Limits Scraper")
    print("=" * 60)
    
    # Scrape rate limits
    rate_limits = scrape_rate_limits_page()
    
    if rate_limits:
        # Save to JSON
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_file = os.path.join(base_dir, 'data', 'anthropic', 'scraped_rate_limits.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'rate_limits': rate_limits,
                'scraped_at': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n✓ Saved to {output_file}")
    else:
        print("\n✗ No rate limits scraped")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
