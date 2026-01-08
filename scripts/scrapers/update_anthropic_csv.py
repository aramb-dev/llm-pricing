#!/usr/bin/env python3
"""
Update the Anthropic CSV with scraped model details.
Combines pricing data with model specifications.
"""

import csv
import json
from datetime import datetime

def load_json(filepath):
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠ File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing JSON {filepath}: {e}")
        return None

def update_csv_with_details(csv_file, model_details_file):
    """Update CSV with model details from JSON"""
    
    # Load model details
    model_details_data = load_json(model_details_file)
    if not model_details_data:
        print("No model details to update")
        return
    
    model_details = model_details_data.get('models', {})
    
    # Read existing CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    updated_count = 0
    
    # Update rows with model details
    for row in rows:
        model_name = row['Model']
        
        # Try to match with scraped data
        matched_details = None
        
        # Exact match
        if model_name in model_details:
            matched_details = model_details[model_name]
        else:
            # Try fuzzy matching
            model_lower = model_name.lower()
            for detail_model, details in model_details.items():
                if model_lower in detail_model.lower() or detail_model.lower() in model_lower:
                    matched_details = details
                    break
        
        if matched_details:
            # Update context window
            if matched_details.get('context_window') and not row['Context Window (Tokens)']:
                row['Context Window (Tokens)'] = matched_details['context_window']
                updated_count += 1
            
            # Update max output tokens
            if matched_details.get('max_output_tokens') and not row['Max Tokens']:
                row['Max Tokens'] = matched_details['max_output_tokens']
                updated_count += 1
            
            # Update billing notes with knowledge cutoff if available
            if matched_details.get('knowledge_cutoff'):
                cutoff_note = f"Knowledge cutoff: {matched_details['knowledge_cutoff']}"
                if row['Billing Notes']:
                    if 'Knowledge cutoff' not in row['Billing Notes']:
                        row['Billing Notes'] += f"; {cutoff_note}"
                else:
                    row['Billing Notes'] = cutoff_note
                updated_count += 1
    
    # Write updated CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Updated {updated_count} fields in {csv_file}")

def main():
    print("=" * 60)
    print("Update Anthropic CSV with Model Details")
    print("=" * 60)
    
    csv_file = '../../data/anthropic/anthropic-pricing.csv'
    model_details_file = '../../data/anthropic/scraped_model_details.json'
    
    update_csv_with_details(csv_file, model_details_file)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
