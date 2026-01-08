#!/usr/bin/env python3
"""
Add rate limits to Anthropic CSV from scraped_rate_limits.json
"""

import csv
import json
import os
from datetime import datetime

def load_rate_limits():
    """Load rate limits from JSON file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_file = os.path.join(base_dir, 'data', 'anthropic', 'scraped_rate_limits.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['rate_limits']

def map_model_to_rate_limit_key(model_name):
    """Map a specific model name to its rate limit key"""
    
    # Normalize the model name
    model = model_name.lower()
    
    # Map model groups
    if any(x in model for x in ['opus 4.5', 'opus 4.1', 'opus 4']):
        return 'Claude Opus 4.x'
    elif any(x in model for x in ['sonnet 4.5', 'sonnet 4']):
        return 'Claude Sonnet 4.x'
    elif 'sonnet 3.7' in model:
        return 'Claude Sonnet 3.7 ()'
    elif 'haiku 4.5' in model:
        return 'Claude Haiku 4.5'
    elif 'haiku 3.5' in model:
        return 'Claude Haiku 3.5 ()'
    elif 'haiku 3' in model:
        return 'Claude Haiku 3'
    
    return None

def format_rate_limit(rpm, itpm, otpm, tier='4'):
    """Format rate limit for display in billing notes"""
    return f"Tier {tier}: {rpm} RPM, {itpm} ITPM, {otpm} OTPM"

def update_csv_with_rate_limits():
    """Update the CSV file with rate limits"""
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file = os.path.join(base_dir, 'data', 'anthropic', 'anthropic-pricing.csv')
    
    # Load rate limits
    rate_limits = load_rate_limits()
    
    # Read CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Update each row
    updated_count = 0
    for row in rows:
        model_name = row['Model']
        
        # Map to rate limit key
        rate_key = map_model_to_rate_limit_key(model_name)
        
        print(f"Model: {model_name} -> Rate key: {rate_key}")
        
        if rate_key:
            # Get Tier 4 limits (highest standard tier)
            tier4_limits = rate_limits.get('tier4', {}).get(rate_key)
            
            if tier4_limits:
                rpm = tier4_limits['rpm']
                itpm = tier4_limits['itpm']
                otpm = tier4_limits['otpm']
                
                # Add to billing notes
                current_notes = row.get('Billing Notes', '')
                rate_limit_note = f"Rate limits: {rpm} RPM | {itpm} ITPM | {otpm} OTPM (Tier 4)"
                
                if current_notes:
                    row['Billing Notes'] = f"{current_notes}; {rate_limit_note}"
                else:
                    row['Billing Notes'] = rate_limit_note
                
                updated_count += 1
                print(f"✓ {model_name}: {rpm} RPM, {itpm} ITPM, {otpm} OTPM")
            else:
                print(f"✗ No tier 4 limits found for rate key: {rate_key}")
        else:
            print(f"✗ No rate key mapping for model: {model_name}")
    
    # Write updated CSV (use the original field names from the file)
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        # Get field names from first row
        if rows:
            fieldnames = list(rows[0].keys())
        else:
            fieldnames = [
                'Provider', 'Model', 'Source Type', 'Context Window (Tokens)',
                'Input Cost per 1M Tokens (USD)', 'Output Cost per 1M Tokens (USD)',
                'Min Tokens', 'Max Tokens', 'Rate Limit (Requests/sec)',
                'Billing Notes', 'Documentation URL', 'Last Updated'
            ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return updated_count

def main():
    print("=" * 60)
    print("Add Rate Limits to Anthropic CSV")
    print("=" * 60)
    
    count = update_csv_with_rate_limits()
    
    print(f"\n✓ Updated {count} rows with rate limits")
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
