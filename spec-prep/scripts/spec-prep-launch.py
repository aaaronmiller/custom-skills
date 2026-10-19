#!/usr/bin/env python3
"""Preview a terminal-agnostic fresh harness launch; execution requires verified preparation."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def argv_json(raw, label):
    value = json.loads(raw)
    if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
        raise ValueError(f'{label} must be a nonempty JSON array of strings')
    return value


def checked_file(repo, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('receipt artifact paths must be relative to the build root')
    target = repo / p
    if target.is_symlink() or not target.resolve().is_relative_to(repo) or not target.is_file():
        raise ValueError(f'missing or unsafe preparation artifact: {name}')
    return target


def verify(repo, receipt):
    data = json.loads(receipt.read_text())
    if data.get('schemaVersion') != 1 or data.get('lifecycle') != 'specification-prepared':
        raise ValueError('receipt must declare schemaVersion 1 and lifecycle specification-prepared')
    artifacts = data.get('artifacts', {})
    for role in ['spec', 'plan', 'tasks', 'constitution', 'handoff']:
        item = artifacts.get(role, {})
        p = checked_file(repo, item.get('path', ''))
        if not item.get('sha256') or hashlib.sha256(p.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'preparation hash mismatch: {role}')
    gates = data.get('gates', {})
    for name in ['constitution', 'prerequisites', 'analysis', 'traceability']:
        gate = gates.get(name, {})
        if gate.get('status') != 'passed' or not all(gate.get(k) for k in ['command', 'observedAt', 'evidence']):
            raise ValueError(f'missing passed gate evidence: {name}')
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
    args = parser.parse_args()
    try:
        repo = args.repo.expanduser().resolve()
        if not repo.is_dir():
            raise ValueError('build root does not exist')
        receipt = args.receipt.expanduser().resolve()
        handoff = verify(repo, receipt)
        harness = argv_json(args.harness_command, 'harness-command')
        if harness.count('{prompt}') != 1:
            raise ValueError('harness-command requires one standalone {prompt} argument')
        if any(x in ['resume', '--resume', 'continue', '--continue'] for x in harness[1:]):
            raise ValueError('fresh initiation cannot resume or continue an existing harness session')
        prompt = f'Read {handoff}. This is a fresh implementation session. Verify the preparation receipt and build root {repo}; record a fresh-session acknowledgement with the consumed handoff hash and next authorized task, then initiate that task within the handoff scope.'
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
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
