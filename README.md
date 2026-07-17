# netbox-atw

The Atw [NetBox](https://netbox.dev) plugin — bulk import and population tooling that reduces the friction of getting real-world data into NetBox.

> **Status:** early development (pre-release). The plugin scaffold and the first bulk-import feature are being built in parallel (ATW-3, ATW-4). Anything marked `<!-- TODO(ATW-x) -->` below is pending a sibling task and will be filled in once that work lands.

## Why

Populating NetBox from real-world sources is the single biggest friction point the community reports. Atw attacks that friction directly: a focused plugin that ingests messy real-world data, maps it to NetBox's model, validates it, and creates/updates records with clear feedback — instead of hand-keyed CSV rows and bespoke scripts.

## Features

- **Bulk import / population tooling** — <!-- TODO(ATW-4): one-line feature summary once the first scenario is defined -->
- Standard NetBox plugin install (pip + `PLUGINS`)
- REST API exposure following NetBox plugin conventions
- Tests against a NetBox dev instance across the compatibility matrix
- <!-- TODO(ATW-4): additional feature bullets -->

## Installation

> The package name and PyPI availability are pending ATW-3 (packaging) and CEO sign-off on the first release. The steps below follow the standard NetBox plugin install pattern and will be verified against the shipped scaffold.

```bash
<!-- TODO(ATW-3): replace `netbox-atw` with the verified package name once pyproject lands -->
pip install netbox-atw
```

Add the plugin to your NetBox configuration (`/etc/netbox/configuration.py`):

```python
PLUGINS = [
    "netbox_atw",
]
```

Run database migrations and restart NetBox:

```bash
cd /opt/netbox
python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

## Configuration

<!-- TODO(ATW-4): document any `PLUGINS_CONFIG` options once the import feature defines its configuration surface -->

```python
PLUGINS_CONFIG = {
    "netbox_atw": {
        # <!-- TODO(ATW-4): configuration options -->
    },
}
```

## Usage

### Bulk import

<!-- TODO(ATW-4): end-to-end usage walkthrough for the first real-world scenario — ingest, map, validate, create/update. -->

```bash
# <!-- TODO(ATW-4): example CLI / API call once the import feature is defined -->
```

### REST API

<!-- TODO(ATW-4): API path, example curl calls, request/response shapes -->

## Compatibility

Atw targets the current NetBox release and tracks the official NetBox support window. The full matrix (NetBox versions × Python versions) is established and maintained on ATW-3 and ATW-5.

<!-- TODO(ATW-3): fill in the verified compatibility matrix once packaging lands -->

| NetBox | Python | Status |
|--------|--------|--------|
| <!-- TODO(ATW-3) --> | <!-- TODO(ATW-3) --> | <!-- TODO(ATW-3) --> |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide (local dev environment, lint, tests, release flow).

Quick start:

```bash
git clone https://github.com/openjarv/netbox-atw.git
cd netbox-atw
# <!-- TODO(ATW-3): install dev extras and local NetBox dev env setup once packaging lands -->
```

## Documentation

- [CHANGELOG.md](CHANGELOG.md) — release history
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [docs/](docs/) — usage guides and examples (populated as features land)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — community standards

## Support

- Open an issue: https://github.com/openjarv/netbox-atw/issues
- Security reports: see [SECURITY.md](SECURITY.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.