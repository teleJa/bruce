"""Unified task-level workflow state machine for Bruce.

This module is deliberately independent from project adapters, runtime execution, and Gate
implementations. It validates a persisted task snapshot and applies one normalized event at a time.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = 1
STATES = (
    "unresolved",
    "contracting",
    "designing",
    "design_ready",
    "design_blocked",
    "implementing",
    "verifying",
    "waiting_external",
    "waiting_user",
    "repairing",
    "re_verifying",
    "completion_review",
    "completion_issues",
    "paused",
    "blocked",
    "completed",
)
MODES = ("design_only", "implementation")
DESIGN_GATE_STATES = ("not_required", "pending", "pass", "blocked")
COMPLETION_RESULTS = (None, "pass", "issues", "blocked")
STOP_REASON_STATES = {"design_blocked", "paused", "blocked"}
WAITING_STATES = {"waiting_external", "waiting_user"}
RECOVERABLE_STATES = STOP_REASON_STATES | WAITING_STATES
DESIGN_GATE_EVENTS = {"design_passed", "design_blocked"}
COMPLETION_GATE_EVENTS = {"completion_passed", "completion_issues", "completion_blocked"}
GATE_EVENT_ACTORS = {
    **{event: "design-gate" for event in DESIGN_GATE_EVENTS},
    **{event: "completion-gate" for event in COMPLETION_GATE_EVENTS},
}
IMPLEMENTATION_PHASE_STATES = {
    "implementing",
    "verifying",
    "waiting_external",
    "waiting_user",
    "repairing",
    "re_verifying",
    "completion_review",
    "completion_issues",
    "completed",
}
FROZEN_REQUIRED_STATES = IMPLEMENTATION_PHASE_STATES | {
    "designing",
    "design_ready",
    "design_blocked",
}
EVENTS = (
    "inspection_complete",
    "contract_frozen",
    "design_required",
    "design_passed",
    "design_blocked",
    "implementation_authorized",
    "implementation_complete",
    "verification_started",
    "external_wait",
    "user_wait",
    "verification_passed",
    "verification_failed",
    "repair_started",
    "repair_complete",
    "reverification_passed",
    "completion_started",
    "completion_passed",
    "completion_issues",
    "completion_blocked",
    "pause",
    "blocked",
    "resume",
    "design_only_stop",
)

TRANSITIONS: dict[str, dict[str, str]] = {
    "unresolved": {"inspection_complete": "contracting"},
    "contracting": {
        "contract_frozen": "contracting",
        "design_required": "designing",
        "implementation_authorized": "implementing",
        "pause": "paused",
        "blocked": "blocked",
    },
    "designing": {
        "design_passed": "design_ready",
        "design_blocked": "design_blocked",
        "pause": "paused",
    },
    "design_ready": {
        "implementation_authorized": "implementing",
        "design_only_stop": "design_ready",
        "pause": "paused",
    },
    "design_blocked": {
        "design_required": "designing",
    },
    "implementing": {
        "implementation_complete": "verifying",
        "pause": "paused",
        "blocked": "blocked",
    },
    "verifying": {
        "external_wait": "waiting_external",
        "user_wait": "waiting_user",
        "repair_started": "repairing",
        "verification_passed": "completion_review",
        "verification_failed": "completion_review",
        "pause": "paused",
        "blocked": "blocked",
    },
    "waiting_external": {"resume": "verifying", "blocked": "blocked"},
    "waiting_user": {"resume": "verifying", "blocked": "blocked"},
    "repairing": {
        "repair_complete": "re_verifying",
        "pause": "paused",
        "blocked": "blocked",
    },
    "re_verifying": {
        "reverification_passed": "completion_review",
        "verification_started": "verifying",
        "repair_started": "repairing",
        "pause": "paused",
        "blocked": "blocked",
    },
    "completion_review": {
        "completion_started": "completion_review",
        "completion_passed": "completed",
        "completion_issues": "completion_issues",
        "completion_blocked": "blocked",
        "pause": "paused",
        "blocked": "blocked",
    },
    "completion_issues": {
        "repair_started": "repairing",
        "pause": "paused",
        "blocked": "blocked",
    },
    "paused": {"resume": "__resume__"},
    "blocked": {
        "resume": "__resume__",
        "design_required": "designing",
        "implementation_authorized": "implementing",
        "verification_started": "verifying",
        "reverification_passed": "completion_review",
    },
    "completed": {},
}


class WorkflowStateError(ValueError):
    """Raised when a snapshot or event violates the state-machine contract."""


def _require_non_empty_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise WorkflowStateError(f"{field} must be a non-empty string")


def _validate_last_event(snapshot: dict[str, Any], revision: int) -> None:
    last_event = snapshot.get("last_event")
    if revision == 0:
        if last_event is not None:
            raise WorkflowStateError("state_revision=0 requires last_event=null")
        return
    if not isinstance(last_event, dict):
        raise WorkflowStateError("positive state_revision requires a last_event mapping")
    for field in ("event_id", "type", "actor", "from_state", "to_state", "basis_revision", "observed_at"):
        _require_non_empty_string(last_event.get(field), f"last_event.{field}")
    if last_event["type"] not in EVENTS:
        raise WorkflowStateError("last_event.type is unknown")
    expected_actor = GATE_EVENT_ACTORS.get(last_event["type"])
    if expected_actor is not None and last_event["actor"] != expected_actor:
        raise WorkflowStateError(f"persisted Gate event must use actor={expected_actor}")
    if expected_actor is not None and not last_event.get("evidence_refs"):
        raise WorkflowStateError("persisted Gate event requires evidence_refs")
    if last_event["from_state"] not in STATES or last_event["to_state"] not in STATES:
        raise WorkflowStateError("last_event states must be known workflow states")
    expected_state = TRANSITIONS[last_event["from_state"]].get(last_event["type"])
    if expected_state is None:
        raise WorkflowStateError("last_event does not match a legal workflow transition")
    if expected_state == "__resume__":
        if last_event.get("resume_state") != last_event["to_state"]:
            raise WorkflowStateError("last_event resume target is missing or invalid")
    elif expected_state != last_event["to_state"]:
        raise WorkflowStateError("last_event does not match a legal workflow transition")
    if last_event["to_state"] != snapshot["state"]:
        raise WorkflowStateError("last_event.to_state does not match current state")
    if last_event["basis_revision"] != snapshot["basis_revision"]:
        raise WorkflowStateError("last_event basis_revision does not match current snapshot")
    evidence_refs = last_event.get("evidence_refs")
    if not isinstance(evidence_refs, list) or any(
        not isinstance(item, str) or not item.strip() for item in evidence_refs
    ):
        raise WorkflowStateError("last_event.evidence_refs must be a list of non-empty strings")


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Validate and return a snapshot without mutating it."""
    if not isinstance(snapshot, dict):
        raise WorkflowStateError("workflow snapshot must be a mapping")
    if snapshot.get("version") != SCHEMA_VERSION:
        raise WorkflowStateError(f"version must be {SCHEMA_VERSION}")
    for field in ("task_id", "basis_revision"):
        _require_non_empty_string(snapshot.get(field), field)
    if snapshot.get("state") not in STATES:
        raise WorkflowStateError(f"unknown workflow state: {snapshot.get('state')!r}")
    if snapshot.get("mode") not in MODES:
        raise WorkflowStateError(f"mode must be one of {MODES}")
    revision = snapshot.get("state_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
        raise WorkflowStateError("state_revision must be a non-negative integer")
    contract_revision = snapshot.get("contract_revision")
    if not isinstance(contract_revision, int) or isinstance(contract_revision, bool) or contract_revision < 1:
        raise WorkflowStateError("contract_revision must be a positive integer")
    frozen_revision = snapshot.get("contract_frozen_revision")
    if frozen_revision is not None and (
        not isinstance(frozen_revision, int)
        or isinstance(frozen_revision, bool)
        or frozen_revision < 1
    ):
        raise WorkflowStateError("contract_frozen_revision must be null or a positive integer")
    if snapshot.get("design_gate") not in DESIGN_GATE_STATES:
        raise WorkflowStateError(f"design_gate must be one of {DESIGN_GATE_STATES}")
    if snapshot.get("completion_result") not in COMPLETION_RESULTS:
        raise WorkflowStateError("completion_result must be null, pass, issues, or blocked")
    _validate_last_event(snapshot, revision)

    state = snapshot["state"]
    design_gate = snapshot["design_gate"]
    completion_result = snapshot["completion_result"]
    if state == "design_ready" and design_gate != "pass":
        raise WorkflowStateError("design_ready requires design_gate=pass")
    if revision == 0 and (
        state in {"design_ready", "design_blocked", "completed"}
        or design_gate in {"pass", "blocked"}
        or completion_result is not None
    ):
        raise WorkflowStateError("state_revision=0 cannot contain Gate or completion results")
    if state == "completed" and completion_result != "pass":
        raise WorkflowStateError("completed requires completion_result=pass")
    if completion_result == "pass" and state != "completed":
        raise WorkflowStateError("completion_result=pass requires state=completed")
    resume_state = snapshot.get("resume_state")
    if resume_state is not None and resume_state not in STATES:
        raise WorkflowStateError("resume_state must be null or a known workflow state")
    if resume_state in {"paused", "blocked", "completed"}:
        raise WorkflowStateError("resume_state must name a resumable workflow state")
    effective_state = resume_state if state in {"paused", "blocked"} else state
    if effective_state in IMPLEMENTATION_PHASE_STATES and design_gate not in {"not_required", "pass"}:
        raise WorkflowStateError("implementation phases require design_gate=not_required or pass")
    if effective_state in FROZEN_REQUIRED_STATES and frozen_revision != contract_revision:
        raise WorkflowStateError("design and implementation phases require the current contract revision to be frozen")
    if state == "completion_issues" and completion_result != "issues":
        raise WorkflowStateError("completion_issues requires completion_result=issues")
    if completion_result == "blocked" and not (
        state == "blocked" or effective_state == "completion_review"
    ):
        raise WorkflowStateError("completion_result=blocked requires blocked or completion_review state")
    resume_conditions = snapshot.get("resume_conditions", [])
    if not isinstance(resume_conditions, list) or any(
        not isinstance(item, str) or not item.strip() for item in resume_conditions
    ):
        raise WorkflowStateError("resume_conditions must be a list of non-empty strings")

    if state in STOP_REASON_STATES:
        if not snapshot.get("stop_reason"):
            raise WorkflowStateError(f"{state} requires stop_reason")
        if not resume_conditions:
            raise WorkflowStateError(f"{state} requires resume_conditions")
        if state in {"paused", "blocked"} and resume_state is None:
            raise WorkflowStateError(f"{state} requires resume_state")
        if state == "design_blocked" and resume_state is not None:
            raise WorkflowStateError("design_blocked uses an explicit design_required transition")
    elif state in WAITING_STATES:
        if not resume_conditions:
            raise WorkflowStateError(f"{state} requires resume_conditions")
        if snapshot.get("stop_reason") is not None or resume_state is not None:
            raise WorkflowStateError(f"{state} cannot carry stop_reason or resume_state")
    elif snapshot.get("stop_reason") is not None or resume_state is not None or resume_conditions:
        raise WorkflowStateError("active states cannot carry stop or resume fields")
    if state == "completed" and snapshot.get("mode") == "design_only":
        raise WorkflowStateError("design_only cannot enter completed")
    return deepcopy(snapshot)


def _validate_checkpoint_consistency(document: dict[str, Any], state: dict[str, Any]) -> None:
    checkpoint_status = document.get("Checkpoint")
    if checkpoint_status not in {"clear", "issues", "blocked"}:
        raise WorkflowStateError("Checkpoint must be clear, issues, or blocked")
    lifecycle = state["state"]
    if lifecycle == "completed" and checkpoint_status != "clear":
        raise WorkflowStateError("completed workflow requires Checkpoint: clear")
    if lifecycle in {"blocked", "design_blocked", "paused"} and checkpoint_status != "blocked":
        raise WorkflowStateError("blocked or paused workflow requires Checkpoint: blocked")

    tasks = document.get("tasks", [])
    if not isinstance(tasks, list):
        raise WorkflowStateError("checkpoint tasks must be a list")
    active_task = document.get("active_task")
    task_row = next((row for row in tasks if isinstance(row, dict) and row.get("task_id") == active_task), None)
    if active_task is not None and task_row is None:
        raise WorkflowStateError("checkpoint active_task must exist in tasks")
    task_status = task_row.get("status") if task_row else None
    allowed_task_statuses = {
        "unresolved": {"pending"},
        "contracting": {"pending", "in_progress"},
        "designing": {"pending", "in_progress"},
        "design_ready": {"pending", "in_progress"},
        "design_blocked": {"blocked"},
        "implementing": {"in_progress", "implemented"},
        "verifying": {"verifying", "implemented", "in_progress"},
        "waiting_external": {"verifying", "blocked"},
        "waiting_user": {"verifying", "blocked"},
        "repairing": {"verifying", "in_progress"},
        "re_verifying": {"verifying", "in_progress"},
        "completion_review": {"verified", "in_progress"},
        "completion_issues": {"verified", "verifying", "in_progress"},
        "paused": {"in_progress", "verifying", "blocked"},
        "blocked": {"blocked"},
        "completed": {"verified", "superseded"},
    }
    if task_status is not None and task_status not in allowed_task_statuses[lifecycle]:
        raise WorkflowStateError(
            f"task status {task_status!r} is inconsistent with workflow state {lifecycle!r}"
        )
    completion = document.get("completion")
    if not isinstance(completion, dict):
        raise WorkflowStateError("checkpoint completion must be a mapping")
    completion_state = completion.get("state")
    completion_result = completion.get("result")
    if completion_state not in {"not_started", "reviewing", "repairing", "ready", "decided"}:
        raise WorkflowStateError("completion.state is invalid")
    if completion_result not in COMPLETION_RESULTS:
        raise WorkflowStateError("completion.result is invalid")
    if completion_result != state["completion_result"]:
        raise WorkflowStateError("checkpoint completion.result does not match workflow_state.completion_result")
    if lifecycle == "completed" and (completion_state != "decided" or completion_result != "pass"):
        raise WorkflowStateError("completed workflow requires completion decided/pass")
    if lifecycle == "completion_review" and completion_state not in {"not_started", "reviewing", "ready"}:
        raise WorkflowStateError("completion_review requires an active completion state")
    if lifecycle == "completion_issues" and completion_result != "issues":
        raise WorkflowStateError("completion_issues requires completion.result=issues")
    if lifecycle == "blocked" and not document.get("blockers"):
        raise WorkflowStateError("blocked workflow requires checkpoint blockers")
    acceptance = document.get("acceptance", {})
    if not isinstance(acceptance, dict):
        raise WorkflowStateError("checkpoint acceptance must be a mapping")
    for field in ("passed", "failed", "unexecuted"):
        if not isinstance(acceptance.get(field, []), list):
            raise WorkflowStateError(f"acceptance.{field} must be a list")
    if lifecycle == "completed" and (acceptance.get("failed") or acceptance.get("unexecuted")):
        raise WorkflowStateError("completed workflow cannot have failed or unexecuted acceptance")


def validate_verification_run(
    run: dict[str, Any],
    workflow_state: dict[str, Any],
    *,
    checkpoint_id: str | None = None,
) -> dict[str, Any]:
    """Validate a Verification Run's identity and state projection."""
    if not isinstance(run, dict):
        raise WorkflowStateError("verification run must be a mapping")
    if run.get("version") != SCHEMA_VERSION:
        raise WorkflowStateError(f"verification run version must be {SCHEMA_VERSION}")
    for field in ("run_id", "task_id", "checkpoint_id", "workflow_state_ref", "basis_revision"):
        _require_non_empty_string(run.get(field), f"verification run {field}")
    if run["task_id"] != workflow_state["task_id"]:
        raise WorkflowStateError("verification run task_id does not match workflow state")
    if checkpoint_id is not None and run["checkpoint_id"] != checkpoint_id:
        raise WorkflowStateError("verification run checkpoint_id does not match checkpoint")
    if run["workflow_state_ref"] != "checkpoint.workflow_state":
        raise WorkflowStateError("verification run must reference checkpoint.workflow_state")
    if run["basis_revision"] != workflow_state["basis_revision"]:
        raise WorkflowStateError("verification run basis_revision does not match workflow state")
    if run.get("workflow_state_revision") != workflow_state["state_revision"]:
        raise WorkflowStateError("verification run workflow_state_revision is stale")
    run_state = run.get("state")
    if run_state not in {"not_started", "running", "waiting_external", "waiting_user", "evaluating", "repairing", "re_verifying", "paused", "passed", "blocked"}:
        raise WorkflowStateError("verification run state is invalid")
    projection = {
        "not_started": {"unresolved", "contracting", "designing", "design_ready", "implementing"},
        "running": {"verifying"},
        "evaluating": {"verifying", "completion_review"},
        "waiting_external": {"waiting_external"},
        "waiting_user": {"waiting_user"},
        "repairing": {"repairing", "completion_issues"},
        "re_verifying": {"re_verifying"},
        "paused": {"paused"},
        "passed": {"completion_review", "completed"},
        "blocked": {"blocked", "design_blocked"},
    }
    if workflow_state["state"] not in projection[run_state]:
        raise WorkflowStateError(
            f"verification run state {run_state!r} is inconsistent with workflow state {workflow_state['state']!r}"
        )
    return deepcopy(run)


def validate_document(document: dict[str, Any]) -> dict[str, Any]:
    """Validate a snapshot or a checkpoint document containing ``workflow_state``."""
    if not isinstance(document, dict):
        raise WorkflowStateError("workflow document must be a mapping")
    if "workflow_state" not in document:
        if "state" in document:
            return validate_snapshot(document)
        raise WorkflowStateError("legacy/current workflow document must contain workflow_state")

    state = validate_snapshot(document["workflow_state"])
    active_task = document.get("active_task")
    if active_task is not None and active_task != state["task_id"]:
        raise WorkflowStateError("checkpoint active_task does not match workflow_state.task_id")
    basis_revision = document.get("basis_revision")
    if basis_revision is not None and basis_revision != state["basis_revision"]:
        raise WorkflowStateError("checkpoint basis_revision does not match workflow_state.basis_revision")
    _validate_checkpoint_consistency(document, state)
    return state


def allowed_events(state: str) -> tuple[str, ...]:
    """Return normalized events accepted from a state."""
    if state not in TRANSITIONS:
        raise WorkflowStateError(f"unknown workflow state: {state!r}")
    return tuple(TRANSITIONS[state])


def apply_event(snapshot: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    """Apply one event and return a new validated snapshot."""
    current = validate_snapshot(snapshot)
    if not isinstance(event, dict):
        raise WorkflowStateError("event must be a mapping")
    event_type = event.get("type")
    if event_type not in EVENTS:
        raise WorkflowStateError(f"unknown workflow event: {event_type!r}")
    current_state = current["state"]
    next_state = TRANSITIONS[current_state].get(event_type)
    if next_state is None:
        raise WorkflowStateError(f"event {event_type!r} is not allowed from {current_state!r}")
    if next_state == "__resume__":
        next_state = current.get("resume_state")
        if next_state is None:
            raise WorkflowStateError(f"{current_state} has no resume_state")
    if event.get("from_state") not in (None, current_state):
        raise WorkflowStateError("event from_state does not match current state")
    if event.get("to_state") not in (None, next_state):
        raise WorkflowStateError("event to_state does not match resolved transition")
    if event.get("basis_revision") not in (None, current["basis_revision"]):
        raise WorkflowStateError("event basis_revision does not match current snapshot")
    actor = event.get("actor", "main-agent")
    _require_non_empty_string(actor, "event actor")
    if event.get("event_id") is not None:
        _require_non_empty_string(event["event_id"], "event_id")
    if event.get("observed_at") is not None:
        _require_non_empty_string(event["observed_at"], "observed_at")
    expected_actor = GATE_EVENT_ACTORS.get(event_type)
    if expected_actor is not None and actor != expected_actor:
        raise WorkflowStateError(f"event {event_type!r} must be emitted by {expected_actor}")
    if event_type == "design_required" and current["contract_frozen_revision"] != current["contract_revision"]:
        raise WorkflowStateError("design_required requires the current contract revision to be frozen")
    if event_type == "implementation_authorized" and actor != "user":
        raise WorkflowStateError("implementation_authorized must be emitted by user")
    if event_type == "resume" and actor != "user":
        raise WorkflowStateError("resume must be emitted by user")
    if event_type == "implementation_authorized" and current["mode"] != "implementation":
        raise WorkflowStateError("implementation_authorized requires mode=implementation")
    if event_type == "implementation_authorized" and current["contract_frozen_revision"] != current["contract_revision"]:
        raise WorkflowStateError("implementation_authorized requires the current contract revision to be frozen")
    if event_type == "implementation_authorized" and current["design_gate"] not in {"not_required", "pass"}:
        raise WorkflowStateError("implementation_authorized requires design_gate=not_required or pass")
    if event_type == "design_only_stop" and current["mode"] != "design_only":
        raise WorkflowStateError("design_only_stop requires mode=design_only")

    evidence_refs = event.get("evidence_refs", [])
    if not isinstance(evidence_refs, list) or any(
        not isinstance(item, str) or not item.strip() for item in evidence_refs
    ):
        raise WorkflowStateError("event evidence_refs must be a list of non-empty strings")
    if event_type in GATE_EVENT_ACTORS and not evidence_refs:
        raise WorkflowStateError(f"event {event_type!r} requires Gate evidence_refs")
    recovery_events = {
        "external_wait",
        "user_wait",
        "design_blocked",
        "completion_blocked",
        "pause",
        "blocked",
    }
    resume_conditions = event.get("resume_conditions", [])
    if not isinstance(resume_conditions, list) or any(
        not isinstance(item, str) or not item.strip() for item in resume_conditions
    ):
        raise WorkflowStateError("event resume_conditions must be a list of non-empty strings")
    if event_type in recovery_events and not resume_conditions:
        raise WorkflowStateError(f"event {event_type!r} requires resume_conditions")
    if event_type in {"design_blocked", "completion_blocked", "pause", "blocked"}:
        _require_non_empty_string(event.get("reason"), "event reason")

    updated = deepcopy(current)
    updated["state"] = next_state
    updated["state_revision"] += 1
    if current_state in RECOVERABLE_STATES and next_state not in RECOVERABLE_STATES:
        updated["stop_reason"] = None
        updated["resume_state"] = None
        updated["resume_conditions"] = []
    updated["last_event"] = {
        "event_id": event.get("event_id", f"EV-{updated['state_revision']:04d}"),
        "type": event_type,
        "actor": actor,
        "from_state": current_state,
        "to_state": next_state,
        "resume_state": current.get("resume_state") if event_type == "resume" else None,
        "basis_revision": current["basis_revision"],
        "observed_at": event.get("observed_at", datetime.now(timezone.utc).isoformat()),
        "evidence_refs": list(evidence_refs),
    }
    if event_type in recovery_events:
        updated["resume_conditions"] = list(resume_conditions)
    if event_type in {"pause", "blocked", "completion_blocked"}:
        updated["resume_state"] = (
            TRANSITIONS[current_state]["resume"]
            if current_state in WAITING_STATES
            else current_state
        )
    if event_type == "contract_frozen":
        updated["contract_frozen_revision"] = current["contract_revision"]
    elif event_type == "pause":
        updated["stop_reason"] = event["reason"]
    elif event_type == "design_required":
        updated["design_gate"] = "pending"
    elif event_type == "design_passed":
        updated["design_gate"] = "pass"
    elif event_type == "design_blocked":
        updated["design_gate"] = "blocked"
        updated["stop_reason"] = event["reason"]
    elif event_type == "completion_passed":
        updated["completion_result"] = "pass"
    elif event_type == "completion_issues":
        updated["completion_result"] = "issues"
    elif event_type == "completion_blocked":
        updated["completion_result"] = "blocked"
        updated["stop_reason"] = event["reason"]
    elif event_type == "blocked":
        updated["stop_reason"] = event["reason"]
    elif event_type == "resume":
        updated["stop_reason"] = None
        updated["resume_state"] = None
        updated["resume_conditions"] = []
    if event_type == "completion_started":
        updated["completion_result"] = None
    return validate_snapshot(updated)
