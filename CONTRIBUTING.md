# Contributing

## Scope

Keep this repository generic and reusable across WeChat Mini Program projects.

Do not add:

- project-specific business logic
- real env ids, app ids, openids, or local machine paths
- screenshots or logs containing private project data

## Change Guidelines

- keep the skill focused on DevTools automation workflows
- prefer small, verifiable changes
- update `README.md` when install or validation steps change
- preserve privacy-safe examples in docs and scripts

## Verification

Before opening a pull request, run:

```bash
bash -n install.sh
python3 wechat-devtools-automation/scripts/bootstrap_wechat_devtools_automation.py --help
python3 wechat-devtools-automation/scripts/validate_bootstrap.py --help
```

For bootstrap validation, test against an existing Mini Program project directory or a temporary directory that already contains a minimal `project.config.json`.
