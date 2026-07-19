# Agent bridge reference

## Preferred route

The local bridge invokes an authenticated Codex CLI session with `codex exec`, a workspace root, explicit sandbox, output schema, and result file. Saved CLI authentication is reused by Codex. The project never reads the authentication file.

Local apply mode uses workspace-write. Plan-only mode uses read-only. Do not bypass approvals and sandboxing unless the user explicitly configures an isolated environment and accepts the risk.

## Prompt shape

The bridge prompt should point to the change-request file and skill rather than embedding the full website. This keeps prompts small and lets the agent inspect the local workspace. The prompt must state:

- apply or plan-only mode;
- approved/rejected/deferred semantics;
- preferred target files;
- worklog and proposal requirements;
- credential exclusions;
- validation requirement;
- structured result requirement.

## Credentials

The browser never receives stored credentials after saving. Session secrets remain in server memory. Remembered secrets are encrypted at rest with a local AES-GCM key stored outside exports. Both files must be mode 0600 where supported.

Never place secrets in:

- localStorage;
- content JSON;
- change requests;
- annotations;
- worklogs;
- exported ZIPs;
- Codex prompts;
- terminal logs.

## Remote backends

A custom webhook receives the structured request through server-side fetch. An OpenAI Responses adapter may be used for a review or patch plan. Remote output is not trusted automatically. Review file paths, reject traversal, and stage replacements before applying.

Package modes:

- `request-json`: smallest and safest.
- `html`: rendered snapshot plus request.
- `zip`: full project without secrets and transient runs.

Use the smallest package that gives the remote model enough context.

## Failure recovery

If Codex is missing, report the exact PATH failure. If authentication is missing, recommend local device-code login or an API key for a trusted automation environment. If structured output fails, preserve stdout, stderr, and the request file. Do not claim files changed unless the workspace confirms it.

If an agent run partially edits files and fails validation, keep the run log, revert only with explicit authorization or version-control support, and report the inconsistent state precisely.
