import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "openwork_setup", ROOT / "bin" / "openwork-setup.py"
)
SETUP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SETUP)


class OpenWorkSetupTests(unittest.TestCase):
    def make_repo(self, root):
        (root / "opencode").mkdir(parents=True)
        (root / "opencode" / "plugin.js").write_text("adapter", encoding="utf-8")
        (root / "skills").mkdir()

    def test_install_is_idempotent_and_uses_absolute_adapter_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            workspace = Path(directory) / "workspace"
            self.make_repo(root)

            target = SETUP.install(workspace, root)
            first = target.read_text(encoding="utf-8")
            self.assertIn((root / "opencode" / "plugin.js").resolve().as_uri(), first)
            self.assertEqual(target, SETUP.install(workspace, root))
            self.assertEqual(first, target.read_text(encoding="utf-8"))

    def test_install_refuses_foreign_loader_and_uninstall_preserves_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            workspace = Path(directory) / "workspace"
            self.make_repo(root)
            target = SETUP.loader_path(workspace)
            target.parent.mkdir(parents=True)
            target.write_text("// user loader\n", encoding="utf-8")

            with self.assertRaises(RuntimeError):
                SETUP.install(workspace, root)
            with self.assertRaises(RuntimeError):
                SETUP.uninstall(workspace)
            self.assertEqual("// user loader\n", target.read_text(encoding="utf-8"))

    def test_stale_owned_loader_is_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            workspace = Path(directory) / "workspace"
            self.make_repo(root)
            target = SETUP.install(workspace, root)
            target.write_text(
                SETUP.OWNED_MARKER + "\n"
                + 'import { OpenWorkJobHuntPlugin } from "file:///moved/plugin.js";\n'
                + "export { OpenWorkJobHuntPlugin };\n",
                encoding="utf-8",
            )

            SETUP.install(workspace, root)
            self.assertEqual(SETUP.loader_text(root), target.read_text(encoding="utf-8"))

    def test_status_reports_missing_malformed_stale_and_source_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            workspace = Path(directory) / "workspace"
            self.make_repo(root)

            state = SETUP.status(workspace, root)
            self.assertEqual(["workspace-missing", "loader-missing"], state["issues"])

            workspace.mkdir()
            SETUP.loader_path(workspace).parent.mkdir(parents=True)
            SETUP.loader_path(workspace).write_text("not a loader", encoding="utf-8")
            self.assertIn("loader-malformed", SETUP.status(workspace, root)["issues"])

            SETUP.loader_path(workspace).write_text(
                SETUP.OWNED_MARKER + "\n"
                + 'import { OpenWorkJobHuntPlugin } from "file:///moved/plugin.js";\n'
                + "export { OpenWorkJobHuntPlugin };\n",
                encoding="utf-8",
            )
            self.assertIn("loader-stale", SETUP.status(workspace, root)["issues"])

            (root / "opencode" / "plugin.js").unlink()
            (root / "skills").rmdir()
            state = SETUP.status(workspace, root)
            self.assertIn("adapter-missing", state["issues"])
            self.assertIn("skills-missing", state["issues"])

    def test_uninstall_is_idempotent_for_owned_loader(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            workspace = Path(directory) / "workspace"
            self.make_repo(root)
            SETUP.install(workspace, root)

            self.assertTrue(SETUP.uninstall(workspace))
            self.assertFalse(SETUP.loader_path(workspace).exists())
            self.assertFalse(SETUP.uninstall(workspace))


if __name__ == "__main__":
    unittest.main()
