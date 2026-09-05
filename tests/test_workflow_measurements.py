"""Opt-in measurement aggregation: explicit fixture data, no native actor claims."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import workflow_behavior_fixture as fixture


def trial(trial_id='one', **overrides):
    return {
        'trial_id': trial_id, 'workflow_revision': 'workflow-a', 'fixture_revision': 'fixture-a',
        'scenario': 'local_fix', 'source': 'fixture_test', 'automated_checks_passed': True,
        'manual_status': 'pending', 'evidence_refs': [], 'metrics': {}, **overrides,
    }


class WorkflowMeasurementTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='bruce-measurement-test-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'explicit-input.json'

    def summarize(self, trials):
        self.path.write_text(json.dumps({'version': 1, 'trials': trials}))
        before = self.path.read_bytes()
        with patch.object(fixture.subprocess, 'run') as run:
            result = fixture.summarize(self.path)
            run.assert_not_called()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])
        return result

    def test_empty_measurements_are_not_success_or_zero_cost(self):
        result = self.summarize([])
        self.assertEqual(result['groups'], [])
        self.assertEqual(result['samples'], 0)
        self.assertNotIn('Completion', result)

    def test_unknown_values_are_not_zero_and_report_coverage(self):
        result = self.summarize([
            trial('a', metrics={'elapsed_seconds': 10, 'tool_calls': 0}),
            trial('b', metrics={'elapsed_seconds': None}),
            trial('c', metrics={'elapsed_seconds': 20}),
        ])
        group = result['groups'][0]
        self.assertEqual(group['metrics']['elapsed_seconds'], {'observed_samples': 2, 'mean': 15})
        self.assertEqual(group['metrics']['tool_calls'], {'observed_samples': 1, 'mean': 0})
        self.assertEqual(group['metrics']['tokens'], {'observed_samples': 0, 'mean': None})
        self.assertIsNone(group['reviewed_pass_rate'])

    def test_only_reviewed_native_records_have_conditional_pass_rate(self):
        base = {'source': 'native_actor', 'manual_status': 'passed', 'evidence_refs': ['trial/tool-result']}
        result = self.summarize([
            trial('a', **base),
            trial('b', **{**base, 'manual_status': 'failed'}),
            trial('c', **{**base, 'automated_checks_passed': False}),
            trial('d', source='native_actor'),
            trial('e', manual_status='passed', evidence_refs=['synthetic/test']),
        ])
        groups = {group['source']: group for group in result['groups']}
        self.assertIsNone(groups['fixture_test']['reviewed_pass_rate'])
        native = groups['native_actor']
        self.assertEqual(native['manual_reviewed_samples'], 3)
        self.assertEqual(native['manual_pending_samples'], 1)
        self.assertAlmostEqual(native['reviewed_pass_rate'], 1 / 3)
        self.assertIn('references are not authenticated', result['evidence_boundary'])

    def test_revisions_scenarios_and_sources_never_mix(self):
        records = [trial('base')]
        for index, (field, value) in enumerate((('workflow_revision', 'other'),
                                              ('fixture_revision', 'other'),
                                              ('scenario', 'pause'), ('source', 'native_actor'))):
            records.append(trial(str(index), **{field: value}))
        self.assertEqual(len(self.summarize(records)['groups']), 5)

    def test_invalid_trials_fail_closed(self):
        invalid = [None, [], {}, {**trial(), 'unknown': True}]
        changes = (
            ('source', 'unknown'), ('scenario', 'unknown'), ('manual_status', 'skipped'),
            ('automated_checks_passed', 1), ('trial_id', ''), ('workflow_revision', []),
            ('evidence_refs', 'path'), ('evidence_refs', ['']), ('manual_status', 'passed'),
            ('metrics', []), ('metrics', {'unknown': 2}),
        )
        invalid.extend(trial(**{field: value}) for field, value in changes)
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.summarize([value])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.summarize([trial(), trial()])

    def test_nonfinite_negative_boolean_and_fractional_counters_rejected(self):
        for metric in fixture.DURATION_METRICS | fixture.COUNT_METRICS:
            bad_values = [True, False, '1', -1, float('inf'), float('nan'), 10 ** 400]
            if metric in fixture.COUNT_METRICS:
                bad_values.append(1.5)
            for value in bad_values:
                with self.subTest(metric=metric, value=value):
                    with self.assertRaises(ValueError):
                        self.summarize([trial(metrics={metric: value})])

    def test_duration_consistency(self):
        for metrics in ({'elapsed_seconds': 1, 'first_verification_seconds': 2},
                        {'elapsed_seconds': 5, 'planning_seconds': 3, 'verification_seconds': 3}):
            with self.subTest(metrics=metrics):
                with self.assertRaises(ValueError):
                    self.summarize([trial(metrics=metrics)])
        result = self.summarize([trial(metrics={'elapsed_seconds': 5, 'planning_seconds': 2,
                                               'verification_seconds': 3, 'first_verification_seconds': 4})])
        self.assertEqual(result['samples'], 1)

    def test_decimal_duration_rounding_is_not_a_real_overrun(self):
        for metrics in (
            {'elapsed_seconds': 0.3, 'planning_seconds': 0.1, 'verification_seconds': 0.2},
            {'elapsed_seconds': 0.3, 'first_verification_seconds': 0.1 + 0.2},
        ):
            with self.subTest(metrics=metrics):
                self.assertEqual(self.summarize([trial(metrics=metrics)])['samples'], 1)

    def test_duration_tolerance_does_not_hide_real_or_zero_budget_overruns(self):
        for metrics in (
            {'elapsed_seconds': 0.3, 'planning_seconds': 0.1, 'verification_seconds': 0.2000000001},
            {'elapsed_seconds': 0.3, 'first_verification_seconds': 0.3000000001},
            {'elapsed_seconds': 0, 'planning_seconds': 1e-15},
            {'elapsed_seconds': 0, 'first_verification_seconds': 1e-15},
        ):
            with self.subTest(metrics=metrics), self.assertRaises(ValueError):
                self.summarize([trial(metrics=metrics)])

    def test_invalid_top_level_shapes(self):
        for data in ([], None, {'version': True, 'trials': []}, {'version': 2, 'trials': []},
                     {'version': 1, 'trials': {}}, {'version': 1, 'trials': [], 'unknown': 0}):
            self.path.write_text(json.dumps(data))
            with self.subTest(data=data), self.assertRaises(ValueError):
                fixture.summarize(self.path)

    def test_cli_success_and_invalid_input_leave_input_unchanged(self):
        self.path.write_text(json.dumps({'version': 1, 'trials': [trial()]}))
        before = self.path.read_bytes()
        command = [str(Path(fixture.__file__).resolve()), 'summarize', str(self.path)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['samples'], 1)
        self.assertEqual(self.path.read_bytes(), before)
        self.path.write_text('{bad input')
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('error', json.loads(result.stdout))
