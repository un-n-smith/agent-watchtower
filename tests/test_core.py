from __future__ import annotations

import contextlib
import io
import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from agent_watchtower import __version__
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

        self.assertIn("agent can check where to resume", readme)
        self.assertIn("Run a local demo", readme)
        self.assertIn("Simplified Chinese](README.zh-CN.md)", readme)
        self.assertIn("Two Readers", readme)
        self.assertIn("http://www.adgwmuren.top/zh-CN.html", readme)
        self.assertIn("pip install .", readme)
        self.assertIn("pip install agent-watchtower-core", readme)
        self.assertIn("Supported Systems", readme)
        self.assertIn("macOS", readme)
        self.assertIn("Windows", readme)
        self.assertNotIn("PyPI publishing is being prepared", readme)
        self.assertIn("brew tap un-n-smith/tap", readme)
        self.assertIn("brew install agent-watchtower", readme)
        self.assertIn("agent-watchtower init", readme)
        self.assertIn("Coding agents read [AGENTS.md]", readme)
        self.assertIn("docs/interrupted-recovery-demo.md", readme)
        self.assertIn("README.zh-CN.md", readme)
        self.assertIn("工作交接本", landing_page)
        self.assertIn("别让 AI 干活断片", landing_page)
        self.assertIn("它会不会一直等我？", landing_page)
        self.assertIn("Interrupted Recovery Demo", demo)
        self.assertIn("not full autonomy", demo)
        self.assertIn("中断恢复演示", demo_zh)
        self.assertIn("再醒来不从零开始", demo_zh)
        self.assertIn("worker-status", agent_rules)
        self.assertIn("worker-run --result", agent_rules)
        self.assertIn("AGENTS.structured.md", readme)
        self.assertIn("When The Human Does Not Reply", agent_rules)
        self.assertIn("work notebook", agent_rules)
        self.assertIn("Do not claim work is complete", agent_rules)
        self.assertIn("pip install .", packaging)
        self.assertIn("agent-watchtower --help", packaging)

    def test_pypi_publish_workflow_uses_trusted_publishing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "publish-pypi.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("pypa/gh-action-pypi-publish@release/v1", workflow)
        self.assertIn("python -B -m unittest discover -s tests -q", workflow)
        self.assertIn("./scripts/release_preflight.sh", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("environment: pypi", workflow)
        self.assertNotIn("PYPI_TOKEN", workflow)

    def test_github_pages_site_files_are_present(self) -> None:
        root = Path(__file__).resolve().parents[1]
        index = (root / "index.html").read_text(encoding="utf-8")
        zh_page = (root / "zh-CN.html").read_text(encoding="utf-8")
        cname = (root / "CNAME").read_text(encoding="utf-8").strip()

        self.assertEqual(cname, "www.adgwmuren.top")
        self.assertIn("<title>Agent Watchtower</title>", index)
        self.assertIn("Let coding agents resume without starting over.", index)
        self.assertIn("No background service", index)
        self.assertIn("zh-CN.html", index)
        self.assertIn("Run a local demo", index)
        self.assertIn("Current version: 0.1.4", index)
        self.assertIn("pip install agent-watchtower-core", index)
        self.assertIn("macOS, Linux, and Windows", index)
        self.assertIn("brew install agent-watchtower", index)
        self.assertIn("github.com/un-n-smith/agent-watchtower", index)
        self.assertIn("<html lang=\"zh-CN\">", zh_page)
        self.assertIn("让 AI 编程助手回来接着干", zh_page)
        self.assertIn("当前版本：0.1.4", zh_page)
        self.assertIn("快速跑通", zh_page)
        self.assertIn("macOS、Linux、Windows", zh_page)
        self.assertNotIn("一分钟试用", zh_page)
        self.assertIn("python3 -m pip install agent-watchtower-core", zh_page)

    def test_pyproject_maps_distribution_to_runtime_module(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(pyproject["project"]["name"], "agent-watchtower-core")
        self.assertEqual(pyproject["project"]["version"], "0.1.4")
        self.assertEqual(__version__, "0.1.4")
        self.assertEqual(pyproject["project"]["scripts"]["agent-watchtower"], "agent_watchtower.cli:main")
        self.assertEqual(pyproject["tool"]["uv"]["build-backend"]["module-name"], "agent_watchtower")
        self.assertIn("Repository", pyproject["project"]["urls"])
        self.assertIn("ai-agents", pyproject["project"]["keywords"])

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

    def test_worker_run_records_result_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = WatchtowerStore(root)
            init_runtime(store)
            added = add_task(
                store,
                title="Inspect repository state",
                next_action="run git status and summarize findings",
            )
            self.assertEqual(added["action"], "added")

            result = "Found 3 files with pending documentation updates."
            run = worker_run(store, result=result)
            artifact = Path(run["artifact_path"]).read_text(encoding="utf-8")
            self.assertIn(result, artifact)
            self.assertEqual(run["task_id"], added["task"]["id"])
            self.assertIn("result_excerpt", run)

    def test_in_progress_task_is_runnable_before_open_demo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = WatchtowerStore(Path(tmp))
            init_runtime(store)
            added = add_task(
                store,
                title="Continue interrupted bug fix",
                next_action="finish the half-done local verification",
                status="in_progress",
            )
            self.assertEqual(added["action"], "added")

            status = worker_status(store)
            self.assertTrue(status["runnable"])
            self.assertEqual(status["in_progress_task_count"], 1)
            self.assertEqual(status["next_task"]["id"], added["task"]["id"])

    def test_empty_runtime_status_tells_agent_to_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            status = worker_status(WatchtowerStore(Path(tmp)))
            self.assertFalse(status["runnable"])
            self.assertEqual(status["goal_count"], 0)
            self.assertEqual(status["next_safe_action"], "run init before adding tasks")

    def test_version_flag_reports_package_version(self) -> None:
        out = io.StringIO()
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(out):
                main(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("agent-watchtower 0.1.4", out.getvalue())

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
