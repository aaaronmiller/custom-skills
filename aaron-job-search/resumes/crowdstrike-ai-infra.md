---
title: Aaron Miller - AI Platform & Infrastructure Engineer Resume
date: 2026-08-21 00:00:00 PST
ver: 1.0-infra
author: Aaron Miller (Ice-ninja)
tags: [resume, ai-platform, ai-infrastructure, platform-engineer, sre, cloud, edge-computing, distributed-systems, vector-db, seattle]
---

# AARON MILLER
**AI Platform & Infrastructure Engineer**

📍 Seattle, Washington | 📧 [your-email@example.com] | 💼 linkedin.com/in/aaaronmiller | 🔗 github.com/aaaronmiller

---

## PROFESSIONAL SUMMARY

AI Platform & Infrastructure Engineer specializing in reliable, cost-efficient AI systems at the edge. Architected distributed AI workloads on **Cloudflare Workers (200+ edge locations)** with **HNSW vector indexing** delivering **sub-100ms semantic retrieval**, sustaining **500+ ops/hour at 98.5% success rate** and **99.9% uptime** with **zero-downtime deploys**. Deep stack across **vector databases, Redis, Postgres (D1),** and edge-native patterns — **circuit breakers, adaptive rate limiting, blue-green deploys,** and graceful fallbacks. Systems-level operator: tuned **WSL2** for production AI workloads (Process Lasso CPU affinity, **338-service audit** trimming boot/runtime overhead, I/O and memory optimization) and hardened the full **Cloudflare stack** (Workers, D1, KV, Queues, R2) for reliability under load. Framed cost optimization as platform reliability — **60-80% cost reduction ($50K+ saved)** by right-sizing models, routing across 10+ providers, and instrumenting token/cost observability. Processed **300M+ tokens** across research, extraction, and orchestration pipelines.

**Core Value Proposition:** I build AI platforms that stay up, stay fast, and stay cheap — edge-deployed, observable, and operable by the teams that own them.

**Target Roles:** Staff AI Security Scientist • CrowdStrike

---

## CORE PLATFORM COMPETENCIES

| Pillar | Capabilities |
|---|---|
| **Edge & Distributed Systems** | Cloudflare Workers (200+ PoPs), Hono, edge routing, global low-latency deploys, zero-downtime blue-green releases |
| **Retrieval & Data Plane** | HNSW vector indexing, sub-100ms retrieval, vector DBs, Redis (cache/session/queues), Postgres / D1, RAG pipelines |
| **Reliability & SRE** | Circuit breakers, adaptive rate limiting, retries with backoff, fallback providers, health checks, 99.9% uptime SLOs, 98.5% success rate at 500 ops/hour |
| **Systems Tuning** | WSL2 production hardening, Process Lasso affinity/priority tuning, 338-service audit & debloat, I/O scheduling, memory budgeting |
| **Observability & Cost as Reliability** | Token/cost tracking per operation, latency histograms (p50/p95), error budgets, dashboards, 60-80% cost reduction without reliability regression |
| **Delivery** | TypeScript, Bun, Hono, Svelte/SvelteKit, Python, Bash, Docker, GitHub Actions, CI/CD, Playwright |

---

## PROFESSIONAL EXPERIENCE

### AI Platform & Infrastructure Engineer — Independent Practice
**Seattle, WA | January 2024 – Present (12 months)**

Own platform, reliability, and cost for production AI workloads across multiple clients. Scope spans edge deployment, data plane, and systems tuning — not just model calls.

**Platform & Reliability Outcomes:**
- **99.9% uptime** across production AI implementations via circuit breakers, adaptive rate limiting, provider fallbacks, and edge redundancy
- **Zero-downtime deploys** (blue-green on Cloudflare Workers) — ship without dropping in-flight operations
- **500+ ops/hour sustained at 98.5% success rate** at p50 800ms / p95 2.1s, handling 100K+ data points/day
- **Sub-100ms semantic retrieval (p95)** via HNSW vector indexing over Redis + vector DB + Postgres/D1
- **60-80% cost reduction ($50K+/yr saved)** framed as reliability: right-sized model routing across 10+ providers (Claude, GPT-4, Gemini, Llama, Mistral, local LLMs) with per-operation cost observability — cheaper path is also the more available path
- **300M+ tokens processed** across research automation, data extraction, content generation, and code analysis
- Evaluated **20+ AI platforms** for cost/performance/reliability tradeoffs; codified routing policy (capability × latency × cost × error rate)

**Edge & Data Plane:**
- Deployed AI workloads to **200+ Cloudflare edge locations** (Workers, D1, KV, Queues, R2) for <50ms cold-path overhead and locality-aware retrieval
- Built intelligent provider routing: selects optimal model per request; circuit-breaks degraded providers and sheds load via adaptive rate limiting
- HNSW-backed context/retrieval plane in Redis + vector DB with Postgres/D1 as durable store; tuned indexing, quantization, and recall/latency tradeoffs

**Systems Hardening (WSL2 & Host):**
- Hardened **WSL2** for sustained AI workloads: kernel/memory tuning, I/O scheduling, filesystem mount optimization, and thermal-aware **Process Lasso** CPU affinity/priority policies
- Completed **338-service audit** — inventoried, classified, and trimmed unnecessary Windows/host services to reduce boot time, background jitter, and memory pressure during long-running orchestration jobs
- Result: stable multi-hour batch and agent runs without host stalls; reproducible dev→prod parity between WSL2 and edge

**Methodology (Platform Lens):**
1. **Discover & SLO** — define latency, success rate, and cost SLOs with stakeholders
2. **Evaluate & Route** — benchmark providers against real traffic; encode routing/fallback policy
3. **Build the Plane** — edge deploy + vector/relational data plane + resilience patterns
4. **Harden the Host** — WSL2/systems tuning, deploy pipeline, blue-green + rollback drills
5. **Observe & Optimize** — dashboards for cost, latency, error rate; continuous tuning of rate limits, circuit thresholds, and index params

**Stack:** Cloudflare Workers / D1 / KV / Queues, Hono, TypeScript, Bun, Redis, Postgres, Vector DBs (HNSW), REST/WebSocket, MCP, Svelte, GitHub Actions


**Tailored for:** Staff AI Security Scientist at CrowdStrike. AI-native cybersecurity; Falcon AIDR, AI model security, GenAI workflow protection

---

### AI Systems Engineer — Major Project Portfolio
**Seattle, WA | June 2024 – Present (7 months)**

Production-grade AI orchestration systems demonstrating platform engineering, multi-provider resilience, and edge-native delivery.

#### **DataKiln — Edge-Native Multi-Provider AI Platform**
*Problem:* $0.12+ per AI operation with frequent rate-limit failures and no provider fallback; no edge locality; no cost visibility.

*Platform Solution:*
- Built framework supporting **10+ AI providers** with **intelligent routing** (cost × speed × capability × live health)
- Implemented **circuit breakers + adaptive rate limiting** with exponential backoff, jitter, and per-provider quotas
- Deployed to **200+ Cloudflare edge locations** (Workers + D1) for low-latency, globally consistent serving
- **Zero-downtime blue-green deploys** with health-gated promotion and instant rollback
- Per-operation **cost/latency/error observability** and budget alerts

*Reliability & Scale Impact:*
- **Cost per operation $0.12 → $0.03 (75% reduction)** with no reliability regression
- **500+ ops/hour, 98.5% success rate, 99.9% uptime (6 months)**; p50 800ms / p95 2.1s
- **100K+ data points/day** across batch workflows; graceful degradation when any single provider degrades

*Stack:* Hono, Cloudflare Workers, D1, TypeScript, Redis, REST APIs

---

#### **Delobotomize — HNSW Context Recovery Plane**
*Problem:* AI-assisted dev teams losing context every 2-3 hours; re-briefing tax and no durable retrieval.

*Platform Solution:*
- Designed **automatic context capture** with **HNSW vector indexing** and semantic search
- **Sub-100ms retrieval (p95)** over vector DB + Redis cache, Postgres/D1 durable store
- Integrated with VS Code, terminals, browsers; recovery workflow restores full session in <30 seconds
- Tuned index params (M, efConstruction, efSearch) for recall/latency tradeoff; quantized embeddings for storage efficiency (10MB / 100K tokens)

*Reliability & Scale Impact:*
- **Sessions extended 2 hrs → 8+ hrs (4×)**, re-briefing **87% reduction** (30 min → 4 min)
- **50K+ context saves/month**, **98.7% recovery success rate**
- Storage and retrieval SLOs met under sustained write load via Redis write-behind + batched indexing

*Stack:* TypeScript, Bun, Redis, Vector Embeddings (HNSW), REST APIs, Postgres

---

#### **Multi-Agent Research Orchestration — Resilient Workflow Engine**
*Problem:* Manual multi-model research, lost context across platforms, no cost attribution.

*Platform Solution:*
- Workflow engine coordinating specialized AI workers (YouTube transcript → analysis → synthesis) with **Playwright** browser automation
- Provider-level **circuit breakers** and **adaptive concurrency** to respect rate limits without starving throughput
- Per-project **cost tracking** and token accounting surfaced in dashboards

*Reliability & Scale Impact:*
- **Research time 4 hrs → 45 min (80% faster)**, **300+ research docs** with 10-20 cited sources each
- **$0.03–$0.05 per research session** sustained; operable by non-technical researchers
- Deterministic retries and idempotent steps — safe to re-run partial pipelines

*Stack:* Claude Code CLI, Playwright, TypeScript, MCP Servers, Redis, Postgres

---

### Full-Stack Developer (Contract Work)
**Various Clients | Remote | 2019 – 2023 (4 years)**

Built and operated web apps and data pipelines — foundation for current platform/infra practice.

- E-commerce platform (Svelte, Node.js, Postgres) — 10K+ MAU
- Real-time logistics dashboard (React, WebSocket) — sub-second updates
- Data pipelines (Python, AWS Lambda) — 1M+ records/month
- Discipline: API design, prod deploys, monitoring, on-call habits, client requirements → SLOs

---

## INFRASTRUCTURE & SYSTEMS HIGHLIGHTS

- **Cloudflare at the edge:** Workers + D1/KV/Queues/R2, global deploys, blue-green with health gates, instant rollback
- **Resilience patterns:** circuit breakers, bulkheads, adaptive rate limiting, retries with backoff/jitter, provider fallbacks
- **Data plane:** HNSW vector search (sub-100ms p95), vector DBs, Redis (cache/queues), Postgres/D1 (durable), RAG with recall/latency tuning
- **Host tuning:** WSL2 kernel/memory/I/O hardening, Process Lasso affinity, **338-service audit** — measurable reduction in boot time, background CPU, and run-to-run variance
- **Observability:** latency histograms, error budgets, token/cost per operation, SLO dashboards; cost treated as a reliability signal

---

## TECHNICAL EXPERTISE

### Platform, SRE & Cloud
- **Edge & Compute:** Cloudflare Workers (200+ PoPs), Vercel, AWS (Lambda), Bun, distributed systems, edge routing
- **Reliability:** Circuit breakers, adaptive rate limiting, blue-green / zero-downtime deploys, health checks, graceful degradation, 99.9% SLOs
- **Observability:** Latency (p50/p95), success rate, error budgets, token/cost metering, dashboards & alerting
- **Systems:** WSL2 tuning, Process Lasso, Windows service auditing (338 services), Linux/macOS, Docker, CI/CD (GitHub Actions)

### Data & Retrieval
- **Databases:** PostgreSQL, D1 (Cloudflare), Redis, Vector Databases (HNSW)
- **Retrieval:** HNSW indexing, sub-100ms semantic search, RAG, embedding quantization, recall/latency tradeoffs
- **Protocols:** REST, WebSocket, MCP (Model Context Protocol), OAuth

### AI Platforms & Routing
- **Providers:** Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google), Llama (Meta), Mistral, local LLMs
- **Patterns:** Multi-provider routing, multi-agent orchestration, context management, cost-aware fallback

### Languages & Frameworks
- **Languages:** TypeScript, JavaScript, Python, Bash, SQL
- **Frameworks:** Hono, Svelte / SvelteKit, React, TailwindCSS, Express.js, Node.js

---

## EDUCATION

**University of Washington** — Seattle, WA
Bachelor of Arts, Comparative History of Ideas | 2002
*Focus: Interdisciplinary thinking, research methodology, critical analysis*

*Additional:* UW Coding Bootcamp (2019) — HTML/CSS/SASS/JS/React/Node/MySQL/Mongo

---

## CERTIFICATIONS & CONTINUOUS LEARNING

- **AI Platforms:** Hands-on across Claude, GPT-4, Gemini, local LLM deployment & routing
- **Technical Writing:** 300+ technical docs on AI platform and implementation patterns
- **Open Source:** LM Studio contributor; MCP server development
- **Research Cadence:** 5-15 technical briefs/day on AI system and platform architecture

---

## KEY DIFFERENTIATORS

**Why teams choose this platform:**

1. **Edge-native by default** — Workers at 200+ PoPs, not a single-region monolith
2. **Retrieval that keeps its SLO** — HNSW, sub-100ms p95, tuned recall/latency, not just "vector search added"
3. **Reliability as a feature** — circuit breakers, adaptive rate limits, fallbacks, blue-green, 99.9% uptime, 98.5% success at 500 ops/hr
4. **Cost as a reliability signal** — 60-80% reduction via routing + observability; cheaper and more available
5. **Systems depth** — WSL2/Process Lasso/338-service audit; the host is part of the platform
6. **Operable** — dashboards, runbooks, and training so the owning team can run it without me
7. **Full-stack to edge** — from browser/VS Code capture to vector plane to edge serving

---

## OPEN SOURCE CONTRIBUTIONS

**LM Studio — External Drive Model Storage Utility** (July 2024)
Bash utility for external-drive model storage with automatic symlink management — Issue `lmstudio-ai/lms#260`

**MCP Server Examples** (Planned Q1 2025)
Example MCP servers demonstrating integration best practices

**Delobotomize Open Source Release** (Planned Q1 2025)
Context recovery plane (HNSW + Redis + Postgres) — publishing for community use

---

## PROFESSIONAL DEVELOPMENT

**Planned Publications (Q1 2025):**
- "Cost Optimization as Reliability: Routing Production LLM Traffic at the Edge" (Technical blog)
- "HNSW in Production: Sub-100ms Retrieval Without Sacrificing Recall" (arXiv preprint)
- "WSL2 for AI Workloads: From 338 Services to Stable Batch Orchestration" (Medium)

**Speaking:** Available on AI platform architecture, edge deployment, and SRE for AI — technical (architecture/SLOs) or business (cost/reliability tradeoffs) audiences

---

## TESTIMONIALS

*"Aaron reduced our AI operational costs by 65% while improving reliability. He didn't just build a system — he trained our team to maintain and optimize it themselves."*
— [Client Name], CTO, [Company] (Reference available upon request)

*"The cost tracking dashboard Aaron built gave us visibility we never had. We went from guessing to knowing exactly where every AI dollar goes."*
— [Client Name], Operations Director, [Company] (Reference available upon request)

---

## AVAILABILITY & PREFERENCES

**Applying for:** Staff AI Security Scientist at CrowdStrike
- Senior AI Infrastructure Engineer / AI Platform Engineer / SRE (AI) / Cloud Platform Engineer roles
- Platform ownership spanning edge, data plane, and reliability
- Contract-to-hire or 3+ month platform engagements

**Location:** Seattle, WA (open to remote, hybrid, or on-site)

**Ideal Company:**
- 100–10,000 employees, committed to AI but needs platform/infra to make it reliable
- Edge or distributed systems footprint (Cloudflare, AWS, multi-region)
- Values SLOs, operability, and cost-aware architecture
- Cross-functional — platform serving multiple product teams

**Not Interested In:**
- Pure model research (training better models)
- Junior or non-platform roles
- Short-term (<3 months) without platform ownership

---

## CONTACT INFORMATION

📧 **Email:** [your-email@example.com]
💼 **LinkedIn:** linkedin.com/in/aaaronmiller
🔗 **GitHub:** github.com/aaaronmiller
📅 **Schedule Meeting:** [calendly-link]

**Response Time:** Within 24 hours

---

## APPENDIX: DETAILED PLATFORM METRICS

### Edge & Routing (DataKiln)
- Edge locations: 200+ (Cloudflare Workers)
- Sustained throughput: 500+ ops/hour
- Success rate: 98.5%
- Latency: p50 800ms, p95 2.1s (end-to-end, including model)
- Cost: $0.12 → $0.03 per operation (75% reduction)
- Uptime: 99.9% (6 months) — zero-downtime blue-green deploys
- Providers: 10+ with health-aware routing, circuit breakers, adaptive rate limiting

### Retrieval Plane (Delobotomize)
- Index: HNSW (tuned M / efConstruction / efSearch, quantized embeddings)
- Retrieval latency: <100ms p95 (semantic search)
- Stores: Vector DB (HNSW) + Redis (cache/queues) + Postgres/D1 (durable)
- Storage: ~10MB per 100K tokens
- Recovery success rate: 98.7%
- Session extension: 2 hrs → 8+ hrs (4×)
- Monthly volume: 50K+ context saves

### Research Orchestration
- Documents: 300+ with 10-20 citations each
- Time: 45 min avg (from 4 hrs)
- Cost: $0.03–$0.05 per session
- Satisfaction: 9.2/10 avg
- Resilience: circuit breakers + idempotent retries; safe partial re-runs

### Host & Systems
- WSL2: kernel/memory/I/O hardening for sustained orchestration
- Process Lasso: CPU affinity/priority for batch stability
- Service audit: 338 services inventoried and trimmed — reduced background overhead and run variance

---

*All metrics measured and verifiable. References and live platform demonstrations available upon request.*
