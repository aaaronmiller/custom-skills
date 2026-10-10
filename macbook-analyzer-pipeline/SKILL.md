---
name: macbook-analyzer-pipeline
description: Daily eBay search for Apple Silicon MacBook logic boards with MDM lock,
  fee-aware profit analysis, and markdown reporting
inputs:
- name: search_params
  description: eBay search parameters for Apple Silicon MacBook logic boards
  pointer_type: parameter
outputs:
- name: analysis_report
  description: Profit analysis report for MacBook logic board listings
  pointer_type: output_file
tags:
- research
- hardware
- macbook
grade: C
source: custom
---

# eBay Logic Board Search Skill

## Purpose
Search eBay for Apple Silicon MacBook logic boards with MDM lock, following specific filtering criteria and data extraction requirements.

## Trigger Conditions
- User requests Apple Silicon MacBook logic board search with MDM lock only
- Specific model IDs: A3114, A3113, A2681, A2338, A2442, A2337
- Price filtering for A2337 (16GB/512GB+ or 8/512 under $90)
- Daily 6am PST execution requirement

## Execution Steps

### 1. Search Preparation
- Target eBay with specific MDM keywords: "MDM", "Mobile Device Management", "company locked", "DEP", "remote management"
- Add Apple Silicon-specific terms: "Apple Silicon", "M1", "M2", "M3", "M4"
- Include model number search: A3114, A3113, A2681, A2338, A2442, A2337
- Exclude Intel boards and iCloud-locked items unless MDM-only

### 2. Search Execution
|- Use **web_search** tool with Google site: operator to bypass eBay bot detection
|- Execute four specific queries:
|  - `mdm_logic`: site:ebay.com "A2337" OR "A2681" OR "A2338" OR "A2442" OR "A3114" OR "A3113" "for parts" "MDM" "logic board"
|  - `clean_logic`: site:ebay.com "A2337" OR "A2681" "clean" "no MDM" "free from MDM" "logic board"
|  - `cross_platform`: site:offerup.com OR site:facebook.com/marketplace "MacBook Air" "A2337" "MDM" "for parts"
|  - `cross_ebay_fallback`: site:ebay.com "MacBook Air" "A2337" "MDM locked" "for parts"
|- For each result URL, use **web_extract** to get page content

### 3. Data Extraction
Process each extracted page to extract:
|- Model ID (from title/specifications)
|- Price (from title or content)
|- RAM and SSD capacity (regex or AI parsing)
|- Chip generation (M1/M2/M3/M4)
|- Condition (New/Used/For Parts/Refurbished)
|- MDM status (detect keywords: MDM, company locked, DEP, remote management, organization lock)
|- Seller info (name, location, feedback if available)
|- Source platform (eBay/OfferUp/Facebook)
|- Direct listing URL

### 4. Filtering Criteria
- Exclude: Intel boards, non-Apple Silicon, iCloud-locked items
- For A2337: Only include 16GB/512GB+ or 8/512 under $90 (board+shipping)
- Exclude boards that boot to setup or mention activation issues unless MDM is primary lock

### 5. Output Format
Generate table: "Apple Silicon Logic Boards (MDM Locked)"
Columns: Model ID | Price | Shipping | Specs | Seller | Condition | MDM Keywords | URL

### 6. Daily Execution
- Schedule for 6am PST daily
- Compare with previous results for price changes
- Document new keywords or strategy changes

## Known Limitations
- eBay API access may be restricted
- Web scraping may be blocked by eBay
- Detailed specs may not be available in search results
- Price filtering may not be precise

## Troubleshooting
- If search fails, try alternative marketplaces: OfferUp, FB Marketplace, Craigslist
- Use cached eBay search results if direct access fails
- Consider using eBay RSS feeds or third-party eBay search APIs

## Success Metrics
- Table with at least 5 relevant listings
- All filtering criteria applied correctly
- Daily execution working
- New keywords documented after each run

# eBay Logic Board Search Skill

## Purpose
Search eBay for Apple Silicon MacBook logic boards with MDM lock, following specific filtering criteria and data extraction requirements.

## Trigger Conditions
- User requests Apple Silicon MacBook logic board search with MDM lock only
- Specific model IDs: A3114, A3113, A2681, A2338, A2442, A2337
- Price filtering for A2337 (16GB/512GB+ or 8/512 under $90)
- Daily 6am PST execution requirement

## Execution Steps

### 1. Search Preparation
- Target eBay with specific MDM keywords: "MDM", "Mobile Device Management", "company locked", "DEP", "remote management"
- Add Apple Silicon-specific terms: "Apple Silicon", "M1", "M2", "M3", "M4"
- Include model number search: A3114, A3113, A2681, A2338, A2442, A2337
- Exclude Intel boards and iCloud-locked items unless MDM-only

### 2. Search Execution
|- Use **web_search** tool with Google site: operator to bypass eBay bot detection
|- Execute four specific queries:
|  - `mdm_logic`: site:ebay.com "A2337" OR "A2681" OR "A2338" OR "A2442" OR "A3114" OR "A3113" "for parts" "MDM" "logic board"
|  - `clean_logic`: site:ebay.com "A2337" OR "A2681" "clean" "no MDM" "free from MDM" "logic board"
|  - `cross_platform`: site:offerup.com OR site:facebook.com/marketplace "MacBook Air" "A2337" "MDM" "for parts"
|  - `cross_ebay_fallback`: site:ebay.com "MacBook Air" "A2337" "MDM locked" "for parts"
|- For each result URL, use **web_extract** to get page content

### 3. Data Extraction
Process each extracted page to extract:
|- Model ID (from title/specifications)
|- Price (from title or content)
|- RAM and SSD capacity (regex or AI parsing)
|- Chip generation (M1/M2/M3/M4)
|- Condition (New/Used/For Parts/Refurbished)
|- MDM status (detect keywords: MDM, company locked, DEP, remote management, organization lock)
|- Seller info (name, location, feedback if available)
|- Source platform (eBay/OfferUp/Facebook)
|- Direct listing URL

### 4. Filtering Criteria
- Exclude: Intel boards, non-Apple Silicon, iCloud-locked items
- For A2337: Only include 16GB/512GB+ or 8/512 under $90 (board+shipping)
- Exclude boards that boot to setup or mention activation issues unless MDM is primary lock

### 5. Output Format
Generate table: "Apple Silicon Logic Boards (MDM Locked)"
Columns: Model ID | Price | Shipping | Specs | Seller | Condition | MDM Keywords | URL

### 6. Daily Execution
- Schedule for 6am PST daily
- Compare with previous results for price changes
- Document new keywords or strategy changes

## Known Limitations
- eBay API access may be restricted
- Web scraping may be blocked by eBay
- Detailed specs may not be available in search results
- Price filtering may not be precise

## Troubleshooting
- If search fails, try alternative marketplaces: OfferUp, FB Marketplace, Craigslist
- Use cached eBay search results if direct access fails
- Consider using eBay RSS feeds or third-party eBay search APIs

## Success Metrics
- Table with at least 5 relevant listings
- All filtering criteria applied correctly
- Daily execution working
- New keywords documented after each run

# eBay Logic Board Search Skill

## Purpose
Search eBay for Apple Silicon MacBook logic boards with MDM lock, following specific filtering criteria and data extraction requirements.

## Trigger Conditions
- User requests Apple Silicon MacBook logic board search with MDM lock only
- Specific model IDs: A3114, A3113, A2681, A2338, A2442, A2337
- Price filtering for A2337 (16GB/512GB+ or 8/512 under $90)
- Daily 6am PST execution requirement

## Execution Steps

### 1. Search Preparation
- Target eBay with specific MDM keywords: "MDM", "Mobile Device Management", "company locked", "DEP", "remote management"
- Add Apple Silicon-specific terms: "Apple Silicon", "M1", "M2", "M3", "M4"
- Include model number search: A3114, A3113, A2681, A2338, A2442, A2337
- Exclude Intel boards and iCloud-locked items unless MDM-only

### 2. Search Execution
|- Use **web_search** tool with Google site: operator to bypass eBay bot detection
|- Execute four specific queries:
|  - `mdm_logic`: site:ebay.com "A2337" OR "A2681" OR "A2338" OR "A2442" OR "A3114" OR "A3113" "for parts" "MDM" "logic board"
|  - `clean_logic`: site:ebay.com "A2337" OR "A2681" "clean" "no MDM" "free from MDM" "logic board"
|  - `cross_platform`: site:offerup.com OR site:facebook.com/marketplace "MacBook Air" "A2337" "MDM" "for parts"
|  - `cross_ebay_fallback`: site:ebay.com "MacBook Air" "A2337" "MDM locked" "for parts"
|- For each result URL, use **web_extract** to get page content

### 3. Data Extraction
Process each extracted page to extract:
|- Model ID (from title/specifications)
|- Price (from title or content)
|- RAM and SSD capacity (regex or AI parsing)
|- Chip generation (M1/M2/M3/M4)
|- Condition (New/Used/For Parts/Refurbished)
|- MDM status (detect keywords: MDM, company locked, DEP, remote management, organization lock)
|- Seller info (name, location, feedback if available)
|- Source platform (eBay/OfferUp/Facebook)
|- Direct listing URL

### 4. Filtering Criteria
- Exclude: Intel boards, non-Apple Silicon, iCloud-locked items
- For A2337: Only include 16GB/512GB+ or 8/512 under $90 (board+shipping)
- Exclude boards that boot to setup or mention activation issues unless MDM is primary lock

### 5. Output Format
Generate table: "Apple Silicon Logic Boards (MDM Locked)"
Columns: Model ID | Price | Shipping | Specs | Seller | Condition | MDM Keywords | URL

### 6. Daily Execution
- Schedule for 6am PST daily
- Compare with previous results for price changes
- Document new keywords or strategy changes

## Known Limitations
- eBay API access may be restricted
- Web scraping may be blocked by eBay
- Detailed specs may not be available in search results
- Price filtering may not be precise

## Troubleshooting
- If search fails, try alternative marketplaces: OfferUp, FB Marketplace, Craigslist
- Use cached eBay search results if direct access fails
- Consider using eBay RSS feeds or third-party eBay search APIs

## Success Metrics
- Table with at least 5 relevant listings
- All filtering criteria applied correctly
- Daily execution working
- New keywords documented after each run

# eBay Logic Board Search Skill

## Purpose
Search eBay for Apple Silicon MacBook logic boards with MDM lock, following specific filtering criteria and data extraction requirements.

## Trigger Conditions
- User requests Apple Silicon MacBook logic board search with MDM lock only
- Specific model IDs: A3114, A3113, A2681, A2338, A2442, A2337
- Price filtering for A2337 (16GB/512GB+ or 8/512 under $90)
- Daily 6am PST execution requirement

## Execution Steps

### 1. Search Preparation
- Target eBay with specific MDM keywords: "MDM", "Mobile Device Management", "company locked", "DEP", "remote management"
- Add Apple Silicon-specific terms: "Apple Silicon", "M1", "M2", "M3", "M4"
- Include model number search: A3114, A3113, A2681, A2338, A2442, A2337
- Exclude Intel boards and iCloud-locked items unless MDM-only

### 2. Search Execution
|- Use **web_search** tool with Google site: operator to bypass eBay bot detection
|- Execute four specific queries:
|  - `mdm_logic`: site:ebay.com "A2337" OR "A2681" OR "A2338" OR "A2442" OR "A3114" OR "A3113" "for parts" "MDM" "logic board"
|  - `clean_logic`: site:ebay.com "A2337" OR "A2681" "clean" "no MDM" "free from MDM" "logic board"
|  - `cross_platform`: site:offerup.com OR site:facebook.com/marketplace "MacBook Air" "A2337" "MDM" "for parts"
|  - `cross_ebay_fallback`: site:ebay.com "MacBook Air" "A2337" "MDM locked" "for parts"
|- For each result URL, use **web_extract** to get page content

### 3. Data Extraction
Process each extracted page to extract:
|- Model ID (from title/specifications)
|- Price (from title or content)
|- RAM and SSD capacity (regex or AI parsing)
|- Chip generation (M1/M2/M3/M4)
|- Condition (New/Used/For Parts/Refurbished)
|- MDM status (detect keywords: MDM, company locked, DEP, remote management, organization lock)
|- Seller info (name, location, feedback if available)
|- Source platform (eBay/OfferUp/Facebook)
|- Direct listing URL

### 4. Filtering Criteria
- Exclude: Intel boards, non-Apple Silicon, iCloud-locked items
- For A2337: Only include 16GB/512GB+ or 8/512 under $90 (board+shipping)
- Exclude boards that boot to setup or mention activation issues unless MDM is primary lock

### 5. Output Format
Generate table: "Apple Silicon Logic Boards (MDM Locked)"
Columns: Model ID | Price | Shipping | Specs | Seller | Condition | MDM Keywords | URL

### 6. Daily Execution
- Schedule for 6am PST daily
- Compare with previous results for price changes
- Document new keywords or strategy changes

## Known Limitations
- eBay API access may be restricted
- Web scraping may be blocked by eBay
- Detailed specs may not be available in search results
- Price filtering may not be precise

## Troubleshooting
- If search fails, try alternative marketplaces: OfferUp, FB Marketplace, Craigslist
- Use cached eBay search results if direct access fails
- Consider using eBay RSS feeds or third-party eBay search APIs

## Success Metrics
- Table with at least 5 relevant listings
- All filtering criteria applied correctly
- Daily execution working
- New keywords documented after each run