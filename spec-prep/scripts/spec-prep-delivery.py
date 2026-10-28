#!/usr/bin/env python3
"""Check compact input handoffs or native preparation; never launch implementation.

Usage: python3 spec-prep-delivery.py PACKAGE_ROOT [--manifest delivery.json]
The package manifest names each workstream, input trio, governance and next operation.
This checks structure, pointers, hashes and stop boundaries, not semantic completeness
or actual fresh-session loading. See references/artifact-contract.md for the schema.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import hashlib


def ready_text(path):
    text = path.read_text()
    if re.search(r'\[(?:[A-Z][A-Z0-9]*_[A-Z0-9_]+|PROJECT NAME|FEATURE NAME|FEATURE BRANCH|DATE|NEEDS CLARIFICATION[^\]]*)\]|\bTXXX\b', text):
        raise ValueError(f'unresolved template content: {path.name}')
    return text


def inspect_transitions(build):
    """Inspect executable command fields, never descriptions or inert workflow definitions.

    This is a conservative dependency-free subset reader, not a general YAML parser.
    Unknown/custom/multiline commands require a separate review rather than execution.
    """
    safe = {'speckit.constitution', 'speckit.specify', 'speckit.clarify', 'speckit.plan',
            'speckit.tasks', 'speckit.analyze', 'speckit.checklist', 'speckit.git.commit'}
    def check(command):
        command = command.strip().strip('\"\'')
        normalized = command.lstrip('/').replace('-', '.')
        if normalized not in safe:
            raise ValueError(f'automatic transition needs review or exclusion before preparation: {command}')
    for extension in ('extensions.yml', 'extensions.yaml'):
        path = build / '.specify' / extension
        if path.is_file():
            text = local(build, '.specify/' + extension).read_text()
            if re.search(r'(?m)^[ \t]*hooks[ \t]*:[ \t]*[^#\s]', text):
                raise ValueError('inline automatic transition configuration requires review')
            if re.search(r'(?m)^[ \t]*(?:before|after)_[A-Za-z_]+[ \t]*:[ \t]*[^#\s]|^[ \t]*-[ \t]*\{', text):
                raise ValueError('inline automatic transition records require review')
            for block in re.split(r'(?m)^\s*-\s+(?=[A-Za-z_]+\s*:)', text):
                if re.search(r'(?m)^\s*enabled\s*:\s*false\s*(?:#.*)?$', block):
                    continue
                for command in re.findall(r'(?m)^\s*(?:command|workflow)\s*:\s*(.*?)\s*(?:#.*)?$', block):
                    check(command)
    for name in ('.claude/settings.json', '.claude/settings.local.json'):
        if (build / name).is_file():
            config = json.loads(local(build, name).read_text())
            if not isinstance(config, dict):
                raise ValueError('harness transition settings must be an object')
            def visit(value):
                if isinstance(value, dict):
                    if 'type' in value and value['type'] != 'command':
                        raise ValueError('prompt/agent automatic transitions require review')
                    if 'command' in value:
                        if not isinstance(value['command'], str):
                            raise ValueError('harness transition command must be a string')
                        check(value['command'])
                    for item in value.values():
                        visit(item)
                elif isinstance(value, list):
                    for item in value:
                        visit(item)
            visit(config.get('hooks', {}))


def _launcher():
    spec = importlib.util.spec_from_file_location('spec_prep_launch', Path(__file__).with_name('spec-prep-launch.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local(root, name, directory=False):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError(f'expected a safe package-relative path: {name!r}')
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
        raise ValueError(f'unsafe path: {name}')
    for component in (path, *path.parents):
        if component == root:
            break
        if component.is_symlink():
            raise ValueError(f'unsafe symlinked path: {name}')
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'missing {"directory" if directory else "file"}: {name}')
    if not directory and not path.read_text().strip():
        raise ValueError(f'empty file: {name}')
    return path


def validate(root, manifest=None):
    root = Path(root).resolve()
    errors = []
    try:
        doc = manifest if manifest is not None else json.loads((root / 'delivery.json').read_text())
        if not isinstance(doc, dict) or doc.get('schemaVersion') != 1:
            raise ValueError('delivery must be a schemaVersion 1 object')
        operation = doc.get('operation')
        if operation not in ('input-handoff', 'native-preparation'):
            raise ValueError('operation must be input-handoff or native-preparation; standalone/intake use their declared gates')
        if doc.get('implementationAuthorized') is not False:
            raise ValueError('preparation delivery requires implementationAuthorized: false')
        streams = doc.get('workstreams')
        if not isinstance(streams, list) or not streams:
            raise ValueError('workstreams must be a nonempty array')
        ids, input_roots, build_roots = set(), set(), set()
        for stream in streams:
            try:
                if not isinstance(stream, dict):
                    raise ValueError('workstream must be an object')
                name = stream.get('id')
                if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in ids:
                    raise ValueError('workstream IDs must be unique kebab-case names')
                ids.add(name)
                build = local(root, stream.get('buildRoot'), True)
                inputs = local(root, stream.get('inputRoot'), True)
                if build.resolve() in build_roots:
                    raise ValueError('workstreams require distinct build roots')
                build_roots.add(build.resolve())
                if inputs.resolve() in input_roots:
                    raise ValueError('each workstream must have its own authoritative input trio')
                input_roots.add(inputs.resolve())
                roles = stream.get('inputs', {})
                if not isinstance(roles, dict) or set(roles) != {'requirements', 'design', 'intent'}:
                    raise ValueError('inputs must name exactly requirements, design and intent')
                for role, path in roles.items():
                    if path != role + '.md':
                        raise ValueError(f'core {role} must be the complete {role}.md entry document')
                    ready_text(local(inputs, path))
                extras = [p.name for p in inputs.iterdir() if p.is_file() and p.suffix == '.md' and p.name not in roles.values()]
                if extras:
                    raise ValueError('compact input root has fragmented extra Markdown; use a linked subordinate appendix: ' + ', '.join(extras))
                if inputs.resolve() != build.resolve():
                    for role in roles:
                        if (build / (role + '.md')).is_file():
                            raise ValueError(f'competing core authority at build root: {role}.md')
                if operation == 'input-handoff':
                    if any(p.name in ('spec.md', 'plan.md', 'tasks.md') for p in (build / 'specs').rglob('*.md')):
                        raise ValueError('input-handoff must not manufacture native spec/plan/tasks; preserve existing packs as source intake instead')
                source = stream.get('sourceMap')
                if not isinstance(source, str):
                    raise ValueError('sourceMap must point to the source-disposition section or file')
                source_path, _, fragment = source.partition('#')
                mapping = local(inputs, source_path)
                if not fragment:
                    raise ValueError('sourceMap requires an explicit disposition heading fragment')
                text = mapping.read_text()
                headings = list(re.finditer(r'^(#{1,6})\s+(.+?)\s*#*$', text, re.M))
                selected = None
                for i, match in enumerate(headings):
                    anchor = re.sub(r'[^\w\- ]', '', match.group(2).lower()).replace(' ', '-')
                    if fragment == anchor:
                        end = next((later.start() for later in headings[i + 1:]
                                    if len(later.group(1)) <= len(match.group(1))), len(text))
                        selected = text[match.end():end]
                        break
                if not selected or not selected.strip() or not re.search(r'(?i)preserv|incorporat|defer|reject|unavailable|unverified|changed|supersed', selected):
                    raise ValueError('sourceMap must identify a nonempty material source-disposition section')
                guide = local(build, stream.get('conversionGuide')).read_text()
                for token in ['requirements.md', 'intent.md', 'design.md', 'spec.md', 'constitution', 'specify', 'plan', 'tasks', 'analyze']:
                    if token not in guide:
                        raise ValueError(f'conversion guide must explicitly map {token}')
                governance = stream.get('governance', {})
                if not isinstance(governance, dict) or governance.get('constitution') != '.specify/memory/constitution.md' or governance.get('instructions') != 'AGENTS.md':
                    raise ValueError('governance requires the native constitution and AGENTS.md')
                ready_text(local(build, governance['constitution']))
                instructions = ready_text(local(build, governance['instructions']))
                handoff_path = governance.get('handoff')
                handoff = local(build, handoff_path).read_text()
                if governance['constitution'] not in instructions or handoff_path not in instructions:
                    raise ValueError('AGENTS.md must load the constitution and reset handoff')
                for pointer in (governance['constitution'], handoff_path):
                    lines = [line for line in instructions.splitlines() if pointer in line]
                    if not any(re.search(r'(?i)\b(read|load)\b', line) for line in lines) or any(re.search(r"(?i)\b(?:(?:never|do not|don't)\s+(?:read|load)|ignore\b)", line) for line in lines):
                        raise ValueError('AGENTS.md must positively require reading the constitution and handoff')
                for text, label in [(instructions, 'AGENTS.md'), (handoff, 'handoff'), (guide, 'conversion guide')]:
                    if re.search(r'(?i)\bimplementation\s+(?:is\s+)?authorized|\bstart building\b|\bimplement immediately\b', text):
                        raise ValueError(f'{label} contains conflicting implementation authorization')
                    if not re.search(r'(?i)(do not implement|implementation (?:is )?not authorized|stop before implementation|preparation.only)', text):
                        raise ValueError(f'{label} must state the preparation-only boundary')
                if governance.get('adapter'):
                    adapter = local(build, governance['adapter']).read_text()
                    if Path(governance['adapter']).name == 'CLAUDE.md' and not re.search(r'(?m)^\s*@AGENTS\.md\s*$', adapter):
                        raise ValueError('CLAUDE.md adapter requires an actual @AGENTS.md import')
                    if 'AGENTS.md' not in adapter:
                        raise ValueError('harness adapter must load AGENTS.md')
                inspect_transitions(build)
                expected_next = ('specification-preparation' if operation == 'input-handoff'
                                 else 'await-implementation-authorization')
                if stream.get('nextOperation') != expected_next:
                    raise ValueError(f'nextOperation must be {expected_next}')
                if operation == 'native-preparation':
                    feature_name = stream.get('featureRoot')
                    if not isinstance(feature_name, str) or len(Path(feature_name).parts) != 2 or Path(feature_name).parts[0] != 'specs':
                        raise ValueError('native featureRoot must be specs/<feature>')
                    feature = local(build, feature_name, True)
                    for filename in ('intent.md', 'spec.md', 'plan.md', 'tasks.md'):
                        ready_text(local(feature, filename))
                    if re.search(r'\[[xX]\]', (feature / 'tasks.md').read_text()):
                        raise ValueError('implementation tasks must remain unchecked after preparation')
                    tasks = (feature / 'tasks.md').read_text()
                    if not re.search(r'(?m)^\s*[-*]\s+\[ \]\s+T\d+\b', tasks) or not re.search(r'(?i)\b(gate|acceptance|verify|validation)\b', tasks):
                        raise ValueError('native tasks require identified unchecked work and observable acceptance gates')
                    receipt_path = local(build, stream.get('receipt'))
                    launcher = _launcher()
                    receipt = launcher.normalize_receipt(json.loads(receipt_path.read_text()))
                    if receipt.get('implementationAuthorized', receipt.get('initiationAuthorized')) is not False:
                        raise ValueError('receipt must explicitly forbid implementation at this handoff')
                    skill = receipt.get('skill', {})
                    if not isinstance(skill, dict) or not isinstance(skill.get('version'), str) or not re.fullmatch(r'[a-f0-9]{64}', str(skill.get('sha256', ''))):
                        raise ValueError('new native delivery receipt requires skill version and sha256 identity')
                    if skill['sha256'] != hashlib.sha256(Path(__file__).resolve().parents[1].joinpath('SKILL.md').read_bytes()).hexdigest():
                        raise ValueError('skill digest does not match this validator release; inspect the original skill snapshot with legacy receipt verification')
                    launcher.verify(build, receipt_path)
                    hashed = {item['path'] for item in receipt['artifacts'].values()}
                    hashed.update(item['path'] for item in receipt.get('artifactInventory', []))
                    consumed = [inputs / filename for filename in roles.values()]
                    consumed += [feature / 'intent.md', build / governance['instructions'], build / stream['conversionGuide'], mapping]
                    for name in ('standing.md', 'ledger.md', 'ledger/standing.md', 'ledger/ledger.md'):
                        if (feature / name).is_file():
                            consumed.append(feature / name)
                        if (build / name).is_file():
                            consumed.append(build / name)
                    if governance.get('adapter'):
                        consumed.append(build / governance['adapter'])
                    for target in consumed:
                        if not target.resolve().is_relative_to(build.resolve()):
                            raise ValueError('native delivery inputs must be preserved within its build root for receipt verification')
                        if target.relative_to(build).as_posix() not in hashed:
                            raise ValueError(f'consumed artifact is not hashed: {target.relative_to(build)}')
                    required = {'spec': feature / 'spec.md', 'plan': feature / 'plan.md',
                                'tasks': feature / 'tasks.md', 'constitution': build / governance['constitution'],
                                'handoff': build / handoff_path}
                    for role, target in required.items():
                        if (build / receipt['artifacts'][role]['path']).resolve() != target.resolve():
                            raise ValueError(f'receipt {role} points to a competing authority')
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
                errors.append(str(exc))
        return errors
    except (OSError, ValueError, TypeError) as exc:
        return [str(exc)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--manifest', default='delivery.json')
    args = parser.parse_args()
    try:
        doc = json.loads(local(args.folder.resolve(), args.manifest).read_text())
        errors = validate(args.folder, doc)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    print(json.dumps({'valid': not errors, 'errors': errors,
                      'scope': 'delivery structure and stop boundary; not proof of workflow execution, semantic completeness, evidence authenticity or runtime loading'}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
