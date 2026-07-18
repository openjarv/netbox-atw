from .version import __version__

try:
    from netbox.plugins import PluginConfig
except ModuleNotFoundError:  # pragma: no cover - allows importing submodules without NetBox installed
    PluginConfig = object  # type: ignore[misc,assignment]


class AtwConfig(PluginConfig):
    name = "netbox_atw"
    verbose_name = "Atw"
    description = "Bulk import and population tooling that reduces the friction of getting real-world data into NetBox."
    version = __version__
    base_url = "atw"
    min_version = "3.5.0"


config = AtwConfig
