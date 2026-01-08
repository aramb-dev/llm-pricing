# Data Directory

This directory contains pricing and specification data for AI models from various providers.

## Structure

```
data/
├── openai/          # OpenAI models (GPT, o-series, DALL-E, etc.)
├── anthropic/       # Anthropic models (Claude family)
└── google/          # Google models (Gemini family)
```

## Data Format

Each provider directory contains:
- `{provider}-pricing.csv` - Main pricing database
- `{provider}-models.json` - Model specifications and metadata
- `scraped_*.json` - Raw scraped data
- `*.html` - Cached HTML for parsing

## CSV Schema

All provider CSVs follow this standardized schema:

| Column | Description | Example |
|--------|-------------|---------|
| Provider | Model provider | OpenAI, Anthropic, Google |
| Model | Model identifier | gpt-5.2, claude-3-opus |
| Source Type | Pricing tier/variant | Standard, Batch, Priority |
| Context Window (Tokens) | Maximum context length | 400000 |
| Input Cost (per 1M tokens) | Cost for input | $1.75 |
| Cached Input Cost (per 1M tokens) | Cost for cached input | $0.175 |
| Output Cost (per 1M tokens) | Cost for output | $14.00 |
| Min Tokens | Minimum allocation | - |
| Max Tokens | Maximum output length | 128000 |
| Rate Limit (Requests/sec) | API rate limits | 500 RPM |
| Billing Notes | Additional info | Per-minute billing |
| Documentation URL | Official docs link | https://... |
| Last Updated | Date of last update | 2026-01-08 |

## Usage

Load data in Python:
```python
import pandas as pd

# Load OpenAI pricing
openai_df = pd.read_csv('data/openai/openai-pricing.csv')

# Load all providers
providers = ['openai', 'anthropic', 'google']
all_models = pd.concat([
    pd.read_csv(f'data/{provider}/{provider}-pricing.csv')
    for provider in providers
])
```

## Contributing

When adding or updating data:
1. Follow the standardized CSV schema
2. Update `Last Updated` field
3. Include source documentation URLs
4. Verify against official provider pricing pages
