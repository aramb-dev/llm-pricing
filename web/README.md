# Web Directory

Public-facing web interface for browsing and comparing AI model pricing.

## Structure

```
web/
├── public/          # Static assets (images, fonts, etc.)
└── src/             # Source code for web application
```

## Features (Planned)

- 🔍 **Search & Filter** - Find models by name, provider, capabilities
- 💰 **Cost Calculator** - Estimate costs for your usage patterns
- 📊 **Comparison Tool** - Side-by-side model comparisons
- 📈 **Price History** - Track pricing changes over time
- 🔔 **Alerts** - Get notified of price changes
- 📱 **Responsive Design** - Works on all devices

## Tech Stack (TBD)

Options to consider:
- **Next.js** - React framework with SSR
- **Astro** - Fast static site generator
- **SvelteKit** - Modern, lightweight framework
- **Vue + Nuxt** - Progressive framework

## Development

```bash
# Setup (once stack is chosen)
cd web
npm install

# Development server
npm run dev

# Build for production
npm run build
```

## Data Integration

The web app will:
- Read CSV data from `../data/`
- Display real-time pricing information
- Support provider filtering and comparison
- Auto-update when CSVs are updated

## Deployment

Options:
- Vercel / Netlify (static hosting)
- Cloudflare Pages
- GitHub Pages
- Custom domain with CDN
