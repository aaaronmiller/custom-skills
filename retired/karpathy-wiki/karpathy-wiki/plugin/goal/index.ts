/**
 * /goal command — Ralph loop with judge, deliberative refinement, adversarial mode
 *
 * Usage:
 *   /goal <task> [max_iterations] [refinement_freq] [adversarial]
 *
 * Examples:
 *   /goal "fix the failing auth tests"
 *   /goal "fix the failing auth tests" 20
 *   /goal "fix the failing auth tests" 20 5
 *   /goal "fix the failing auth tests" 20 3 adversarial
 *
 * Sub-commands:
 *   /goal status     — Show current goal state
 *   /goal pause      — Pause the current goal
 *   /goal resume     — Resume the current goal
 *   /goal clear      — Clear the current goal
 *   /goal cancel     — Cancel the current goal
 *
 * Dependencies: @lnilluv/pi-ralph-loop (npm package), pi-agent-suite (npm package)
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

interface GoalConfig {
  task: string;
  maxIterations: number;
  refinementFreq: number;
  adversarial: boolean;
}

function parseGoalArgs(raw: string): GoalConfig {
  const parts = raw.trim().split(/\s+/);
  const config: GoalConfig = {
    task: raw,
    maxIterations: 20,
    refinementFreq: 3,
    adversarial: false,
  };

  const last = parts[parts.length - 1];
  if (last?.toLowerCase() === "adversarial") {
    config.adversarial = true;
    parts.pop();
  }

  const lastNum = parts[parts.length - 1];
  const penultNum = parts[parts.length - 2];
  const lastNumVal = parseInt(lastNum);
  const penultNumVal = parseInt(penultNum);

  if (!isNaN(lastNumVal) && isNaN(penultNumVal)) {
    config.maxIterations = lastNumVal;
    parts.pop();
  } else if (!isNaN(lastNumVal) && !isNaN(penultNumVal)) {
    config.maxIterations = penultNumVal;
    config.refinementFreq = lastNumVal;
    parts.pop();
    parts.pop();
  }

  config.task = parts.join(" ");
  return config;
}

export default function (pi: ExtensionAPI) {
  pi.registerCommand({
    name: "goal",
    description: "Set a persistent goal with autonomous iteration loop",
    usage: '/goal <task> [max_iterations] [refinement_freq] [adversarial]',
    handler: async (args: string, ctx) => {
      const trimmed = args?.trim() || "";
      if (!trimmed) {
        ctx.ui.notify("Usage: /goal <task> [max_iterations] [refinement_freq] [adversarial]", "info");
        return;
      }

      const subCmd = trimmed.split(/\s+/)[0]?.toLowerCase();
      if (["status", "pause", "resume", "clear", "cancel"].includes(subCmd)) {
        const subArgs = trimmed.slice(subCmd.length).trim();
        const piCmds = (pi as any).commands;
        if (piCmds?.execute) {
          await piCmds.execute(`/ralph-${subCmd} ${subArgs}`, ctx);
        } else {
          ctx.ui.notify(`Goal ${subCmd} — delegates to ralph loop`, "info");
        }
        return;
      }

      const config = parseGoalArgs(trimmed);
      const taskDir = `.goal/${Date.now()}`;

      let yamlFrontmatter = `---\nmax_iterations: ${config.maxIterations}\ntimeout: 300\ncommands:\n  - name: tests\n    run: echo "checking completion"\n    timeout: 60\n`;

      if (config.adversarial) {
        yamlFrontmatter += `guardrails:\n  block_commands:\n    - 'git\\s+push'\n  protected_files:\n    - '.env*'\n`;
        yamlFrontmatter += `adversarial_review: true\n`;
      }

      yamlFrontmatter += `refinement_freq: ${config.refinementFreq}\ncompletion_promise: DONE\n---\n\n`;
      yamlFrontmatter += `# Goal\n\n${config.task}\n\nStop with <promise>DONE</promise> when achieved.\n`;

      const fs = await import("node:fs");
      const path = await import("node:path");
      const cwd = ctx.cwd || process.cwd();
      const goalDir = path.join(cwd, taskDir);
      fs.mkdirSync(goalDir, { recursive: true });
      fs.writeFileSync(path.join(goalDir, "RALPH.md"), yamlFrontmatter, "utf8");

      ctx.ui.notify(
        `⊙ Goal set (${config.maxIterations}-turn budget, refine every ${config.refinementFreq} turns${config.adversarial ? ", adversarial mode" : ""}): ${config.task}`,
        "info"
      );
      ctx.ui.notify(`→ Run /ralph --path ${taskDir} to start the loop`, "info");
    },
  });
}
