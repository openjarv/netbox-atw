# NetBox dev configuration for netbox-atw.
# Minimal config that enables the plugin and is safe for local dev only.

ALLOWED_HOSTS = ["*"]
SECRET_KEY = "dev-only-not-for-production-CHANGE-ME-0123456789-abcdefghij-0123456789-abcdefghij"
DEBUG = True

DATABASE = {
    "NAME": "netbox",
    "USER": "netbox",
    "PASSWORD": "netbox",
    "HOST": "postgres",
    "PORT": 5432,
    "CONN_MAX_AGE": 300,
}

REDIS = {
    "tasks": {
        "HOST": "redis",
        "PORT": 6379,
        "PASSWORD": "",
    },
    "caching": {
        "HOST": "redis",
        "PORT": 6379,
        "PASSWORD": "",
    },
}

PLUGINS = [
    "netbox_atw",
]

PLUGINS_CONFIG = {
    "netbox_atw": {},
}