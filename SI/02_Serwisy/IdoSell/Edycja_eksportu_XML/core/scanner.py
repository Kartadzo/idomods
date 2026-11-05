# -*- coding: utf-8 -*-
"""Skan pliku wejściowego.

Jeden przelot, który ustala to, czego nie da się zaszyć na sztywno: jakie języki
i sklepy są w tym konkretnym eksporcie, jakie parametry mają produkty i ile
maksymalnie zdjęć trzeba przewidzieć na kolumny.

Zestaw kolumn CSV zmienia się między sklepami - dwa eksporty z tego samego
panelu miały 298 i 334 kolumny z zupełnie innym zestawem języków - więc skan
jest obowiązkowy, nie opcjonalny.
"""

import re

from .readers.base import open_reader, detect_source_type
from .readers.csv_reader import split_path

LANG_IN_PATH = re.compile(r"\[([a-z]{3})\]$")

DEFAULT_LIMIT = 2000


class ScanResult(object):

    def __init__(self):
        self.source_type = None
        self.products = 0
        self.sizes = 0
        self.max_sizes = 0
        self.langs = []
        self.sites = []
        self.params = []            # [(id, nazwa)] w kolejności pierwszego wystąpienia
        self.image_kinds = {}       # typ -> maksymalna liczba zdjęć
        self.columns = []           # nagłówki CSV albo wykryte ścieżki XML
        self.unknown_columns = []
        self.issues = []
        self.truncated = False      # czy skan zatrzymał się na limicie

    @property
    def max_images(self):
        return max(self.image_kinds.values()) if self.image_kinds else 0

    def summary(self):
        parts = [u"%d produktów" % self.products]
        if self.max_sizes:
            parts.append(u"%d rozmiarów (maks. %d na produkt)" % (self.sizes, self.max_sizes))
        if self.langs:
            parts.append(u"%d języków: %s" % (len(self.langs), u", ".join(self.langs)))
        if self.sites:
            parts.append(u"sklepy: %s" % u", ".join(self.sites))
        if self.params:
            parts.append(u"%d parametrów" % len(self.params))
        if self.image_kinds:
            kinds = u", ".join(u"%s×%d" % (k, v) for k, v in sorted(self.image_kinds.items()))
            parts.append(u"zdjęcia: %s" % kinds)
        if self.truncated:
            parts.append(u"skan przerwany na limicie - lista może być niepełna")
        return u", ".join(parts)


def scan(path, limit=DEFAULT_LIMIT, registry=None, progress=None):
    """Przegląda plik i zwraca ScanResult."""
    result = ScanResult()
    result.source_type = detect_source_type(path)

    langs = set()
    sites = set()
    params = []
    seen_params = set()
    paths = set()

    reader = open_reader(path)
    count = 0
    for record in reader.iter_records(limit=limit):
        count += 1
        result.products += 1
        result.sizes += len(record.sizes)
        if len(record.sizes) > result.max_sizes:
            result.max_sizes = len(record.sizes)

        for key in record.values:
            paths.add(key)
            match = LANG_IN_PATH.search(key)
            if match:
                langs.add(match.group(1))

        for element, entries in record.blocks.items():
            # Tylko elementy będące samym `site` - inaczej `/navigation/site/menu`
            # wpuszcza do listy sklepów identyfikatory menu.
            if not element.endswith(u"/site"):
                continue
            for entry in entries:
                value = entry.get(u"@id")
                if value:
                    sites.add(value)

        for param in record.params:
            key = param.get(u"id") or param.get(u"name")
            if key and key not in seen_params:
                seen_params.add(key)
                params.append((param.get(u"id", u""), param.get(u"name", u"")))

        for kind, urls in record.images.items():
            if len(urls) > result.image_kinds.get(kind, 0):
                result.image_kinds[kind] = len(urls)

        result.issues.extend(record.issues)
        if progress is not None and count % 500 == 0:
            progress(count)

    if limit and count >= limit:
        result.truncated = True

    result.langs = sorted(langs)
    result.sites = sorted(sites, key=_as_int)
    result.params = params
    result.columns = sorted(paths)

    if result.source_type == "csv":
        result.columns = _csv_header(path)
    if registry is not None:
        result.unknown_columns = _register_unknown(registry, result)

    return result


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10 ** 9


def _csv_header(path):
    import csv
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            return row
    return []


def _register_unknown(registry, result):
    """Kolumny spoza rdzenia trafiają do grupy 'Nierozpoznane', nie do kosza."""
    known = registry.known_paths()
    unknown = []
    for column in result.columns:
        if column in known:
            continue
        element, attr = split_path(column)
        if attr and (element + attr) in known:
            continue
        base = LANG_IN_PATH.sub(u"", column)
        if base in known:
            continue
        if _is_handled_branch(column):
            continue
        registry.add_unknown_column(column)
        unknown.append(column)
    return unknown


HANDLED_PREFIXES = (u"/sizes/size", u"/parameters/parameter", u"/images/")


def _is_handled_branch(column):
    for prefix in HANDLED_PREFIXES:
        if column.startswith(prefix):
            return True
    return False
