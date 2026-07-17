# Contributing to netbox-atw

Thanks for your interest in contributing to **netbox-atw** — the Atw NetBox plugin for bulk import and population tooling. This guide covers the expectations, setup, and workflow for contributors.

## Code of Conduct

Participation in this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## Before you contribute

- **Search existing issues** before opening a new one. Add details to an existing issue rather than duplicating it.
- **Open an issue first** for new features or larger changes so we can align on approach before you spend time on code.
- **One concern per PR** — keep PRs small and focused so review is fast and history stays readable.

## Development setup

> The local NetBox dev environment and dev dependencies are finalized on ATW-3. The steps below are the standard pattern and will be verified against the shipped scaffold.

### Prerequisites

- Python 3.10+ (see the compatibility matrix in the README)
- A working NetBox development environment (NetBox, PostgreSQL, Redis) — see the [NetBox development docs](https://netboxlabs.com/docs/netbox/en/stable/installation/)
- `git`

### Get the code

```bash
git clone https://github.com/openjarv/netbox-atw.git
cd netbox-atw
```

### Install dev dependencies

```bash
# <!-- TODO(ATW-3): verified install command once pyproject dev extras land -->
pip install -e ".[dev]"
```

### Run a local NetBox with the plugin

<!-- TODO(ATW-3): document the exact steps to point a local NetBox dev instance at this checkout -->

### Run lint and tests

```bash
# Lint (exact commands pinned in ATW-5 once CI lands)
# <!-- TODO(ATW-5): lint command -->
# <!-- TODO(ATW-5): type-check command -->

# Tests against the local NetBox dev instance
# <!-- TODO(ATW-3): pytest invocation once the test config lands -->
```

## Code standards

- Follow the existing style. We use `black` and `isort` (line length 120, matching the NetBox ecosystem convention).
- Keep functions and modules small and single-purpose.
- No commented-out code in merged PRs.
- Write tests for new behavior; do not regress existing tests.
- Keep the [CHANGELOG.md](CHANGELOG.md) `Unreleased` section updated with your change under the right heading (`Added`, `Changed`, `Fixed`, `Removed`).

## Git workflow

1. **Branch from `main`**, do not commit directly to `main`.
2. Use a clear branch prefix and descriptive name, e.g. `feat/bulk-import-csv`, `fix/import-validation-error`, `docs/usage-guide`.
3. Commit messages: imperative mood, lead with the point — e.g. `Add CSV column mapping to bulk importer`.
4. Push your branch and open a PR against `main`.
5. Request review. Address feedback with new commits (avoid force-pushing during review unless asked).

## Pull request expectations

- **Title:** concise, describes the change.
- **Description:** what + why. Link the issue (e.g. `Closes #12`). Call out anything a reviewer should look at closely.
- **Tests:** new behavior ships with tests; CI must be green.
- **Docs:** if your change affects user-facing behavior, update the README, CHANGELOG, and `docs/` in the same PR.
- **Compatibility:** if your change touches the NetBox compatibility surface, call it out explicitly and tag a maintainer.

## Reporting bugs

- Use the **Bug report** issue template.
- Include: NetBox version, plugin version, Python version, OS, exact steps to reproduce, expected vs. actual behavior, and relevant logs.
- Reproduce on a clean local NetBox dev instance if you can.

## Suggesting features

- Open an issue with **Feature request** and describe the real-world scenario and the friction it removes. Atw prioritizes features that measurably reduce population friction.

## Releasing

Releases are cut by maintainers. The first PyPI release requires CEO sign-off (see the hiring plan). Versioning follows [Semantic Versioning](https://semver.org/). See [RELEASING.md](docs/RELEASING.md) for the release runbook (populated once the pipeline lands).