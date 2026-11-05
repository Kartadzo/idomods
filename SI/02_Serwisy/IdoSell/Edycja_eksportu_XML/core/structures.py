# -*- coding: utf-8 -*-
"""Wczytywanie i zapis definicji struktur wyjściowych.

Struktura to plik JSON w katalogu `structures/`. Dodanie nowej nie wymaga zmian
w kodzie - generator odczytuje katalog przy starcie. Własną konfigurację
użytkownika też można zapisać jako strukturę.
"""

import json
import os

from .paths import data_path, resource_path

MODE_FLAT = "flat"
MODE_TREE = "tree"

#: Katalog na struktury użytkownika - obok aplikacji, więc edytowalny.
STRUCTURES_DIR = data_path("structures")


def structures_dir():
    """Katalog, z którego czytamy struktury.

    Pierwszeństwo ma katalog obok aplikacji: użytkownik może tam dorzucić własną
    strukturę albo poprawić istniejącą. Gdy go nie ma (świeżo rozpakowany `.exe`),
    czytamy komplet dołączony do paczki.
    """
    if os.path.isdir(STRUCTURES_DIR):
        return STRUCTURES_DIR
    return resource_path("structures")


class Column(object):

    __slots__ = ("out", "field", "enabled")

    def __init__(self, out, field, enabled=True):
        self.out = out
        self.field = field
        self.enabled = enabled

    def to_dict(self):
        data = {"out": self.out, "field": self.field}
        if not self.enabled:
            data["enabled"] = False
        return data

    @staticmethod
    def from_dict(data):
        return Column(data.get("out", u""), data.get("field", u""),
                      data.get("enabled", True))


class Structure(object):

    def __init__(self, data=None, path=None):
        data = data or {}
        self.path = path
        self.id = data.get("id", u"custom")
        self.label = data.get("label", self.id)
        self.description = data.get("description", u"")
        self.mode = data.get("mode", MODE_FLAT)
        self.format = data.get("format", "csv")
        self.sources = tuple(data.get("sources", ("xml", "csv")))
        self.row_context = data.get("row_context", "product")
        self.columns = [Column.from_dict(c) for c in data.get("columns", [])]
        self.keep = list(data.get("keep", []))
        self.xml = dict(data.get("xml", {}))
        self.csv = dict(data.get("csv", {}))
        self.images = dict(data.get("images", {}))
        self.params = dict(data.get("params", {}))

    def supports(self, source_type):
        return source_type in self.sources

    def unsupported_reason(self, source_type):
        if self.supports(source_type):
            return u""
        if self.mode == MODE_TREE and source_type == "csv":
            return (u"Przycinanie IOF wymaga źródła XML - z CSV byłaby to budowa "
                    u"nowego drzewa, a nie przycięcie istniejącego.")
        return u"Struktura niedostępna dla tego typu źródła."

    def to_dict(self):
        data = {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "mode": self.mode,
            "format": self.format,
            "sources": list(self.sources),
            "row_context": self.row_context,
        }
        if self.columns:
            data["columns"] = [c.to_dict() for c in self.columns]
        if self.keep:
            data["keep"] = list(self.keep)
        for name in ("xml", "csv", "images", "params"):
            value = getattr(self, name)
            if value:
                data[name] = value
        return data

    def copy(self):
        return Structure(json.loads(json.dumps(self.to_dict())))


def load_all(directory=None):
    """Wszystkie struktury z katalogu, posortowane wg etykiety."""
    directory = directory or structures_dir()
    result = []
    if not os.path.isdir(directory):
        return result
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        full = os.path.join(directory, name)
        try:
            with open(full, "r", encoding="utf-8") as handle:
                result.append(Structure(json.load(handle), path=full))
        except (ValueError, IOError):
            continue
    order = {"flat_csv": 0, "simple_xml": 1, "iof_subset": 2}
    result.sort(key=lambda s: (order.get(s.id, 99), s.label))
    return result


def save(structure, directory=None):
    directory = directory or STRUCTURES_DIR
    if not os.path.isdir(directory):
        os.makedirs(directory)
    path = structure.path or os.path.join(directory, structure.id + ".json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(structure.to_dict(), handle, ensure_ascii=False, indent=2)
    structure.path = path
    return path
