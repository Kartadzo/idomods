# -*- coding: utf-8 -*-
"""Potok eksportu: czytaj -> zbuduj wiersz -> odfiltruj -> zastosuj reguły -> zapisz.

Wszystko idzie strumieniowo. Przy setkach tysięcy produktów nic nie może
lądować w pamięci w całości - ani wejście, ani wynik.
"""

import os
import xml.etree.ElementTree as ET

from . import structures as structures_mod
from .expanders import IconExpander, ImageExpander, ParamExpander, PARAM_RAW
from .readers.base import open_reader, detect_source_type
from .naming import output_name
from .readers.xml_reader import local
from .rules import RuleSet
from .schema import Context, build_registry
from .writers.csv_writer import CsvWriter
from .writers.iof_tree_writer import IofTreeWriter, KeepSet
from .writers.simple_xml_writer import SimpleXmlWriter

ROW_PRODUCT = "product"
ROW_SIZE = "size"


class Cancelled(Exception):
    """Rzucane, gdy użytkownik przerwie eksport."""


class Report(object):

    def __init__(self):
        self.written = 0
        self.skipped = 0
        self.read = 0
        self.issues = []
        self.param_overflow = []
        self.missing_fields = []
        self.output_path = u""

    def summary(self):
        parts = [u"zapisano %d wierszy" % self.written]
        if self.skipped:
            parts.append(u"pominięto %d przez filtry" % self.skipped)
        if self.issues:
            parts.append(u"%d ostrzeżeń przy odczycie" % len(self.issues))
        if self.param_overflow:
            parts.append(u"%d parametrów poza listą kolumn" % len(self.param_overflow))
        if self.missing_fields:
            parts.append(u"%d pól niedostępnych w źródle" % len(self.missing_fields))
        return u", ".join(parts)


class ExportConfig(object):
    """Wszystko, co użytkownik wybrał - to samo, co ląduje w profilu."""

    def __init__(self):
        self.source_path = u""
        self.source_type = None
        self.structure = None
        self.lang = u"pol"
        self.site = u"1"
        self.row_context = ROW_PRODUCT
        self.ruleset = RuleSet()
        self.output_path = u""
        # Parametry i zdjęcia.
        self.param_mode = PARAM_RAW
        self.param_names = []
        self.param_separator = u", "
        self.param_max_pairs = 10
        self.param_other_column = True
        self.param_order = "source"
        self.include_params = False
        self.image_kind = u"large"
        self.image_mode = "columns"
        self.image_count = 5
        self.image_separator = u", "
        self.include_images = False
        self.image_base_name = u"image"
        self.image_extra_name = u"image_extra_*"
        # Ikony - osobna kolumna, niezależna od zdjęć produktowych.
        self.include_icons = False
        self.icon_kind = u"icons"
        self.icon_column_name = u"icon"
        self.icon_as_main_image = False
        # Pisownia nagłówków - dotyczy wszystkich nazw wyniku naraz.
        self.uppercase_names = False
        # Opcje zapisu.
        self.csv_delimiter = u";"
        self.csv_encoding = "utf-8-sig"
        self.csv_quoting = "minimal"
        self.csv_header = True
        self.xml_root = u"products"
        self.xml_item = u"product"
        self.xml_keep_empty = True
        self.xml_cdata = False

    def detect(self):
        if self.source_path and not self.source_type:
            self.source_type = detect_source_type(self.source_path)
        return self.source_type


class Pipeline(object):

    def __init__(self, config, registry=None):
        self.config = config
        self.registry = registry or build_registry()
        self.report = Report()
        self._param_expander = None
        self._image_expander = None
        self._icon_expander = None

    # -- kolumny --------------------------------------------------------

    def param_expander(self):
        if self._param_expander is None:
            cfg = self.config
            self._param_expander = ParamExpander(
                mode=cfg.param_mode, names=cfg.param_names,
                separator=cfg.param_separator, max_pairs=cfg.param_max_pairs,
                other_column=cfg.param_other_column, order=cfg.param_order,
                line_separator=self._line_separator())
        return self._param_expander

    def _line_separator(self):
        """Czym rozdzielić kolejne parametry w kolumnie zbiorczej.

        W XML element i tak jest jeden, więc wystarczy spacja; w CSV kreska
        pozwala rozpoznać granicę parametru okiem i regułą.
        """
        structure = self.config.structure
        if structure is not None and structure.format == "xml":
            return u" "
        return u" | "

    def image_expander(self):
        if self._image_expander is None:
            cfg = self.config
            structure = cfg.structure
            names = structure.images if structure else {}
            # Nazwa z konfiguracji ma pierwszeństwo - struktura jest tylko
            # punktem wyjścia, użytkownik może ją nadpisać w zakładce Pola.
            lead = cfg.icon_kind if (cfg.include_icons and cfg.icon_as_main_image) else None
            self._image_expander = ImageExpander(
                kind=cfg.image_kind, mode=cfg.image_mode, count=cfg.image_count,
                separator=cfg.image_separator,
                base_name=cfg.image_base_name or names.get("base_name", u"image"),
                extra_name=cfg.image_extra_name or names.get("extra_name",
                                                             u"image_extra_*"),
                lead_kind=lead)
        return self._image_expander

    def icon_expander(self):
        if self._icon_expander is None:
            cfg = self.config
            self._icon_expander = IconExpander(kind=cfg.icon_kind,
                                               column_name=cfg.icon_column_name)
        return self._icon_expander

    def out(self, name):
        """Nazwa kolumny w postaci, w jakiej trafi do pliku."""
        return output_name(name, self.config.uppercase_names)

    def columns(self):
        """Nagłówek wyniku - stały dla całego pliku."""
        names = []
        for column in self.config.structure.columns:
            if column.enabled and self.out(column.out) not in names:
                names.append(self.out(column.out))
        if self.config.include_images:
            for name in self.image_expander().columns():
                if self.out(name) not in names:
                    names.append(self.out(name))
        if self.config.include_icons:
            for name in self.icon_expander().columns():
                if self.out(name) not in names:
                    names.append(self.out(name))
        if self.config.include_params:
            for name in self.param_expander().columns():
                if self.out(name) not in names:
                    names.append(self.out(name))
        return names

    # -- budowa wierszy -------------------------------------------------

    def _row_from(self, record, ctx):
        row = {}
        source_type = self.config.source_type
        for column in self.config.structure.columns:
            if not column.enabled:
                continue
            name = self.out(column.out)
            field = self.registry.get(column.field)
            if field is None:
                row[name] = u""
                continue
            if not field.available_in(source_type):
                row[name] = u""
                if column.field not in self.report.missing_fields:
                    self.report.missing_fields.append(column.field)
                continue
            row[name] = field.resolve(record, ctx)
        if self.config.include_images:
            for name, value in self.image_expander().expand(record).items():
                row[self.out(name)] = value
        if self.config.include_icons:
            for name, value in self.icon_expander().expand(record).items():
                row[self.out(name)] = value
        if self.config.include_params:
            for name, value in self.param_expander().expand(record).items():
                row[self.out(name)] = value
        return row

    def iter_rows(self, limit=None, cancel=None):
        """Gotowe wiersze po filtrach i regułach."""
        cfg = self.config
        cfg.detect()
        ctx = Context(lang=cfg.lang, site=cfg.site)
        ruleset = cfg.ruleset
        per_size = cfg.row_context == ROW_SIZE
        produced = 0

        reader = open_reader(cfg.source_path)
        for record in reader.iter_records():
            if cancel is not None and cancel():
                raise Cancelled()
            self.report.read += 1
            self.report.issues.extend(record.issues)

            contexts = []
            if per_size and record.sizes:
                for size in record.sizes:
                    contexts.append(Context(lang=cfg.lang, site=cfg.site, size=size))
            else:
                base = Context(lang=cfg.lang, site=cfg.site)
                base.size = record.sizes[0] if record.sizes else None
                contexts.append(base)

            for context in contexts:
                row = self._row_from(record, context)
                if not ruleset.accepts(row):
                    continue
                yield ruleset.apply(row)
                produced += 1
                if limit and produced >= limit:
                    return

    # -- uruchomienie ---------------------------------------------------

    def run(self, progress=None, cancel=None):
        cfg = self.config
        cfg.detect()
        structure = cfg.structure
        if structure.mode == structures_mod.MODE_TREE:
            return self._run_tree(progress=progress, cancel=cancel)
        return self._run_flat(progress=progress, cancel=cancel)

    def _make_writer(self, columns):
        cfg = self.config
        if cfg.structure.format == "xml":
            xml = cfg.structure.xml or {}
            return SimpleXmlWriter(
                cfg.output_path, columns,
                root=cfg.xml_root or xml.get("root", u"products"),
                item=cfg.xml_item or xml.get("item", u"product"),
                keep_empty=cfg.xml_keep_empty,
                cdata=cfg.xml_cdata,
                list_separator=u" ",
                newline_replacement=u" ")
        return CsvWriter(cfg.output_path, columns, delimiter=cfg.csv_delimiter,
                         encoding=cfg.csv_encoding, quoting=cfg.csv_quoting,
                         header=cfg.csv_header)

    def _run_flat(self, progress=None, cancel=None):
        columns = self.columns()
        writer = self._make_writer(columns)
        writer.open()
        try:
            for row in self.iter_rows(cancel=cancel):
                writer.write(row)
                if progress is not None and writer.written % 250 == 0:
                    progress(self.report.read, writer.written)
        finally:
            writer.close()
        self.report.written = writer.written
        self.report.skipped = self.config.ruleset.skipped
        self.report.output_path = self.config.output_path
        if self.config.include_params:
            self.report.param_overflow = list(self.param_expander().overflow)
        return self.report

    def _run_tree(self, progress=None, cancel=None):
        """Przycięty IOF - pracujemy na drzewie, nie na wierszach."""
        cfg = self.config
        keep = KeepSet(cfg.structure.keep)
        root_attrib, products_attrib = _read_containers(cfg.source_path)
        writer = IofTreeWriter(cfg.output_path, keep, root_attrib=root_attrib,
                               products_attrib=products_attrib)
        writer.open()
        read = 0
        try:
            context = ET.iterparse(cfg.source_path, events=("start", "end"))
            root = None
            depth = 0
            for event, element in context:
                if root is None:
                    root = element
                if local(element.tag) != u"product":
                    continue
                # `associated_products/product` to odsyłacz, nie produkt.
                if event == "start":
                    depth += 1
                    continue
                depth -= 1
                if depth:
                    continue
                if cancel is not None and cancel():
                    raise Cancelled()
                writer.write_product(element)
                read += 1
                element.clear()
                if root is not None:
                    for done in list(root):
                        for stale in list(done):
                            if stale is not element:
                                done.remove(stale)
                if progress is not None and read % 250 == 0:
                    progress(read, writer.written)
        finally:
            writer.close()
        self.report.read = read
        self.report.written = writer.written
        self.report.output_path = cfg.output_path
        return self.report


def _read_containers(path):
    """Atrybuty `<offer>` i `<products>` z oryginału, żeby nagłówek się zgadzał."""
    root_attrib, products_attrib = {}, {}
    context = ET.iterparse(path, events=("start",))
    for _, element in context:
        name = local(element.tag)
        if name == u"offer":
            root_attrib = _plain_attrs(element)
        elif name == u"products":
            products_attrib = _plain_attrs(element)
            break
    return root_attrib, products_attrib


def _plain_attrs(element):
    result = {}
    for key, value in element.attrib.items():
        if key.startswith(u"{"):
            from .writers.iof_tree_writer import qname
            result[qname(key)] = value
        else:
            result[key] = value
    return result


def suggest_output(source_path, structure):
    """Domyślna ścieżka wyniku obok pliku źródłowego."""
    folder = os.path.dirname(os.path.abspath(source_path or u"."))
    base = os.path.splitext(os.path.basename(source_path or u"eksport"))[0]
    extension = ".xml" if structure and structure.format == "xml" else ".csv"
    suffix = structure.id if structure else u"wynik"
    return os.path.join(folder, u"%s_%s%s" % (base, suffix, extension))
