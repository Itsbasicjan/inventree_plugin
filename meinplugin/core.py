"""A short description of the project"""

# Standard Django imports for Views and URLs
from django.http import HttpResponse
from django.urls import path

# InvenTree plugin imports
from plugin import InvenTreePlugin
from plugin.mixins import (NavigationMixin, ScheduleMixin, SettingsMixin,
                           UrlsMixin, UserInterfaceMixin)

from . import PLUGIN_VERSION # Stellt sicher, dass die Version aus __init__.py geladen wird

# Die Hauptklasse für dein Plugin
class meinplugin(ScheduleMixin, SettingsMixin, UserInterfaceMixin, NavigationMixin, UrlsMixin, InvenTreePlugin):
    """meinplugin - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "Mein Cooles Plugin" # Angepasster Titel
    NAME = "meinplugin"
    SLUG = "meinplugin" # Wichtig für URL-Referenzen!
    DESCRIPTION = "Ein Beispiel-Plugin mit Navigationselement"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Jan Schüler"
    LICENSE = "MIT"

    # Optional: Gruppiere die Links unter einem eigenen Tab in der Navigation
    NAVIGATION_TAB_NAME = "Mein Plugin Tab"
    NAVIGATION_TAB_ICON = 'fas fa-cogs' # Beispiel FontAwesome 4 Icon

    # Navigationselemente (von NavigationMixin)
    # Ref: https://docs.inventree.org/en/latest/extend/plugins/integration/navigation/
    NAVIGATION = [
        {
            'name': 'Beispiel Seite', # Angezeigter Text des Links
            'link': 'plugin:meinplugin:hello', # URL-Name: plugin:<SLUG>:<url_name>
            'icon': 'fas fa-info-circle', # Beispiel FontAwesome 4 Icon
        },
        # Hier könnten weitere Links für dieses Plugin hinzugefügt werden
    ]

    # URL-Definitionen (von UrlsMixin)
    # Ref: https://docs.inventree.org/en/latest/extend/plugins/integration/urls/
    def setup_urls(self):
        """Definiert URL-Muster für dieses Plugin."""
        return [
            # Definiert eine URL unter /plugin/meinplugin/hello/
            path('hello/', self.hello_world_view, name='hello'),
            # Hier könnten weitere URLs für dieses Plugin definiert werden
        ]

    # Eine einfache View-Funktion
    def hello_world_view(self, request, *args, **kwargs):
        """Eine Beispiel-Ansicht, die von der URL aufgerufen wird."""
        # Du kannst hier komplexeren HTML-Code oder sogar Templates rendern
        html = "<h1>Hallo Welt!</h1><p>Dies ist eine einfache Seite vom 'meinplugin'.</p>"
        return HttpResponse(html)

    # --- Bestehende Mixin-Konfigurationen ---

    # Scheduled tasks (from ScheduleMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/schedule/
    SCHEDULED_TASKS = {
        # Define your scheduled tasks here...
    }

    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/settings/
    SETTINGS = {
        'CUSTOM_VALUE': {
            'name': 'Custom Value',
            'description': 'A custom value',
            'validator': int,
            'default': 42,
        }
        # Hier könnten weitere Einstellungen definiert werden
    }

    # User interface elements (from UserInterfaceMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/ui/
    # Diese sind für Dashboard-Elemente, Panels etc. relevant,
    # nicht direkt für die einfache Navigation, die wir hier erstellen.
    # Die bereitgestellten JavaScript-Beispiele würden hier konfiguriert werden,
    # wenn du z.B. ein benutzerdefiniertes Panel hinzufügen wolltest.