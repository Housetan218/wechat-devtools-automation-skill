# WeChat DevTools Automation Skill

Reusable Codex skill for repeatable WeChat Mini Program workflows in WeChat DevTools.

## What This Repo Ships

- one installable skill folder: `wechat-devtools-automation/`
- a bootstrap script that adds a project-local automation skeleton
- a validation script that checks the generated skeleton
- reference documents for the expected project contract

## Good Fit

Use this when you want a repeatable terminal-driven flow for:

- opening a Mini Program project in WeChat DevTools
- checking DevTools login status
- deploying cloud functions repeatedly
- selecting a compile mode automatically
- compiling, refreshing, and capturing screenshots on macOS
- creating a minimal automation scaffold in an existing Mini Program project

## Repository Layout

```text
wechat-devtools-automation/
  SKILL.md
  references/
    bootstrap-template.md
    project-contract.md
  scripts/
    bootstrap_wechat_devtools_automation.py
    validate_bootstrap.py
```

## Install Into Codex

```bash
cp -R wechat-devtools-automation ~/.codex/skills/
```

## Requirements

- macOS
- WeChat DevTools desktop app installed
- DevTools HTTP service port enabled
- a real Mini Program project directory as bootstrap target

The bootstrap script is not a full project generator. `--project-dir` must already contain a valid WeChat Mini Program project, including `project.config.json`.

## Bootstrap Example

Run from the repository root:

```bash
python3 wechat-devtools-automation/scripts/bootstrap_wechat_devtools_automation.py \
  --project-dir /path/to/existing-miniapp \
  --env-id your-env-id \
  --functions login,autoTest,auditGameRecords
```

Typical output adds:

- `utils/devAutomationConfig.js`
- `utils/devLaunchConfig.js`
- `utils/generatedDevLaunchConfig.js`
- `scripts/wechat-cli.sh`
- `scripts/wechat-gui-compile.sh`
- `scripts/wechat-gui-refresh.sh`
- `scripts/wechat-gui-capture.sh`
- `scripts/wechat-set-compile-mode.js`
- `scripts/wechat-regression.sh`

## Validate Example

```bash
python3 wechat-devtools-automation/scripts/validate_bootstrap.py \
  --project-dir /path/to/existing-miniapp
```

Validation checks the generated files, compile mode wiring, placeholder resolution, and JavaScript syntax of the generated helpers.

## What It Intentionally Does Not Include

- Mini Program business pages
- project-specific cloud functions
- production diagnostics endpoints
- any real env id, app id, openid, or project path

You still need to add your own guarded diagnostics page and cloud-side auth checks in each target project.

## Publishing As A Codex Skill

After cloning this repository on another machine:

```bash
cp -R wechat-devtools-automation ~/.codex/skills/
```

Then reference the skill by name in Codex when working on a WeChat Mini Program project.

## Tested Scope

Validated on macOS with WeChat DevTools installed. The included scripts were verified by:

- `python3 .../bootstrap_wechat_devtools_automation.py --help`
- `python3 .../validate_bootstrap.py --help`
- bootstrap into a temporary project directory
- validation against that generated output
