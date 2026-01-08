# Architecture

## Project Structure

```
llm-pricing/
├── data/                    # Provider-specific pricing data
│   ├── openai/
│   │   ├── openai-pricing.csv
│   │   ├── scraped_model_details.json
│   │   └── *.html
│   ├── anthropic/
│   │   └── anthropic-pricing.csv
│   └── google/
│       └── google-pricing.csv
│
├── scripts/                 # Data collection & processing
│   ├── scrapers/           # Web scrapers per provider
│   ├── parsers/            # HTML & data parsers
│   └── validators/         # Data validation
│
├── web/                     # Public web interface
│   ├── public/             # Static assets
│   └── src/                # Application source
│
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md     # This file
│   ├── API.md              # API documentation (future)
│   └── CONTRIBUTING.md     # Contribution guide
│
└── .github/
    └── workflows/          # CI/CD automation
```

## Data Flow

```
1. Data Collection
   ├─→ Manual entry (CSV direct edit)
   └─→ Automated scraping
       ├─→ Fetch HTML from provider docs
       ├─→ Clean & parse HTML
       ├─→ Extract pricing/specs
       └─→ Update CSV

2. Data Validation
   ├─→ Schema validation
   ├─→ Price sanity checks
   └─→ URL verification

3. Web Application
   ├─→ Read CSV data
   ├─→ Parse & transform
   ├─→ Display in UI
   └─→ Export/API endpoints

4. Updates & Notifications
   ├─→ Scheduled scraping (GitHub Actions)
   ├─→ Detect changes
   └─→ Notify subscribers
```

## Design Principles

1. **Provider Agnostic** - Easy to add new AI providers
2. **Data First** - CSV as source of truth, easily editable
3. **Automation** - Scrape and update automatically where possible
4. **Transparency** - All data sources documented
5. **Performance** - Fast static site, minimal dependencies
6. **Accessibility** - WCAG compliant, keyboard navigation

## Future Enhancements

- [ ] GraphQL/REST API for programmatic access
- [ ] Historical price tracking & charts
- [ ] Email alerts for price changes
- [ ] Model performance benchmarks
- [ ] Cost optimization recommendations
- [ ] Multi-currency support
- [ ] Provider API key cost tracking
