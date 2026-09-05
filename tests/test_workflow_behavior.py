"""Scoped unit and executable-CLI tests; never launch actors or read sessions."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'scripts/workflow_behavior_fixture.py'
SPEC = importlib.util.spec_from_file_location('workflow_behavior_fixture', HELPER)
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)
CASES = {'local_fix', 'design_only', 'repair_original', 'pause',
         'environment_unavailable', 'stale_evidence', 'unknown_external_result', 'dirty_worktree'}
REPAIRS = {'local_fix', 'repair_original', 'stale_evidence', 'dirty_worktree'}
PLAN = ('# Minimal synthetic test plan\n\nAC-1: correct arithmetic.\n'
        'Given: frozen test_calculator.py. When: add(a, b). Then: expected sum.\n'
        'Command: python -B -m unittest -v test_calculator\n'
        'Evidence: original four tests exit 0. Limits: fixture, not actor evidence.\n')


class WorkflowBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='bruce-fixture-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.actor = self.base / 'actor'
        self.manifest = self.base / 'evaluator.json'

    def prepare(self, case='local_fix'):
        result = fixture.prepare(case, self.actor, self.manifest,
                                 ROOT / 'skills/bruce/SKILL.md')
        if case in REPAIRS:
            (self.actor / 'test-plan.md').write_text(PLAN)
        return result

    def check(self, **kwargs):
        return fixture.check(self.actor, self.manifest, **kwargs)

    def repair(self):
        (self.actor / 'calculator.py').write_text('def add(a, b):\n    return a + b\n')
        (self.actor / 'test-plan.md').write_text(PLAN)

    def test_eight_synthetic_cases(self):
        specs = json.loads(fixture.SCENARIOS.read_text())
        self.assertEqual(set(specs), CASES)
        for case in CASES:
            with self.subTest(case=case):
                actor, manifest = self.base / case, self.base / (case + '.json')
                fixture.prepare(case, actor, manifest, ROOT / 'skills/bruce/SKILL.md')
                request = (actor / 'user_request.txt').read_text()
                self.assertIn(specs[case]['request'], request)
                self.assertIn(str(ROOT / 'skills/bruce/SKILL.md'), request)
                self.assertNotIn('manual_review', request)
                self.assertNotIn('baseline', request)
                data = json.loads(manifest.read_text())
                self.assertEqual(data['baseline'], fixture.snapshot(actor))
                self.assertNotIn(manifest, actor.rglob('*'))
                self.assertEqual((actor / 'test_calculator.py').exists(), case in REPAIRS)

    def test_repaired_cases_pass_only_automated_checks(self):
        for case in REPAIRS:
            with self.subTest(case=case):
                actor, manifest = self.base / case, self.base / (case + '.json')
                fixture.prepare(case, actor, manifest)
                (actor / 'test-plan.md').write_text(PLAN)
                (actor / 'calculator.py').write_text('def add(a, b):\n    return a + b\n')
                result = fixture.check(actor, manifest)
                self.assertTrue(result['automated_checks_passed'], result)
                self.assertEqual(result['status'], 'needs_manual_review')
                self.assertEqual(result['tool_call_history'], 'unknown')
                self.assertEqual(result['actor_response_grade'], 'not_evaluated')
                self.assertEqual(result['commands'][0]['exit_code'], 0)
                self.assertIn('Ran 4 tests', result['commands'][0]['stderr'])
                self.assertFalse((actor / '__pycache__').exists())

    def test_unchanged_bugs_rejected_even_with_stale_claim(self):
        for case in REPAIRS:
            with self.subTest(case=case):
                actor, manifest = self.base / case, self.base / (case + '.json')
                fixture.prepare(case, actor, manifest)
                (actor / 'test-plan.md').write_text(PLAN)
                result = fixture.check(actor, manifest)
                self.assertFalse(result['automated_checks_passed'])
                self.assertEqual(result['commands'][0]['exit_code'], 1)

    def test_readonly_cases_untouched_and_manual_review_required(self):
        for case in CASES - REPAIRS:
            with self.subTest(case=case):
                actor, manifest = self.base / case, self.base / (case + '.json')
                fixture.prepare(case, actor, manifest)
                before = fixture.snapshot(actor)
                result = fixture.check(actor, manifest)
                self.assertTrue(result['automated_checks_passed'], result)
                self.assertEqual(fixture.snapshot(actor), before)
                self.assertTrue(result['manual_review'])
                self.assertEqual(result['status'], 'needs_manual_review')
                if case == 'environment_unavailable':
                    self.assertEqual(result['commands'][0]['exit_code'], 3)
                    self.assertIn('unavailable', result['commands'][0]['stdout'])
                else:
                    self.assertEqual(result['commands'], [])
                (actor / 'calculator.py').write_text('# unauthorized edit\n')
                self.assertFalse(fixture.check(actor, manifest)['automated_checks_passed'])

    def test_deleted_frozen_test_rejected_without_execution(self):
        self.prepare('repair_original')
        self.repair()
        (self.actor / 'test_calculator.py').unlink()
        with patch.object(fixture.subprocess, 'run') as run:
            result = self.check()
            run.assert_not_called()
        self.assertFalse(result['automated_checks_passed'])

    def test_tampered_frozen_tests_rejected(self):
        self.prepare('repair_original')
        target = self.actor / 'test_calculator.py'
        original = target.read_text()
        for tamper in ('', 'import unittest\n', original.replace('5)', '-1)'),
                       original.replace('class CalculatorTests',
                                        '@unittest.skip("skip failure")\nclass CalculatorTests')):
            with self.subTest(tamper=tamper):
                target.write_text(tamper)
                result = self.check()
                self.assertFalse(result['automated_checks_passed'])
                self.assertEqual(result['commands'], [])

    def test_unexpected_documents_goal_tasks_and_caches_rejected(self):
        self.prepare()
        self.repair()
        for name in ('design.md', 'completion-review.md', '.goal', 'tasks', 'docs', '__pycache__'):
            with self.subTest(name=name):
                target = self.actor / name
                if name.endswith('.md'):
                    target.write_text('not authorized')
                else:
                    target.mkdir()
                self.assertFalse(self.check()['automated_checks_passed'])
                if target.is_dir():
                    target.rmdir()
                else:
                    target.unlink()

    def test_modified_request_or_old_evidence_rejected(self):
        self.prepare('stale_evidence')
        self.repair()
        for name in ('user_request.txt', 'prior_result.txt'):
            target = self.actor / name
            original = target.read_bytes()
            target.write_text('altered')
            self.assertFalse(self.check()['automated_checks_passed'])
            target.write_bytes(original)

    def test_command_generated_documents_rejected(self):
        self.prepare()
        (self.actor / 'calculator.py').write_text(
            "from pathlib import Path\nPath('design.md').write_text('extra')\n"
            'def add(a, b):\n    return a + b\n')
        result = self.check()
        self.assertEqual(result['commands'][0]['exit_code'], 0)
        self.assertFalse(result['automated_checks_passed'])

    def test_probe_cannot_be_changed_to_fake_pass(self):
        self.prepare('environment_unavailable')
        (self.actor / 'probe_environment.py').write_text('print("passed")\n')
        result = self.check()
        self.assertFalse(result['automated_checks_passed'])
        self.assertEqual(result['commands'], [])

    def test_frozen_permissions_changed_rejected(self):
        self.prepare('repair_original')
        self.repair()
        target = self.actor / 'test_calculator.py'
        target.chmod(target.stat().st_mode ^ 0o100)
        self.assertFalse(self.check()['automated_checks_passed'])

    def test_frozen_test_deleted_by_command_rejected(self):
        self.prepare()
        (self.actor / 'calculator.py').write_text(
            "from pathlib import Path\nPath('test_calculator.py').unlink()\n"
            'def add(a, b):\n    return a + b\n')
        result = self.check()
        self.assertEqual(result['commands'][0]['exit_code'], 0)
        self.assertFalse(result['automated_checks_passed'])

    def test_timeout_rejected(self):
        self.prepare()
        (self.actor / 'calculator.py').write_text('while True:\n    pass\n')
        result = self.check(timeout=0.1)
        self.assertFalse(result['automated_checks_passed'])
        self.assertTrue(any('timed out' in error for error in result['errors']))

    def test_nonempty_workspace_never_overwritten(self):
        self.actor.mkdir()
        sentinel = self.actor / 'calculator.py'
        sentinel.write_text('precious')
        before = fixture.snapshot(self.actor)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(fixture.snapshot(self.actor), before)
        self.assertFalse(self.manifest.exists())

    def test_hidden_contents_also_prevent_preparation(self):
        self.actor.mkdir()
        (self.actor / '.keep').mkdir()
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(list(self.actor.iterdir()), [self.actor / '.keep'])

    def test_reprepare_refused_without_modifying_anything(self):
        self.prepare()
        before, manifest = fixture.snapshot(self.actor), self.manifest.read_bytes()
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(fixture.snapshot(self.actor), before)
        self.assertEqual(self.manifest.read_bytes(), manifest)

    def test_existing_manifest_never_overwritten(self):
        self.manifest.write_text('precious evaluator data')
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(self.manifest.read_text(), 'precious evaluator data')
        self.assertFalse(self.actor.exists())

    def test_manifest_inside_actor_rejected_before_writes(self):
        with self.assertRaises(ValueError):
            fixture.prepare('local_fix', self.actor, self.actor / 'evaluator.json')
        self.assertFalse(self.actor.exists())

    def test_new_and_existing_empty_directories_supported(self):
        self.actor.mkdir()
        self.prepare('pause')
        self.assertTrue(self.check()['automated_checks_passed'])

    def test_regular_file_workspace_rejected(self):
        self.actor.write_text('precious')
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(self.actor.read_text(), 'precious')

    def test_unknown_case_does_not_create_anything(self):
        with self.assertRaises(KeyError):
            self.prepare('unknown')
        self.assertEqual(list(self.base.iterdir()), [])

    def test_symlink_workspace_and_manifest_rejected(self):
        target = self.base / 'empty'
        target.mkdir()
        self.actor.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(list(target.iterdir()), [])
        self.actor.unlink()
        self.manifest.symlink_to(self.base / 'missing')
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.actor.exists())

    def test_symlink_entry_rejected_without_following(self):
        self.prepare()
        self.repair()
        external = self.base / 'external.py'
        external.write_text('precious')
        (self.actor / 'calculator.py').unlink()
        (self.actor / 'calculator.py').symlink_to(external)
        self.assertFalse(self.check()['automated_checks_passed'])
        self.assertEqual(external.read_text(), 'precious')

    def test_missing_workspace_rejected(self):
        self.prepare('pause')
        for target in self.actor.iterdir():
            target.unlink()
        self.actor.rmdir()
        self.assertFalse(self.check()['automated_checks_passed'])

    def test_manifest_cannot_be_used_for_different_workspace(self):
        self.prepare()
        with self.assertRaises(ValueError):
            fixture.check(self.base / 'other', self.manifest)

    def test_cli_direct_executable_and_exit_codes(self):
        def cli(*args):
            return subprocess.run([str(HELPER), *map(str, args)],
                                  capture_output=True, text=True)

        result = cli('prepare', 'local_fix', self.actor, '--manifest', self.manifest,
                     '--workflow-path', ROOT / 'skills/bruce/SKILL.md')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['workspace'], str(self.actor.resolve()))
        result = cli('check', self.actor, '--manifest', self.manifest)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)['automated_checks_passed'])
        self.repair()
        result = cli('check', self.actor, '--manifest', self.manifest)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = cli('prepare', 'local_fix', self.actor, '--manifest', self.manifest)
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stdout))

    def test_required_plan_missing_empty_or_directory_blocks_commands(self):
        self.prepare()
        self.repair()
        plan = self.actor / 'test-plan.md'
        plan.unlink()
        for kind in ('missing', 'empty', 'directory'):
            with self.subTest(kind=kind):
                if kind == 'empty':
                    plan.write_text(' \n')
                elif kind == 'directory':
                    plan.unlink()
                    plan.mkdir()
                with patch.object(fixture.subprocess, 'run') as run:
                    result = self.check()
                    run.assert_not_called()
                self.assertFalse(result['automated_checks_passed'])

    def test_legacy_manifest_without_created_stays_compatible(self):
        self.prepare()
        self.repair()
        data = json.loads(self.manifest.read_text())
        data.pop('created')
        self.manifest.write_text(json.dumps(data))
        (self.actor / 'test-plan.md').unlink()
        self.assertTrue(self.check()['automated_checks_passed'])

    def test_creation_allowlist_rejects_unsafe_or_overlapping_names(self):
        self.prepare()
        data = json.loads(self.manifest.read_text())
        for value in ('test-plan.md', [None], [''], ['..'], ['/outside'], ['a/b'],
                      ['a\\b'], ['calculator.py'], ['plan.md', 'plan.md']):
            with self.subTest(value=value):
                data['created'] = value
                self.manifest.write_text(json.dumps(data))
                with patch.object(fixture.subprocess, 'run') as run:
                    with self.assertRaises(ValueError):
                        self.check()
                    run.assert_not_called()

    def test_unknown_external_result_is_not_replayed_by_checker(self):
        self.prepare('unknown_external_result')
        with patch.object(fixture.subprocess, 'run') as run:
            result = self.check()
            run.assert_not_called()
        self.assertTrue(result['automated_checks_passed'])
        self.assertEqual(result['status'], 'needs_manual_review')
        self.assertFalse((self.actor / 'replayed.txt').exists())
        (self.actor / 'replayed.txt').write_text('unexpected replay')
        self.assertFalse(self.check()['automated_checks_passed'])

    def test_dirty_user_work_is_frozen_during_repair(self):
        self.prepare('dirty_worktree')
        draft = self.actor / 'user_draft.md'
        before = draft.read_bytes()
        self.repair()
        self.assertTrue(self.check()['automated_checks_passed'])
        self.assertEqual(draft.read_bytes(), before)
        draft.write_text('unauthorized edit')
        with patch.object(fixture.subprocess, 'run') as run:
            self.assertFalse(self.check()['automated_checks_passed'])
            run.assert_not_called()

    def test_command_cannot_empty_required_plan(self):
        self.prepare()
        (self.actor / 'calculator.py').write_text(
            "from pathlib import Path\nPath('test-plan.md').write_text('')\n"
            'def add(a, b):\n    return a + b\n')
        result = self.check()
        self.assertEqual(result['commands'][0]['exit_code'], 0)
        self.assertFalse(result['automated_checks_passed'])

    def test_repair_requests_authorize_only_minimal_test_plan(self):
        specs = json.loads(fixture.SCENARIOS.read_text())
        for case in REPAIRS:
            with self.subTest(case=case):
                self.assertEqual(specs[case]['created'], ['test-plan.md'])
                self.assertIn('test-plan.md', specs[case]['request'])
                self.assertNotIn('Do not create docs', specs[case]['request'])


if __name__ == '__main__':
    unittest.main()
