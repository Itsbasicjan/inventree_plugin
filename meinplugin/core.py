# Ersetze den Inhalt deiner generierten Haupt-Plugin-Datei
# (z.B. meinplugin/plugin.py oder meinplugin/core.py) mit diesem Code:

"""MeinPlugin - Angepasstes InvenTree Plugin."""

# Core InvenTree imports
from plugin import InvenTreePlugin
# --- Mixins ---
# Behalte SettingsMixin
# Füge die hinzu, die wir brauchen: Navigation, Panel, Urls
# Entferne ScheduleMixin, UserInterfaceMixin (für dieses Beispiel nicht benötigt)
from plugin.mixins import SettingsMixin, NavigationMixin, PanelMixin, UrlsMixin

# Django imports
from django.urls import path

# InvenTree view imports (Ziel für das Panel)
from part.views import PartDetail

# Lokale Imports aus unserem Plugin-Paket
try:
    # Importiert die Version aus version.py (Cookiecutter sollte diese erstellt haben)
    from .version import PLUGIN_VERSION
except ImportError:
    PLUGIN_VERSION = "0.0.0" # Fallback, falls version.py fehlt
# Importiert die views.py (stelle sicher, dass diese Datei existiert!)
from . import views

# --- Haupt-Plugin Klasse ---
# Umbenannt zu MeinPlugin (Großbuchstabe am Anfang - Konvention)
# Vererbungsliste angepasst
class MeinPlugin(SettingsMixin, NavigationMixin, PanelMixin, UrlsMixin, InvenTreePlugin):
    """meinplugin - custom InvenTree plugin.""" # Beschreibung ggf. anpassen

    # --- Plugin Metadaten ---
    # Diese Werte stammen aus den Cookiecutter-Eingaben
    # Du kannst TITLE und DESCRIPTION hier noch anpassen
    TITLE = "meinplugin" # Vielleicht besser: "Mein Cooles Plugin"
    NAME = "meinplugin" # Interner Name, sollte normalerweise dem Slug entsprechen
    SLUG = "meinplugin" # Wichtig für Aktivierung in config.yaml und URLs
    DESCRIPTION = "Ein Plugin mit Navigation und Panel, erstellt mit Cookiecutter." # Angepasst
    VERSION = PLUGIN_VERSION
    AUTHOR = "Jan Schüler"
    LICENSE = "MIT"

    # --- Navigation (via Konstante) ---
    NAVIGATION_ENABLED = True # Navigation explizit aktivieren
    NAVIGATION = [
        {
            'name': 'Coole Plugin Seite', # Name im Navigationsmenü
            'link': 'plugin:meinplugin:index', # Verweist auf URL 'index' unten
            'icon': 'fas fa-star', # Icon
        },
    ]

    # --- Einstellungen (SettingsMixin) ---
    # Beispiel-Einstellung von Cookiecutter, kann angepasst/erweitert werden
    SETTINGS = {
        'CUSTOM_VALUE': {
            'name': 'Custom Value',
            'description': 'A custom value',
            'validator': int,
            'default': 42,
        }
        # Hier können weitere Einstellungen hinzugefügt werden
    }

    # --- Panel Implementation (PanelMixin) ---
    def get_custom_panels(self, view, request):
        panels = []
        # Zeige Panel nur auf der Teiledetailseite an
        if isinstance(view, PartDetail):
            part = view.get_object() # Das aktuell angezeigte Teil
            panels.append({
                'title': 'Mein Teil-Panel',
                'icon': 'fas fa-info-circle',
                # Inhalt direkt als HTML:
                'content': f'<h3>Panel von MeinPlugin</h3><p>Dieses Panel wird für das Teil <strong>{part.name}</strong> (PK: {part.pk}) angezeigt.</p>',
                # Alternativ über Template-Datei:
                # 'content_template': 'meinplugin/mein_panel_inhalt.html',
                # 'context': {'anzeige_teil': part} # Daten für Template
            })
        return panels

    # --- URL Definition (UrlsMixin) ---
    # Definiert die URL für die eigene Seite dieses Plugins
    def setup_plugin_urls(self):
        return [
            # Leerer Pfad ('') ist die Basis-URL: /plugin/meinplugin/
            # name='index' wird oben im Navigationslink verwendet
            path('', views.mein_plugin_view, name='index'),
        ]

    # Die SCHEDULED_TASKS von ScheduleMixin wurden entfernt.
    # Die Kommentare für UserInterfaceMixin wurden entfernt.

