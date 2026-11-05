# -*- coding: utf-8 -*-
"""Czytnik eksportu tabelarycznego z panelu IdoSell.

Nagłówki tego CSV to ścieżki IOF (`/description/name[pol]`, `/sizes/size@code`),
a wielokrotności są sklejone znakiem nowej linii wewnątrz jednej komórki.

Listy w komórkach nie są równoległe, dlatego parowanie idzie wg reguł opisanych
w DESIGN.md sekcja 1:

1. jest kolumna z kluczem (`value@parameter_id`, `stock@size_id`, `site@id`) - po niej;
2. klucz `size_id == '0'` to wartość bazowa dla rozmiarów bez własnego wpisu;
3. brak klucza, długość równa liczbie elementów nadrzędnych - po pozycji;
4. brak klucza, jedna wartość - ta sama dla wszystkich (zwinięty blok);
5. pusta kolumna - brak wartości, nie lista jednoelementowa;
6. cokolwiek innego - Issue, nie zgadywanie.
"""

import csv
import sys

from .base import BaseReader, Record, ISSUE_LIST_MISMATCH

SIZE_ROOT = u"/sizes/size"
PARAM_ROOT = u"/parameters/parameter"
PARAM_VALUE_ROOT = u"/parameters/parameter/value"

# Ścieżka kolumny -> nazwa typu zdjęć w rekordzie.
IMAGE_SOURCES = {
    u"/images/large/image": u"large",
    u"/images/icons/icon": u"icons",
    u"/images/icons/auction_icon": u"auction_icon",
    u"/images/icons/group_icon": u"group_icon",
    u"/attachments/image/picture": u"attachments",
}


def split_path(header):
    """Rozdziela nagłówek na (element, atrybut).

    '/price_retail/site@gross'        -> ('/price_retail/site', '@gross')
    '/description/name[pol]'          -> ('/description/name[pol]', None)
    '/responsible_entity/producer/@id'-> ('/responsible_entity/producer', '@id')
    '@id'                             -> ('', '@id')
    """
    at = header.find(u"@")
    if at < 0:
        return header, None
    element = header[:at].rstrip(u"/")
    return element, header[at:]


# Segmenty ścieżki IOF, które w obrębie jednego produktu potrafią się powtórzyć.
# Tylko w kolumnach takich elementów znak nowej linii skleił listę wartości.
# W pozostałych kolumnach (opisy HTML, notatka, dane producenta) nowa linia jest
# treścią — dzielenie jej gubiło wszystko poza pierwszą linią.
REPEATABLE_SEGMENTS = frozenset((
    u"site", u"size", u"stock", u"price", u"parameter", u"value",
    u"image", u"icon", u"auction_icon", u"group_icon", u"picture",
    u"product", u"product_value", u"group_by_parameter",
    u"sound", u"doc", u"movie", u"file", u"document_type",
    u"person", u"menu", u"item",
))


def is_repeatable(element):
    """Czy kolumna należy do elementu powtarzalnego — czyli czy nowa linia dzieli listę.

    '/parameters/parameter'        -> True  (segment 'parameter')
    '/sizes/size/stock'            -> True
    '/description/long_desc[pol]'  -> False (nowa linia to treść opisu)
    '/size_chart'                  -> False ('size_chart' to nie 'size')
    """
    for segment in element.split(u"/"):
        if not segment:
            continue
        bracket = segment.find(u"[")
        if bracket >= 0:
            segment = segment[:bracket]
        if segment in REPEATABLE_SEGMENTS:
            return True
    return False


def _split_cell(cell, repeatable=True):
    """Komórka -> lista wartości. Pusta komórka to brak wartości, nie [u""].

    `repeatable=False` oznacza kolumnę skalarną: cała komórka to jedna wartość,
    nawet jeśli zawiera znaki nowej linii.
    """
    if not cell:
        return []
    if repeatable and u"\n" in cell:
        return cell.split(u"\n")
    return [cell]


def align(values, count):
    """Dopasowuje listę wartości do `count` pozycji wg reguł 3-6.

    Zwraca (lista_długości_count, czy_rozjazd).
    """
    length = len(values)
    if length == count:
        return values, False
    if length == 0:
        return [u""] * count, False
    if length == 1:
        return [values[0]] * count, False
    if length > count:
        return values[:count], True
    return values + [u""] * (count - length), True


class CsvReader(BaseReader):

    source_type = "csv"

    def __init__(self, path, encoding="utf-8-sig", delimiter=None):
        BaseReader.__init__(self, path)
        self.encoding = encoding
        self.delimiter = delimiter
        self.header = []
        self._handle = None
        self._prepared = False
        # Mapy budowane raz, przy pierwszym czytaniu.
        self._size_attrs = []       # [(kolumna, '@attr')]
        self._size_blocks = {}      # '/price' -> [(kolumna, '@attr')]
        self._param_attrs = []
        self._param_value_attrs = []
        self._image_cols = {}       # typ -> [(kolumna, '@attr')]
        self._product_blocks = {}   # element -> [(kolumna, '@attr')]
        self._plain_cols = []       # kolumny bez '@'
        self._repeatable = []       # po kolumnie: czy '\n' w komórce dzieli listę

    # -- przygotowanie --------------------------------------------------

    def _open(self):
        handle = open(self.path, "r", encoding=self.encoding, newline="")
        sample = handle.read(65536)
        handle.seek(0)
        delimiter = self.delimiter
        if delimiter is None:
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = u","
        self.delimiter = delimiter
        return handle

    def _prepare(self, header):
        self.header = header
        self._repeatable = [False] * len(header)
        for index, name in enumerate(header):
            element, attr = split_path(name)
            self._repeatable[index] = is_repeatable(element)
            if attr is None:
                self._plain_cols.append((index, name))
                if element in IMAGE_SOURCES:
                    self._image_cols.setdefault(IMAGE_SOURCES[element], []).append((index, u"@url"))
                continue
            if element == SIZE_ROOT:
                self._size_attrs.append((index, attr))
            elif element.startswith(SIZE_ROOT + u"/"):
                sub = element[len(SIZE_ROOT):]
                self._size_blocks.setdefault(sub, []).append((index, attr))
            elif element == PARAM_VALUE_ROOT or element.startswith(PARAM_VALUE_ROOT + u"["):
                self._param_value_attrs.append((index, attr, name))
            elif element == PARAM_ROOT or element.startswith(PARAM_ROOT + u"["):
                self._param_attrs.append((index, attr, name))
            elif element in IMAGE_SOURCES:
                self._image_cols.setdefault(IMAGE_SOURCES[element], []).append((index, attr))
            else:
                self._product_blocks.setdefault(element, []).append((index, attr))
        self._prepared = True

    # -- czytanie -------------------------------------------------------

    def iter_records(self, limit=None):
        # Komórka ze sklejonymi opisami w kilkunastu językach bywa ogromna.
        try:
            csv.field_size_limit(sys.maxsize)
        except OverflowError:
            csv.field_size_limit(2 ** 31 - 1)

        self._handle = self._open()
        try:
            reader = csv.reader(self._handle, delimiter=self.delimiter)
            try:
                header = next(reader)
            except StopIteration:
                return
            if not self._prepared:
                self._prepare(header)

            count = 0
            for row in reader:
                if not row or not any(row):
                    continue
                if len(row) < len(header):
                    row = row + [u""] * (len(header) - len(row))
                yield self._build(row)
                count += 1
                if limit and count >= limit:
                    return
        finally:
            self.close()

    def close(self):
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    # -- budowa rekordu -------------------------------------------------

    def _build(self, row):
        record = Record()
        # Jeden przebieg po wierszu - i tak kazda kolumna trafia do `values`,
        # wiec leniwy cache tylko dokladalby wywolan funkcji.
        # Wiersz bywa dłuższy od nagłówka (nadmiarowe kolumny) - te i tak nie
        # trafią do `values`, więc dzielimy je po staremu.
        repeatable = self._repeatable
        limit = len(repeatable)
        cells = [_split_cell(value, index >= limit or repeatable[index])
                 for index, value in enumerate(row)]
        values = record.values
        for index, name in enumerate(self.header):
            column = cells[index]
            if column:
                values[name] = column

        self._build_sizes(record, cells)
        self._build_params(record, cells)
        self._build_images(record, cells)
        self._build_product_blocks(record, cells)
        return record

    def _build_sizes(self, record, cells):
        ids = []
        for index, attr in self._size_attrs:
            if attr == u"@id":
                ids = cells[index]
                break
        count = len(ids)
        if not count:
            return

        sizes = [{u"@id": ids[i]} for i in range(count)]
        for index, attr in self._size_attrs:
            if attr == u"@id":
                continue
            values, mismatch = align(cells[index], count)
            if mismatch:
                record.add_issue(ISSUE_LIST_MISMATCH, u"%s%s" % (SIZE_ROOT, attr))
            for i in range(count):
                sizes[i][attr] = values[i]

        for sub, columns in self._size_blocks.items():
            keyed = self._keyed_entries(columns, cells, u"@size_id")
            if keyed is not None:
                for i, size in enumerate(sizes):
                    entry = keyed.get(size[u"@id"]) or keyed.get(u"0") or {}
                    for attr, value in entry.items():
                        size[sub + attr] = value
                continue
            for index, attr in columns:
                values, mismatch = align(cells[index], count)
                if mismatch:
                    record.add_issue(ISSUE_LIST_MISMATCH, u"%s%s%s" % (SIZE_ROOT, sub, attr))
                for i in range(count):
                    sizes[i][sub + attr] = values[i]

        record.sizes = sizes

    def _keyed_entries(self, columns, cells, key_attr):
        """Wpisy bloku zmapowane po kolumnie-kluczu, albo None gdy klucza brak."""
        key_index = None
        for index, attr in columns:
            if attr == key_attr:
                key_index = index
                break
        if key_index is None:
            return None
        keys = cells[key_index]
        if not keys:
            return None
        count = len(keys)
        prepared = [(attr, cells[index]) for index, attr in columns if attr != key_attr]
        result = {}
        for position, key in enumerate(keys):
            entry = {}
            for attr, values in prepared:
                length = len(values)
                if length == count:
                    entry[attr] = values[position]
                elif length == 1:
                    entry[attr] = values[0]
                else:
                    entry[attr] = u""
            result[key] = entry
        return result

    def _build_params(self, record, cells):
        ids = []
        attr_columns = []
        for index, attr, name in self._param_attrs:
            if attr == u"@id":
                ids = cells[index]
            else:
                attr_columns.append((attr.lstrip(u"@"), cells[index]))
        count = len(ids)
        if not count:
            return

        values_by_param = {}
        value_key_index = None
        for index, attr, name in self._param_value_attrs:
            if attr == u"@parameter_id":
                value_key_index = index
                break
        if value_key_index is not None:
            keys = cells[value_key_index]
            value_columns = [(attr, cells[index])
                             for index, attr, _ in self._param_value_attrs
                             if attr != u"@parameter_id"]
            # Parametr może mieć kilka wartości - ten sam parameter_id powtarza
            # się wtedy w liście, więc zbieramy wpisy, nie nadpisujemy.
            for position, key in enumerate(keys):
                entry = {}
                for attr, values in value_columns:
                    entry[attr] = values[position] if position < len(values) else u""
                values_by_param.setdefault(key, []).append(entry)

        params = []
        for position in range(count):
            param = {u"id": ids[position]}
            for key, values in attr_columns:
                param[key] = values[position] if position < len(values) else u""
            found = values_by_param.get(ids[position]) or []
            texts = [t for t in (_first_named(e) for e in found) if t]
            param[u"value"] = texts[0] if texts else u""
            param[u"values"] = texts
            if not param.get(u"name"):
                param[u"name"] = _pick_lang(param, u"name")
            params.append(param)
        record.params = params

    def _build_images(self, record, cells):
        for kind, columns in self._image_cols.items():
            urls = []
            for index, attr in columns:
                if attr == u"@url":
                    urls = cells[index]
                    break
            if urls:
                record.images[kind] = urls

    def _build_product_blocks(self, record, cells):
        blocks = record.blocks
        for element, columns in self._product_blocks.items():
            prepared = [(attr, cells[index]) for index, attr in columns]
            count = 0
            for _, values in prepared:
                if len(values) > count:
                    count = len(values)
            if not count:
                continue
            entries = []
            for position in range(count):
                entry = {}
                for attr, values in prepared:
                    length = len(values)
                    if length == count:
                        entry[attr] = values[position]
                    elif length == 1:
                        entry[attr] = values[0]
                    else:
                        entry[attr] = u""
                entries.append(entry)
            blocks[element] = entries


def _pick_lang(mapping, base):
    """Wartość klucza `base` w dowolnym języku: 'name[pol]' -> 'name'."""
    prefix = base + u"["
    for key in sorted(mapping):
        if key.startswith(prefix) and mapping[key]:
            return mapping[key]
    for key in sorted(mapping):
        if key.startswith(prefix):
            return mapping[key]
    return u""


def _first_named(entry):
    """Wartość parametru: preferuje kolumnę nazwy w dowolnym języku."""
    if not entry:
        return u""
    for attr in sorted(entry):
        if attr.startswith(u"@name"):
            return entry[attr]
    for attr in sorted(entry):
        if entry[attr]:
            return entry[attr]
    return u""
