# -*- coding: utf-8 -*-
"""Wspólny kształt danych dla obu czytników.

Czytnik XML i czytnik CSV produkują ten sam rekord pośredni, kluczowany ścieżką
w konwencji nagłówka CSV (`/description/name[pol]`, `/price_retail/site@gross`).
Dzięki temu reszta aplikacji nie wie, z jakiego pliku przyszły dane.
"""

# Rodzaje problemów raportowanych przy czytaniu.
ISSUE_LIST_MISMATCH = u"rozjechane listy"
ISSUE_UNKNOWN_COLUMN = u"nieznana kolumna"
ISSUE_PARAM_ORPHAN = u"parametr bez pary"
ISSUE_PARSE = u"błąd odczytu"


class Issue(object):
    """Problem napotkany przy czytaniu - trafia do raportu, nie do wyniku."""

    __slots__ = ("product_id", "kind", "detail")

    def __init__(self, product_id, kind, detail):
        self.product_id = product_id
        self.kind = kind
        self.detail = detail

    def __str__(self):
        return u"produkt %s: %s - %s" % (self.product_id, self.kind, self.detail)


class Record(object):
    """Jeden produkt ze wszystkim, co da się z niego wyciągnąć.

    values  - ścieżka kanoniczna -> lista wartości (zawsze lista, może być pusta)
    blocks  - element powtarzalny -> lista wpisów, każdy to {'@atrybut': wartość}
              np. '/price_retail/site' -> [{'@gross': '12.00', '@id': '1', '@size_id': '0'}]
    sizes   - lista rozmiarów, każdy to {'@id', '@name', '/price@gross', ...}
    params  - lista parametrów: {'id', 'name', 'value', 'type', 'priority'}
    images  - {'large': [url, ...], 'icons': [...], 'medium': [...], ...}
    issues  - lista Issue
    """

    __slots__ = ("values", "blocks", "sizes", "params", "images", "issues")

    def __init__(self, values=None, blocks=None, sizes=None, params=None,
                 images=None, issues=None):
        self.values = values if values is not None else {}
        self.blocks = blocks if blocks is not None else {}
        self.sizes = sizes if sizes is not None else []
        self.params = params if params is not None else []
        self.images = images if images is not None else {}
        self.issues = issues if issues is not None else []

    @property
    def product_id(self):
        return self.first(u"@id")

    def first(self, path, default=u""):
        """Pierwsza wartość spod ścieżki albo `default`."""
        values = self.values.get(path)
        if not values:
            return default
        value = values[0]
        return default if value is None else value

    def all(self, path):
        """Wszystkie wartości spod ścieżki jako lista."""
        return self.values.get(path) or []

    def block(self, element, site=None, size_id=None):
        """Wpis bloku powtarzalnego wybrany po sklepie i rozmiarze.

        Wpis o `size_id == '0'` jest wartością bazową: bierzemy go, gdy rozmiar
        nie ma własnego wpisu. Tak panel zapisuje ceny wspólne dla rozmiarów.
        """
        entries = self.blocks.get(element)
        if not entries:
            return None
        if site is not None:
            narrowed = [e for e in entries if e.get(u"@id", site) == site]
            if narrowed:
                entries = narrowed
        if size_id is not None:
            exact = [e for e in entries if e.get(u"@size_id") == size_id]
            if exact:
                return exact[0]
            base = [e for e in entries if e.get(u"@size_id") in (u"0", u"", None)]
            if base:
                return base[0]
        return entries[0]

    def size_value(self, size, path, default=u""):
        """Wartość z rozmiaru z odwrotem do poziomu produktu."""
        value = size.get(path)
        if value not in (None, u""):
            return value
        return self.first(path, default)

    def add_issue(self, kind, detail):
        self.issues.append(Issue(self.product_id, kind, detail))


class BaseReader(object):
    """Interfejs czytnika. Implementacje: XmlReader, CsvReader."""

    #: 'xml' albo 'csv'
    source_type = None

    def __init__(self, path):
        self.path = path

    def iter_records(self, limit=None):
        """Generator obiektów Record. `limit` przerywa czytanie po N produktach."""
        raise NotImplementedError

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def detect_source_type(path):
    """Rozpoznaje typ pliku po zawartości, nie po rozszerzeniu."""
    with open(path, "rb") as handle:
        head = handle.read(4096)
    if head[:3] == b"\xef\xbb\xbf":
        head = head[3:]
    if head.lstrip()[:1] == b"<":
        return "xml"
    return "csv"


def open_reader(path):
    """Zwraca czytnik dopasowany do zawartości pliku."""
    kind = detect_source_type(path)
    if kind == "xml":
        from .xml_reader import XmlReader
        return XmlReader(path)
    from .csv_reader import CsvReader
    return CsvReader(path)
