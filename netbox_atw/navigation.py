from django.utils.translation import gettext_lazy as _
from netbox.plugins import PluginMenuItem

menu_items = [
    PluginMenuItem(
        link="plugins:netbox_atw:importjob_list",
        link_text=_("Import Jobs"),
        permissions=["netbox_atw.view_importjob"],
    ),
    PluginMenuItem(
        link="plugins:netbox_atw:import_home",
        link_text=_("New Import"),
        permissions=["netbox_atw.add_importjob"],
    ),
]
