#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


REQUIRED_FILES = [
    "utils/devAutomationConfig.js",
    "utils/devLaunchConfig.js",
    "utils/generatedDevLaunchConfig.js",
    "scripts/wechat-cli.sh",
    "scripts/wechat-gui-compile.sh",
    "scripts/wechat-gui-refresh.sh",
    "scripts/wechat-gui-capture.sh",
    "scripts/wechat-set-compile-mode.js",
    "scripts/wechat-regression.sh",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a WeChat DevTools automation bootstrap output")
    parser.add_argument("--project-dir", required=True, help="Target project directory")
    parser.add_argument("--compile-mode-name", default="dev-tools-autorun", help="Expected compile mode name")
    parser.add_argument("--diagnostics-page", default="pages/dev-tools/dev-tools", help="Expected diagnostics page path")
    return parser.parse_args()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"[validate] failed: {message}")
    print(f"[validate] ok: {message}")


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    check(project_dir.exists(), f"project exists: {project_dir}")

    for rel in REQUIRED_FILES:
      path = project_dir / rel
      check(path.exists(), f"required file exists: {rel}")

    project_config_path = project_dir / "project.config.json"
    check(project_config_path.exists(), "project.config.json exists")

    project_config = json.loads(project_config_path.read_text(encoding="utf-8"))
    condition = project_config.get("condition") or project_config.get("condiction") or {}
    miniprogram = condition.get("miniprogram") or {}
    entries = miniprogram.get("list") or []
    target_entry = next((item for item in entries if isinstance(item, dict) and item.get("name") == args.compile_mode_name), None)
    check(target_entry is not None, f"compile mode exists: {args.compile_mode_name}")
    check(target_entry.get("pathName") == args.diagnostics_page, f"compile mode path matches: {args.diagnostics_page}")

    for rel in [
        "utils/devAutomationConfig.js",
        "utils/devLaunchConfig.js",
        "scripts/wechat-set-compile-mode.js",
    ]:
        subprocess.run(["node", "--check", str(project_dir / rel)], check=True)
        print(f"[validate] ok: node --check {rel}")

    generated_text = (project_dir / "utils/generatedDevLaunchConfig.js").read_text(encoding="utf-8")
    check("expiresAt" in generated_text, "generated launch config contains expiresAt")

    regression_text = (project_dir / "scripts/wechat-regression.sh").read_text(encoding="utf-8")
    check("__DIAGNOSTICS_ROUTE__" not in regression_text, "diagnostics route placeholder resolved")

    print("[validate] bootstrap output looks consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
