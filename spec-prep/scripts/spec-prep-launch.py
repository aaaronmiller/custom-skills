#!/usr/bin/env python3
"""Preview a terminal-agnostic fresh harness launch; execution requires verified preparation."""
import argparse
import hashlib
import json
import shutil
import subprocess
import copy
from pathlib import Path


def argv_json(raw, label):
    value = json.loads(raw)
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f'{label} must be a nonempty JSON array of strings')
    return value


def checked_file(repo, name):
    if not isinstance(name, str) or not name:
        raise ValueError('receipt artifact path must be a nonempty relative string')
    p = Path(name)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('receipt artifact paths must be relative to the build root')
    target = repo / p
    if target.is_symlink() or not target.resolve().is_relative_to(repo) or not target.is_file():
        raise ValueError(f'missing or unsafe preparation artifact: {name}')
    return target


def normalize_receipt(data):
    """Read legacy receipts without mutation, inferring roles only from unique filenames."""
    if not isinstance(data, dict):
        raise ValueError('receipt must be an object')
    result = copy.deepcopy(data)
    artifacts = result.get('artifacts', {})
    if isinstance(artifacts, list):
        names = {'spec': {'spec.md'}, 'plan': {'plan.md'}, 'tasks': {'tasks.md'},
                 'constitution': {'constitution.md'}, 'handoff': {'reset-handoff.md'}}
        explicit = result.get('legacyRoleMap', {})
        if not isinstance(explicit, dict):
            raise ValueError('legacyRoleMap must be an object')
        mapped = {}
        for role, basenames in names.items():
            matches = [item for item in artifacts if isinstance(item, dict)
                       and isinstance(item.get('path'), str)
                       and (item['path'] == explicit[role] if role in explicit
                            else Path(item['path']).name in basenames)]
            if len(matches) != 1:
                raise ValueError(f'legacy receipt requires unambiguous {role} mapping; use legacyRoleMap')
            mapped[role] = matches[0]
        result['artifactInventory'] = artifacts
        result['artifacts'] = mapped
    elif not isinstance(artifacts, dict):
        raise ValueError('receipt artifacts must be a role-keyed object or legacy inventory array')
    gates = result.get('gates', {})
    if isinstance(gates, list):
        mapped = {}
        for gate in gates:
            if not isinstance(gate, dict) or not isinstance(gate.get('name'), str) or gate['name'] in mapped:
                raise ValueError('legacy gates require unique explicit names')
            mapped[gate['name']] = gate
        result['gates'] = mapped
    elif not isinstance(gates, dict):
        raise ValueError('receipt gates must be an object or legacy named array')
    return result


def verify(repo, receipt):
    repo = repo.resolve()
    data = normalize_receipt(json.loads(receipt.read_text()))
    if data.get('schemaVersion') != 1 or data.get('lifecycle') != 'specification-prepared':
        raise ValueError('receipt must declare schemaVersion 1 and lifecycle specification-prepared')
    artifacts = data.get('artifacts', {})
    for role in ['spec', 'plan', 'tasks', 'constitution', 'handoff']:
        if role not in artifacts:
            raise ValueError(f'missing preparation artifact role: {role}')
    inventory = data.get('artifactInventory', [])
    if not isinstance(inventory, list):
        raise ValueError('artifactInventory must be an array')
    for role, item in [*artifacts.items(), *[(f'inventory[{i}]', item) for i, item in enumerate(inventory)]]:
        if not isinstance(item, dict):
            raise ValueError(f'invalid receipt artifact: {role}')
        p = checked_file(repo, item.get('path', ''))
        if not item.get('sha256') or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'preparation hash mismatch: {role}')
    gates = data.get('gates', {})
    for name in ['constitution', 'prerequisites', 'analysis', 'traceability']:
        gate = gates.get(name, {})
        if not isinstance(gate, dict) or gate.get('status') != 'passed' or not all(gate.get(k) for k in ['command', 'observedAt', 'evidence']):
            raise ValueError(f'missing passed gate evidence: {name}')
        evidence = gate['evidence']
        paths = evidence if isinstance(evidence, list) else [x.strip() for x in evidence.split(';')]
        for name in paths:
            target = checked_file(repo, name)
            if not target.read_text().strip():
                raise ValueError(f'empty gate evidence: {name}')
    return checked_file(repo, artifacts['handoff']['path'])


def launch_argv(terminal, binary, repo, harness, custom=None, wsl=None):
    cwd = str(repo)
    if wsl:
        harness = ['wsl.exe', '--distribution', wsl, '--cd', cwd, '--exec', *harness]
    if terminal == 'wezterm':
        return [binary, 'cli', 'spawn', *([] if wsl else ['--cwd', cwd]), '--', *harness]
    if terminal == 'wt':
        return [binary, '--window', '0', 'new-tab', *([] if wsl else ['--startingDirectory', cwd]), *harness]
    if terminal == 'gnome-terminal':
        return [binary, '--tab', '--working-directory', cwd, '--', *harness]
    if terminal == 'kitty':
        return [binary, '@', 'launch', '--type=tab', '--cwd', cwd, '--', *harness]
    if terminal == 'tmux':
        return [binary, 'new-window', '-c', cwd, '--', *harness]
    if terminal == 'custom':
        if not custom or custom.count('{command}') != 1:
            raise ValueError('custom terminal argv requires exactly one standalone {command} token')
        result = []
        for arg in custom:
            result.extend(harness if arg == '{command}' else [arg.replace('{cwd}', cwd)])
        return result
    raise ValueError(f'unknown terminal adapter: {terminal}')


def verify_launch_authority(repo, receipt, handoff, authority_path):
    """Record a real current user launch instruction separately from preparation.

    This is an auditable scope/digest check, not authentication of the human author.
    The agent writes it from existing user authority; it is not a new approval ritual.
    """
    if authority_path is None:
        raise ValueError('execute requires a separate --launch-authority record; preparation is not launch authority')
    authority = json.loads(Path(authority_path).read_text())
    if not isinstance(authority, dict) or authority.get('schemaVersion') != 1 or authority.get('operation') != 'project-initiation':
        raise ValueError('invalid project-initiation authority record')
    if authority.get('source') != 'user' or not all(isinstance(authority.get(k), str) and authority[k].strip() for k in ('userInstruction', 'authorizedAt', 'buildRoot')):
        raise ValueError('launch authority must record the actual user instruction, time and exact root')
    if Path(authority['buildRoot']).resolve() != repo.resolve():
        raise ValueError('launch authority names a different project root')
    for key, path in [('receiptSha256', receipt), ('handoffSha256', handoff)]:
        if authority.get(key) != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('launch authority is stale or refers to a different prepared handoff')
    return authority


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--terminal', choices=['wezterm', 'wt', 'gnome-terminal', 'kitty', 'tmux', 'custom'], required=True)
    parser.add_argument('--terminal-binary')
    parser.add_argument('--terminal-command', help='JSON argv; standalone {command} expands the harness argv')
    parser.add_argument('--harness-command', required=True, help='JSON argv with one standalone {prompt} argument')
    parser.add_argument('--wsl-distro')
    parser.add_argument('--execute', action='store_true', help='Use only with current authorization to initiate this project')
    parser.add_argument('--launch-authority', type=Path, help='Separate record of the real user launch instruction and exact receipt/handoff digests; required by --execute')
    args = parser.parse_args()
    try:
        repo = args.repo.expanduser().resolve()
        if not repo.is_dir():
            raise ValueError('build root does not exist')
        receipt = args.receipt.expanduser().resolve()
        handoff = verify(repo, receipt)
        if args.execute:
            verify_launch_authority(repo, receipt, handoff, args.launch_authority)
        harness = argv_json(args.harness_command, 'harness-command')
        if harness.count('{prompt}') != 1:
            raise ValueError('harness-command requires one standalone {prompt} argument')
        if any(x in ['resume', '--resume', 'continue', '--continue'] for x in harness[1:]):
            raise ValueError('fresh initiation cannot resume or continue an existing harness session')
        prompt = f'Read AGENTS.md, .specify/memory/constitution.md and {handoff}. Verify the preparation receipt and build root {repo}. Preparation alone does not authorize implementation. '
        if args.execute:
            prompt += f'Read the separately authorized launch record {args.launch_authority.resolve()}; record a fresh-session acknowledgement with the consumed handoff hash and next authorized task, then initiate only that task within the actual user authority.'
        else:
            prompt += 'This is a preview only. Do not implement or launch without a later explicit user instruction and a matching launch-authority record.'
        harness = [prompt if x == '{prompt}' else x for x in harness]
        custom = argv_json(args.terminal_command, 'terminal-command') if args.terminal_command else None
        binary = args.terminal_binary or args.terminal
        command = launch_argv(args.terminal, binary, repo, harness, custom, args.wsl_distro)
        result = {'operation': 'project-initiation', 'mode': 'execute' if args.execute else 'preview', 'cwd': str(repo), 'argv': command, 'handoff': str(handoff)}
        if args.execute:
            if not shutil.which(command[0]) and not Path(command[0]).is_file():
                raise ValueError(f'terminal executable unavailable: {command[0]}')
            completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
            result.update({'transportStatus': 'spawn-command-succeeded', 'terminalResult': completed.stdout.strip(), 'initiation': 'unverified-until-fresh-session-acknowledgement'})
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
