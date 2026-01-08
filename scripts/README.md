# Scripts Directory

Utilities for scraping, parsing, and validating model pricing data.

## Structure

```
scripts/
├── scrapers/        # Web scrapers for each provider
├── parsers/         # HTML/data parsers
└── validators/      # Data validation utilities
```

## Scrapers

### OpenAI
- `scrape_multiple_models.py` - Batch scrape OpenAI model details
- `scrape_openai_details.py` - Individual model scraper
- `parse_models_page.py` - Extract model links from overview page
- `parse_model_details.py` - Parse individual model detail pages

### Anthropic
- Coming soon

### Google
- Coming soon

## Utilities

- `clean_html.py` - Remove scripts/styles from HTML for easier parsing
- Data validators (coming soon)

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Scrape OpenAI models
cd scripts/scrapers
python scrape_multiple_models.py

# Parse HTML manually
python clean_html.py input.html output.html
python parse_model_details.py
```

## Adding New Scrapers

When adding scrapers for new providers:

1. Create provider-specific scraper in `scrapers/{provider}_scraper.py`
2. Follow existing patterns for consistency
3. Extract: pricing, context windows, max tokens, rate limits
4. Save to `data/{provider}/{provider}-pricing.csv`
5. Include error handling and rate limiting
6. Document in this README
