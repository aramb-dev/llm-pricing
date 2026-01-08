import requests
from bs4 import BeautifulSoup
import csv
import re
import json
import time

def get_headers():
    """Return headers for requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def normalize_model_name(model):
    """Normalize model name to match URL format"""
    # Remove resolution info like (1024x1024)
    model = re.sub(r'\s*\([^)]*\)', '', model)
    
    # Remove specific version dates (but keep version numbers like 4.1)
    model = re.sub(r'-\d{4}-\d{2}-\d{2}', '', model)
    
    # Remove "data sharing" suffix
    model = re.sub(r'\s*\(data sharing\)', '', model, flags=re.IGNORECASE)
    
    # Clean up spaces and special chars
    model = model.strip()
    
    return model

def get_model_links_from_csv(csv_file):
    """Extract unique model names from the CSV to scrape"""
    models = {}  # Map normalized -> original
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row['Model'].strip()
            if model:
                # Normalize the model name
                normalized = normalize_model_name(model)
                
                # Skip non-model entries
                if not normalized or normalized.lower() in ['code interpreter', 'file search storage', 
                                                              'file search tool call', 'web search', 
                                                              'web search preview', 'chatkit']:
                    continue
                
                # Keep track of original model names for this normalized version
                if normalized not in models:
                    models[normalized] = []
                models[normalized].append(model)
    
    model_links = {}
    for normalized_model, originals in models.items():
        # Convert model name to URL format
        model_url = normalized_model.lower()
        full_url = f"https://platform.openai.com/docs/models/{model_url}"
        model_links[normalized_model] = {
            'url': full_url,
            'display_name': normalized_model,
            'original_names': originals
        }
    
    return model_links

def get_model_links():
    """Get all model links - combination of CSV models and known models"""
    
    # Start with models from CSV
    print("Extracting models from CSV...")
    csv_models = get_model_links_from_csv("openai-pricing.csv")
    
    print(f"Found {len(csv_models)} unique models in CSV")
    
    return csv_models

def scrape_model_page(model_id, url):
    """Scrape an individual model page for detailed information"""
    print(f"  Scraping {model_id}...", end=' ')
    
    try:
        response = requests.get(url, headers=get_headers())
        response.raise_for_status()
        
        print("✓")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        details = {
            'model_id': model_id,
            'context_window': None,
            'max_output': None,
            'knowledge_cutoff': None,
            'rate_limits': {}
        }
        
        # Extract quick stats from the icon boxes
        # Look for text patterns like "400,000 context window", "128,000 max output tokens"
        text_content = soup.get_text()
        
        # Context window
        context_match = re.search(r'([\d,]+)\s+context window', text_content, re.IGNORECASE)
        if context_match:
            details['context_window'] = context_match.group(1).replace(',', '')
        
        # Max output tokens
        output_match = re.search(r'([\d,]+)\s+max output tokens', text_content, re.IGNORECASE)
        if output_match:
            details['max_output'] = output_match.group(1).replace(',', '')
        
        # Knowledge cutoff
        cutoff_match = re.search(r'([A-Za-z]+\s+\d+,\s+\d{4})\s+knowledge cutoff', text_content, re.IGNORECASE)
        if cutoff_match:
            details['knowledge_cutoff'] = cutoff_match.group(1)
        
        # Extract rate limits table
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this is a rate limits table
            headers = table.find_all('th')
            header_texts = [h.get_text(strip=True).lower() for h in headers]
            
            if 'rpm' in header_texts and 'tier' in header_texts:
                # Extract rate limits for each tier
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        tier = cells[0].get_text(strip=True)
                        
                        # Check if tier is supported
                        if 'not supported' in row.get_text(strip=True).lower():
                            continue
                        
                        rpm = cells[1].get_text(strip=True) if len(cells) > 1 else None
                        tpm = cells[2].get_text(strip=True) if len(cells) > 2 else None
                        batch_limit = cells[3].get_text(strip=True) if len(cells) > 3 else None
                        
                        details['rate_limits'][tier] = {
                            'rpm': rpm.replace(',', '') if rpm else None,
                            'tpm': tpm.replace(',', '') if tpm else None,
                            'batch_limit': batch_limit.replace(',', '') if batch_limit else None
                        }
                break
        
        return details
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print("✗ (404 Not Found)")
        elif e.response.status_code == 403:
            print("✗ (403 Rate Limited - will retry with longer delay)")
            time.sleep(2)  # Wait longer before next request
        else:
            print(f"✗ ({e})")
        return None
    except Exception as e:
        print(f"✗ (Error: {e})")
        return None

def scrape_openai_models():
    """Scrape all OpenAI model pages for detailed information"""
    
    # Get all model links
    model_links = get_model_links()
    
    # Dictionary to store all model details
    all_details = {}
    
    # Scrape each model page
    print("\nScraping individual model pages...")
    for model_id, info in model_links.items():
        details = scrape_model_page(model_id, info['url'])
        if details:
            all_details[model_id] = details
        
        # Be polite - add a delay between requests to avoid rate limiting
        time.sleep(1.5)
    
    return all_details

def update_csv_with_details(csv_file, all_details, dry_run=True):
    """Update the CSV file with scraped details"""
    
    # Read the CSV
    rows = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    print(f"\nFound {len(all_details)} model detail pages")
    
    # Track updates
    updates_made = []
    
    # Update rows with details
    for row in rows:
        model = row['Model']
        original_row = row.copy()
        
        # Try to match model name with scraped model IDs
        matched = False
        for model_id, details in all_details.items():
            # Direct match or model name contains model_id
            if (model.lower() == model_id.lower() or 
                model.lower().replace('-', '') == model_id.lower().replace('-', '') or
                model_id.lower() in model.lower() or
                model.lower() in model_id.lower()):
                
                matched = True
                changes = []
                
                # Update context window
                if details.get('context_window'):
                    row['Context Window (Tokens)'] = details['context_window']
                    if row['Context Window (Tokens)'] != original_row['Context Window (Tokens)']:
                        changes.append(f"Context: {row['Context Window (Tokens)']}")
                
                # Update max output tokens
                if details.get('max_output'):
                    row['Max Tokens'] = details['max_output']
                    if row['Max Tokens'] != original_row['Max Tokens']:
                        changes.append(f"Max: {row['Max Tokens']}")
                
                # Add knowledge cutoff to billing notes if exists
                if details.get('knowledge_cutoff'):
                    cutoff_text = details['knowledge_cutoff']
                    if row['Billing Notes']:
                        if cutoff_text not in row['Billing Notes']:
                            row['Billing Notes'] += f"; {cutoff_text}"
                    else:
                        row['Billing Notes'] = cutoff_text
                
                # Update rate limits - use Tier 1 RPM as the standard
                if details.get('rate_limits') and 'Tier 1' in details['rate_limits']:
                    tier1 = details['rate_limits']['Tier 1']
                    if tier1.get('rpm'):
                        rpm = int(tier1['rpm'])
                        rps = rpm / 60
                        row['Rate Limit (Requests/sec)'] = f"{rps:.2f}"
                        if row['Rate Limit (Requests/sec)'] != original_row['Rate Limit (Requests/sec)']:
                            changes.append(f"Rate: {rps:.2f} req/sec ({rpm} RPM)")
                
                if changes:
                    updates_made.append(f"{model} <- {model_id}: {', '.join(changes)}")
                break
        
        if not matched and model:
            # Try looser matching for variants
            for model_id, details in all_details.items():
                # Check if base model name matches (e.g., "gpt-4o" matches "gpt-4o-2024-05-13")
                base_model = model.split('-')[0:2]  # Get first two parts
                base_id = model_id.split('-')[0:2]
                
                if base_model == base_id and len(base_model) >= 2:
                    changes = []
                    
                    # Only update if empty
                    if not original_row['Context Window (Tokens)'] and details.get('context_window'):
                        row['Context Window (Tokens)'] = details['context_window']
                        changes.append(f"Context: {row['Context Window (Tokens)']}")
                    
                    if not original_row['Max Tokens'] and details.get('max_output'):
                        row['Max Tokens'] = details['max_output']
                        changes.append(f"Max: {row['Max Tokens']}")
                    
                    if changes:
                        updates_made.append(f"{model} <- {model_id} (base match): {', '.join(changes)}")
                    break
    
    if dry_run:
        print(f"\n{'='*80}")
        print("DRY RUN MODE - No files will be modified")
        print(f"{'='*80}")
        if updates_made:
            print(f"\nWould make {len(updates_made)} updates:")
            for update in updates_made:
                print(f"  ✓ {update}")
        else:
            print("\nNo updates would be made.")
        print(f"\n{'='*80}")
    else:
        # Write updated CSV
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"\nUpdated {csv_file} with {len(updates_made)} changes")
    
    return updates_made

if __name__ == "__main__":
    # Scrape all model pages
    all_details = scrape_openai_models()
    
    print("\n=== Sample Model Details ===")
    sample_count = 0
    for model_id, details in all_details.items():
        if sample_count < 5:  # Show first 5 as samples
            print(f"\n{model_id}:")
            print(f"  Context Window: {details.get('context_window')}")
            print(f"  Max Output: {details.get('max_output')}")
            print(f"  Knowledge Cutoff: {details.get('knowledge_cutoff')}")
            if details.get('rate_limits'):
                print(f"  Rate Limits:")
                for tier, limits in details['rate_limits'].items():
                    print(f"    {tier}: RPM={limits.get('rpm')}, TPM={limits.get('tpm')}")
            sample_count += 1
    
    if len(all_details) > 5:
        print(f"\n... and {len(all_details) - 5} more models")
    
    # Save full details to JSON for inspection
    with open('model_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_details, f, indent=2)
    print(f"\nSaved all details to model_details.json")
    
    # Update CSV
    csv_file = "openai-pricing.csv"
    updates = update_csv_with_details(csv_file, all_details, dry_run=True)
    
    print(f"\n\nTo apply changes, edit the script and set dry_run=False")
