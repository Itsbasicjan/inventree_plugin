"""A short description of the project"""

from plugin import InvenTreePlugin

from plugin.mixins import ScheduleMixin, SettingsMixin, UserInterfaceMixin

from . import PLUGIN_VERSION


class meinplugin(ScheduleMixin, SettingsMixin, UserInterfaceMixin, InvenTreePlugin):

    """meinplugin - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "meinplugin"
    NAME = "meinplugin"
    SLUG = "meinplugin"
    DESCRIPTION = "A short description of the project"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Jan Schüler"
    
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'
    
    # Scheduled tasks (from ScheduleMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/schedule/
    SCHEDULED_TASKS = {
        # Define your scheduled tasks here...
    }
    
    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/settings/
    SETTINGS = {
        # Define your plugin settings here...
        'CUSTOM_VALUE': {
            'name': 'Custom Value',
            'description': 'A custom value',
            'validator': int,
            'default': 42,
        }
    }
    
    
    

    # User interface elements (from UserInterfaceMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/ui/
    
    
