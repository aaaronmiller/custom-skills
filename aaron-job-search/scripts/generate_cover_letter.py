#!/usr/bin/env python3
"""Generate cover letter for a job from cluster template + job details. Usage: generate_cover_letter.py --job-id N --cluster ai-infra|solutions|startup"""
import sqlite3, argparse, json, pathlib

def load_template(cluster):
    templates={
        'ai-infra':"""To the Hiring Manager,

I'm applying for the {role} position at {company}. My background in AI platform engineering — including building production orchestration systems that process 300M+ tokens, achieving 99.9% uptime, and reducing operational costs 60-80% through strategic tool selection — aligns well with what you're building.

In my current independent practice, I've designed and deployed multi-agent research orchestration systems, context recovery pipelines using HNSW vector indexing with sub-100ms retrieval, and edge-deployed microservices across 200+ global locations via Cloudflare Workers. I've evaluated 20+ AI platforms and built cost-optimization frameworks that reduced per-operation spend from $0.12 to $0.03.

I'm particularly drawn to {company}'s work on {what_they_do_short}. My experience with distributed systems, vector databases, and production AI infrastructure would let me contribute from day one.

I'd welcome the chance to discuss how my experience fits your team's needs.

Best regards,
Aaron Miller""",
        
        'solutions':"""To the Hiring Manager,

I'm writing about the {role} role at {company}. I've spent the past two years as an AI implementation consultant, helping organizations adopt AI-powered workflows. My core methodology — discovery & analysis, tool evaluation, integration design, training & rollout, monitoring & optimization — has delivered measurable results: 60-80% cost reductions, 99.9% uptime, and 15+ users trained across multiple client organizations.

At {company}, I'd bring both the technical depth and the client-facing communication skills this role requires. I've evaluated 20+ AI platforms, built production integration frameworks connecting AI to existing systems (databases, APIs, spreadsheets), and created training programs that enabled non-technical teams to adopt AI tools effectively.

I'm drawn to {company}'s mission of {what_they_do_short}. I'd be excited to help your customers realize the same kind of results I've delivered independently.

Best regards,
Aaron Miller""",
        
        'startup':"""To the Hiring Manager,

I'm interested in the {role} position at {company}. As a full-stack engineer with 17 years of experience running my own software practice and the past two years building production AI systems independently, I bring a rare combination of shipping speed and systems depth.

My tech stack — Svelte/SvelteKit, React, TypeScript, Hono/Express/Bun, PostgreSQL/Redis/D1, Cloudflare Workers — is production-tested across e-commerce platforms serving 10K+ monthly users, real-time dashboards, and data pipelines processing 1M+ records monthly. I've also built AI orchestration systems with 300M+ tokens processed and 99.9% uptime.

I'm excited about {company}'s work on {what_they_do_short}. As someone who has built and shipped products independently for years, I'm comfortable with the pace and ambiguity of early-stage work.

Best regards,
Aaron Miller"""
    }
    return templates.get(cluster, templates['startup'])

def short_desc(what_they_do):
    if not what_they_do: return 'an innovative product in your space'
    return what_they_do[:120] + ('...' if len(what_they_do)>120 else '')

parser=argparse.ArgumentParser()
parser.add_argument('--job-id', type=int, required=True)
parser.add_argument('--cluster', default='auto')
args=parser.parse_args()

db=sqlite3.connect('/home/cheta/code/custom-skills/aaron-job-search/submissions.db')
db.row_factory=sqlite3.Row
cur=db.cursor()

cur.execute("SELECT * FROM jobs WHERE id=?", (args.job_id,))
job=cur.fetchone()
if not job: print("Job not found"); exit(1)

cluster=args.cluster if args.cluster!='auto' else (job['resume_fork'] or 'startup').replace('resume-','').replace('.md','')
if cluster not in ['ai-infra','solutions','startup']: cluster='startup'

template=load_template(cluster)
letter=template.format(
    role=job['role'], company=job['company'],
    what_they_do_short=short_desc(job['what_they_do'])
)

outpath=f"/home/cheta/code/custom-skills/aaron-job-search/cover-letters/{job['company'].lower().replace(' ','-')}-{cluster}.md"
pathlib.Path(outpath).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(outpath).write_text(letter)

cur.execute("UPDATE jobs SET cover_letter_generated=1, status='ready' WHERE id=?", (args.job_id,))
cur.execute("INSERT INTO cover_letters (job_id, cluster, content, generated_at) VALUES (?, ?, ?, datetime('now'))", 
            (args.job_id, cluster, letter))
db.commit()
db.close()
print(f"Generated: {outpath}")
print(f"Cluster: {cluster}")
print(f"Job: {job['company']} — {job['role']}")
