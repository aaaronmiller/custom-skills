#!/usr/bin/env python3
"""Write/check portable workbench pointers without preparing specs or initiating a build."""
import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path, PurePosixPath

MODES = ('auto', 'on', 'off')
ROLES = {
    'intent.md': 'intent', 'spec.md': 'spec', 'requirements.md': 'spec',
    'plan.md': 'plan', 'design.md': 'plan', 'context.md': 'context-rationale',
    'tasks.md': 'tasks', 'constitution.md': 'constitution',
    'agents.md': 'agent-instructions', 'claude.md': 'agent-instructions',
    'agent.md': 'agent-instructions', 'experience.md': 'experience',
    'traceability.md': 'traceability', 'source-map.md': 'source-map',
    'preparation.json': 'preparation-receipt', 'reset-handoff.md': 'reset-handoff',
    'research.md': 'research', 'research-notes.md': 'research',
    'data-model.md': 'data-model', 'quickstart.md': 'quickstart',
    'substrate.md': 'substrate', 'evals-location.md': 'eval-pointer',
    'standing.md': 'continuity', 'ledger.md': 'continuity',
}


def safe_file(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError('artifact path must be a nonempty relative POSIX path')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError(f'unsafe artifact path: {relative}')
    path = root / rel
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'missing or escaping artifact: {relative}')
    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f'symlinked artifact: {relative}')
        current = current.parent
    return path


def validate_workbench(root, doc):
    root = Path(root).resolve()
    try:
        if not isinstance(doc, dict):
            raise ValueError('workbench must be an object')
        if doc.get('schemaVersion') != 1 or doc.get('kind') != 'spec-prep-workbench':
            raise ValueError('expected schemaVersion 1 and kind spec-prep-workbench')
        if doc.get('intake') != 'project-intake.json':
            raise ValueError('intake must reference project-intake.json')
        safe_file(root, doc['intake'])
        if doc.get('mode') not in MODES or doc.get('additionalFiles') != 'discover':
            raise ValueError('invalid workbench mode or additionalFiles policy')
        ld = doc.get('integrations', {}).get('livingDocuments', {})
        if not isinstance(ld, dict) or ld.get('mode') not in MODES:
            raise ValueError('invalid Living Documents mode')
        if 'dossier' in ld and (not isinstance(ld['dossier'], str) or not ld['dossier'].strip()):
            raise ValueError('dossier must be a nonempty declared locator')
        build = None
        if 'buildRoot' in doc:
            if not isinstance(doc['buildRoot'], str) or not doc['buildRoot'].strip():
                raise ValueError('buildRoot must be a nonempty actual directory')
            raw = Path(doc['buildRoot']).expanduser()
            build = (root / raw).resolve() if not raw.is_absolute() else raw.resolve()
            if not build.is_dir():
                raise ValueError('declared buildRoot is unavailable')
        artifacts = doc.get('artifacts')
        if not isinstance(artifacts, list):
            raise ValueError('artifacts must be an array')
        seen = set()
        for item in artifacts:
            if not isinstance(item, dict) or not isinstance(item.get('role'), str) or not item['role'].strip():
                raise ValueError('artifact requires a nonempty role')
            if item.get('scope') not in ['intake', 'build'] or item.get('use') not in ['source', 'operational']:
                raise ValueError('invalid artifact scope or use')
            if item['scope'] == 'intake' and item['use'] != 'source':
                raise ValueError('intake artifacts are source pointers, not operational authority')
            base = root if item['scope'] == 'intake' else build
            if base is None:
                raise ValueError('build artifact requires a declared buildRoot')
            safe_file(base, item.get('path'))
            key = (item['scope'], item['path'])
            if key in seen:
                raise ValueError('duplicate artifact pointer')
            seen.add(key)
        return []
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        return [str(exc)]


def discover(root, scope):
    result = []
    for parent, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__', 'target', 'dist'] and not (Path(parent) / d).is_symlink())
        for name in sorted(names):
            p = Path(parent) / name
            if name.startswith('.') or p.is_symlink():
                continue
            rel = p.relative_to(root).as_posix()
            role = ROLES.get(name.lower())
            if 'checklists' in p.relative_to(root).parts and p.suffix.lower() == '.md':
                role = 'quality-checklist'
            elif 'contracts' in p.relative_to(root).parts:
                role = 'contract'
            elif 'plays' in p.relative_to(root).parts and p.suffix.lower() == '.md':
                role = 'playbook'
            if role:
                result.append({'role': role, 'scope': scope, 'path': rel, 'use': 'source' if scope == 'intake' else 'operational'})
    constitution = root / '.specify/memory/constitution.md'
    if constitution.is_file() and not constitution.is_symlink():
        result.append({'role': 'constitution', 'scope': scope, 'path': '.specify/memory/constitution.md', 'use': 'source' if scope == 'intake' else 'operational'})
    return result


def write_workbench(root, mode=None, ld_mode=None, build_root=None):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('intake folder does not exist')
    if mode == 'off':
        return {'operation': 'skipped', 'reason': 'workbench opted out; existing files untouched'}
    destination = root / 'workbench.json'
    doc = {}
    if destination.exists():
        safe_file(root, 'workbench.json')
        doc = json.loads(destination.read_text())
        errors = validate_workbench(root, doc)
        if errors:
            raise ValueError('existing workbench needs repair: ' + '; '.join(errors))
    resolved_mode = mode or doc.get('mode', 'auto')
    if resolved_mode == 'off':
        return {'operation': 'skipped', 'reason': 'existing workbench opted out; files untouched'}
    intake_spec = importlib.util.spec_from_file_location('spec-prep_intake', Path(__file__).with_name('spec-prep-intake.py'))
    intake = importlib.util.module_from_spec(intake_spec); intake_spec.loader.exec_module(intake)
    errors = intake.validate(root)
    if errors:
        raise ValueError('intake invalid: ' + '; '.join(errors))
    doc.update({'schemaVersion': 1, 'kind': 'spec-prep-workbench', 'intake': 'project-intake.json', 'mode': resolved_mode, 'additionalFiles': 'discover'})
    integrations = doc.setdefault('integrations', {})
    ld = integrations.setdefault('livingDocuments', {})
    ld['mode'] = ld_mode or ld.get('mode', 'auto')
    if build_root is not None:
        build = Path(build_root).expanduser().resolve()
        if not build.is_dir():
            raise ValueError('buildRoot must already exist')
        if doc.get('buildRoot'):
            old_raw = Path(doc['buildRoot']).expanduser()
            old_build = (root / old_raw).resolve() if not old_raw.is_absolute() else old_raw.resolve()
            if old_build != build:
                raise ValueError('existing buildRoot differs; review mappings before retargeting')
        doc['buildRoot'] = Path(os.path.relpath(build, root)).as_posix()
    artifacts = doc.setdefault('artifacts', [])
    seen = {(x['scope'], x['path']) for x in artifacts}
    discovered = discover(root, 'intake')
    if doc.get('buildRoot'):
        raw = Path(doc['buildRoot']).expanduser()
        build = (root / raw).resolve() if not raw.is_absolute() else raw.resolve()
        discovered += discover(build, 'build')
    for item in discovered:
        if (item['scope'], item['path']) not in seen:
            artifacts.append(item); seen.add((item['scope'], item['path']))
    errors = validate_workbench(root, doc)
    if errors:
        raise ValueError('; '.join(errors))
    serialized = json.dumps(doc, indent=2, ensure_ascii=False) + '\n'
    if destination.exists() and destination.read_text() == serialized:
        return {'operation': 'unchanged', 'path': str(destination), 'artifacts': len(artifacts)}
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=root, prefix='.workbench-', suffix='.tmp', delete=False) as stream:
        stream.write(serialized); stream.flush(); os.fsync(stream.fileno()); temporary = Path(stream.name)
    temporary.replace(destination)
    return {'operation': 'written', 'path': str(destination), 'artifacts': len(artifacts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['write', 'check'])
    parser.add_argument('folder', type=Path)
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--living-documents', choices=MODES)
    parser.add_argument('--build-root', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'write':
            result = write_workbench(args.folder, args.mode, args.living_documents, args.build_root)
        else:
            doc = json.loads((args.folder / 'workbench.json').read_text())
            errors = validate_workbench(args.folder, doc)
            result = {'valid': not errors, 'errors': errors}
            print(json.dumps(result, indent=2)); return 1 if errors else 0
        print(json.dumps(result, indent=2)); return 0
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps({'error': str(exc)})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
