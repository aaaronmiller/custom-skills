# Site Grading — S → E

| Grade | Meaning | Example |
|-------|---------|---------|
| **S** | Dense Seattle-small-startup, high signal, 1-click apply, fresh (<14d) | Wellfound Seattle 2–50 filter |
| **A** | Strong but some noise or light filtering needed | Built In Seattle |
| **B** | Useful with manual filtering, moderate density | GeekWire 200, Otta |
| **C** | Low density / stale (>30d) / heavy irrelevant | Generic LinkedIn Seattle |
| **D** | Mostly irrelevant / paywalled / login-gated scrape blocked | ZipRecruiter scrape |
| **E** | Spam / broken / CAPTCHA wall | Scraped aggregator with no Apply link |

## Log Template (append to hunts/site-log.csv)

```
timestamp,site_url,hunt,jobs_reviewed,grade,rationale
2026-08-20T...,https://wellfound.com/location/seattle,1,42,S,"38/42 Seattle small startups, salary bands present"
```

## Quality-over-time Note

Some sites are A for Aaron but C for generic SWE — e.g., Wellfound is S for AI infra + small team, D for enterprise .NET. Grade is *for Aaron specifically*, not generic quality. Re-grade after each hunt as filters change.
