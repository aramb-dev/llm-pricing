#!/usr/bin/env python3
"""
Parse Google (Gemini) pricing from markdown files and save to CSV format
matching OpenAI/Anthropic structure.
"""

import csv
import re
from datetime import datetime
import os

def parse_price(price_str):
    """Parse price string like '$2.00' or '$0.30 (text / image / video)' to float"""
    if not price_str or price_str.lower() in ['not available', 'free of charge', '']:
        return None
    # Extract first number found
    match = re.search(r'\$?([\d.]+)', price_str.replace(',', ''))
    return float(match.group(1)) if match else None

def extract_model_context_window(models_content, model_code):
    """Extract context window for a model from models.md content"""
    # Find the model section
    pattern = rf'`{re.escape(model_code)}`.*?Input token limit.*?(\d+(?:,\d+)*)'
    match = re.search(pattern, models_content, re.DOTALL | re.IGNORECASE)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def extract_model_max_output(models_content, model_code):
    """Extract max output tokens for a model from models.md content"""
    pattern = rf'`{re.escape(model_code)}`.*?Output token limit.*?(\d+(?:,\d+)*)'
    match = re.search(pattern, models_content, re.DOTALL | re.IGNORECASE)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def parse_gemini_3_pro_preview(pricing_content, models_content):
    """Parse Gemini 3 Pro Preview pricing"""
    rows = []
    model_name = "Gemini 3 Pro Preview"
    model_code = "gemini-3-pro-preview"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 2.00,
        'Output Cost per 1M Tokens (USD)': 12.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts <= 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (>200k)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 4.00,
        'Output Cost per 1M Tokens (USD)': 18.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts > 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Context caching
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.20,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts <= 200k tokens; Storage: $4.50/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write (>200k)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.40,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts > 200k tokens; Storage: $4.50/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 1.00,
        'Output Cost per 1M Tokens (USD)': 6.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts <= 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (>200k)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 2.00,
        'Output Cost per 1M Tokens (USD)': 9.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts > 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_3_flash_preview(pricing_content, models_content):
    """Parse Gemini 3 Flash Preview pricing"""
    rows = []
    model_name = "Gemini 3 Flash Preview"
    model_code = "gemini-3-flash-preview"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing - text/image/video
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.50,
        'Output Cost per 1M Tokens (USD)': 3.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Standard pricing - audio
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 1.00,
        'Output Cost per 1M Tokens (USD)': 3.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Context caching
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.05,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.10,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.25,
        'Output Cost per 1M Tokens (USD)': 1.50,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.50,
        'Output Cost per 1M Tokens (USD)': 1.50,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_3_pro_image_preview(pricing_content, models_content):
    """Parse Gemini 3 Pro Image Preview pricing"""
    rows = []
    model_name = "Gemini 3 Pro Image Preview"
    model_code = "gemini-3-pro-image-preview"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 65536,
        'Input Cost per 1M Tokens (USD)': 2.00,
        'Output Cost per 1M Tokens (USD)': 12.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 32768,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image input; Text output pricing',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (Image Output)',
        'Context Window (Tokens)': context_window or 65536,
        'Input Cost per 1M Tokens (USD)': 2.00,
        'Output Cost per 1M Tokens (USD)': 120.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 32768,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Image output: $0.134 per 1K/2K image, $0.24 per 4K image',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 65536,
        'Input Cost per 1M Tokens (USD)': 1.00,
        'Output Cost per 1M Tokens (USD)': 6.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 32768,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text input/output pricing',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (Image Output)',
        'Context Window (Tokens)': context_window or 65536,
        'Input Cost per 1M Tokens (USD)': 1.00,
        'Output Cost per 1M Tokens (USD)': 60.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 32768,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Image output: $0.067 per 1K/2K image, $0.12 per 4K image',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_25_pro(pricing_content, models_content):
    """Parse Gemini 2.5 Pro pricing"""
    rows = []
    model_name = "Gemini 2.5 Pro"
    model_code = "gemini-2.5-pro"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 1.25,
        'Output Cost per 1M Tokens (USD)': 10.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts <= 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (>200k)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 2.50,
        'Output Cost per 1M Tokens (USD)': 15.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts > 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Context caching
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.125,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts <= 200k tokens; Storage: $4.50/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write (>200k)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.25,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts > 200k tokens; Storage: $4.50/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.625,
        'Output Cost per 1M Tokens (USD)': 5.00,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts <= 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (>200k)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 1.25,
        'Output Cost per 1M Tokens (USD)': 7.50,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Prompts > 200k tokens; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_25_flash(pricing_content, models_content):
    """Parse Gemini 2.5 Flash pricing"""
    rows = []
    model_name = "Gemini 2.5 Flash"
    model_code = "gemini-2.5-flash"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing - text/image/video
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.30,
        'Output Cost per 1M Tokens (USD)': 2.50,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Standard pricing - audio
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 1.00,
        'Output Cost per 1M Tokens (USD)': 2.50,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Context caching
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.03,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.10,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.15,
        'Output Cost per 1M Tokens (USD)': 1.25,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.50,
        'Output Cost per 1M Tokens (USD)': 1.25,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_25_flash_lite(pricing_content, models_content):
    """Parse Gemini 2.5 Flash-Lite pricing"""
    rows = []
    model_name = "Gemini 2.5 Flash-Lite"
    model_code = "gemini-2.5-flash-lite"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing - text/image/video
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.10,
        'Output Cost per 1M Tokens (USD)': 0.40,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Standard pricing - audio
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.30,
        'Output Cost per 1M Tokens (USD)': 0.40,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Context caching
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.01,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.03,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.05,
        'Output Cost per 1M Tokens (USD)': 0.20,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.15,
        'Output Cost per 1M Tokens (USD)': 0.20,
        'Min Tokens': '',
        'Max Tokens': max_output or 65536,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input; Output includes thinking tokens',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_20_flash(pricing_content, models_content):
    """Parse Gemini 2.0 Flash pricing"""
    rows = []
    model_name = "Gemini 2.0 Flash"
    model_code = "gemini-2.0-flash"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.10,
        'Output Cost per 1M Tokens (USD)': 0.40,
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Standard pricing - audio
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.70,
        'Output Cost per 1M Tokens (USD)': 0.40,
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Context caching
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.025,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Cache Write (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.175,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio; Storage: $1.00/1M tokens/hour',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.05,
        'Output Cost per 1M Tokens (USD)': 0.20,
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Text/image/video input',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch (Audio)',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.35,
        'Output Cost per 1M Tokens (USD)': 0.20,
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Audio input',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_gemini_20_flash_lite(pricing_content, models_content):
    """Parse Gemini 2.0 Flash-Lite pricing"""
    rows = []
    model_name = "Gemini 2.0 Flash-Lite"
    model_code = "gemini-2.0-flash-lite"
    context_window = extract_model_context_window(models_content, model_code)
    max_output = extract_model_max_output(models_content, model_code)
    
    # Standard pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Standard',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.075,
        'Output Cost per 1M Tokens (USD)': 0.30,
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    # Batch pricing
    rows.append({
        'Provider': 'Google',
        'Model': model_name,
        'Source Type': 'Batch',
        'Context Window (Tokens)': context_window or 1048576,
        'Input Cost per 1M Tokens (USD)': 0.0375,
        'Output Cost per 1M Tokens (USD)': 0.15,
        'Min Tokens': '',
        'Max Tokens': max_output or 8192,
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': datetime.now().strftime('%Y-%m-%d')
    })
    
    return rows

def parse_additional_models(pricing_content, models_content):
    """Parse additional models like embeddings, TTS, image generation"""
    rows = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Gemini Embedding
    rows.append({
        'Provider': 'Google',
        'Model': 'Gemini Embedding',
        'Source Type': 'Standard',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': 0.15,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Embeddings model',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': 'Gemini Embedding',
        'Source Type': 'Batch',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': 0.075,
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': 'Embeddings model',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    # Image generation models
    rows.append({
        'Provider': 'Google',
        'Model': 'Imagen 4 Fast',
        'Source Type': 'Image Generation',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': '',
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '$0.02 per image',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': 'Imagen 4 Standard',
        'Source Type': 'Image Generation',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': '',
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '$0.04 per image',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': 'Imagen 4 Ultra',
        'Source Type': 'Image Generation',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': '',
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '$0.06 per image',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': 'Imagen 3',
        'Source Type': 'Image Generation',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': '',
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '$0.03 per image',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    # Video generation
    rows.append({
        'Provider': 'Google',
        'Model': 'Veo 3.1 Standard',
        'Source Type': 'Video Generation',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': '',
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '$0.40 per second (with audio)',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    rows.append({
        'Provider': 'Google',
        'Model': 'Veo 3.1 Fast',
        'Source Type': 'Video Generation',
        'Context Window (Tokens)': '',
        'Input Cost per 1M Tokens (USD)': '',
        'Output Cost per 1M Tokens (USD)': '',
        'Min Tokens': '',
        'Max Tokens': '',
        'Rate Limit (Requests/sec)': '',
        'Billing Notes': '$0.15 per second (with audio)',
        'Documentation URL': 'https://ai.google.dev/gemini-api/docs/pricing',
        'Last Updated': today
    })
    
    return rows

def main():
    print("=" * 60)
    print("Google (Gemini) Pricing Parser")
    print("=" * 60)
    
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Read markdown files
    models_file = os.path.join(base_dir, 'data', 'google', 'models.md')
    pricing_file = os.path.join(base_dir, 'data', 'google', 'pricing.md')
    
    print(f"\nReading {models_file}...")
    with open(models_file, 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    print(f"Reading {pricing_file}...")
    with open(pricing_file, 'r', encoding='utf-8') as f:
        pricing_content = f.read()
    
    # Parse all models
    all_rows = []
    
    print("\nParsing Gemini 3 Pro Preview...")
    all_rows.extend(parse_gemini_3_pro_preview(pricing_content, models_content))
    
    print("Parsing Gemini 3 Flash Preview...")
    all_rows.extend(parse_gemini_3_flash_preview(pricing_content, models_content))
    
    print("Parsing Gemini 3 Pro Image Preview...")
    all_rows.extend(parse_gemini_3_pro_image_preview(pricing_content, models_content))
    
    print("Parsing Gemini 2.5 Pro...")
    all_rows.extend(parse_gemini_25_pro(pricing_content, models_content))
    
    print("Parsing Gemini 2.5 Flash...")
    all_rows.extend(parse_gemini_25_flash(pricing_content, models_content))
    
    print("Parsing Gemini 2.5 Flash-Lite...")
    all_rows.extend(parse_gemini_25_flash_lite(pricing_content, models_content))
    
    print("Parsing Gemini 2.0 Flash...")
    all_rows.extend(parse_gemini_20_flash(pricing_content, models_content))
    
    print("Parsing Gemini 2.0 Flash-Lite...")
    all_rows.extend(parse_gemini_20_flash_lite(pricing_content, models_content))
    
    print("Parsing additional models...")
    all_rows.extend(parse_additional_models(pricing_content, models_content))
    
    # Write CSV
    output_file = os.path.join(base_dir, 'data', 'google', 'google-pricing.csv')
    
    fieldnames = [
        'Provider', 'Model', 'Source Type', 'Context Window (Tokens)',
        'Input Cost per 1M Tokens (USD)', 'Output Cost per 1M Tokens (USD)',
        'Min Tokens', 'Max Tokens', 'Rate Limit (Requests/sec)',
        'Billing Notes', 'Documentation URL', 'Last Updated'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\n✓ Saved {len(all_rows)} rows to {output_file}")
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == '__main__':
    main()
