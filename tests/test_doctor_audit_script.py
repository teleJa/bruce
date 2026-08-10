import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "doctor" / "scripts" / "audit_codex_thread.py"


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
