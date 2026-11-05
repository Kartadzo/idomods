# -*- coding: utf-8 -*-
"""Zapis prostego XML, który arkusze kalkulacyjne wczytują bez konfiguracji.

Płaskie drzewo, jeden element na wartość, bez atrybutów i przestrzeni nazw.
Puste elementy zostają w wyniku, bo ich brak rozjeżdża kolumny przy imporcie.
"""

import re

_INVALID = re.compile(r"[^0-9A-Za-z_.\-]")
_ESCAPES = ((u"&", u"&amp;"), (u"<", u"&lt;"), (u">", u"&gt;"))

# Znaki, których XML 1.0 nie dopuszcza nawet w postaci encji.
_CONTROL = re.compile(u"[\x00-\x08\x0b\x0c\x0e-\x1f]")

POLISH_MAP = {
    u"ą": u"a", u"ć": u"c", u"ę": u"e", u"ł": u"l", u"ń": u"n",
    u"ó": u"o", u"ś": u"s", u"ź": u"z", u"ż": u"z",
    u"Ą": u"A", u"Ć": u"C", u"Ę": u"E", u"Ł": u"L", u"Ń": u"N",
    u"Ó": u"O", u"Ś": u"S", u"Ź": u"Z", u"Ż": u"Z",
}


def element_name(label, fallback=u"pole"):
    """Nazwa docelowa -> poprawna nazwa elementu XML."""
    text = u"".join(POLISH_MAP.get(ch, ch) for ch in (label or u""))
    text = text.strip().replace(u" ", u"_")
    text = _INVALID.sub(u"_", text)
    text = text.strip(u"_")
    if not text:
        return fallback
    if text[0].isdigit() or text[0] in u".-":
        text = u"_" + text
    return text


def escape(text):
    for needle, replacement in _ESCAPES:
        text = text.replace(needle, replacement)
    return _CONTROL.sub(u"", text)


class SimpleXmlWriter(object):

    extension = ".xml"

    def __init__(self, path, columns, root=u"products", item=u"product",
                 encoding="utf-8", indent=u"  ", keep_empty=True,
                 cdata=False, list_separator=u", ", newline_replacement=None):
        self.path = path
        self.columns = list(columns)
        self.root = element_name(root, u"products")
        self.item = element_name(item, u"product")
        self.encoding = encoding
        self.indent = indent
        self.keep_empty = keep_empty
        self.cdata = cdata
        # `list_separator` skleja wiele wartości kolumny, `newline_replacement`
        # podmienia nową linię wewnątrz jednej wartości (None = zostawia ją).
        self.list_separator = list_separator
        self.newline_replacement = newline_replacement
        self.names = dict((c, element_name(c)) for c in self.columns)
        self._handle = None
        self.written = 0

    def open(self):
        self._handle = open(self.path, "w", encoding=self.encoding, newline="")
        self._handle.write(u'<?xml version="1.0" encoding="%s"?>\n' % self.encoding)
        self._handle.write(u"<%s>\n" % self.root)
        return self

    def write(self, row):
        parts = [self.indent, u"<", self.item, u">\n"]
        for column in self.columns:
            value = row.get(column, u"")
            if isinstance(value, list):
                value = (self.list_separator or u", ").join([v for v in value if v])
            elif value is None:
                value = u""
            elif not isinstance(value, str):
                value = u"%s" % value
            if not value and not self.keep_empty:
                continue
            if self.newline_replacement is not None and u"\n" in value:
                value = value.replace(u"\n", self.newline_replacement)
            name = self.names[column]
            if self.cdata and value:
                body = u"<![CDATA[%s]]>" % value.replace(u"]]>", u"]]]]><![CDATA[>")
            else:
                body = escape(value)
            parts.append(u"%s%s<%s>%s</%s>\n" % (self.indent, self.indent, name, body, name))
        parts.append(u"%s</%s>\n" % (self.indent, self.item))
        self._handle.write(u"".join(parts))
        self.written += 1

    def close(self):
        if self._handle is not None:
            self._handle.write(u"</%s>\n" % self.root)
            self._handle.close()
            self._handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
