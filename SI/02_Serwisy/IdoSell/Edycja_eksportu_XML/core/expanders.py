# -*- coding: utf-8 -*-
"""Rozbijanie kolekcji na kolumny wyjściowe.

Parametry i zdjęcia to jedyne dane, których liczba zmienia się między
produktami, więc każde z nich ma własny tryb rozbicia wybierany przez
użytkownika. Oba expandery zwracają gotowe pary kolumna -> wartość, a listę
kolumn deklarują z góry, żeby nagłówek CSV i kolejność elementów XML były stałe
w całym pliku.
"""

# Tryby parametrów.
PARAM_RAW = "raw"                     # jedna kolumna, wartości jak w źródle
PARAM_COLUMN = "column_per_param"     # kolumna na parametr
PARAM_PAIRS = "name_value_pairs"      # nazwa i wartość w osobnych kolumnach

# Rodzaje ikon - nazwy zgodne z tym, jak rozdziela je eksport CSV.
ICON_KIND_LABELS = [
    (u"icons", u"ikona karty produktu"),
    (u"auction_icon", u"ikona aukcyjna"),
    (u"group_icon", u"ikona grupy"),
]

# Tryby zdjęć.
IMAGE_COLUMNS = "columns"             # image, image_extra_1, image_extra_2, ...
IMAGE_SINGLE = "single"               # wszystko w jednej kolumnie
IMAGE_FIRST = "first"                 # tylko pierwsze

PARAM_MODE_LABELS = [
    (PARAM_RAW, u"komórka oryginalna"),
    (PARAM_COLUMN, u"kolumna na parametr"),
    (PARAM_PAIRS, u"nazwa i wartość osobno"),
]

IMAGE_MODE_LABELS = [
    (IMAGE_COLUMNS, u"kolumna na zdjęcie"),
    (IMAGE_SINGLE, u"jedna kolumna"),
    (IMAGE_FIRST, u"tylko pierwsze"),
]


class ParamExpander(object):
    """Zamienia listę parametrów produktu na kolumny.

    W trybie `column_per_param` kolumny biorą się z listy wykrytej przy skanie.
    Parametr, który pojawi się poza tą listą (skan miał limit), trafia do
    kolumny zbiorczej i do raportu - nie znika po cichu.
    """

    def __init__(self, mode=PARAM_RAW, names=None, separator=u", ", max_pairs=10,
                 column_name=u"parametry", other_column=True, order="source",
                 line_separator=u" | "):
        self.mode = mode
        self.names = list(names or [])
        self.separator = separator
        # Separator między kolejnymi parametrami w kolumnie zbiorczej. Kiedyś
        # sklejało to znakiem nowej linii, licząc na podmianę w writerze - przez
        # co nie dało się odróżnić granicy parametru od nowej linii w treści.
        self.line_separator = line_separator
        self.max_pairs = max_pairs
        self.column_name = column_name
        self.other_column = other_column
        self.order = order
        self.overflow = []

    def columns(self):
        if self.mode == PARAM_COLUMN:
            names = list(self.names)
            if self.other_column:
                names.append(u"parametry_pozostale")
            return names
        if self.mode == PARAM_PAIRS:
            columns = []
            for index in range(1, self.max_pairs + 1):
                columns.append(u"parametr_%d_nazwa" % index)
                columns.append(u"parametr_%d_wartosc" % index)
            return columns
        return [self.column_name]

    def expand(self, record):
        params = self._ordered(record.params)
        if self.mode == PARAM_COLUMN:
            return self._as_columns(params)
        if self.mode == PARAM_PAIRS:
            return self._as_pairs(params)
        return self._as_raw(params)

    # -- tryby ----------------------------------------------------------

    def _as_raw(self, params):
        lines = []
        for param in params:
            name = param.get(u"name") or param.get(u"id") or u""
            value = _param_value(param, self.separator)
            lines.append(u"%s: %s" % (name, value) if value else name)
        return {self.column_name: self.line_separator.join(lines)}

    def _as_columns(self, params):
        row = dict((name, u"") for name in self.names)
        leftovers = []
        wanted = set(self.names)
        for param in params:
            name = param.get(u"name") or param.get(u"id") or u""
            value = _param_value(param, self.separator)
            if name in wanted:
                # Jeden parametr - jedna kolumna, także gdy ma kilka wartości.
                if row.get(name):
                    row[name] = row[name] + self.separator + value
                else:
                    row[name] = value
            else:
                leftovers.append(u"%s: %s" % (name, value) if value else name)
                if name and name not in self.overflow:
                    self.overflow.append(name)
        if self.other_column:
            row[u"parametry_pozostale"] = self.line_separator.join(leftovers)
        return row

    def _as_pairs(self, params):
        row = {}
        for index in range(1, self.max_pairs + 1):
            row[u"parametr_%d_nazwa" % index] = u""
            row[u"parametr_%d_wartosc" % index] = u""
        for position, param in enumerate(params[: self.max_pairs], start=1):
            row[u"parametr_%d_nazwa" % position] = param.get(u"name") or param.get(u"id") or u""
            row[u"parametr_%d_wartosc" % position] = _param_value(param, self.separator)
        if len(params) > self.max_pairs:
            dropped = len(params) - self.max_pairs
            if dropped not in self.overflow:
                self.overflow.append(dropped)
        return row

    def _ordered(self, params):
        if self.order == "priority":
            return sorted(params, key=lambda p: _as_number(p.get(u"priority")))
        return params


class IconExpander(object):
    """Ikona produktu jako jedna kolumna.

    Ikona to nie zdjęcie produktu - w panelu jest miniaturą karty, ikoną grupy
    albo aukcji - dlatego ma osobną kolumnę i osobny przełącznik. Bywa jednak
    jedynym obrazkiem w dobrej proporcji, stąd opcja wystawienia jej jako
    zdjęcia głównego (obsługuje ją ImageExpander).
    """

    def __init__(self, kind=u"icons", column_name=u"icon"):
        self.kind = kind
        self.column_name = column_name or u"icon"

    def columns(self):
        return [self.column_name]

    def expand(self, record):
        urls = list(record.images.get(self.kind) or [])
        return {self.column_name: urls[0] if urls else u""}


class ImageExpander(object):
    """Zamienia listę adresów zdjęć na kolumny."""

    def __init__(self, kind=u"large", mode=IMAGE_COLUMNS, count=5, separator=u", ",
                 base_name=u"image", extra_name=u"image_extra_*", lead_kind=None):
        self.kind = kind
        self.mode = mode
        self.count = max(1, int(count or 1))
        self.separator = separator
        self.base_name = base_name or u"image"
        self.extra_name = extra_name or u"image_extra_*"
        # Ikona wystawiona jako zdjęcie główne: wchodzi przed zdjęcia, reszta
        # przesuwa się o jedno miejsce. Sklepy, które trzymają zdjęcie
        # katalogowe w ikonie, dostają w feedzie właściwy obrazek pierwszy.
        self.lead_kind = lead_kind

    def urls(self, record):
        found = list(record.images.get(self.kind) or [])
        if not self.lead_kind:
            return found
        lead = list(record.images.get(self.lead_kind) or [])[:1]
        return lead + [url for url in found if url not in lead]

    def numbered(self, index):
        """Nazwa kolejnego zdjęcia. Numer wchodzi w miejsce `*` albo `{n}`.

        Wzorzec bez znaku numeru dostaje go na końcu - inaczej wszystkie
        kolumny nazywałyby się tak samo i zostałaby z nich jedna.
        """
        number = unicode_str(index)
        pattern = self.extra_name
        if u"*" in pattern:
            return pattern.replace(u"*", number)
        if u"{n}" in pattern:
            return pattern.replace(u"{n}", number)
        return pattern + number

    def columns(self):
        if self.mode == IMAGE_COLUMNS:
            columns = [self.base_name]
            for index in range(1, self.count):
                columns.append(self.numbered(index))
            return columns
        return [self.base_name]

    def expand(self, record):
        urls = self.urls(record)
        if self.mode == IMAGE_SINGLE:
            return {self.base_name: self.separator.join(urls)}
        if self.mode == IMAGE_FIRST:
            return {self.base_name: urls[0] if urls else u""}
        row = {self.base_name: urls[0] if urls else u""}
        for index in range(1, self.count):
            row[self.numbered(index)] = urls[index] if index < len(urls) else u""
        return row


def unicode_str(value):
    return u"%d" % value if isinstance(value, int) else u"%s" % value


def _param_value(param, separator):
    values = param.get(u"values")
    if isinstance(values, list) and values:
        return separator.join([v for v in values if v])
    return param.get(u"value") or u""


def _as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 10.0 ** 9
