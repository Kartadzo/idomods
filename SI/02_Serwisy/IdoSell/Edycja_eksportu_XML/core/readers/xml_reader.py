# -*- coding: utf-8 -*-
"""Czytnik eksportu IOF 3.0 z panelu IdoSell.

Produkuje ten sam rekord pośredni co czytnik CSV, więc ścieżki są zapisywane
w konwencji nagłówka CSV: prefiks `iaiext:` znika, `xml:lang` staje się sufiksem
`[pol]`, a atrybuty dostają przedrostek `@`.

    <iaiext:price_retail><iaiext:site gross="12.00" id="1"/>  ->  /price_retail/site@gross
    <name xml:lang="pol">Nazwa</name>                         ->  /description/name[pol]

Czytanie idzie strumieniowo (`iterparse` + `clear`), bo pliki potrafią mieć
setki tysięcy produktów.
"""

import xml.etree.ElementTree as ET

from .base import BaseReader, Record

XML_LANG = u"{http://www.w3.org/XML/1998/namespace}lang"

# Gałęzie obsługiwane osobno - nie wchodzą do generycznego spaceru po drzewie.
SPECIAL_BRANCHES = frozenset([u"sizes", u"parameters", u"images", u"description",
                              u"opinions"])

# Ścieżka w drzewie zdjęć -> nazwa typu w rekordzie.
IMAGE_BRANCHES = {
    u"large": u"large",
    u"medium": u"medium",
    u"small": u"small",
    u"originals": u"originals",
}

# Gałąź `icons` mieszczą trzy różne rzeczy naraz. CSV rozdziela je na osobne
# kolumny, więc XML też musi je rozdzielić - inaczej ikona grupy udawałaby
# ikonę karty produktu.
ICON_KINDS = {
    u"icon": u"icons",
    u"auction_icon": u"auction_icon",
    u"group_icon": u"group_icon",
}


def local(tag):
    """Nazwa lokalna bez przestrzeni nazw."""
    if tag and tag[0] == u"{":
        return tag.rsplit(u"}", 1)[1]
    return tag


def find_child(element, name):
    """Dziecko o danej nazwie lokalnej, bez względu na przestrzeń nazw.

    Ten sam element bywa zapisany jako `images` albo `iaiext:images` - zależnie
    od sklepu i wersji eksportu. `find` po samej nazwie trafiałby tylko w ten
    pierwszy przypadek.
    """
    for item in element:
        if local(item.tag) == name:
            return item
    return None


def _child_text(element, name):
    found = find_child(element, name)
    if found is None:
        return u""
    return (found.text or u"").strip()


def _as_note(text):
    """Ocena jako liczba 1-5 albo None, gdy opinia jej nie ma."""
    try:
        note = int(float(text))
    except (TypeError, ValueError):
        return None
    return note if 1 <= note <= 5 else None


def _attributes(element):
    """Atrybuty elementu jako {'@nazwa': wartość}, bez xml:lang."""
    result = {}
    for key, value in element.attrib.items():
        if key == XML_LANG:
            continue
        result[u"@" + local(key)] = value
    return result


class XmlReader(BaseReader):

    source_type = "xml"

    def iter_records(self, limit=None):
        """Produkty najwyższego poziomu.

        Eksport potrafi zagnieździć `product` w `associated_products` - to
        odsyłacz do innego towaru, nie osobny produkt. Bez liczenia zagnieżdżeń
        sklep z produktami powiązanymi dawał kilka razy więcej wierszy, niż ma
        towarów.
        """
        count = 0
        depth = 0
        context = ET.iterparse(self.path, events=("start", "end"))
        root = None
        for event, element in context:
            if root is None:
                root = element
            if local(element.tag) != u"product":
                continue
            if event == "start":
                depth += 1
                continue
            depth -= 1
            if depth:
                continue
            yield self._build(element)
            count += 1
            element.clear()
            # Bez tego rodzeństwo zostaje w pamięci i drzewo rośnie do rozmiaru pliku.
            if root is not None:
                for done in list(root):
                    for stale in list(done):
                        if stale is not element:
                            done.remove(stale)
            if limit and count >= limit:
                return

    # -- budowa rekordu -------------------------------------------------

    def _build(self, product):
        record = Record()
        for key, value in _attributes(product).items():
            record.values[key] = [value]

        for child in product:
            name = local(child.tag)
            if name in SPECIAL_BRANCHES:
                continue
            self._walk(record, child, u"/" + name)

        self._build_description(record, product)
        self._build_sizes(record, product)
        self._build_params(record, product)
        self._build_images(record, product)
        self._build_opinions(record, product)
        return record

    def _walk(self, record, element, path):
        """Zapisuje element i jego potomków jako ścieżki kanoniczne."""
        lang = element.get(XML_LANG)
        attributes = _attributes(element)

        if attributes:
            record.blocks.setdefault(path, []).append(attributes)
            for attr, value in attributes.items():
                record.values.setdefault(path + attr, []).append(value)
                if lang:
                    record.values.setdefault(
                        u"%s%s[%s]" % (path, attr, lang), []).append(value)

        text = (element.text or u"").strip()
        if text:
            record.values.setdefault(path, []).append(text)
            if lang:
                record.values.setdefault(u"%s[%s]" % (path, lang), []).append(text)

        for child in element:
            self._walk(record, child, path + u"/" + local(child.tag))

    def _build_description(self, record, product):
        description = find_child(product, u"description")
        if description is None:
            return
        for child in description:
            name = local(child.tag)
            lang = child.get(XML_LANG)
            text = u"".join(child.itertext()).strip()
            path = u"/description/" + name
            if text:
                record.values.setdefault(path, []).append(text)
            if lang:
                record.values[u"%s[%s]" % (path, lang)] = [text]
            for attr, value in _attributes(child).items():
                record.values.setdefault(path + attr, []).append(value)

    def _build_sizes(self, record, product):
        container = find_child(product, u"sizes")
        if container is None:
            return
        for key, value in (container.attrib or {}).items():
            record.values.setdefault(u"/sizes@" + local(key), []).append(value)

        sizes = []
        for element in container:
            if local(element.tag) != u"size":
                continue
            size = _attributes(element)
            for child in element:
                prefix = u"/" + local(child.tag)
                for attr, value in _attributes(child).items():
                    size[prefix + attr] = value
                text = (child.text or u"").strip()
                if text:
                    size[prefix] = text
                for grandchild in child:
                    sub = prefix + u"/" + local(grandchild.tag)
                    for attr, value in _attributes(grandchild).items():
                        size[sub + attr] = value
            sizes.append(size)
        record.sizes = sizes

    def _build_params(self, record, product):
        container = find_child(product, u"parameters")
        if container is None:
            return
        params = []
        for element in container:
            if local(element.tag) != u"parameter":
                continue
            attributes = _attributes(element)
            param = {
                u"id": attributes.get(u"@id", u""),
                u"name": attributes.get(u"@name", u""),
                u"type": attributes.get(u"@type", u""),
                u"priority": attributes.get(u"@priority", u""),
            }
            values = []
            for child in element:
                if local(child.tag) != u"value":
                    continue
                value_attrs = _attributes(child)
                text = (child.text or u"").strip()
                values.append(value_attrs.get(u"@name") or text)
            param[u"value"] = values[0] if values else u""
            param[u"values"] = values
            params.append(param)
        record.params = params

    def _build_images(self, record, product):
        container = find_child(product, u"images")
        if container is None:
            return
        for key, value in (container.attrib or {}).items():
            record.values.setdefault(u"/images@" + local(key), []).append(value)

        for branch in container:
            name = local(branch.tag)
            if name == u"icons":
                self._build_icons(record, branch)
                continue
            kind = IMAGE_BRANCHES.get(name)
            if kind is None:
                continue
            urls = []
            for image in branch:
                url = image.get(u"url")
                if url:
                    urls.append((image.get(u"priority") or u"", url))
            if urls:
                record.images[kind] = [url for _, url in urls]

    def _build_icons(self, record, branch):
        for element in branch:
            kind = ICON_KINDS.get(local(element.tag))
            url = element.get(u"url")
            if kind is None or not url:
                continue
            record.images.setdefault(kind, []).append(url)

    def _build_opinions(self, record, product):
        """Statystyki opinii liczone w locie.

        IOF nie ma gotowych agregatów - są pojedyncze opinie z oceną w `note`.
        Trzymanie ich w całości nie ma sensu przy plikach na setki tysięcy
        produktów, więc zostaje sama statystyka: ile, jaka średnia i jak
        rozkładają się oceny.
        """
        container = find_child(product, u"opinions")
        if container is None:
            return
        total = 0
        confirmed = 0
        notes = []
        distribution = dict((n, 0) for n in range(1, 6))
        last_date = u""
        for opinion in container:
            if local(opinion.tag) != u"opinion":
                continue
            total += 1
            if _child_text(opinion, u"confirmed").lower() == u"y":
                confirmed += 1
            note = _as_note(_child_text(opinion, u"note"))
            if note:
                notes.append(note)
                distribution[note] += 1
            added = _child_text(opinion, u"date_add")
            if added and not added.startswith(u"0000") and added > last_date:
                last_date = added
        if not total:
            return
        record.values[u"/opinions@count"] = [u"%d" % total]
        record.values[u"/opinions@confirmed"] = [u"%d" % confirmed]
        if notes:
            average = sum(notes) / float(len(notes))
            record.values[u"/opinions@average"] = [u"%.2f" % average]
        for note, count in distribution.items():
            record.values[u"/opinions@note_%d" % note] = [u"%d" % count]
        if last_date:
            record.values[u"/opinions@last_date"] = [last_date]
