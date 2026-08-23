# Angle Library — 4 Hunts, Different Each Time

## Angle 1 — Wellfound / AngelList: Small Startups (2–50), Seattle

- **Target:** Wellfound `location=seattle` + `company_size=1-50` → Built In Seattle startups tab.
- **Why first:** Highest S-tier density for Aaron. Salary bands visible, 1-click apply, AI-heavy small teams where Aaron's cross-domain edge is a differentiator, not commodity.
- **Filters:** Exclude 500+ person, exclude non-Seattle remote-only. Prioritize AI infra, devtools, security.
- **Pitfall:** Wellfound pagination/JS — use browse or API; don't trust raw HTML scrape alone.

## Angle 2 — Built In Seattle + GeekWire 200 (Under-the-Radar)

- **Target:** BuiltIn Seattle `startups` + GeekWire 200 list → company sites directly (careers pages).
- **Why second:** Catches Seattle companies Wellfound misses (bootstrapped, non-venture, Eastside hardware). GeekWire 200 is curated Seattle-only.
- **Filters:** Company ≤200 employees preferred but allow 200–500 if Seattle HQ. Visit careers page for live postings (not aggregator stale).
- **Pitfall:** Many GeekWire 200 have no open roles — log zero-result sites too (they still count as scanned).

## Angle 3 — Remote-First but Seattle-Friendly + YC / TinySeed Alumni

- **Target:** YC Work at a Startup (Seattle filter) + TinySeed alumni + Otta remote+Seattle.
- **Why third:** Expands pool without abandoning Seattle — remote roles that explicitly welcome Seattle timezone. Founder-led, small team, high autonomy — Aaron's independent-practice background is a plus.
- **Filters:** Require overlap with Seattle timezone or "US remote" with Seattle mentioned.
- **Pitfall:** YC WaaS requires login — grade accordingly if blocked.

## Angle 4 — Niche-Fit: AI Infra / Security / Hardware / Repair (Profile-Matched)

- **Target:** Search by skill, not location: AI infra, LLM evaluation, security/pen-test, hardware diagnostics, knowledge systems. Cross Wellfound search + Built In + direct company sites.
- **Why last:** Highest Skill Leverage scores. Even if company is 5–20 people, Aaron's 300M-token, 300+ research docs, CH341A/hardware work is directly the job.
- **Filters:** Role keywords: `LLM`, `MCP`, `agent`, `infrastructure`, `security`, `firmware`, `support engineer`, `solutions architect`, `implementation`.
- **Pitfall:** Smallest pool — may need to relax Seattle to "Seattle or remote" to hit 100.

## How to Pick the Next Angle

After each hunt, check coverage gap:
- If hunt yielded many AI roles but no hardware/security → Angle 4 next.
- If Wellfound saturated (>50% duplicates next scrape) → switch source family.
- Log duplicate rate per site in site-log.csv.
