# -*- coding: utf-8 -*-
"""Zapis płaskiego CSV."""

import csv

QUOTING = {
    "minimal": csv.QUOTE_MINIMAL,
    "all": csv.QUOTE_ALL,
    "nonnumeric": csv.QUOTE_NONNUMERIC,
    "none": csv.QUOTE_NONE,
}


class CsvWriter(object):

    extension = ".csv"

    def __init__(self, path, columns, delimiter=u";", encoding="utf-8-sig",
                 quoting="minimal", line_terminator="\r\n", header=True,
                 list_separator=u" | ", newline_replacement=u" "):
        self.path = path
        self.columns = list(columns)
        self.delimiter = delimiter
        self.encoding = encoding
        self.quoting = QUOTING.get(quoting, csv.QUOTE_MINIMAL)
        self.line_terminator = line_terminator
        self.header = header
        # Dwie różne rzeczy, kiedyś mylone ze sobą:
        # - `list_separator` skleja wiele wartości jednej kolumny (parametry, zdjęcia);
        # - `newline_replacement` podmienia nową linię *wewnątrz* jednej wartości,
        #   bo znak nowej linii w komórce rozbija większość importerów. Opis HTML
        #   jest jedną wartością z nowymi liniami - nie wolno go ciąć ani znaczyć
        #   separatorem listy.
        self.list_separator = list_separator
        self.newline_replacement = newline_replacement
        self._handle = None
        self._writer = None
        self.written = 0

    def open(self):
        self._handle = open(self.path, "w", encoding=self.encoding, newline="")
        self._writer = csv.writer(self._handle, delimiter=self.delimiter,
                                  quoting=self.quoting,
                                  lineterminator=self.line_terminator)
        if self.header:
            self._writer.writerow(self.columns)
        return self

    def write(self, row):
        values = []
        for column in self.columns:
            value = row.get(column, u"")
            if isinstance(value, list):
                value = self.list_separator.join([v for v in value if v])
            elif value is None:
                value = u""
            elif not isinstance(value, str):
                value = u"%s" % value
            if self.newline_replacement is not None and (
                    u"\n" in value or u"\r" in value):
                value = value.replace(u"\r\n", u"\n").replace(u"\r", u"\n")
                value = value.replace(u"\n", self.newline_replacement)
            values.append(value)
        self._writer.writerow(values)
        self.written += 1

    def close(self):
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
