# Security Policy

## Reporting

If you find a security issue in this repository, do not publish sensitive details in a public issue.

Report the problem privately to the maintainer with:

- affected file or script
- impact summary
- reproduction steps
- suggested mitigation if available

## Repository Boundaries

This repository ships local automation helpers and project bootstrap utilities. It does not include production cloud credentials or deployment secrets.

When contributing, avoid committing:

- real Tencent cloud env ids
- real app ids
- real user identifiers
- local paths that reveal private project locations
