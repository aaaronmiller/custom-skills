#!/usr/bin/env python3
"""Print submission status dashboard for all 100 jobs. Usage: submission_dashboard.py [--status pending|ready|submitted] [--cluster ai-infra|solutions|startup]"""
import sqlite3, argparse

parser=argparse.ArgumentParser()
parser.add_argument('--status', default=None)
parser.add_argument('--cluster', default=None)
args=parser.parse_args()

db=sqlite3.connect('/home/cheta/code/custom-skills/aaron-job-search/submissions.db')
db.row_factory=sqlite3.Row

query="SELECT * FROM jobs WHERE 1=1"
params=[]
if args.status: query+=" AND status=?"; params.append(args.status)
if args.cluster: query+=" AND resume_fork LIKE ?"; params.append(f'%{args.cluster}%')
query+=" ORDER BY rank"

jobs=db.execute(query, params).fetchall()

# Summary
total=len(jobs)
by_status={}
by_type={}
by_cluster={}
for j in jobs:
    s=j['status'] or 'pending'
    by_status[s]=by_status.get(s,0)+1
    t=j['submission_type'] or 'unclassified'
    by_type[t]=by_type.get(t,0)+1
    c=(j['resume_fork'] or 'unassigned').replace('resume-','').replace('.md','')
    by_cluster[c]=by_cluster.get(c,0)+1

print(f"=== SUBMISSION DASHBOARD ===")
print(f"Total jobs: {total}")
print(f"\nBy status: {dict(by_status)}")
print(f"\nBy submission type: {dict(by_type)}")
print(f"\nBy resume cluster: {dict(by_cluster)}")

# Ready to submit
ready=[j for j in jobs if j['status']=='ready']
if ready:
    print(f"\n=== READY TO SUBMIT ({len(ready)}) ===")
    for j in ready:
        print(f"  {j['rank']:3d} | {j['company'][:22]:22s} | {j['role'][:42]:42s} | {j['composite']:5.1f} | {j['submission_type'] or '?'}")

# Needs attention
needs=[j for j in jobs if j['status']=='pending' and not j['submission_type']]
if needs:
    print(f"\n=== NEEDS URL RESOLUTION ({len(needs)}) ===")
    for j in needs[:10]:
        print(f"  {j['rank']:3d} | {j['company'][:22]:22s} | {j['apply_url'][:60]}")
    if len(needs)>10: print(f"  ... and {len(needs)-10} more")

db.close()
