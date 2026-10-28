#!/usr/bin/env python3
"""Validate staged evidence without authoring specifications or initiating a project."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def local_file(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError(f"expected a relative file path: {value!r}")
    if '..' in Path(value).parts:
        raise ValueError(f"path traversal is forbidden: {value!r}")
    path = root / value
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes the intake folder: {value!r}")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"missing or symlinked input: {value!r}")
    return path


def validate(root, manifest=None):
    root = Path(root).resolve()
    errors = []
    try:
        m = manifest if manifest is not None else json.loads((root / 'project-intake.json').read_text())
        if not isinstance(m, dict):
            raise ValueError('manifest must be an object')
        if m.get('schemaVersion') != 1:
            errors.append('schemaVersion must be 1')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', str(m.get('projectId', ''))):
            errors.append('projectId must be kebab-case')
        for key in ['title', 'summary', 'nextOperation']:
            if not isinstance(m.get(key), str) or not m[key].strip():
                errors.append(f'{key} must be a nonempty string')
        if m.get('lifecycle') not in ['staged', 'input-handoff-ready', 'specification-reviewed-incomplete', 'specification-prepared', 'initiated']:
            errors.append('invalid lifecycle')
        if m.get('assignment') not in ['unassigned', 'assigned', 'tooling']:
            errors.append('invalid assignment')
        for key in ['sources', 'readOrder', 'issues', 'relatedProjects', 'externalResources']:
            if not isinstance(m.get(key), list):
                errors.append(f'{key} must be an array')
        seen = set()
        for source in m.get('sources', []) if isinstance(m.get('sources'), list) else []:
            if not isinstance(source, dict):
                errors.append('each source must be an object')
                continue
            try:
                path = local_file(root, source.get('path'))
                if source['path'] in seen:
                    errors.append(f"duplicate source: {source['path']}")
                seen.add(source['path'])
                if not all(isinstance(source.get(k), str) and source[k] for k in ['format', 'role']):
                    errors.append(f"source lacks format or role: {source['path']}")
                if source.get('sha256') and hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
                    errors.append(f"source hash mismatch: {source['path']}")
            except (OSError, ValueError, TypeError) as exc:
                errors.append(str(exc))
        for name in m.get('readOrder', []) if isinstance(m.get('readOrder'), list) else []:
            try:
                local_file(root, name)
            except (OSError, ValueError, TypeError) as exc:
                errors.append(str(exc))
        if not m.get('readOrder'):
            errors.append('readOrder must name at least one file')
        for item in m.get('issues', []) if isinstance(m.get('issues'), list) else []:
            if not isinstance(item, dict) or item.get('severity') not in ['info', 'conversion', 'missing-input'] or not isinstance(item.get('detail'), str):
                errors.append('issues require severity and detail')
        for item in m.get('externalResources', []) if isinstance(m.get('externalResources'), list) else []:
            if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k] for k in ['path', 'role', 'handling']):
                errors.append('externalResources require path, role and handling')
        return errors
    except (OSError, ValueError, TypeError) as exc:
        return [str(exc)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    errors = validate(args.folder)
    print(json.dumps({'valid': not errors, 'folder': str(args.folder.resolve()), 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
