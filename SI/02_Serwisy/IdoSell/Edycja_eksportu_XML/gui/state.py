# -*- coding: utf-8 -*-
"""Stan współdzielony przez zakładki.

Zakładki nie rozmawiają ze sobą wprost - zmieniają stan i ogłaszają zdarzenie,
a zainteresowane widoki same się odświeżają. Dzięki temu zmiana źródła
przebudowuje drzewo pól i podgląd bez wiązania zakładek ze sobą.
"""

from core.pipeline import ExportConfig
from core.profile import load_settings, save_settings
from core.schema import build_registry
from core.structures import load_all

# Zdarzenia.
SOURCE_CHANGED = "source"       # wybrano plik albo zmieniono skan
FIELDS_CHANGED = "fields"       # zmieniono kolumny, parametry, zdjęcia
RULES_CHANGED = "rules"         # zmieniono reguły albo filtry
OUTPUT_CHANGED = "output"       # zmieniono strukturę albo opcje zapisu


class AppState(object):

    def __init__(self):
        self.config = ExportConfig()
        self.registry = build_registry()
        self.structures = load_all()
        self.scan = None
        self.settings = load_settings()
        self.profile_path = u""
        self._listeners = []
        if self.structures:
            self.config.structure = self.structures[0].copy()

    # -- powiadomienia ---------------------------------------------------

    def subscribe(self, callback):
        self._listeners.append(callback)

    def notify(self, event):
        for callback in list(self._listeners):
            try:
                callback(event)
            except Exception:
                # Błąd jednego widoku nie może wywrócić pozostałych.
                pass

    # -- pomocnicze ------------------------------------------------------

    @property
    def source_type(self):
        return self.config.source_type

    def reset_registry(self):
        self.registry = build_registry()
        return self.registry

    def structure_by_id(self, structure_id):
        for structure in self.structures:
            if structure.id == structure_id:
                return structure
        return None

    def remember_dir(self, path):
        import os
        self.settings["last_dir"] = os.path.dirname(os.path.abspath(path))
        save_settings(self.settings)

    def save_settings(self):
        save_settings(self.settings)
