# -*- coding: utf-8 -*-
"""Zakładka 1: źródło danych.

Typ pliku rozpoznajemy po zawartości, nie po rozszerzeniu. Skan jest
obowiązkowy, bo zestaw kolumn CSV zmienia się między sklepami - dwa eksporty
z tego samego panelu potrafią mieć inny komplet języków.
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk

from core.readers.base import detect_source_type
from core.scanner import scan
from .state import FIELDS_CHANGED, SOURCE_CHANGED
from .worker import BackgroundTask

SOURCE_LABELS = {"xml": u"XML (IOF 3.0)", "csv": u"CSV (eksport tabelaryczny)"}


class SourceTab(ttk.Frame):

    def __init__(self, master, state):
        ttk.Frame.__init__(self, master, padding=12)
        self.state = state
        self._scanning = False
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text=u"Plik źródłowy").grid(row=0, column=0, sticky="w", pady=4)
        self.path_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.path_var)
        entry.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(self, text=u"Wybierz…", command=self.choose).grid(row=0, column=2)

        self.type_var = tk.StringVar(value=u"—")
        ttk.Label(self, text=u"Rozpoznany typ").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(self, textvariable=self.type_var, font=("", 9, "bold")).grid(
            row=1, column=1, sticky="w", padx=6)

        scan_row = ttk.Frame(self)
        scan_row.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 4))
        self.scan_button = ttk.Button(scan_row, text=u"Skanuj plik", command=self.run_scan)
        self.scan_button.pack(side="left")
        ttk.Label(scan_row, text=u"limit produktów:").pack(side="left", padx=(12, 4))
        self.limit_var = tk.StringVar(value=u"%d" % self.state.settings.get("scan_limit", 2000))
        ttk.Entry(scan_row, textvariable=self.limit_var, width=8).pack(side="left")
        ttk.Label(scan_row, text=u"(0 = cały plik)").pack(side="left", padx=6)

        box = ttk.LabelFrame(self, text=u"Wynik skanu", padding=8)
        box.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=8)
        box.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self.summary = tk.Text(box, height=7, wrap="word", relief="flat")
        self.summary.configure(state="disabled", background=_surface())
        self.summary.pack(fill="both", expand=True)

        options = ttk.LabelFrame(self, text=u"Zakres eksportu", padding=8)
        options.grid(row=4, column=0, columnspan=3, sticky="ew", pady=4)

        ttk.Label(options, text=u"Wiersz wyniku:").grid(row=0, column=0, sticky="w")
        self.row_var = tk.StringVar(value=self.state.config.row_context)
        ttk.Radiobutton(options, text=u"jeden na produkt", value="product",
                        variable=self.row_var, command=self._row_changed).grid(
            row=0, column=1, sticky="w", padx=6)
        ttk.Radiobutton(options, text=u"jeden na rozmiar", value="size",
                        variable=self.row_var, command=self._row_changed).grid(
            row=0, column=2, sticky="w", padx=6)

        ttk.Label(options, text=u"Język:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.lang_var = tk.StringVar(value=self.state.config.lang)
        self.lang_combo = ttk.Combobox(options, textvariable=self.lang_var, width=8,
                                       state="readonly", values=[u"pol"])
        self.lang_combo.grid(row=1, column=1, sticky="w", padx=6, pady=(8, 0))
        self.lang_combo.bind("<<ComboboxSelected>>", lambda e: self._context_changed())

        ttk.Label(options, text=u"Sklep:").grid(row=1, column=2, sticky="e", pady=(8, 0))
        self.site_var = tk.StringVar(value=self.state.config.site)
        self.site_combo = ttk.Combobox(options, textvariable=self.site_var, width=8,
                                       state="readonly", values=[u"1"])
        self.site_combo.grid(row=1, column=3, sticky="w", padx=6, pady=(8, 0))
        self.site_combo.bind("<<ComboboxSelected>>", lambda e: self._context_changed())

    # -- akcje -----------------------------------------------------------

    def choose(self):
        initial = self.state.settings.get("last_dir") or os.getcwd()
        path = filedialog.askopenfilename(
            title=u"Wybierz eksport produktów",
            initialdir=initial,
            filetypes=[(u"Eksport IdoSell", "*.xml *.csv"), (u"Wszystkie pliki", "*.*")])
        if not path:
            return
        self.set_path(path)

    def set_path(self, path):
        self.path_var.set(path)
        self.state.config.source_path = path
        try:
            source_type = detect_source_type(path)
        except IOError:
            source_type = None
        self.state.config.source_type = source_type
        self.type_var.set(SOURCE_LABELS.get(source_type, u"nierozpoznany"))
        self.state.remember_dir(path)
        self.state.notify(SOURCE_CHANGED)
        self.run_scan()

    def run_scan(self):
        path = self.path_var.get().strip()
        if not path or self._scanning:
            return
        try:
            limit = int(self.limit_var.get() or 0)
        except ValueError:
            limit = 2000
        self.state.settings["scan_limit"] = limit
        self.state.save_settings()

        self._scanning = True
        self.scan_button.configure(state="disabled")
        self._write_summary(u"Skanowanie…")

        registry = self.state.reset_registry()

        def work(emit, cancelled):
            return scan(path, limit=limit or None, registry=registry,
                        progress=lambda count: emit(count))

        BackgroundTask(self, work,
                       on_done=self._scan_done,
                       on_error=self._scan_failed,
                       on_progress=self._scan_progress).start()

    def _scan_progress(self, count):
        self._write_summary(u"Skanowanie… przeczytano %d produktów" % count)

    def _scan_failed(self, error):
        self._scanning = False
        self.scan_button.configure(state="normal")
        self._write_summary(u"Nie udało się odczytać pliku:\n%s" % error)

    def _scan_done(self, result):
        self._scanning = False
        self.scan_button.configure(state="normal")
        self.state.scan = result

        langs = result.langs or [u"pol"]
        self.lang_combo.configure(values=langs)
        if self.lang_var.get() not in langs:
            self.lang_var.set(u"pol" if u"pol" in langs else langs[0])
        sites = result.sites or [u"1"]
        self.site_combo.configure(values=sites)
        if self.site_var.get() not in sites:
            self.site_var.set(sites[0])
        self._context_changed(notify=False)

        lines = [result.summary()]
        if result.unknown_columns:
            lines.append(u"%d kolumn spoza rdzenia trafiło do grupy „Nierozpoznane”."
                         % len(result.unknown_columns))
        if result.truncated:
            lines.append(u"Uwaga: skan zatrzymał się na limicie, więc lista parametrów "
                         u"i maksimum zdjęć mogą być niepełne.")
        if result.issues:
            lines.append(u"Ostrzeżenia przy odczycie: %d." % len(result.issues))
        self._write_summary(u"\n".join(lines))
        self.state.notify(SOURCE_CHANGED)
        self.state.notify(FIELDS_CHANGED)

    def _row_changed(self):
        self.state.config.row_context = self.row_var.get()
        self.state.notify(FIELDS_CHANGED)

    def _context_changed(self, notify=True):
        self.state.config.lang = self.lang_var.get()
        self.state.config.site = self.site_var.get()
        if notify:
            self.state.notify(FIELDS_CHANGED)

    def _write_summary(self, text):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", text)
        self.summary.configure(state="disabled")

    def on_event(self, event):
        if event == SOURCE_CHANGED:
            config = self.state.config
            if config.source_path and config.source_path != self.path_var.get():
                self.path_var.set(config.source_path)
                self.type_var.set(SOURCE_LABELS.get(config.source_type, u"nierozpoznany"))
            self.row_var.set(config.row_context)


def _surface():
    """Kolor tła kontenerów ttk - zwykły Text musi go dostać wprost."""
    try:
        return ttk.Style().lookup("TFrame", "background") or "#f0f0f0"
    except tk.TclError:
        return "#f0f0f0"
