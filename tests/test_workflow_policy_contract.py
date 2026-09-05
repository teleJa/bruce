"""Exercise authoritative decision tables; not an Agent execution simulator."""
from itertools import product
import unittest

from tests._support import read


def rows(path, prefix):
    return [tuple(part.strip() for part in line.strip('|').split('|'))
            for line in read(path).splitlines() if line.startswith(f'| {prefix}-')]


def select(table, inputs):
    for row in table:
        if all(expected == 'any' or expected == actual
               for expected, actual in zip(row[1:1 + len(inputs)], inputs)):
            return row[1 + len(inputs):]
    raise AssertionError(f'no decision for {inputs}')


class WorkflowPolicyContractTest(unittest.TestCase):
    def test_test_design_truth_table_covers_all_inputs(self):
        table = rows('skills/bruce/references/artifact-policy.md', 'TEST')
        self.assertEqual([row[0] for row in table], [f'TEST-0{i}' for i in range(1, 6)])
        for behavior, requested, complex_acceptance in product(('no', 'yes'), repeat=3):
            with self.subTest(behavior=behavior, requested=requested, complex=complex_acceptance):
                expected = ('skipped', 'none')
                if behavior == 'yes' or requested == 'yes':
                    expected = ('required', 'expanded' if complex_acceptance == 'yes' else 'minimal')
                self.assertEqual(select(table, (behavior, requested, complex_acceptance)), expected)

    def test_entry_summary_and_skill_use_the_same_mandatory_rule(self):
        workflow = read('skills/bruce/SKILL.md')
        skill = read('skills/write-tests/SKILL.md')
        description = next(line for line in skill.splitlines() if line.startswith('description:'))
        for body in (workflow, description):
            self.assertIn('every behavior change', body)
            self.assertIn('independent', body)
            self.assertIn('minimal', body)
            self.assertIn('expanded', body)
        self.assertNotIn('complex acceptance and regression design: `write-tests`', workflow)
        self.assertIn('下列复杂度条件只决定模板深度', skill)
        self.assertIn('所有行为变更均触发测试设计', skill)

    def test_minimal_template_has_evidence_without_empty_matrices(self):
        template = read('skills/write-tests/templates/test-plan-minimal.md')
        for field in ('验收 ID', '前置条件', 'Given:', 'When:', 'Then:', '验证命令',
                      'Evidence:', '限制与回归', 'consistency_check', 'visual_scope'):
            self.assertIn(field, template)
        self.assertFalse(any(line.startswith('|') for line in template.splitlines()))
        self.assertLess(len(template.splitlines()), 30)
        expanded = read('skills/write-tests/templates/test-plan.md')
        self.assertIn('test-plan-minimal.md', expanded)
        self.assertIn('省略本矩阵', expanded)
        self.assertIn('一致性与权威状态矩阵', expanded)

    def test_budget_decisions_cover_overlap_resume_and_new_findings(self):
        table = rows('skills/bruce/references/failure-recovery.md', 'BUDGET')
        self.assertEqual([row[0] for row in table], [f'BUDGET-0{i}' for i in range(1, 8)])
        examples = (
            (('unknown', '0-or-1', 'batch', 'below_limit'), 'freeze_L4'),
            (('known', 'unknown', 'completion', 'below_limit'), 'recover_counts'),
            (('known', '2+', 'batch', 'below_limit'), 'replan_L2'),
            (('known', '2+', 'completion', 'below_limit'), 'replan_L2'),
            (('known', '2+', 'completion', 'at_limit'), 'replan_L2'),
            (('known', '0-or-1', 'completion', 'unknown'), 'recover_counts'),
            (('known', '0-or-1', 'completion', 'at_limit'), 'stop_completion'),
            (('known', '0-or-1', 'completion', 'below_limit'), 'repair_both'),
            (('known', '0-or-1', 'batch', 'at_limit'), 'repair_local'),
            (('known', '0-or-1', 'batch', 'unknown'), 'repair_local'),
        )
        for inputs, expected in examples:
            with self.subTest(inputs=inputs):
                self.assertEqual(select(table, inputs), (expected,))
        # Resume does not turn an exhausted failure into a new zero-count failure.
        self.assertEqual(select(table, ('known', '2+', 'completion', 'below_limit')), ('replan_L2',))

    def test_counter_consumers_do_not_widen_local_budget(self):
        policy = read('skills/bruce/references/failure-recovery.md')
        self.assertIn('missing history is unknown, not zero', policy)
        self.assertIn('renaming a repeated failure never grants more attempts', policy)
        self.assertIn('Batch verification never reads or spends the Completion budget', policy)
        for path in ('skills/bruce/templates/checkpoint.yaml', 'skills/completion-gate/SKILL.md'):
            body = read(path)
            self.assertIn('failure_id', body)
            self.assertIn('l1_repair_rounds', body)
        loop = read('skills/bruce/references/verification-loop.md')
        self.assertNotIn('subsequent repair rounds read\n`workflow.repair_loop.max_rounds`', loop)
        self.assertIn('they never consume the Completion-only', loop)
        self.assertIn('only to Completion Gate', read('skills/bruce/SKILL.md'))
