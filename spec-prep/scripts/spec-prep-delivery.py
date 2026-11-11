#!/usr/bin/env python3
"""Check a spec-prep delivery package (delivery.json); never launch anything.

Usage: python3 spec-prep-delivery.py PACKAGE_ROOT [--manifest delivery.json]

The manifest names each workstream, its input trio, governance, optional priorArt,
supporting and reviewedHooks entries, and its next operation (schema:
references/artifact-contract.md, section "Delivery manifest and gate"). For
native-preparation it also verifies the preparation receipt: lifecycle, the five passed
gates with nonempty evidence (the validation gate also records the spec-prep-validate
command, exit status 0 and all nine per-check results), the artifact hashes and the
loaded SKILL.md digest. Output is JSON; exit 1 on any error.

Heading fragments (sourceMap, priorArt.record) match a heading's GitHub slug, ignoring a
leading section number, the same rule spec-prep-validate.py uses: '#prior-art' names
'## 10. Prior art'. Listed '[NEEDS CLARIFICATION: <question>]' markers are allowed in
inputs and native outputs; other template stubs, and a bare marker with no question, fail.

This checks structure, pointers, hashes and the stop boundary. It does not prove
workflow execution, semantic completeness, evidence authenticity or that a fresh
harness actually loads the instructions. PyYAML is needed only when a build root
contains .specify/extensions.yml.
"""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

SKILL_MD = Path(__file__).resolve().parents[1] / "SKILL.md"
SAFE_TRANSITIONS = {"speckit.constitution", "speckit.specify", "speckit.clarify", "speckit.plan",
                    "speckit.tasks", "speckit.analyze", "speckit.checklist", "speckit.git.commit"}
SUPPORTING_ROLES = {"analysis-input", "reference", "evidence", "fixture", "project-specific"}
PRIOR_ART_STATUSES = {"done", "directed", "waived"}
RECEIPT_ROLES = ("spec", "plan", "tasks", "constitution", "handoff")
RECEIPT_GATES = ("constitution", "prerequisites", "analysis", "traceability", "validation")
# The nine spec-prep-validate.py checks; the validation gate records each one's result.
VALIDATION_CHECKS = ("separation", "eval-binding", "testability", "identity", "drift",
                     "continuity", "honesty", "authorship", "prior-art")
# Template stubs. A clarification marker that states its question is a listed open item,
# not a stub; only the bare '[NEEDS CLARIFICATION]' with nothing after it is.
TEMPLATE_RE = re.compile(r"\[(?:[A-Z][A-Z0-9]*_[A-Z0-9_]+|PROJECT NAME|FEATURE NAME|FEATURE BRANCH|DATE|"
                         r"NEEDS CLARIFICATION\s*:?\s*)\]|\bTXXX\b")


def read(path):
    return path.read_text(encoding="utf-8")


def gh_slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def heading_matches(heading, fragment):
    """Same rule as spec-prep-validate.py: GitHub slug, leading section number ignored."""
    frag = fragment.strip().lower()
    unnumbered = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", heading.strip())
    return frag in (gh_slug(heading), gh_slug(unnumbered)) or re.sub(r"^\d+-", "", frag) == gh_slug(unnumbered)


def heading_section(text, fragment):
    heads = list(re.finditer(r"^(#{1,6})\s+(.+?)\s*#*\s*$", text, re.M))
    for i, m in enumerate(heads):
        if heading_matches(m.group(2), fragment):
            end = next((h.start() for h in heads[i + 1:] if len(h.group(1)) <= len(m.group(1))), len(text))
            return text[m.end():end]
    return None


def ready_text(path):
    text = read(path)
    if TEMPLATE_RE.search(text):
        raise ValueError(f"unresolved template content: {path.name}")
    return text


def local(root, name, directory=False):
    """A package-relative path that exists, stays inside root and crosses no symlink."""
    if not isinstance(name, str) or not name or Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError(f"expected a safe package-relative path: {name!r}")
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"unsafe path: {name}")
    for component in (path, *path.parents):
        if component == root:
            break
        if component.is_symlink():
            raise ValueError(f"unsafe symlinked path: {name}")
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'missing {"directory" if directory else "file"}: {name}')
    if not directory and not read(path).strip():
        raise ValueError(f"empty file: {name}")
    return path


def within(base, name, boundary):
    """A path relative to base (".." allowed) that must resolve inside boundary."""
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError(f"expected a relative path: {name!r}")
    path = (base / name).resolve()
    if not path.is_relative_to(boundary.resolve()):
        raise ValueError(f"path escapes the build root: {name}")
    if not path.exists():
        raise ValueError(f"missing supporting path: {name}")
    return path


def package_file(inputs, build, name):
    """A file named relative to inputRoot, else to buildRoot, that stays inside buildRoot."""
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError(f"expected a relative path: {name!r}")
    escaped = False
    for base in (inputs, build):
        path = (base / name).resolve()
        if not path.is_relative_to(build.resolve()):
            escaped = True
            continue
        if path.is_file():
            if any(c.is_symlink() for c in (base / name, *(base / name).parents) if c.is_relative_to(build)
                   and c != build):
                raise ValueError(f"unsafe symlinked path: {name}")
            if not read(path).strip():
                raise ValueError(f"empty file: {name}")
            return path
    raise ValueError(f"path escapes the build root: {name}" if escaped else f"missing file: {name}")


# ---------- receipts ----------

def checked_file(repo, name):
    if not isinstance(name, str) or not name:
        raise ValueError("receipt artifact path must be a nonempty relative string")
    p = Path(name)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("receipt artifact paths must be relative to the build root")
    target = repo / p
    if target.is_symlink() or not target.resolve().is_relative_to(repo.resolve()) or not target.is_file():
        raise ValueError(f"missing or unsafe preparation artifact: {name}")
    return target


def normalize_receipt(data):
    """Read older list-form receipts without mutating them; roles come only from unique names."""
    if not isinstance(data, dict):
        raise ValueError("receipt must be an object")
    result = copy.deepcopy(data)
    artifacts = result.get("artifacts", {})
    if isinstance(artifacts, list):
        names = {"spec": {"spec.md"}, "plan": {"plan.md"}, "tasks": {"tasks.md"},
                 "constitution": {"constitution.md"}, "handoff": {"reset-handoff.md"}}
        explicit = result.get("legacyRoleMap", {})
        if not isinstance(explicit, dict):
            raise ValueError("legacyRoleMap must be an object")
        mapped = {}
        for role, basenames in names.items():
            matches = [item for item in artifacts if isinstance(item, dict)
                       and isinstance(item.get("path"), str)
                       and (item["path"] == explicit[role] if role in explicit
                            else Path(item["path"]).name in basenames)]
            if len(matches) != 1:
                raise ValueError(f"legacy receipt requires an unambiguous {role} mapping; use legacyRoleMap")
            mapped[role] = matches[0]
        result["artifactInventory"] = artifacts
        result["artifacts"] = mapped
    elif not isinstance(artifacts, dict):
        raise ValueError("receipt artifacts must be a role-keyed object or a legacy array")
    gates = result.get("gates", {})
    if isinstance(gates, list):
        mapped = {}
        for gate in gates:
            if not isinstance(gate, dict) or not isinstance(gate.get("name"), str) or gate["name"] in mapped:
                raise ValueError("legacy gates require unique explicit names")
            mapped[gate["name"]] = gate
        result["gates"] = mapped
    elif not isinstance(gates, dict):
        raise ValueError("receipt gates must be an object or a legacy named array")
    return result


def verify_receipt(repo, data):
    if data.get("schemaVersion") != 1 or data.get("lifecycle") != "specification-prepared":
        raise ValueError("receipt must declare schemaVersion 1 and lifecycle specification-prepared")
    artifacts = data.get("artifacts", {})
    for role in RECEIPT_ROLES:
        if role not in artifacts:
            raise ValueError(f"missing preparation artifact role: {role}")
    inventory = data.get("artifactInventory", [])
    if not isinstance(inventory, list):
        raise ValueError("artifactInventory must be an array")
    for role, item in [*artifacts.items(), *[(f"inventory[{i}]", x) for i, x in enumerate(inventory)]]:
        if not isinstance(item, dict):
            raise ValueError(f"invalid receipt artifact: {role}")
        p = checked_file(repo, item.get("path", ""))
        if not item.get("sha256") or hashlib.sha256(p.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"preparation hash mismatch: {role}")
    gates = data.get("gates", {})
    for name in RECEIPT_GATES:
        gate = gates.get(name, {})
        if not isinstance(gate, dict) or gate.get("status") != "passed" or \
                not all(gate.get(k) for k in ("command", "observedAt", "evidence")):
            raise ValueError(f"missing passed gate evidence: {name}")
        evidence = gate["evidence"]
        for item in (evidence if isinstance(evidence, list) else [x.strip() for x in evidence.split(";")]):
            if not read(checked_file(repo, item)).strip():
                raise ValueError(f"empty gate evidence: {item}")
    verify_validation_gate(gates["validation"])


def verify_validation_gate(gate):
    """The nine-check result: the spec-prep-validate command, exit status 0, every check."""
    command = str(gate.get("command", ""))
    if "spec-prep-validate" not in command or "native-preparation" not in command:
        raise ValueError("validation gate command must be the spec-prep-validate.py run with "
                         "--operation native-preparation")
    if gate.get("exitStatus") != 0:
        raise ValueError("validation gate requires exitStatus 0 from spec-prep-validate.py")
    checks = gate.get("checks")
    if isinstance(checks, list):
        checks = {c.get("name"): c.get("status") for c in checks if isinstance(c, dict)}
    if not isinstance(checks, dict):
        raise ValueError("validation gate requires per-check results (checks)")
    missing = [n for n in VALIDATION_CHECKS if n not in checks]
    if missing:
        raise ValueError("validation gate lacks per-check results: " + ", ".join(missing))
    bad = [n for n in VALIDATION_CHECKS if checks[n] not in ("passed", "not_run")]
    if bad:
        raise ValueError("validation gate records a check that did not pass: " + ", ".join(bad))


# ---------- automatic transitions ----------

def reviewed_hooks(stream):
    """Commands a reviewer accepted for this build root: [{command, review}] in delivery.json."""
    entries = stream.get("reviewedHooks", [])
    if not isinstance(entries, list):
        raise ValueError("reviewedHooks must be an array")
    reviewed = set()
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("command"), str) or not item["command"].strip():
            raise ValueError("each reviewedHooks entry needs the hook's command text")
        note = item.get("review")
        if not isinstance(note, str) or not re.search(r"\w{2,}", note) or "\n" in note.strip():
            raise ValueError(f"reviewedHooks entry needs a one-line review note: {item['command']!r}")
        reviewed.add(item["command"].strip())
    return reviewed


def check_transition(command, reviewed=frozenset()):
    command = str(command).strip().strip("\"'")
    if command.lstrip("/").replace("-", ".") in SAFE_TRANSITIONS:
        return
    if re.search(r"(?i)implement", command):
        raise ValueError(f"automatic transition to implementation must be removed or disabled during "
                         f"preparation; review cannot admit it: {command}")
    if command not in reviewed:
        raise ValueError(f"automatic transition needs review (reviewedHooks) or exclusion before "
                         f"preparation: {command}")


def inspect_transitions(build, reviewed=frozenset()):
    """Inspect executable command fields, never descriptions or inert workflow definitions."""
    for extension in ("extensions.yml", "extensions.yaml"):
        if (build / ".specify" / extension).is_file():
            try:
                import yaml
            except ImportError as exc:
                raise ValueError(f".specify/{extension} needs PyYAML to inspect; install it or review "
                                 "its hooks by hand and record the review") from exc
            try:
                data = yaml.safe_load(read(local(build, ".specify/" + extension)))
            except yaml.YAMLError as exc:
                raise ValueError(f".specify/{extension} is not valid YAML: {exc}") from exc

            def visit(value):
                if isinstance(value, dict):
                    if value.get("enabled") is False:
                        return
                    for key in ("command", "workflow"):
                        if key in value and isinstance(value[key], (str, int, float)):
                            check_transition(value[key], reviewed)
                    for item in value.values():
                        visit(item)
                elif isinstance(value, list):
                    for item in value:
                        visit(item)
            visit(data.get("hooks", {}) if isinstance(data, dict) else {})
    for name in (".claude/settings.json", ".claude/settings.local.json"):
        if (build / name).is_file():
            config = json.loads(read(local(build, name)))
            if not isinstance(config, dict):
                raise ValueError("harness transition settings must be an object")

            def visit_hooks(value):
                if isinstance(value, dict):
                    if "type" in value and value["type"] != "command":
                        text = value.get("prompt") or value.get("agent") or ""
                        if not isinstance(text, str) or text.strip() not in reviewed:
                            raise ValueError("prompt or agent automatic transitions require review "
                                             "(list the prompt text in reviewedHooks)")
                    if "command" in value:
                        if not isinstance(value["command"], str):
                            raise ValueError("harness transition command must be a string")
                        check_transition(value["command"], reviewed)
                    for item in value.values():
                        visit_hooks(item)
                elif isinstance(value, list):
                    for item in value:
                        visit_hooks(item)
            visit_hooks(config.get("hooks", {}))


# ---------- additive fields ----------

def check_prior_art(stream, inputs, build, operation):
    prior = stream.get("priorArt")
    if prior is None:
        return
    if not isinstance(prior, dict) or prior.get("status") not in PRIOR_ART_STATUSES:
        raise ValueError("priorArt.status must be done, directed or waived")
    record = prior.get("record")
    if not isinstance(record, str) or not re.search(r"\w{2,}", record):
        raise ValueError("priorArt.record must name the record, the directive or the waiver reason")
    if prior["status"] == "directed" and operation == "native-preparation":
        raise ValueError("priorArt is only directed; plan and tasks wait until the record lands")
    if prior["status"] == "done":
        path, _, fragment = record.partition("#")
        if re.search(r"\.(?:md|json|txt)$", path):
            target = package_file(inputs, build, path)
            if fragment and heading_section(read(target), fragment) is None:
                raise ValueError(f"priorArt.record heading not found: {record}")


def check_supporting(stream, inputs, build, source_text):
    supporting = stream.get("supporting")
    if supporting is None:
        return
    if not isinstance(supporting, list):
        raise ValueError("supporting must be an array")
    for item in supporting:
        if not isinstance(item, dict):
            raise ValueError("each supporting entry must be an object")
        if item.get("role") not in SUPPORTING_ROLES:
            raise ValueError(f"supporting role must be one of {', '.join(sorted(SUPPORTING_ROLES))}: "
                             f"{item.get('path')!r}")
        if not isinstance(item.get("why"), str) or not item["why"].strip():
            raise ValueError(f"supporting entry needs a why: {item.get('path')!r}")
        target = within(inputs, item.get("path"), build)
        rel = target.relative_to(build.resolve()).as_posix()
        names = {item["path"], rel, *(p.as_posix() + "/" for p in Path(rel).parents if p.as_posix() != ".")}
        if not any(n in source_text for n in names):
            raise ValueError(f"supporting path is not declared in the source-disposition map: {item['path']}")


# ---------- validation ----------

def check_stream(root, stream, operation, ids, input_roots, build_roots):
    if not isinstance(stream, dict):
        raise ValueError("workstream must be an object")
    name = stream.get("id")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or name in ids:
        raise ValueError("workstream IDs must be unique kebab-case names")
    ids.add(name)
    build = local(root, stream.get("buildRoot"), True)
    inputs = local(root, stream.get("inputRoot"), True)
    if build.resolve() in build_roots:
        raise ValueError("workstreams require distinct build roots")
    build_roots.add(build.resolve())
    if inputs.resolve() in input_roots:
        raise ValueError("each workstream must have its own authoritative input trio")
    input_roots.add(inputs.resolve())
    roles = stream.get("inputs", {})
    if not isinstance(roles, dict) or set(roles) != {"requirements", "design", "intent"}:
        raise ValueError("inputs must name exactly requirements, design and intent")
    for role, path in roles.items():
        if path != role + ".md":
            raise ValueError(f"core {role} must be the complete {role}.md entry document")
        ready_text(local(inputs, path))
    # A README.md conversion or read-order guide may sit beside the trio; it is not an entry document.
    extras = [p.name for p in inputs.iterdir() if p.is_file() and p.suffix == ".md"
              and p.name not in roles.values() and p.name != "README.md"]
    if extras:
        raise ValueError("compact input root has fragmented extra Markdown; use a linked appendix: " + ", ".join(extras))
    if inputs.resolve() != build.resolve():
        for role in roles:
            if (build / (role + ".md")).is_file():
                raise ValueError(f"competing core authority at build root: {role}.md")
    if operation == "input-handoff" and (build / "specs").is_dir():
        if any(p.name in ("spec.md", "plan.md", "tasks.md") for p in (build / "specs").rglob("*.md")):
            raise ValueError("input-handoff must not manufacture native spec, plan or tasks")
    source = stream.get("sourceMap")
    if not isinstance(source, str):
        raise ValueError("sourceMap must point to the source-disposition section or file")
    source_path, _, fragment = source.partition("#")
    mapping = local(inputs, source_path)
    if not fragment:
        raise ValueError("sourceMap requires an explicit disposition heading fragment")
    selected = heading_section(read(mapping), fragment)
    if not selected or not re.search(r"(?i)preserv|incorporat|defer|reject|unavailable|unverified|changed|supersed",
                                     selected):
        raise ValueError("sourceMap must identify a nonempty material source-disposition section")
    guide = read(local(build, stream.get("conversionGuide")))
    for token in ("requirements.md", "intent.md", "design.md", "spec.md", "constitution",
                  "specify", "plan", "tasks", "analyze"):
        if token not in guide:
            raise ValueError(f"conversion guide must explicitly map {token}")
    governance = stream.get("governance", {})
    if not isinstance(governance, dict) or governance.get("constitution") != ".specify/memory/constitution.md" \
            or governance.get("instructions") != "AGENTS.md":
        raise ValueError("governance requires the native constitution and AGENTS.md")
    ready_text(local(build, governance["constitution"]))
    instructions = ready_text(local(build, governance["instructions"]))
    handoff_path = governance.get("handoff")
    handoff = read(local(build, handoff_path))
    if governance["constitution"] not in instructions or handoff_path not in instructions:
        raise ValueError("AGENTS.md must load the constitution and reset handoff")
    for pointer in (governance["constitution"], handoff_path):
        lines = [line for line in instructions.splitlines() if pointer in line]
        if not any(re.search(r"(?i)\b(read|load)\b", line) for line in lines) or \
                any(re.search(r"(?i)\b(?:(?:never|do not|don't)\s+(?:read|load)|ignore\b)", line) for line in lines):
            raise ValueError("AGENTS.md must positively require reading the constitution and handoff")
    for text, label in ((instructions, "AGENTS.md"), (handoff, "handoff"), (guide, "conversion guide")):
        if re.search(r"(?i)\bimplementation\s+(?:is\s+)?authorized|\bstart building\b|\bimplement immediately\b", text):
            raise ValueError(f"{label} contains conflicting implementation authorization")
        if not re.search(r"(?i)(do not implement|implementation (?:is )?not authorized|stop before implementation|"
                         r"preparation.only)", text):
            raise ValueError(f"{label} must state the preparation-only boundary")
    if governance.get("adapter"):
        adapter = read(local(build, governance["adapter"]))
        if Path(governance["adapter"]).name == "CLAUDE.md" and not re.search(r"(?m)^\s*@AGENTS\.md\s*$", adapter):
            raise ValueError("CLAUDE.md adapter requires an actual @AGENTS.md import")
        if "AGENTS.md" not in adapter:
            raise ValueError("harness adapter must load AGENTS.md")
    check_prior_art(stream, inputs, build, operation)
    check_supporting(stream, inputs, build, selected)
    inspect_transitions(build, reviewed_hooks(stream))
    expected_next = "specification-preparation" if operation == "input-handoff" else "await-implementation-authorization"
    if stream.get("nextOperation") != expected_next:
        raise ValueError(f"nextOperation must be {expected_next}")
    if operation == "native-preparation":
        check_native(stream, build, inputs, roles, governance, handoff_path, mapping)


def check_native(stream, build, inputs, roles, governance, handoff_path, mapping):
    feature_name = stream.get("featureRoot")
    if not isinstance(feature_name, str) or len(Path(feature_name).parts) != 2 or Path(feature_name).parts[0] != "specs":
        raise ValueError("native featureRoot must be specs/<feature>")
    feature = local(build, feature_name, True)
    for filename in ("intent.md", "spec.md", "plan.md", "tasks.md"):
        ready_text(local(feature, filename))
    tasks = read(feature / "tasks.md")
    if re.search(r"\[[xX]\]", tasks):
        raise ValueError("implementation tasks must remain unchecked after preparation")
    if not re.search(r"(?m)^\s*[-*]\s+\[ \]\s+T\d+\b", tasks) or \
            not re.search(r"(?i)\b(gate|acceptance|verify|validation)\b", tasks):
        raise ValueError("native tasks require identified unchecked work and observable acceptance gates")
    receipt_path = local(build, stream.get("receipt"))
    receipt = normalize_receipt(json.loads(read(receipt_path)))
    if receipt.get("implementationAuthorized", receipt.get("initiationAuthorized")) is not False:
        raise ValueError("receipt must explicitly forbid implementation at this handoff")
    skill = receipt.get("skill", {})
    if not isinstance(skill, dict) or not isinstance(skill.get("version"), str) or \
            not re.fullmatch(r"[a-f0-9]{64}", str(skill.get("sha256", ""))):
        raise ValueError("native receipt requires skill version and sha256 identity")
    if skill["sha256"] != hashlib.sha256(SKILL_MD.read_bytes()).hexdigest():
        raise ValueError(f"receipt skill digest differs from {SKILL_MD.name} beside this checker (receipt version "
                         f"{skill['version']}); check it with that release's checker or re-run preparation")
    verify_receipt(build, receipt)
    hashed = {item["path"] for item in receipt["artifacts"].values()}
    hashed.update(item["path"] for item in receipt.get("artifactInventory", []))
    consumed = [inputs / filename for filename in roles.values()]
    consumed += [feature / "intent.md", build / governance["instructions"], build / stream["conversionGuide"], mapping]
    for name in ("standing.md", "ledger.md", "ledger/standing.md", "ledger/ledger.md"):
        for base in (feature, build):
            if (base / name).is_file():
                consumed.append(base / name)
    if governance.get("adapter"):
        consumed.append(build / governance["adapter"])
    for target in consumed:
        if not target.resolve().is_relative_to(build.resolve()):
            raise ValueError("native delivery inputs must be preserved inside its build root for receipt verification")
        if target.resolve().relative_to(build.resolve()).as_posix() not in hashed:
            raise ValueError(f"consumed artifact is not hashed: {target.relative_to(build)}")
    required = {"spec": feature / "spec.md", "plan": feature / "plan.md", "tasks": feature / "tasks.md",
                "constitution": build / governance["constitution"], "handoff": build / handoff_path}
    for role, target in required.items():
        if (build / receipt["artifacts"][role]["path"]).resolve() != target.resolve():
            raise ValueError(f"receipt {role} points to a competing authority")


def validate(root, manifest=None):
    """Return a list of error strings; empty means the delivery passed."""
    root = Path(root).resolve()
    try:
        doc = manifest if manifest is not None else json.loads(read(root / "delivery.json"))
        if not isinstance(doc, dict) or doc.get("schemaVersion") != 1:
            raise ValueError("delivery must be a schemaVersion 1 object")
        operation = doc.get("operation")
        if operation not in ("input-handoff", "native-preparation"):
            raise ValueError("operation must be input-handoff or native-preparation")
        if doc.get("implementationAuthorized") is not False:
            raise ValueError("preparation delivery requires implementationAuthorized: false")
        streams = doc.get("workstreams")
        if not isinstance(streams, list) or not streams:
            raise ValueError("workstreams must be a nonempty array")
    except (OSError, ValueError, TypeError) as exc:
        return [str(exc)]
    errors, ids, input_roots, build_roots = [], set(), set(), set()
    for stream in streams:
        try:
            check_stream(root, stream, operation, ids, input_roots, build_roots)
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            label = stream.get("id") if isinstance(stream, dict) else "?"
            errors.append(f"{label}: {exc}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", type=Path, help="package root containing the manifest")
    parser.add_argument("--manifest", default="delivery.json", help="manifest path relative to the package root")
    args = parser.parse_args(argv)
    try:
        doc = json.loads(read(local(args.folder.resolve(), args.manifest)))
        errors = validate(args.folder, doc)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    print(json.dumps({"valid": not errors, "errors": errors,
                      "scope": "delivery structure, hashes and stop boundary; not proof of workflow execution, "
                               "semantic completeness, evidence authenticity or runtime loading"}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
