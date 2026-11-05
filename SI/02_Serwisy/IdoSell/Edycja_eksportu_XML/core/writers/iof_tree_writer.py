# -*- coding: utf-8 -*-
"""Przycinanie eksportu IOF.

Wynik to ten sam dokument, tylko z wyciętymi gałęziami: zachowane przestrzenie
nazw, atrybuty, zagnieżdżenia i deklaracja XML. Dostępne wyłącznie dla źródła
XML - z CSV byłaby to budowa nowego drzewa, nie przycięcie istniejącego.

Serializacja jest własna, bo `ElementTree.tostring` dokleja deklaracje
przestrzeni nazw do każdego fragmentu, a przy zapisie strumieniowym prefiksy
muszą zostać zadeklarowane raz, w elemencie głównym.
"""

import re

from ..readers.xml_reader import local, XML_LANG

_ESCAPES = ((u"&", u"&amp;"), (u"<", u"&lt;"), (u">", u"&gt;"))
_ATTR_ESCAPES = _ESCAPES + ((u'"', u"&quot;"),)
_CONTROL = re.compile(u"[\x00-\x08\x0b\x0c\x0e-\x1f]")

#: Prefiksy używane w plikach IdoSell.
NAMESPACES = {
    u"http://www.iai-shop.com/developers/iof/extensions.phtml": u"iaiext",
    u"http://www.iai-shop.com/developers/iof.phtml": u"iof",
    u"http://www.w3.org/XML/1998/namespace": u"xml",
}


def _escape(text, table):
    for needle, replacement in table:
        text = text.replace(needle, replacement)
    return _CONTROL.sub(u"", text)


def qname(tag):
    """'{ns}name' -> 'iaiext:name', gdy przestrzeń jest znana."""
    if tag and tag[0] == u"{":
        uri, name = tag[1:].split(u"}", 1)
        prefix = NAMESPACES.get(uri)
        return u"%s:%s" % (prefix, name) if prefix else name
    return tag


class KeepSet(object):
    """Zbiór zachowywanych ścieżek, z odpowiedzią na pytania o przodków.

    Ścieżki są w konwencji `product/description/name` i `product/@id`. Element
    zostaje, gdy sam jest wybrany albo gdy prowadzi do czegoś wybranego.
    """

    def __init__(self, paths):
        self.elements = set()
        self.attributes = {}
        self.prefixes = set()
        for raw in paths or []:
            path = raw.strip().strip(u"/")
            if not path:
                continue
            if u"@" in path:
                element, attr = path.split(u"@", 1)
                element = element.rstrip(u"/")
                self.attributes.setdefault(element, set()).add(attr)
                self._add_prefixes(element)
            else:
                self.elements.add(path)
                self._add_prefixes(path)

    def _add_prefixes(self, path):
        parts = path.split(u"/")
        for index in range(1, len(parts) + 1):
            self.prefixes.add(u"/".join(parts[:index]))

    def keeps_subtree(self, path):
        """Czy ten element jest wybrany w całości (z potomkami)."""
        if path in self.elements:
            return True
        parts = path.split(u"/")
        for index in range(1, len(parts)):
            if u"/".join(parts[:index]) in self.elements:
                return True
        return False

    def leads_somewhere(self, path):
        return path in self.prefixes

    def attrs_for(self, path):
        return self.attributes.get(path)


class IofTreeWriter(object):
    """Zapisuje przycięte drzewo, produkt po produkcie."""

    extension = ".xml"

    def __init__(self, path, keep, encoding="utf-8", indent=u"  ",
                 root_attrib=None, products_attrib=None):
        self.path = path
        self.keep = keep if isinstance(keep, KeepSet) else KeepSet(keep)
        self.encoding = encoding
        self.indent = indent
        self.root_attrib = dict(root_attrib or {})
        self.products_attrib = dict(products_attrib or {})
        self._handle = None
        self.written = 0

    def open(self):
        self._handle = open(self.path, "w", encoding=self.encoding, newline="")
        self._handle.write(u'<?xml version="1.0" encoding="%s"?>\n' % self.encoding)
        self._handle.write(u"<offer%s>\n" % self._root_attributes())
        self._handle.write(u"%s<products%s>\n" % (self.indent,
                                                  _format_attrs(self.products_attrib)))
        return self

    def _root_attributes(self):
        parts = []
        for uri, prefix in sorted(NAMESPACES.items(), key=lambda kv: kv[1]):
            if prefix == u"xml":
                continue
            parts.append(u' xmlns:%s="%s"' % (prefix, uri))
        parts.append(_format_attrs(self.root_attrib))
        return u"".join(parts)

    def write_product(self, element):
        """Zapisuje jeden `<product>` po przycięciu. Pusty wynik jest pomijany."""
        text = self._render(element, u"product", 2)
        if text:
            self._handle.write(text)
            self.written += 1

    # Zgodność z interfejsem writerów wierszowych.
    def write(self, row):
        self.write_product(row)

    def _render(self, element, path, depth):
        keep_all = self.keep.keeps_subtree(path)
        if not keep_all and not self.keep.leads_somewhere(path):
            return u""

        attributes = {}
        wanted = self.keep.attrs_for(path)
        for key, value in element.attrib.items():
            name = qname(key) if key.startswith(u"{") else key
            plain = local(key)
            if keep_all or (wanted and (plain in wanted or name in wanted)):
                attributes[name] = value
        if key_is_lang(element) and (keep_all or wanted):
            attributes.setdefault(u"xml:lang", element.get(XML_LANG))

        children = []
        for child in element:
            rendered = self._render(child, path + u"/" + local(child.tag), depth + 1)
            if rendered:
                children.append(rendered)

        text = (element.text or u"").strip()
        has_body = bool(children or text)
        if not attributes and not has_body:
            # Element bez treści zostaje tylko wtedy, gdy sam był wybrany.
            if not keep_all or not element.attrib:
                return u""

        pad = self.indent * depth
        tag = qname(element.tag)
        opening = u"%s<%s%s" % (pad, tag, _format_attrs(attributes))
        if not has_body:
            return opening + u"/>\n"
        if children:
            return u"%s>\n%s%s</%s>\n" % (opening, u"".join(children), pad, tag)
        return u"%s>%s</%s>\n" % (opening, _escape(text, _ESCAPES), tag)

    def close(self):
        if self._handle is not None:
            self._handle.write(u"%s</products>\n" % self.indent)
            self._handle.write(u"</offer>\n")
            self._handle.close()
            self._handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def key_is_lang(element):
    return XML_LANG in element.attrib


def _format_attrs(attributes):
    if not attributes:
        return u""
    parts = []
    for name in attributes:
        value = attributes[name]
        if value is None:
            continue
        parts.append(u' %s="%s"' % (name, _escape(u"%s" % value, _ATTR_ESCAPES)))
    return u"".join(parts)
