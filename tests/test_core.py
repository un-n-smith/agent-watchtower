from __future__ import annotations

import contextlib
import io
import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from agent_watchtower.cli import main
from agent_watchtower.store import WatchtowerStore
from agent_watchtower.worker import add_task, init_runtime, worker_run, worker_status


class CoreLoopTests(unittest.TestCase):
    def test_readme_opens_with_user_scene_and_pip_install_path(self) -> None:
        root = Path(__file__).resolve().parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        packaging = (root / "PACKAGING.md").read_text(encoding="utf-8")
        agent_rules = (root / "AGENTS.md").read_text(encoding="utf-8")
        landing_page = (root / "docs" / "landing-page.zh.md").read_text(encoding="utf-8")
        demo = (root / "docs" / "interrupted-recovery-demo.md").read_text(encoding="utf-8")
        demo_zh = (root / "docs" / "interrupted-recovery-demo.zh-CN.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Agent 记得做到哪了", readme)
        self.assertIn("60 秒看到价值", readme)
        self.assertIn("Two Readers", readme)
        self.assertIn("pip install .", readme)
        self.assertIn("brew tap un-n-smith/tap", readme)
        self.assertIn("brew install agent-watchtower", readme)
        self.assertIn("agent-watchtower init", readme)
        self.assertIn("Coding agents read `AGENTS.md`", readme)
        self.assertIn("docs/landing-page.zh.md", readme)
        self.assertIn("docs/interrupted-recovery-demo.md", readme)
        self.assertIn("docs/interrupted-recovery-demo.zh-CN.md", readme)
        self.assertIn("工作交接本", landing_page)
        self.assertIn("别让 AI 干活断片", landing_page)
        self.assertIn("它会不会一直等我？", landing_page)
        self.assertIn("Interrupted Recovery Demo", demo)
        self.assertIn("not full autonomy", demo)
        self.assertIn("中断恢复演示", demo_zh)
        self.assertIn("再醒来不从零开始", demo_zh)
        self.assertIn("worker-status", agent_rules)
        self.assertIn("When The Human Does Not Reply", agent_rules)
        self.assertIn("work notebook", agent_rules)
        self.assertIn("Do not claim work is complete", agent_rules)
        self.assertIn("pip install .", packaging)
        self.assertIn("agent-watchtower --help", packaging)

    def test_github_pages_site_files_are_present(self) -> None:
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        cname = (root / "CNAME").read_text(encoding="utf-8").strip()

        self.assertEqual(cname, "www.adgwmuren.top")
        self.assertIn("<title>Agent Watchtower</title>", index)
        self.assertIn("Let coding agents resume without starting over.", index)
        self.assertIn("No background service", index)
        self.assertIn("brew install agent-watchtower", index)
        self.assertIn("github.com/un-n-smith/agent-watchtower", index)

    def test_pyproject_maps_distribution_to_runtime_module(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(pyproject["project"]["name"], "agent-watchtower-core")
        self.assertEqual(pyproject["project"]["scripts"]["agent-watchtower"], "agent_watchtower.cli:main")
        self.assertEqual(pyproject["tool"]["uv"]["build-backend"]["module-name"], "agent_watchtower")

    def test_init_status_run_and_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--root", tmp, "init"]), 0)

            status = worker_status(WatchtowerStore(root))
            self.assertTrue(status["runnable"])
            self.assertEqual(status["open_task_count"], 1)

            run = worker_run(WatchtowerStore(root))
            self.assertEqual(run["action"], "completed_task")
            self.assertTrue(Path(run["artifact_path"]).exists())

            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(["--root", tmp, "artifact-path"]), 0)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["artifact_path"], run["artifact_path"])
            self.assertTrue(payload["exists"])

    def test_task_add_rejects_unknown_goal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--root", tmp, "init"])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = main(
                    [
                        "--root",
                        tmp,
                        "task-add",
                        "--goal-id",
                        "missing",
                        "--title",
                        "Do work",
                        "--next-action",
                        "write artifact",
                    ]
                )
            payload = json.loads(out.getvalue())
            self.assertEqual(code, 1)
            self.assertEqual(payload["action"], "blocked")
            self.assertEqual(payload["reason"], "unknown_or_inactive_goal")

    def test_worker_status_reports_invalid_goals_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_runtime(WatchtowerStore(root))
            (root / "goals.json").write_text("{", encoding="utf-8")
            status = worker_status(WatchtowerStore(root))
            self.assertFalse(status["runnable"])
            self.assertEqual(status["state_health"], "blocked")
            self.assertEqual(status["reason"], "invalid_runtime_state")
            self.assertEqual(status["diagnostics"][0]["code"], "invalid_goals_json")

    def test_worker_status_reports_invalid_row_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = WatchtowerStore(root)
            init_runtime(store)

            (root / "work-queue.json").write_text(
                json.dumps(
                    [
                        {
                            "id": "task-bad-priority",
                            "goal_id": "goal-watchtower-demo",
                            "title": "Bad priority",
                            "next_action": "should block",
                            "created_at": "2026-01-01T00:00:00Z",
                            "updated_at": "2026-01-01T00:00:00Z",
                            "status": "open",
                            "priority": "high",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            status = worker_status(store)
            self.assertFalse(status["runnable"])
            self.assertEqual(status["state_health"], "blocked")
            self.assertEqual(status["reason"], "invalid_runtime_state")
            self.assertEqual(status["diagnostics"][0]["code"], "invalid_work_queue_json")

    def test_unsluggable_generated_task_ids_are_stable_and_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WatchtowerStore(Path(tmp))
            init_runtime(store)
            first = add_task(store, title="!!!", next_action="write punctuation task")
            second = add_task(store, title="全中文任务", next_action="write unicode task")
            duplicate = add_task(store, title="全中文任务", next_action="write unicode task")

            self.assertEqual(first["action"], "added")
            self.assertEqual(second["action"], "added")
            self.assertEqual(duplicate["action"], "duplicate")
            self.assertNotEqual(first["task"]["id"], second["task"]["id"])

    def test_help_exposes_only_public_commands(self) -> None:
        out = io.StringIO()
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(out):
                main(["--help"])
        self.assertEqual(raised.exception.code, 0)
        help_text = out.getvalue()
        for command in ["init", "task-add", "worker-status", "worker-run", "artifact-path"]:
            self.assertIn(command, help_text)
        self.assertNotIn("--bridge-root", help_text)
        self.assertNotIn("internal", help_text.lower())


if __name__ == "__main__":
    unittest.main()
