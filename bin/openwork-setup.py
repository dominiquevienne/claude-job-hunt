#!/usr/bin/env python3
"""Install the OpenWork loader for the local job-hunt checkout."""

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DEFAULT = "~/OpenWork"
LOADER_RELATIVE = Path(".opencode") / "plugins" / "job-hunt.js"
OWNED_MARKER = "// openwork-job-hunt: installer-owned"
PLUGIN_EXPORT = "OpenWorkJobHuntPlugin"
IMPORT_LINE = re.compile(
    r'^import \{ ' + re.escape(PLUGIN_EXPORT) + r' \} from "([^"]+)";$'
)


def workspace_path(value: str) -> Path:
    """Return a normalized absolute workspace path."""
    return Path(os.path.abspath(os.path.expanduser(value)))


def loader_path(workspace: Path) -> Path:
    return workspace_path(str(workspace)) / LOADER_RELATIVE


def loader_text(repo_root: Path = REPO_ROOT) -> str:
    """Build the complete loader, including its stable ownership marker."""
    adapter = (Path(repo_root).resolve() / "opencode" / "plugin.js").as_uri()
    return (
        OWNED_MARKER
        + "\n"
        + 'import { '
        + PLUGIN_EXPORT
        + ' } from '
        + json.dumps(adapter)
        + ";\n"
        + "export { "
        + PLUGIN_EXPORT
        + " };\n"
    )


def _read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def _is_owned(text: str) -> bool:
    return text.startswith(OWNED_MARKER + "\n")


def _loader_adapter_uri(text: str) -> Optional[str]:
    """Return the adapter URI for a well-formed owned loader."""
    if not _is_owned(text):
        return None
    lines = text.splitlines()
    if len(lines) != 3 or lines[2] != "export { " + PLUGIN_EXPORT + " };":
        return None
    match = IMPORT_LINE.fullmatch(lines[1])
    return match.group(1) if match else None


def _atomic_write(path: Path, content: str) -> None:
    """Replace *path* atomically after fully writing the new content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        fd, name = tempfile.mkstemp(
            prefix="." + path.name + ".", dir=str(path.parent)
        )
        temporary = Path(name)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def install(workspace: Path, repo_root: Path = REPO_ROOT) -> Path:
    """Install or refresh the owned loader, refusing unrelated files."""
    target = loader_path(workspace)
    desired = loader_text(repo_root)
    if target.exists():
        current = _read_text(target)
        if current is None or (
            current != desired and _loader_adapter_uri(current) is None
        ):
            raise RuntimeError(
                "refusing to overwrite non-installer-owned loader: " + str(target)
            )
        if current == desired:
            return target
    _atomic_write(target, desired)
    return target


def _loader_issue(target: Path, expected: str) -> Optional[str]:
    if not target.exists():
        return "loader-missing"
    if not target.is_file():
        return "loader-malformed"
    current = _read_text(target)
    if current is None:
        return "loader-malformed"
    if current == expected:
        return None
    if not _is_owned(current):
        return "loader-malformed"
    adapter = _loader_adapter_uri(current)
    if adapter is None:
        return "loader-malformed"
    if adapter != _loader_adapter_uri(expected):
        return "loader-stale"
    return "loader-malformed"


def status(workspace: Path, repo_root: Path = REPO_ROOT) -> Dict[str, object]:
    """Return observable installation health without changing the workspace."""
    workspace = workspace_path(str(workspace))
    repo_root = Path(repo_root).resolve()
    target = loader_path(workspace)
    issues: List[str] = []
    loader_issue = _loader_issue(target, loader_text(repo_root))
    if loader_issue:
        issues.append(loader_issue)
    if not (repo_root / "opencode" / "plugin.js").is_file():
        issues.append("adapter-missing")
    if not (repo_root / "skills").is_dir():
        issues.append("skills-missing")
    if not workspace.is_dir():
        issues.insert(0, "workspace-missing")
    return {
        "ok": not issues,
        "workspace": str(workspace),
        "loader": str(target),
        "repo": str(repo_root),
        "issues": issues,
    }


def uninstall(workspace: Path) -> bool:
    """Remove the loader only when its ownership marker proves provenance."""
    target = loader_path(workspace)
    if not target.exists():
        return False
    if not target.is_file():
        raise RuntimeError("refusing to remove non-file loader: " + str(target))
    current = _read_text(target)
    if current is None or _loader_adapter_uri(current) is None:
        raise RuntimeError("refusing to remove non-installer-owned loader: " + str(target))
    target.unlink()
    return True


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=WORKSPACE_DEFAULT)
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("install", "status", "uninstall"):
        subparser = subparsers.add_parser(action)
        subparser.add_argument("--workspace", dest="sub_workspace", default=None)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    workspace = args.sub_workspace or args.workspace
    if args.action == "install":
        try:
            target = install(workspace_path(workspace))
        except RuntimeError as error:
            print(str(error), file=sys.stderr)
            return 2
        print("installed " + str(target))
        return 0
    if args.action == "uninstall":
        try:
            removed = uninstall(workspace_path(workspace))
        except RuntimeError as error:
            print(str(error), file=sys.stderr)
            return 2
        print(("removed " if removed else "already absent ") + str(loader_path(workspace)))
        return 0

    state = status(workspace_path(workspace))
    if state["ok"]:
        print("ok: " + str(state["loader"]))
        return 0
    print("not ready: " + str(state["workspace"]))
    for issue in state["issues"]:
        print("- " + str(issue))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
