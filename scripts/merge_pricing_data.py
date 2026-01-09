#!/usr/bin/env python3
"""
Merge all provider pricing CSV files into one consolidated CSV file.
"""

import csv
import os
from datetime import datetime

def read_csv_file(filepath):
    """Read a CSV file and return rows as list of dicts"""
    rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        print(f"  ✓ Read {len(rows)} rows from {os.path.basename(filepath)}")
        return rows
    except Exception as e:
        print(f"  ✗ Error reading {filepath}: {e}")
        return []

def merge_pricing_files(base_dir):
    """Merge all provider pricing CSV files"""
    
    # Define provider CSV files
    provider_files = [
        os.path.join(base_dir, 'data', 'openai', 'openai-pricing.csv'),
        os.path.join(base_dir, 'data', 'anthropic', 'anthropic-pricing.csv'),
        os.path.join(base_dir, 'data', 'google', 'google-pricing.csv'),
    ]
    
    all_rows = []
    
    print("\nReading provider CSV files...")
    for filepath in provider_files:
        if os.path.exists(filepath):
            rows = read_csv_file(filepath)
            all_rows.extend(rows)
        else:
            print(f"  ⚠ File not found: {filepath}")
    
    return all_rows

def write_merged_csv(rows, output_file):
    """Write merged data to CSV file"""
    
    if not rows:
        print("\n⚠ No data to write")
        return
    
    # Define fieldnames (using the standard schema)
    fieldnames = [
        'Provider',
        'Model',
        'Source Type',
        'Context Window (Tokens)',
        'Input Cost per 1M Tokens (USD)',
        'Output Cost per 1M Tokens (USD)',
        'Min Tokens',
        'Max Tokens',
        'Rate Limit (Requests/sec)',
        'Billing Notes',
        'Documentation URL',
        'Last Updated'
    ]
    
    # Ensure all rows have all fields
    normalized_rows = []
    for row in rows:
        normalized_row = {}
        for field in fieldnames:
            normalized_row[field] = row.get(field, '')
        normalized_rows.append(normalized_row)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_rows)
    
    print(f"\n✓ Saved {len(normalized_rows)} rows to {output_file}")

def generate_summary(rows):
    """Generate summary statistics"""
    
    if not rows:
        return
    
    # Count by provider
    providers = {}
    for row in rows:
        provider = row.get('Provider', 'Unknown')
        providers[provider] = providers.get(provider, 0) + 1
    
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("=" * 60)
    print(f"Total rows: {len(rows)}")
    print("\nBy Provider:")
    for provider, count in sorted(providers.items()):
        print(f"  {provider}: {count} rows")
    
    # Count by source type
    source_types = {}
    for row in rows:
        source_type = row.get('Source Type', 'Unknown')
        source_types[source_type] = source_types.get(source_type, 0) + 1
    
    print("\nBy Source Type:")
    for source_type, count in sorted(source_types.items(), key=lambda x: x[1], reverse=True):
        if count > 5:  # Only show common types
            print(f"  {source_type}: {count} rows")

def main():
    print("=" * 60)
    print("LLM Pricing Data Merger")
    print("=" * 60)
    
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Merge all provider files
    all_rows = merge_pricing_files(base_dir)
    
    if not all_rows:
        print("\n✗ No data found to merge")
        return
    
    # Write merged CSV
    output_file = os.path.join(base_dir, 'data', 'all-pricing.csv')
    write_merged_csv(all_rows, output_file)
    
    # Generate summary
    generate_summary(all_rows)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
