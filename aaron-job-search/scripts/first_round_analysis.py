#!/usr/bin/env python3
"""Analyze first-round pass optimization for all 100 jobs. Identifies ATS keywords, referral needs, and application strategy."""
import sqlite3, json

db=sqlite3.connect('/home/cheta/code/custom-skills/aaron-job-search/submissions.db')
db.row_factory=sqlite3.Row

jobs=db.execute("SELECT * FROM jobs ORDER BY rank").fetchall()

# ATS keyword analysis per job
# Common ATS filters: keyword matching, years of experience, education, location
ats_keywords={
    'greenhouse': ['python','javascript','typescript','react','node','aws','docker','kubernetes','ci/cd','git','agile','sql','api','rest','microservices','linux'],
    'ashby': ['python','javascript','typescript','react','node','aws','docker','kubernetes','ci/cd','git','agile','sql','api','rest','microservices','linux'],
    'workday': ['python','javascript','typescript','react','node','aws','docker','kubernetes','ci/cd','git','agile','sql','api','rest','microservices','linux'],
}

# First-round pass factors
analysis=[]
for j in jobs:
    score=0
    factors=[]
    
    # 1. ATS keyword match (30% weight)
    role_text=(j['role']+' '+j['what_they_do']).lower()
    matched_kw=sum(1 for kw in ats_keywords.get('greenhouse',[]) if kw in role_text)
    kw_score=min(matched_kw/5*30, 30)
    score+=kw_score
    if matched_kw>=3: factors.append(f"Strong keyword match ({matched_kw})")
    
    # 2. Location match (15% weight)
    loc=(j['location'] or '').lower()
    if 'seattle' in loc: score+=15; factors.append("Seattle location")
    elif 'remote' in loc: score+=12; factors.append("Remote-eligible")
    elif 'hybrid' in loc: score+=10; factors.append("Hybrid")
    
    # 3. Experience level match (20% weight)
    yoe_text=role_text
    if 'senior' in yoe_text or 'sr.' in yoe_text: score+=15; factors.append("Senior level match")
    elif 'staff' in yoe_text or 'principal' in yoe_text: score+=10; factors.append("Staff level (stretch)")
    elif 'junior' in yoe_text or 'entry' in yoe_text: score+=5; factors.append("Junior level (overshoot)")
    
    # 4. Company size fit (10% weight)
    size=j['company_size'] or ''
    if '1-10' in size or '11-50' in size: score+=10; factors.append("Small startup (strong fit)")
    elif '51-200' in size: score+=8; factors.append("Growth-stage")
    elif '201-500' in size: score+=6; factors.append("Mid-size")
    elif '500+' in size or '1000' in size: score+=4; factors.append("Large company")
    
    # 5. Composite score bonus (15% weight)
    composite=j['composite'] or 0
    if composite>=55: score+=15; factors.append("Top composite")
    elif composite>=50: score+=12; factors.append("High composite")
    elif composite>=45: score+=8; factors.append("Medium composite")
    
    # 6. Submission method ease (10% weight)
    submit=j['submission_type'] or ''
    if submit in ['greenhouse','ashby','workday','custom_form']: 
        score+=10; factors.append("Direct ATS (easy submit)")
    elif submit=='manual_redirect': score+=5; factors.append("Redirect (needs navigation)")
    
    grade='S' if score>=80 else 'A' if score>=65 else 'B' if score>=50 else 'C' if score>=35 else 'D'
    
    analysis.append({
        'rank': j['rank'], 'company': j['company'], 'role': j['role'],
        'first_round_score': score, 'grade': grade, 'factors': factors,
        'composite': composite, 'submit_type': submit, 'ats': j['ats_platform']
    })

analysis.sort(key=lambda x: -x['first_round_score'])

# Save analysis
with open('/home/cheta/code/custom-skills/aaron-job-search/first-round-analysis.json','w') as f:
    json.dump(analysis, f, indent=2)

# Print top 20
print("=== FIRST-ROUND PASS PROBABILITY (Top 20) ===")
for a in analysis[:20]:
    print(f"  {a['grade']} {a['first_round_score']:3d} | #{a['rank']:2d} {a['company'][:20]:20s} | {a['role'][:42]} | {', '.join(a['factors'][:2])}")

# Strategy summary
print(f"\n=== STRATEGY SUMMARY ===")
s_count=sum(1 for a in analysis if a['grade']=='S')
a_count=sum(1 for a in analysis if a['grade']=='A')
b_count=sum(1 for a in analysis if a['grade']=='B')
print(f"S-grade (likely pass): {s_count}")
print(f"A-grade (good shot): {a_count}")
print(f"B-grade (competitive): {b_count}")
print(f"\n=== TOP COMPANIES BY FIRST-ROUND SCORE ===")
# Group by company
from collections import defaultdict
by_company=defaultdict(list)
for a in analysis:
    by_company[a['company']].append(a)
for comp, items in sorted(by_company.items(), key=lambda x: -max(i['first_round_score'] for i in x[1])):
    best=max(items, key=lambda x: x['first_round_score'])
    if best['first_round_score']>=50:
        print(f"  {comp[:25]:25s} best={best['first_round_score']} ({best['grade']}) | {len(items)} roles")

db.close()
