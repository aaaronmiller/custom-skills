# Weekly Report Suite Self-Improvement Loop

After generating the dad report, personal report, and dashboard bundle, audit the workflow.

## 1. Evidence audit

Answer:

- Which evidence sources were used?
- Which sources failed or were stale?
- Did CASS return useful session data?
- Did filesystem/git evidence contradict the narrative?
- Which claims depend on user-provided input only?

## 2. Report quality audit

Dad report:

- Was it under the target length?
- Did it explain technical terms by function?
- Did it overclaim any designed/scaffolded work as shipped?
- Did it maintain the established tone?
- Did it avoid needless negativity?

Personal report:

- Did it preserve exact paths and caveats?
- Did it separate done, WIP, and planned work?
- Did it capture carry-over items?
- Would next week's agent understand the state?

## 3. Dashboard audit

- Which metrics were present?
- Which were estimated or missing?
- Which visualization was least useful?
- Which new graph would make the week easier to understand?
- Are Prometheus metric names stable?

## 4. Improvement candidates

Pick 1-3 concrete improvements for next week:

- Add a classifier for a recurring topic.
- Add a chart for carry-over closure rate.
- Improve CASS query keywords.
- Add a new Prometheus metric.
- Add per-project evidence confidence.
- Improve stale-project detection.
- Add manual correction fields to the JSON schema.

## 5. Where to write the audit

Write to the personal report under `## Self-Improvement Notes` and, if a dashboard bundle exists, to:

```text
/home/cheta/code/weekly-report-dashboard/YYYY-MM-DD/improvement-notes.md
```

Do not change the skill itself unless the user explicitly asks for a skill update.
