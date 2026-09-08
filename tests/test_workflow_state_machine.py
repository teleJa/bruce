from __future__ import annotations

from copy import deepcopy
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

import yaml

from scripts.workflow_state import (
    WorkflowStateError,
    allowed_events,
    apply_event,
    validate_document,
    validate_snapshot,
    validate_verification_run,
)
from tests._support import ROOT, read


def snapshot(**overrides):
    result = {
        "version": 1,
        "task_id": "T-001",
        "state": "unresolved",
        "state_revision": 0,
        "mode": "implementation",
        "contract_revision": 1,
        "contract_frozen_revision": None,
        "basis_revision": "basis-1",
        "design_gate": "pending",
        "completion_result": None,
        "last_event": None,
        "stop_reason": None,
        "resume_state": None,
        "resume_conditions": [],
    }
    result.update(overrides)
    if result["state"] not in {"unresolved", "contracting"} and result["contract_frozen_revision"] is None:
        result["contract_frozen_revision"] = result["contract_revision"]
    return result


class WorkflowStateMachineTest(unittest.TestCase):
    def event(self, state, event_type, **fields):
        payload = {"type": event_type, "basis_revision": state["basis_revision"]}
        payload.update(fields)
        return apply_event(state, payload)

    def state_at(self, target):
        state = snapshot()
        if target == "unresolved":
            return state
        state = self.event(state, "inspection_complete")
        if target == "contracting":
            return state
        state = self.event(state, "contract_frozen")
        if target == "designing":
            return self.event(state, "design_required")
        if target in {"design_ready", "design_blocked"}:
            state = self.event(state, "design_required")
            if target == "design_ready":
                return self.event(
                    state,
                    "design_passed",
                    actor="design-gate",
                    evidence_refs=["design-review.md"],
                )
            return self.event(
                state,
                "design_blocked",
                actor="design-gate",
                reason="design blocker",
                resume_conditions=["design is corrected"],
                evidence_refs=["design-review.md"],
            )
        state["design_gate"] = "not_required"
        state = self.event(state, "implementation_authorized", actor="user")
        if target == "implementing":
            return state
        state = self.event(state, "implementation_complete")
        if target == "verifying":
            return state
        if target == "waiting_external":
            return self.event(
                state,
                "external_wait",
                resume_conditions=["external result is available"],
            )
        if target == "waiting_user":
            return self.event(
                state,
                "user_wait",
                resume_conditions=["user returns structured evidence"],
            )
        if target == "repairing":
            return self.event(state, "repair_started")
        if target == "re_verifying":
            return self.event(self.event(state, "repair_started"), "repair_complete")
        state = self.event(state, "verification_passed", actor="verifier")
        if target == "completion_review":
            return state
        if target == "completed":
            return self.event(
                state,
                "completion_passed",
                actor="completion-gate",
                evidence_refs=["pytest"],
            )
        if target == "completion_issues":
            return self.event(
                state,
                "completion_issues",
                actor="completion-gate",
                evidence_refs=["review finding"],
            )
        if target == "blocked":
            return self.event(
                state,
                "blocked",
                reason="verification blocked",
                resume_conditions=["dependency is available"],
            )
        raise AssertionError(f"unsupported fixture state: {target}")

    def test_design_and_implementation_path_reaches_completed_only_via_completion_pass(self):
        state = snapshot()
        state = self.event(state, "inspection_complete")
        state = self.event(state, "contract_frozen")
        state = self.event(state, "design_required")
        state = self.event(state, "design_passed", actor="design-gate", evidence_refs=["design-review.md"])
        self.assertEqual("design_ready", state["state"])
        self.assertEqual("pass", state["design_gate"])
        state = self.event(state, "implementation_authorized", actor="user")
        state = self.event(state, "implementation_complete")
        state = self.event(state, "verification_passed", actor="verifier")
        state = self.event(state, "completion_passed", actor="completion-gate", evidence_refs=["pytest"])
        self.assertEqual("completed", state["state"])
        self.assertEqual("pass", state["completion_result"])
        self.assertEqual(8, state["state_revision"])

    def test_design_required_marks_gate_pending(self):
        state = snapshot(state="contracting", design_gate="not_required", contract_frozen_revision=1)
        state = self.event(state, "design_required")
        self.assertEqual("designing", state["state"])
        self.assertEqual("pending", state["design_gate"])

    def test_contract_freeze_does_not_authorize_implementation(self):
        state = snapshot(state="contracting", design_gate="not_required")
        frozen = self.event(state, "contract_frozen")
        self.assertEqual("contracting", frozen["state"])
        self.assertEqual(1, frozen["state_revision"])
        authorized = self.event(frozen, "implementation_authorized", actor="user")
        self.assertEqual("implementing", authorized["state"])

    def test_implementation_authorization_requires_design_resolution(self):
        state = snapshot(state="contracting", design_gate="pending")
        with self.assertRaises(WorkflowStateError):
            self.event(state, "implementation_authorized", actor="user")
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(snapshot(state="implementing", design_gate="blocked"))
        state["design_gate"] = "not_required"
        state["contract_frozen_revision"] = state["contract_revision"]
        self.assertEqual("implementing", self.event(state, "implementation_authorized", actor="user")["state"])

    def test_waiting_and_resume_preserve_unowned_fields(self):
        state = snapshot(
            state="verifying",
            design_gate="not_required",
            repair_loop={"current_round": 2},
            evidence_revision="evidence-3",
            profile_revision=4,
        )
        waiting = self.event(
            state,
            "external_wait",
            actor="adapter",
            resume_conditions=["external result is available"],
        )
        resumed = self.event(waiting, "resume", actor="user")
        self.assertEqual("verifying", resumed["state"])
        self.assertEqual(state["repair_loop"], resumed["repair_loop"])
        self.assertEqual("evidence-3", resumed["evidence_revision"])
        self.assertEqual(4, resumed["profile_revision"])

    def test_waiting_that_becomes_blocked_resumes_to_verification(self):
        state = snapshot(state="verifying", design_gate="not_required")
        waiting = self.event(
            state,
            "user_wait",
            resume_conditions=["user returns structured evidence"],
        )
        blocked = self.event(
            waiting,
            "blocked",
            reason="user evidence cannot be obtained",
            resume_conditions=["required evidence becomes available"],
        )
        self.assertEqual("verifying", blocked["resume_state"])
        resumed = self.event(blocked, "resume", actor="user")
        self.assertEqual("verifying", resumed["state"])

    def test_pause_and_resume_return_to_previous_safe_state(self):
        state = snapshot(state="implementing", design_gate="not_required")
        paused = self.event(
            state,
            "pause",
            actor="user",
            reason="user requested pause",
            resume_conditions=["user requests continue"],
        )
        self.assertEqual("paused", paused["state"])
        self.assertEqual("implementing", paused["resume_state"])
        resumed = self.event(paused, "resume", actor="user")
        self.assertEqual("implementing", resumed["state"])
        self.assertIsNone(resumed["resume_state"])
        self.assertIsNone(resumed["stop_reason"])
        self.assertEqual([], resumed["resume_conditions"])

    def test_resume_requires_user_and_persisted_resume_target_is_checked(self):
        paused = self.event(
            self.state_at("implementing"),
            "pause",
            actor="user",
            reason="user paused",
            resume_conditions=["user requests continue"],
        )
        with self.assertRaises(WorkflowStateError):
            self.event(paused, "resume", actor="main-agent")
        resumed = self.event(paused, "resume", actor="user")
        tampered = deepcopy(resumed)
        tampered["last_event"]["resume_state"] = "verifying"
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(tampered)

    def test_repair_loop_is_explicit_and_revisioned(self):
        state = snapshot(state="verifying", design_gate="not_required")
        state = self.event(state, "repair_started")
        state = self.event(state, "repair_complete")
        state = self.event(state, "reverification_passed")
        self.assertEqual("completion_review", state["state"])
        self.assertEqual(3, state["state_revision"])

    def test_gate_events_require_gate_actor(self):
        design = snapshot(state="designing", design_gate="pending", contract_frozen_revision=1)
        with self.assertRaises(WorkflowStateError):
            self.event(design, "design_passed", actor="main-agent")
        completion = snapshot(state="completion_review", design_gate="not_required", contract_frozen_revision=1)
        with self.assertRaises(WorkflowStateError):
            self.event(completion, "completion_passed", actor="reviewer")
        blocked = self.event(
            completion,
            "completion_blocked",
            actor="completion-gate",
            evidence_refs=["completion-review"],
            reason="evidence missing",
            resume_conditions=["required evidence is current"],
        )
        self.assertEqual("blocked", blocked["state"])
        self.assertEqual("completion_review", blocked["resume_state"])
        self.assertEqual("blocked", blocked["completion_result"])

    def test_unknown_event_illegal_transition_and_basis_mismatch_fail_closed(self):
        state = snapshot(state="verifying", design_gate="not_required")
        with self.assertRaises(WorkflowStateError):
            apply_event(state, {"type": "invented"})
        with self.assertRaises(WorkflowStateError):
            apply_event(state, {"type": "inspection_complete"})
        with self.assertRaises(WorkflowStateError):
            apply_event(state, {"type": "external_wait", "basis_revision": "stale"})
        with self.assertRaises(WorkflowStateError):
            apply_event(
                state,
                {
                    "type": "external_wait",
                    "to_state": "completed",
                    "resume_conditions": ["external result is available"],
                },
            )

    def test_persisted_last_event_must_match_current_state_and_gate_source(self):
        state = snapshot(state="completion_review", design_gate="not_required")
        completed = self.event(state, "completion_passed", actor="completion-gate", evidence_refs=["pytest"])
        tampered = deepcopy(completed)
        tampered["last_event"]["to_state"] = "completion_review"
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(tampered)
        tampered = deepcopy(completed)
        tampered["last_event"]["actor"] = "main-agent"
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(tampered)

    def test_direct_gate_bypass_and_unfrozen_authorization_fail_closed(self):
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(
                snapshot(
                    state="completed",
                    design_gate="not_required",
                    completion_result="pass",
                )
            )
        with self.assertRaises(WorkflowStateError):
            self.event(
                snapshot(state="contracting", design_gate="not_required"),
                "implementation_authorized",
                actor="user",
            )
        design_only = snapshot(
            mode="design_only",
            state="contracting",
            design_gate="not_required",
            contract_frozen_revision=1,
        )
        with self.assertRaises(WorkflowStateError):
            self.event(design_only, "implementation_authorized", actor="user")

    def test_completed_is_terminal_and_requires_completion_pass(self):
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(self.state_at("completed") | {"completion_result": "issues"})
        completed = self.state_at("completed")
        self.assertEqual((), allowed_events("completed"))
        with self.assertRaises(WorkflowStateError):
            self.event(completed, "resume")

    def test_blocked_requires_reason_and_resume_clears_it(self):
        with self.assertRaises(WorkflowStateError):
            validate_snapshot(snapshot(state="blocked"))
        state = snapshot(state="verifying", design_gate="not_required")
        state = self.event(
            state,
            "blocked",
            reason="provider unavailable",
            resume_conditions=["configured provider preflight passes"],
        )
        self.assertEqual("provider unavailable", state["stop_reason"])
        state = self.event(state, "resume", actor="user")
        self.assertIsNone(state["stop_reason"])
        self.assertEqual([], state["resume_conditions"])

    def test_checkpoint_mapping_must_match_task_basis_and_completion(self):
        state = self.state_at("completed")
        checkpoint = {
            "workflow_state": state,
            "Checkpoint": "clear",
            "active_task": "T-001",
            "basis_revision": "basis-1",
            "tasks": [{"task_id": "T-001", "status": "verified"}],
            "completion": {"state": "decided", "result": "pass"},
            "blockers": [],
            "acceptance": {"passed": ["AC-1"], "failed": [], "unexecuted": []},
        }
        self.assertEqual("completed", validate_document(checkpoint)["state"])
        checkpoint["active_task"] = "T-002"
        with self.assertRaises(WorkflowStateError):
            validate_document(checkpoint)
        checkpoint["active_task"] = "T-001"
        checkpoint["completion"]["result"] = "issues"
        with self.assertRaises(WorkflowStateError):
            validate_document(checkpoint)

    def test_verification_run_identity_and_projection_are_validated(self):
        state = self.state_at("verifying")
        run = {
            "version": 1,
            "workflow_state_ref": "checkpoint.workflow_state",
            "run_id": "VR-001",
            "task_id": "T-001",
            "checkpoint_id": "CP-001",
            "workflow_state_revision": state["state_revision"],
            "basis_revision": state["basis_revision"],
            "state": "running",
        }
        self.assertEqual("VR-001", validate_verification_run(run, state, checkpoint_id="CP-001")["run_id"])
        stale = deepcopy(run)
        stale["workflow_state_revision"] -= 1
        with self.assertRaises(WorkflowStateError):
            validate_verification_run(stale, state, checkpoint_id="CP-001")
        mismatch = deepcopy(run)
        mismatch["state"] = "passed"
        with self.assertRaises(WorkflowStateError):
            validate_verification_run(mismatch, state, checkpoint_id="CP-001")

    def test_checkpoint_consistency_rejects_conflicting_task_and_completion_states(self):
        state = self.state_at("completed")
        checkpoint = {
            "workflow_state": state,
            "Checkpoint": "clear",
            "active_task": "T-001",
            "basis_revision": "basis-1",
            "tasks": [{"task_id": "T-001", "status": "pending"}],
            "completion": {"state": "not_started", "result": "pass"},
            "blockers": [],
            "acceptance": {"passed": ["AC-1"], "failed": [], "unexecuted": []},
        }
        with self.assertRaises(WorkflowStateError):
            validate_document(checkpoint)

    def test_legacy_checkpoint_fails_closed_until_explicit_migration(self):
        with self.assertRaises(WorkflowStateError):
            validate_document({"version": 1, "Checkpoint": "clear", "active_task": "T-001"})
        policy = read("skills/bruce/references/workflow-state.md")
        self.assertIn("Legacy checkpoint migration", policy)
        self.assertIn("state_revision: 0", policy)
        self.assertIn("never infer `design_ready`, `verified`, or `completed`", policy)

    def test_cli_validates_template_and_rejects_invalid_snapshot(self):
        command = [sys.executable, "scripts/validate_workflow_state.py"]
        valid = subprocess.run(
            command + ["skills/bruce/templates/workflow-state.yaml"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, valid.returncode, valid.stderr)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.yaml"
            invalid = deepcopy(snapshot())
            invalid["state"] = "completed"
            path.write_text(yaml.safe_dump(invalid), encoding="utf-8")
            result = subprocess.run(command + [str(path)], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("state_revision=0 cannot contain Gate or completion results", result.stderr)

    def test_checkpoint_run_and_gate_contracts_reference_shared_state(self):
        checkpoint = read("skills/bruce/templates/checkpoint.yaml")
        run = read("skills/bruce/templates/verification-run.yaml")
        workflow = read("skills/bruce/SKILL.md")
        design_gate = read("skills/design-gate/SKILL.md")
        completion_gate = read("skills/completion-gate/SKILL.md")
        self.assertIn("workflow_state:", checkpoint)
        self.assertIn("workflow_state_ref: checkpoint.workflow_state", run)
        self.assertIn("references/workflow-state.md", workflow)
        self.assertIn("design_passed(actor=design-gate) -> design_ready", design_gate)
        self.assertIn("completion_passed(actor=completion-gate) -> completed", completion_gate)
        self.assertIn("cannot generate or override this Gate verdict", completion_gate)


if __name__ == "__main__":
    unittest.main()
