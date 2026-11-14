# custom-skills

Aaron's agent skills: 45 skills, deployed to every harness by skillshare.

Cleaned on 2026-11-14: duplicates and one-off "skills" removed, every description cut to one to three sentences. What went and why: `docs/2026-11-14-skill-cull.md`.

## Layout

- One folder per skill, each with a `SKILL.md`.
- Skills with their own GitHub repo are symlinks: `create-viral-content`, `deliberative-refinement`, `frontend-design-masterclass`, `hallmark`, `humanize-writing`, `living-documents`, `ui-ux-doctor`. Edit them in their own repo.
- `docs/` holds per-skill notes, the cull record and packaging guides. `sources/` holds absorbed older material kept as records; nothing there is deployed.

## Deploy

```bash
skillshare update <skill> && skillshare sync
```

## Skills

| Skill | What it does |
|---|---|
| `aaron-job-search` | Runs Aaron's Seattle job hunt, small startups first: searches the job boards, scores each role on fit, income and odds, and logs it to the submission tracker. Use when asked to find, rank or log jobs. |
| `agy-headless-driver` | Delegates judgment-heavy work to headless Antigravity CLI sessions: splits it into units, builds a context pack and prompt for each, launches and paces them against agy's quota, then verifies the output. |
| `assignment-librarian` | Keeps the new_assignments library in Living Documents indexed: finds new folders, onboards idea drops into intake manifests, and triages which are ready for spec-prep. |
| `black-magic` | The intent-first loop for project work: tidy the folder, bring its intent record current, then answer open questions from the record across all projects before calling anything blocked. Use when working a punchlist or about to report a blocker. |
| `browser` | Scrapes and drives websites with local CLIs, escalating from Obscura to Camoufox to Interceptor as a site fights bots. Use to read pages, scrape, check prices or fill forms. |
| `bypass-paywall` | Finds a complete, readable copy of a paywalled or failed article through author links, archives and reader services, and checks it is whole before using it. |
| `capacity-watch` | Reads the remaining quota of every paid and free model pool, grades the free models we can reach, and says where the next agent should run. |
| `casr` | Converts a session from one coding agent into another (omp, Codex, Gemini, Claude Code and more) so it can be resumed there. |
| `cass-cli` | Searches past agent sessions from every harness with cass to recover what was said, decided or tried. Use for prior-work lookup, intent recovery and session forensics. |
| `cli-tui-styling` | Makes terminal output look good: colour roles, hierarchy, tables, borders, icons and the right library per language. Use when building or styling a CLI or TUI. |
| `competition-analysis` | Researches a competitor (a product, company or person) and files a dossier with screenshots, accounts, the builders' track record and ideas for our own projects. |
| `create-viral-content` | Writes and sharpens social posts, threads, titles, hooks and scripts so they spread and read as human. Use for any public-facing post, title or caption. |
| `deep-research` | Researches a question across many web sources and writes a cited report, from a quick survey to an exhaustive one. Use when an answer needs several sources and searches. |
| `deliberative-refinement` | Tests a decision, claim or plan through rounds of adversarial debate among several perspectives before committing to it. Use for high-stakes choices, comparing options or validating a claim. |
| `erotic-seduction` | Adaptive, non-explicit flirtation for adult users who ask an agent to flirt or take on a romantic persona, learning their preferences from how they respond while keeping any task on track. |
| `frontend-design-masterclass` | Designs and builds distinctive web pages, UI and HTML output. |
| `game-mechanics-design` | A twelve-pillar framework for designing fun, balanced game mechanics, drawn from Magic: The Gathering, tabletop RPGs, video games and sports. Use when designing or reviewing game rules and systems. |
| `git-audit-sync` | Audits every git repo under a folder and brings each current with its remote, doing only safe fast-forwards and pushes itself and flagging the rest. Use to sync many repos or find uncommitted work. |
| `hallmark` | Opt-in design skill: use ONLY when the user names Hallmark (as in `/hallmark <prompt>`, `/hallmark redesign <path>` or `/hallmark audit <path>`). Never trigger it on a generic request to build or design a page; frontend-design-masterclass owns those, and its Visual Floor outranks Hallmark's restraint rules. |
| `harness-config-audit` | Checks an agent harness's config against its current build so features added in updates are actually switched on, and holds the model-assignment policy. Use after upgrading a harness or when a documented feature does nothing. |
| `humanize-writing` | Rewrites AI-sounding prose in a natural human voice. Use on substantial prose before it ships, or when writing reads as robotic or corporate. |
| `imagegen` | Generates or edits images headlessly with no API keys, through Codex's image tool or the Antigravity CLI. Use for icons, banners, illustrations and placeholder art. |
| `intent-organizer` | Declutters folders such as Downloads or Desktop by working out why each item is there, then gives the owner a short approval page with full undo. Removes only superseded, duplicate or temporary items. |
| `intent-refresh` | Brings the intent record current: collects operator prompts from every harness since the last run, cleans them, ties sessions to projects, derives intents for intent-find and writes each dossier's intent pages. Runs weekly from cron. |
| `living-documents` | Maintains the Living Documents planning system under ~/LIVING_DOCUMENTS: project dossiers, decisions, evidence and task state for long-running work. Use when starting, resuming or recording substantial work. |
| `make-it-funny` | Writes satire and comedy (cartoon panels, articles, jokes, video scripts) aimed at institutions, and scores whether a piece lands with a comedy-expert council. |
| `mcp-toolkit` | Builds MCP servers in Python or TypeScript, or converts an existing MCP server into a CLI, script or skill. |
| `motion-lab` | Directs studio-quality motion design as code (HTML, CSS, SVG, Canvas, three.js) and renders it frame-exact to GIF or MP4. Use for animations, loops, logo stings and product shots. |
| `notes-sweeper` | Monthly recovery of unsaved Notepad and Notepad++ tabs into durable project files and a searchable note library. |
| `portfolio-lineage` | Compares an old project version clause by clause against its successor and blocks archiving while anything unique has no new home. Use to pick the canonical version or check a folder is safe to archive. |
| `project-archive` | Archives a project folder safely: mines and indexes it, checks what depends on it, moves and links it, and tests recovery. |
| `proven-better-new` | Tests an app, product or business idea against what already exists, with mandatory prior-art research, and returns a validation card. Use when asked whether an idea is worth building. |
| `refinement-loop` | Improves a draft through repeated generate, critique and revise passes until it meets a rubric score. Use when work should get better over several passes rather than one. |
| `reply-ledger` | Captures every Claude Code reply into navigable HTML pages in Living Documents through a Stop hook. Use to find, reread or backfill past replies. |
| `rules-file-optimizer` | Merges and compresses a CLAUDE.md, AGENTS.md or system prompt that has grown too long to be followed, measuring compliance before and after. |
| `session-cleanup` | Closes out a long agent session: finishes small loose ends, writes handoff docs for big ones, and checks every touched repo is committed and pushed. Also surveys all running sessions. |
| `skill-audit` | Audits skills for structure, duplicates, broken references, description quality and cross-platform portability, and fixes what it finds. Use when reviewing, cleaning up or uploading skills. |
| `skill-doctor` | Grades skills from real conversation history (efficiency, code quality, procedure compliance, verbosity) and drafts concrete edits. Use to see which skills work and why one did not fire. |
| `skillranker` | Asks the sr CLI which installed skill fits the next step of the current session. Use when unsure which skill applies. |
| `spec-audit` | Checks spec-driven work for drift by rebuilding intent from a downstream artifact and comparing it with its source. Use to ask whether the code, plan or tasks still match the spec. |
| `spec-prep` | Prepares project intent, requirements, design and Spec Kit specs, plans and tasks, stopping before implementation. Use for project intake, spec updates or intent recovery. |
| `system-checkup` | Runs the periodic full checkup of this Windows 11 and WSL2 workstation (updates, memory, crashes, storage, outdated software) and produces a cleanup plan with an approval page. |
| `ui-ux-doctor` | Audits an existing interface for usability, accessibility and visual problems, then fixes them. Use to review, improve or redesign a UI. |
| `weekly-report-suite` | Writes the weekly progress report for Aaron's dad or mentor, plus a fuller personal report and HTML dashboard, from the week's project history. |
| `yt-transcript-artifact` | Turns a YouTube video or transcript into a structured Obsidian note with forensic extraction and analysis. |
