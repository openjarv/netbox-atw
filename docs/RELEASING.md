# Release runbook

Releases are cut by maintainers. Versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The first PyPI
release requires CEO sign-off (role boundary — see the hiring plan).

> Status: 0.1.0 has not been released to PyPI yet. This runbook is the
> checklist for the first and subsequent releases.

## Pre-release checklist

- [ ] All planned changes for the release are merged to `main`.
- [ ] `main` is green on CI across the full NetBox × Python matrix
  (ATW-5).
- [ ] `__version__` in `netbox_atw/version.py` and `version` in
  `pyproject.toml` match the target release.
- [ ] `CHANGELOG.md` `Unreleased` section is complete and is renamed to
  the target version with a date.
- [ ] Compatibility matrix in the README is current.
- [ ] `python manage.py makemigrations netbox_atw --check --dry-run` reports
  no missing migrations against the supported NetBox versions.
- [ ] **CEO sign-off** on the first release (and any compatibility-matrix
  change).

## Cutting the release

1. Create a release branch: `git checkout -b release/0.1.0`.
2. Update `version.py` and `pyproject.toml` to the target version.
3. Move `CHANGELOG.md` `Unreleased` → `## [0.1.0] - YYYY-MM-DD`.
4. Commit: `Bump version to 0.1.0`.
5. Open a PR to `main`; merge after review.
6. Tag the merge commit: `git tag -a v0.1.0 -m "Release 0.1.0" && git push origin v0.1.0`.
7. Build the distribution:
   ```bash
   python -m build
   ```
8. Upload to PyPI (requires CEO sign-off for the first release):
   ```bash
   twine upload dist/*
   ```
9. Create a GitHub Release from the tag with the changelog section as the
   body and the built artifacts attached.

## Post-release

- [ ] Add a new `## [Unreleased]` section at the top of `CHANGELOG.md`.
- [ ] Bump dev version if needed.
- [ ] Announce on the NetBox community channels.

## Compatibility-matrix changes

Any change to the supported NetBox or Python versions requires CEO sign-off
(role boundary). Document the change in the README matrix and CHANGELOG
under `Changed` with the NetBox version that triggered it.

## Hotfixes

For a hotfix on a released version:

1. Branch from the release tag: `git checkout -b hotfix/0.1.1 v0.1.0`.
2. Fix, test, bump the patch version.
3. Add a `## [0.1.1] - YYYY-MM-DD` section to `CHANGELOG.md` under `Fixed`.
4. PR → merge → tag → release as above.