---
name: research-macbook
description: "Run research-focused eBay searches for Apple Silicon MacBook logic boards with MDM lock detection, separate from the macbook-analyzer-pipeline cron skill."
category: research
always_invoke: true for cron job execution of macbook-analyzer-pipeline
tags:
- research
- hardware
- data
grade: C
source: custom
---

# MacBook Analyzer Pipeline

## Config
- Script: `~/code/ebay-tracker/macbook_analyzer.py`
- Config: `~/code/ebay-tracker/config.json`
- Inventory: `~/code/ebay-tracker/inventory.json`
- Database: `~/Documents/hermes/macbook_data.db`
- Reports: `~/Documents/hermes/ebay-search-results-YYYY-MM-DD.md`

## Models Tracked
- A3114 (M4), A3113 (M4 Pro), A2681 (M2 Pro/Max), A2338 (M1 Pro), A2442 (M1 Pro/Max), A2337 (M1)

## MDM Keywords
"MDM", "Mobile Device Management", "company locked", "DEP", "remote management", "boot to setup", "cannot activate"

## Exclusions
- Intel-based boards (exclude)
- iCloud-only locked boards (exclude unless MDM also mentioned)

## Search Strategy
Use `google site:ebay.com` operator searches to bypass eBay bot detection.

## Pipeline Steps
1. Read config from `~/code/ebay-tracker/config.json`
2. Load inventory from `~/code/ebay-tracker/inventory.json`
3. Run searches for MDM-locked boards across all tracked models
4. Extract: title, price, specs (RAM, SSD, chip), condition, MDM status, seller, URL
5. Run profit analysis using config parameters (labor, eBay fee 15%, PayPal fee 4%, shipping $20)
6. Save findings to database + generate markdown report
7. Report to user (or [SILENT] if cron and no notable finds)

## Cost Analysis Parameters
- Labor: $150.00 (overrides: A2337=$120, A2681=$180)
- eBay fee: 15%
- PayPal fee: 4%
- Shipping: $20
- Min profit alert: $50

## Price Benchmarks (Mar 2026)
- A2337 (M1 8/256): ~$180-295 working
- A2681 (M2 Pro 8/512): ~$239-299 working
- A2442 (M1 Pro 32/512): ~$179 MDM-locked (found)

## Special Targets
- A2337: 16GB/512GB+ or 8/512 under $90 desirable


# MacBook Analyzer Pipeline

## Config
- Script: `~/code/ebay-tracker/macbook_analyzer.py`
- Config: `~/code/ebay-tracker/config.json`
- Inventory: `~/code/ebay-tracker/inventory.json`
- Database: `~/Documents/hermes/macbook_data.db`
- Reports: `~/Documents/hermes/ebay-search-results-YYYY-MM-DD.md`

## Models Tracked
- A3114 (M4), A3113 (M4 Pro), A2681 (M2 Pro/Max), A2338 (M1 Pro), A2442 (M1 Pro/Max), A2337 (M1)

## MDM Keywords
"MDM", "Mobile Device Management", "company locked", "DEP", "remote management", "boot to setup", "cannot activate"

## Exclusions
- Intel-based boards (exclude)
- iCloud-only locked boards (exclude unless MDM also mentioned)

## Search Strategy
Use `google site:ebay.com` operator searches to bypass eBay bot detection.

## Pipeline Steps
1. Read config from `~/code/ebay-tracker/config.json`
2. Load inventory from `~/code/ebay-tracker/inventory.json`
3. Run searches for MDM-locked boards across all tracked models
4. Extract: title, price, specs (RAM, SSD, chip), condition, MDM status, seller, URL
5. Run profit analysis using config parameters (labor, eBay fee 15%, PayPal fee 4%, shipping $20)
6. Save findings to database + generate markdown report
7. Report to user (or [SILENT] if cron and no notable finds)

## Cost Analysis Parameters
- Labor: $150.00 (overrides: A2337=$120, A2681=$180)
- eBay fee: 15%
- PayPal fee: 4%
- Shipping: $20
- Min profit alert: $50

## Price Benchmarks (Mar 2026)
- A2337 (M1 8/256): ~$180-295 working
- A2681 (M2 Pro 8/512): ~$239-299 working
- A2442 (M1 Pro 32/512): ~$179 MDM-locked (found)

## Special Targets
- A2337: 16GB/512GB+ or 8/512 under $90 desirable


# MacBook Analyzer Pipeline

## Config
- Script: `~/code/ebay-tracker/macbook_analyzer.py`
- Config: `~/code/ebay-tracker/config.json`
- Inventory: `~/code/ebay-tracker/inventory.json`
- Database: `~/Documents/hermes/macbook_data.db`
- Reports: `~/Documents/hermes/ebay-search-results-YYYY-MM-DD.md`

## Models Tracked
- A3114 (M4), A3113 (M4 Pro), A2681 (M2 Pro/Max), A2338 (M1 Pro), A2442 (M1 Pro/Max), A2337 (M1)

## MDM Keywords
"MDM", "Mobile Device Management", "company locked", "DEP", "remote management", "boot to setup", "cannot activate"

## Exclusions
- Intel-based boards (exclude)
- iCloud-only locked boards (exclude unless MDM also mentioned)

## Search Strategy
Use `google site:ebay.com` operator searches to bypass eBay bot detection.

## Pipeline Steps
1. Read config from `~/code/ebay-tracker/config.json`
2. Load inventory from `~/code/ebay-tracker/inventory.json`
3. Run searches for MDM-locked boards across all tracked models
4. Extract: title, price, specs (RAM, SSD, chip), condition, MDM status, seller, URL
5. Run profit analysis using config parameters (labor, eBay fee 15%, PayPal fee 4%, shipping $20)
6. Save findings to database + generate markdown report
7. Report to user (or [SILENT] if cron and no notable finds)

## Cost Analysis Parameters
- Labor: $150.00 (overrides: A2337=$120, A2681=$180)
- eBay fee: 15%
- PayPal fee: 4%
- Shipping: $20
- Min profit alert: $50

## Price Benchmarks (Mar 2026)
- A2337 (M1 8/256): ~$180-295 working
- A2681 (M2 Pro 8/512): ~$239-299 working
- A2442 (M1 Pro 32/512): ~$179 MDM-locked (found)

## Special Targets
- A2337: 16GB/512GB+ or 8/512 under $90 desirable


# MacBook Analyzer Pipeline

## Config
- Script: `~/code/ebay-tracker/macbook_analyzer.py`
- Config: `~/code/ebay-tracker/config.json`
- Inventory: `~/code/ebay-tracker/inventory.json`
- Database: `~/Documents/hermes/macbook_data.db`
- Reports: `~/Documents/hermes/ebay-search-results-YYYY-MM-DD.md`

## Models Tracked
- A3114 (M4), A3113 (M4 Pro), A2681 (M2 Pro/Max), A2338 (M1 Pro), A2442 (M1 Pro/Max), A2337 (M1)

## MDM Keywords
"MDM", "Mobile Device Management", "company locked", "DEP", "remote management", "boot to setup", "cannot activate"

## Exclusions
- Intel-based boards (exclude)
- iCloud-only locked boards (exclude unless MDM also mentioned)

## Search Strategy
Use `google site:ebay.com` operator searches to bypass eBay bot detection.

## Pipeline Steps
1. Read config from `~/code/ebay-tracker/config.json`
2. Load inventory from `~/code/ebay-tracker/inventory.json`
3. Run searches for MDM-locked boards across all tracked models
4. Extract: title, price, specs (RAM, SSD, chip), condition, MDM status, seller, URL
5. Run profit analysis using config parameters (labor, eBay fee 15%, PayPal fee 4%, shipping $20)
6. Save findings to database + generate markdown report
7. Report to user (or [SILENT] if cron and no notable finds)

## Cost Analysis Parameters
- Labor: $150.00 (overrides: A2337=$120, A2681=$180)
- eBay fee: 15%
- PayPal fee: 4%
- Shipping: $20
- Min profit alert: $50

## Price Benchmarks (Mar 2026)
- A2337 (M1 8/256): ~$180-295 working
- A2681 (M2 Pro 8/512): ~$239-299 working
- A2442 (M1 Pro 32/512): ~$179 MDM-locked (found)

## Special Targets
- A2337: 16GB/512GB+ or 8/512 under $90 desirable
