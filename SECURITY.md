# Security Policy

## Supported versions

Atw tracks the current NetBox release and follows the NetBox support window.
The supported plugin versions table will be populated once the first release
ships.

| Version | Supported |
|---------|-----------|
| < 0.1.0 | unreleased |

## Reporting a vulnerability

Please report security vulnerabilities privately — **do not open a public
issue**.

Email: **engineering@atw.dev**

Include:

- A description of the issue and its impact
- Steps to reproduce (or a proof of concept)
- Affected NetBox and plugin versions
- Any suggested mitigation

We will acknowledge receipt within 2 business days and aim to send a first
assessment within 7 days. Coordinated disclosure is preferred; please allow
time for a fix before public disclosure.

## Security considerations for plugin users

- Run the plugin on a supported NetBox version (>= 3.5.0; see the README
  compatibility matrix).
- The plugin has no required configuration and no `PLUGINS_CONFIG` keys in
  0.1.0. If future versions add configuration that takes secrets, supply them
  via environment variables or your secrets manager — do not commit them to
  your NetBox configuration repo.
- ImportJob records store the **raw pasted input** in the `data` field for
  audit. If your input contains sensitive values, restrict
  `netbox_atw.view_importjob` and `netbox_atw.view_importjob_data`
  accordingly in production.