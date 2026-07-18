#!/bin/bash
# Dev-only entrypoint wrapper for netbox-atw.
# Installs the plugin (editable, from the bind-mounted repo) before the normal
# NetBox entrypoint runs migrations and launches the server.
set -e
umask 002

echo "⚙️ Installing netbox_atw (editable) from /opt/netbox/netbox/netbox_atw_src"
# The NetBox container ships uv, not pip; install into the NetBox venv.
VIRTUAL_ENV=/opt/netbox/venv uv pip install --editable /opt/netbox/netbox/netbox_atw_src

# Hand off to the stock NetBox entrypoint (runs migrations, creates superuser,
# then launches granian via launch-netbox.sh).
exec /opt/netbox/docker-entrypoint.sh /opt/netbox/launch-netbox.sh