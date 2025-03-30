# meinplugin/views.py
"""
Views für das MeinPlugin Plugin.
Diese Datei behandelt Anfragen an die URLs, die in plugin.py definiert wurden.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def mein_plugin_view(request: HttpRequest) -> HttpResponse:
    """
    Rendert die Hauptseite für das MeinPlugin.

    Diese Funktion wird aufgerufen, wenn die URL '/plugin/meinplugin/'
    (oder was auch immer in setup_plugin_urls definiert ist) aufgerufen wird.
    """
    # Kontextdaten, die an das HTML-Template übergeben werden.
    # Du kannst hier beliebige Daten hinzufügen, die du auf der Seite anzeigen möchtest.
    context = {
        'page_title': 'Mein Plugin Seite',
        'message': 'Willkommen auf der benutzerdefinierten Seite meines InvenTree Plugins!',
        'plugin_version': getattr(request, 'plugin_version', 'N/A') # Versucht Version aus Request zu holen (optional)
    }

    # Rendert das HTML-Template und übergibt den Kontext.
    # Stelle sicher, dass die Template-Datei unter 'templates/meinplugin/mein_plugin_seite.html' existiert.
    return render(request, 'meinplugin/mein_plugin_seite.html', context)

# Hier könntest du weitere View-Funktionen für andere URLs deines Plugins definieren
# def andere_ansicht(request: HttpRequest) -> HttpResponse:
#     context = {'message': 'Dies ist eine andere Seite.'}
#     return render(request, 'meinplugin/andere_seite.html', context)
