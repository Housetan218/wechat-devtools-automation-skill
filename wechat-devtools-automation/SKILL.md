---
name: wechat-devtools-automation
description: Use when working on a WeChat Mini Program and you need repeatable WeChat DevTools actions such as opening the project, checking login, deploying cloud functions, selecting compile modes, compiling, refreshing, taking stable screenshots, or reducing manual DevTools steps across projects.
---

# WeChat DevTools Automation

## Overview

Use the WeChat DevTools CLI first. Add project-local GUI helpers only for the last mile that the CLI cannot do reliably.

## When to Use

- Need to open a Mini Program project from terminal
- Need to deploy one or more cloud functions repeatedly
- Need a stable compile, refresh, and screenshot loop
- Need a diagnostics page or fixed regression route for screenshots
- Need to carry the same automation pattern into another WeChat project

Do not start with coordinate clicking. Exhaust CLI, compile mode selection, and menu-driven GUI scripting first.

## Core Workflow

1. Confirm the DevTools HTTP service port is enabled.
2. Use the official CLI at `/Applications/wechatwebdevtools.app/Contents/MacOS/cli`.
3. Check whether the project already has the local automation contract described in `references/project-contract.md`.
4. If not, bootstrap the minimum adapter files with `scripts/bootstrap_wechat_devtools_automation.py`.
5. Use a project-local wrapper such as `scripts/wechat-cli.sh`.
6. Use one orchestrator such as `scripts/wechat-regression.sh`.
7. Keep GUI helpers limited to:
   - compile
   - refresh
   - screenshot capture
8. Save artifacts under one output root such as `tmp/wechat-regression/<timestamp>/`.

## Command Pattern

- Login check: `cli islogin --project <path> --port <port>`
- Open project: `cli open --project <path> --port <port>`
- List functions: `cli cloud functions list -e <env> --project <path> --port <port>`
- Deploy functions: `cli cloud functions deploy -e <env> -n <names...> --provided --remote-npm-install --project <path> --port <port>`

## Cross-Project Contract

For a project to be automation-ready, it should have:

- one config module with project path, port, env id, default function list, compile mode name
- one CLI wrapper
- one compile mode selector
- GUI helpers for compile, refresh, screenshot
- one regression orchestrator
- one diagnostics route that can render fixed structured output
- one generated launch config file with an expiry guard

Read `references/project-contract.md` for the full contract and file list.

If the project does not yet have these files, read `references/bootstrap-template.md` and create the minimum adapter set before trying to automate the workflow.
Prefer running the bootstrap script first from the skill directory:

```bash
python3 scripts/bootstrap_wechat_devtools_automation.py \
  --project-dir /path/to/project \
  --env-id your-env-id \
  --functions login,autoTest,auditGameRecords
```

Then validate the generated skeleton:

```bash
python3 scripts/validate_bootstrap.py \
  --project-dir /path/to/project
```

## Guardrails

- Prefer compile mode routing over runtime `reLaunch` as the primary path.
- If runtime launch config is used as fallback, it must have an expiry timestamp so failed runs do not poison future local launches.
- Generated JS config modules must be statically imported by Mini Program code.
- Diagnostics or admin pages must be protected by cloud-side auth checks before exposing global data.
- For data checks, prefer deterministic queries with explicit sort order over unordered full-table slices.

## Failure Order

When the automation route fails, debug in this order:

1. CLI connectivity and login
2. project-local config values
3. compile mode selection
4. compile and refresh helpers
5. diagnostics route navigation
6. diagnostics cloud function auth and packaging
7. screenshot capture window targeting

Capture logs and screenshots after each attempt. Do not guess.
