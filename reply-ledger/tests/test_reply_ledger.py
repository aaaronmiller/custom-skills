import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(tmp_path):
    os.environ["REPLY_LEDGER_DIR"] = str(tmp_path / "replies")
    spec = importlib.util.spec_from_file_location("reply_ledger", HERE.parent / "scripts" / "reply_ledger.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def line(**kw):
    return json.dumps(kw) + "\n"


def transcript(path, lines):
    with open(path, "a") as fh:
        fh.writelines(lines)


def test_capture_keeps_prompts_and_reply_text_only(tmp_path):
    rl = load(tmp_path)
    t = tmp_path / "s.jsonl"
    transcript(t, [
        line(type="user", timestamp="2026-11-07T22:00:00Z", uuid="u1", message={"content": "do the thing <system-reminder>x</system-reminder>"}),
        line(type="assistant", timestamp="2026-11-07T22:00:05Z", uuid="a1", message={"id": "m1", "content": [{"type": "thinking", "thinking": "secret"}, {"type": "text", "text": "Working on it."}]}),
        line(type="assistant", timestamp="2026-11-07T22:00:06Z", uuid="a2", message={"id": "m1", "content": [{"type": "tool_use", "name": "Bash", "input": {}}]}),
        line(type="user", timestamp="2026-11-07T22:00:07Z", uuid="u2", message={"content": [{"type": "tool_result", "content": "out"}]}),
        line(type="user", timestamp="2026-11-07T22:00:08Z", uuid="u3", isMeta=True, message={"content": "meta"}),
        line(type="assistant", timestamp="2026-11-07T22:00:09Z", uuid="a3", isSidechain=True, message={"content": [{"type": "text", "text": "subagent"}]}),
        line(type="assistant", timestamp="2026-11-07T22:01:00Z", uuid="a4", message={"id": "m2", "content": [{"type": "text", "text": "**DONE:** the thing\n\n| a | b |\n|---|---|\n| 1 | 2 |"}]}),
        line(type="user", timestamp="2026-11-07T22:02:00Z", uuid="u4", message={"content": "<task-notification>\n<summary>Job x finished</summary></task-notification>"}),
    ])
    assert rl.run(t, "s", "/w") == 4
    recs = [json.loads(l) for l in (rl.OUT / "s.jsonl").read_text().splitlines()]
    assert [r["role"] for r in recs] == ["user", "assistant", "assistant", "event"]
    assert recs[0]["text"] == "do the thing"
    assert recs[3]["text"] == "Job x finished"
    page = (rl.OUT / "s.html").read_text()
    assert "<table>" in page and "secret" not in page and "subagent" not in page
    assert "Background event: Job x finished" in page
    assert (rl.OUT / "index.html").exists()


def test_incremental_and_partial_last_line(tmp_path):
    rl = load(tmp_path)
    t = tmp_path / "s.jsonl"
    transcript(t, [line(type="user", timestamp="2026-11-07T22:00:00Z", message={"content": "one"})])
    assert rl.run(t, "s", "") == 1
    with open(t, "a") as fh:  # a half-written line must wait for its newline
        fh.write('{"type": "assistant", "message": {"content": [{"type": "text", "text": "two"}]}')
    assert rl.run(t, "s", "") == 0
    with open(t, "a") as fh:
        fh.write("}\n")
    assert rl.run(t, "s", "") == 1
    assert rl.run(t, "s", "") == 0


def test_html_in_replies_is_escaped(tmp_path):
    rl = load(tmp_path)
    t = tmp_path / "s.jsonl"
    transcript(t, [line(type="user", timestamp="2026-11-07T22:00:00Z", message={"content": "<b>hi</b>"}),
                   line(type="assistant", timestamp="2026-11-07T22:00:01Z", message={"content": [{"type": "text", "text": "a <script>alert(1)</script> b"}]})])
    rl.run(t, "s", "")
    page = (rl.OUT / "s.html").read_text()
    assert "<script>alert(1)" not in page and "&lt;script&gt;" in page


def test_hook_never_fails(tmp_path, monkeypatch):
    rl = load(tmp_path)
    monkeypatch.setattr(sys, "argv", ["reply_ledger.py", "--hook"])
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO("not json"))
    assert rl.main() == 0
    assert "Traceback" in (rl.STATE / "errors.log").read_text()
