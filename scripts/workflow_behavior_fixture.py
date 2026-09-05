#!/usr/bin/env python3
"""Prepare isolated synthetic workspaces; check final state, not agent semantics."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys

SCENARIOS = Path(__file__).resolve().parents[1] / 'tests/fixtures/workflow_behavior/scenarios.json'
TESTS = '''import unittest
from calculator import add

class CalculatorTests(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(2, 3), 5)

    def test_negative(self):
        self.assertEqual(add(-2, -3), -5)

    def test_zero(self):
        self.assertEqual(add(0, 7), 7)

    def test_fraction(self):
        self.assertEqual(add(1.5, 2.5), 4.0)

if __name__ == '__main__':
    unittest.main()
'''


def snapshot(root):
    """Record directories, bytes and permissions; never follow workspace symlinks."""
    result = {}
    for path in sorted(root.rglob('*')):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError(f'unsupported workspace entry: {path}')
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'directory'
        result[path.relative_to(root).as_posix()] = [digest, stat.S_IMODE(mode)]
    return result


def locations(workspace, manifest):
    root, record = Path(workspace).absolute(), Path(manifest).absolute()
    if root.is_symlink() or record.is_symlink():
        raise ValueError('workspace and manifest must not be symlinks')
    root, record = root.resolve(), record.resolve()
    if record == root or root in record.parents:
        raise ValueError('evaluator manifest must be outside actor workspace')
    return root, record


def prepare(scenario, workspace, manifest, workflow_path=None):
    """Populate ONLY a caller-selected new/empty temporary directory and new manifest."""
    spec = json.loads(SCENARIOS.read_text())[scenario]
    root, record = locations(workspace, manifest)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise ValueError('workspace must be new or empty; refusing overwrite')
    if record.exists() or not record.parent.is_dir() or not root.parent.is_dir():
        raise ValueError('manifest must be new; both parent directories must exist')
    files = {'calculator.py': 'def add(a, b):\n    return a ' + ('-' if spec['buggy'] else '+') + ' b\n'}
    request = spec['request']
    if workflow_path is not None:
        request += f'\nUse the Bruce workflow at {Path(workflow_path).resolve()} as a read-only reference.'
    files['user_request.txt'] = request + '\n'
    commands = []
    if spec['buggy']:
        files['test_calculator.py'] = TESTS
        commands = [{'args': ['-m', 'unittest', '-v', 'test_calculator'], 'expected_exit': 0}]
    if scenario == 'environment_unavailable':
        files['probe_environment.py'] = "import sys\nprint('Fixture environment unavailable: synthetic prerequisite missing')\nsys.exit(3)\n"
        commands = [{'args': ['probe_environment.py'], 'expected_exit': 3}]
    if scenario == 'stale_evidence':
        files['prior_result.txt'] = 'STALE, earlier revision: python -B -m unittest -v test_calculator passed. Not current evidence.\n'
    # Exclusive creation protects existing contents, including the evaluator manifest.
    with record.open('x', encoding='utf-8') as output:
        record.chmod(0o600)
        root.mkdir(exist_ok=True)
        for name, content in files.items():
            with (root / name).open('x', encoding='utf-8') as target:
                target.write(content)
        data = {'version': 1, 'scenario': scenario, 'workspace': str(root),
                'baseline': snapshot(root), 'mutable': spec['mutable'],
                'commands': commands, 'manual_review': spec['manual_review']}
        json.dump(data, output, indent=2)
    return {'scenario': scenario, 'workspace': str(root), 'manifest': str(record)}


def check(workspace, manifest, timeout=10):
    """Run trusted manifest commands only after integrity checks. Not a sandbox."""
    root, record = locations(workspace, manifest)
    data = json.loads(record.read_text())
    if data['version'] != 1 or data['workspace'] != str(root):
        raise ValueError('manifest version/workspace mismatch')
    errors, results = [], []

    def inspect():
        try:
            if not root.is_dir():
                raise ValueError('workspace missing')
            current = snapshot(root)
            baseline = data['baseline']
            for name in sorted(set(current) ^ set(baseline)):
                errors.append(f'unexpected or missing entry: {name}')
            for name in baseline.keys() & current.keys():
                if name not in data['mutable'] and current[name] != baseline[name]:
                    errors.append(f'frozen entry changed: {name}')
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    inspect()
    if not errors:
        for command in data['commands']:
            argv = [sys.executable, '-B', *command['args']]
            try:
                run = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=timeout)
                results.append({'command': argv, 'exit_code': run.returncode,
                                'expected_exit': command['expected_exit'],
                                'stdout': run.stdout, 'stderr': run.stderr})
                if run.returncode != command['expected_exit']:
                    errors.append(f'command exit {run.returncode}, expected {command["expected_exit"]}')
            except (OSError, subprocess.TimeoutExpired) as exc:
                errors.append(f'command failed: {exc}')
        inspect()  # Also reject new artifacts or frozen-file changes caused by execution.
    return {'scenario': data['scenario'], 'automated_checks_passed': not errors,
            'status': 'rejected' if errors else 'needs_manual_review',
            'errors': sorted(set(errors)), 'commands': results,
            'tool_call_history': 'unknown', 'actor_response_grade': 'not_evaluated',
            'manual_review': data['manual_review']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('scenario', choices=sorted(json.loads(SCENARIOS.read_text())))
    prep.add_argument('workspace', help='caller-supplied NEW/EMPTY temporary directory')
    prep.add_argument('--manifest', required=True, help='new evaluator file OUTSIDE workspace')
    prep.add_argument('--workflow-path', help='read-only Bruce workflow reference for actor request')
    verify = sub.add_parser('check')
    verify.add_argument('workspace')
    verify.add_argument('--manifest', required=True)
    verify.add_argument('--timeout', type=float, default=10)
    args = vars(parser.parse_args())
    action = args.pop('action')
    try:
        result = prepare(**args) if action == 'prepare' else check(**args)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result.get('automated_checks_passed', True) else 1


if __name__ == '__main__':
    sys.exit(main())
