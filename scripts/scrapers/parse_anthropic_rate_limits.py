#!/usr/bin/env python3
"""
Parse Anthropic rate limits from the local markdown file.
"""

import json
import re
from datetime import datetime

def parse_rate_limits_markdown(md_file):
    """Parse rate limits from the markdown file"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    rate_limits = {}
    
    # Find Tier 1, 2, 3, 4 sections
    # The tabs are formatted as <Tab title="Tier X">...</Tab>
    tier_pattern = r'<Tab title="Tier (\d+)">\s*\n(.*?)\n</Tab>'
    tier_matches = re.findall(tier_pattern, content, re.DOTALL)
    
    for tier_num, tier_content in tier_matches:
        tier_key = f'tier{tier_num}'
        print(f"\nProcessing Tier {tier_num}...")
        
        # Find the table in this tier
        # Format: | Model | RPM | ITPM | OTPM |
        lines = tier_content.strip().split('\n')
        
        tier_limits = {}
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            # Start table when we see the separator line
            if '|' in line and '---' in line:
                in_table = True
                continue
            
            # Skip header line
            if 'Model' in line and 'Maximum requests' in line:
                continue
                
            # Parse table rows
            if in_table and line.startswith('|') and line.endswith('|'):
                # Parse data rows
                cells = [cell.strip() for cell in line.split('|')]
                cells = [c for c in cells if c]  # Remove empty cells
                
                if len(cells) >= 4:
                    model = cells[0]
                    rpm = cells[1]
                    itpm = cells[2]
                    otpm = cells[3]
                    
                    # Clean up markdown annotations and links
                    model = re.sub(r'<sup>.*?</sup>', '', model).strip()
                    model = re.sub(r'\[deprecated\].*?\)', '', model).strip()
                    model = re.sub(r'\(deprecated\)', '', model).strip()
                    itpm = re.sub(r'<sup>.*?</sup>', '', itpm).strip()
                    
                    # Skip empty models
                    if not model:
                        continue
                    
                    tier_limits[model] = {
                        'rpm': rpm,
                        'itpm': itpm,
                        'otpm': otpm
                    }
                    
                    print(f"  {model}: {rpm} RPM, {itpm} ITPM, {otpm} OTPM")
        
        # Only add to rate_limits if we found data
        if tier_limits:
            rate_limits[tier_key] = tier_limits
    
    return rate_limits

def main():
    print("=" * 60)
    print("Anthropic Rate Limits Parser (from Markdown)")
    print("=" * 60)
    
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    md_file = os.path.join(base_dir, 'data', 'anthropic', 'rate-limits.md')
    
    # Parse rate limits
    rate_limits = parse_rate_limits_markdown(md_file)
    
    if rate_limits:
        # Save to JSON
        output_file = os.path.join(base_dir, 'data', 'anthropic', 'scraped_rate_limits.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'rate_limits': rate_limits,
                'scraped_at': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n✓ Saved to {output_file}")
        print(f"✓ Parsed {sum(len(limits) for limits in rate_limits.values())} model limits across {len(rate_limits)} tiers")
    else:
        print("\n✗ No rate limits parsed")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
