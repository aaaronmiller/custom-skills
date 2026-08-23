# Technique — Aaron Job Search

## Hunt 1 Learnings (2026-08-20)

- Wellfound SSR renders page 1 without login — S-tier for 2-50 Seattle startups (26 jobs from 452 total). Pages 2-8 need browser + login.
- Built In Seattle is A-tier: 46 jobs, 29 with bands, but mixes large enterprises. Filter by company profile before pulling cards.
- 101+ employee jobs (supplemental 181) are B-tier backup; no 2-50 jobs outside Wellfound in tested sources.
- Cloudflare WAF blocks GeekWire, Indeed, YC WaaS — needs cached/textise or browser bypass.
- Income inference needed for 38% of jobs — calibrate via Levels.fyi / Glassdoor by role+stage, mark [INFERRED].
- Scoring: CrowdStrike Agentic AI (58.1) is the archetype high-fit — LangGraph/CrewAI/Python/AWS/LLM exact match.

## Hunt 2 (2026-08-20) — Wellfound p2-5 + Built In Deep + GeekWire 200

- Wellfound `?page=N` SSR pagination: requests+BeautifulSoup with salary-line anchors works without login; browse daemon timed out on p3 — fallback runbook: requests+BS + iPhone UA.
- Built In deep: curl+regex on data-id job-card/company-title is most reliable; JSON-LD missing company/salary; Seattle filter leaks national jobs (85/126 non-Seattle).
- GeekWire 200: full list is JS widget after CF challenge — 33/200 via articles (Q1+Q2), remaining 167 need browser CF solve (Hunt 3).
- 3 resume forks now drive per-cluster scoring; fork noted per row in merged top100.
- Merged 200 -> Top 10 reshuffled: Tonifo Agentic (55.4), Ravenna AI (53.2), Affirm Solutions (53.2) join CrowdStrike 58.1 leader; threshold 34.0.
