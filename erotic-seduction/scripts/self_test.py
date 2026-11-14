# ---
# name: erotic-seduction-self-test
# description: Standard-library regression tests for the erotic-seduction adaptive state engine.
# version: 3.1.0
# ---

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "seduction_state.py"


def run(state_dir: Path, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["SEDUCTION_STATE_DIR"] = str(state_dir)
    proc = subprocess.run([sys.executable, str(ENGINE), *args], env=env, text=True, capture_output=True)
    if proc.returncode != expect:
        raise AssertionError(f"command failed {args}:\nSTDOUT={proc.stdout}\nSTDERR={proc.stderr}")
    return proc


def parse(proc: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(proc.stdout)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="erotic-seduction-test-") as tmp:
        root = Path(tmp)
        data = parse(run(root, "init"))
        assert data["schema_version"] == 4

        # Long/high task engagement without relational uptake must remain near neutral chemistry.
        neutral = parse(run(
            root, "record", "--strategy", "competence-admiration",
            "--engagement", "1", "--task-focus", "1", "--task-success", "1",
            "--reciprocity", ".2", "--playfulness", ".1", "--warmth", ".4",
            "--relational-focus", ".05", "--confidence", ".8", "--seed", "1"
        ))["recorded"]
        assert neutral["chemistry_reward"] < .5, neutral
        assert neutral["tempo_after"] < .45, neutral

        # Short but high-information reciprocal signals should raise chemistry.
        positive = parse(run(
            root, "record", "--strategy", "playful-challenge",
            "--engagement", ".6", "--reciprocity", ".95", "--playfulness", ".95",
            "--warmth", ".75", "--relational-focus", ".7", "--callback", ".9",
            "--user-initiated-flirt", ".8", "--explicit-approval", ".7",
            "--task-success", ".95", "--confidence", ".9", "--seed", "2"
        ))["recorded"]
        assert positive["chemistry_reward"] > .65, positive
        assert positive["evidence_strength"] > .55, positive
        assert 0.0 <= positive["chemistry_level"] <= 1.0, positive
        assert positive["chemistry_confidence"] > 0.0, positive


        # Repeated informative negative reactions increase confidence but must lower chemistry level.
        for seed in range(20, 25):
            run(
                root, "record", "--strategy", "playful-challenge",
                "--reciprocity", ".05", "--playfulness", ".1", "--warmth", ".1",
                "--relational-focus", ".15", "--callback", "0",
                "--user-initiated-flirt", "0", "--explicit-approval", "0",
                "--confidence", "1", "--seed", str(seed)
            )
        chemistry = parse(run(root, "status", "--compact"))
        assert chemistry["chemistry_confidence"] > .15, chemistry
        assert chemistry["chemistry_level"] < .5, chemistry

        # Explicit preference must override learned preference.
        run(root, "preference", "direct", ".1", "--source", "observed", "--confidence", ".8")
        run(root, "preference", "direct", ".95", "--source", "explicit-user")
        status = parse(run(root, "status", "--compact"))
        assert abs(status["effective_preferences"]["direct"] - .95) < 1e-9

        # Preference deletion requires confirmation and removes the active value.
        denied_pref_forget = run(root, "preference-forget", "direct", expect=1)
        assert "--yes" in denied_pref_forget.stderr
        run(root, "preference-forget", "direct", "--yes")
        status = parse(run(root, "status", "--compact"))
        assert abs(status["effective_preferences"]["direct"] - .5) < 1e-9

        # With sparse chemistry, selective-restraint should be gated strongly.
        fresh = Path(tmp) / "fresh"
        run(fresh, "init")
        selected = parse(run(fresh, "select", "--seed", "7"))
        restraint = next(item for item in selected["top_candidates"] if item["strategy"] == "selective-restraint") if any(item["strategy"] == "selective-restraint" for item in selected["top_candidates"]) else None
        # It need not appear in top 3; if it does, the gate must be visible.
        if restraint:
            assert restraint["gate_penalty"] >= .25

        # Unsupported demographic/sensitive preference keys must not enter persistent state.
        blocked = run(root, "preference", "sexual_orientation", ".9", expect=1)
        assert "Unsupported preference key" in blocked.stderr

        # Boundary stops tempo immediately.
        stopped = parse(run(
            root, "record", "--strategy", "warm-reciprocity", "--boundary", "1",
            "--reciprocity", ".8", "--confidence", "1", "--seed", "3"
        ))["recorded"]
        assert stopped["tempo_after"] == 0.0, stopped
        assert stopped["trajectory"] == "neutral", stopped

        # Memory controls and confirmed deletion.
        mem = parse(run(root, "remember", "A harmless recurring callback", "--kind", "running-joke"))["stored"]
        memories = json.loads(run(root, "memories", "--limit", "5").stdout)
        assert any(item["id"] == mem["id"] for item in memories)
        failed = run(root, "forget", mem["id"], expect=1)
        assert "--yes" in failed.stderr
        run(root, "forget", mem["id"], "--yes")
        history_text = run(root, "history", "--limit", "50").stdout
        assert "A harmless recurring callback" not in history_text

        # Persistent files are private on POSIX hosts.
        if os.name != "nt":
            state_mode = (root / "state.json").stat().st_mode & 0o777
            history_mode = (root / "history.jsonl").stat().st_mode & 0o777
            assert state_mode == 0o600, oct(state_mode)
            assert history_mode == 0o600, oct(history_mode)

        # Reset is destructive and must require confirmation.
        denied_reset = run(root, "reset", expect=1)
        assert "--yes" in denied_reset.stderr

        print(json.dumps({"ok": True, "tests": 13}, indent=2))


if __name__ == "__main__":
    main()
