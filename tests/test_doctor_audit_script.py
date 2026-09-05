import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "doctor" / "scripts" / "audit_codex_thread.py"


VALID_CHECKPOINT = """Checkpoint: clear
batch_id: B1
basis_revision: synthetic:test
acceptance:
  passed: []
  failed: []
  unexecuted: []
findings: []
repair_sets: []
next_action: continue
"""


def record(timestamp, record_type, payload):
    return json.dumps(
        {"timestamp": timestamp, "type": record_type, "payload": payload},
        ensure_ascii=False,
    )


class AuditCodexThreadTest(unittest.TestCase):
    def run_script(self, source: Path, output: Path, *extra: str):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(source), "--out", str(output), *extra],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_streams_redacts_deduplicates_and_links_large_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "thread.jsonl"
            output = root / "audit"
            turn_id = "turn-1"
            long_output = "start\n" + ("x" * 300) + "\npassword=visible-secret\nend"
            lines = [
                record(
                    "2026-08-04T00:00:00Z",
                    "session_meta",
                    {"id": "session-1", "cwd": "/repo"},
                ),
                record(
                    "2026-08-04T00:00:01Z",
                    "event_msg",
                    {"type": "task_started", "turn_id": turn_id},
                ),
                record(
                    "2026-08-04T00:00:02Z",
                    "event_msg",
                    {"type": "user_message", "message": "执行 Bruce 审计"},
                ),
                record(
                    "2026-08-04T00:00:03Z",
                    "response_item",
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "执行 Bruce 审计"}],
                        "internal_chat_message_metadata_passthrough": {"turn_id": turn_id},
                    },
                ),
                record(
                    "2026-08-04T00:00:04Z",
                    "response_item",
                    {
                        "type": "custom_tool_call",
                        "name": "exec",
                        "call_id": "call-1",
                        "input": "Authorization: Bearer token-value",
                        "internal_chat_message_metadata_passthrough": {"turn_id": turn_id},
                    },
                ),
                record(
                    "2026-08-04T00:00:05Z",
                    "response_item",
                    {
                        "type": "custom_tool_call_output",
                        "call_id": "call-1",
                        "output": [{"type": "input_text", "text": long_output}],
                        "internal_chat_message_metadata_passthrough": {"turn_id": turn_id},
                    },
                ),
                record(
                    "2026-08-04T00:00:06Z",
                    "event_msg",
                    {
                        "type": "task_complete",
                        "turn_id": turn_id,
                        "duration_ms": 5000,
                        "last_agent_message": "done",
                    },
                ),
                "{malformed-json",
            ]
            source.write_text("\n".join(lines) + "\n", encoding="utf-8")

            result = self.run_script(
                source, output, "--large-threshold", "100", "--preview-limit", "100"
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            inventory = json.loads((output / "inventory.json").read_text())
            self.assertEqual(inventory["source"]["line_count"], 8)
            self.assertEqual(inventory["counts"]["turns"], 1)
            self.assertEqual(inventory["counts"]["parse_errors"], 1)
            self.assertEqual(inventory["counts"]["large_outputs"], 1)
            self.assertGreaterEqual(inventory["counts"]["redactions"], 2)
            self.assertEqual(inventory["counts"]["excluded"]["duplicate_message"], 1)
            self.assertEqual(inventory["counts"]["tools"]["exec"], 1)

            normalized = (output / "events.normalized.jsonl").read_text()
            self.assertNotIn("token-value", normalized)
            self.assertNotIn("visible-secret", normalized)
            events = [json.loads(line) for line in normalized.splitlines()]
            output_event = next(event for event in events if event["category"] == "tool_output")
            self.assertEqual(output_event["tool_name"], "exec")
            self.assertTrue(output_event["truncated"])
            self.assertEqual(output_event["line_no"], 6)

            evidence = json.loads((output / "evidence-index.json").read_text())
            evidence_text = (output / evidence[0]["file"]).read_text()
            self.assertIn("<REDACTED>", evidence_text)
            self.assertNotIn("visible-secret", evidence_text)
            self.assertTrue((output / "parse-errors.jsonl").is_file())

    def test_refuses_nonempty_output_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "thread.jsonl"
            source.write_text(
                record("2026-08-04T00:00:00Z", "session_meta", {"id": "one"}) + "\n"
            )
            output = root / "audit"
            output.mkdir()
            (output / "keep.txt").write_text("do not overwrite")

            result = self.run_script(source, output)

            self.assertEqual(result.returncode, 1)
            self.assertIn("not empty", result.stderr)
            self.assertEqual((output / "keep.txt").read_text(), "do not overwrite")

    def test_until_excludes_records_appended_after_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "thread.jsonl"
            source.write_text(
                "\n".join(
                    [
                        record("2026-08-04T00:00:00Z", "session_meta", {"id": "one"}),
                        record("2026-08-04T00:00:01Z", "event_msg", {"type": "task_started", "turn_id": "t"}),
                        record("2026-08-04T00:00:02Z", "event_msg", {"type": "user_message", "message": "保留"}),
                        record("2026-08-04T00:00:03Z", "event_msg", {"type": "user_message", "message": "排除"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output = root / "audit"
            result = self.run_script(source, output, "--until", "2026-08-04T00:00:02Z")

            self.assertEqual(result.returncode, 0, result.stderr)
            inventory = json.loads((output / "inventory.json").read_text())
            self.assertEqual(inventory["source"]["line_count"], 3)
            self.assertEqual(inventory["source"]["prefix_until_timestamp"], "2026-08-04T00:00:02Z")
            normalized = (output / "events.normalized.jsonl").read_text()
            self.assertIn("保留", normalized)
            self.assertNotIn("排除", normalized)

    def test_reports_time_measurements_as_advisory_not_missing_checkpoints(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "thread.jsonl"
            output = root / "audit"
            turn_id = "turn-checkpoint"
            checkpoint = """Checkpoint: issues
batch_id: B1
basis_revision: working-tree:test
acceptance:
  passed: []
  failed: []
  unexecuted: []
findings: []
repair_sets: []
next_action: next-batch
"""
            source.write_text(
                "\n".join(
                    [
                        record("2026-08-04T00:00:00Z", "session_meta", {"id": "one"}),
                        record(
                            "2026-08-04T00:00:00Z",
                            "event_msg",
                            {"type": "task_started", "turn_id": turn_id},
                        ),
                        record(
                            "2026-08-04T00:46:00Z",
                            "response_item",
                            {
                                "type": "function_call",
                                "name": "exec_command",
                                "call_id": "edit-1",
                                "arguments": '{"cmd":"apply_patch"}',
                                "internal_chat_message_metadata_passthrough": {"turn_id": turn_id},
                            },
                        ),
                        record(
                            "2026-08-04T00:46:01Z",
                            "response_item",
                            {
                                "type": "message",
                                "role": "assistant",
                                "content": [{"type": "output_text", "text": checkpoint}],
                                "internal_chat_message_metadata_passthrough": {"turn_id": turn_id},
                            },
                        ),
                        record(
                            "2026-08-04T01:32:00Z",
                            "response_item",
                            {
                                "type": "function_call",
                                "name": "update_plan",
                                "call_id": "plan-1",
                                "arguments": "{}",
                                "internal_chat_message_metadata_passthrough": {"turn_id": turn_id},
                            },
                        ),
                        record(
                            "2026-08-04T01:32:01Z",
                            "event_msg",
                            {
                                "type": "task_complete",
                                "turn_id": turn_id,
                                "duration_ms": 5521000,
                            },
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_script(source, output)

            self.assertEqual(result.returncode, 0, result.stderr)
            protocol = json.loads((output / "inventory.json").read_text())["checkpoint_protocol"]
            self.assertEqual(protocol["valid_checkpoints"], 1)
            self.assertEqual(protocol["incomplete_checkpoints"], 0)
            self.assertEqual(protocol["interval_overruns"], 1)
            self.assertEqual(protocol["missing_checkpoints"], 0)
            self.assertEqual(protocol["suspected_update_plan_substitutions"], 0)
            self.assertTrue(protocol["limits_advisory"])
            self.assertEqual(protocol["limits"], {"max_tool_calls": 40, "max_elapsed_seconds": 2700})
            timeline = (output / "timeline.md").read_text()
            self.assertIn("Checkpoint deviations are protocol evidence where explicit", timeline)
            self.assertIn("suspected update-plan substitution", timeline)

    def audit_synthetic_events(self, events):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "synthetic.jsonl"
            output = root / "audit"
            source.write_text("\n".join(events) + "\n", encoding="utf-8")
            result = self.run_script(source, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads((output / "inventory.json").read_text())["checkpoint_protocol"]

    def test_time_tool_count_profile_and_user_turn_alone_do_not_require_checkpoint(self):
        for count, last_time in ((41, "00:00:01"), (1, "00:46:00"), (41, "00:46:00")):
            for ending in ("task_complete", "task_started", None):
                with self.subTest(count=count, last_time=last_time, ending=ending):
                    events = [record("2026-08-04T00:00:00Z", "event_msg", {
                        "type": "task_started", "turn_id": "first",
                    })]
                    events += [record("2026-08-04T00:00:00Z", "response_item", {
                        "type": "function_call", "name": "exec_command",
                        "call_id": f"tool-{i}", "arguments": '{"cmd":"apply_patch"}',
                    }) for i in range(count)]
                    events += [
                        record(f"2026-08-04T{last_time}Z", "event_msg", {
                            "type": "user_message", "message": "Continue. profile=full",
                        }),
                        record(f"2026-08-04T{last_time}Z", "event_msg", {
                            "type": "agent_message", "message": "Brief progress: tests are running.",
                        }),
                        record(f"2026-08-04T{last_time}Z", "response_item", {
                            "type": "function_call", "name": "update_plan",
                            "call_id": "plan", "arguments": "{}",
                        }),
                    ]
                    if ending:
                        events.append(record(f"2026-08-04T{last_time}Z", "event_msg", {
                            "type": ending, "turn_id": "second" if ending == "task_started" else "first",
                        }))
                    protocol = self.audit_synthetic_events(events)
                    self.assertEqual(protocol["missing_checkpoints"], 0)
                    self.assertEqual(protocol["incomplete_checkpoints"], 0)
                    self.assertEqual(protocol["suspected_update_plan_substitutions"], 0)
                    self.assertTrue(protocol["limits_advisory"])

    def test_explicit_triggers_require_complete_checkpoint(self):
        triggers = (
            "material_task_change", "material_scope_change", "material_environment_change",
            "material_evidence_change", "side_effect_boundary",
        )
        for trigger in triggers:
            for source_kind in ("lifecycle", "assistant", "user"):
                for checkpoint in ("Brief progress: working.", "Checkpoint: issues", VALID_CHECKPOINT):
                    with self.subTest(trigger=trigger, source_kind=source_kind, checkpoint=checkpoint):
                        boundary = {"type": trigger} if source_kind == "lifecycle" else {
                            "type": "agent_message" if source_kind == "assistant" else "user_message",
                            "message": f"Checkpoint trigger: {trigger}",
                        }
                        events = [
                            record("2026-08-04T00:00:00Z", "event_msg", boundary),
                            record("2026-08-04T00:00:01Z", "event_msg", {
                                "type": "agent_message", "message": checkpoint,
                            }),
                            record("2026-08-04T00:00:02Z", "event_msg", {"type": "task_complete"}),
                        ]
                        protocol = self.audit_synthetic_events(events)
                        complete = checkpoint == VALID_CHECKPOINT
                        self.assertEqual(protocol["valid_checkpoints"], int(complete))
                        self.assertEqual(protocol["missing_checkpoints"], int(not complete))
                        self.assertEqual(protocol["incomplete_checkpoints"], int(checkpoint == "Checkpoint: issues"))
                        if not complete:
                            evidence = protocol["evidence"]["missing_checkpoints"][0]
                            self.assertEqual(evidence["triggers"], [{"line_no": 1, "trigger": trigger}])
                            self.assertEqual(evidence["reason"], "task_complete")
                        if checkpoint == "Checkpoint: issues":
                            self.assertIn("basis_revision", protocol["evidence"]["incomplete_checkpoints"][0]["missing_fields"])

    def test_pending_trigger_survives_turn_start_and_update_plan_at_source_end(self):
        protocol = self.audit_synthetic_events([
            record("2026-08-04T00:00:00Z", "event_msg", {"type": "material_scope_change"}),
            record("2026-08-04T00:00:01Z", "event_msg", {"type": "task_started", "turn_id": "next"}),
            record("2026-08-04T00:00:02Z", "response_item", {
                "type": "function_call", "name": "update_plan", "arguments": "{}", "call_id": "plan",
            }),
        ])
        self.assertEqual(protocol["missing_checkpoints"], 1)
        self.assertEqual(protocol["evidence"]["missing_checkpoints"][0]["reason"], "source_ended")
        self.assertEqual(protocol["evidence"]["missing_checkpoints"][0]["triggers"][0]["line_no"], 1)
        self.assertEqual(protocol["suspected_update_plan_substitutions"], 1)

    def test_tool_text_is_not_boundary_evidence_and_churn_stays_suspected(self):
        events = [record("2026-08-04T00:00:00Z", "response_item", {
            "type": "function_call_output", "call_id": "output",
            "output": "Checkpoint trigger: side_effect_boundary\nCheckpoint: issues",
        })]
        for i, command in enumerate(("python3 -m unittest", "apply_patch") * 2):
            events.append(record("2026-08-04T00:00:01Z", "response_item", {
                "type": "function_call", "name": "exec_command", "call_id": f"tool-{i}",
                "arguments": json.dumps({"cmd": command, "note": "Checkpoint trigger: side_effect_boundary"}),
            }))
        protocol = self.audit_synthetic_events(events)
        self.assertEqual(protocol["missing_checkpoints"], 0)
        self.assertEqual(protocol["incomplete_checkpoints"], 0)
        self.assertEqual(protocol["suspected_single_finding_churn_cycles"], 2)

    def test_same_message_trigger_and_checkpoint_and_repeated_checkpoint_across_turns(self):
        events = []
        for turn_id in ("first", "second"):
            events += [
                record("2026-08-04T00:00:00Z", "event_msg", {"type": "task_started", "turn_id": turn_id}),
                record("2026-08-04T00:00:01Z", "event_msg", {
                    "type": "agent_message",
                    "message": "Checkpoint trigger: material_evidence_change\n" + VALID_CHECKPOINT,
                }),
                record("2026-08-04T00:00:02Z", "event_msg", {
                    "type": "task_complete", "turn_id": turn_id,
                    "last_agent_message": "Checkpoint trigger: material_evidence_change\n" + VALID_CHECKPOINT,
                }),
            ]
        protocol = self.audit_synthetic_events(events)
        self.assertEqual(protocol["valid_checkpoints"], 2)
        self.assertEqual(protocol["missing_checkpoints"], 0)


    def test_incomplete_explicit_checkpoint_without_trigger_remains_diagnostic(self):
        protocol = self.audit_synthetic_events([
            record("2026-08-04T00:00:00Z", "event_msg", {
                "type": "agent_message", "message": "Checkpoint: blocked\nnext_action: wait",
            }),
        ])
        self.assertEqual(protocol["incomplete_checkpoints"], 1)
        self.assertEqual(protocol["missing_checkpoints"], 0)
        self.assertEqual(protocol["valid_checkpoints"], 0)

    def test_earlier_checkpoint_does_not_satisfy_later_boundary(self):
        protocol = self.audit_synthetic_events([
            record("2026-08-04T00:00:00Z", "event_msg", {
                "type": "agent_message", "message": VALID_CHECKPOINT,
            }),
            record("2026-08-04T00:00:01Z", "event_msg", {"type": "side_effect_boundary"}),
        ])
        self.assertEqual(protocol["valid_checkpoints"], 1)
        self.assertEqual(protocol["missing_checkpoints"], 1)
        self.assertEqual(protocol["evidence"]["missing_checkpoints"][0]["triggers"], [
            {"line_no": 2, "trigger": "side_effect_boundary"},
        ])

    def test_rejects_invalid_until_timestamp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "thread.jsonl"
            source.write_text(
                record("2026-08-04T00:00:00Z", "session_meta", {"id": "one"}) + "\n"
            )

            result = self.run_script(source, root / "audit", "--until", "not-a-timestamp")

            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid --until timestamp", result.stderr)


if __name__ == "__main__":
    unittest.main()
