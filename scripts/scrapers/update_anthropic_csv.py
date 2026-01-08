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
    
    # Define context windows for all models based on their family
    # If not in details, use these defaults
    model_context_windows = {
        'Claude Opus 4.5': {'context': '200000', 'output': '64000'},
        'Claude Opus 4.1': {'context': '200000', 'output': '64000'},
        'Claude Opus 4': {'context': '200000', 'output': '64000'},
        'Claude Opus 3': {'context': '200000', 'output': '64000'},
        'Claude Sonnet 4.5': {'context': '200000', 'output': '64000'},
        'Claude Sonnet 4': {'context': '200000', 'output': '64000'},
        'Claude Sonnet 3.7': {'context': '200000', 'output': '64000'},
        'Claude Haiku 4.5': {'context': '200000', 'output': '64000'},
        'Claude Haiku 3.5': {'context': '200000', 'output': '64000'},
        'Claude Haiku 3': {'context': '100000', 'output': '4096'},
    }
    
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
        
        # Get context window from matched details or defaults
        context_window = None
        max_output = None
        
        if matched_details:
            context_window = matched_details.get('context_window')
            max_output = matched_details.get('max_output_tokens')
        
        # If not found in scraped data, use defaults based on model name
        if not context_window or not max_output:
            # Try to match model name to defaults
            for model_key, specs in model_context_windows.items():
                if model_key in model_name:
                    if not context_window:
                        context_window = specs['context']
                    if not max_output:
                        max_output = specs['output']
                    break
        
        # Update the row
        if context_window and not row['Context Window (Tokens)']:
            row['Context Window (Tokens)'] = context_window
            updated_count += 1
        
        if max_output and not row['Max Tokens']:
            row['Max Tokens'] = max_output
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
    
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_file = os.path.join(base_dir, 'data', 'anthropic', 'anthropic-pricing.csv')
    model_details_file = os.path.join(base_dir, 'data', 'anthropic', 'scraped_model_details.json')
    
    update_csv_with_details(csv_file, model_details_file)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
