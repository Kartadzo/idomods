# -*- coding: utf-8 -*-
"""Zakładka 4: struktura wyniku, opcje zapisu i eksport.

Eksport idzie w wątku roboczym z paskiem postępu i przyciskiem Anuluj, bo przy
setkach tysięcy produktów zamrożone okno wygląda jak zawieszona aplikacja.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.pipeline import Cancelled, Pipeline, suggest_output
from core.structures import MODE_TREE
from .state import FIELDS_CHANGED, OUTPUT_CHANGED, SOURCE_CHANGED
from .worker import BackgroundTask

ENCODINGS = [("utf-8-sig", u"UTF-8 z BOM (Excel)"), ("utf-8", u"UTF-8"),
             ("cp1250", u"Windows-1250")]
DELIMITERS = [(u";", u"średnik ;"), (u",", u"przecinek ,"), (u"\t", u"tabulator")]
QUOTINGS = [("minimal", u"tylko gdy trzeba"), ("all", u"zawsze"),
            ("nonnumeric", u"poza liczbami"), ("none", u"nigdy")]


class OutputTab(ttk.Frame):

    def __init__(self, master, state):
        ttk.Frame.__init__(self, master, padding=10)
        self.state = state
        self._worker = None
        self._cancel = False
        self._build()
        self.refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)

        structure_box = ttk.LabelFrame(self, text=u"Struktura wyniku", padding=8)
        structure_box.grid(row=0, column=0, sticky="ew")
        self.structure_var = tk.StringVar()
        self._structure_buttons = {}
        for index, structure in enumerate(self.state.structures):
            button = ttk.Radiobutton(structure_box, text=structure.label,
                                     value=structure.id, variable=self.structure_var,
                                     command=self._structure_changed)
            button.grid(row=index, column=0, sticky="w")
            note = ttk.Label(structure_box, text=structure.description,
                             foreground="#666666", wraplength=520)
            note.grid(row=index, column=1, sticky="w", padx=10)
            self._structure_buttons[structure.id] = (button, note)

        self.csv_box = ttk.LabelFrame(self, text=u"Opcje CSV", padding=8)
        self.csv_box.grid(row=1, column=0, sticky="ew", pady=8)
        config = self.state.config

        ttk.Label(self.csv_box, text=u"Separator:").grid(row=0, column=0, sticky="w")
        self.delimiter = tk.StringVar(value=_label_for(DELIMITERS, config.csv_delimiter))
        ttk.Combobox(self.csv_box, textvariable=self.delimiter, width=16, state="readonly",
                     values=[l for _, l in DELIMITERS]).grid(row=0, column=1, sticky="w",
                                                             padx=6)
        ttk.Label(self.csv_box, text=u"Kodowanie:").grid(row=0, column=2, sticky="e",
                                                        padx=(12, 0))
        self.encoding = tk.StringVar(value=_label_for(ENCODINGS, config.csv_encoding))
        ttk.Combobox(self.csv_box, textvariable=self.encoding, width=22, state="readonly",
                     values=[l for _, l in ENCODINGS]).grid(row=0, column=3, sticky="w",
                                                            padx=6)
        ttk.Label(self.csv_box, text=u"Cudzysłowy:").grid(row=1, column=0, sticky="w",
                                                         pady=(6, 0))
        self.quoting = tk.StringVar(value=_label_for(QUOTINGS, config.csv_quoting))
        ttk.Combobox(self.csv_box, textvariable=self.quoting, width=16, state="readonly",
                     values=[l for _, l in QUOTINGS]).grid(row=1, column=1, sticky="w",
                                                           padx=6, pady=(6, 0))
        self.csv_header = tk.BooleanVar(value=config.csv_header)
        ttk.Checkbutton(self.csv_box, text=u"nagłówek z nazwami kolumn",
                        variable=self.csv_header).grid(row=1, column=2, columnspan=2,
                                                       sticky="w", pady=(6, 0))

        self.xml_box = ttk.LabelFrame(self, text=u"Opcje XML", padding=8)
        self.xml_box.grid(row=2, column=0, sticky="ew")
        ttk.Label(self.xml_box, text=u"Element główny:").grid(row=0, column=0, sticky="w")
        self.xml_root = tk.StringVar(value=config.xml_root)
        ttk.Entry(self.xml_box, textvariable=self.xml_root, width=18).grid(
            row=0, column=1, sticky="w", padx=6)
        ttk.Label(self.xml_box, text=u"Element wiersza:").grid(row=0, column=2, sticky="e",
                                                              padx=(12, 0))
        self.xml_item = tk.StringVar(value=config.xml_item)
        ttk.Entry(self.xml_box, textvariable=self.xml_item, width=18).grid(
            row=0, column=3, sticky="w", padx=6)
        self.xml_keep_empty = tk.BooleanVar(value=config.xml_keep_empty)
        ttk.Checkbutton(self.xml_box, text=u"zachowaj puste elementy",
                        variable=self.xml_keep_empty).grid(row=1, column=0, columnspan=2,
                                                           sticky="w", pady=(6, 0))
        self.xml_cdata = tk.BooleanVar(value=config.xml_cdata)
        ttk.Checkbutton(self.xml_box, text=u"wartości w CDATA",
                        variable=self.xml_cdata).grid(row=1, column=2, columnspan=2,
                                                      sticky="w", pady=(6, 0))

        path_box = ttk.LabelFrame(self, text=u"Plik wynikowy", padding=8)
        path_box.grid(row=3, column=0, sticky="ew", pady=8)
        path_box.columnconfigure(0, weight=1)
        self.output_var = tk.StringVar(value=config.output_path)
        ttk.Entry(path_box, textvariable=self.output_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(path_box, text=u"Zapisz jako…", command=self.choose_output).grid(
            row=0, column=1, padx=6)

        run_box = ttk.Frame(self)
        run_box.grid(row=4, column=0, sticky="ew")
        run_box.columnconfigure(1, weight=1)
        self.export_button = ttk.Button(run_box, text=u"Eksportuj", command=self.export)
        self.export_button.grid(row=0, column=0)
        self.progress = ttk.Progressbar(run_box, mode="indeterminate")
        self.progress.grid(row=0, column=1, sticky="ew", padx=10)
        self.cancel_button = ttk.Button(run_box, text=u"Anuluj", command=self.cancel,
                                        state="disabled")
        self.cancel_button.grid(row=0, column=2)

        self.report_text = tk.Text(self, height=6, wrap="word", relief="flat")
        self.report_text.configure(state="disabled", background=_surface())
        self.report_text.grid(row=5, column=0, sticky="nsew", pady=(8, 0))
        self.rowconfigure(5, weight=1)

    # -- struktura ---------------------------------------------------------

    def refresh(self):
        config = self.state.config
        if config.structure:
            self.structure_var.set(config.structure.id)
        source_type = self.state.source_type
        for structure in self.state.structures:
            button, note = self._structure_buttons[structure.id]
            if source_type and not structure.supports(source_type):
                button.configure(state="disabled")
                note.configure(text=structure.unsupported_reason(source_type),
                               foreground="#b45f06")
            else:
                button.configure(state="normal")
                note.configure(text=structure.description, foreground="#666666")
        self._toggle_option_boxes()

    def _toggle_option_boxes(self):
        structure = self.state.config.structure
        is_xml = structure is not None and structure.format == "xml"
        is_tree = structure is not None and structure.mode == MODE_TREE
        for child in self.csv_box.winfo_children():
            child.configure(state="disabled" if is_xml else "normal")
        for child in self.xml_box.winfo_children():
            # Przycięty IOF zachowuje oryginalne drzewo, więc nazwy elementów
            # nie są do wyboru.
            child.configure(state="disabled" if (not is_xml or is_tree) else "normal")

    def _structure_changed(self):
        chosen = self.state.structure_by_id(self.structure_var.get())
        if chosen is None:
            return
        current = self.state.config.structure
        keep_columns = False
        if current and current.columns and chosen.mode != MODE_TREE:
            keep_columns = messagebox.askyesno(
                u"Zmiana struktury",
                u"Zachować obecne kolumny wyniku?\n\n"
                u"„Nie” wczyta domyślne kolumny struktury „%s”." % chosen.label,
                parent=self)
        columns = list(current.columns) if (keep_columns and current) else None
        self.state.config.structure = chosen.copy()
        if columns is not None:
            self.state.config.structure.columns = columns
        # Struktura może narzucać nazewnictwo kolumn ze zdjęciami - przejmujemy je,
        # a użytkownik i tak może je nadpisać w zakładce Pola.
        images = self.state.config.structure.images or {}
        if images.get("base_name"):
            self.state.config.image_base_name = images["base_name"]
        if images.get("extra_name"):
            self.state.config.image_extra_name = images["extra_name"]
        self._suggest_path()
        self.refresh()
        self.state.notify(OUTPUT_CHANGED)

    def _suggest_path(self):
        config = self.state.config
        if config.source_path:
            path = suggest_output(config.source_path, config.structure)
            self.output_var.set(path)
            config.output_path = path

    def choose_output(self):
        config = self.state.config
        extension = ".xml" if config.structure and config.structure.format == "xml" else ".csv"
        initial = self.output_var.get() or suggest_output(config.source_path,
                                                          config.structure)
        path = filedialog.asksaveasfilename(
            title=u"Zapisz wynik", defaultextension=extension,
            initialdir=os.path.dirname(initial) or os.getcwd(),
            initialfile=os.path.basename(initial),
            filetypes=[(u"Plik wyniku", "*" + extension), (u"Wszystkie pliki", "*.*")])
        if path:
            self.output_var.set(path)
            config.output_path = path

    # -- eksport -----------------------------------------------------------

    def _collect(self):
        config = self.state.config
        config.csv_delimiter = _value_for(DELIMITERS, self.delimiter.get(), u";")
        config.csv_encoding = _value_for(ENCODINGS, self.encoding.get(), "utf-8-sig")
        config.csv_quoting = _value_for(QUOTINGS, self.quoting.get(), "minimal")
        config.csv_header = bool(self.csv_header.get())
        config.xml_root = self.xml_root.get() or u"products"
        config.xml_item = self.xml_item.get() or u"product"
        config.xml_keep_empty = bool(self.xml_keep_empty.get())
        config.xml_cdata = bool(self.xml_cdata.get())
        config.output_path = self.output_var.get().strip()
        return config

    def export(self):
        config = self._collect()
        if not config.source_path:
            messagebox.showwarning(u"Eksport", u"Najpierw wybierz plik źródłowy.",
                                   parent=self)
            return
        if not config.output_path:
            self._suggest_path()
            config.output_path = self.output_var.get().strip()
        if not config.output_path:
            messagebox.showwarning(u"Eksport", u"Wskaż plik wynikowy.", parent=self)
            return
        structure = config.structure
        if structure and config.source_type and not structure.supports(config.source_type):
            messagebox.showwarning(u"Eksport",
                                   structure.unsupported_reason(config.source_type),
                                   parent=self)
            return
        if structure and structure.mode != MODE_TREE and not structure.columns \
                and not config.include_params and not config.include_images:
            messagebox.showwarning(u"Eksport",
                                   u"Nie wybrano żadnych kolumn - zakładka Pola.",
                                   parent=self)
            return

        self._cancel = False
        self.export_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress.configure(mode="indeterminate")
        self.progress.start(12)
        self._write_report(u"Eksport w toku…")

        pipeline = Pipeline(config, self.state.registry)

        def work(emit, cancelled):
            try:
                return pipeline.run(progress=lambda read, written: emit(read, written),
                                    cancel=cancelled)
            except Cancelled:
                return None

        self._worker = BackgroundTask(
            self, work,
            on_done=lambda report: self._finished(report,
                                                  None if report else u"Eksport przerwany."),
            on_error=lambda error: self._finished(None, u"Błąd eksportu: %s" % error),
            on_progress=self._progress).start()

    def _progress(self, read, written):
        self._write_report(u"Przeczytano %d produktów, zapisano %d wierszy…"
                           % (read, written))

    def cancel(self):
        if self._worker is not None:
            self._worker.cancel()
        self.cancel_button.configure(state="disabled")

    def _finished(self, report, error):
        self.progress.stop()
        self.export_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        if error:
            self._write_report(error)
            return
        lines = [u"Gotowe: %s" % report.summary(), u"Plik: %s" % report.output_path]
        if report.missing_fields:
            lines.append(u"Pola nieobecne w tym źródle (puste w wyniku): %s"
                         % u", ".join(report.missing_fields))
        if report.param_overflow:
            lines.append(u"Parametry poza listą kolumn: %s"
                         % u", ".join(u"%s" % p for p in report.param_overflow[:10]))
        if report.issues:
            lines.append(u"Ostrzeżenia przy odczycie: %d (pierwsze: %s)"
                         % (len(report.issues), report.issues[0]))
        self._write_report(u"\n".join(lines))

    def _write_report(self, text):
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", text)
        self.report_text.configure(state="disabled")

    def on_event(self, event):
        if event == SOURCE_CHANGED:
            if not self.output_var.get():
                self._suggest_path()
            self.refresh()
        elif event in (FIELDS_CHANGED, OUTPUT_CHANGED):
            self.refresh()


def _label_for(pairs, value, default=u""):
    for key, label in pairs:
        if key == value:
            return label
    return pairs[0][1] if pairs else default


def _value_for(pairs, label, default):
    for key, text in pairs:
        if text == label:
            return key
    return default


def _surface():
    """Kolor tła kontenerów ttk - zwykły Text musi go dostać wprost."""
    try:
        return ttk.Style().lookup("TFrame", "background") or "#f0f0f0"
    except tk.TclError:
        return "#f0f0f0"
