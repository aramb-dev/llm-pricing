# ModelHub

> *Comprehensive pricing and specifications for AI language models*

A public catalog of AI model pricing, technical specifications, and rate limits across OpenAI, Anthropic, and Google.

---

## 🎯 Features

- **Multi-Provider Support** - OpenAI, Anthropic (Claude), Google (Gemini)
- **Comprehensive Data** - Pricing, context windows, rate limits, and more
- **Always Updated** - Automated scraping keeps data current
- **Web Interface** - Beautiful UI for browsing and comparing models (coming soon)
- **API Access** - Programmatic access to pricing data (coming soon)

## 📊 Data Coverage

### Providers
- ✅ **OpenAI** - GPT, o-series, DALL-E, Whisper, TTS
- 🚧 **Anthropic** - Claude family (coming soon)
- 🚧 **Google** - Gemini models (coming soon)

### Information Tracked
- Input/Output pricing across tiers (Batch, Flex, Standard, Priority)
- Context window sizes
- Maximum output tokens
- Rate limits (RPM/TPM by tier)
- Knowledge cutoffs
- Documentation links

## 🗂️ Project Structure

```
modelhub/
├── data/                    # Provider-specific pricing data
│   ├── openai/             # OpenAI models
│   ├── anthropic/          # Claude models
│   └── google/             # Gemini models
├── scripts/                 # Data collection scripts
│   ├── scrapers/           # Web scrapers
│   ├── parsers/            # Data parsers
│   └── validators/         # Validation utilities
├── web/                     # Public web interface
└── docs/                    # Documentation
```

## 🚀 Quick Start

### View Data

Browse CSV files in the `data/` directory:
- [`data/openai/openai-pricing.csv`](data/openai/openai-pricing.csv) - OpenAI pricing

### Use Scrapers

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Scrape OpenAI model details
cd scripts/scrapers
python scrape_multiple_models.py
```

## 🌐 Web Interface (Coming Soon)

A public website for easy browsing, filtering, and cost calculation.

**Planned Features:**
- Search and filter models
- Side-by-side comparisons
- Cost calculator for your usage
- Price history tracking
- Email alerts for changes

## Contributing

### Adding New Models

1. **Manual Entry**: Add model pricing data directly to `openai-pricing.csv`
2. **Automated Scraping**: Use the provided Python scripts to fetch model details

### Updating Model Details

To update context windows, max tokens, and rate limits:

1. **Install dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Scrape model details**:
   ```bash
   python scrape_multiple_models.py
   ```

   This will:
   - Fetch details from platform.openai.com/docs/models
   - Extract context windows, max tokens, and rate limits
   - Update the CSV automatically
   - Save raw data to `scraped_model_details.json`

3. **Manual HTML parsing** (if automated scraping fails):
   ```bash
   # 1. Copy HTML from model detail page
   # 2. Paste into models_page_raw.html
   # 3. Clean the HTML
   python clean_html.py models_page_raw.html models_page_clean.html
   
   # 4. Parse and update CSV
   python parse_model_details.py
   ```

### Contribution Guidelines

- **Accuracy**: Verify all pricing and specifications against official OpenAI documentation
- **Completeness**: Fill in as many fields as possible for each model entry
- **Date Tracking**: Update the `Last Updated` field when making changes
- **Documentation**: Include source URLs in the `Documentation URL` field
- **Formatting**: Maintain consistent CSV formatting (no extra spaces, proper escaping)

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b update-model-pricing`)
3. Make your changes to `openai-pricing.csv`
4. Verify data accuracy against official sources
5. Update `Last Updated` field to current date
6. Commit with descriptive message (`git commit -m "Add GPT-5.3 pricing data"`)
7. Push to your fork (`git push origin update-model-pricing`)
8. Submit a pull request with description of changes

### Data Verification

Before submitting:
- [ ] Pricing matches official OpenAI pricing page
- [ ] Model specifications match official model documentation
- [ ] All URLs are valid and point to correct documentation
- [ ] CSV file is properly formatted (test with `python -c "import csv; list(csv.DictReader(open('openai-pricing.csv')))"`)
- [ ] `Last Updated` field is current

## Scripts

- `scrape_multiple_models.py`: Automated scraper for model details
- `parse_models_page.py`: Extract model links from overview page
- `parse_model_details.py`: Parse individual model detail pages
- `clean_html.py`: Remove unnecessary HTML for easier parsing
- `scrape_openai_details.py`: Original scraping utility

## License

Data is compiled from publicly available OpenAI documentation. Please refer to OpenAI's terms of service for usage restrictions.

## Disclaimer

This is a community-maintained resource. Always verify pricing and specifications with official OpenAI documentation before making decisions based on this data.