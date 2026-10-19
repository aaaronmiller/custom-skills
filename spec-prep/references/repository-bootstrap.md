---
title: Optional repository bootstrap
version: "2.2.0"
tags: [spec-prep, git, licensing, onboarding]
---

# Optional repository bootstrap

When preparing specifications, inspect the selected build directory before creating anything. Skip each item already completed. A supplied repository is the target; never create a second repository just because it lacks one optional file.

Resolve project name, description, local build path, license, ignore rules and hosting separately. Derive the name and description from explicit intake metadata when clear. If the user requested repository setup and the directory is not in a Git repository, initialize locally with git init --initial-branch=main <build-path>. Detect parent repositories first; do not create an unintended nested repository. Preserve existing branch and remote settings. Do not commit, push or rewrite history as an incidental setup step.

For a new local repository, record its human-readable description in .git/description and its project name and purpose in README.md. Preserve an existing README and existing meaningful description; add only missing information. Local repository naming comes from the chosen directory. Do not rename a preexisting directory to match a inferred label.

If LICENSE already exists, inspect and retain it. If an explicit SPDX license choice exists, obtain the standard license text from its official source and use the authorized copyright holder and year. If ownership or license choice is ambiguous, ask a targeted question; the safe default is no licensing declaration. Do not silently choose a permissive license, or copy another project's license. A request to stage intake does not require answering license questions yet.

Generate or extend .gitignore using the derived stack and current primary templates, preserving existing rules. Cover generated outputs, dependency caches, local environment/credential files, machine state and private fixtures appropriate to this project. Do not ignore source contracts, lockfiles or spec artifacts indiscriminately. Verify representative rules with git check-ignore --no-index, and inspect git status so necessary files remain trackable.

Remote hosting is optional and separate from local initialization. If requested, resolve provider, account/organization, repository name, description, visibility and license before creation. A remote repository creation or first push is a publishing action: the current request must authorize its exact target. Ask only when that target or visibility is ambiguous. Never infer a public repository or transmit source code from local setup authority.

Record completed/skipped choices and local verification in the preparation handoff. Repository creation does not initiate implementation.
