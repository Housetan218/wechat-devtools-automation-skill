# WeChat DevTools Automation Skill

Reusable Codex skill for automating WeChat Mini Program workflows in WeChat DevTools.

## What It Includes

- one installable skill folder: `wechat-devtools-automation/`
- a bootstrap script for generating a project-local automation skeleton
- a validation script for checking that generated files satisfy the expected contract
- references for project contract and bootstrap expectations

## Use Cases

- open a Mini Program project from terminal
- check DevTools login
- deploy cloud functions repeatedly
- select a compile mode automatically
- trigger compile and refresh from macOS
- capture stable screenshots for regression review
- bootstrap the minimum automation files into a new WeChat project

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

Copy the skill folder into your Codex skills directory:

```bash
cp -R wechat-devtools-automation ~/.codex/skills/
```

## Bootstrap a Project

From inside the skill directory:

```bash
python3 scripts/bootstrap_wechat_devtools_automation.py \
  --project-dir /path/to/project \
  --env-id your-env-id \
  --functions login,autoTest,auditGameRecords
```

## Validate a Bootstrapped Project

```bash
python3 scripts/validate_bootstrap.py \
  --project-dir /path/to/project
```

## Scope

This repository deliberately avoids shipping any project-specific business logic.

It only provides:

- the automation skill
- the bootstrap generator
- the bootstrap validator
- the contract documentation

You still need to add project-specific diagnostics pages and cloud functions in each target Mini Program.
