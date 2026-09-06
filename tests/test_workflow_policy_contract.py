"""Exercise authoritative decision tables; not an Agent execution simulator."""
from itertools import product
import unittest

import yaml

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
    def test_design_gate_handoff_preserves_negative_applicability_boundaries(self):
        policy = ' '.join(read('skills/bruce/references/artifact-policy.md').split())
        for phrase in (
            '持久化工件包含待确认的设计决策或下游合同',
            '只是执行清单、现有命令列表、进度说明或普通文档编辑',
            '治理型工件已成功落盘并完成本地文档检查',
            '必须在同一轮内立即执行 Gate，无需用户追加指令',
        ):
            self.assertIn(phrase, policy)

        plan = ' '.join(read('skills/write-plan/SKILL.md').split())
        self.assertIn('An execution checklist alone does not require the handoff', plan)

        prototype = ' '.join(read('skills/write-prototype/SKILL.md').split())
        self.assertIn('When the confirmed prototype will govern implementation', prototype)
        self.assertIn(
            'Pending, unconfirmed, or otherwise non-governing prototype state does not create this handoff',
            prototype,
        )

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
            (('unknown', 'below_limit', 'batch', 'below_limit'), 'freeze_L4'),
            (('known', 'unknown', 'completion', 'below_limit'), 'recover_counts'),
            (('known', 'at_limit', 'batch', 'below_limit'), 'replan_L2'),
            (('known', 'at_limit', 'completion', 'below_limit'), 'replan_L2'),
            (('known', 'at_limit', 'completion', 'at_limit'), 'replan_L2'),
            (('known', 'below_limit', 'completion', 'unknown'), 'recover_counts'),
            (('known', 'below_limit', 'completion', 'at_limit'), 'stop_completion'),
            (('known', 'below_limit', 'completion', 'below_limit'), 'repair_both'),
            (('known', 'below_limit', 'batch', 'at_limit'), 'repair_local'),
            (('known', 'below_limit', 'batch', 'unknown'), 'repair_local'),
        )
        for inputs, expected in examples:
            with self.subTest(inputs=inputs):
                self.assertEqual(select(table, inputs), (expected,))
        # Resume does not turn an exhausted failure into a new zero-count failure.
        self.assertEqual(select(table, ('known', 'at_limit', 'completion', 'below_limit')), ('replan_L2',))

    def test_configured_numeric_boundaries_drive_budget_table(self):
        table = rows('skills/bruce/references/failure-recovery.md', 'BUDGET')
        configured = yaml.safe_load(read('.bruce/config.yaml'))['workflow']['repair_loop']
        template = yaml.safe_load(read('skills/bruce/templates/config.yaml'))['workflow']['repair_loop']
        overrides = yaml.safe_load("""
max_rounds: 7
max_rounds_per_failure: 3
""")
        # Translate numeric counts to the authoritative table's categories, not an Agent runtime.
        for limits in (configured, template, overrides):
            local_limit = limits['max_rounds_per_failure']
            global_limit = limits['max_rounds']
            for local_count, global_count, phase in product(
                range(local_limit + 2), range(global_limit + 2), ('batch', 'completion')
            ):
                with self.subTest(limits=limits, local=local_count, overall=global_count, phase=phase):
                    local_state = 'below_limit' if local_count < local_limit else 'at_limit'
                    global_state = 'below_limit' if global_count < global_limit else 'at_limit'
                    if local_count >= local_limit:
                        expected = 'replan_L2'
                    elif phase == 'batch':
                        expected = 'repair_local'
                    elif global_count >= global_limit:
                        expected = 'stop_completion'
                    else:
                        expected = 'repair_both'
                    self.assertEqual(select(table, ('known', local_state, phase, global_state)), (expected,))

    def test_active_consumers_read_both_configured_limits(self):
        consumers = (
            'skills/bruce/SKILL.md',
            'skills/bruce/references/artifact-placement.md',
            'skills/bruce/references/failure-recovery.md',
            'skills/bruce/references/verification-loop.md',
            'skills/completion-gate/SKILL.md',
            'skills/bruce/templates/checkpoint.yaml',
        )
        for path in consumers:
            with self.subTest(path=path):
                body = ' '.join(read(path).split())
                self.assertIn('workflow.repair_loop.max_rounds_per_failure', body)
                self.assertIn('workflow.repair_loop.max_rounds', body)
                self.assertNotIn('at most two complete repair-and-reverify rounds', body)
                self.assertNotIn('two unsuccessful complete repairs', body)
                self.assertNotIn('max_rounds` (integer 1 through 5', body)
                self.assertNotIn('max_rounds` defaults to 5', body)

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
