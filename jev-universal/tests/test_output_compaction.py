import stat
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

# ruff: noqa: E402 — the hook package is intentionally loaded from the plugin root.
from hooks.post_tool_use import process_event, should_compact
from scripts.jev_output_recall import select_lines
from scripts.jev_output_store import (
    OUTPUT_TTL_SECONDS,
    cleanup_stale,
    read_output,
    store_output,
)


class OutputCompactionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.session_id = "test-session-id"
        self.event = {
            "tool_name": "Bash",
            "tool_input": {"command": "sed -n '1,500p' src/example.py"},
            "tool_response": "\n".join(f"line {index}" for index in range(1, 101)),
            "session_id": self.session_id,
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_large_output_is_replaced_with_preview_and_recoverable_id(self):
        result = process_event(self.event, self.root)
        self.assertIsNotNone(result)
        self.assertIs(result["continue"], False)
        self.assertIn("command has already run", result["stopReason"])
        output_id = result["stopReason"].split("recall id `", 1)[1].split("`", 1)[0]
        self.assertEqual(read_output(output_id, self.root), self.event["tool_response"])
        session_dir = next(self.root.glob("session-*"))
        output_file = next(session_dir.glob("*.txt"))
        self.assertEqual(stat.S_IMODE(self.root.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(session_dir.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(output_file.stat().st_mode), 0o600)

    def test_store_refuses_symlinked_root(self):
        target = self.root / "target"
        target.mkdir()
        store_link = self.root / "store-link"
        store_link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(OSError, "symlinked output store"):
            store_output(self.session_id, self.event["tool_response"], store_link)
        self.assertEqual(list(target.iterdir()), [])

    def test_small_failure_and_sensitive_output_pass_through(self):
        self.assertFalse(should_compact("pytest -q", "1 failed\nAssertionError: broken"))
        self.assertFalse(should_compact("cat secret.txt", "api_key=" + "x" * 24 + "\n" * 40))
        small = {**self.event, "tool_response": "short"}
        self.assertIsNone(process_event(small, self.root))

    def test_non_bash_tool_passes_through(self):
        self.assertIsNone(process_event({**self.event, "tool_name": "Read"}, self.root))

    def test_output_remains_recallable_after_session_is_over_and_expires(self):
        result = process_event(self.event, self.root)
        output_id = result["stopReason"].split("recall id `", 1)[1].split("`", 1)[0]
        # Session end has no cleanup path; data expires by TTL instead.
        self.assertEqual(read_output(output_id, self.root), self.event["tool_response"])
        output_path = next(self.root.glob("session-*/*.txt"))
        old_time = output_path.stat().st_mtime - OUTPUT_TTL_SECONDS - 1
        import os

        os.utime(output_path, (old_time, old_time))
        with self.assertRaisesRegex(FileNotFoundError, "expired"):
            read_output(output_id, self.root)

    def test_test_failures_and_private_keys_are_never_compacted(self):
        failure = "header\n" + "detail\n" * 40 + "FAILED test_example.py\n"
        self.assertFalse(should_compact("pytest -q", failure))
        private_key = "-----BEGIN PRIVATE KEY-----\n" + ("A" * 50) + "\n" * 40
        self.assertFalse(should_compact("cat key.pem", private_key))
        bearer = "Authorization: Bearer " + ("a" * 32) + "\n" * 40
        self.assertFalse(should_compact("cat config", bearer))

    def test_recall_can_select_lines_or_search(self):
        text = "alpha\nbeta marker\ngamma\nbeta again"
        self.assertEqual(
            select_lines(text, "2-3", None), "matched 2 of 4 lines\n2: beta marker\n3: gamma"
        )
        self.assertIn("2: beta marker\n4: beta again", select_lines(text, None, "beta"))

    def test_stale_cleanup_removes_only_old_valid_session_directories(self):
        old_dir = self.root / ("session-" + "a" * 16)
        other_dir = self.root / "session-not-a-valid-id"
        old_dir.mkdir()
        other_dir.mkdir()
        old_time = 1
        import os

        os.utime(old_dir, (old_time, old_time))
        os.utime(other_dir, (old_time, old_time))
        cleanup_stale(self.root, max_age_seconds=1)
        self.assertFalse(old_dir.exists())
        self.assertTrue(other_dir.exists())

    def test_stale_cleanup_removes_expired_files_even_in_recent_sessions(self):
        _, output_path = store_output(self.session_id, "expired", self.root)
        expired = output_path.stat().st_mtime - OUTPUT_TTL_SECONDS - 1
        import os

        os.utime(output_path, (expired, expired))
        cleanup_stale(self.root)
        self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
