#!/usr/bin/env python3
"""Customize resume for a specific job. Usage: customize_resume.py --job-id N --output /path/to/resume.md"""
import sqlite3, argparse, pathlib, re

parser=argparse.ArgumentParser()
parser.add_argument('--job-id', type=int, required=True)
parser.add_argument('--output', default=None)
args=parser.parse_args()

db=sqlite3.connect('/home/cheta/code/custom-skills/aaron-job-search/submissions.db')
db.row_factory=sqlite3.Row
j=db.execute("SELECT * FROM jobs WHERE id=?", (args.job_id,)).fetchone()
db.close()

if not j: print("Job not found"); exit(1)

# Select base resume
fork=(j['resume_fork'] or 'startup').replace('resume-','').replace('.md','')
if fork not in ['ai-infra','solutions','startup']: fork='startup'
base_resume=pathlib.Path(f"/home/cheta/code/custom-skills/aaron-job-search/notes/resume-{fork}.md")

if not base_resume.exists(): print(f"Base resume not found: {base_resume}"); exit(1)

content=base_resume.read_text()

# Customize: inject job-specific keywords into summary and target roles
role_keywords=(j['role']+' '+(j['what_they_do'] or '')).lower()
company=j['company']

# Find and customize target roles line
if '**Target Roles:**' in content:
    new_target=f"**Target Roles:** {j['role']} • {company}"
    content=content.replace(re.search(r'\*\*Target Roles:\*\*.*', content).group(), new_target)

# Find and customize availability
if '**Open to:**' in content:
    content=content.replace('**Open to:**', f'**Applying for:** {j["role"]} at {company}')

# Add job-specific line after professional summary
summary_end=content.find('---', content.find('## PROFESSIONAL EXPERIENCE'))
if summary_end>0:
    job_specific=f"\n**Tailored for:** {j['role']} at {company}. {j['what_they_do'][:150] if j['what_they_do'] else ''}\n\n"
    content=content[:summary_end]+job_specific+content[summary_end:]

# Output
if args.output:
    outpath=args.output
else:
    outpath=f"/home/cheta/code/custom-skills/aaron-job-search/resumes/{company.lower().replace(' ','-')}-{fork}.md"

pathlib.Path(outpath).parent.mkdir(parents=True, exist_ok=True)
pathlib.Path(outpath).write_text(content)
print(f"Customized: {outpath}")
print(f"Base: resume-{fork}.md")
print(f"Job: {company} — {j['role']}")
